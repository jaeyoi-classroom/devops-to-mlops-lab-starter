import json
import os

import gradio as gr
import requests


# KServe로 요청을 보내는 함수
def predict(today_close):
    url = os.getenv("MODEL_API_URL")
    payload = {
        "inputs": [
            {
                "name": "today_close",
                "shape": [1],
                "datatype": "integer",
                "data": [today_close],
            }
        ]
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        j = response.json()
        return json.loads(j["outputs"][0]["data"][0])
    else:
        return f"Error: {response.status_code}"


# Gradio 인터페이스
inputs = gr.Number(label="오늘의 종가")
outputs = gr.JSON(label="예측 결과")


gr.Interface(
    fn=predict,
    inputs=inputs,
    outputs="label",
    flagging_options=["Incorrect"],
    title="KOSPI 지수 예측",
    description="오늘의 종가만 입력하면 내일의 KOSPI 지수 상승/하락 확률을 예측합니다",
).launch()
