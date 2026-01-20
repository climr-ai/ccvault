"""Combat tool definitions."""

from dnd_manager.ai.tools.schema import ToolCategory, ToolDefinition, ToolRiskLevel


DEAL_DAMAGE = ToolDefinition(
    name="deal_damage",
    description="Apply damage to the character. Temporary HP is consumed first, then regular HP. Use this when the character takes damage in combat.",
    input_schema={
        "type": "object",
        "properties": {
            "amount": {
                "type": "integer",
                "description": "Amount of damage to deal (positive integer)",
                "minimum": 1,
            },
            "damage_type": {
                "type": "string",
                "description": "Type of damage for flavor/logging",
                "enum": [
                    "bludgeoning", "piercing", "slashing", "fire", "cold",
                    "lightning", "thunder", "poison", "acid", "necrotic",
                    "radiant", "force", "psychic",
                ],
            },
            "source": {
                "type": "string",
                "description": "Source of the damage for logging (e.g., 'Goblin attack', 'Fall damage')",
            },
        },
        "required": ["amount"],
    },
    category=ToolCategory.COMBAT,
    risk_level=ToolRiskLevel.MODERATE,
)

HEAL_CHARACTER = ToolDefinition(
    name="heal_character",
    description="Heal the character by restoring hit points. Cannot exceed maximum HP. Resets death saves if healing from 0 HP.",
    input_schema={
        "type": "object",
        "properties": {
            "amount": {
                "type": "integer",
                "description": "Amount of HP to restore (positive integer)",
                "minimum": 1,
            },
            "source": {
                "type": "string",
                "description": "Source of healing (e.g., 'Cure Wounds', 'Healing Potion')",
            },
        },
        "required": ["amount"],
    },
    category=ToolCategory.COMBAT,
    risk_level=ToolRiskLevel.SAFE,
)

TAKE_SHORT_REST = ToolDefinition(
    name="take_short_rest",
    description="Apply short rest effects: restore short-rest features. Hit dice can be spent separately using spend_hit_die to heal.",
    input_schema={
        "type": "object",
        "properties": {},
        "required": [],
    },
    category=ToolCategory.COMBAT,
    risk_level=ToolRiskLevel.SAFE,
)

TAKE_LONG_REST = ToolDefinition(
    name="take_long_rest",
    description="Apply long rest effects: restore all HP, restore half hit dice (minimum 1), restore all spell slots, restore long-rest features, reset death saves.",
    input_schema={
        "type": "object",
        "properties": {},
        "required": [],
    },
    category=ToolCategory.COMBAT,
    risk_level=ToolRiskLevel.SAFE,
)

SPEND_HIT_DIE = ToolDefinition(
    name="spend_hit_die",
    description="Spend hit dice to heal during a short rest. Rolls the hit die and adds CON modifier (minimum 1 HP per die).",
    input_schema={
        "type": "object",
        "properties": {
            "die_type": {
                "type": "string",
                "description": "Specific die type to spend (e.g., 'd10'). If not specified, uses largest available.",
                "pattern": "^d(4|6|8|10|12)$",
            },
            "count": {
                "type": "integer",
                "description": "Number of hit dice to spend",
                "minimum": 1,
            },
        },
        "required": [],
    },
    category=ToolCategory.COMBAT,
    risk_level=ToolRiskLevel.SAFE,
)

MODIFY_DEATH_SAVES = ToolDefinition(
    name="modify_death_saves",
    description="Record a death saving throw result or reset death saves.",
    input_schema={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to take",
                "enum": ["add_success", "add_failure", "add_crit_success", "add_crit_failure", "reset"],
            },
        },
        "required": ["action"],
    },
    category=ToolCategory.COMBAT,
    risk_level=ToolRiskLevel.MODERATE,
)
