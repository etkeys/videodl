from dotenv import load_dotenv
from os import environ

load_dotenv()


class Config:
    APP_DB_ADDRESS = environ.get("VIDEODL_DB_ADDRESS")
    APP_DB_CATALOG = environ.get("VIDEODL_DB_CATALOG")
    APP_DB_PASSWORD = environ.get("VIDEODL_DB_PASSWORD")
    APP_DB_USER = environ.get("VIDEODL_DB_USER")
    APP_DEBUG_MODE = environ.get("VIDEODL_APP_DEBUG_MODE")
    APP_DIR_ARTIFACTS = environ.get("VIDEODL_DIR_ARTIFACTS")
    APP_DIR_LOGS = environ.get("VIDEODL_DIR_LOGS")
    APP_ENVIRONMENT = environ.get("VIDEODL_ENVIRONMENT")
    APP_NAME = environ.get("VIDEODL_APP_NAME")
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_PROTECTION = environ.get("SESSION_PROTECTION")
    WORKER_DEFAULT_WAIT_SECONDS = environ.get("VIDEODL_WORKER_DEFAULT_WAIT_SECONDS")
