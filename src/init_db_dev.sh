#!/usr/bin/env bash

docker stop videodl-db

docker rm videodl-db && docker volume rm postgres_videodl-db-data

docker compose -f postgres/compose.yml up --detach && \
sleep 2s && \
flask db upgrade && \
python3 seed_db_dev.py

echo "Done"