# LSTM 모델을 이용한 사용자 패턴 예측

## 파일 구조

```
lstm/
│
├── data/                           # 로그 및 학습용 CSV 데이터 저장
│   └── user_log.csv
│
├── model/                          # 학습된 LSTM 모델 저장
│   └── idle_predictor_lstm.keras
│
├── utils/
│   ├── collect.py                  # 사용자 활동 로그 수집 스크립트
│   ├── predict.py                  # 예측 후 자동 정리 작동 스크립트
│   ├── preprocess.py               # 시계열 데이터 전처리 함수
│   ├── train_model.py              # LSTM 모델 학습 스크립트
│   └── cleanup.py                  # 실제 파일 정리 기능 구현
│
├── main.py
├── cpu.py                          # cpu 부하 주는 용도
├── requirements.txt                # 필요한 패키지 목록
└── README.md                       # 실행 방법 및 설명 문서
```

## 실행 방법

```
pip install [필요 라이브러리]

python main.py
```

## LSTM

- RNN의 특별한 한 종류

    - RNN(순환 신경망) : 스스로 반복하며 이전 단계에서 얻은 정보 지속되도록 함

- Long Short-Term Memory(긴 단기 기억) - 더 긴 기간의 패턴 기억, 예측 가능

- 시계열 예측 기술

## ToDo

- 영상을 틀어놓는 경우 데이터 수집 어떻게 되는가? 

- 컴퓨터 꺼져 있는 경우는 학습 시 데이터 제외?

    - cpu==0, mouse==0, keyboard==0

    - 문제점 : 컴퓨터가 켜져 있는 경우에도 위와 같은 경우 존재

- 현재 10분 동안의 과거 데이터 이용해 현재 유휴 여부 판별

- 예측 시 결과(pred) : 0~1

    - 현재 pred > 0.5 인 경우 유휴 상태라 판단

    - 유휴 판단 기준 : (마우스 + 키보드 카운트 >= 3) & (cpu 사용률 >= 10%)

- 데이터 수집 형태 : timestamp, mouse, keyboard, cpu, label

    - timestamp : utc 기준 경과 초

    - label : 유휴 여부(0/1, 1: 유휴 상태)

    - 실시간으로 프로그램이 동작하는 동안 작동해 사용자 데이터 직접 수집
    
    - 데이터 100개 이상 모인 경우 모델 생성해 저장