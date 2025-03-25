import psutil
import time
from pynput import mouse, keyboard
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

# 마우스, 키보드 입력 감지지
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
    mouse_count = 0
    keyboard_count = 0

    # 마우스/키보드 리스너 등록
    MouseListener(on_move=on_move, on_click=on_click).start()
    KeyboardListener(on_press=on_press).start()

    # 1분 간격으로 현재 상태 기록
    while True:
        cpu = psutil.cpu_percent()  # CPU 사용률
        label = 1 if mouse_count + keyboard_count < 3 and cpu < 10 else 0   #유휴 여부

        with open("data/user_log.csv", "a") as log:
            log.write(f"{time.time()},{mouse_count},{keyboard_count},{cpu},{label}\n")

        mouse_count = 0
        keyboard_count = 0
        time.sleep(60)