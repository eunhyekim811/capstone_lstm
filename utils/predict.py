import numpy as np
import pandas as pd
import os
from tensorflow.keras.models import load_model
from .preprocess import load_and_preprocess

def predict():
    if not os.path.exists("model/idle_predictor2.keras"):
        print("모델 없음")
        return

    # 학습 데이터 로드
    X, y, _ = load_and_preprocess()
    if len(X) == 0:
        print("데이터 부족")
        return

    # 학습된 모델 로드
    model = load_model("model/idle_predictor2.keras")

    # 가장 최신 10분 동안의 데이터를 통해 현재 유휴 상태일 확률 예측
    pred = model.predict(np.array([X[-1]]))[0][0]

    # 모델 평가
    loss, accuracy = model.evaluate(X, y, verbose=0)
    
    print("==============================================")
    print(f"평가 결과 : 손실 {loss:.4f}, 정확도 {accuracy:.4f}")
    print(f"예측 결과 : {pred}")

    # 유휴 상태 예측 결과 출력
    if pred > 0.5:
        print("유휴 상태 → 파일 정리 시작")
    else:
        print("활성 상태 → 대기 중")
    print("==============================================")