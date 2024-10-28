from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


# 데이터 수집 및 전처리
def get_kospi_data(days) -> pd.DataFrame:
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=days)
    df = yf.download(
        "^KS11",
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        group_by="ticker",
    )["^KS11"]
    df["Label"] = df["Close"].diff().apply(lambda x: 1 if x > 0 else 0)
    df["MA5"] = df["Close"].rolling(window=5).mean()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["Volatility"] = (df["High"] - df["Low"]) / df["Low"]
    df.dropna(inplace=True)
    return df
