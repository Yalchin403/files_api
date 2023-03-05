from dotenv import load_dotenv
import os


load_dotenv()


class ConfigClass:
    LOCAL = "LocalConfig"
    DEV = "DevelopmentConfig"
    TEST = "TestingConfig"
    STAGE = "StagingConfig"
    PROD = "ProductionConfig"


FLASK_ENV = os.getenv("FLASK_ENV")


def get_conf_cls():
    if FLASK_ENV == "LOCAL":
        return ConfigClass.LOCAL

    elif FLASK_ENV == "DEV":
        return ConfigClass.DEV

    elif FLASK_ENV == "TEST":
        return ConfigClass.TEST

    elif FLASK_ENV == "STAGE":
        return ConfigClass.STAGE

    elif FLASK_ENV == "PROD":
        return ConfigClass.PROD



