import numpy as np
import pandas as pd
import os
from tensorflow.keras.models import load_model
from preprocess import load_and_preprocess

def predict():
    if not os.path.exists("model/idle_predictor.h5"):
        print("모델 없음")
        return

    X, _, _ = load_and_preprocess()
    if len(X) == 0:
        print("데이터 부족")
        return

    model = load_model("model/idle_predictor.h5")
    pred = model.predict(np.array([X[-1]]))[0][0]   # 가장 최신 10분 예측

    print(f"예측 결과 : {pred}")
    if pred > 0.5:
        print("유휴 상태 예측 → 파일 정리 시작")
    else:
        print("활성 상태 예측 → 대기 중")