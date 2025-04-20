
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY src/worker_run.py worker.py
COPY src/App App

RUN mkdir -p /artifacts /logs
RUN chmod 774 /artifacts /logs
VOLUME ["/artifacts", "/logs"]

RUN apt-get update && apt-get install -y \
    ffmpeg

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "worker.py"]