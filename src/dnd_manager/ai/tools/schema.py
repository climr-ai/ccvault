"""Tool definition schemas for AI function calling."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class ToolCategory(str, Enum):
    """Categories of tools for organization and filtering."""
    QUERY = "query"           # Read-only information retrieval
    COMBAT = "combat"         # Combat-related modifications
    CHARACTER = "character"   # Character stat modifications
    INVENTORY = "inventory"   # Inventory management
    SPELLS = "spells"         # Spell management
    CUSTOM = "custom"         # Custom stats and notes


class ToolRiskLevel(str, Enum):
    """Risk level determining confirmation requirements."""
    SAFE = "safe"             # No confirmation needed
    MODERATE = "moderate"     # Confirm for significant changes
    DESTRUCTIVE = "destructive"  # Always confirm


@dataclass
class ToolDefinition:
    """Complete definition of an AI-callable tool.

    Attributes:
        name: Unique tool identifier (e.g., "deal_damage")
        description: Human-readable description for the AI
        input_schema: JSON Schema for input validation
        category: Tool category for organization
        risk_level: Determines confirmation requirements
        requires_character: Whether a character must be loaded
        handler: Optional handler function (set during registration)
    """
    name: str
    description: str
    input_schema: dict[str, Any]
    category: ToolCategory
    risk_level: ToolRiskLevel = ToolRiskLevel.SAFE
    requires_character: bool = True
    handler: Optional[Callable] = field(default=None, repr=False)

    def to_anthropic_format(self) -> dict:
        """Convert to Anthropic tool use format.

        Returns:
            Dict compatible with Anthropic's tools parameter
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def validate_input(self, tool_input: dict[str, Any]) -> Optional[str]:
        """Validate input against the schema.

        Args:
            tool_input: Input dict from the AI

        Returns:
            Error message if validation fails, None if valid
        """
        schema = self.input_schema

        # Check required fields
        required = schema.get("required", [])
        for field_name in required:
            if field_name not in tool_input:
                return f"Missing required field: {field_name}"

        # Validate field types and constraints
        properties = schema.get("properties", {})
        for field_name, value in tool_input.items():
            if field_name not in properties:
                continue  # Allow extra fields

            prop_schema = properties[field_name]
            error = self._validate_field(field_name, value, prop_schema)
            if error:
                return error

        return None

    def _validate_field(
        self, field_name: str, value: Any, prop_schema: dict
    ) -> Optional[str]:
        """Validate a single field against its schema."""
        expected_type = prop_schema.get("type")

        # Type validation
        if expected_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                return f"Field '{field_name}' must be an integer"
        elif expected_type == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return f"Field '{field_name}' must be a number"
        elif expected_type == "string":
            if not isinstance(value, str):
                return f"Field '{field_name}' must be a string"
        elif expected_type == "boolean":
            if not isinstance(value, bool):
                return f"Field '{field_name}' must be a boolean"
        elif expected_type == "array":
            if not isinstance(value, list):
                return f"Field '{field_name}' must be an array"

        # Enum validation
        if "enum" in prop_schema and value not in prop_schema["enum"]:
            return f"Field '{field_name}' must be one of: {prop_schema['enum']}"

        # Range validation
        if "minimum" in prop_schema and value < prop_schema["minimum"]:
            return f"Field '{field_name}' must be >= {prop_schema['minimum']}"
        if "maximum" in prop_schema and value > prop_schema["maximum"]:
            return f"Field '{field_name}' must be <= {prop_schema['maximum']}"

        # Pattern validation for strings
        if expected_type == "string" and "pattern" in prop_schema:
            import re
            if not re.match(prop_schema["pattern"], value):
                return f"Field '{field_name}' does not match required pattern"

        return None
