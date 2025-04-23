import threading
import time
from utils.collect import start_collection, stop_event
from utils.train_model import train
from utils.predict import predict
from utils.evaluate import evaluate
from config.db_config import init_db, DatabaseManager

# 로그 수집 스레드
def run_data_collection():
    print(">> 사용자 로그 수집 시작")
    start_collection()

# 주기적 모델 학습 스레드
def run_training():
    while not stop_event.is_set():
        print(">> 모델 학습 대기 중 (10분마다 확인)")
        # 10분 대기하되, stop_event가 설정되면 즉시 종료
        if stop_event.wait(600):  # 10분 간격 학습
            return
        if not stop_event.is_set():
            train()

# 예측 및 파일 정리 스레드
def run_prediction():
    while not stop_event.is_set():
        print(">> 모델 예측 대기 중 (5분마다 확인)")
        # 5분 대기하되, stop_event가 설정되면 즉시 종료
        if stop_event.wait(300):  # 5분 간격 예측
            return
        if not stop_event.is_set():
            predict()

def run_evaluation():
    while not stop_event.is_set():
        print(">> 평가 대기 중 (15분마다 확인)")
        if stop_event.wait(900):  # 15분 간격 평가
            return
        if not stop_event.is_set():
            evaluate()

if __name__ == "__main__":

    # 데이터베이스 초기화
    init_db()

    try:
        t1 = threading.Thread(target=run_data_collection)
        t2 = threading.Thread(target=run_training)
        t3 = threading.Thread(target=run_prediction)
        t4 = threading.Thread(target=run_evaluation)

        t1.start()
        t2.start()
        t3.start()
        t4.start()

        # 메인 스레드는 대기
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(">> 종료 요청됨. 스레드를 정리합니다...")
        stop_event.set()

        t1.join()
        t2.join()
        t3.join()
        t4.join()

        # 데이터베이스 연결 종료
        DatabaseManager().close()

        print(">> 프로그램이 정상적으로 종료되었습니다.")