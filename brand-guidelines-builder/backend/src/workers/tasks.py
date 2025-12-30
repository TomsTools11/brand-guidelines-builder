"""
Celery tasks for brand extraction pipeline.
"""

import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse

import redis
from bs4 import BeautifulSoup

from ..celery_app import celery_app
from ..config import settings
from ..models.job import JobStatus
from ..models.brand_data import ExtractedBrand

# Redis client for job status updates
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def update_job_status(
    job_id: str,
    status: JobStatus,
    progress: int,
    step: str,
    **kwargs
):
    """Update job status in Redis."""
    # Get existing job data
    existing = redis_client.get(f"job:{job_id}")
    job_data = json.loads(existing) if existing else {}

    # Update fields
    job_data.update({
        "job_id": job_id,
        "status": status.value,
        "progress_percent": progress,
        "current_step": step,
        **kwargs
    })

    redis_client.set(f"job:{job_id}", json.dumps(job_data), ex=86400)


@celery_app.task(bind=True, max_retries=2)
def extract_brand_task(self, job_id: str, url: str):
    """
    Main extraction pipeline as Celery task.

    Steps:
    1. Scrape website
    2. Extract colors
    3. Extract typography
    4. Extract logo
    5. Generate AI content
    6. Build PDF
    """
    try:
        # Step 1: Scrape
        update_job_status(job_id, JobStatus.SCRAPING, 10, "Scraping website...")

        from ..scraper.website_scraper import WebsiteScraper

        async def do_scrape():
            async with WebsiteScraper() as scraper:
                return await scraper.scrape(url)

        scraped = asyncio.run(do_scrape())

        # Step 2: Extract colors
        update_job_status(
            job_id, JobStatus.EXTRACTING_COLORS, 30,
            "Extracting colors..."
        )

        from ..extractors.color_extractor import ColorExtractor

        color_extractor = ColorExtractor()
        all_css = (
            scraped.pages['home'].css_contents +
            scraped.external_css
        )
        colors = color_extractor.extract(all_css, [])

        # Step 3: Extract typography
        update_job_status(
            job_id, JobStatus.EXTRACTING_TYPOGRAPHY, 45,
            "Analyzing typography..."
        )

        from ..extractors.typography_extractor import TypographyExtractor

        typography_extractor = TypographyExtractor()
        typography = typography_extractor.extract(
            scraped.pages['home'].html,
            all_css
        )

        # Step 4: Extract logo
        update_job_status(
            job_id, JobStatus.EXTRACTING_LOGO, 55,
            "Finding logo..."
        )

        from ..extractors.logo_extractor import LogoExtractor

        logo_extractor = LogoExtractor()

        async def do_extract_logo():
            return await logo_extractor.extract(
                scraped.pages['home'].html,
                scraped.base_url,
                scraped.meta
            )

        logo = asyncio.run(do_extract_logo())

        # Build initial brand data
        domain = urlparse(url).netloc
        company_name = (
            scraped.meta.get('ogTitle') or
            scraped.meta.get('title') or
            domain.split('.')[0].title()
        )

        # Clean company name
        company_name = company_name.split('|')[0].split('-')[0].strip()

        brand_data = ExtractedBrand(
            company_name=company_name,
            domain=domain,
            colors=colors,
            typography=typography,
            logo=logo
        )

        # Step 5: AI content generation
        update_job_status(
            job_id, JobStatus.GENERATING_CONTENT, 70,
            "Generating brand content with AI..."
        )

        # Extract text from scraped pages
        text_content = ""
        for page_name, page in scraped.pages.items():
            soup = BeautifulSoup(page.html, 'html.parser')

            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer']):
                element.decompose()

            text_content += soup.get_text(separator=' ', strip=True) + "\n\n"

        from ..extractors.ai_analyzer import AIAnalyzer

        ai_analyzer = AIAnalyzer(api_key=settings.ANTHROPIC_API_KEY)

        async def do_analyze():
            return await ai_analyzer.analyze(text_content, company_name, brand_data)

        brand_data = asyncio.run(do_analyze())

        # Step 6: Generate PDF
        update_job_status(
            job_id, JobStatus.BUILDING_PDF, 90,
            "Building PDF..."
        )

        output_dir = Path(settings.PDF_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{job_id}.pdf"

        from ..generator.pdf_generator import BrandGuidelinesPDF

        pdf_generator = BrandGuidelinesPDF(brand_data)
        pdf_generator.generate(str(output_path))

        # Complete
        update_job_status(
            job_id, JobStatus.COMPLETED, 100,
            "Complete!",
            pdf_path=str(output_path)
        )

        return {"status": "completed", "pdf_path": str(output_path)}

    except Exception as e:
        update_job_status(
            job_id, JobStatus.FAILED, 0,
            "Failed",
            error_message=str(e)
        )
        # Re-raise to mark task as failed
        raise
