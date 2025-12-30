"""
Color extraction from CSS and images.
"""

import re
from collections import Counter
from io import BytesIO
from typing import Optional

from colorthief import ColorThief

from ..models.brand_data import ColorSpec, ColorPalette
from ..utils.color_utils import (
    hex_to_rgb,
    rgb_to_cmyk,
    find_nearest_pantone,
    is_near_white,
    is_near_black,
    color_distance,
)


class ColorExtractor:
    """Extract color palette from CSS and images."""

    def extract(
        self,
        css_contents: list[str],
        images: Optional[list[bytes]] = None
    ) -> ColorPalette:
        """
        Extract color palette from CSS and images.

        Args:
            css_contents: List of CSS content strings
            images: Optional list of image bytes (logos, hero images)

        Returns:
            ColorPalette with primary, secondary, accent, and neutral colors
        """
        images = images or []

        # Extract from CSS
        css_colors = self._extract_from_css(css_contents)

        # Extract from images (logos, hero images)
        image_colors = self._extract_from_images(images)

        # Combine and rank
        all_colors = css_colors + image_colors
        ranked = self._rank_colors(all_colors)

        # Build palette
        return self._build_palette(ranked)

    def _extract_from_css(self, css_contents: list[str]) -> list[str]:
        """Extract all color values from CSS."""
        colors = []
        combined_css = '\n'.join(css_contents)

        # Hex colors (6 or 3 digit)
        hex_pattern = r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b'
        for match in re.finditer(hex_pattern, combined_css):
            hex_val = match.group(0)
            if len(hex_val) == 4:  # Expand #ABC to #AABBCC
                hex_val = '#' + ''.join(c * 2 for c in hex_val[1:])
            colors.append(hex_val.upper())

        # RGB/RGBA
        rgb_pattern = r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)'
        for match in re.finditer(rgb_pattern, combined_css):
            r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
            colors.append(f'#{r:02X}{g:02X}{b:02X}')

        # HSL (convert to hex approximately)
        hsl_pattern = r'hsla?\s*\(\s*(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?'
        for match in re.finditer(hsl_pattern, combined_css):
            h, s, l = int(match.group(1)), int(match.group(2)), int(match.group(3))
            rgb = self._hsl_to_rgb(h, s / 100, l / 100)
            colors.append(f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}')

        return colors

    def _hsl_to_rgb(self, h: int, s: float, l: float) -> tuple[int, int, int]:
        """Convert HSL to RGB."""
        if s == 0:
            r = g = b = int(l * 255)
            return (r, g, b)

        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q

        h_norm = h / 360
        r = hue_to_rgb(p, q, h_norm + 1/3)
        g = hue_to_rgb(p, q, h_norm)
        b = hue_to_rgb(p, q, h_norm - 1/3)

        return (int(r * 255), int(g * 255), int(b * 255))

    def _extract_from_images(self, images: list[bytes]) -> list[str]:
        """Extract dominant colors from images."""
        colors = []

        for img_data in images[:5]:  # Limit to 5 images
            try:
                ct = ColorThief(BytesIO(img_data))
                palette = ct.get_palette(color_count=5)
                for r, g, b in palette:
                    colors.append(f'#{r:02X}{g:02X}{b:02X}')
            except Exception:
                continue

        return colors

    def _rank_colors(self, colors: list[str]) -> list[tuple[str, int]]:
        """Rank colors by frequency, filtering near-white/black."""
        # Filter out near-white and near-black colors
        filtered = [
            c for c in colors
            if not is_near_white(c) and not is_near_black(c)
        ]

        # Count frequencies
        counts = Counter(filtered)

        # Cluster similar colors
        clustered = self._cluster_similar_colors(counts)

        return clustered.most_common(10)

    def _cluster_similar_colors(self, counts: Counter) -> Counter:
        """Merge similar colors into clusters."""
        colors = list(counts.keys())
        merged = Counter()
        used = set()

        for color in colors:
            if color in used:
                continue

            cluster_count = counts[color]
            for other in colors:
                if other != color and other not in used:
                    if color_distance(color, other) < 30:  # Threshold
                        cluster_count += counts[other]
                        used.add(other)

            merged[color] = cluster_count
            used.add(color)

        return merged

    def _build_palette(self, ranked: list[tuple[str, int]]) -> ColorPalette:
        """Build ColorPalette from ranked colors."""
        if not ranked:
            # Fallback defaults
            return ColorPalette(
                primary=ColorSpec(name="Primary", hex="#1A1A2E"),
                secondary=ColorSpec(name="Secondary", hex="#4A4A6A"),
                accent=ColorSpec(name="Accent", hex="#0066FF"),
            )

        def make_color_spec(hex_val: str, name: str) -> ColorSpec:
            rgb = hex_to_rgb(hex_val)
            return ColorSpec(
                name=name,
                hex=hex_val,
                rgb=f"{rgb[0]}, {rgb[1]}, {rgb[2]}",
                cmyk=rgb_to_cmyk(rgb),
                pantone=find_nearest_pantone(hex_val)
            )

        colors = [c[0] for c in ranked]

        return ColorPalette(
            primary=make_color_spec(colors[0], "Primary"),
            secondary=make_color_spec(colors[1], "Secondary") if len(colors) > 1 else None,
            accent=make_color_spec(colors[2], "Accent") if len(colors) > 2 else None,
            neutrals=[
                make_color_spec(c, f"Neutral {i + 1}")
                for i, c in enumerate(colors[3:7])
            ]
        )
