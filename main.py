import threading
import time
from utils.collect_data import start_collection
from utils.train_model import train
from utils.predict_and_act import predict

# 로그 수집 스레드
def run_data_collection():
    print(">> 사용자 로그 수집 시작")
    start_collection()

# 주기적 모델 학습 스레드
def run_training():
    while True:
        print(">> 모델 학습 대기 중 (10분마다 확인)")
        time.sleep(600)  # 10분 간격
        train()

# 예측 및 파일 정리 스레드
def run_prediction():
    while True:
        time.sleep(300)  # 5분 간격
        predict()

if __name__ == "__main__":
    threading.Thread(target=run_data_collection).start()
    threading.Thread(target=run_training).start()
    threading.Thread(target=run_prediction).start()