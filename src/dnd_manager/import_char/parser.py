"""AI-powered character sheet parsing using vision models."""

import json
import logging
import re
from typing import Any, Optional

from dnd_manager.import_char.prompts import (
    get_parsing_prompt,
    get_targeted_extraction_prompt,
)
from dnd_manager.import_char.session import ParsedCharacterData

logger = logging.getLogger(__name__)


class ParsingError(Exception):
    """Error during character sheet parsing."""

    pass


class CharacterSheetParser:
    """Parses character sheet images using AI vision models.

    Supports multiple AI providers with vision capabilities:
    - Gemini (google-genai)
    - Claude (anthropic)
    - GPT-4V (openai)
    """

    def __init__(self, provider_name: Optional[str] = None) -> None:
        """Initialize parser.

        Args:
            provider_name: AI provider to use. If None, uses default provider.
        """
        self.provider_name = provider_name
        self._provider = None

    async def _get_provider(self):
        """Get AI provider with vision support."""
        if self._provider is not None:
            return self._provider

        from dnd_manager.ai.providers import get_provider, get_default_provider

        if self.provider_name:
            provider = get_provider(self.provider_name)
        else:
            provider = get_default_provider()

        if provider is None:
            raise ParsingError(
                "No AI provider available. Configure an API key for Gemini, Claude, or GPT-4."
            )

        if not provider.supports_vision():
            raise ParsingError(
                f"Provider '{provider.name}' does not support vision. "
                "Use Gemini, Claude, or GPT-4V for character sheet parsing."
            )

        self._provider = provider
        return provider

    async def parse_full_sheet(
        self,
        images: list[bytes],
        source_type: str = "auto",
    ) -> ParsedCharacterData:
        """Parse a complete character sheet from images.

        Args:
            images: List of PNG image data (one per page)
            source_type: Type of sheet ("dndbeyond", "roll20", "generic", "auto")

        Returns:
            ParsedCharacterData with all extracted information
        """
        if not images:
            raise ParsingError("No images provided for parsing")

        provider = await self._get_provider()
        system_prompt = get_parsing_prompt(source_type)

        logger.info(f"Parsing {len(images)} page(s) with {provider.name}")

        try:
            response = await provider.chat_with_images(
                messages=[],
                images=images,
                system_prompt=system_prompt,
                max_tokens=4096,
            )

            # Extract JSON from response
            parsed_json = self._extract_json(response.content)
            if parsed_json is None:
                logger.warning("Failed to extract JSON, using raw response")
                return ParsedCharacterData(
                    raw_response=response.content,
                    confidence={"overall": 0.2},
                )

            # Convert to ParsedCharacterData
            data = self._json_to_parsed_data(parsed_json)
            data.raw_response = response.content

            return data

        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            raise ParsingError(f"Failed to parse character sheet: {e}") from e

    async def extract_missing_fields(
        self,
        images: list[bytes],
        fields: list[str],
    ) -> dict[str, Any]:
        """Extract specific fields that were missing or low-confidence.

        Args:
            images: List of PNG image data
            fields: List of field names to extract

        Returns:
            Dictionary of field names to extracted values
        """
        if not images or not fields:
            return {}

        provider = await self._get_provider()
        prompt = get_targeted_extraction_prompt(fields)

        try:
            response = await provider.chat_with_images(
                messages=[],
                images=images,
                system_prompt=prompt,
                max_tokens=1024,
            )

            parsed_json = self._extract_json(response.content)
            return parsed_json or {}

        except Exception as e:
            logger.error(f"Targeted extraction failed: {e}")
            return {}

    def _extract_json(self, text: str) -> Optional[dict]:
        """Extract JSON from AI response text.

        Handles responses that may have JSON in code blocks or mixed with text.
        """
        # Try to find JSON in code blocks first
        json_block_pattern = r"```(?:json)?\s*\n?([\s\S]*?)\n?```"
        matches = re.findall(json_block_pattern, text)

        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        # Try to find raw JSON object
        json_object_pattern = r"\{[\s\S]*\}"
        matches = re.findall(json_object_pattern, text)

        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        # Try the entire text as JSON
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return None

    def _json_to_parsed_data(self, data: dict) -> ParsedCharacterData:
        """Convert parsed JSON to ParsedCharacterData object."""
        # Normalize field names (handle variations)
        normalized = {}

        # Direct mappings
        direct_fields = [
            "name", "player_name", "class_name", "subclass", "level",
            "species", "subspecies", "background", "alignment",
            "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
            "armor_class", "hit_points_max", "hit_points_current", "speed", "initiative_bonus",
            "skill_proficiencies", "skill_expertise", "saving_throw_proficiencies",
            "armor_proficiencies", "weapon_proficiencies", "tool_proficiencies", "languages",
            "spellcasting_ability", "spell_save_dc", "spell_attack_bonus",
            "cantrips", "spells_known", "spells_prepared", "spell_slots",
            "features", "equipment", "currency",
            "personality_traits", "ideals", "bonds", "flaws", "backstory",
            "multiclass", "confidence",
        ]

        for field in direct_fields:
            if field in data:
                normalized[field] = data[field]

        # Handle alternate field names
        name_mappings = {
            "race": "species",
            "subrace": "subspecies",
            "class": "class_name",
            "hp_max": "hit_points_max",
            "hp_current": "hit_points_current",
            "max_hp": "hit_points_max",
            "current_hp": "hit_points_current",
            "ac": "armor_class",
            "init": "initiative_bonus",
            "initiative": "initiative_bonus",
            "proficient_skills": "skill_proficiencies",
            "saving_throws": "saving_throw_proficiencies",
            "save_proficiencies": "saving_throw_proficiencies",
            "spells": "spells_known",
            "known_spells": "spells_known",
            "prepared": "spells_prepared",
            "traits": "personality_traits",
            "gold": "currency",  # Will need special handling
            "items": "equipment",
            "inventory": "equipment",
        }

        for alt_name, canonical_name in name_mappings.items():
            if alt_name in data and canonical_name not in normalized:
                normalized[canonical_name] = data[alt_name]

        # Handle numeric conversions
        int_fields = [
            "level", "strength", "dexterity", "constitution", "intelligence",
            "wisdom", "charisma", "armor_class", "hit_points_max",
            "hit_points_current", "speed", "initiative_bonus",
            "spell_save_dc", "spell_attack_bonus",
        ]

        for field in int_fields:
            if field in normalized and normalized[field] is not None:
                try:
                    normalized[field] = int(normalized[field])
                except (ValueError, TypeError):
                    normalized[field] = None

        # Handle spell slots - ensure keys are integers
        if "spell_slots" in normalized and normalized["spell_slots"]:
            slots = {}
            for level, count in normalized["spell_slots"].items():
                try:
                    slots[int(level)] = int(count)
                except (ValueError, TypeError):
                    pass
            normalized["spell_slots"] = slots

        # Handle currency - might be just a gold value
        if "currency" in normalized:
            curr = normalized["currency"]
            if isinstance(curr, (int, float)):
                normalized["currency"] = {"gp": int(curr)}
            elif isinstance(curr, dict):
                # Normalize currency keys
                currency = {}
                for key, val in curr.items():
                    key_lower = key.lower()
                    if key_lower in ("pp", "platinum"):
                        currency["pp"] = int(val or 0)
                    elif key_lower in ("gp", "gold"):
                        currency["gp"] = int(val or 0)
                    elif key_lower in ("ep", "electrum"):
                        currency["ep"] = int(val or 0)
                    elif key_lower in ("sp", "silver"):
                        currency["sp"] = int(val or 0)
                    elif key_lower in ("cp", "copper"):
                        currency["cp"] = int(val or 0)
                normalized["currency"] = currency

        # Ensure list fields are lists
        list_fields = [
            "skill_proficiencies", "skill_expertise", "saving_throw_proficiencies",
            "armor_proficiencies", "weapon_proficiencies", "tool_proficiencies",
            "languages", "cantrips", "spells_known", "spells_prepared",
            "features", "equipment", "multiclass",
        ]

        for field in list_fields:
            if field in normalized:
                if normalized[field] is None:
                    normalized[field] = []
                elif isinstance(normalized[field], str):
                    # Split comma-separated string
                    normalized[field] = [s.strip() for s in normalized[field].split(",") if s.strip()]

        # Ensure confidence dict exists
        if "confidence" not in normalized or not isinstance(normalized.get("confidence"), dict):
            normalized["confidence"] = {}

        return ParsedCharacterData.from_dict(normalized)


async def parse_character_sheet(
    images: list[bytes],
    source_type: str = "auto",
    provider_name: Optional[str] = None,
) -> ParsedCharacterData:
    """Convenience function to parse a character sheet.

    Args:
        images: List of PNG image data
        source_type: Type of character sheet
        provider_name: AI provider to use

    Returns:
        ParsedCharacterData with extracted information
    """
    parser = CharacterSheetParser(provider_name=provider_name)
    return await parser.parse_full_sheet(images, source_type)
