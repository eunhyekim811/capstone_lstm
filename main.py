import threading
import time
from utils.collect import start_collection, stop_event
from utils.train_model import train
from utils.predict import predict

# 로그 수집 스레드
def run_data_collection():
    print(">> 사용자 로그 수집 시작")
    start_collection()

# 주기적 모델 학습 스레드
def run_training():
    while not stop_event.is_set():
        print(">> 모델 학습 대기 중 (10분마다 확인)")
        # 10분 대기하되, stop_event가 설정되면 즉시 종료
        if stop_event.wait(600):  # 10분
            return
        if not stop_event.is_set():
            train()

# 예측 및 파일 정리 스레드
def run_prediction():
    while not stop_event.is_set():
        print(">> 모델 예측 대기 중 (5분마다 확인)")
        # 5분 대기하되, stop_event가 설정되면 즉시 종료
        if stop_event.wait(300):  # 5분
            return
        if not stop_event.is_set():
            predict()

if __name__ == "__main__":
    try:
        t1 = threading.Thread(target=run_data_collection)
        t2 = threading.Thread(target=run_training)
        t3 = threading.Thread(target=run_prediction)

        t1.start()
        t2.start()
        t3.start()

        # 메인 스레드는 대기
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(">> 종료 요청됨. 스레드를 정리합니다...")
        stop_event.set()

        t1.join()
        t2.join()
        t3.join()

        print(">> 프로그램이 정상적으로 종료되었습니다.")