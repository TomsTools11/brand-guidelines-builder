"""
PDF Brand Guidelines Generator using ReportLab.
Redesigned to match professional brand guidelines style similar to Credit Key.
"""

from pathlib import Path
import math

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor, white, Color
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from ..models.brand_data import ExtractedBrand


# Page dimensions for landscape letter
PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)


class HexagonPattern(Flowable):
    """Draw a hexagon pattern background element."""

    def __init__(self, width: float, height: float, color: HexColor, opacity: float = 0.15):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
        self.opacity = opacity

    def draw(self):
        self.canv.saveState()
        self.canv.setFillColor(self.color)
        self.canv.setStrokeColor(self.color)
        self.canv.setFillAlpha(self.opacity)
        self.canv.setStrokeAlpha(self.opacity)

        hex_size = 20
        hex_spacing = hex_size * 1.8

        for row in range(int(self.height / hex_spacing) + 2):
            offset = (row % 2) * (hex_spacing / 2)
            for col in range(int(self.width / hex_spacing) + 2):
                x = col * hex_spacing + offset
                y = row * hex_spacing * 0.866
                self._draw_hexagon(x, y, hex_size * 0.4)

        self.canv.restoreState()

    def _draw_hexagon(self, cx, cy, size):
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 6
            points.append(cx + size * math.cos(angle))
            points.append(cy + size * math.sin(angle))
        self.canv.setLineWidth(0.5)
        path = self.canv.beginPath()
        path.moveTo(points[0], points[1])
        for i in range(1, 6):
            path.lineTo(points[i * 2], points[i * 2 + 1])
        path.close()
        self.canv.drawPath(path, stroke=1, fill=0)


class GradientRect(Flowable):
    """Draw a gradient rectangle background."""

    def __init__(self, width: float, height: float, start_color: str, end_color: str,
                 direction: str = "horizontal"):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.start_color = HexColor(start_color)
        self.end_color = HexColor(end_color)
        self.direction = direction

    def draw(self):
        steps = 100
        if self.direction == "horizontal":
            step_width = self.width / steps
            for i in range(steps):
                r = self.start_color.red + (self.end_color.red - self.start_color.red) * i / steps
                g = self.start_color.green + (self.end_color.green - self.start_color.green) * i / steps
                b = self.start_color.blue + (self.end_color.blue - self.start_color.blue) * i / steps
                self.canv.setFillColor(Color(r, g, b))
                self.canv.rect(i * step_width, 0, step_width + 1, self.height, fill=1, stroke=0)
        else:
            step_height = self.height / steps
            for i in range(steps):
                r = self.start_color.red + (self.end_color.red - self.start_color.red) * i / steps
                g = self.start_color.green + (self.end_color.green - self.start_color.green) * i / steps
                b = self.start_color.blue + (self.end_color.blue - self.start_color.blue) * i / steps
                self.canv.setFillColor(Color(r, g, b))
                self.canv.rect(0, i * step_height, self.width, step_height + 1, fill=1, stroke=0)


class ColorSwatch(Flowable):
    """Draw a rounded rectangle color swatch with label."""

    def __init__(self, width: float, height: float, color: HexColor, name: str = "",
                 text_color: HexColor = white, show_hex: bool = True, hex_value: str = ""):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
        self.name = name
        self.text_color = text_color
        self.show_hex = show_hex
        self.hex_value = hex_value

    def draw(self):
        # Draw rounded rectangle
        self.canv.setFillColor(self.color)
        radius = min(self.width, self.height) * 0.15
        self.canv.roundRect(0, 0, self.width, self.height, radius, fill=1, stroke=0)

        # Draw color name
        if self.name:
            self.canv.setFillColor(self.text_color)
            self.canv.setFont("Helvetica-Bold", 11)
            self.canv.drawString(12, self.height - 25, self.name)

        # Draw hex value
        if self.show_hex and self.hex_value:
            self.canv.setFont("Helvetica", 9)
            self.canv.drawString(12, 12, self.hex_value)


class CircleColorSwatch(Flowable):
    """Draw a circular color swatch (hexagon shape for brand alignment)."""

    def __init__(self, size: float, color: HexColor, name: str = "", hex_value: str = ""):
        Flowable.__init__(self)
        self.width = size
        self.height = size + 60  # Extra space for text below
        self.size = size
        self.color = color
        self.name = name
        self.hex_value = hex_value

    def draw(self):
        # Draw hexagon shape
        cx = self.size / 2
        cy = self.size / 2 + 50
        radius = self.size / 2 - 5

        self.canv.setFillColor(self.color)
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 2
            points.append(cx + radius * math.cos(angle))
            points.append(cy + radius * math.sin(angle))

        path = self.canv.beginPath()
        path.moveTo(points[0], points[1])
        for i in range(1, 6):
            path.lineTo(points[i * 2], points[i * 2 + 1])
        path.close()
        self.canv.drawPath(path, stroke=0, fill=1)

        # Draw name below
        if self.name:
            self.canv.setFillColor(HexColor("#070d59"))
            self.canv.setFont("Helvetica-Bold", 11)
            text_width = self.canv.stringWidth(self.name, "Helvetica-Bold", 11)
            self.canv.drawString(cx - text_width / 2, 25, self.name)

        # Draw hex below name
        if self.hex_value:
            self.canv.setFillColor(HexColor("#666666"))
            self.canv.setFont("Helvetica", 9)
            text_width = self.canv.stringWidth(self.hex_value, "Helvetica", 9)
            self.canv.drawString(cx - text_width / 2, 10, self.hex_value)


