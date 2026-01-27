"""AI prompts for character sheet parsing."""

# Base prompt used for all character sheet types
BASE_PARSING_PROMPT = """You are an expert at parsing D&D 5th Edition character sheets. You will be shown images of a character sheet.

Your task is to extract ALL available character information from the images and return it as structured JSON.

IMPORTANT GUIDELINES:
1. Extract everything you can see clearly
2. If a field is unclear, unreadable, or not present, set it to null
3. Use exact spell names when possible (e.g., "Cure Wounds" not "cure wounds")
4. Use standard D&D ability names (Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma)
5. For skills, use standard names (e.g., "Perception", "Stealth", "Athletics")
6. For proficient skills/saves, look for filled circles, checkmarks, or highlighted entries
7. Include a "confidence" object rating your certainty for each major section (0.0 = uncertain, 1.0 = certain)

Return ONLY valid JSON in this exact structure:
```json
{
  "name": "Character Name",
  "player_name": "Player Name or null",
  "class_name": "Primary Class",
  "subclass": "Subclass or null",
  "level": 5,
  "species": "Race/Species",
  "subspecies": "Subrace or null",
  "background": "Background",
  "alignment": "Lawful Good",

  "strength": 16,
  "dexterity": 14,
  "constitution": 13,
  "intelligence": 10,
  "wisdom": 12,
  "charisma": 8,

  "armor_class": 18,
  "hit_points_max": 45,
  "hit_points_current": 45,
  "speed": 30,
  "initiative_bonus": 2,

  "skill_proficiencies": ["Perception", "Athletics", "Intimidation"],
  "skill_expertise": [],
  "saving_throw_proficiencies": ["Strength", "Constitution"],
  "armor_proficiencies": ["Light Armor", "Medium Armor", "Heavy Armor", "Shields"],
  "weapon_proficiencies": ["Simple Weapons", "Martial Weapons"],
  "tool_proficiencies": ["Smith's Tools"],
  "languages": ["Common", "Dwarvish"],

  "spellcasting_ability": "Intelligence",
  "spell_save_dc": 15,
  "spell_attack_bonus": 7,
  "cantrips": ["Fire Bolt", "Prestidigitation"],
  "spells_known": ["Magic Missile", "Shield", "Fireball"],
  "spells_prepared": ["Magic Missile", "Fireball"],
  "spell_slots": {"1": 4, "2": 3, "3": 2},

  "features": [
    {"name": "Fighting Style: Defense", "source": "class", "description": "+1 AC when wearing armor"},
    {"name": "Second Wind", "source": "class", "description": "Bonus action heal 1d10+level"}
  ],

  "equipment": [
    {"name": "Longsword", "quantity": 1, "equipped": true, "attuned": false},
    {"name": "Shield", "quantity": 1, "equipped": true, "attuned": false},
    {"name": "Chain Mail", "quantity": 1, "equipped": true, "attuned": false}
  ],
  "currency": {"pp": 0, "gp": 50, "ep": 0, "sp": 20, "cp": 15},

  "personality_traits": "I judge people by their actions, not their words.",
  "ideals": "Honor. My word is my bond.",
  "bonds": "I protect those who cannot protect themselves.",
  "flaws": "I have trouble trusting allies.",
  "backstory": "Brief backstory if visible...",

  "multiclass": [],

  "confidence": {
    "identity": 0.95,
    "abilities": 0.90,
    "combat": 0.85,
    "proficiencies": 0.80,
    "spells": 0.75,
    "equipment": 0.70,
    "personality": 0.60
  }
}
```

If a section is not applicable (e.g., spellcasting for a non-caster), use empty values (null, [], {}).
If you see multiclass levels, include them in the "multiclass" array with the same structure.
"""

# D&D Beyond specific prompt additions
DNDBEYOND_PROMPT_ADDITION = """
SPECIFIC TO D&D BEYOND CHARACTER SHEETS:
- D&D Beyond uses a modern digital layout with distinct card-like sections
- Ability scores are shown in hexagonal boxes with modifier below
- Proficiency is indicated by filled circles (●) vs unfilled (○)
- Expertise is indicated by double-filled or highlighted entries
- The character name and class/level appear prominently at the top
- Spells are typically shown in a list format with spell level headers
- Equipment may be spread across multiple pages
- Look for "Proficiency Bonus" displayed prominently
- AC is typically shown in a shield icon
- HP current/max are shown together (e.g., "45/45")
"""

# Roll20 specific prompt additions
ROLL20_PROMPT_ADDITION = """
SPECIFIC TO ROLL20 CHARACTER SHEETS:
- Roll20 uses a form-based layout with labeled input fields
- Ability scores appear in a grid with score and modifier
- Skills are listed with checkboxes for proficiency
- The sheet may have a more compact, tabular appearance
- Spell slots may be shown as checkboxes or circular pips
- Equipment is often in a free-form text area
- Look for "Prof Bonus" or "PB" abbreviation
- Initiative may be auto-calculated or shown separately
"""

# Generic/unknown sheet prompt additions
GENERIC_PROMPT_ADDITION = """
PARSING UNKNOWN/CUSTOM CHARACTER SHEET:
- This appears to be a custom or unfamiliar character sheet format
- Look for common D&D terminology and abbreviations
- Ability scores are usually abbreviated: STR, DEX, CON, INT, WIS, CHA
- AC = Armor Class, HP = Hit Points, Init = Initiative
- Skills are typically listed alphabetically
- Be flexible with layout - data may be arranged differently
- If handwritten, extract what you can clearly read
- Mark uncertain values with lower confidence scores
"""


def get_parsing_prompt(source_type: str) -> str:
    """Get the full parsing prompt for a given source type.

    Args:
        source_type: One of "dndbeyond", "roll20", "generic", or "auto"

    Returns:
        Complete system prompt for AI parsing
    """
    prompt = BASE_PARSING_PROMPT

    if source_type == "dndbeyond":
        prompt += "\n" + DNDBEYOND_PROMPT_ADDITION
    elif source_type == "roll20":
        prompt += "\n" + ROLL20_PROMPT_ADDITION
    elif source_type in ("generic", "auto"):
        prompt += "\n" + GENERIC_PROMPT_ADDITION

    return prompt


def get_targeted_extraction_prompt(fields: list[str]) -> str:
    """Get a prompt for extracting specific missing fields.

    Args:
        fields: List of field names to extract

    Returns:
        Prompt for targeted extraction
    """
    field_list = ", ".join(fields)

    return f"""Look at the character sheet images and extract ONLY the following specific information:
{field_list}

Return a JSON object with just these fields. Use null for any field you cannot find.

Example response format:
```json
{{
  "field_name": "extracted value",
  "another_field": 15
}}
```
"""


def get_validation_prompt() -> str:
    """Get a prompt for validating parsed data consistency."""
    return """Review the following parsed character data for consistency and D&D 5e rule compliance:

1. Check if ability modifiers match the ability scores
2. Verify skill modifiers are reasonable given proficiencies
3. Check if spell slots match the class/level
4. Verify HP is reasonable for class/level/CON
5. Check if proficiency bonus matches level

Return JSON with:
- "valid": true/false
- "issues": ["list of any issues found"]
- "suggestions": ["list of suggested corrections"]
"""
