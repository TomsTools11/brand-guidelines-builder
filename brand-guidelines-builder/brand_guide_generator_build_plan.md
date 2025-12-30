# Brand Guidelines Generator - Build Plan

## Project Overview

A web-based tool that automatically generates professional brand guidelines from any company website URL. Users input a URL, the system extracts brand elements (colors, typography, logos, imagery patterns), and produces a downloadable PDF brand guide following the CreditKey-style template.

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React/Next.js)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  URL Input  │→ │  Progress   │→ │  Overview   │→ │  Download   │ │
│  │    Page     │  │   Tracker   │  │    Page     │  │    PDF      │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND API (Python/FastAPI)                 │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      /api/extract-brand                          ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ ││
│  │  │  Scraper │→ │  Parser  │→ │ Analyzer │→ │ Content Generator│ ││
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      /api/generate-pdf                           ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ ││
│  │  │ Template     │→ │ ReportLab    │→ │ PDF Storage/Delivery   │ ││
│  │  │ Population   │  │ Generation   │  │ (S3/Local)             │ ││
│  │  └──────────────┘  └──────────────┘  └────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES & AI                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Playwright │  │   Claude    │  │   Google    │  │  Font API   │ │
│  │  (Scraping) │  │   (AI/LLM)  │  │   Fonts     │  │  Detection  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation & Scraping Engine
**Timeline: Week 1-2**

### 1.1 Project Setup
- [ ] Initialize Python project with Poetry/uv for dependency management
- [ ] Set up FastAPI backend structure
- [ ] Configure environment variables and secrets management
- [ ] Set up logging and error tracking (Sentry optional)
- [ ] Create Docker development environment

### 1.2 Web Scraping Module
**File: `src/scraper/website_scraper.py`**

| Component | Purpose | Technology |
|-----------|---------|------------|
| Page Fetcher | Load full page with JS rendering | Playwright |
| Multi-page Crawler | Navigate key pages (Home, About, Contact) | Playwright |
| Screenshot Capture | Visual backup for AI analysis | Playwright |
| Asset Downloader | Fetch CSS, images, fonts | httpx/aiohttp |

**Key Functions:**
```python
async def scrape_website(url: str) -> ScrapedData:
    """
    Main entry point for website scraping.
    Returns: HTML, CSS, images, fonts, screenshots, metadata
    """

async def fetch_page_with_js(url: str) -> str:
    """Render JavaScript and return full HTML."""

async def crawl_key_pages(base_url: str) -> List[PageData]:
    """Identify and scrape: home, about, products, contact."""

async def download_assets(urls: List[str]) -> Dict[str, bytes]:
    """Download CSS files, images, font files."""
```

### 1.3 Data Models
**File: `src/models/brand_data.py`**

```python
@dataclass
class ScrapedData:
    url: str
    html_content: Dict[str, str]  # page_name: html
    css_content: List[str]
    images: List[ImageAsset]
    fonts: List[FontAsset]
    screenshots: Dict[str, bytes]
    metadata: SiteMetadata

@dataclass
class ExtractedBrand:
    company_name: str
    tagline: Optional[str]
    colors: ColorPalette
    typography: TypographySpec
    logo: LogoAsset
    imagery_style: str
    voice_tone: VoiceTone
    mission: Optional[str]
    vision: Optional[str]
    values: List[str]
```

---

## Phase 2: Extraction & Analysis Engine
**Timeline: Week 2-3**

### 2.1 Color Extraction Module
**File: `src/extractors/color_extractor.py`**

| Method | Data Source | Output |
|--------|-------------|--------|
| CSS Parsing | Stylesheets | All declared colors |
| Image Analysis | Logo, hero images | Dominant colors via ColorThief |
| Frequency Analysis | Combined | Primary, secondary, accent ranking |
| Contrast Validation | Color pairs | WCAG accessibility scores |

**Key Functions:**
```python
def extract_colors_from_css(css: str) -> List[HexColor]:
    """Parse all color declarations from CSS."""

def extract_colors_from_image(image: bytes) -> List[HexColor]:
    """Use ColorThief to get dominant colors."""

def build_color_palette(colors: List[HexColor]) -> ColorPalette:
    """Rank and categorize: primary, secondary, accent, neutrals."""

def convert_color_formats(hex: str) -> ColorSpec:
    """Return HEX, RGB, CMYK, and suggest Pantone match."""
```

### 2.2 Typography Extraction Module
**File: `src/extractors/typography_extractor.py`**

