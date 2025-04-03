import psutil
import time
from pynput import mouse, keyboard
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import threading
from .power_check import check_power    
from datetime import datetime

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

def start_collection():
    global mouse_count, keyboard_count
    mouse_count = 0
    keyboard_count = 0

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
        label = 1 if mouse_count + keyboard_count < 3 and cpu < 10 and disk < 10 else 0
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("data/user_log2.csv", "a") as log:
            log.write(f"{timestamp},{power},{mouse_count},{keyboard_count},{cpu},{disk},{label}\n")

        mouse_count = 0
        keyboard_count = 0
        
        # time.sleep 대신 wait 사용
        if stop_event.wait(60):  # 1분
            # 종료 시 리스너도 정지
            mouse_listener.stop()
            keyboard_listener.stop()
            return