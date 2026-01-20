"""Query tool definitions (read-only)."""

from dnd_manager.ai.tools.schema import ToolCategory, ToolDefinition, ToolRiskLevel


GET_CHARACTER_SUMMARY = ToolDefinition(
    name="get_character_summary",
    description="Get a comprehensive summary of the character including class, level, HP, AC, and key stats. Use this to understand the character's current state before making changes.",
    input_schema={
        "type": "object",
        "properties": {
            "include_equipment": {
                "type": "boolean",
                "description": "Include equipped items in summary",
            },
            "include_spells": {
                "type": "boolean",
                "description": "Include spell information in summary",
            },
        },
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
)

GET_ABILITY_SCORES = ToolDefinition(
    name="get_ability_scores",
    description="Get all six ability scores with their modifiers, base values, and any bonuses.",
    input_schema={
        "type": "object",
        "properties": {},
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
)

GET_SPELL_SLOTS = ToolDefinition(
    name="get_spell_slots",
    description="Get current spell slot availability for each level, showing total and remaining slots.",
    input_schema={
        "type": "object",
        "properties": {},
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
)

GET_INVENTORY = ToolDefinition(
    name="get_inventory",
    description="Get the character's inventory including all items, currency, and equipment status.",
    input_schema={
        "type": "object",
        "properties": {
            "filter_equipped": {
                "type": "boolean",
                "description": "Only show equipped items",
            },
            "filter_attuned": {
                "type": "boolean",
                "description": "Only show attuned items",
            },
        },
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
)

CHECK_MULTICLASS_REQUIREMENTS = ToolDefinition(
    name="check_multiclass_requirements",
    description="Check if the character meets the ability score requirements to multiclass into a specific class.",
    input_schema={
        "type": "object",
        "properties": {
            "target_class": {
                "type": "string",
                "description": "The class to check multiclass requirements for",
                "enum": [
                    "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
                    "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
                    "Warlock", "Wizard",
                ],
            },
        },
        "required": ["target_class"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
)
