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

- 평가 과정 구축

- 통합