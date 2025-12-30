"""Celery workers module."""

from .tasks import extract_brand_task

__all__ = ["extract_brand_task"]
