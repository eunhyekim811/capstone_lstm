import numpy as np
import pandas as pd
import os
from tensorflow.keras.models import load_model
from .preprocess import load_and_preprocess
import csv
from datetime import datetime
from .config import PREDICTIONS_LOG_FILE, MODEL_FILE

# 예측 결과를 로그 파일에 저장
def log_prediction(timestamp, predicted):
    log_path = PREDICTIONS_LOG_FILE

    # 예측 결과 로그 파일에 추가
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        # 시퀀스 값을 세미콜론으로 구분하여 하나의 문자열로 저장
        predicted_str = ";".join(map(str, predicted))
        writer.writerow([timestamp, predicted_str])


def predict():
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
    log_prediction(timestamp, predicted)
    
    # 전체 데이터 대상으로 모델 평가
    decoder_input = np.zeros((len(X), future_steps, X.shape[2]))
    loss, accuracy = model.evaluate([X, decoder_input], y, verbose=0)
    
    print("==============================================")
    print(f"전체 평가 결과 : 손실 {loss:.4f}, 정확도 {accuracy:.4f}")
    print(f"예측 결과 : {predicted} (원본: {pred})")

    # 유휴 상태 예측 결과 출력
    if pred.mean() > 0.6:
        print("30분간 유휴 상태 → 파일 정리 시작")
    else:
        print("활성 상태 → 대기 중")
    print("==============================================")