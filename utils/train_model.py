from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from .preprocess import load_and_preprocess
import os

def train():
    if not os.path.exists("data/user_log2.csv"):
        print("데이터 없음")
        return

    X, y, _ = load_and_preprocess()

    if len(X) < 100:
        print(f"데이터 부족 : {len(X)}개")
        return

    model = Sequential([
        # Input 레이어 추가
        Input(shape=(X.shape[1], X.shape[2])),
        # LSTM 레이어에서 input_shape 제거
        LSTM(64),
        Dropout(0.2),   # 과적합 방지
        Dense(32, activation='relu'),   # 은닉층
        Dense(1, activation='sigmoid')  # 출력층(유휴 여부 예측) - 이진 분류용 시그모이드 함수.
    ])

    # 학습 전 손실 함수(loss), 최적화 방법(optimizer), 평가지표(metrics) 정의
    # 이진 분류 문제이므로 이진 교차 엔트로피 손실 함수 사용
    # 최적화 방법 : adam(가중치 업데이트)
    # 평가지표 : 정확도(accuracy)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # 실제 모델 학습을 시키는 부분
    # x : 학습 입력 데이터(시계열 데이터) ex. (samples, timesteps, features)
    # y : 학습 출력 데이터(유휴 여부)
    # epochs : 학습 반복 횟수
    # batch_size : 한 번에 학습할 데이터 개수
    # verbose : 학습 과정 출력 여부(1: epoch마다 출력, 0: 진행상황 출력X, 2: 간략 출력)
    model.fit(X, y, epochs=5, batch_size=32, verbose=1)

    # 학습된 모델 저장(없는 경우 자동 생성)
    os.makedirs("model", exist_ok=True)  # model 디렉토리가 없으면 생성
    model.save("model/idle_predictor2.keras")

    print("모델 학습 및 저장 완료")