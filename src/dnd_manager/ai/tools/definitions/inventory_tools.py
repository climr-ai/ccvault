"""Inventory management tool definitions."""

from dnd_manager.ai.tools.schema import ToolCategory, ToolDefinition, ToolRiskLevel


ADD_ITEM = ToolDefinition(
    name="add_item",
    description="Add an item to the character's inventory.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the item",
            },
            "quantity": {
                "type": "integer",
                "description": "Number of items to add",
                "minimum": 1,
            },
            "weight": {
                "type": "number",
                "description": "Weight per item in pounds",
            },
            "description": {
                "type": "string",
                "description": "Item description",
            },
            "equipped": {
                "type": "boolean",
                "description": "Whether item is immediately equipped",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.INVENTORY,
    risk_level=ToolRiskLevel.SAFE,
)

REMOVE_ITEM = ToolDefinition(
    name="remove_item",
    description="Remove an item from the character's inventory.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the item to remove",
            },
            "quantity": {
                "type": "integer",
                "description": "Number to remove (removes all if not specified)",
                "minimum": 1,
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.INVENTORY,
    risk_level=ToolRiskLevel.MODERATE,
)

EQUIP_ITEM = ToolDefinition(
    name="equip_item",
    description="Equip or unequip an item in the character's inventory.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the item",
            },
            "equipped": {
                "type": "boolean",
                "description": "True to equip, False to unequip",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.INVENTORY,
    risk_level=ToolRiskLevel.SAFE,
)

ATTUNE_ITEM = ToolDefinition(
    name="attune_item",
    description="Attune or end attunement to a magic item. Characters can attune to maximum 3 items.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the magic item",
            },
            "attuned": {
                "type": "boolean",
                "description": "True to attune, False to end attunement",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.INVENTORY,
    risk_level=ToolRiskLevel.SAFE,
)

MODIFY_CURRENCY = ToolDefinition(
    name="modify_currency",
    description="Add or remove currency from the character's inventory.",
    input_schema={
        "type": "object",
        "properties": {
            "cp": {
                "type": "integer",
                "description": "Copper pieces to add (negative to remove)",
            },
            "sp": {
                "type": "integer",
                "description": "Silver pieces to add (negative to remove)",
            },
            "ep": {
                "type": "integer",
                "description": "Electrum pieces to add (negative to remove)",
            },
            "gp": {
                "type": "integer",
                "description": "Gold pieces to add (negative to remove)",
            },
            "pp": {
                "type": "integer",
                "description": "Platinum pieces to add (negative to remove)",
            },
        },
        "required": [],
    },
    category=ToolCategory.INVENTORY,
    risk_level=ToolRiskLevel.SAFE,
)
