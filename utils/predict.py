import numpy as np
import subprocess
import pandas as pd
import os
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from .preprocess import load_and_preprocess
from datetime import datetime
from config.db_config import DatabaseManager
from config.config import MODEL_FILE
import uuid
from mysql.connector import Error
from apscheduler.schedulers.background import BackgroundScheduler

# fileindexingproject/main.py 실행을 위한 함수
def _run_file_indexing_job():
    project_path = r"C:\Users\default.DESKTOP-A742PF6\Desktop\H\capstone\Local-File-Organizer\fileindexingproject\main.py"
    try:
        print(" APScheduler job: 파일 인덱싱 스크립트 실행 시도")
        subprocess.run(["python", project_path, "auto"], check=True, capture_output=True, text=True)
        print(" APScheduler job: 파일 인덱싱 스크립트 실행 완료")
    except subprocess.CalledProcessError as e:
        print(f" APScheduler job: 파일 인덱싱 스크립트 실행 오류: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print(f" APScheduler job: 파일 인덱싱 스크립트 경로 오류: {project_path}")
    except Exception as e:
        print(f" APScheduler job: 예상치 못한 오류 발생 - {e}")

def log_prediction(uid, timestamp, predicted):
    """예측 결과를 데이터베이스에 저장"""
    db = DatabaseManager()
    connection = db.get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO predictLog (uid, timestamp, m1, m2, m3, m4, m5, m6)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            # NumPy int64를 Python int로 변환
            values = (uid, timestamp, *[int(x) for x in predicted])
            cursor.execute(query, values)
            connection.commit()
        except Error as e:
            print(f"예측 결과 저장 오류: {e}")
        finally:
            cursor.close()

def predict(scheduler: BackgroundScheduler):
    try:
        window_size = 20
        future_steps = 6
        
        if not os.path.exists(MODEL_FILE):
            print("모델 없음")
            return

        # 학습 데이터 로드
        X, y, _ = load_and_preprocess(window_size=window_size, future_steps=future_steps)
        if len(X) == 0:
            print("데이터 부족")
            return

        # 학습된 모델 로드
        model = load_model(MODEL_FILE)
        # 디코더 입력: 0 벡터 (시작 토큰)
        decoder_start = np.zeros((1, future_steps, X.shape[2]))
        # 가장 최신 10분 동안의 데이터를 통해 현재 유휴 상태일 확률 예측
        latest_input = np.array([X[-1]])
        pred = model.predict([latest_input, decoder_start])[0]
        pred = pred.flatten()

        # 예측 결과 로그 파일에 추가
        # 0, 1 두 가지 값 중 하나로 예측하도록 바꾸는데 0.5 이상이면 1로 예측
        predicted = (pred > 0.5).astype(int)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 현재 사용자의 uid 가져오기
        db = DatabaseManager()
        connection = db.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                mac = uuid.getnode()
                cursor.execute("SELECT uid FROM user WHERE mac = %s", (mac,))
                result = cursor.fetchone()
                if result:
                    uid = result[0]
                    log_prediction(uid, timestamp, predicted)
                else:
                    print("사용자 ID를 찾을 수 없습니다.")
            except Error as e:
                print(f"사용자 ID 조회 오류: {e}")
            finally:
                cursor.close()
        
        # 전체 데이터 대상으로 모델 평가
        decoder_input = np.zeros((len(X), future_steps, X.shape[2]))
        loss, accuracy = model.evaluate([X, decoder_input], y, verbose=0)
        
        print("==============================================")
        print(f"전체 평가 결과 : 손실 {loss:.4f}, 정확도 {accuracy:.4f}")
        print(f"예측 결과 : {predicted} (원본: {pred})")

        # 유휴 상태 예측 결과 출력
        if pred.mean() > 0.55:
            print("30분간 유휴 상태로 예측됨 → 파일 정리 작업 스케줄링")
            scheduler.add_job(_run_file_indexing_job)
        else:
            print("활성 상태로 예측됨 → 대기 중")
        print("==============================================")
    finally:
        K.clear_session()
        print("예측 후 Keras 세션 정리 완료")