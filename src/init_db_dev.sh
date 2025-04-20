#!/usr/bin/env bash

docker compose rm --stop --force
echo "Removing volume..." && docker volume rm videodl-development_videodl-db-data

docker compose up --detach && \
echo "Waiting for DB to start..." && \
sleep 2s && \
echo "Applying migrations..." && \
flask db upgrade && \
python3 seed_db_dev.py

echo "Done"