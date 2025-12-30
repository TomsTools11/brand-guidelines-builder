"""
Celery application configuration for background job processing.
"""

from celery import Celery
from .config import settings

celery_app = Celery(
    "brand_guide_generator",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.workers.tasks"]
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task tracking
    task_track_started=True,

    # Limits
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=270,  # Soft limit at 4.5 minutes

    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time (extraction is heavy)
    worker_concurrency=2,  # Max 2 concurrent extractions

    # Result settings
    result_expires=86400,  # Results expire after 24 hours
)