| Method | Data Source | Output |
|--------|-------------|--------|
| CSS Font Parsing | @font-face, font-family | Font names and sources |
| Google Fonts Detection | Link tags, CSS imports | Google Font identifiers |
| Hierarchy Analysis | h1-h6, p, body styles | Size/weight hierarchy |
| Fallback Identification | font-family stacks | System font alternatives |

**Key Functions:**
```python
def extract_fonts_from_css(css: str) -> List[FontSpec]:
    """Parse font-family declarations and @font-face rules."""

def detect_google_fonts(html: str, css: str) -> List[str]:
    """Identify Google Fonts via API links."""

def build_typography_hierarchy(css: str) -> TypographySpec:
    """Map heading levels to font specs."""
```

### 2.3 Logo Extraction Module
**File: `src/extractors/logo_extractor.py`**

| Method | Data Source | Priority |
|--------|-------------|----------|
| Meta Tags | og:image, logo schema | High |
| Header Scan | <header> img elements | High |
| SVG Detection | Inline SVG, .svg files | Medium |
| Favicon Fallback | Favicon, apple-touch-icon | Low |

**Key Functions:**
```python
def extract_logo(html: str, base_url: str) -> LogoAsset:
    """Multi-strategy logo detection and download."""

def detect_logo_variations(images: List[ImageAsset]) -> LogoVariations:
    """Identify dark/light/badge versions if available."""
```

### 2.4 AI Content Generation Module
**File: `src/extractors/ai_analyzer.py`**

**Claude API Integration for:**

| Content Type | Input | Output |
|--------------|-------|--------|
| Company Description | About page text, meta | Positioning statement |
| Mission/Vision | About page, homepage | Inferred mission & vision |
| Brand Personality | All text content | 4 personality traits |
| Voice & Tone | Blog posts, copy samples | Voice characteristics |
| Brand Pillars | Products/services pages | 3 brand pillars |
| Boilerplate | All extracted content | Short & long boilerplate |

**Key Functions:**
```python
async def analyze_brand_content(scraped: ScrapedData) -> BrandContent:
    """Use Claude to generate all text content for brand guide."""

async def generate_brand_personality(text_samples: List[str]) -> List[Trait]:
    """Identify 4 personality traits with descriptions."""

async def generate_voice_guidelines(text_samples: List[str]) -> VoiceTone:
    """Create voice IS/IS NOT table with examples."""

async def infer_mission_vision(about_text: str) -> Tuple[str, str]:
    """Generate mission and vision statements."""
```

**Prompt Engineering Notes:**
- Use structured output (JSON mode) for consistency
- Include CreditKey examples as few-shot examples
- Validate outputs match expected schema
- Implement retry logic for malformed responses

---

## Phase 3: PDF Generation Engine
**Timeline: Week 3-4**

### 3.1 Template Population
**File: `src/generator/template_populator.py`**

```python
def populate_brand_config(extracted: ExtractedBrand) -> Dict[str, Any]:
    """
    Map extracted brand data to template placeholders.
    Returns config dict matching BRAND_CONFIG structure.
    """

def validate_brand_config(config: Dict) -> ValidationResult:
    """Ensure all required fields are populated."""

def apply_brand_colors_to_template(config: Dict) -> Dict:
    """Override template colors with extracted brand colors."""
```

### 3.2 PDF Generation
**File: `src/generator/pdf_generator.py`**

Refactor existing `brand_guidelines_template.py` into:

```python
class BrandGuidelinesPDF:
    def __init__(self, brand_config: Dict[str, Any]):
        self.config = brand_config
        self.styles = self._create_styles()
    
    def generate(self, output_path: str) -> str:
        """Generate complete PDF and return file path."""
    
    def _create_cover_page(self) -> List[Flowable]:
        """Generate cover page elements."""
    
    # ... other section methods
```

### 3.3 Asset Embedding
**File: `src/generator/asset_handler.py`**

```python
def embed_logo(logo_asset: LogoAsset) -> Image:
    """Prepare logo for PDF embedding with proper sizing."""

def create_color_swatches(colors: ColorPalette) -> List[Flowable]:
    """Generate visual color swatch boxes."""

def embed_screenshot_samples(screenshots: Dict) -> List[Flowable]:
    """Include website screenshots as work samples."""
```

---

## Phase 4: API & Backend
**Timeline: Week 4-5**

