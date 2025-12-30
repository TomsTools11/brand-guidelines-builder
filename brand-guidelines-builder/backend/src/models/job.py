"""
Job tracking models for the extraction pipeline.
"""

from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional


class JobStatus(str, Enum):
    """Status values for extraction jobs."""
    PENDING = "pending"
    SCRAPING = "scraping"
    EXTRACTING_COLORS = "extracting_colors"
    EXTRACTING_TYPOGRAPHY = "extracting_typography"
    EXTRACTING_LOGO = "extracting_logo"
    GENERATING_CONTENT = "generating_content"
    BUILDING_PDF = "building_pdf"
    COMPLETED = "completed"
    FAILED = "failed"


class JobProgress(BaseModel):
    """Progress tracking for an extraction job."""
    job_id: str
    status: JobStatus
    progress_percent: int = 0
    current_step: str = ""
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    pdf_path: Optional[str] = None
