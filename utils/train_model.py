from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, TimeDistributed
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from .preprocess import load_and_preprocess
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
from config.config import MODEL_FILE, TRAIN_DIR

matplotlib.use('Agg')  # Tkinter 대신 Agg 백엔드 사용

def plot_training_history(history):
    """학습 곡선을 그리는 함수"""
    plt.figure(figsize=(12, 4))
    
    # 손실 곡선
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='train_loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.title('Loss Curve')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    # 정확도 곡선
    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='train_accuracy')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
    plt.title('Accuracy Curve')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    plt.tight_layout()
    
    # 현재 시간을 파일명에 포함
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'{current_time}.png'
    plt.savefig(os.path.join(TRAIN_DIR, filename))
    plt.close()

def train():
    try:
        window_size = 20
        future_steps = 6
        X, y, scaler = load_and_preprocess(window_size=window_size, future_steps=future_steps)

        if len(X) < 100:
            print(f"데이터 부족 : {len(X)}개")
            return
        
        if os.path.exists(MODEL_FILE):
            model = load_model(MODEL_FILE)
        else:
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

        # 5 epoch 동안 개선이 없으면 학습을 자동으로 중단
        # 가장 좋은 성능을 보인 가중치로 모델을 복원
        early_stopping = EarlyStopping(
            monitor='val_loss',  # 검증 손실을 모니터링
            patience=5,          # 5 epoch 동안 개선이 없으면 학습 중단
            restore_best_weights=True  # 가장 좋은 가중치로 복원
        )

        # 학습 과정의 히스토리를 저장
        history = model.fit(
            [X, decoder_start], 
            y, 
            epochs=50,           # 최대 50 epoch까지 학습
            batch_size=32, 
            validation_split=0.2,
            callbacks=[early_stopping]  # Early Stopping 적용
        )
        
        # 학습 곡선 시각화
        plot_training_history(history)

        model.save(MODEL_FILE)
        print("모델 학습 및 저장 완료")

    except ValueError as e:
        print(f"학습 오류: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")