### 4.1 FastAPI Application Structure

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── extract.py       # POST /api/extract-brand
│   │   ├── generate.py      # POST /api/generate-pdf
│   │   └── status.py        # GET /api/job/{job_id}
│   └── dependencies.py
├── scraper/
│   └── website_scraper.py
├── extractors/
│   ├── color_extractor.py
│   ├── typography_extractor.py
│   ├── logo_extractor.py
│   └── ai_analyzer.py
├── generator/
│   ├── template_populator.py
│   ├── pdf_generator.py
│   └── asset_handler.py
├── models/
│   └── brand_data.py
├── workers/
│   └── celery_tasks.py      # Background job processing
└── utils/
    ├── color_utils.py
    └── font_utils.py
```

### 4.2 API Endpoints

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/extract-brand` | POST | Start extraction job | `{job_id, status}` |
| `/api/job/{job_id}` | GET | Check job status | `{status, progress, data?}` |
| `/api/generate-pdf/{job_id}` | POST | Generate PDF from job | `{pdf_url}` |
| `/api/download/{job_id}` | GET | Download PDF file | PDF binary |

### 4.3 Background Processing

Use **Celery + Redis** for long-running extraction jobs:

```python
@celery.task
def extract_brand_task(url: str) -> ExtractedBrand:
    """
    Background task pipeline:
    1. Scrape website (30-60s)
    2. Extract colors (5s)
    3. Extract typography (5s)
    4. Extract logo (5s)
    5. AI content generation (15-30s)
    6. Return combined results
    """
```

---

## Phase 5: Frontend Application
**Timeline: Week 5-6**

### 5.1 Technology Stack
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS
- **State:** React Query for API state
- **Components:** shadcn/ui

### 5.2 Page Structure

```
app/
├── page.tsx                  # Landing + URL input
├── extract/
│   └── [jobId]/
│       └── page.tsx          # Progress tracking
├── preview/
│   └── [jobId]/
│       └── page.tsx          # Brand overview + download
└── api/
    └── [...proxy]/
        └── route.ts          # API proxy (optional)
```

### 5.3 User Flow & Components

