from celery import Celery
from config import Config

def make_celery(app_name=__name__):
    """Crée et configure l'instance Celery"""
    celery = Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['app.tasks.reporting']
    )

    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Europe/Paris',
        enable_utc=True,
        broker_connection_retry_on_startup=True
    )

    return celery

celery = make_celery()

if __name__ == '__main__':
    celery.start()
