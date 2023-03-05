import os
from dotenv import load_dotenv
from src.utils.load_env import get_env_file


env_file = get_env_file()
load_dotenv(env_file)
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    TESTING = True
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv("SECRET_KEY")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    SUMMARY_FOLDER = os.getenv("SUMMARY_FOLDER")
    FLASK_DEBUG = True


class LocalConfig(Config):
    LOCAL = True
    DEBUG = True
    CELERY_RESULT_DBURI = "sqlite:///temp.db"
    CELERY_TRACK_STARTED = True
    CELERY_SEND_EVENTS = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class StagingConfig(Config):
    STAGING = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
