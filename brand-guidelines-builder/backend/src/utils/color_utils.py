"""
Color utility functions for format conversion and analysis.
"""

import math
from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color."""
    return f"#{r:02X}{g:02X}{b:02X}"


def rgb_to_cmyk(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB to CMYK string."""
    r, g, b = rgb
    if r == 0 and g == 0 and b == 0:
        return "0, 0, 0, 100"

    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255

    k = min(c, m, y)
    if k == 1:
        return "0, 0, 0, 100"

    c = (c - k) / (1 - k)
    m = (m - k) / (1 - k)
    y = (y - k) / (1 - k)

    return f"{int(c * 100)}, {int(m * 100)}, {int(y * 100)}, {int(k * 100)}"


def color_distance(hex1: str, hex2: str) -> float:
    """
    Calculate Euclidean distance between two colors in RGB space.
    Returns a value between 0 (identical) and ~441 (black vs white).
    """
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)

    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def is_near_white(hex_color: str, threshold: int = 240) -> bool:
    """Check if a color is near white."""
    r, g, b = hex_to_rgb(hex_color)
    return r >= threshold and g >= threshold and b >= threshold


def is_near_black(hex_color: str, threshold: int = 15) -> bool:
    """Check if a color is near black."""
    r, g, b = hex_to_rgb(hex_color)
    return r <= threshold and g <= threshold and b <= threshold


def get_luminance(hex_color: str) -> float:
    """
    Calculate relative luminance of a color.
    Returns value between 0 (black) and 1 (white).
    """
    r, g, b = hex_to_rgb(hex_color)

    # Convert to sRGB
    r_srgb = r / 255
    g_srgb = g / 255
    b_srgb = b / 255

    # Apply gamma correction
    def gamma(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r_lin = gamma(r_srgb)
    g_lin = gamma(g_srgb)
    b_lin = gamma(b_srgb)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(hex1: str, hex2: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.
    Returns value between 1 (no contrast) and 21 (max contrast).
    """
    l1 = get_luminance(hex1)
    l2 = get_luminance(hex2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


# Common Pantone color approximations
PANTONE_COLORS = {
    "#FF0000": "Pantone 185 C",
    "#FF6600": "Pantone 1505 C",
    "#FFCC00": "Pantone 116 C",
    "#00FF00": "Pantone 802 C",
    "#00CCFF": "Pantone 2995 C",
    "#0066FF": "Pantone 2728 C",
    "#0000FF": "Pantone 286 C",
    "#6600FF": "Pantone 2685 C",
    "#FF00FF": "Pantone 807 C",
    "#000000": "Pantone Black C",
    "#FFFFFF": "Pantone White",
    "#1A1A2E": "Pantone 5395 C",
    "#4A4A6A": "Pantone 5275 C",
}


def find_nearest_pantone(hex_color: str) -> str:
    """
    Find the nearest Pantone color match.
    This is a simplified approximation - real Pantone matching requires
    proprietary color databases.
    """
    min_distance = float('inf')
    nearest = "N/A"

    for pantone_hex, pantone_name in PANTONE_COLORS.items():
        distance = color_distance(hex_color, pantone_hex)
        if distance < min_distance:
            min_distance = distance
            nearest = pantone_name

    # Only return if reasonably close
    if min_distance < 100:
        return nearest
    return "Contact Pantone for exact match"
