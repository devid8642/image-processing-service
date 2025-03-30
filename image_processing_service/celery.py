from celery import Celery

from image_processing_service.settings import settings

celery_app = Celery(
    'image_processing_service',
    broker=settings.CELERY_BROKER_URL,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    timezone='UTC',
)

celery_app.autodiscover_tasks(['image_processing_service.tasks'])
