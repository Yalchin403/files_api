from dotenv import load_dotenv
import os


load_dotenv()


class EnvPath:
    LOCAL = ".envs/.env.local"
    DEV = ".envs/.env.dev"
    TEST = ".envs/.env.test"
    STAGE = ".envs/.env.stage"
    PROD = ".envs/.env.prod"


FLASK_ENV = os.getenv("FLASK_ENV")


def get_env_file():
    if FLASK_ENV == "LOCAL":
        return EnvPath.LOCAL

    elif FLASK_ENV == "DEV":
        return EnvPath.DEV

    elif FLASK_ENV == "TEST":
        return EnvPath.TEST

    elif FLASK_ENV == "STAGE":
        return EnvPath.STAGE

    elif FLASK_ENV == "PROD":
        return EnvPath.PROD



