FROM python:3.12-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 모델 피클 생성
RUN python training.py

EXPOSE 8080

CMD ["python", "model.py"]