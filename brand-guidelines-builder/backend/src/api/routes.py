"""
FastAPI routes for the brand guide generator API.
"""

import json
import uuid
from datetime import datetime

import redis
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl

from ..config import settings
from ..models.job import JobStatus

router = APIRouter(prefix="/api")

# Redis client for job storage
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class ExtractRequest(BaseModel):
    """Request body for starting an extraction job."""
    url: HttpUrl


class JobResponse(BaseModel):
    """Response for job creation."""
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    """Response for job status queries."""
    job_id: str
    status: str
    progress_percent: int
    current_step: str
    error_message: str | None = None
    pdf_path: str | None = None


def get_job(job_id: str) -> dict | None:
    """Get job from Redis."""
    data = redis_client.get(f"job:{job_id}")
    if data:
        return json.loads(data)
    return None


def set_job(job_id: str, job_data: dict):
    """Store job in Redis with 24h TTL."""
    redis_client.set(f"job:{job_id}", json.dumps(job_data), ex=86400)


@router.post("/jobs", response_model=JobResponse)
async def create_job(request: ExtractRequest):
    """
    Start a new brand extraction job.

    The job will be processed asynchronously by a Celery worker.
    Poll the /jobs/{job_id} endpoint to check status.
    """
    job_id = str(uuid.uuid4())

    # Initialize job in Redis
    set_job(job_id, {
        "job_id": job_id,
        "status": JobStatus.PENDING.value,
        "progress_percent": 0,
        "current_step": "Queued for processing",
        "created_at": datetime.now().isoformat(),
        "url": str(request.url),
    })

    # Queue Celery task
    from ..workers.tasks import extract_brand_task
    extract_brand_task.delay(job_id, str(request.url))

    return JobResponse(job_id=job_id, status=JobStatus.PENDING.value)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status and progress of an extraction job.

    Poll this endpoint to track job progress.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress_percent=job.get("progress_percent", 0),
        current_step=job.get("current_step", ""),
        error_message=job.get("error_message"),
        pdf_path=job.get("pdf_path"),
    )


@router.get("/jobs/{job_id}/pdf")
async def download_pdf(job_id: str):
    """
    Download the generated PDF for a completed job.

    Returns 400 if the job is not yet complete.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.get("status") != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400,
            detail=f"PDF not ready. Current status: {job.get('status')}"
        )

    pdf_path = job.get("pdf_path")
    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"brand_guidelines_{job_id[:8]}.pdf"
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        redis_client.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    return {
        "status": "healthy",
        "redis": redis_status,
    }
