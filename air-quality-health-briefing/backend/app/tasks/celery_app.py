from celery import Celery
from app.config import settings

celery_app = Celery(
    "air_quality_briefing",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.briefing_tasks',
        'app.tasks.pdf_report_tasks'
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
