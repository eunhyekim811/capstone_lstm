# LSTM 모델을 이용한 사용자 패턴 예측

## 파일 구조

```
lstm/
│
├── data/                         # 로그 및 학습용 CSV 데이터 저장
│   └── user_log.csv
│
├── model/                        # 학습된 LSTM 모델 저장
│   └── idle_predictor_lstm.h5
│
├── utils/
│   ├── collect.py          # 사용자 활동 로그 수집 스크립트
│   ├── predict.py            # 시계열 데이터 전처리 함수
│   ├── preprocess.py           # LSTM 모델 학습 스크립트
│   ├── train_model.py       # 예측 후 자동 정리 작동 스크립트
│   └── cleanup.py               # 실제 파일 정리 기능 구현
│
├── scheduler.py           # 일정 시간마다 예측 → 정리 실행
├── requirements.txt             # 필요한 패키지 목록
└── README.md                    # 실행 방법 및 설명 문서
```