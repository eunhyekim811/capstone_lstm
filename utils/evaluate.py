import os
from datetime import datetime, timedelta
import numpy as np
from config.db_config import DatabaseManager
from mysql.connector import Error
import uuid

def evaluate():
    db = DatabaseManager()
    connection = db.get_connection()
    if not connection:
        print("데이터베이스 연결 실패")
        return

    try:
        cursor = connection.cursor()
        
        # 현재 사용자의 uid 가져오기
        mac = uuid.getnode()
        cursor.execute("SELECT uid FROM user WHERE mac = %s", (mac,))
        result = cursor.fetchone()
        if not result:
            print("사용자 ID를 찾을 수 없습니다.")
            return
        uid = result[0]

        # 예측 결과 조회
        query = """
            SELECT timestamp, m1, m2, m3, m4, m5, m6
            FROM predictLog
            WHERE uid = %s
            ORDER BY timestamp
        """
        cursor.execute(query, (uid,))
        predictions = {}
        for row in cursor.fetchall():
            timestamp = row[0]
            pred_seq = list(row[1:])  # m1부터 m6까지의 예측값
            predictions[timestamp] = pred_seq

        # 실제 결과 조회
        query = """
            SELECT timestamp, is_idle
            FROM collectLog
            WHERE uid = %s
            ORDER BY timestamp
        """
        cursor.execute(query, (uid,))
        actuals = [(row[0], row[1]) for row in cursor.fetchall()]

        # 예측 결과와 실제 결과 비교
        accuracy = []
        if predictions:
            seq_length = len(next(iter(predictions.values())))
        else:
            print("예측 로그가 없습니다.")
            return

        for pred_time, pred_seq in predictions.items():
            start_time = pred_time
            end_time = pred_time + timedelta(minutes=seq_length)

            # 실제 결과 중 해당 시간대에 속하는 데이터 추출
            actual_values = [label for (actual_time, label) in actuals if start_time <= actual_time <= end_time]
            if len(actual_values) < seq_length:
                print("실제 결과 시간대에 데이터가 부족합니다.")
                continue
            
            actual_seq = actual_values[:seq_length]
            seq_acc = np.mean(np.array(pred_seq) == np.array(actual_seq))
            accuracy.append(seq_acc)
            
        if accuracy:
            overall_acc = np.mean(accuracy)
            print(f"전체 시퀀스 정확도 (전체 {len(accuracy)}개 예측): {overall_acc:.4f}")
        else:
            print("정확도 계산 불가")

    except Error as e:
        print(f"데이터베이스 조회 오류: {e}")
    finally:
        cursor.close()
        
