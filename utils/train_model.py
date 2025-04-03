from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, TimeDistributed
from tensorflow.keras.optimizers import Adam
from .preprocess import load_and_preprocess
import os
import numpy as np

def train():
    if not os.path.exists("data/user_log3.csv"):
        print("데이터 없음")
        return

    window_size = 20
    future_steps = 6
    X, y, scaler = load_and_preprocess(window_size=window_size, future_steps=future_steps)

    if len(X) < 100:
        print(f"데이터 부족 : {len(X)}개")
        return
    
    encoder_inputs = Input(shape=(window_size, X.shape[2]))
    encoder_lstm = LSTM(64, return_state=True)
    _, state_h, state_c = encoder_lstm(encoder_inputs)
    encoder_states = [state_h, state_c]

    decoder_inputs = Input(shape=(future_steps, X.shape[2]))
    decoder_lstm = LSTM(64, return_sequences=True)
    decoder_outputs = decoder_lstm(decoder_inputs, initial_state=encoder_states)
    decoder_dense = TimeDistributed(Dense(1, activation='sigmoid'))
    decoder_outputs = decoder_dense(decoder_outputs)

    model = Model(inputs=[encoder_inputs, decoder_inputs], outputs=decoder_outputs)
    model.compile(loss='binary_crossentropy', optimizer=Adam(), metrics=['accuracy'])
    model.summary()

    decoder_start = np.zeros((X.shape[0], future_steps, X.shape[2]))

    model.fit([X, decoder_start], y, epochs=10, batch_size=32, validation_split=0.2)

    # model = Sequential([
    #     # Input 레이어 추가
    #     Input(shape=(X.shape[1], X.shape[2])),
    #     # LSTM 레이어에서 input_shape 제거
    #     LSTM(64),
    #     Dropout(0.2),   # 과적합 방지
    #     Dense(32, activation='relu'),   # 은닉층
    #     Dense(1, activation='sigmoid')  # 출력층(유휴 여부 예측) - 이진 분류용 시그모이드 함수.
    # ])

    # # 학습 전 손실 함수(loss), 최적화 방법(optimizer), 평가지표(metrics) 정의
    # model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # # 실제 모델 학습을 시키는 부분
    # model.fit(X, y, epochs=5, batch_size=32, verbose=1)

    # 학습된 모델 저장(없는 경우 자동 생성)
    if not os.path.exists("model"):
        os.makedirs("model", exist_ok=True)  # model 디렉토리가 없으면 생성
    model.save("model/idle_predictor3.keras")

    print("모델 학습 및 저장 완료")