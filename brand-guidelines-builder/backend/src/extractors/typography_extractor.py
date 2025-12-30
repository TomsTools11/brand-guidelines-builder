"""
Typography extraction from HTML and CSS.
"""

import re
from ..models.brand_data import FontSpec, Typography


class TypographyExtractor:
    """Extract typography information from HTML and CSS."""

    GOOGLE_FONTS_PATTERN = r'fonts\.googleapis\.com/css[^"\']*family=([^"\'&]+)'
    FONT_FAMILY_PATTERN = r'font-family:\s*([^;]+)'

    # Generic font families to ignore
    GENERIC_FONTS = {
        'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy',
        'system-ui', 'ui-serif', 'ui-sans-serif', 'ui-monospace',
        'inherit', 'initial', 'unset', 'revert'
    }

    def extract(self, html: str, css_contents: list[str]) -> Typography:
        """
        Extract typography from HTML and CSS.

        Args:
            html: HTML content of the page
            css_contents: List of CSS content strings

        Returns:
            Typography specification with primary and secondary fonts
        """
        # Check for Google Fonts
        google_fonts = self._extract_google_fonts(html, css_contents)

        # Extract font-family declarations
        font_families = self._extract_font_families(css_contents)

        # Build typography spec
        return self._build_typography(google_fonts, font_families)

    def _extract_google_fonts(self, html: str, css_contents: list[str]) -> list[str]:
        """Find Google Fonts from link tags and CSS imports."""
        fonts = []
        combined = html + '\n'.join(css_contents)

        for match in re.finditer(self.GOOGLE_FONTS_PATTERN, combined):
            font_param = match.group(1)

            # Parse font names (handle URL encoding)
            font_param = font_param.replace('%20', ' ').replace('+', ' ')

            # Handle multiple fonts separated by |
            font_names = font_param.split('|')

            for name in font_names:
                # Remove weight specs like :400,700 or :wght@400;700
                clean_name = re.split(r'[:@]', name)[0].strip()
                if clean_name:
                    fonts.append(clean_name)

        # Also check for Google Fonts API v2 format
        v2_pattern = r'fonts\.googleapis\.com/css2\?family=([^"\'&]+)'
        for match in re.finditer(v2_pattern, combined):
            font_param = match.group(1)
            font_param = font_param.replace('%20', ' ').replace('+', ' ')

            # V2 format uses & to separate families
            families = font_param.split('&family=')
            for family in families:
                clean_name = re.split(r'[:@]', family)[0].strip()
                if clean_name:
                    fonts.append(clean_name)

        return list(set(fonts))

    def _extract_font_families(self, css_contents: list[str]) -> list[str]:
        """Extract font-family declarations from CSS."""
        families = []
        combined = '\n'.join(css_contents)

        for match in re.finditer(self.FONT_FAMILY_PATTERN, combined):
            family_string = match.group(1).strip()

            # Get first font in stack
            first_font = family_string.split(',')[0].strip()

            # Remove quotes
            first_font = first_font.strip('"\'')

            if first_font and not self._is_generic_font(first_font):
                families.append(first_font)

        return list(set(families))

    def _is_generic_font(self, name: str) -> bool:
        """Check if font name is a generic family."""
        return name.lower() in self.GENERIC_FONTS

    def _build_typography(
        self,
        google_fonts: list[str],
        font_families: list[str]
    ) -> Typography:
        """Build Typography object from extracted fonts."""
        # Prefer Google Fonts as primary (higher quality, downloadable)
        primary_font = None

        if google_fonts:
            primary_name = google_fonts[0]
            primary_font = FontSpec(
                name=primary_name,
                family=primary_name,
                source='google',
                download_url=f'https://fonts.google.com/specimen/{primary_name.replace(" ", "+")}'
            )
        elif font_families:
            primary_name = font_families[0]
            primary_font = FontSpec(
                name=primary_name,
                family=primary_name,
                source='custom'
            )
        else:
            # Fallback to Inter
            primary_font = FontSpec(
                name='Inter',
                family='Inter',
                source='google',
                download_url='https://fonts.google.com/specimen/Inter'
            )

        # Secondary font (if multiple found)
        secondary_font = None
        all_fonts = google_fonts + font_families

        if len(all_fonts) > 1:
            # Find a different font family
            for font_name in all_fonts[1:]:
                if font_name != primary_font.name:
                    secondary_font = FontSpec(
                        name=font_name,
                        family=font_name,
                        source='google' if font_name in google_fonts else 'custom',
                        download_url=(
                            f'https://fonts.google.com/specimen/{font_name.replace(" ", "+")}'
                            if font_name in google_fonts else None
                        )
                    )
                    break

        return Typography(
            primary=primary_font,
            secondary=secondary_font,
            system_fallback='Arial, Helvetica, sans-serif'
        )
