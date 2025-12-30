#!/usr/bin/env python3
"""
Brand Guidelines Template Generator
Generates a professional brand guidelines PDF template following the CreditKey style.
This template is designed for use in automated brand guide generation tools.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, Flowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ============================================================================
# TEMPLATE CONFIGURATION - Edit these values for each brand
# ============================================================================

BRAND_CONFIG = {
    # Brand Identity
    "company_name": "{{COMPANY_NAME}}",
    "tagline": "{{TAGLINE}}",
    "year": "{{YEAR}}",
    
    # Brand Positioning
    "positioning_headline": "{{POSITIONING_HEADLINE}}",
    "positioning_description": "{{POSITIONING_DESCRIPTION}}",
    
    # Brand Pillars (3 pillars)
    "pillar_1_title": "{{PILLAR_1_TITLE}}",
    "pillar_1_description": "{{PILLAR_1_DESCRIPTION}}",
    
    "pillar_2_title": "{{PILLAR_2_TITLE}}",
    "pillar_2_description": "{{PILLAR_2_DESCRIPTION}}",
    
    "pillar_3_title": "{{PILLAR_3_TITLE}}",
    "pillar_3_description": "{{PILLAR_3_DESCRIPTION}}",
    
    # Mission & Vision
    "mission": "{{MISSION_STATEMENT}}",
    "mission_description": "{{MISSION_DESCRIPTION}}",
    
    "vision": "{{VISION_STATEMENT}}",
    "vision_description": "{{VISION_DESCRIPTION}}",
    
    # Brand Personality (4 traits)
    "personality_intro": "{{PERSONALITY_INTRO}}",
    "trait_1_name": "{{TRAIT_1_NAME}}",
    "trait_1_description": "{{TRAIT_1_DESCRIPTION}}",
    "trait_2_name": "{{TRAIT_2_NAME}}",
    "trait_2_description": "{{TRAIT_2_DESCRIPTION}}",
    "trait_3_name": "{{TRAIT_3_NAME}}",
    "trait_3_description": "{{TRAIT_3_DESCRIPTION}}",
    "trait_4_name": "{{TRAIT_4_NAME}}",
    "trait_4_description": "{{TRAIT_4_DESCRIPTION}}",
    
    # Brand Promise
    "promise": "{{BRAND_PROMISE}}",
    "promise_description": "{{PROMISE_DESCRIPTION}}",
    
    # Boilerplate
    "boilerplate_headline": "{{BOILERPLATE_HEADLINE}}",
    "boilerplate_full": "{{BOILERPLATE_FULL}}",
    
    # Colors
    "color_primary_name": "{{PRIMARY_COLOR_NAME}}",
    "color_primary_hex": "{{PRIMARY_COLOR_HEX}}",
    "color_primary_rgb": "{{PRIMARY_COLOR_RGB}}",
    "color_primary_cmyk": "{{PRIMARY_COLOR_CMYK}}",
    "color_primary_pantone": "{{PRIMARY_COLOR_PANTONE}}",
    
    "color_secondary_name": "{{SECONDARY_COLOR_NAME}}",
    "color_secondary_hex": "{{SECONDARY_COLOR_HEX}}",
    "color_secondary_rgb": "{{SECONDARY_COLOR_RGB}}",
    "color_secondary_cmyk": "{{SECONDARY_COLOR_CMYK}}",
    "color_secondary_pantone": "{{SECONDARY_COLOR_PANTONE}}",
    
    "color_accent_name": "{{ACCENT_COLOR_NAME}}",
    "color_accent_hex": "{{ACCENT_COLOR_HEX}}",
    "color_accent_rgb": "{{ACCENT_COLOR_RGB}}",
    "color_accent_cmyk": "{{ACCENT_COLOR_CMYK}}",
    "color_accent_pantone": "{{ACCENT_COLOR_PANTONE}}",
    
    "color_neutral_1_name": "{{NEUTRAL_1_NAME}}",
    "color_neutral_1_hex": "{{NEUTRAL_1_HEX}}",
    "color_neutral_2_name": "{{NEUTRAL_2_NAME}}",
    "color_neutral_2_hex": "{{NEUTRAL_2_HEX}}",
    "color_neutral_3_name": "{{NEUTRAL_3_NAME}}",
    "color_neutral_3_hex": "{{NEUTRAL_3_HEX}}",
    "color_neutral_4_name": "{{NEUTRAL_4_NAME}}",
    "color_neutral_4_hex": "{{NEUTRAL_4_HEX}}",
    
    # Typography
    "font_primary": "{{PRIMARY_FONT}}",
    "font_primary_description": "{{PRIMARY_FONT_DESCRIPTION}}",
    "font_primary_download": "{{PRIMARY_FONT_DOWNLOAD_URL}}",
    
    "font_system": "{{SYSTEM_FONT}}",
    "font_system_description": "{{SYSTEM_FONT_DESCRIPTION}}",
    
    # Photography
    "photo_style": "{{PHOTOGRAPHY_STYLE_DESCRIPTION}}",
    
    # Voice Guidelines
    "voice_is_1": "{{VOICE_IS_1}}",
    "voice_is_1_example": "{{VOICE_IS_1_EXAMPLE}}",
    "voice_is_not_1": "{{VOICE_IS_NOT_1}}",
    "voice_is_not_1_example": "{{VOICE_IS_NOT_1_EXAMPLE}}",
    
    "voice_is_2": "{{VOICE_IS_2}}",
    "voice_is_2_example": "{{VOICE_IS_2_EXAMPLE}}",
    "voice_is_not_2": "{{VOICE_IS_NOT_2}}",
    "voice_is_not_2_example": "{{VOICE_IS_NOT_2_EXAMPLE}}",
    
    "voice_is_3": "{{VOICE_IS_3}}",
    "voice_is_3_example": "{{VOICE_IS_3_EXAMPLE}}",
    "voice_is_not_3": "{{VOICE_IS_NOT_3}}",
    "voice_is_not_3_example": "{{VOICE_IS_NOT_3_EXAMPLE}}",
}

# Default template colors (will be replaced by brand colors)
TEMPLATE_COLORS = {
    "primary": HexColor("#1a1a2e"),      # Deep navy
    "secondary": HexColor("#4a4a6a"),     # Medium gray-blue
    "accent": HexColor("#0066ff"),        # Bright blue
    "white": HexColor("#ffffff"),
    "light_gray": HexColor("#f5f5f7"),
    "text_dark": HexColor("#1a1a1a"),
    "text_light": HexColor("#666666"),
}


class ColoredBox(Flowable):
    """A colored rectangle with text overlay."""
    def __init__(self, width, height, color, text="", text_color=white, font_size=12):
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
            self.canv.drawCentredString(self.width/2, self.height/2 - 4, self.text)


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
        self.drawRightString(letter[0] - 0.75*inch, 0.5*inch, str(page))


def create_styles():
    """Create paragraph styles for the document."""
    styles = getSampleStyleSheet()
    
    # Cover title
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontSize=48,
        leading=56,
        textColor=TEMPLATE_COLORS["primary"],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=20,
    ))
    
    # Cover subtitle
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontSize=16,
        leading=24,
        textColor=TEMPLATE_COLORS["text_light"],
        fontName='Helvetica',
        alignment=TA_LEFT,
    ))
    
    # Section header (large)
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=36,
        leading=44,
        textColor=TEMPLATE_COLORS["primary"],
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
        textColor=TEMPLATE_COLORS["primary"],
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
        textColor=TEMPLATE_COLORS["primary"],
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
        textColor=TEMPLATE_COLORS["text_dark"],
        fontName='Helvetica',
        alignment=TA_JUSTIFY,
        spaceAfter=12,
    ))
    
    # Body text light
    styles.add(ParagraphStyle(
        name='BodyTextLight',
        fontSize=11,
        leading=18,
        textColor=TEMPLATE_COLORS["text_light"],
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=12,
    ))
    
    # Label text
    styles.add(ParagraphStyle(
        name='LabelText',
        fontSize=10,
        leading=14,
        textColor=TEMPLATE_COLORS["text_light"],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceBefore=5,
        spaceAfter=5,
    ))
    
    # Personality trait name
    styles.add(ParagraphStyle(
        name='TraitName',
        fontSize=14,
        leading=20,
        textColor=TEMPLATE_COLORS["primary"],
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=5,
    ))
    
    # Quote or highlight text
    styles.add(ParagraphStyle(
        name='QuoteText',
        fontSize=12,
        leading=18,
        textColor=TEMPLATE_COLORS["accent"],
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
        textColor=TEMPLATE_COLORS["text_dark"],
        fontName='Helvetica',
        alignment=TA_LEFT,
    ))
    
    # TOC number
    styles.add(ParagraphStyle(
        name='TOCNumber',
        fontSize=10,
        leading=28,
        textColor=TEMPLATE_COLORS["text_light"],
        fontName='Helvetica',
        alignment=TA_LEFT,
    ))
    
    # Page label (top of page)
    styles.add(ParagraphStyle(
        name='PageLabel',
        fontSize=9,
        leading=12,
        textColor=TEMPLATE_COLORS["text_light"],
        fontName='Helvetica',
        alignment=TA_LEFT,
    ))
    
    return styles


def create_cover_page(story, styles, config):
    """Create the cover page."""
    story.append(Spacer(1, 2.5*inch))
    story.append(Paragraph("Brand", styles['CoverTitle']))
    story.append(Paragraph("Guidelines", styles['CoverTitle']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(config.get("year", "2024"), styles['CoverSubtitle']))
    story.append(PageBreak())


def create_toc(story, styles):
    """Create table of contents."""
    story.append(Paragraph("Contents", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.5*inch))
    
    toc_items = [
        ("01", "Brand Strategy"),
        ("02", "Messaging"),
        ("03", "Verbal Expression"),
        ("04", "Logo"),
        ("05", "Color"),
        ("06", "Typography"),
        ("07", "Photography"),
        ("08", "Patterns"),
        ("09", "Work Samples"),
    ]
    
    for num, title in toc_items:
        toc_row = Table(
            [[Paragraph(num, styles['TOCNumber']), Paragraph(title, styles['TOCEntry'])]],
            colWidths=[0.5*inch, 5*inch]
        )
        toc_row.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(toc_row)
    
    story.append(PageBreak())


def create_brand_strategy_section(story, styles, config):
    """Create the Brand Strategy section."""
    # Section divider page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Brand", styles['SectionHeader']))
    story.append(Paragraph("Strategy", styles['SectionHeader']))
    story.append(PageBreak())
    
    # Brand Positioning
    story.append(Paragraph("BRAND POSITIONING", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(config.get("positioning_headline", "{{POSITIONING_HEADLINE}}"), styles['FeatureHeadline']))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph(config.get("positioning_description", "{{POSITIONING_DESCRIPTION}}"), styles['BrandBodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    # Brand Pillars
    pillars = [
        (config.get("pillar_1_title", "{{PILLAR_1_TITLE}}"), config.get("pillar_1_description", "{{PILLAR_1_DESCRIPTION}}")),
        (config.get("pillar_2_title", "{{PILLAR_2_TITLE}}"), config.get("pillar_2_description", "{{PILLAR_2_DESCRIPTION}}")),
        (config.get("pillar_3_title", "{{PILLAR_3_TITLE}}"), config.get("pillar_3_description", "{{PILLAR_3_DESCRIPTION}}")),
    ]
    
    for title, desc in pillars:
        story.append(Paragraph(title, styles['TraitName']))
        story.append(Paragraph(desc, styles['BrandBodyText']))
        story.append(Spacer(1, 0.15*inch))
    
    story.append(PageBreak())
    
    # Mission
    story.append(Paragraph("OUR MISSION", styles['PageLabel']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(config.get("mission", "{{MISSION_STATEMENT}}"), styles['FeatureHeadline']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(config.get("mission_description", "{{MISSION_DESCRIPTION}}"), styles['BodyTextLight']))
    story.append(PageBreak())
    
    # Vision
    story.append(Paragraph("OUR VISION", styles['PageLabel']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(config.get("vision", "{{VISION_STATEMENT}}"), styles['FeatureHeadline']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(config.get("vision_description", "{{VISION_DESCRIPTION}}"), styles['BodyTextLight']))
    story.append(PageBreak())
    
    # Brand Personality
    story.append(Paragraph("BRAND PERSONALITY", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(config.get("personality_intro", "{{PERSONALITY_INTRO}}"), styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    traits = [
        (config.get("trait_1_name", "{{TRAIT_1_NAME}}"), config.get("trait_1_description", "{{TRAIT_1_DESCRIPTION}}")),
        (config.get("trait_2_name", "{{TRAIT_2_NAME}}"), config.get("trait_2_description", "{{TRAIT_2_DESCRIPTION}}")),
        (config.get("trait_3_name", "{{TRAIT_3_NAME}}"), config.get("trait_3_description", "{{TRAIT_3_DESCRIPTION}}")),
        (config.get("trait_4_name", "{{TRAIT_4_NAME}}"), config.get("trait_4_description", "{{TRAIT_4_DESCRIPTION}}")),
    ]
    
    for name, desc in traits:
        story.append(Paragraph(name, styles['TraitName']))
        story.append(Paragraph(desc, styles['BrandBodyText']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Brand Promise
    story.append(Paragraph("BRAND PROMISE", styles['PageLabel']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(config.get("promise", "{{BRAND_PROMISE}}"), styles['FeatureHeadline']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(config.get("promise_description", "{{PROMISE_DESCRIPTION}}"), styles['BodyTextLight']))
    story.append(PageBreak())
    
    # Boilerplate
    story.append(Paragraph("BOILERPLATE", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(config.get("boilerplate_headline", "{{BOILERPLATE_HEADLINE}}"), styles['SubsectionHeader']))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph(config.get("boilerplate_full", "{{BOILERPLATE_FULL}}"), styles['BrandBodyText']))
    story.append(PageBreak())


def create_messaging_section(story, styles, config):
    """Create the Messaging Frameworks section."""
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Messaging", styles['SectionHeader']))
    story.append(Paragraph("Frameworks", styles['SectionHeader']))
    story.append(PageBreak())
    
    # Brand Pillars Overview
    story.append(Paragraph("OVERVIEW", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Brand Pillars", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    
    # Create pillar boxes
    pillar_data = [
        ["01", "02", "03"],
        [
            config.get("pillar_1_title", "{{PILLAR_1_TITLE}}"),
            config.get("pillar_2_title", "{{PILLAR_2_TITLE}}"),
            config.get("pillar_3_title", "{{PILLAR_3_TITLE}}")
        ],
    ]
    
    pillar_table = Table(pillar_data, colWidths=[2*inch, 2*inch, 2*inch])
    pillar_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('TEXTCOLOR', (0, 0), (-1, 0), TEMPLATE_COLORS["text_light"]),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('TEXTCOLOR', (0, 1), (-1, 1), TEMPLATE_COLORS["primary"]),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(pillar_table)
    story.append(Spacer(1, 0.5*inch))
    
    # Messaging descriptions
    story.append(Paragraph("Pillar messaging should be adapted for different audience segments while maintaining core themes.", styles['BrandBodyText']))
    
    story.append(PageBreak())
    
    # Value Proposition
    story.append(Paragraph("VALUE PROPOSITION", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Value Proposition", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("{{VALUE_PROPOSITION_HEADLINE}}", styles['FeatureHeadline']))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("{{VALUE_PROPOSITION_DESCRIPTION}}", styles['BrandBodyText']))
    story.append(PageBreak())


def create_verbal_expression_section(story, styles, config):
    """Create the Verbal Expression section."""
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Verbal", styles['SectionHeader']))
    story.append(Paragraph("Expression", styles['SectionHeader']))
    story.append(PageBreak())
    
    # Voice characteristics table
    story.append(Paragraph("VOICE CHARACTERISTICS", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    
    voice_header = [
        Paragraph(f"<b>{config.get('company_name', '{{COMPANY_NAME}}')} IS</b>", styles['TraitName']),
        Paragraph(f"<b>{config.get('company_name', '{{COMPANY_NAME}}')} IS NOT</b>", styles['TraitName'])
    ]
    
    voice_data = [
        voice_header,
        [
            Paragraph(f"<b>{config.get('voice_is_1', '{{VOICE_IS_1}}')}</b><br/><i>\"{config.get('voice_is_1_example', '{{VOICE_IS_1_EXAMPLE}}')}\"</i>", styles['BrandBodyText']),
            Paragraph(f"<b>{config.get('voice_is_not_1', '{{VOICE_IS_NOT_1}}')}</b><br/><i>\"{config.get('voice_is_not_1_example', '{{VOICE_IS_NOT_1_EXAMPLE}}')}\"</i>", styles['BrandBodyText']),
        ],
        [
            Paragraph(f"<b>{config.get('voice_is_2', '{{VOICE_IS_2}}')}</b><br/><i>\"{config.get('voice_is_2_example', '{{VOICE_IS_2_EXAMPLE}}')}\"</i>", styles['BrandBodyText']),
            Paragraph(f"<b>{config.get('voice_is_not_2', '{{VOICE_IS_NOT_2}}')}</b><br/><i>\"{config.get('voice_is_not_2_example', '{{VOICE_IS_NOT_2_EXAMPLE}}')}\"</i>", styles['BrandBodyText']),
        ],
        [
            Paragraph(f"<b>{config.get('voice_is_3', '{{VOICE_IS_3}}')}</b><br/><i>\"{config.get('voice_is_3_example', '{{VOICE_IS_3_EXAMPLE}}')}\"</i>", styles['BrandBodyText']),
            Paragraph(f"<b>{config.get('voice_is_not_3', '{{VOICE_IS_NOT_3}}')}</b><br/><i>\"{config.get('voice_is_not_3_example', '{{VOICE_IS_NOT_3_EXAMPLE}}')}\"</i>", styles['BrandBodyText']),
        ],
    ]
    
    voice_table = Table(voice_data, colWidths=[3*inch, 3*inch])
    voice_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, TEMPLATE_COLORS["light_gray"]),
    ]))
    story.append(voice_table)
    story.append(PageBreak())
    
    # Tone Spectrum
    story.append(Paragraph("SPECTRUM", styles['PageLabel']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("While brand voice should remain consistent in everything we write, there is a spectrum of tones within that voice that you can adopt to suit a particular communication.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    spectrum_header = ["SCENARIO", "USE CASE SAMPLE", "RATIONALE"]
    spectrum_data = [
        spectrum_header,
        ["Education, Product Copy", "{{EDUCATION_EXAMPLE}}", "Since product education is the primary objective here, this copy should be clear and instructional."],
        ["Website, Marketing Communications", "{{MARKETING_EXAMPLE}}", "Website copy should convey confidence and provide a clear understanding of the product."],
        ["Advertising, Social Media", "{{SOCIAL_EXAMPLE}}", "The most conversational messaging, social media copy should showcase approachability."],
        ["Internal Communication", "{{INTERNAL_EXAMPLE}}", "Internal messaging reflects optimism and positive company culture."],
    ]
    
    spectrum_table = Table(spectrum_data, colWidths=[1.8*inch, 2.2*inch, 2*inch])
    spectrum_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), TEMPLATE_COLORS["text_light"]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, TEMPLATE_COLORS["light_gray"]),
    ]))
    story.append(spectrum_table)
    story.append(PageBreak())
    
    # AP Style / Writing Guidelines
    story.append(Paragraph("WRITING STYLE", styles['PageLabel']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("{{COMPANY_NAME}} follows [style guide reference] as its third-party source of style authority. These additional rules should serve as guideposts when crafting copy.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    style_rules = [
        ("Headlines", "Write main headlines in title case; all others should be sentence case.", "{{HEADLINE_EXAMPLE}}"),
        ("Serial Comma", "{{COMPANY_NAME}} uses the serial/Oxford comma.", "{{COMMA_EXAMPLE}}"),
        ("Percentages", "Always use a numeral and percent symbol, unless the percentage starts a sentence.", "{{PERCENT_EXAMPLE}}"),
        ("Numerals", "Spell out one through nine; use numerals for 10 and above.", "{{NUMERAL_EXAMPLE}}"),
    ]
    
    for rule, desc, example in style_rules:
        story.append(Paragraph(f"<b>{rule}</b>", styles['TraitName']))
        story.append(Paragraph(desc, styles['BrandBodyText']))
        story.append(Paragraph(f"<i>{example}</i>", styles['QuoteText']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Inclusive Language
    story.append(Paragraph("INCLUSIVE LANGUAGE", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"As in all areas of our company, {config.get('company_name', '{{COMPANY_NAME}}')} writes with every reader in mind, using inclusive language.", styles['FeatureHeadline']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("That means zero words, phrases, or tones that reflect prejudiced, stereotyped, or discriminatory views of particular people.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.25*inch))
    
    inclusive_points = [
        "Is the inclusion of personal characteristics such as gender, religion, racial group, disability, or age truly necessary? If not, leave them out.",
        "Are references to group characteristics couched in inclusive terms?",
        "Do references to people reflect the diversity of that audience?",
        "Is your use of jargon and acronyms excluding people who may not have specialized knowledge?",
    ]
    
    for point in inclusive_points:
        story.append(Paragraph(f"• {point}", styles['BrandBodyText']))
    
    story.append(PageBreak())


def create_logo_section(story, styles, config):
    """Create the Logo section."""
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Logo", styles['SectionHeader']))
    story.append(PageBreak())
    
    # Primary Logo
    story.append(Paragraph("PRIMARY LOGO", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Primary Logo", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"{config.get('company_name', '{{COMPANY_NAME}}')}'s primary logo consists of our wordmark accompanied by our badge. Because it's our most frequently viewed asset, the logo must be applied consistently across all collateral.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.25*inch))
    
    # Logo placeholder
    logo_placeholder = ColoredBox(4*inch, 1.5*inch, TEMPLATE_COLORS["light_gray"], "[ Primary Logo Placement ]", TEMPLATE_COLORS["text_light"], 14)
    story.append(logo_placeholder)
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("Never stretch, recreate, distort, or alter our logo in any application — only use it as provided.", styles['BodyTextLight']))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("To ensure legibility across all mediums, our logo should never appear smaller than .25\" tall in print and 15px tall on screen.", styles['BodyTextLight']))
    story.append(PageBreak())
    
    # Logo Badge
    story.append(Paragraph("LOGO BADGE", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Logo Badge", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("The logo badge should be used in instances where the primary logo is not feasible (usually because of size) or repetitive (in paginated content like white papers or presentations).", styles['BrandBodyText']))
    story.append(Spacer(1, 0.25*inch))
    
    badge_placeholder = ColoredBox(1.5*inch, 1.5*inch, TEMPLATE_COLORS["light_gray"], "[ Badge ]", TEMPLATE_COLORS["text_light"], 12)
    story.append(badge_placeholder)
    story.append(PageBreak())
    
    # Clear Space
    story.append(Paragraph("CLEAR SPACE", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Clearspace", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Clearspace is the negative space maintained around the logo and logo badge, allowing them to breathe.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("To maintain our logo's integrity and ensure visibility, clear space must be free from graphics, text, or other logos.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.25*inch))
    
    clearspace_placeholder = ColoredBox(4*inch, 2*inch, TEMPLATE_COLORS["light_gray"], "[ Clearspace Diagram ]", TEMPLATE_COLORS["text_light"], 14)
    story.append(clearspace_placeholder)
    story.append(PageBreak())
    
    # Variations
    story.append(Paragraph("VARIATIONS", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Variations", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("The logo has four color variations to ensure legibility against any background. Do not build other color variations.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    var_data = [
        ["PRIMARY", "REVERSE"],
        [ColoredBox(2.5*inch, 1*inch, TEMPLATE_COLORS["white"], "[ Primary on Light ]", TEMPLATE_COLORS["text_light"], 10),
         ColoredBox(2.5*inch, 1*inch, TEMPLATE_COLORS["primary"], "[ Reverse on Dark ]", white, 10)],
        ["MONOCHROMATIC - DARK", "MONOCHROMATIC - LIGHT"],
        [ColoredBox(2.5*inch, 1*inch, TEMPLATE_COLORS["white"], "[ Black Logo ]", TEMPLATE_COLORS["text_light"], 10),
         ColoredBox(2.5*inch, 1*inch, TEMPLATE_COLORS["primary"], "[ White Logo ]", white, 10)],
    ]
    
    var_table = Table(var_data, colWidths=[3*inch, 3*inch])
    var_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 2), (-1, 2), 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), TEMPLATE_COLORS["text_light"]),
        ('TEXTCOLOR', (0, 2), (-1, 2), TEMPLATE_COLORS["text_light"]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(var_table)
    story.append(PageBreak())
    
    # Logo Don'ts
    story.append(Paragraph("LOGO DON'TS", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Logo Don'ts", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    
    donts = [
        "Don't rotate the wordmark or badge.",
        "Don't distort, stretch, or skew logo proportions.",
        "Don't add effects (drop shadows, glows, gradients).",
        "Don't create stacked or edited versions.",
        "Don't remove the badge from the logo.",
        "Don't change colors or outline of the wordmark or badge.",
    ]
    
    for i, dont in enumerate(donts, 1):
        story.append(Paragraph(f"{i}. {dont}", styles['BrandBodyText']))
    
    story.append(PageBreak())


def create_color_section(story, styles, config):
    """Create the Color section."""
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Color", styles['SectionHeader']))
    story.append(PageBreak())
    
    # Overview
    story.append(Paragraph("OVERVIEW", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Overview", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"{config.get('company_name', '{{COMPANY_NAME}}')}'s brand should lean into lighter layout applications with high contrast sections. This ensures that our brand feels clean and sleek. Our primary accent color should be used sparingly to highlight key information.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    # Color swatches
    story.append(Paragraph("<b>PRIMARY COLORS</b>", styles['LabelText']))
    story.append(Spacer(1, 0.15*inch))
    
    primary_colors = Table([
        [ColoredBox(1.2*inch, 1*inch, TEMPLATE_COLORS["primary"], config.get("color_primary_name", "Primary"), white, 9),
         ColoredBox(1.2*inch, 1*inch, TEMPLATE_COLORS["accent"], config.get("color_accent_name", "Accent"), white, 9),
         ColoredBox(1.2*inch, 1*inch, TEMPLATE_COLORS["white"], config.get("color_neutral_1_name", "White"), TEMPLATE_COLORS["text_light"], 9),
         ColoredBox(1.2*inch, 1*inch, TEMPLATE_COLORS["secondary"], config.get("color_secondary_name", "Secondary"), white, 9)],
    ], colWidths=[1.4*inch, 1.4*inch, 1.4*inch, 1.4*inch])
    primary_colors.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(primary_colors)
    story.append(Spacer(1, 0.5*inch))
    
    # Neutral colors
    story.append(Paragraph("<b>NEUTRAL COLORS</b>", styles['LabelText']))
    story.append(Spacer(1, 0.15*inch))
    
    neutral_colors = Table([
        [ColoredBox(1.2*inch, 0.8*inch, TEMPLATE_COLORS["light_gray"], config.get("color_neutral_2_name", "Light Gray"), TEMPLATE_COLORS["text_dark"], 8),
         ColoredBox(1.2*inch, 0.8*inch, HexColor("#e0e0e0"), config.get("color_neutral_3_name", "Medium Gray"), TEMPLATE_COLORS["text_dark"], 8),
         ColoredBox(1.2*inch, 0.8*inch, HexColor("#c0c0c0"), config.get("color_neutral_4_name", "Dark Gray"), TEMPLATE_COLORS["text_dark"], 8),
         ColoredBox(1.2*inch, 0.8*inch, HexColor("#dcc8b0"), "Warm Neutral", TEMPLATE_COLORS["text_dark"], 8)],
    ], colWidths=[1.4*inch, 1.4*inch, 1.4*inch, 1.4*inch])
    neutral_colors.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(neutral_colors)
    story.append(PageBreak())
    
    # Color Codes
    story.append(Paragraph("COLOR CODES", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Color Codes", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    
    color_specs = [
        (config.get("color_primary_name", "Primary"), config.get("color_primary_hex", "#000000"), 
         config.get("color_primary_rgb", "0, 0, 0"), config.get("color_primary_cmyk", "0, 0, 0, 100"), 
         config.get("color_primary_pantone", "N/A")),
        (config.get("color_accent_name", "Accent"), config.get("color_accent_hex", "#0066FF"), 
         config.get("color_accent_rgb", "0, 102, 255"), config.get("color_accent_cmyk", "100, 60, 0, 0"), 
         config.get("color_accent_pantone", "N/A")),
        (config.get("color_secondary_name", "Secondary"), config.get("color_secondary_hex", "#444444"), 
         config.get("color_secondary_rgb", "68, 68, 68"), config.get("color_secondary_cmyk", "0, 0, 0, 73"), 
         config.get("color_secondary_pantone", "N/A")),
    ]
    
    for name, hex_val, rgb, cmyk, pantone in color_specs:
        story.append(Paragraph(f"<b>{name}</b>", styles['TraitName']))
        story.append(Paragraph(f"Hex - {hex_val}<br/>RGB - {rgb}<br/>CMYK - {cmyk}<br/>Pantone - {pantone}", styles['BodyTextLight']))
        story.append(Spacer(1, 0.2*inch))
    
    story.append(PageBreak())


def create_typography_section(story, styles, config):
    """Create the Typography section."""
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Typography", styles['SectionHeader']))
    story.append(PageBreak())
    
    # Primary Font
    story.append(Paragraph("PRIMARY FONT", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(config.get("font_primary", "{{PRIMARY_FONT}}"), styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(config.get("font_primary_description", "{{PRIMARY_FONT_DESCRIPTION}}"), styles['BrandBodyText']))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph(f"Download the font: {config.get('font_primary_download', '{{PRIMARY_FONT_DOWNLOAD_URL}}')}", styles['BodyTextLight']))
    story.append(Spacer(1, 0.5*inch))
    
    # Font specimen
    story.append(Paragraph("The quick brown fox jumps over the lazy dog.", styles['FeatureHeadline']))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("ABCDEFGHIJKLMNOPQRSTUVWXYZ<br/>abcdefghijklmnopqrstuvwxyz<br/>0123456789 !@#$%^&*()", styles['BrandBodyText']))
    story.append(PageBreak())
    
    # System Alternative
    story.append(Paragraph("SYSTEM ALTERNATIVE", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(config.get("font_system", "{{SYSTEM_FONT}}"), styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(config.get("font_system_description", "{{SYSTEM_FONT_DESCRIPTION}}"), styles['BrandBodyText']))
    story.append(PageBreak())
    
    # Hierarchy
    story.append(Paragraph("HIERARCHY", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Hierarchy", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Typeface hierarchy communicates importance, guides a reader's eye, and clearly organizes and prioritizes content.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    hierarchy_data = [
        ["ELEMENT", "CASE", "LEADING", "TRACKING"],
        ["LABEL", "All caps", "140%", "0"],
        ["HEADING", "Sentence case", "120%", "0"],
        ["SUBHEADING", "Sentence case", "130%", "0"],
        ["PARAGRAPH", "Sentence case", "150%", "0"],
    ]
    
    hierarchy_table = Table(hierarchy_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    hierarchy_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, 0), TEMPLATE_COLORS["text_light"]),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, TEMPLATE_COLORS["light_gray"]),
    ]))
    story.append(hierarchy_table)
    story.append(PageBreak())
    
    # CTA Buttons
    story.append(Paragraph("CTA BUTTONS", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("CTA Buttons", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Creating a reliable, consistent customer experience is key to building trust. Using a consistent button style is important.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    # Button examples
    story.append(Paragraph("<b>PRIMARY</b>", styles['LabelText']))
    story.append(ColoredBox(2*inch, 0.4*inch, TEMPLATE_COLORS["accent"], "Get Started", white, 11))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>SECONDARY</b>", styles['LabelText']))
    story.append(ColoredBox(2*inch, 0.4*inch, TEMPLATE_COLORS["white"], "Get Started", TEMPLATE_COLORS["accent"], 11))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>TERTIARY</b>", styles['LabelText']))
    story.append(Paragraph("<u>Get Started →</u>", styles['BrandBodyText']))
    
    story.append(PageBreak())


def create_photography_section(story, styles, config):
    """Create the Photography section."""
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Photography", styles['SectionHeader']))
    story.append(PageBreak())
    
    # Overview
    story.append(Paragraph("OVERVIEW", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Overview", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(config.get("photo_style", f"{config.get('company_name', '{{COMPANY_NAME}}')}'s imagery reflects the tone of our company and captures positive interactions and relationships."), styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    photo_guidelines = [
        "Select photos that are rich, bright, and warm in tone.",
        "Images should not be overly saturated or edited with flares.",
        "Subjects should be authentic, modern, and candid.",
        "They should be diverse in gender, ethnicity, and age.",
        "Environmental photos should be inviting and modern.",
    ]
    
    for guideline in photo_guidelines:
        story.append(Paragraph(f"• {guideline}", styles['BrandBodyText']))
    
    story.append(Spacer(1, 0.5*inch))
    
    # Photo placeholder
    photo_placeholder = ColoredBox(5*inch, 3*inch, TEMPLATE_COLORS["light_gray"], "[ Sample Photography ]", TEMPLATE_COLORS["text_light"], 16)
    story.append(photo_placeholder)
    story.append(PageBreak())
    
    # Image Treatment
    story.append(Paragraph("IMAGE TREATMENT", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Overlays & Masking", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Our image mask and cutout style allows us to focus on customers and the impact we have on their business.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    # Overlay examples
    overlay_data = [
        [ColoredBox(1.5*inch, 1*inch, TEMPLATE_COLORS["accent"], "Accent Overlay", white, 9),
         ColoredBox(1.5*inch, 1*inch, TEMPLATE_COLORS["white"], "Light Overlay", TEMPLATE_COLORS["text_light"], 9),
         ColoredBox(1.5*inch, 1*inch, TEMPLATE_COLORS["primary"], "Dark Overlay", white, 9)],
    ]
    
    overlay_table = Table(overlay_data, colWidths=[2*inch, 2*inch, 2*inch])
    overlay_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(overlay_table)
    story.append(PageBreak())


def create_patterns_section(story, styles, config):
    """Create the Patterns section."""
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Patterns", styles['SectionHeader']))
    story.append(PageBreak())
    
    # Overview
    story.append(Paragraph("OVERVIEW", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Overview", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Using the brand equity in our logo shapes, we can scale them up to create interesting compositions or scale them down to create patterns. This allows for flexibility in diversifying layouts.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    # Pattern placeholder
    pattern_placeholder = ColoredBox(5*inch, 2*inch, TEMPLATE_COLORS["light_gray"], "[ Pattern Examples ]", TEMPLATE_COLORS["text_light"], 16)
    story.append(pattern_placeholder)
    story.append(PageBreak())
    
    # Construction
    story.append(Paragraph("CONSTRUCTION", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Construction", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Our branded pattern style can be used to accent compositions. Make sure any pattern remains subtle—it should never overtake the user's eye.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    construction_steps = [
        "Create an artboard with appropriate dimensions.",
        "Choose brand shapes from the asset library.",
        "Apply 'brick by row' tile type with appropriate offset.",
        "Adjust H and V spacing to match brand standards.",
        "Export as PNG for use in compositions.",
    ]
    
    for i, step in enumerate(construction_steps, 1):
        story.append(Paragraph(f"{i}. {step}", styles['BrandBodyText']))
    
    story.append(PageBreak())
    
    # Sample usage
    story.append(Paragraph("SAMPLE", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Sample", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<b>Tips</b>", styles['TraitName']))
    story.append(Paragraph("• Use patterns to accent the composition", styles['BrandBodyText']))
    story.append(Paragraph("• Use shapes as background elements to frame copy", styles['BrandBodyText']))
    story.append(Paragraph("• Use shapes to create interesting image crops", styles['BrandBodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<b>Do Not</b>", styles['TraitName']))
    story.append(Paragraph("• Use bold patterns that distract from messaging", styles['BrandBodyText']))
    story.append(Paragraph("• Overwhelm compositions with large background shapes", styles['BrandBodyText']))
    story.append(Paragraph("• Overuse image crops in any single composition", styles['BrandBodyText']))
    
    story.append(PageBreak())


def create_work_samples_section(story, styles, config):
    """Create the Work Samples section."""
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Application", styles['SectionHeader']))
    story.append(Paragraph("and Work", styles['SectionHeader']))
    story.append(Paragraph("Samples", styles['SectionHeader']))
    story.append(PageBreak())
    
    # Grid
    story.append(Paragraph("GRID", styles['PageLabel']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Grid", styles['SubsectionHeader']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"{config.get('company_name', '{{COMPANY_NAME}}')} is a sleek and streamlined brand. All assets must adhere to our unified look.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("Use a square grid and keep compositions clean and free of clutter. Grids may vary by asset type but should set the foundation for every designed asset.", styles['BrandBodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    grid_placeholder = ColoredBox(5*inch, 3*inch, TEMPLATE_COLORS["light_gray"], "[ Grid System Example ]", TEMPLATE_COLORS["text_light"], 16)
    story.append(grid_placeholder)
    story.append(PageBreak())
    
    # Sample applications
    applications = [
        ("WHITE PAPER", "Whitepaper", "Document layout example for long-form content."),
        ("SOCIAL MEDIA", "LinkedIn", "Social media post template for professional platforms."),
        ("COLLATERAL", "Business Cards", "Print collateral following brand standards."),
    ]
    
    for label, title, desc in applications:
        story.append(Paragraph(label, styles['PageLabel']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(title, styles['SubsectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(desc, styles['BodyTextLight']))
        story.append(Spacer(1, 0.3*inch))
        app_placeholder = ColoredBox(5*inch, 2.5*inch, TEMPLATE_COLORS["light_gray"], f"[ {title} Sample ]", TEMPLATE_COLORS["text_light"], 14)
        story.append(app_placeholder)
        story.append(PageBreak())


def generate_brand_guidelines(output_path, config=None):
    """Generate the complete brand guidelines PDF."""
    if config is None:
        config = BRAND_CONFIG
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = create_styles()
    story = []
    
    # Build document sections
    create_cover_page(story, styles, config)
    create_toc(story, styles)
    create_brand_strategy_section(story, styles, config)
    create_messaging_section(story, styles, config)
    create_verbal_expression_section(story, styles, config)
    create_logo_section(story, styles, config)
    create_color_section(story, styles, config)
    create_typography_section(story, styles, config)
    create_photography_section(story, styles, config)
    create_patterns_section(story, styles, config)
    create_work_samples_section(story, styles, config)
    
    # Build the PDF with page numbers
    doc.build(story, canvasmaker=PageNumberCanvas)
    print(f"Brand guidelines generated: {output_path}")
    return output_path


if __name__ == "__main__":
    output_file = "/home/claude/Brand_Guidelines_Template.pdf"
    generate_brand_guidelines(output_file)
