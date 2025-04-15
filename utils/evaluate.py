import os
import csv
from datetime import datetime, timedelta
import numpy as np
from .config import PREDICTIONS_LOG_FILE, USER_LOG_FILE

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def evaluate():
    # 예측 결과 로그 파일 읽기
    prediction_log_path = PREDICTIONS_LOG_FILE
    actual_log_path = USER_LOG_FILE

    if not os.path.exists(prediction_log_path):
        print("예측 로그 파일이 존재하지 않습니다.")
        return
    if not os.path.exists(actual_log_path):
        print("실제 결과 로그 파일이 존재하지 않습니다.")
        return

    # 예측 결과 로그 파일 읽기
    predictions = {}
    with open(prediction_log_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue

            timestamp, pred = row[0], row[1]
            try:
                pred_time = datetime.strptime(timestamp, TIME_FORMAT)
            except Exception as e:
                print(f"예측 결과 형식 오류: {e}")
                continue

            predictions[pred_time] = list(map(int, pred.split(";")))

    # 실제 결과 로그 파일 읽기
    actuals = []
    with open(actual_log_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 7:
                continue

            try:
                actual_time = datetime.strptime(row[0], TIME_FORMAT)
            except Exception as e:
                print(f"실제 결과 형식 오류: {e}")
                continue
            
            try:
                label = int(row[-1])
            except Exception as e:
                print(f"라벨 변환 오류: {e}")
                continue
            actuals.append((actual_time, label))

    # 예측 결과와 실제 결과 비교
    accuracy = []
    if predictions:
        seq_length = len(next(iter(predictions.values())))
    else:
        print("예측 로그가 없습니다.")
        return

    for pred_time, pred_seq in predictions.items():
        start_time = pred_time
        end_time = pred_time + timedelta(minutes=seq_length)

        # 실제 결과 중 해당 시간대에 속하는 데이터 추출
        actual_values = [label for (actual_time, label) in actuals if start_time <= actual_time <= end_time]
        if len(actual_values) < seq_length:
            print("실제 결과 시간대에 데이터가 부족합니다.")
            continue
        
        actual_seq = actual_values[:seq_length]
        seq_acc = np.mean(np.array(pred_seq) == np.array(actual_seq))
        accuracy.append(seq_acc)
        
    if accuracy:
        overall_acc = np.mean(accuracy)
        print(f"전체 시퀀스 정확도 (전체 {len(accuracy)}개 예측): {overall_acc:.4f}")
    else:
        print("정확도 계산 불가")
        
