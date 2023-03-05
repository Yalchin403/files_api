from celery import Celery
from src import app

celery = Celery(app.name, broker="redis://redis:6379/0", backend="redis://redis:6379/0")
celery.conf.update(app.config)
