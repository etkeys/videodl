from dotenv import load_dotenv
from os import environ

load_dotenv()


class Config:
    DATABASE_URL = environ.get("DATABASE_URL")
    APP_DEBUG_MODE = environ.get("FLASK_DEBUG", 0)
    APP_DIR_ARTIFACTS = environ.get("VIDEODL_DIR_ARTIFACTS", "/artifacts")
    APP_DIR_LOGS = environ.get("VIDEODL_DIR_LOGS", "/logs")
    APP_ENVIRONMENT = environ.get("VIDEODL_ENVIRONMENT")
    APP_NAME = environ.get("VIDEODL_APP_NAME", "Video DL")
    SECRET_KEY = environ.get("WEB_SECRET_KEY")
    SESSION_PROTECTION = "strong"
    WORKER_MIN_IDLE_TIMEOUT_SECONDS = environ.get(
        "WORKER_MIN_IDLE_TIMEOUT_SECONDS",
        240
    )
    WORKER_MAX_IDLE_TIMEOUT_SECONDS = environ.get(
        "WORKER_MAX_IDLE_TIMEOUT_SECONDS",
        300
    )
