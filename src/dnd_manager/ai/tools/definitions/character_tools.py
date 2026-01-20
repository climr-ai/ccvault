"""Character modification tool definitions."""

from dnd_manager.ai.tools.schema import ToolCategory, ToolDefinition, ToolRiskLevel


SET_ABILITY_SCORE = ToolDefinition(
    name="set_ability_score",
    description="Set the base value of an ability score. Use for character creation or when changing base stats.",
    input_schema={
        "type": "object",
        "properties": {
            "ability": {
                "type": "string",
                "description": "The ability to modify",
                "enum": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"],
            },
            "value": {
                "type": "integer",
                "description": "The new base value (typically 3-20, or up to 30 with items)",
                "minimum": 1,
                "maximum": 30,
            },
        },
        "required": ["ability", "value"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.MODERATE,
)

ADD_ABILITY_BONUS = ToolDefinition(
    name="add_ability_bonus",
    description="Add a tracked bonus to an ability score from a temporary effect, magic item, or other source.",
    input_schema={
        "type": "object",
        "properties": {
            "ability": {
                "type": "string",
                "description": "The ability to modify",
                "enum": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"],
            },
            "bonus": {
                "type": "integer",
                "description": "The bonus to add (can be negative for penalties)",
            },
            "source": {
                "type": "string",
                "description": "Source of the bonus (e.g., 'Belt of Giant Strength', 'Enhance Ability')",
            },
            "is_override": {
                "type": "boolean",
                "description": "If true, sets the score to override_value instead of adding a bonus",
            },
            "override_value": {
                "type": "integer",
                "description": "Value to set if is_override is true",
                "minimum": 1,
                "maximum": 30,
            },
        },
        "required": ["ability", "bonus", "source"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.MODERATE,
)

LEVEL_UP = ToolDefinition(
    name="level_up",
    description="Increase the character's level by 1. For multiclass characters, specify which class to level. Updates HP, spell slots, and hit dice automatically.",
    input_schema={
        "type": "object",
        "properties": {
            "class_name": {
                "type": "string",
                "description": "Class to gain a level in. If not specified, uses primary class. Specify for multiclassing.",
                "enum": [
                    "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
                    "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
                    "Warlock", "Wizard",
                ],
            },
            "hp_method": {
                "type": "string",
                "description": "How to determine HP gained",
                "enum": ["average", "max"],
            },
        },
        "required": [],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.DESTRUCTIVE,
)

ADD_FEATURE = ToolDefinition(
    name="add_feature",
    description="Add a class feature, racial trait, feat, or other ability to the character.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the feature",
            },
            "source": {
                "type": "string",
                "description": "Source of the feature (e.g., 'Fighter', 'Human', 'Feat')",
            },
            "description": {
                "type": "string",
                "description": "Description of what the feature does",
            },
            "uses": {
                "type": "integer",
                "description": "Number of uses if limited (omit for unlimited)",
                "minimum": 1,
            },
            "recharge": {
                "type": "string",
                "description": "When the feature recharges",
                "enum": ["short rest", "long rest"],
            },
        },
        "required": ["name", "source", "description"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.MODERATE,
)

REMOVE_FEATURE = ToolDefinition(
    name="remove_feature",
    description="Remove a feature from the character by name.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the feature to remove",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.DESTRUCTIVE,
)
