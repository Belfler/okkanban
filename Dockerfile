FROM python:3.9

ENV PYTHONBUFFERED=1

WORKDIR /code

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .
