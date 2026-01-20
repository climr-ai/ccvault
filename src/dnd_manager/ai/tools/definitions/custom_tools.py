"""Custom stat and personality tool definitions."""

from dnd_manager.ai.tools.schema import ToolCategory, ToolDefinition, ToolRiskLevel


MODIFY_CUSTOM_STAT = ToolDefinition(
    name="modify_custom_stat",
    description="Modify a custom campaign stat like Luck, Renown, Piety, Sanity, etc.",
    input_schema={
        "type": "object",
        "properties": {
            "stat_name": {
                "type": "string",
                "description": "Name of the custom stat",
            },
            "amount": {
                "type": "integer",
                "description": "Amount to add (positive) or subtract (negative)",
            },
            "set_value": {
                "type": "integer",
                "description": "Set to a specific value instead of adjusting (overrides amount)",
            },
        },
        "required": ["stat_name"],
    },
    category=ToolCategory.CUSTOM,
    risk_level=ToolRiskLevel.SAFE,
)

ADD_NOTE = ToolDefinition(
    name="add_note",
    description="Add a note to the character's notes section.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Note title",
            },
            "content": {
                "type": "string",
                "description": "Note content",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags for the note",
            },
        },
        "required": ["title", "content"],
    },
    category=ToolCategory.CUSTOM,
    risk_level=ToolRiskLevel.SAFE,
)

SET_PERSONALITY_TRAIT = ToolDefinition(
    name="set_personality_trait",
    description="Set or add a personality trait, ideal, bond, or flaw.",
    input_schema={
        "type": "object",
        "properties": {
            "trait_type": {
                "type": "string",
                "description": "Type of trait",
                "enum": ["trait", "ideal", "bond", "flaw"],
            },
            "value": {
                "type": "string",
                "description": "The trait text",
            },
            "action": {
                "type": "string",
                "description": "Whether to add to existing or replace all",
                "enum": ["add", "replace"],
            },
        },
        "required": ["trait_type", "value"],
    },
    category=ToolCategory.CUSTOM,
    risk_level=ToolRiskLevel.SAFE,
)
