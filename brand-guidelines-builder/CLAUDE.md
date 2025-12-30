# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Brand Guidelines Generator - A web tool that automatically generates professional brand guidelines PDFs from company website URLs. Users input a URL, the system extracts brand elements (colors, typography, logos), uses AI to generate brand content, and produces a downloadable PDF brand guide.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 16)                         │
│  URL Input → Progress Polling → Preview → Download               │
└─────────────────────────────────────────────────────────────────┘
                                │ HTTP
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│  POST /api/jobs          - Start extraction job                  │
│  GET  /api/jobs/{id}     - Poll job status                       │
│  GET  /api/jobs/{id}/pdf - Download generated PDF                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CELERY WORKER                                 │
│  Scraper → ColorExtractor → TypographyExtractor →               │
│  LogoExtractor → AIAnalyzer → PDFGenerator                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │    Redis    │
                         │  (Broker +  │
                         │   Backend)  │
                         └─────────────┘
```

## Development Commands

### Backend (from `backend/` directory)

```bash
# Setup (first time)
python -m venv venv
source venv/bin/activate
pip install -e .
pip install -e ".[dev]"
playwright install chromium
cp .env.example .env  # Then add ANTHROPIC_API_KEY

# Start Redis
docker compose up -d

# Run FastAPI server
uvicorn src.main:app --reload --port 8000

# Run Celery worker (separate terminal)
celery -A src.celery_app worker --loglevel=info

# Linting
ruff check src/
ruff format src/

# Testing
pytest tests/
pytest tests/test_specific.py -v  # Single test file
```

### Frontend (from `frontend/` directory)

```bash
# Setup
npm install

# Development server
npm run dev

# Linting
npm run lint

# Build
npm run build
```

### Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Job Status Flow

```
PENDING → SCRAPING → EXTRACTING_COLORS → EXTRACTING_TYPOGRAPHY →
EXTRACTING_LOGO → GENERATING_CONTENT → BUILDING_PDF → COMPLETED
```

On failure: Any status → FAILED (with error_message)

## Key Backend Modules

| Module | Location | Purpose |
|--------|----------|---------|
| API Routes | `src/api/routes.py` | FastAPI endpoints |
| Celery Tasks | `src/workers/tasks.py` | Background job orchestration |
| Website Scraper | `src/scraper/website_scraper.py` | Playwright-based scraping |
| Color Extractor | `src/extractors/color_extractor.py` | CSS/image color extraction |
| Typography Extractor | `src/extractors/typography_extractor.py` | Font detection |
| Logo Extractor | `src/extractors/logo_extractor.py` | Logo finding/download |
| AI Analyzer | `src/extractors/ai_analyzer.py` | Claude API brand content |
| PDF Generator | `src/generator/pdf_generator.py` | ReportLab PDF generation |
| Brand Data Models | `src/models/brand_data.py` | ExtractedBrand, ColorPalette, Typography |
| Job Models | `src/models/job.py` | JobStatus, JobProgress |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key (required) |
| `REDIS_URL` | Redis connection URL (default: `redis://localhost:6379/0`) |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend (default: `http://localhost:8000`) |

## Deployment (Railway)

1. **Backend Service**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
2. **Worker Service**: `celery -A src.celery_app worker --loglevel=info`
3. **Redis**: Use Railway Redis plugin
4. **Frontend**: Deploy to Vercel with `NEXT_PUBLIC_API_URL` pointing to Railway backend
