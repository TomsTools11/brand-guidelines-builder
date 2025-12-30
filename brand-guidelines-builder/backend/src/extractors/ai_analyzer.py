"""
AI-powered brand content generation using Claude API.
"""

import json
import anthropic

from ..models.brand_data import (
    ExtractedBrand,
    BrandPillar,
    PersonalityTrait,
    VoiceGuideline,
)


class AIAnalyzer:
    """Use Claude to generate brand content from scraped text."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def analyze(
        self,
        scraped_text: str,
        company_name: str,
        existing_data: ExtractedBrand
    ) -> ExtractedBrand:
        """
        Use Claude to generate brand content from scraped text.

        Args:
            scraped_text: Combined text content from scraped pages
            company_name: Name of the company
            existing_data: Existing ExtractedBrand with visual data

        Returns:
            Updated ExtractedBrand with AI-generated content
        """
        prompt = self._build_prompt(scraped_text, company_name)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse structured response
        content = self._parse_response(response.content[0].text)

        # Merge with existing extracted data
        return self._merge_data(existing_data, content)

    def _build_prompt(self, text: str, company_name: str) -> str:
        """Build the prompt for Claude."""
        # Limit text to avoid token limits
        truncated_text = text[:15000] if len(text) > 15000 else text

        return f'''Analyze this website content for {company_name} and generate brand guidelines content.

WEBSITE CONTENT:
{truncated_text}

Based on the content above, generate brand guidelines in JSON format. Be specific to this company based on what you learned from their website. Do not be generic.

Generate the following JSON structure:
{{
    "tagline": "Short memorable tagline (max 10 words)",
    "positioning_headline": "Bold positioning statement that captures what makes this company unique",
    "positioning_description": "2-3 sentences expanding on the positioning",
    "mission": "Mission statement (1-2 sentences)",
    "mission_description": "Paragraph explaining the mission in more detail",
    "vision": "Vision statement (1-2 sentences)",
    "vision_description": "Paragraph explaining the vision in more detail",
    "pillars": [
        {{"title": "First Pillar Name", "description": "1-2 sentence description of this pillar"}},
        {{"title": "Second Pillar Name", "description": "1-2 sentence description of this pillar"}},
        {{"title": "Third Pillar Name", "description": "1-2 sentence description of this pillar"}}
    ],
    "traits": [
        {{"name": "First Trait", "description": "1-2 sentence description of this personality trait"}},
        {{"name": "Second Trait", "description": "1-2 sentence description of this personality trait"}},
        {{"name": "Third Trait", "description": "1-2 sentence description of this personality trait"}},
        {{"name": "Fourth Trait", "description": "1-2 sentence description of this personality trait"}}
    ],
    "promise": "Brand promise statement",
    "promise_description": "Paragraph explaining what this promise means to customers",
    "voice_guidelines": [
        {{
            "is_trait": "Voice characteristic (e.g., Confident)",
            "is_example": "Example copy demonstrating this characteristic",
            "is_not_trait": "Opposite to avoid (e.g., Arrogant)",
            "is_not_example": "Example of what to avoid"
        }},
        {{
            "is_trait": "Another voice characteristic",
            "is_example": "Example copy",
            "is_not_trait": "Opposite to avoid",
            "is_not_example": "Example of what to avoid"
        }},
        {{
            "is_trait": "Third voice characteristic",
            "is_example": "Example copy",
            "is_not_trait": "Opposite to avoid",
            "is_not_example": "Example of what to avoid"
        }}
    ],
    "boilerplate": "Company boilerplate paragraph for press releases (2-3 sentences)",
    "photo_style": "Description of photography style that would fit this brand (2-3 sentences)"
}}

Return ONLY valid JSON, no additional text or explanation.'''

    def _parse_response(self, text: str) -> dict:
        """Parse JSON from Claude response."""
        # Find JSON in response (handle markdown code blocks)
        text = text.strip()

        # Remove markdown code block if present
        if text.startswith('```'):
            # Find the end of the code block
            lines = text.split('\n')
            start_idx = 1 if lines[0].startswith('```') else 0
            end_idx = len(lines)
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '```':
                    end_idx = i
                    break
            text = '\n'.join(lines[start_idx:end_idx])

        # Find JSON object
        start = text.find('{')
        end = text.rfind('}') + 1

        if start >= 0 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)

        raise ValueError("Could not parse JSON from AI response")

    def _merge_data(self, existing: ExtractedBrand, ai_content: dict) -> ExtractedBrand:
        """Merge AI-generated content with existing extracted data."""
        # Update text fields
        existing.tagline = ai_content.get('tagline')
        existing.positioning_headline = ai_content.get('positioning_headline')
        existing.positioning_description = ai_content.get('positioning_description')
        existing.mission = ai_content.get('mission')
        existing.mission_description = ai_content.get('mission_description')
        existing.vision = ai_content.get('vision')
        existing.vision_description = ai_content.get('vision_description')
        existing.promise = ai_content.get('promise')
        existing.promise_description = ai_content.get('promise_description')
        existing.boilerplate = ai_content.get('boilerplate')
        existing.photo_style = ai_content.get('photo_style')

        # Parse structured content
        if 'pillars' in ai_content and ai_content['pillars']:
            existing.pillars = [
                BrandPillar(**p) for p in ai_content['pillars'][:3]
            ]

        if 'traits' in ai_content and ai_content['traits']:
            existing.traits = [
                PersonalityTrait(**t) for t in ai_content['traits'][:4]
            ]

        if 'voice_guidelines' in ai_content and ai_content['voice_guidelines']:
            existing.voice_guidelines = [
                VoiceGuideline(**v) for v in ai_content['voice_guidelines'][:3]
            ]

        return existing
