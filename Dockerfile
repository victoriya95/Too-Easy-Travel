FROM python:3.11

WORKDIR /app

COPY . .

RUN set -ex \
    && pip install -r requirements.txt

ARG TELEGRAM_API_TOKEN

ENTRYPOINT ["python", "main.py"]