class BrandPageTemplate:
    """Custom page template for brand guidelines."""

    def __init__(self, colors: dict, company_name: str, logo_data: bytes = None):
        self.colors = colors
        self.company_name = company_name
        self.logo_data = logo_data
        self.page_count = 0
        self.dark_pages = set()  # Track which pages should be dark

    def draw_dark_page(self, canvas, doc):
        """Draw dark navy background with hexagon pattern."""
        canvas.saveState()

        # Dark navy background
        canvas.setFillColor(self.colors['monsoon'])
        canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

        # Subtle hexagon pattern
        canvas.setStrokeColor(self.colors['storm'])
        canvas.setStrokeAlpha(0.3)
        canvas.setLineWidth(0.5)

        hex_size = 25
        hex_spacing = hex_size * 2.2

        for row in range(-1, int(PAGE_HEIGHT / (hex_spacing * 0.866)) + 2):
            offset = (row % 2) * (hex_spacing / 2)
            for col in range(-1, int(PAGE_WIDTH / hex_spacing) + 2):
                x = col * hex_spacing + offset
                y = row * hex_spacing * 0.866
                self._draw_hexagon_outline(canvas, x, y, hex_size * 0.5)

        # Curved accent shape
        canvas.setFillColor(self.colors['storm'])
        canvas.setFillAlpha(0.4)
        path = canvas.beginPath()
        path.moveTo(PAGE_WIDTH * 0.4, 0)
        path.curveTo(PAGE_WIDTH * 0.6, PAGE_HEIGHT * 0.3,
                     PAGE_WIDTH * 0.7, PAGE_HEIGHT * 0.5,
                     PAGE_WIDTH, PAGE_HEIGHT * 0.3)
        path.lineTo(PAGE_WIDTH, 0)
        path.close()
        canvas.drawPath(path, fill=1, stroke=0)

        canvas.restoreState()

    def draw_light_page(self, canvas, doc):
        """Draw light gradient background."""
        canvas.saveState()

        # White to light blue gradient
        steps = 50
        for i in range(steps):
            ratio = i / steps
            r = 1.0 - (1.0 - 0.945) * ratio  # Blend to light blue
            g = 1.0 - (1.0 - 0.953) * ratio
            b = 1.0 - (1.0 - 0.973) * ratio
            canvas.setFillColor(Color(r, g, b))
            x = PAGE_WIDTH * ratio / steps * steps
            canvas.rect(i * PAGE_WIDTH / steps, 0, PAGE_WIDTH / steps + 1, PAGE_HEIGHT, fill=1, stroke=0)

        # Subtle hexagon pattern on right side
        canvas.setStrokeColor(self.colors['fog'])
        canvas.setStrokeAlpha(0.5)
        canvas.setLineWidth(0.3)

        hex_size = 20
        hex_spacing = hex_size * 2

        for row in range(int(PAGE_HEIGHT / (hex_spacing * 0.866)) + 2):
            offset = (row % 2) * (hex_spacing / 2)
            for col in range(int(PAGE_WIDTH * 0.5 / hex_spacing), int(PAGE_WIDTH / hex_spacing) + 2):
                x = col * hex_spacing + offset
                y = row * hex_spacing * 0.866
                self._draw_hexagon_outline(canvas, x, y, hex_size * 0.4)

        canvas.restoreState()

    def _draw_hexagon_outline(self, canvas, cx, cy, size):
        """Draw hexagon outline at position."""
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 6
            points.append(cx + size * math.cos(angle))
            points.append(cy + size * math.sin(angle))

        path = canvas.beginPath()
        path.moveTo(points[0], points[1])
        for i in range(1, 6):
            path.lineTo(points[i * 2], points[i * 2 + 1])
        path.close()
        canvas.drawPath(path, stroke=1, fill=0)

    def draw_footer(self, canvas, doc, is_dark: bool = False):
        """Draw footer with logo badge and page number."""
        canvas.saveState()

        # Page number
        page_num = doc.page
        text_color = white if is_dark else self.colors['text_light']
        canvas.setFillColor(text_color)
        canvas.setFont("Helvetica", 10)
        canvas.drawRightString(PAGE_WIDTH - 40, 30, str(page_num))

        # Logo badge placeholder (simplified hexagon with CK)
        badge_color = self.colors['aurora'] if is_dark else self.colors['aurora']
        self._draw_logo_badge(canvas, 40, 30, 20, badge_color)

        canvas.restoreState()

    def _draw_logo_badge(self, canvas, x, y, size, color):
        """Draw simplified logo badge."""
        canvas.setFillColor(color)
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 2
            points.append(x + size * math.cos(angle))
            points.append(y + size * math.sin(angle))

        path = canvas.beginPath()
        path.moveTo(points[0], points[1])
        for i in range(1, 6):
            path.lineTo(points[i * 2], points[i * 2 + 1])
        path.close()
        canvas.drawPath(path, stroke=0, fill=1)

        # Inner design
        canvas.setFillColor(white)
        inner_size = size * 0.5
        canvas.circle(x - inner_size * 0.3, y + inner_size * 0.3, inner_size * 0.35, fill=1, stroke=0)
        canvas.circle(x + inner_size * 0.3, y + inner_size * 0.3, inner_size * 0.35, fill=1, stroke=0)
        canvas.circle(x, y - inner_size * 0.3, inner_size * 0.35, fill=1, stroke=0)


