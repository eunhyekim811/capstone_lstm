import schedule
import time
from utils.predict import predict

schedule.every(5).minutes.do(predict)

print("LSTM 기반 유휴 감지 시스템 작동 중...")

while True:
    schedule.run_pending()
    time.sleep(1)