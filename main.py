import threading
import time
import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from utils.collect import start_collection, stop_event
from utils.train_model import train
from utils.predict import predict
from utils.evaluate import evaluate
from config.db_config import init_db, DatabaseManager

# 스케줄러 객체 생성
scheduler = BackgroundScheduler()

# 로그 수집 스레드
def run_data_collection():
    try:
        print(">> 사용자 로그 수집 시작")
        start_collection()
    except BaseException:
        print(">> EXCEPTION in run_data_collection thread:")
        traceback.print_exc()
    finally:
        print(">> THREAD TERMINATED: run_data_collection")

# 주기적 모델 학습 스레드
def run_training():
    try:
        while not stop_event.is_set():
            print(">> 모델 학습 대기 중 (20분마다 확인)")
            # 10분 대기하되, stop_event가 설정되면 즉시 종료
            if stop_event.wait(1200):  # 20분 간격 학습
                break
            if not stop_event.is_set():
                train()
    except BaseException:
        print(">> EXCEPTION in run_training thread:")
        traceback.print_exc()
    finally:
        print(">> THREAD TERMINATED: run_training")

# 예측 및 파일 정리 스레드
def run_prediction(scheduler):
    try:
        while not stop_event.is_set():
            print(">> 모델 예측 대기 중 (30분마다 확인)")
            # 5분 대기하되, stop_event가 설정되면 즉시 종료
            if stop_event.wait(1800):  # 30분 간격 예측
                break
            if not stop_event.is_set():
                predict(scheduler)
    except BaseException:
        print(">> EXCEPTION in run_prediction thread:")
        traceback.print_exc()
    finally:
        print(">> THREAD TERMINATED: run_prediction")

def run_evaluation():
    try:
        while not stop_event.is_set():
            print(">> 평가 대기 중 (60분마다 확인)")
            if stop_event.wait(3600):  # 60분 간격 평가
                break
            if not stop_event.is_set():
                evaluate()
    except BaseException:
        print(">> EXCEPTION in run_evaluation thread:")
        traceback.print_exc()
    finally:
        print(">> THREAD TERMINATED: run_evaluation")

if __name__ == "__main__":

    # 데이터베이스 초기화
    init_db()

    # 스케줄러 시작
    scheduler.start()

    # 초기 샘플 수집해 임계값 설정 -> start_collection 내부에서 처리하도록 변경
    # cpu_threshold, disk_threshold = calibrate(duration=300, interval=10) # 기존 코드

    # calibrate 함수 결과를 담을 리스트 -> 더 이상 필요 없음
    # calibration_results = []

    # calibrate 함수를 실행하고 결과를 calibration_results 리스트에 저장하는 래퍼 함수 -> 더 이상 필요 없음
    # def run_calibrate_in_thread(duration, interval, results_list):
    #     cpu_thresh, disk_thresh = calibrate(duration, interval)
    #     results_list.append(cpu_thresh)
    #     results_list.append(disk_thresh)

    # calibrate 함수를 위한 스레드 생성 및 시작 -> 더 이상 필요 없음
    # t_calibrate = threading.Thread(target=run_calibrate_in_thread, args=(300, 10, calibration_results))
    # t_calibrate.start()
    # t_calibrate.join() # calibrate 스레드가 완료될 때까지 대기

    # calibrate 스레드로부터 결과 가져오기 -> 더 이상 필요 없음
    # cpu_threshold = calibration_results[0]
    # disk_threshold = calibration_results[1]

    try:
        t1 = threading.Thread(target=run_data_collection)
        t2 = threading.Thread(target=run_training)
        t3 = threading.Thread(target=run_prediction, args=(scheduler,))
        # t4 = threading.Thread(target=run_evaluation)

        t1.start()
        t2.start()
        t3.start()
        # t4.start()

        # 메인 스레드는 대기
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(">> 종료 요청됨. 스레드를 정리합니다...")
        stop_event.set()

        t1.join()
        t2.join()
        t3.join()
        # t4.join()

        # 스케줄러 종료
        scheduler.shutdown()

        # 데이터베이스 연결 종료
        DatabaseManager().close()

        print(">> 프로그램이 정상적으로 종료되었습니다.")

    except BaseException:
        print(">> UNHANDLED EXCEPTION in main thread, terminating.")
        traceback.print_exc()
    finally:
        print(">> Main thread is exiting.")