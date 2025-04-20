
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY src/app.py app.py
COPY src/recovery.py recovery.py
COPY src/migrations migrations
COPY src/App App

RUN mkdir -p /artifacts /logs
RUN chmod 777 /artifacts /logs
VOLUME ["/artifacts", "/logs"]

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]