class BrandGuidelinesPDF:
    """Generate a professional brand guidelines PDF."""

    def __init__(self, brand_data: ExtractedBrand):
        self.brand = brand_data
        self.colors = self._setup_colors()
        self.styles = self._create_styles()
        self.page_template = BrandPageTemplate(
            self.colors,
            brand_data.company_name,
            brand_data.logo.primary_data if brand_data.logo else None
        )

    def _setup_colors(self) -> dict:
        """Set up the color palette matching Credit Key style."""
        # Use extracted primary color or default to Credit Key navy
        primary_hex = self.brand.colors.primary.hex if self.brand.colors.primary else "#070d59"
        accent_hex = (
            self.brand.colors.accent.hex
            if self.brand.colors.accent
            else "#0066ff"
        )
        secondary_hex = (
            self.brand.colors.secondary.hex
            if self.brand.colors.secondary
            else "#1f3c88"
        )

        return {
            'monsoon': HexColor("#070d59"),  # Dark navy - primary brand
            'aurora': HexColor(accent_hex),   # Bright blue - accent
            'storm': HexColor(secondary_hex), # Medium navy
            'frost': HexColor("#ffffff"),     # White
            'fog': HexColor("#d6e0f0"),       # Light blue-gray
            'mist': HexColor("#f1f3f8"),      # Very light gray
            'dust': HexColor("#e0bea3"),      # Warm tan
            'haze': HexColor("#decfc3"),      # Beige
            'white': HexColor("#ffffff"),
            'text_dark': HexColor("#070d59"),
            'text_light': HexColor("#666666"),
            'primary': HexColor(primary_hex),
            'accent': HexColor(accent_hex),
            'secondary': HexColor(secondary_hex),
        }

    def _create_styles(self) -> dict:
        """Create paragraph styles matching professional brand guidelines."""
        styles = getSampleStyleSheet()

        # Large section title (for dark pages)
        styles.add(ParagraphStyle(
            name='SectionTitle',
            fontSize=72,
            leading=80,
            textColor=self.colors['white'],
            fontName='Helvetica-Light' if 'Helvetica-Light' in styles.byName else 'Helvetica',
            alignment=TA_LEFT,
            spaceAfter=0,
        ))

        # Cover title
        styles.add(ParagraphStyle(
            name='CoverTitle',
            fontSize=64,
            leading=72,
            textColor=self.colors['white'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=10,
        ))

        # Cover subtitle/year
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            fontSize=14,
            leading=20,
            textColor=self.colors['fog'],
            fontName='Helvetica',
            alignment=TA_LEFT,
        ))

        # TOC title
        styles.add(ParagraphStyle(
            name='TOCTitle',
            fontSize=56,
            leading=64,
            textColor=self.colors['white'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=40,
        ))

        # TOC number
        styles.add(ParagraphStyle(
            name='TOCNumber',
            fontSize=11,
            leading=16,
            textColor=self.colors['fog'],
            fontName='Helvetica',
            alignment=TA_LEFT,
        ))

        # TOC item
        styles.add(ParagraphStyle(
            name='TOCItem',
            fontSize=20,
            leading=28,
            textColor=self.colors['white'],
            fontName='Helvetica',
            alignment=TA_LEFT,
        ))

        # Page label (small uppercase)
        styles.add(ParagraphStyle(
            name='PageLabel',
            fontSize=10,
            leading=14,
            textColor=self.colors['text_dark'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=20,
        ))

        # Large headline (dark color)
        styles.add(ParagraphStyle(
            name='LargeHeadline',
            fontSize=42,
            leading=50,
            textColor=self.colors['text_dark'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=10,
        ))

        # Large headline accent (colored text)
        styles.add(ParagraphStyle(
            name='LargeHeadlineAccent',
            fontSize=42,
            leading=50,
            textColor=self.colors['aurora'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=20,
        ))

        # Subsection header
        styles.add(ParagraphStyle(
            name='SubsectionHeader',
            fontSize=20,
            leading=28,
            textColor=self.colors['aurora'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=10,
        ))

        # Body text
        styles.add(ParagraphStyle(
            name='BrandBodyText',
            fontSize=11,
            leading=18,
            textColor=self.colors['text_dark'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=12,
        ))

        # Body text light
        styles.add(ParagraphStyle(
            name='BrandBodyTextLight',
            fontSize=11,
            leading=18,
            textColor=self.colors['text_light'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=12,
        ))

        # Intro paragraph (larger)
        styles.add(ParagraphStyle(
            name='IntroText',
            fontSize=12,
            leading=20,
            textColor=self.colors['text_dark'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=15,
        ))

        # Trait name (large colored)
        styles.add(ParagraphStyle(
            name='TraitName',
            fontSize=32,
            leading=40,
            textColor=self.colors['aurora'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=5,
        ))

        # Trait name muted
        styles.add(ParagraphStyle(
            name='TraitNameMuted',
            fontSize=32,
            leading=40,
            textColor=self.colors['dust'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=5,
        ))

        # Pillar title
        styles.add(ParagraphStyle(
            name='PillarTitle',
            fontSize=24,
            leading=32,
            textColor=self.colors['text_dark'],
            fontName='Helvetica',
            alignment=TA_CENTER,
            spaceAfter=10,
        ))

        # Pillar number
        styles.add(ParagraphStyle(
            name='PillarNumber',
            fontSize=11,
            leading=16,
            textColor=self.colors['text_light'],
            fontName='Helvetica',
            alignment=TA_CENTER,
        ))

        # Voice table header
        styles.add(ParagraphStyle(
            name='VoiceHeader',
            fontSize=14,
            leading=20,
            textColor=self.colors['text_dark'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
        ))

        # Voice trait
        styles.add(ParagraphStyle(
            name='VoiceTrait',
            fontSize=28,
            leading=36,
            textColor=self.colors['text_dark'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=5,
        ))

        # Voice trait muted
        styles.add(ParagraphStyle(
            name='VoiceTraitMuted',
            fontSize=28,
            leading=36,
            textColor=self.colors['fog'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=5,
        ))

        return styles

    def generate(self, output_path: str) -> str:
        """Generate the complete PDF."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Create canvas for custom drawing
        c = canvas.Canvas(output_path, pagesize=landscape(letter))

        # Build document pages
        self._draw_cover(c)
        self._draw_toc(c)
        self._draw_brand_strategy_section(c)
        self._draw_messaging_section(c)
        self._draw_verbal_expression_section(c)
        self._draw_logo_section(c)
        self._draw_color_section(c)
        self._draw_typography_section(c)
        self._draw_photography_section(c)

        c.save()
        return output_path

    def _draw_cover(self, c: canvas.Canvas):
        """Draw the cover page."""
        # Dark background
        self.page_template.draw_dark_page(c, None)

        # Logo in top left
        self._draw_logo_badge(c, 60, PAGE_HEIGHT - 60, 25)
        c.setFillColor(self.colors['white'])
        c.setFont("Helvetica", 20)
        c.drawString(95, PAGE_HEIGHT - 68, self.brand.company_name)

        # Main title
        c.setFillColor(self.colors['white'])
        c.setFont("Helvetica", 72)
        c.drawString(60, PAGE_HEIGHT * 0.45, "Brand")
        c.drawString(60, PAGE_HEIGHT * 0.45 - 80, "Guidelines")

        # Year/subtitle
        c.setFillColor(self.colors['fog'])
        c.setFont("Helvetica", 14)
        c.drawString(60, PAGE_HEIGHT * 0.45 - 160, "2024")

        # Footer with page number
        c.setFillColor(self.colors['fog'])
        c.setFont("Helvetica", 10)

        c.showPage()

    def _draw_toc(self, c: canvas.Canvas):
        """Draw table of contents page."""
        self.page_template.draw_dark_page(c, None)

        # Title
        c.setFillColor(self.colors['white'])
        c.setFont("Helvetica", 56)
        c.drawString(60, PAGE_HEIGHT - 100, "Contents")

        # TOC items in 3-column grid
        toc_items = [
            ("01", "Brand Strategy"),
            ("02", "Messaging"),
            ("03", "Verbal Expression"),
            ("04", "Logo"),
            ("05", "Color"),
            ("06", "Typography"),
            ("07", "Photography"),
        ]

        col_width = (PAGE_WIDTH - 120) / 3
        row_height = 80
        start_y = PAGE_HEIGHT - 250

        for i, (num, title) in enumerate(toc_items):
            col = i % 3
            row = i // 3
            x = 60 + col * col_width
            y = start_y - row * row_height

            # Number
            c.setFillColor(self.colors['fog'])
            c.setFont("Helvetica", 11)
            c.drawString(x, y + 25, num)

            # Title
            c.setFillColor(self.colors['white'])
            c.setFont("Helvetica", 20)
            c.drawString(x, y, title)

        # Footer
        self._draw_logo_badge(c, 40, 30, 18)
        c.setFillColor(self.colors['fog'])
        c.setFont("Helvetica", 10)
        c.drawRightString(PAGE_WIDTH - 40, 30, "2")

        c.showPage()

    def _draw_section_divider(self, c: canvas.Canvas, title: str, page_num: int):
        """Draw a section divider page with dark background."""
        self.page_template.draw_dark_page(c, None)

        # Split title into multiple lines if needed
        words = title.split()
        c.setFillColor(self.colors['white'])
        c.setFont("Helvetica", 72)

        if len(words) == 1:
            c.drawString(60, PAGE_HEIGHT * 0.5, title)
        else:
            y = PAGE_HEIGHT * 0.55
            for word in words:
                c.drawString(60, y, word)
                y -= 85

        # Footer
        self._draw_logo_badge(c, 40, 30, 18)
        c.setFillColor(self.colors['fog'])
        c.setFont("Helvetica", 10)
        c.drawRightString(PAGE_WIDTH - 40, 30, str(page_num))

        c.showPage()

    def _draw_content_page(self, c: canvas.Canvas, page_num: int):
        """Draw light background for content page."""
        self.page_template.draw_light_page(c, None)

        # Footer
        self._draw_logo_badge(c, 40, 30, 18)
        c.setFillColor(self.colors['text_light'])
        c.setFont("Helvetica", 10)
        c.drawRightString(PAGE_WIDTH - 40, 30, str(page_num))

    def _draw_logo_badge(self, c: canvas.Canvas, x: float, y: float, size: float):
        """Draw simplified logo badge."""
        c.saveState()
        c.setFillColor(self.colors['aurora'])

        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 2
            points.append(x + size * math.cos(angle))
            points.append(y + size * math.sin(angle))

        path = c.beginPath()
        path.moveTo(points[0], points[1])
        for i in range(1, 6):
            path.lineTo(points[i * 2], points[i * 2 + 1])
        path.close()
        c.drawPath(path, stroke=0, fill=1)

        # Inner white design
        c.setFillColor(self.colors['white'])
        inner = size * 0.35
        c.circle(x - inner * 0.4, y + inner * 0.4, inner * 0.4, fill=1, stroke=0)
        c.circle(x + inner * 0.4, y + inner * 0.4, inner * 0.4, fill=1, stroke=0)
        c.circle(x, y - inner * 0.4, inner * 0.4, fill=1, stroke=0)

        c.restoreState()

    def _draw_brand_strategy_section(self, c: canvas.Canvas):
        """Draw brand strategy section."""
        # Section divider
        self._draw_section_divider(c, "Brand Strategy", 3)

        # Brand Positioning page
        self._draw_content_page(c, 4)

        # Page label
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, PAGE_HEIGHT - 60, "BRAND POSITIONING")

        # Main headline (two-color style)
        headline = self.brand.positioning_headline or f"{self.brand.company_name} is your brand partner."
        c.setFont("Helvetica", 36)
        c.setFillColor(self.colors['text_dark'])

        # Split and render headline
        y = PAGE_HEIGHT - 150
        lines = self._wrap_text(headline, 35)
        for i, line in enumerate(lines[:4]):
            if i < 2:
                c.setFillColor(self.colors['text_dark'])
            else:
                c.setFillColor(self.colors['dust'])
            c.drawString(60, y, line)
            y -= 45

        # Intro text
        intro = self.brand.positioning_description or ""
        if intro:
            c.setFillColor(self.colors['text_light'])
            c.setFont("Helvetica", 11)
            y = PAGE_HEIGHT - 360
            intro_lines = self._wrap_text(intro, 50)
            for line in intro_lines[:4]:
                c.drawString(60, y, line)
                y -= 18

        # Pillars on right side
        if self.brand.pillars:
            x_start = PAGE_WIDTH * 0.55
            y = PAGE_HEIGHT - 120

            for i, pillar in enumerate(self.brand.pillars[:3]):
                # Pillar title
                c.setFillColor(self.colors['aurora'])
                c.setFont("Helvetica-Bold", 16)
                c.drawString(x_start, y, pillar.title)

                # Pillar description
                c.setFillColor(self.colors['text_dark'])
                c.setFont("Helvetica", 10)
                desc_lines = self._wrap_text(pillar.description, 55)
                y -= 25
                for line in desc_lines[:5]:
                    c.drawString(x_start, y, line)
                    y -= 15

                y -= 30

        c.showPage()

        # Mission page
        self._draw_content_page(c, 5)
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, PAGE_HEIGHT - 60, "OUR MISSION")

        mission = self.brand.mission or "Our mission statement."
        c.setFont("Helvetica", 42)
        y = PAGE_HEIGHT - 180
        mission_lines = self._wrap_text(mission, 30)
        for i, line in enumerate(mission_lines[:4]):
            if i < len(mission_lines) // 2:
                c.setFillColor(self.colors['text_dark'])
            else:
                c.setFillColor(self.colors['aurora'])
            c.drawString(60, y, line)
            y -= 55

        # Mission description
        if self.brand.mission_description:
            c.setFillColor(self.colors['text_light'])
            c.setFont("Helvetica", 11)
            y -= 30
            desc_lines = self._wrap_text(self.brand.mission_description, 70)
            for line in desc_lines[:3]:
                c.drawString(60, y, line)
                y -= 18

        c.showPage()

        # Vision page
        self._draw_content_page(c, 6)
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, PAGE_HEIGHT - 60, "OUR VISION")

        vision = self.brand.vision or "Our vision statement."
        c.setFont("Helvetica", 42)
        y = PAGE_HEIGHT - 180
        vision_lines = self._wrap_text(vision, 30)
        for i, line in enumerate(vision_lines[:4]):
            if i < len(vision_lines) // 2:
                c.setFillColor(self.colors['text_dark'])
            else:
                c.setFillColor(self.colors['dust'])
            c.drawString(60, y, line)
            y -= 55

        if self.brand.vision_description:
            c.setFillColor(self.colors['text_light'])
            c.setFont("Helvetica", 11)
            y -= 30
            desc_lines = self._wrap_text(self.brand.vision_description, 70)
            for line in desc_lines[:3]:
                c.drawString(60, y, line)
                y -= 18

        c.showPage()

        # Brand Personality page
        if self.brand.traits:
            self._draw_content_page(c, 7)
            c.setFillColor(self.colors['text_dark'])
            c.setFont("Helvetica-Bold", 10)
            c.drawString(60, PAGE_HEIGHT - 60, "BRAND PERSONALITY")

            # Intro text
            c.setFillColor(self.colors['text_dark'])
            c.setFont("Helvetica", 11)
            intro = "Our brand personality is a set of human traits our brand seeks to embody."
            c.drawString(60, PAGE_HEIGHT - 100, intro)

            # Traits in two columns
            y = PAGE_HEIGHT - 180
            for i, trait in enumerate(self.brand.traits[:4]):
                # Trait name (alternating colors)
                if i % 2 == 0:
                    c.setFillColor(self.colors['aurora'])
                else:
                    c.setFillColor(self.colors['dust'])
                c.setFont("Helvetica", 32)
                c.drawString(200, y, trait.name)

                # Trait description on right
                c.setFillColor(self.colors['text_dark'])
                c.setFont("Helvetica", 10)
                desc_lines = self._wrap_text(trait.description, 50)
                desc_y = y + 5
                for line in desc_lines[:4]:
                    c.drawString(PAGE_WIDTH * 0.5, desc_y, line)
                    desc_y -= 14

                y -= 90

            c.showPage()

        # Brand Promise page
        self._draw_content_page(c, 8)
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, PAGE_HEIGHT - 60, "BRAND PROMISE")

        promise = self.brand.promise or "Our brand promise."
        c.setFont("Helvetica", 42)
        y = PAGE_HEIGHT - 180
        promise_lines = self._wrap_text(promise, 28)
        for i, line in enumerate(promise_lines[:4]):
            if i < len(promise_lines) // 2:
                c.setFillColor(self.colors['text_dark'])
            else:
                c.setFillColor(self.colors['aurora'])
            c.drawString(60, y, line)
            y -= 55

        if self.brand.promise_description:
            c.setFillColor(self.colors['text_light'])
            c.setFont("Helvetica", 11)
            y -= 30
            desc_lines = self._wrap_text(self.brand.promise_description, 70)
            for line in desc_lines[:4]:
                c.drawString(60, y, line)
                y -= 18

        c.showPage()

        # Boilerplate page
        if self.brand.boilerplate:
            self._draw_content_page(c, 9)
            c.setFillColor(self.colors['text_dark'])
            c.setFont("Helvetica-Bold", 10)
            c.drawString(60, PAGE_HEIGHT - 60, "BOILERPLATE")

            # Large headline
            c.setFont("Helvetica", 36)
            c.setFillColor(self.colors['text_dark'])
            c.drawString(60, PAGE_HEIGHT - 150, f"{self.brand.company_name} is")

            c.setFillColor(self.colors['dust'])
            c.drawString(60, PAGE_HEIGHT - 195, "your trusted partner.")

            # Boilerplate text
            c.setFillColor(self.colors['text_dark'])
            c.setFont("Helvetica", 11)
            y = PAGE_HEIGHT - 280
            bp_lines = self._wrap_text(self.brand.boilerplate, 85)
            for line in bp_lines[:8]:
                c.drawString(60, y, line)
                y -= 18

            c.showPage()

    def _draw_messaging_section(self, c: canvas.Canvas):
        """Draw messaging frameworks section."""
        self._draw_section_divider(c, "Messaging Frameworks", 10)

        # Brand Pillars Overview page
        if self.brand.pillars:
            self._draw_content_page(c, 11)
            c.setFillColor(self.colors['text_dark'])
            c.setFont("Helvetica-Bold", 10)
            c.drawString(60, PAGE_HEIGHT - 60, "OVERVIEW")

            c.setFont("Helvetica", 32)
            c.setFillColor(self.colors['text_dark'])
            c.drawString(60, PAGE_HEIGHT - 120, "Brand Pillars")

            # Pillars in columns
            col_width = (PAGE_WIDTH - 120) / min(3, len(self.brand.pillars))
            y = PAGE_HEIGHT - 220

            for i, pillar in enumerate(self.brand.pillars[:3]):
                x = 60 + i * col_width

                # Number
                c.setFillColor(self.colors['text_light'])
                c.setFont("Helvetica", 11)
                c.drawString(x, y + 40, f"0{i + 1}")

                # Pillar title
                c.setFillColor(self.colors['text_dark'])
                c.setFont("Helvetica", 22)
                c.drawString(x, y, pillar.title)

                # Description
                c.setFillColor(self.colors['text_light'])
                c.setFont("Helvetica", 10)
                desc_lines = self._wrap_text(pillar.description, 35)
                desc_y = y - 30
                for line in desc_lines[:6]:
                    c.drawString(x, desc_y, line)
                    desc_y -= 14

            c.showPage()

    def _draw_verbal_expression_section(self, c: canvas.Canvas):
        """Draw verbal expression section."""
        self._draw_section_divider(c, "Verbal Expression", 12)

        # Voice characteristics page
        if self.brand.voice_guidelines:
            self._draw_content_page(c, 13)

            # Headers
            c.setFillColor(self.colors['text_dark'])
            c.setFont("Helvetica-Bold", 10)
            c.drawString(60, PAGE_HEIGHT - 60, f"{self.brand.company_name.upper()} IS")
            c.drawString(PAGE_WIDTH / 2, PAGE_HEIGHT - 60, f"{self.brand.company_name.upper()} IS NOT")

            # Voice guidelines
            y = PAGE_HEIGHT - 120
            for vg in self.brand.voice_guidelines[:3]:
                # IS column
                c.setFillColor(self.colors['text_dark'])
                c.setFont("Helvetica", 28)
                c.drawString(60, y, vg.is_trait)

                c.setFillColor(self.colors['text_light'])
                c.setFont("Helvetica", 10)
                is_lines = self._wrap_text(vg.is_example, 45)
                is_y = y - 30
                for line in is_lines[:3]:
                    c.drawString(60, is_y, line)
                    is_y -= 14

                c.setFillColor(self.colors['aurora'])
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(60, is_y - 10, f'"{vg.is_example[:60]}..."' if len(vg.is_example) > 60 else f'"{vg.is_example}"')

                # IS NOT column
                c.setFillColor(self.colors['fog'])
                c.setFont("Helvetica", 28)
                c.drawString(PAGE_WIDTH / 2, y, vg.is_not_trait)

                c.setFillColor(self.colors['text_light'])
                c.setFont("Helvetica", 10)
                not_lines = self._wrap_text(vg.is_not_example, 45)
                not_y = y - 30
                for line in not_lines[:3]:
                    c.drawString(PAGE_WIDTH / 2, not_y, line)
                    not_y -= 14

                c.setFillColor(self.colors['dust'])
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(PAGE_WIDTH / 2, not_y - 10, f'"{vg.is_not_example[:60]}..."' if len(vg.is_not_example) > 60 else f'"{vg.is_not_example}"')

                y -= 150

            c.showPage()

    def _draw_logo_section(self, c: canvas.Canvas):
        """Draw logo section."""
        self._draw_section_divider(c, "Logo", 14)

        # Primary Logo page
        self._draw_content_page(c, 15)
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, PAGE_HEIGHT - 60, "PRIMARY LOGO")

        # Description
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica", 11)
        desc = f"{self.brand.company_name}'s primary logo consists of our wordmark accompanied by our badge. Because it's our most frequently viewed asset, the logo must be applied consistently across all collateral."
        desc_lines = self._wrap_text(desc, 45)
        y = PAGE_HEIGHT - 100
        for line in desc_lines[:5]:
            c.drawString(60, y, line)
            y -= 16

        # Logo display area
        logo_x = PAGE_WIDTH * 0.55
        logo_y = PAGE_HEIGHT * 0.5

        # Draw logo badge large
        self._draw_logo_badge(c, logo_x, logo_y, 60)

        # Company name next to badge
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica", 36)
        c.drawString(logo_x + 90, logo_y - 12, self.brand.company_name)

        # Usage note
        c.setFillColor(self.colors['text_light'])
        c.setFont("Helvetica", 10)
        c.drawString(60, 100, "Never stretch, recreate, distort, or alter our logo in any application.")
        c.drawString(60, 85, "To ensure legibility, our logo should never appear smaller than .25\" tall in print and 15 PX tall on screen.")

        c.showPage()

    def _draw_color_section(self, c: canvas.Canvas):
        """Draw color section."""
        self._draw_section_divider(c, "Color", 16)

        # Color Overview page
        self._draw_content_page(c, 17)
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, PAGE_HEIGHT - 60, "OVERVIEW")

        c.setFont("Helvetica", 24)
        c.drawString(60, PAGE_HEIGHT - 100, "Overview")

        # Description
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica", 11)
        desc = f"{self.brand.company_name}'s brand should lean into lighter layout applications with high contrast sections. Our primary accent color should be used sparingly to highlight key information."
        desc_lines = self._wrap_text(desc, 50)
        y = PAGE_HEIGHT - 140
        for line in desc_lines[:3]:
            c.drawString(60, y, line)
            y -= 16

        # Color swatches
        swatch_y = PAGE_HEIGHT - 280
        swatch_size = 100

        # Primary color
        colors_to_show = [
            (self.brand.colors.primary.hex, self.brand.colors.primary.name, white),
        ]
        if self.brand.colors.secondary:
            colors_to_show.append((self.brand.colors.secondary.hex, self.brand.colors.secondary.name, white))
        if self.brand.colors.accent:
            colors_to_show.append((self.brand.colors.accent.hex, self.brand.colors.accent.name, white))

        swatch_x = PAGE_WIDTH * 0.45
        for i, (hex_val, name, text_col) in enumerate(colors_to_show):
            x = swatch_x + i * (swatch_size + 30)

            # Draw hexagon swatch
            c.setFillColor(HexColor(hex_val))
            points = []
            cx = x + swatch_size / 2
            cy = swatch_y + swatch_size / 2
            radius = swatch_size / 2 - 5
            for j in range(6):
                angle = math.pi / 3 * j - math.pi / 2
                points.append(cx + radius * math.cos(angle))
                points.append(cy + radius * math.sin(angle))

            path = c.beginPath()
            path.moveTo(points[0], points[1])
            for j in range(1, 6):
                path.lineTo(points[j * 2], points[j * 2 + 1])
            path.close()
            c.drawPath(path, stroke=0, fill=1)

            # Name below
            c.setFillColor(self.colors['text_dark'])
            c.setFont("Helvetica-Bold", 11)
            name_width = c.stringWidth(name, "Helvetica-Bold", 11)
            c.drawString(cx - name_width / 2, swatch_y - 20, name)

            # Hex below
            c.setFillColor(self.colors['text_light'])
            c.setFont("Helvetica", 9)
            hex_width = c.stringWidth(hex_val, "Helvetica", 9)
            c.drawString(cx - hex_width / 2, swatch_y - 35, hex_val)

        c.showPage()

        # Color Codes page
        self._draw_content_page(c, 18)
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, PAGE_HEIGHT - 60, "COLOR CODES")

        c.setFont("Helvetica", 24)
        c.drawString(60, PAGE_HEIGHT - 100, "Color Codes")

        # Color specifications
        color_specs = [self.brand.colors.primary]
        if self.brand.colors.secondary:
            color_specs.append(self.brand.colors.secondary)
        if self.brand.colors.accent:
            color_specs.append(self.brand.colors.accent)

        # Display in grid
        col_width = (PAGE_WIDTH - 120) / min(4, len(color_specs) + 1)
        y = PAGE_HEIGHT - 200

        for i, color in enumerate(color_specs[:4]):
            x = 60 + i * col_width

            # Color swatch
            c.setFillColor(HexColor(color.hex))
            cx = x + 40
            cy = y + 50
            radius = 35
            points = []
            for j in range(6):
                angle = math.pi / 3 * j - math.pi / 2
                points.append(cx + radius * math.cos(angle))
                points.append(cy + radius * math.sin(angle))

            path = c.beginPath()
            path.moveTo(points[0], points[1])
            for j in range(1, 6):
                path.lineTo(points[j * 2], points[j * 2 + 1])
            path.close()
            c.drawPath(path, stroke=0, fill=1)

            # Color info below
            c.setFillColor(self.colors['text_dark'])
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x, y - 30, color.name)

            c.setFillColor(self.colors['text_light'])
            c.setFont("Helvetica", 10)
            c.drawString(x, y - 50, f"Hex - {color.hex}")
            c.drawString(x, y - 65, f"RGB - {color.rgb or 'N/A'}")
            c.drawString(x, y - 80, f"CMYK - {color.cmyk or 'N/A'}")
            c.drawString(x, y - 95, f"Pantone - {color.pantone or 'N/A'}")

        c.showPage()

    def _draw_typography_section(self, c: canvas.Canvas):
        """Draw typography section."""
        self._draw_section_divider(c, "Typography", 19)

        # Primary Font page
        self._draw_content_page(c, 20)
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, PAGE_HEIGHT - 60, "PRIMARY FONT")

        # Font name
        font_name = self.brand.typography.primary.name if self.brand.typography.primary else "Helvetica"
        c.setFillColor(self.colors['aurora'])
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, PAGE_HEIGHT - 100, font_name)

        # Description
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica", 11)
        desc = f"{font_name} is {self.brand.company_name}'s primary typeface and should be used for headlines, sub-headlines, labels, and body copy."
        desc_lines = self._wrap_text(desc, 50)
        y = PAGE_HEIGHT - 130
        for line in desc_lines[:3]:
            c.drawString(60, y, line)
            y -= 16

        # Font specimen (large)
        c.setFillColor(self.colors['fog'])
        c.setFont("Helvetica", 42)
        c.drawString(PAGE_WIDTH * 0.4, PAGE_HEIGHT * 0.55, "The quick brown fox jumps")
        c.drawString(PAGE_WIDTH * 0.4, PAGE_HEIGHT * 0.55 - 50, "over the lazy dog.")

        # Character set
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica", 14)
        c.drawString(PAGE_WIDTH * 0.4, PAGE_HEIGHT * 0.3, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        c.drawString(PAGE_WIDTH * 0.4, PAGE_HEIGHT * 0.3 - 25, "abcdefghijklmnopqrstuvwxyz")
        c.drawString(PAGE_WIDTH * 0.4, PAGE_HEIGHT * 0.3 - 50, "0123456789 !@#$%^&*()")

        if self.brand.typography.primary.download_url:
            c.setFillColor(self.colors['aurora'])
            c.setFont("Helvetica", 10)
            c.drawString(60, 80, f"Download: {self.brand.typography.primary.download_url}")

        c.showPage()

    def _draw_photography_section(self, c: canvas.Canvas):
        """Draw photography section."""
        self._draw_section_divider(c, "Photography", 21)

        # Overview page
        self._draw_content_page(c, 22)
        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, PAGE_HEIGHT - 60, "OVERVIEW")

        c.setFont("Helvetica", 24)
        c.drawString(60, PAGE_HEIGHT - 100, "Overview")

        # Description
        photo_style = self.brand.photo_style or f"{self.brand.company_name}'s imagery should reflect the tone of the company and capture positive interactions and relationships."

        c.setFillColor(self.colors['text_dark'])
        c.setFont("Helvetica", 11)
        desc_lines = self._wrap_text(photo_style, 50)
        y = PAGE_HEIGHT - 150
        for line in desc_lines[:5]:
            c.drawString(60, y, line)
            y -= 16

        # Guidelines
        guidelines = [
            "Select photos that are rich, bright, and warm in tone.",
            "Images should not be overly saturated or edited with flares.",
            "Subjects should be authentic, modern, and candid.",
            "They should be diverse in gender, ethnicity, and age.",
            "Environmental photos should be inviting and modern.",
        ]

        y -= 30
        c.setFillColor(self.colors['text_dark'])
        for guideline in guidelines:
            c.setFont("Helvetica", 10)
            c.drawString(70, y, f"• {guideline}")
            y -= 20

        c.showPage()

    def _wrap_text(self, text: str, max_chars: int) -> list:
        """Wrap text into lines of max_chars length."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(' '.join(current_line))

        return lines
