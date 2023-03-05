from src.utils.get_config_cls import get_conf_cls
from dotenv import load_dotenv
import os
from flask import Flask

load_dotenv()
config_cls = get_conf_cls()
app = Flask(__name__)
app.app_context().push()
app.config.from_object(f"src.config.{config_cls}")


os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["SUMMARY_FOLDER"], exist_ok=True)

from src.routes import apis
