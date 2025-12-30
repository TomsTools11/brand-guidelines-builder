# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Brand Guidelines Generator - A web tool that automatically generates professional brand guidelines PDFs from company website URLs. Users input a URL, the system extracts brand elements (colors, typography, logos), uses AI to generate brand content, and produces a downloadable PDF brand guide.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14)                         │
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

## Directory Structure

```
brand-guidelines-builder/
├── backend/
│   ├── pyproject.toml              # Python dependencies
│   ├── .env.example                # Environment variables template
│   ├── docker-compose.yml          # Redis for local dev
│   └── src/
│       ├── main.py                 # FastAPI app entry point
│       ├── config.py               # Pydantic settings
│       ├── celery_app.py           # Celery configuration
│       ├── models/
│       │   ├── brand_data.py       # ExtractedBrand, ColorPalette, Typography, etc.
│       │   └── job.py              # JobStatus, JobProgress
│       ├── api/
│       │   └── routes.py           # FastAPI endpoints
│       ├── workers/
│       │   └── tasks.py            # Celery extraction task
│       ├── scraper/
│       │   └── website_scraper.py  # Playwright-based scraper
│       ├── extractors/
│       │   ├── color_extractor.py  # CSS/image color extraction
│       │   ├── typography_extractor.py  # Font detection
│       │   ├── logo_extractor.py   # Logo finding/download
│       │   └── ai_analyzer.py      # Claude API brand content
│       ├── generator/
│       │   └── pdf_generator.py    # ReportLab PDF generation
│       └── utils/
│           └── color_utils.py      # Hex/RGB/CMYK/Pantone conversion
├── frontend/
│   ├── app/
│   │   ├── page.tsx                # URL input form
│   │   ├── extract/[jobId]/page.tsx  # Progress polling
│   │   └── preview/[jobId]/page.tsx  # Download page
│   ├── package.json
│   └── tailwind.config.ts
└── brand_guidelines_template.py    # Original template (reference)
```

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (or Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium

# Copy and configure environment
cp .env.example .env
# Edit .env to add:
#   ANTHROPIC_API_KEY=sk-ant-...
#   REDIS_URL=redis://localhost:6379/0

# Start Redis (local development)
docker compose up -d

# Start FastAPI server
uvicorn src.main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A src.celery_app worker --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs` | Create extraction job (body: `{"url": "..."}`) |
| GET | `/api/jobs/{id}` | Get job status and progress |
| GET | `/api/jobs/{id}/pdf` | Download generated PDF |
| GET | `/api/health` | Health check |

## Job Status Flow

```
PENDING → SCRAPING → EXTRACTING_COLORS → EXTRACTING_TYPOGRAPHY →
EXTRACTING_LOGO → GENERATING_CONTENT → BUILDING_PDF → COMPLETED
```

On failure: Any status → FAILED (with error_message)

## Key Models

### ExtractedBrand (brand_data.py)
Complete brand data structure containing:
- `company_name`, `tagline`, `domain`
- `colors`: ColorPalette (primary, secondary, accent, neutrals)
- `typography`: Typography (primary font, secondary, fallback)
- `logo`: LogoAsset (URL, binary data, format)
- AI-generated content: positioning, mission, vision, pillars, traits, voice guidelines

### JobProgress (job.py)
```python
class JobProgress:
    job_id: str
    status: JobStatus
    progress_percent: int
    current_step: str
    error_message: Optional[str]
    pdf_path: Optional[str]
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-...` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend | `http://localhost:8000` |

## Deployment (Railway)

1. **Backend Service**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
2. **Worker Service**: `celery -A src.celery_app worker --loglevel=info`
3. **Redis**: Use Railway Redis plugin
4. **Frontend**: Deploy to Vercel with `NEXT_PUBLIC_API_URL` pointing to Railway backend

## Testing a Full Flow

1. Start all services (Redis, FastAPI, Celery worker, Next.js)
2. Navigate to http://localhost:3000
3. Enter a URL (e.g., `https://stripe.com`)
4. Watch extraction progress (~1-2 minutes)
5. Download the generated PDF
