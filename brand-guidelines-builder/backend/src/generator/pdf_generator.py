"""
PDF Brand Guidelines Generator using ReportLab.
Refactored from the original template to use ExtractedBrand data model.
"""

from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, Flowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from PIL import Image as PILImage

from ..models.brand_data import ExtractedBrand


class ColoredBox(Flowable):
    """A colored rectangle with text overlay."""

    def __init__(
        self,
        width: float,
        height: float,
        color: HexColor,
        text: str = "",
        text_color: HexColor = white,
        font_size: int = 12
    ):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font_size = font_size

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        if self.text:
            self.canv.setFillColor(self.text_color)
            self.canv.setFont("Helvetica", self.font_size)
            self.canv.drawCentredString(self.width / 2, self.height / 2 - 4, self.text)


class PageNumberCanvas(canvas.Canvas):
    """Canvas subclass that adds page numbers."""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        page = len(self.pages)
        self.setFont("Helvetica", 9)
        self.setFillColor(HexColor("#666666"))
        self.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch, str(page))


class BrandGuidelinesPDF:
    """Generate a professional brand guidelines PDF."""

    def __init__(self, brand_data: ExtractedBrand):
        self.brand = brand_data
        self.colors = self._setup_colors()
        self.styles = self._create_styles()

    def _setup_colors(self) -> dict:
        """Convert extracted colors to ReportLab HexColor objects."""
        primary_hex = self.brand.colors.primary.hex
        secondary_hex = (
            self.brand.colors.secondary.hex
            if self.brand.colors.secondary
            else "#4A4A6A"
        )
        accent_hex = (
            self.brand.colors.accent.hex
            if self.brand.colors.accent
            else "#0066FF"
        )

        return {
            'primary': HexColor(primary_hex),
            'secondary': HexColor(secondary_hex),
            'accent': HexColor(accent_hex),
            'white': HexColor("#FFFFFF"),
            'light_gray': HexColor("#F5F5F7"),
            'text_dark': HexColor("#1A1A1A"),
            'text_light': HexColor("#666666"),
        }

    def _create_styles(self) -> dict:
        """Create paragraph styles for the document."""
        styles = getSampleStyleSheet()

        # Cover title
        styles.add(ParagraphStyle(
            name='CoverTitle',
            fontSize=48,
            leading=56,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=20,
        ))

        # Cover subtitle
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            fontSize=16,
            leading=24,
            textColor=self.colors['text_light'],
            fontName='Helvetica',
            alignment=TA_LEFT,
        ))

        # Section header (large)
        styles.add(ParagraphStyle(
            name='SectionHeader',
            fontSize=36,
            leading=44,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceBefore=40,
            spaceAfter=30,
        ))

        # Subsection header
        styles.add(ParagraphStyle(
            name='SubsectionHeader',
            fontSize=24,
            leading=32,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceBefore=30,
            spaceAfter=15,
        ))

        # Feature headline (large statement text)
        styles.add(ParagraphStyle(
            name='FeatureHeadline',
            fontSize=28,
            leading=36,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=20,
        ))

        # Body text
        styles.add(ParagraphStyle(
            name='BrandBodyText',
            fontSize=11,
            leading=18,
            textColor=self.colors['text_dark'],
            fontName='Helvetica',
            alignment=TA_JUSTIFY,
            spaceAfter=12,
        ))

        # Body text light
        styles.add(ParagraphStyle(
            name='BodyTextLight',
            fontSize=11,
            leading=18,
            textColor=self.colors['text_light'],
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=12,
        ))

        # Label text
        styles.add(ParagraphStyle(
            name='LabelText',
            fontSize=10,
            leading=14,
            textColor=self.colors['text_light'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceBefore=5,
            spaceAfter=5,
        ))

        # Trait name
        styles.add(ParagraphStyle(
            name='TraitName',
            fontSize=14,
            leading=20,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=5,
        ))

        # Quote text
        styles.add(ParagraphStyle(
            name='QuoteText',
            fontSize=12,
            leading=18,
            textColor=self.colors['accent'],
            fontName='Helvetica-Oblique',
            alignment=TA_LEFT,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=10,
            spaceAfter=10,
        ))

        # TOC entry
        styles.add(ParagraphStyle(
            name='TOCEntry',
            fontSize=14,
            leading=28,
            textColor=self.colors['text_dark'],
            fontName='Helvetica',
            alignment=TA_LEFT,
        ))

        # TOC number
        styles.add(ParagraphStyle(
            name='TOCNumber',
            fontSize=10,
            leading=28,
            textColor=self.colors['text_light'],
            fontName='Helvetica',
            alignment=TA_LEFT,
        ))

        # Page label
        styles.add(ParagraphStyle(
            name='PageLabel',
            fontSize=9,
            leading=12,
            textColor=self.colors['text_light'],
            fontName='Helvetica',
            alignment=TA_LEFT,
        ))

        return styles

    def generate(self, output_path: str) -> str:
        """Generate the complete PDF."""
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        story = []

        # Build document sections
        self._add_cover(story)
        self._add_toc(story)
        self._add_brand_strategy(story)
        self._add_messaging(story)
        self._add_verbal_expression(story)
        self._add_logo_section(story)
        self._add_color_section(story)
        self._add_typography_section(story)
        self._add_photography_section(story)

        # Build the PDF with page numbers
        doc.build(story, canvasmaker=PageNumberCanvas)

        return output_path

    def _add_cover(self, story: list):
        """Add cover page."""
        story.append(Spacer(1, 2.5 * inch))
        story.append(Paragraph("Brand", self.styles['CoverTitle']))
        story.append(Paragraph("Guidelines", self.styles['CoverTitle']))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(self.brand.company_name, self.styles['CoverSubtitle']))
        story.append(PageBreak())

    def _add_toc(self, story: list):
        """Add table of contents."""
        story.append(Paragraph("Contents", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 0.5 * inch))

        toc_items = [
            ("01", "Brand Strategy"),
            ("02", "Messaging"),
            ("03", "Verbal Expression"),
            ("04", "Logo"),
            ("05", "Color"),
            ("06", "Typography"),
            ("07", "Photography"),
        ]

        for num, title in toc_items:
            toc_row = Table(
                [[
                    Paragraph(num, self.styles['TOCNumber']),
                    Paragraph(title, self.styles['TOCEntry'])
                ]],
                colWidths=[0.5 * inch, 5 * inch]
            )
            toc_row.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(toc_row)

        story.append(PageBreak())

    def _add_brand_strategy(self, story: list):
        """Add brand strategy section."""
        # Section divider
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Brand", self.styles['SectionHeader']))
        story.append(Paragraph("Strategy", self.styles['SectionHeader']))
        story.append(PageBreak())

        # Brand Positioning
        story.append(Paragraph("BRAND POSITIONING", self.styles['PageLabel']))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            self.brand.positioning_headline or "Our Positioning",
            self.styles['FeatureHeadline']
        ))
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph(
            self.brand.positioning_description or "",
            self.styles['BrandBodyText']
        ))
        story.append(Spacer(1, 0.5 * inch))

        # Brand Pillars
        if self.brand.pillars:
            story.append(Paragraph("<b>BRAND PILLARS</b>", self.styles['LabelText']))
            story.append(Spacer(1, 0.2 * inch))
            for pillar in self.brand.pillars:
                story.append(Paragraph(pillar.title, self.styles['TraitName']))
                story.append(Paragraph(pillar.description, self.styles['BrandBodyText']))
                story.append(Spacer(1, 0.15 * inch))

        story.append(PageBreak())

        # Mission
        story.append(Paragraph("OUR MISSION", self.styles['PageLabel']))
        story.append(Spacer(1, 1 * inch))
        story.append(Paragraph(
            self.brand.mission or "Our Mission",
            self.styles['FeatureHeadline']
        ))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            self.brand.mission_description or "",
            self.styles['BodyTextLight']
        ))
        story.append(PageBreak())

        # Vision
        story.append(Paragraph("OUR VISION", self.styles['PageLabel']))
        story.append(Spacer(1, 1 * inch))
        story.append(Paragraph(
            self.brand.vision or "Our Vision",
            self.styles['FeatureHeadline']
        ))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            self.brand.vision_description or "",
            self.styles['BodyTextLight']
        ))
        story.append(PageBreak())

        # Brand Personality
        if self.brand.traits:
            story.append(Paragraph("BRAND PERSONALITY", self.styles['PageLabel']))
            story.append(Spacer(1, 0.5 * inch))

            for trait in self.brand.traits:
                story.append(Paragraph(trait.name, self.styles['TraitName']))
                story.append(Paragraph(trait.description, self.styles['BrandBodyText']))
                story.append(Spacer(1, 0.1 * inch))

            story.append(PageBreak())

        # Brand Promise
        story.append(Paragraph("BRAND PROMISE", self.styles['PageLabel']))
        story.append(Spacer(1, 1 * inch))
        story.append(Paragraph(
            self.brand.promise or "Our Promise",
            self.styles['FeatureHeadline']
        ))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            self.brand.promise_description or "",
            self.styles['BodyTextLight']
        ))
        story.append(PageBreak())

        # Boilerplate
        if self.brand.boilerplate:
            story.append(Paragraph("BOILERPLATE", self.styles['PageLabel']))
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph(
                f"About {self.brand.company_name}",
                self.styles['SubsectionHeader']
            ))
            story.append(Spacer(1, 0.25 * inch))
            story.append(Paragraph(self.brand.boilerplate, self.styles['BrandBodyText']))
            story.append(PageBreak())

    def _add_messaging(self, story: list):
        """Add messaging section."""
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Messaging", self.styles['SectionHeader']))
        story.append(Paragraph("Frameworks", self.styles['SectionHeader']))
        story.append(PageBreak())

        # Brand Pillars Overview
        if self.brand.pillars:
            story.append(Paragraph("OVERVIEW", self.styles['PageLabel']))
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph("Brand Pillars", self.styles['SubsectionHeader']))
            story.append(Spacer(1, 0.3 * inch))

            pillar_data = [
                [f"0{i+1}" for i in range(len(self.brand.pillars))],
                [p.title for p in self.brand.pillars],
            ]

            pillar_table = Table(pillar_data, colWidths=[2 * inch] * len(self.brand.pillars))
            pillar_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['text_light']),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, 1), 14),
                ('TEXTCOLOR', (0, 1), (-1, 1), self.colors['primary']),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ]))
            story.append(pillar_table)

        story.append(PageBreak())

    def _add_verbal_expression(self, story: list):
        """Add verbal expression section."""
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Verbal", self.styles['SectionHeader']))
        story.append(Paragraph("Expression", self.styles['SectionHeader']))
        story.append(PageBreak())

        # Voice characteristics
        if self.brand.voice_guidelines:
            story.append(Paragraph("VOICE CHARACTERISTICS", self.styles['PageLabel']))
            story.append(Spacer(1, 0.5 * inch))

            voice_header = [
                Paragraph(f"<b>{self.brand.company_name} IS</b>", self.styles['TraitName']),
                Paragraph(f"<b>{self.brand.company_name} IS NOT</b>", self.styles['TraitName'])
            ]

            voice_data = [voice_header]

            for vg in self.brand.voice_guidelines:
                voice_data.append([
                    Paragraph(
                        f"<b>{vg.is_trait}</b><br/><i>\"{vg.is_example}\"</i>",
                        self.styles['BrandBodyText']
                    ),
                    Paragraph(
                        f"<b>{vg.is_not_trait}</b><br/><i>\"{vg.is_not_example}\"</i>",
                        self.styles['BrandBodyText']
                    ),
                ])

            voice_table = Table(voice_data, colWidths=[3 * inch, 3 * inch])
            voice_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.colors['light_gray']),
            ]))
            story.append(voice_table)

        story.append(PageBreak())

    def _add_logo_section(self, story: list):
        """Add logo section."""
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Logo", self.styles['SectionHeader']))
        story.append(PageBreak())

        # Primary Logo
        story.append(Paragraph("PRIMARY LOGO", self.styles['PageLabel']))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("Primary Logo", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(
            f"{self.brand.company_name}'s primary logo should be applied consistently "
            "across all collateral.",
            self.styles['BrandBodyText']
        ))
        story.append(Spacer(1, 0.25 * inch))

        # Logo placeholder or actual logo
        if self.brand.logo and self.brand.logo.primary_data:
            try:
                # Try to embed actual logo
                logo_img = self._create_logo_image(self.brand.logo.primary_data)
                if logo_img:
                    story.append(logo_img)
                else:
                    story.append(self._logo_placeholder())
            except Exception:
                story.append(self._logo_placeholder())
        else:
            story.append(self._logo_placeholder())

        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph(
            "Never stretch, recreate, distort, or alter the logo in any application.",
            self.styles['BodyTextLight']
        ))

        story.append(PageBreak())

    def _logo_placeholder(self) -> ColoredBox:
        """Create a placeholder for logo."""
        return ColoredBox(
            4 * inch, 1.5 * inch,
            self.colors['light_gray'],
            "[ Primary Logo Placement ]",
            self.colors['text_light'],
            14
        )

    def _create_logo_image(self, logo_data: bytes) -> Image | None:
        """Create a ReportLab Image from logo data."""
        try:
            # Open with PIL to get dimensions
            pil_img = PILImage.open(BytesIO(logo_data))
            width, height = pil_img.size

            # Scale to fit (max 4 inches wide, 2 inches tall)
            max_width = 4 * inch
            max_height = 2 * inch

            aspect = width / height
            if width > height:
                img_width = min(max_width, width)
                img_height = img_width / aspect
            else:
                img_height = min(max_height, height)
                img_width = img_height * aspect

            if img_width > max_width:
                img_width = max_width
                img_height = img_width / aspect

            if img_height > max_height:
                img_height = max_height
                img_width = img_height * aspect

            return Image(BytesIO(logo_data), width=img_width, height=img_height)
        except Exception:
            return None

    def _add_color_section(self, story: list):
        """Add color section."""
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Color", self.styles['SectionHeader']))
        story.append(PageBreak())

        # Overview
        story.append(Paragraph("OVERVIEW", self.styles['PageLabel']))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("Overview", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(
            f"{self.brand.company_name}'s brand should lean into lighter layout applications "
            "with high contrast sections. Our primary accent color should be used sparingly "
            "to highlight key information.",
            self.styles['BrandBodyText']
        ))
        story.append(Spacer(1, 0.5 * inch))

        # Color swatches
        story.append(Paragraph("<b>PRIMARY COLORS</b>", self.styles['LabelText']))
        story.append(Spacer(1, 0.15 * inch))

        primary_boxes = [
            ColoredBox(
                1.2 * inch, 1 * inch,
                self.colors['primary'],
                self.brand.colors.primary.name,
                white, 9
            ),
        ]

        if self.brand.colors.secondary:
            primary_boxes.append(ColoredBox(
                1.2 * inch, 1 * inch,
                self.colors['secondary'],
                self.brand.colors.secondary.name,
                white, 9
            ))

        if self.brand.colors.accent:
            primary_boxes.append(ColoredBox(
                1.2 * inch, 1 * inch,
                self.colors['accent'],
                self.brand.colors.accent.name,
                white, 9
            ))

        primary_colors = Table([primary_boxes], colWidths=[1.4 * inch] * len(primary_boxes))
        primary_colors.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(primary_colors)
        story.append(PageBreak())

        # Color Codes
        story.append(Paragraph("COLOR CODES", self.styles['PageLabel']))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("Color Codes", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 0.3 * inch))

        color_specs = [self.brand.colors.primary]
        if self.brand.colors.secondary:
            color_specs.append(self.brand.colors.secondary)
        if self.brand.colors.accent:
            color_specs.append(self.brand.colors.accent)

        for color in color_specs:
            story.append(Paragraph(f"<b>{color.name}</b>", self.styles['TraitName']))
            story.append(Paragraph(
                f"Hex - {color.hex}<br/>"
                f"RGB - {color.rgb or 'N/A'}<br/>"
                f"CMYK - {color.cmyk or 'N/A'}<br/>"
                f"Pantone - {color.pantone or 'N/A'}",
                self.styles['BodyTextLight']
            ))
            story.append(Spacer(1, 0.2 * inch))

        story.append(PageBreak())

    def _add_typography_section(self, story: list):
        """Add typography section."""
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Typography", self.styles['SectionHeader']))
        story.append(PageBreak())

        # Primary Font
        story.append(Paragraph("PRIMARY FONT", self.styles['PageLabel']))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            self.brand.typography.primary.name,
            self.styles['SubsectionHeader']
        ))
        story.append(Spacer(1, 0.3 * inch))

        if self.brand.typography.primary.download_url:
            story.append(Paragraph(
                f"Download: {self.brand.typography.primary.download_url}",
                self.styles['BodyTextLight']
            ))
        story.append(Spacer(1, 0.5 * inch))

        # Font specimen
        story.append(Paragraph(
            "The quick brown fox jumps over the lazy dog.",
            self.styles['FeatureHeadline']
        ))
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ<br/>abcdefghijklmnopqrstuvwxyz<br/>0123456789 !@#$%^&*()",
            self.styles['BrandBodyText']
        ))
        story.append(PageBreak())

        # System Alternative
        if self.brand.typography.secondary or self.brand.typography.system_fallback:
            story.append(Paragraph("SYSTEM ALTERNATIVE", self.styles['PageLabel']))
            story.append(Spacer(1, 0.5 * inch))

            fallback_name = (
                self.brand.typography.secondary.name
                if self.brand.typography.secondary
                else self.brand.typography.system_fallback
            )
            story.append(Paragraph(fallback_name, self.styles['SubsectionHeader']))
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph(
                "When the primary font is unavailable, use this system alternative "
                "to maintain brand consistency.",
                self.styles['BrandBodyText']
            ))
            story.append(PageBreak())

    def _add_photography_section(self, story: list):
        """Add photography section."""
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Photography", self.styles['SectionHeader']))
        story.append(PageBreak())

        # Overview
        story.append(Paragraph("OVERVIEW", self.styles['PageLabel']))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("Overview", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 0.3 * inch))

        photo_style = self.brand.photo_style or (
            f"{self.brand.company_name}'s imagery should reflect the tone of the company "
            "and capture positive interactions and relationships."
        )
        story.append(Paragraph(photo_style, self.styles['BrandBodyText']))
        story.append(Spacer(1, 0.3 * inch))

        guidelines = [
            "Select photos that are rich, bright, and warm in tone.",
            "Images should not be overly saturated or edited with flares.",
            "Subjects should be authentic, modern, and candid.",
            "They should be diverse in gender, ethnicity, and age.",
            "Environmental photos should be inviting and modern.",
        ]

        for guideline in guidelines:
            story.append(Paragraph(f"• {guideline}", self.styles['BrandBodyText']))

        story.append(PageBreak())
