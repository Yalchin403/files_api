from celery import Celery

celery = Celery(
    "worker", broker="redis://0.0.0.0:6379/0", backend="redis://0.0.0.0:6379/0"
)
