from pathlib import Path
from pickle import dump

from data import get_kospi_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


# 모델 학습
def train_model():
    df = get_kospi_data(days=2 * 365)
    X = df[["MA5", "MA20"]]
    y = df["Label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model


if __name__ == "__main__":
    model = train_model()

    with open(Path(__file__).parent / "kospi_model.pkl", "wb") as f:
        dump(model, f, protocol=5)
