"""Spell management tool definitions."""

from dnd_manager.ai.tools.schema import ToolCategory, ToolDefinition, ToolRiskLevel


ADD_SPELL = ToolDefinition(
    name="add_spell",
    description="Add a spell to the character's known, prepared, or cantrip list.",
    input_schema={
        "type": "object",
        "properties": {
            "spell_name": {
                "type": "string",
                "description": "Name of the spell to add",
            },
            "list_type": {
                "type": "string",
                "description": "Which list to add to",
                "enum": ["cantrips", "known", "prepared"],
            },
        },
        "required": ["spell_name"],
    },
    category=ToolCategory.SPELLS,
    risk_level=ToolRiskLevel.SAFE,
)

REMOVE_SPELL = ToolDefinition(
    name="remove_spell",
    description="Remove a spell from the character's spell list.",
    input_schema={
        "type": "object",
        "properties": {
            "spell_name": {
                "type": "string",
                "description": "Name of the spell to remove",
            },
            "list_type": {
                "type": "string",
                "description": "Which list to remove from",
                "enum": ["cantrips", "known", "prepared"],
            },
        },
        "required": ["spell_name"],
    },
    category=ToolCategory.SPELLS,
    risk_level=ToolRiskLevel.MODERATE,
)

USE_SPELL_SLOT = ToolDefinition(
    name="use_spell_slot",
    description="Use a spell slot of a specific level.",
    input_schema={
        "type": "object",
        "properties": {
            "level": {
                "type": "integer",
                "description": "Spell slot level to use",
                "minimum": 1,
                "maximum": 9,
            },
        },
        "required": ["level"],
    },
    category=ToolCategory.SPELLS,
    risk_level=ToolRiskLevel.SAFE,
)

RESTORE_SPELL_SLOT = ToolDefinition(
    name="restore_spell_slot",
    description="Restore a used spell slot (e.g., from Arcane Recovery or similar features).",
    input_schema={
        "type": "object",
        "properties": {
            "level": {
                "type": "integer",
                "description": "Spell slot level to restore",
                "minimum": 1,
                "maximum": 9,
            },
            "count": {
                "type": "integer",
                "description": "Number of slots to restore",
                "minimum": 1,
            },
        },
        "required": ["level"],
    },
    category=ToolCategory.SPELLS,
    risk_level=ToolRiskLevel.SAFE,
)
