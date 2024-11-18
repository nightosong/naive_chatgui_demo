FROM python:3.11.9-slim
ENV TZ=Asia/Shanghai

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt