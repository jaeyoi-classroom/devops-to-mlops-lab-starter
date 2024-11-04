import json
from datetime import datetime
from pathlib import Path
from pickle import load
from typing import Dict

import pandas as pd
from data import get_kospi_data
from kserve import Model, ModelServer


class KospiPredictionModel(Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.load()

    def load(self) -> bool:
        model_path = Path(__file__).parent / "kospi_model.pkl"
        with open(model_path, "rb") as f:
            self.model = load(f)
        self.df = get_kospi_data(60)

        return super().load()

    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        today_close = payload.inputs[0].data[0]
        today_df = pd.DataFrame({"Close": today_close}, index=[datetime.now().date()])

        # 5일 이동평균 및 20일 이동평균 계산
        last_five_days = pd.concat([self.df.tail(4), today_df])
        last_twenty_days = pd.concat([self.df.tail(19), today_df])
        ma5 = last_five_days["Close"].mean()
        ma20 = last_twenty_days["Close"].mean()

        input_data = pd.DataFrame(
            [[ma5, ma20]],
            columns=["MA5", "MA20"],
        )

        prob = self.model.predict_proba(input_data)[0]

        response = {"상승": prob[1], "하락": prob[0]}
        response_bytes = json.dumps(response).encode("UTF-8")

        return {
            "id": "x",
            "model_name": self.name,
            "outputs": [
                {
                    "name": "kospi-prediction-response",
                    "shape": [len(response_bytes)],
                    "datatype": "BYTES",
                    "data": [response_bytes],
                }
            ],
        }


if __name__ == "__main__":
    model = KospiPredictionModel("kospi-prediction-model")
    ModelServer().start([model])
