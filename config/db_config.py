import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 연결 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT'))
}

class DatabaseManager:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._connection is None:
            try:
                self._connection = mysql.connector.connect(**DB_CONFIG)
                print("데이터베이스 연결이 성공적으로 설정되었습니다.")
            except Error as e:
                print(f"데이터베이스 연결 오류: {e}")
                self._connection = None

    def get_connection(self):
        if self._connection is None or not self._connection.is_connected():
            try:
                self._connection = mysql.connector.connect(**DB_CONFIG)
            except Error as e:
                print(f"데이터베이스 재연결 오류: {e}")
                return None
        return self._connection

    def close(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

def init_db():
    db = DatabaseManager()
    connection = db.get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # 학생 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    uid INT AUTO_INCREMENT PRIMARY KEY,
                    mac BIGINT NOT NULL UNIQUE
                )
            """)
            
            # 사용자 활동 로그 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collectLog (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    uid INT,
                    timestamp DATETIME,
                    power_status INT,
                    mouse_count INT,
                    keyboard_count INT,
                    cpu_usage FLOAT,
                    disk_usage FLOAT,
                    is_idle BOOLEAN,
                    FOREIGN KEY (uid) REFERENCES user(uid)
                )
            """)
            
            # 예측 결과 로그 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictLog (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    uid INT,
                    timestamp DATETIME,
                    m1 INT, 
                    m2 INT,
                    m3 INT,
                    m4 INT,
                    m5 INT,
                    m6 INT,
                    FOREIGN KEY (uid) REFERENCES user(uid)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS count (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    uid INT,
                    last_training_time DATETIME,
                    FOREIGN KEY (uid) REFERENCES user(uid)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threshold (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    uid INT,
                    cpu_threshold FLOAT NOT NULL DEFAULT 0.0,
                    FOREIGN KEY (uid) REFERENCES user(uid)
                )
            """)
            
            connection.commit()
            print("데이터베이스와 테이블이 성공적으로 생성되었습니다.")
            
        except Error as e:
            print(f"테이블 생성 오류: {e}")
        finally:
            cursor.close()

def add_user(mac: int):
    db = DatabaseManager()
    connection = db.get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # MAC 주소가 이미 존재하는지 확인
            cursor.execute("SELECT uid FROM user WHERE mac = %s", (mac,))
            result = cursor.fetchone()
            
            if result is None:
                # MAC 주소가 없으면 새로 추가
                query = "INSERT INTO user (mac) VALUES (%s)"
                cursor.execute(query, (mac,))
                connection.commit()
                print(f"새로운 사용자({mac})가 성공적으로 추가되었습니다.")
                return cursor.lastrowid  # 새로 생성된 uid 반환
            else:
                # 이미 존재하는 경우 해당 uid 반환
                return result[0]
                
        except Error as e:
            print(f"사용자 추가 오류: {e}")
            return None
        finally:
            cursor.close() 

# thread 테이블에서 cpu_thread 조회
def get_cpu_thread(uid):
    db = DatabaseManager()
    connection = db.get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT cpu_threshold FROM threshold WHERE uid = %s"
            cursor.execute(query, (uid,))
            result = cursor.fetchone()
            if result:
                return result[0]  # cpu_threshold 값 반환
            return None
        except Error as e:
            print(f"CPU 임계값 조회 오류: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
    return None

# thread 테이블에 cpu_thread 저장 또는 업데이트
def save_cpu_thread(uid, cpu_thread_value):
    db = DatabaseManager()
    connection = db.get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # 먼저 해당 uid의 데이터가 있는지 확인
            cursor.execute("SELECT id FROM threshold WHERE uid = %s", (uid,))
            if cursor.fetchone():
                # 데이터가 있으면 UPDATE
                query = "UPDATE threshold SET cpu_threshold = %s WHERE uid = %s"
                values = (cpu_thread_value, uid)
            else:
                # 데이터가 없으면 INSERT
                query = "INSERT INTO threshold (uid, cpu_threshold) VALUES (%s, %s)"
                values = (uid, cpu_thread_value)
            cursor.execute(query, values)
            connection.commit()
            print(f"사용자 {uid}의 CPU 임계값 {cpu_thread_value} 저장/업데이트 완료.")
        except Error as e:
            print(f"CPU 임계값 저장 오류: {e}")
        finally:
            if connection.is_connected():
                cursor.close() 