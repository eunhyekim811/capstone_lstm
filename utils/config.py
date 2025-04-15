import os

# 현재 파일의 절대 경로를 기준으로 베이스 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 데이터, 모델, 로그 디렉토리
DATA_DIR = "data"
MODEL_DIR = "model"
LOG_DIR = "logs"

# 디렉토리가 없으면 생성
for directory in [DATA_DIR, MODEL_DIR, LOG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# 각 파일 경로 정의
USER_LOG_FILE = "data/user_log.csv"
MODEL_FILE = "model/idle_predictor.keras"
PREDICTIONS_LOG_FILE = "logs/predictions.csv"
