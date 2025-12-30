"""
Logo extraction from HTML and meta tags.
"""

import json
import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from ..models.brand_data import LogoAsset


class LogoExtractor:
    """Extract logo from various sources in a webpage."""

    LOGO_PATTERNS = ['logo', 'brand', 'mark', 'icon']

    async def extract(
        self,
        html: str,
        base_url: str,
        meta: dict
    ) -> LogoAsset:
        """
        Extract logo from various sources.

        Args:
            html: HTML content of the page
            base_url: Base URL of the website
            meta: Metadata dict from scraper

        Returns:
            LogoAsset with URL and optional binary data
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Priority 1: Schema.org logo
        logo_url = self._find_schema_logo(soup)

        # Priority 2: og:image (if looks like logo)
        if not logo_url and meta.get('ogImage'):
            og_image = meta['ogImage']
            if any(p in og_image.lower() for p in self.LOGO_PATTERNS):
                logo_url = og_image

        # Priority 3: Header/nav images with logo keywords
        if not logo_url:
            logo_url = self._find_header_logo(soup, base_url)

        # Priority 4: SVG with logo class/id
        if not logo_url:
            logo_url = self._find_svg_logo(soup, base_url)

        # Priority 5: Favicon/apple-touch-icon as last resort
        if not logo_url:
            logo_url = self._find_favicon(soup, base_url, meta)

        # Download the logo
        logo_data = None
        if logo_url:
            logo_data = await self._download_image(logo_url)

        return LogoAsset(
            primary_url=logo_url,
            primary_data=logo_data,
            format=self._detect_format(logo_url) if logo_url else 'png'
        )

    def _find_schema_logo(self, soup: BeautifulSoup) -> str | None:
        """Find logo from schema.org markup."""
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                if not script.string:
                    continue
                data = json.loads(script.string)

                # Handle array of schemas
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'logo' in item:
                            logo = item['logo']
                            if isinstance(logo, str):
                                return logo
                            elif isinstance(logo, dict):
                                return logo.get('url') or logo.get('contentUrl')
                elif isinstance(data, dict):
                    if 'logo' in data:
                        logo = data['logo']
                        if isinstance(logo, str):
                            return logo
                        elif isinstance(logo, dict):
                            return logo.get('url') or logo.get('contentUrl')
            except (json.JSONDecodeError, TypeError):
                continue

        # Microdata
        logo_elem = soup.find(itemprop='logo')
        if logo_elem:
            return logo_elem.get('src') or logo_elem.get('content') or logo_elem.get('href')

        return None

    def _find_header_logo(self, soup: BeautifulSoup, base_url: str) -> str | None:
        """Find logo image in header/nav."""
        # Look in header, nav, or first section
        containers = [
            soup.find('header'),
            soup.find('nav'),
            soup.find(class_=re.compile(r'header|nav', re.I)),
            soup.find(id=re.compile(r'header|nav', re.I)),
        ]

        for container in containers:
            if not container:
                continue

            # Check images
            for img in container.find_all('img'):
                src = img.get('src', '')
                alt = (img.get('alt', '') or '').lower()
                classes = ' '.join(img.get('class', [])).lower()
                img_id = (img.get('id', '') or '').lower()

                if any(p in src.lower() or p in alt or p in classes or p in img_id
                       for p in self.LOGO_PATTERNS):
                    return urljoin(base_url, src)

            # Check links with images
            for link in container.find_all('a'):
                img = link.find('img')
                if img:
                    link_class = ' '.join(link.get('class', [])).lower()
                    if any(p in link_class for p in self.LOGO_PATTERNS):
                        return urljoin(base_url, img.get('src', ''))

        return None

    def _find_svg_logo(self, soup: BeautifulSoup, base_url: str) -> str | None:
        """Find SVG logo element."""
        # Check for SVG elements with logo-related attributes
        for svg in soup.find_all('svg'):
            classes = ' '.join(svg.get('class', [])).lower()
            svg_id = (svg.get('id', '') or '').lower()

            if any(p in classes or p in svg_id for p in self.LOGO_PATTERNS):
                # For inline SVGs, we'd need to serialize them
                # Skip for MVP - would need data URI conversion
                continue

        # Check for .svg file links
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if '.svg' in src.lower():
                if any(p in src.lower() for p in self.LOGO_PATTERNS):
                    return urljoin(base_url, src)

        return None

    def _find_favicon(
        self,
        soup: BeautifulSoup,
        base_url: str,
        meta: dict
    ) -> str | None:
        """Find favicon/apple-touch-icon."""
        # Apple touch icon (usually higher res) from meta
        if meta.get('appleTouchIcon'):
            return meta['appleTouchIcon']

        # Apple touch icon from HTML
        apple_icon = soup.find('link', rel=re.compile(r'apple-touch-icon'))
        if apple_icon and apple_icon.get('href'):
            return urljoin(base_url, apple_icon['href'])

        # Favicon from meta
        if meta.get('favicon'):
            return meta['favicon']

        # Standard favicon
        favicon = soup.find('link', rel=re.compile(r'^icon$|^shortcut icon$'))
        if favicon and favicon.get('href'):
            return urljoin(base_url, favicon['href'])

        # Default favicon.ico
        return urljoin(base_url, '/favicon.ico')

    async def _download_image(self, url: str) -> bytes | None:
        """Download image data."""
        try:
            async with httpx.AsyncClient(
                timeout=15.0,
                follow_redirects=True
            ) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    content_type = resp.headers.get('content-type', '')
                    if 'image' in content_type or url.endswith(('.png', '.jpg', '.jpeg', '.svg', '.ico')):
                        return resp.content
        except Exception:
            pass
        return None

    def _detect_format(self, url: str) -> str:
        """Detect image format from URL."""
        url_lower = url.lower()
        if '.svg' in url_lower:
            return 'svg'
        elif '.png' in url_lower:
            return 'png'
        elif '.jpg' in url_lower or '.jpeg' in url_lower:
            return 'jpeg'
        elif '.ico' in url_lower:
            return 'ico'
        return 'png'
