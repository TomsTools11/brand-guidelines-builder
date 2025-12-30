"""
Website scraper using Playwright for JavaScript-rendered pages.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse, urljoin

import httpx
from playwright.async_api import async_playwright, Browser, Page


@dataclass
class ScrapedPage:
    """Data from a single scraped page."""
    url: str
    html: str
    css_contents: list[str] = field(default_factory=list)
    screenshot: Optional[bytes] = None


@dataclass
class ScrapedData:
    """Complete scraped data from a website."""
    base_url: str
    pages: dict[str, ScrapedPage] = field(default_factory=dict)
    external_css: list[str] = field(default_factory=list)
    images: list[tuple[str, bytes]] = field(default_factory=list)
    meta: dict = field(default_factory=dict)


class WebsiteScraper:
    """Scraper for extracting brand elements from websites."""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self._playwright = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(self, *args):
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def scrape(self, url: str) -> ScrapedData:
        """
        Main entry point - scrapes website and returns all data.

        Args:
            url: The website URL to scrape

        Returns:
            ScrapedData containing HTML, CSS, screenshots, and metadata
        """
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'

        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()

        try:
            # Scrape homepage
            home_data = await self._scrape_page(page, url)
            pages = {'home': home_data}

            # Extract meta tags from homepage
            meta = await self._extract_meta(page)

            # Find and scrape key pages (about, contact)
            key_pages = await self._find_key_pages(page, url)

            for page_name, page_url in key_pages.items():
                try:
                    pages[page_name] = await self._scrape_page(page, page_url)
                except Exception:
                    continue  # Skip pages that fail

            # Download external CSS
            css_urls = await self._find_css_urls(page)
            external_css = await self._download_css(css_urls)

            return ScrapedData(
                base_url=url,
                pages=pages,
                external_css=external_css,
                images=[],  # Populated by logo extractor
                meta=meta
            )

        finally:
            await context.close()

    async def _scrape_page(self, page: Page, url: str) -> ScrapedPage:
        """Scrape a single page."""
        await page.goto(url, wait_until='networkidle', timeout=30000)

        # Wait for any lazy-loaded content
        await page.wait_for_timeout(1000)

        html = await page.content()

        # Get inline styles
        css_contents = await page.evaluate('''
            () => Array.from(document.querySelectorAll('style'))
                       .map(s => s.textContent || '')
                       .filter(s => s.length > 0)
        ''')

        # Take screenshot for AI analysis
        screenshot = await page.screenshot(full_page=True, type='png')

        return ScrapedPage(
            url=url,
            html=html,
            css_contents=css_contents,
            screenshot=screenshot
        )

    async def _find_key_pages(self, page: Page, base_url: str) -> dict[str, str]:
        """Find about/contact pages from navigation."""
        links = await page.evaluate('''
            () => Array.from(document.querySelectorAll('a[href]'))
                       .map(a => ({
                           text: (a.textContent || '').toLowerCase().trim(),
                           href: a.href
                       }))
                       .filter(a => a.href && a.text)
        ''')

        base_domain = urlparse(base_url).netloc

        key_pages = {}
        patterns = {
            'about': ['about', 'about-us', 'who-we-are', 'our-story', 'company'],
            'contact': ['contact', 'contact-us', 'get-in-touch', 'reach-us'],
        }

        for page_type, keywords in patterns.items():
            for link in links:
                link_domain = urlparse(link['href']).netloc

                # Only follow internal links
                if link_domain and link_domain != base_domain:
                    continue

                if any(kw in link['text'] or kw in link['href'].lower() for kw in keywords):
                    # Ensure absolute URL
                    href = link['href']
                    if not href.startswith('http'):
                        href = urljoin(base_url, href)
                    key_pages[page_type] = href
                    break

        return key_pages

    async def _extract_meta(self, page: Page) -> dict:
        """Extract meta tags and other page metadata."""
        return await page.evaluate('''
            () => ({
                title: document.title || '',
                description: document.querySelector('meta[name="description"]')?.content || '',
                ogImage: document.querySelector('meta[property="og:image"]')?.content || '',
                ogTitle: document.querySelector('meta[property="og:title"]')?.content || '',
                ogDescription: document.querySelector('meta[property="og:description"]')?.content || '',
                favicon: document.querySelector('link[rel="icon"]')?.href ||
                         document.querySelector('link[rel="shortcut icon"]')?.href || '',
                appleTouchIcon: document.querySelector('link[rel="apple-touch-icon"]')?.href || '',
            })
        ''')

    async def _find_css_urls(self, page: Page) -> list[str]:
        """Find external CSS file URLs."""
        return await page.evaluate('''
            () => Array.from(document.querySelectorAll('link[rel="stylesheet"]'))
                       .map(link => link.href)
                       .filter(href => href && href.startsWith('http'))
        ''')

    async def _download_css(self, urls: list[str]) -> list[str]:
        """Download external CSS files."""
        css_contents = []

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for url in urls[:10]:  # Limit to 10 CSS files
                try:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        css_contents.append(resp.text)
                except Exception:
                    continue

        return css_contents


async def scrape_website(url: str) -> ScrapedData:
    """
    Convenience function to scrape a website.

    Args:
        url: The website URL to scrape

    Returns:
        ScrapedData containing all extracted data
    """
    async with WebsiteScraper() as scraper:
        return await scraper.scrape(url)
