from datetime import datetime
from pathlib import Path
from pickle import load

import gradio as gr
import pandas as pd
from data import get_kospi_data

df = get_kospi_data(60)
with open(Path(__file__).parent / "kospi_model.pkl", "rb") as f:
    model = load(f)


# 예측 함수 (오늘 종가만 입력받음)
def predict_kospi(today_close):
    today_df = pd.DataFrame({"Close": today_close}, index=[datetime.now().date()])

    # 5일 이동평균 및 20일 이동평균 계산
    last_five_days = pd.concat([df.tail(4), today_df])
    last_twenty_days = pd.concat([df.tail(19), today_df])
    ma5 = last_five_days["Close"].mean()
    ma20 = last_twenty_days["Close"].mean()

    input_data = pd.DataFrame(
        [[ma5, ma20]],
        columns=["MA5", "MA20"],
    )

    prob = model.predict_proba(input_data)[0]
    return {"상승": prob[1], "하락": prob[0]}


# Gradio 인터페이스
inputs = gr.Number(label="오늘의 종가")
outputs = gr.JSON(label="예측 결과")

gr.Interface(
    fn=predict_kospi,
    inputs=inputs,
    outputs="label",
    flagging_options=["Incorrect"],
    title="KOSPI 지수 예측",
    description="오늘의 종가만 입력하면 내일의 KOSPI 지수 상승/하락 확률을 예측합니다",
).launch()
