import psutil
import time
from pynput import mouse, keyboard
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import threading
from .power_check import check_power    
from datetime import datetime
import uuid
from config.db_config import DatabaseManager, add_user

mouse_count = 0
keyboard_count = 0

# 전역 stop_event 변수 생성
stop_event = threading.Event()

# 마우스, 키보드 입력 감지
def on_move(x, y): 
    global mouse_count
    mouse_count += 1
def on_click(x, y, button, pressed): 
    global mouse_count
    mouse_count += 1
def on_press(key):
    global keyboard_count
    keyboard_count += 1

def save_to_db(timestamp, power, mouse_count, keyboard_count, cpu, disk, label, uid):
    db = DatabaseManager()
    connection = db.get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            query = """
                INSERT INTO collectLog 
                (uid, timestamp, power_status, mouse_count, keyboard_count, cpu_usage, disk_usage, is_idle)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (uid, timestamp, power, mouse_count, keyboard_count, cpu, disk, bool(label))
            cursor.execute(query, values)
            connection.commit()
        except Error as e:
            print(f"데이터 저장 오류: {e}")
        finally:
            cursor.close()

def start_collection():
    global mouse_count, keyboard_count
    mouse_count = 0
    keyboard_count = 0

    # MAC 주소를 기반으로 사용자 등록 및 uid 가져오기
    mac = uuid.getnode()  # MAC 주소를 정수로 사용
    uid = add_user(mac)
    
    print(mac)

    if uid is None:
        print("사용자 등록 실패. 데이터 수집을 중단합니다.")
        return

    # 마우스/키보드 리스너 등록
    mouse_listener = MouseListener(on_move=on_move, on_click=on_click)
    keyboard_listener = KeyboardListener(on_press=on_press)
    
    mouse_listener.start()
    keyboard_listener.start()

    # 1분 간격으로 현재 상태 기록
    while not stop_event.is_set():
        power = check_power()
        cpu = psutil.cpu_percent()  # CPU 사용률
        disk = psutil.disk_usage('/').percent  # 디스크 사용률
        
        # 유휴 여부
        # 마우스 클릭 수와 키보드 입력 수의 합이 3보다 작음 + cpu 사용률 10% 미만 + 디스크 사용률 10% 미만 -> 유휴
        label = 1 if mouse_count + keyboard_count < 5 and cpu < 1.0 and disk < 30 else 0
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 데이터베이스에 저장
        save_to_db(timestamp, power, mouse_count, keyboard_count, cpu, disk, label, uid)

        mouse_count = 0
        keyboard_count = 0
        
        # time.sleep 대신 wait 사용
        if stop_event.wait(60):  # 1분
            # 종료 시 리스너도 정지
            mouse_listener.stop()
            keyboard_listener.stop()
            return