import time
import psutil
import multiprocessing
import signal
from datetime import datetime

def load_cpu(target_load, stop_event):
    # 자식 프로세스의 시그널 핸들러 설정
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    interval = 1
    busy_time = interval * target_load
    idle_time = interval - busy_time

    try:
        while True:  # stop_event.is_set() 체크를 루프 안으로 이동
            if stop_event.is_set():  # 여기서 한 번만 체크
                break
            
            start = time.time()
            while (time.time() - start) < busy_time:
                sum([i**0.5 for i in range(10000)])
            stop_event.wait(idle_time)
    except KeyboardInterrupt:
        pass

def print_cpu_usage(stop_event):
    try:
        while True:  # stop_event.is_set() 체크를 루프 안으로 이동
            if stop_event.is_set():  # 여기서 한 번만 체크
                break
                
            print(f"[{time.strftime('%H:%M:%S')}] 현재 CPU 사용률: {psutil.cpu_percent()}%")
            stop_event.wait(1)
        print(">> 모니터링 종료")
    except KeyboardInterrupt:
        pass

def run_periodic_load(duration=1, interval=5):
    """
    duration: CPU 부하를 실행할 시간 (초)
    interval: 다음 실행까지 대기할 시간 (초)
    """
    stop_event = multiprocessing.Event()
    processes = []
    num_cores = multiprocessing.cpu_count()

    try:
        while True:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n▶️ [{current_time}] CPU 부하 테스트 시작 (코어 수: {num_cores})")
            
            # CPU 부하 프로세스 시작
            for _ in range(6):
                p = multiprocessing.Process(target=load_cpu, args=(0.5, stop_event))
                p.start()
                processes.append(p)

            # CPU 사용률 모니터링 프로세스 시작
            monitor = multiprocessing.Process(target=print_cpu_usage, args=(stop_event,))
            monitor.start()
            processes.append(monitor)

            try:
                # 지정된 시간동안 실행
                time.sleep(duration)
                
                # 정상 종료
                stop_event.set()
                for p in processes:
                    p.join(timeout=1)
                    if p.is_alive():
                        p.terminate()
                
                # 프로세스 리스트 및 이벤트 초기화
                processes.clear()
                stop_event.clear()
                
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"\n>> [{current_time}] 테스트 완료. {interval}초 후 다시 시작합니다.")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                raise  # 외부 try-except 블록으로 전달

    except KeyboardInterrupt:
        print("\n>> 종료 요청됨. 프로세스를 정리합니다...")
        try:
            stop_event.set()
            for p in processes:
                try:
                    p.join(timeout=1)
                    if p.is_alive():
                        p.terminate()
                except:
                    pass  # 프로세스 종료 중 발생하는 오류 무시
        except:
            pass  # 세마포어 관련 오류 무시
        print(">> 프로그램이 정상적으로 종료되었습니다.")

if __name__ == "__main__":
    # 1분 실행, 5분 대기 주기로 실행 (원하는 시간으로 수정 가능)
    run_periodic_load(duration=15, interval=900)
