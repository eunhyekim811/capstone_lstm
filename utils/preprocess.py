import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import uuid
from config.db_config import DatabaseManager

def get_user_id():
    """현재 컴퓨터의 MAC 주소에 해당하는 uid를 반환"""
    db = DatabaseManager()
    connection = db.get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            mac = uuid.getnode()  # MAC 주소 전체 사용
            cursor.execute("SELECT uid FROM user WHERE mac = %s", (mac,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"사용자 ID 조회 오류: {e}")
            return None
        finally:
            cursor.close()

# 슬라이딩 윈도우 형태의 시계열 데이터로 구성
def load_and_preprocess(window_size=20, future_steps=6):
    # 현재 사용자의 uid 가져오기
    uid = get_user_id()
    if uid is None:
        raise ValueError("사용자 ID를 찾을 수 없습니다.")

    # 데이터베이스에서 데이터 가져오기
    db = DatabaseManager()
    connection = db.get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # 해당 사용자의 데이터만 가져오기
            query = """
                SELECT timestamp, power_status, mouse_count, keyboard_count, 
                       cpu_usage, disk_usage, is_idle 
                FROM collectLog 
                WHERE uid = %s 
                ORDER BY timestamp
            """
            cursor.execute(query, (uid,))
            columns = ["timestamp", "power", "mouse", "keyboard", "cpu", "disk", "label"]
            data = cursor.fetchall()
            
            if not data:
                raise ValueError("수집된 데이터가 없습니다.")
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(data, columns=columns)
            
            # 전원이 켜진 데이터만 사용
            df = df[df["power"] == 1]

            features = df[["mouse", "keyboard", "cpu", "disk"]]     # 입력값 X
            target = df["label"]    # 예측값(유휴 여부) y

            # 정규화(입력값들을 0~1 사이로 변환)
            scaler = MinMaxScaler()
            features_scaled = scaler.fit_transform(features)

            # 시계열 데이터 구성
            # 연속된 과거 window_size개의 입력값으로, 그 다음 시점의 유휴 상태 예측
            X, y = [], []
            # window_size 이후부터 future_steps 타임스텝까지 예측
            for i in range(len(df) - window_size - future_steps + 1):
                X.append(features_scaled[i:i+window_size])      # 과거 10분 입력값
                y.append(target.iloc[i+window_size:i+window_size+future_steps].values)     # 그 다음 시간의 유휴 여부

            return np.array(X), np.array(y), scaler
            
        except Error as e:
            print(f"데이터 조회 오류: {e}")
            raise
        finally:
            cursor.close()