```
┌──────────────────────────────────────────────────────────────────┐
│  PAGE 1: URL INPUT                                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  "Generate Brand Guidelines"                                │  │
│  │  ┌──────────────────────────────────┐ ┌─────────────────┐  │  │
│  │  │  https://example.com             │ │  Generate →     │  │  │
│  │  └──────────────────────────────────┘ └─────────────────┘  │  │
│  │  Example: Paste any company website URL                     │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  PAGE 2: EXTRACTION PROGRESS                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Analyzing acme.com...                                      │  │
│  │  ════════════════════════════░░░░░░░░  65%                 │  │
│  │                                                             │  │
│  │  ✓ Website scraped                                          │  │
│  │  ✓ Colors extracted (5 colors found)                        │  │
│  │  ✓ Typography identified (Inter, System)                    │  │
│  │  ● Generating brand content...                              │  │
│  │  ○ Building PDF                                             │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  PAGE 3: BRAND OVERVIEW + DOWNLOAD                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  ACME Corporation Brand Guidelines                          │  │
│  │                                                             │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │  │
│  │  │ ██ Primary  │ │ ██ Second.  │ │ ██ Accent   │  COLORS   │  │
│  │  │ #1a1a2e     │ │ #4a4a6a     │ │ #0066ff     │           │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘           │  │
│  │                                                             │  │
│  │  Typography: Inter (Primary), Arial (System)                │  │
│  │                                                             │  │
│  │  Brand Personality: Innovative, Trusted, Bold, Human        │  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐   │  │
│  │  │              📄 Download Full Brand Guide            │   │  │
│  │  │                    (47 pages, PDF)                   │   │  │
│  │  └─────────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 5.4 Key Components

| Component | Purpose |
|-----------|---------|
| `<URLInput />` | Validated URL input with submit |
| `<ProgressTracker />` | Real-time job status with steps |
| `<ColorPaletteDisplay />` | Visual color swatches |
| `<TypographyPreview />` | Font specimen display |
| `<BrandOverviewCard />` | Summary of extracted brand |
| `<DownloadButton />` | PDF download with loading state |

---

## Phase 6: Deployment & Production
**Timeline: Week 6-7**

### 6.1 Infrastructure Options

| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **Vercel + Railway** | Easy deploy, serverless | Cold starts, timeout limits | $20-50/mo |
| **AWS (ECS + Lambda)** | Scalable, reliable | Complex setup | $50-100/mo |
| **DigitalOcean Apps** | Simple, predictable | Less serverless | $25-50/mo |

**Recommended: Vercel (Frontend) + Railway (Backend + Workers)**

### 6.2 Environment Configuration

```bash
# Backend (.env)
ANTHROPIC_API_KEY=sk-ant-...
REDIS_URL=redis://...
DATABASE_URL=postgresql://...
S3_BUCKET=brand-guides-pdfs
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.brandguide.tool
```

### 6.3 Production Checklist

- [ ] Rate limiting on API endpoints
- [ ] Input validation and sanitization
- [ ] Error handling and user-friendly messages
- [ ] PDF storage with expiration (7-day retention)
- [ ] Monitoring and alerting (Sentry, LogTail)
- [ ] CORS configuration
- [ ] SSL/HTTPS everywhere
- [ ] Health check endpoints

---

## Technical Specifications

### Dependencies

**Backend (Python 3.11+):**
```toml
[dependencies]
fastapi = "^0.109"
uvicorn = "^0.27"
playwright = "^1.41"
httpx = "^0.26"
beautifulsoup4 = "^4.12"
colorthief = "^0.2"
reportlab = "^4.1"
anthropic = "^0.18"
celery = "^5.3"
redis = "^5.0"
pydantic = "^2.6"
boto3 = "^1.34"  # For S3 storage
```

**Frontend (Node 20+):**
```json
{
  "dependencies": {
    "next": "^14.1",
    "react": "^18.2",
    "@tanstack/react-query": "^5.0",
    "tailwindcss": "^3.4",
    "@radix-ui/react-progress": "^1.0"
  }
}
```

### Performance Targets

| Operation | Target Time | Notes |
|-----------|-------------|-------|
| Page scrape | < 30s | Playwright with timeout |
| Color extraction | < 5s | CSS parsing + image analysis |
| Typography extraction | < 3s | CSS parsing only |
| AI content generation | < 45s | Claude API call |
| PDF generation | < 15s | ReportLab rendering |
| **Total extraction** | **< 2 minutes** | End-to-end |

### Error Handling Strategy

| Error Type | User Message | Action |
|------------|--------------|--------|
| Invalid URL | "Please enter a valid website URL" | Inline validation |
| Site unreachable | "We couldn't access this website" | Suggest retry |
| Scrape timeout | "This site took too long to load" | Offer simplified extraction |
| AI failure | "Content generation failed" | Use fallback templates |
| PDF failure | "PDF creation failed" | Retry with simplified template |

---

## Development Milestones

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| 1 | Project setup + scraping | Working Playwright scraper |
| 2 | Extraction modules | Colors, typography, logo extraction |
| 3 | AI integration | Claude-powered content generation |
| 4 | PDF generation | Complete PDF from extracted data |
| 5 | API + backend | Full FastAPI backend with Celery |
| 6 | Frontend | Complete Next.js application |
| 7 | Integration + deploy | Production deployment |
| 8 | Testing + polish | Bug fixes, UX improvements |

---

## Future Enhancements (v2.0)

- [ ] **User accounts** - Save and manage generated guides
- [ ] **Edit before download** - Inline editing of extracted content
- [ ] **Multiple templates** - Different industry/style templates
- [ ] **White-label** - Custom branding for agencies
- [ ] **Bulk processing** - Multiple URLs at once
- [ ] **Brand comparison** - Compare two brand guides
- [ ] **Export formats** - DOCX, Figma, Notion in addition to PDF
- [ ] **API access** - Programmatic brand extraction for developers

---

## Getting Started

```bash
# Clone and setup
git clone https://github.com/your-org/brand-guide-generator
cd brand-guide-generator

# Backend setup
cd backend
poetry install
playwright install chromium
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Start Redis (for Celery)
docker run -d -p 6379:6379 redis:alpine

# Start backend
poetry run uvicorn src.api.main:app --reload

# Start Celery worker (separate terminal)
poetry run celery -A src.workers.celery_tasks worker --loglevel=info

# Frontend setup (separate terminal)
cd ../frontend
npm install
cp .env.example .env.local
npm run dev
```

---

## Questions to Resolve

1. **Hosting preference?** Vercel/Railway vs self-hosted vs AWS?
2. **User authentication needed?** Anonymous vs accounts?
3. **Storage duration?** How long to keep generated PDFs?
4. **Rate limiting?** Requests per user/IP?
5. **Pricing model?** Free vs freemium vs paid?

---

*Document Version: 1.0*  
*Last Updated: December 2024*
