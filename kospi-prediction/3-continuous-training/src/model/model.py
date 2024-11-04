import json
from datetime import datetime
from pathlib import Path
from pickle import load
from typing import Dict

import pandas as pd
from data import get_kospi_data
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from kserve import Model, ModelServer
from prometheus_client import Gauge

# Prometheus 메트릭 설정
data_drift_metric_ma5 = Gauge("data_drift_score_ma5", "Data drift 점수 (MA5)")
data_drift_metric_ma20 = Gauge("data_drift_score_ma20", "Data drift 점수 (MA20)")


class KospiPredictionModel(Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.load()

        self.predictions = pd.DataFrame(columns=["MA5", "MA20", "prediction", "actual"])
        # Evidently Reports 설정
        self.data_drift_report = Report(metrics=[DataDriftPreset()])

    def load(self) -> bool:
        model_path = Path(__file__).parent / "kospi_model.pkl"
        with open(model_path, "rb") as f:
            self.model = load(f)
        self.df = get_kospi_data(60)
        self.df["prediction"] = self.df["Label"]

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

        # 예측 결과 기록
        self.predictions = pd.concat(
            [
                self.predictions,
                pd.DataFrame(
                    {
                        "MA5": [ma5],
                        "MA20": [ma20],
                        "prediction": [int(prob[1] > 0.5)],
                        "actual": [None],
                    }
                ),
            ],
            ignore_index=True,
        )
        self.update_metrics()

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

    def update_metrics(self):
        # Evidently 리포트 업데이트
        self.data_drift_report.run(
            reference_data=self.df[["MA5", "MA20", "prediction"]],
            current_data=self.predictions,
        )
        drift_results = self.data_drift_report.as_dict()
        data_drift_score_ma5 = drift_results["metrics"][1]["result"][
            "drift_by_columns"
        ]["MA5"]["drift_score"]
        data_drift_score_ma20 = drift_results["metrics"][1]["result"][
            "drift_by_columns"
        ]["MA20"]["drift_score"]

        # Prometheus 메트릭 갱신
        data_drift_metric_ma5.set(data_drift_score_ma5)
        data_drift_metric_ma20.set(data_drift_score_ma20)


if __name__ == "__main__":
    model = KospiPredictionModel("kospi-prediction-model")
    ModelServer().start([model])
