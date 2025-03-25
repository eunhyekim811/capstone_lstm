from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from preprocess import load_and_preprocess
import os

def train():
    if not os.path.exists("data/user_log.csv"):
        print("데이터 없음")
        return

    X, y, _ = load_and_preprocess()

    if len(X) < 100:
        print(f"데이터 부족 : {len(X)}개")
        return

    model = Sequential([
        LSTM(64, input_shape=(X.shape[1], X.shape[2])),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')
    ])

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)
    model.save("model/idle_predictor.h5")

    print("모델 학습 및 저장 완료")