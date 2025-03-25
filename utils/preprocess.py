import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# 슬라이딩 윈도우 형태의 시계열 데이터로 구성
def load_and_preprocess(path="data/user_log.csv", window_size=10):
    df = pd.read_csv(path, header=None, names=["timestamp", "mouse", "keyboard", "cpu", "label"])
    features = df[["mouse", "keyboard", "cpu"]]     # 입력값
    target = df["label"]    # 예측값(유휴 여부)

    # 정규화
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    # 시계열 데이터 구성
    X, y = [], []
    for i in range(len(df) - window_size):
        X.append(features_scaled[i:i+window_size])      # 과거 10분 입력값
        y.append(target[i+window_size])     # 그 다음 시간의 유휴 여부부

    return np.array(X), np.array(y), scaler