"""
Brand data models for the extraction pipeline.
These Pydantic models define the structure of extracted brand data.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class ColorSpec(BaseModel):
    """Specification for a single color with multiple format representations."""
    name: str
    hex: str
    rgb: Optional[str] = None
    cmyk: Optional[str] = None
    pantone: Optional[str] = None

    @field_validator('hex')
    @classmethod
    def validate_hex(cls, v: str) -> str:
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Invalid hex color format. Expected #RRGGBB')
        return v.upper()


class ColorPalette(BaseModel):
    """Complete color palette with primary, secondary, accent, and neutrals."""
    primary: ColorSpec
    secondary: Optional[ColorSpec] = None
    accent: Optional[ColorSpec] = None
    neutrals: list[ColorSpec] = Field(default_factory=list)


class FontSpec(BaseModel):
    """Specification for a font/typeface."""
    name: str
    family: str
    weight: Optional[str] = None
    style: Optional[str] = None
    source: Optional[str] = None  # 'google', 'adobe', 'custom'
    download_url: Optional[str] = None


class Typography(BaseModel):
    """Typography specification with primary, secondary, and fallback fonts."""
    primary: FontSpec
    secondary: Optional[FontSpec] = None
    system_fallback: str = "Arial, Helvetica, sans-serif"


class BrandPillar(BaseModel):
    """A brand pillar with title and description."""
    title: str
    description: str


class PersonalityTrait(BaseModel):
    """A brand personality trait."""
    name: str
    description: str


class VoiceGuideline(BaseModel):
    """Voice guideline with IS/IS NOT pairs and examples."""
    is_trait: str
    is_example: str
    is_not_trait: str
    is_not_example: str


class LogoAsset(BaseModel):
    """Logo asset with URL and optional binary data."""
    primary_url: Optional[str] = None
    primary_data: Optional[bytes] = None
    variations: list[str] = Field(default_factory=list)
    format: str = "png"

    class Config:
        # Allow bytes field
        arbitrary_types_allowed = True


class ExtractedBrand(BaseModel):
    """Complete extracted brand data structure."""

    # Identity
    company_name: str
    tagline: Optional[str] = None
    domain: str

    # Visual Identity
    colors: ColorPalette
    typography: Typography
    logo: Optional[LogoAsset] = None

    # Brand Strategy (AI-generated)
    positioning_headline: Optional[str] = None
    positioning_description: Optional[str] = None
    mission: Optional[str] = None
    mission_description: Optional[str] = None
    vision: Optional[str] = None
    vision_description: Optional[str] = None

    # Brand Personality
    pillars: list[BrandPillar] = Field(default_factory=list, max_length=3)
    traits: list[PersonalityTrait] = Field(default_factory=list, max_length=4)
    promise: Optional[str] = None
    promise_description: Optional[str] = None

    # Voice & Tone
    voice_guidelines: list[VoiceGuideline] = Field(default_factory=list, max_length=3)
    boilerplate: Optional[str] = None

    # Photography
    photo_style: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
