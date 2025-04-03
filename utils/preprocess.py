import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# 슬라이딩 윈도우 형태의 시계열 데이터로 구성
def load_and_preprocess(path="data/user_log2.csv", window_size=10, future_steps=6):
    df = pd.read_csv(path, header=None, names=["timestamp", "power", "mouse", "keyboard", "cpu", "disk","label"])
    
    # 전원이 켜진 데이터만 사용
    df = df[df["power"] == 1]

    features = df[["mouse", "keyboard", "cpu", "disk"]]     # 입력값 X
    target = df["label"]    # 예측값(유휴 여부) y

    # 정규화(입력값들을 0~1 사이로 변환)
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    # 시계열 데이터 구성
    # 연속된 과거 window_size개의 입력값으로, 그 다음 시점의 유휴 상태 예측
    X, y = [], []
    # window_size 이후부터 future_steps 타임스텝까지 예측
    for i in range(len(df) - window_size - future_steps + 1):
        X.append(features_scaled[i:i+window_size])      # 과거 10분 입력값
        y.append(target.iloc[i+window_size:i+window_size+future_steps].values)     # 그 다음 시간의 유휴 여부

    return np.array(X), np.array(y), scaler