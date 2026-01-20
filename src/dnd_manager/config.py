"""Configuration management for D&D Character Manager.

Handles user settings, API keys, and preferences stored in a YAML config file.
Config location: ~/.config/dnd-manager/config.yaml (or OS-appropriate equivalent)
"""

import os
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field
from platformdirs import user_config_dir, user_data_dir
import yaml


# Settings that contain sensitive data (shown masked in list)
SENSITIVE_KEYS = {
    "ai.gemini.api_key",
    "ai.anthropic.api_key",
    "ai.openai.api_key",
}


class AIProviderConfig(BaseModel):
    """Configuration for an AI provider."""

    enabled: bool = True
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None


class GeminiConfig(BaseModel):
    """Gemini-specific configuration."""

    enabled: bool = True
    api_key: Optional[str] = None
    auto_classify: bool = True  # Use intelligent routing
    preferred_model: Optional[str] = None  # Override auto-routing


class AIConfig(BaseModel):
    """AI integration configuration."""

    default_provider: str = Field(default="gemini")
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    anthropic: AIProviderConfig = Field(default_factory=AIProviderConfig)
    openai: AIProviderConfig = Field(default_factory=AIProviderConfig)
    ollama: AIProviderConfig = Field(
        default_factory=lambda: AIProviderConfig(
            base_url="http://localhost:11434",
            model="llama3.2",
        )
    )


class UIConfig(BaseModel):
    """UI configuration."""

    theme: str = Field(default="dark")
    min_terminal_width: int = Field(default=120)
    min_terminal_height: int = Field(default=40)
    notes_editor: Optional[str] = Field(default=None, description="Override $EDITOR for notes")


class EnforcementConfig(BaseModel):
    """Configuration for rule enforcement toggles.

    These settings control which D&D rules are strictly enforced vs. allowed
    to be bypassed for flexibility in different playstyles.
    """

    # Ability Scores
    enforce_ability_limits: bool = Field(
        default=True,
        description="Enforce 1-30 ability score range"
    )
    enforce_ability_cap_20: bool = Field(
        default=False,
        description="Enforce 20 as max ability score (before magic items)"
    )

    # Equipment
    enforce_item_rarity: bool = Field(
        default=False,
        description="Warn when adding items above character tier"
    )
    enforce_attunement_limit: bool = Field(
        default=True,
        description="Enforce maximum 3 attuned items"
    )
    max_attunement_slots: int = Field(
        default=3,
        description="Maximum number of attunement slots"
    )
    enforce_armor_proficiency: bool = Field(
        default=False,
        description="Warn when equipping armor without proficiency"
    )
    enforce_weapon_proficiency: bool = Field(
        default=False,
        description="Warn when equipping weapons without proficiency"
    )
    enforce_encumbrance: bool = Field(
        default=False,
        description="Track and enforce carrying capacity"
    )

    # Leveling
    enforce_level_limits: bool = Field(
        default=True,
        description="Enforce 1-20 level range"
    )
    enforce_multiclass_requirements: bool = Field(
        default=False,
        description="Enforce ability score requirements for multiclassing"
    )

    # Spellcasting
    enforce_spell_slots: bool = Field(
        default=True,
        description="Track and enforce spell slot limits"
    )
    enforce_spell_preparation: bool = Field(
        default=False,
        description="Enforce prepared spell limits"
    )
    enforce_spell_components: bool = Field(
        default=False,
        description="Track material components and foci"
    )
    enforce_concentration: bool = Field(
        default=False,
        description="Warn about concentration conflicts"
    )

    # Combat
    enforce_action_economy: bool = Field(
        default=False,
        description="Track actions, bonus actions, reactions"
    )

    # General
    strict_mode: bool = Field(
        default=False,
        description="Prevent saving characters that violate enforced rules"
    )


class Config(BaseModel):
    """Application configuration."""

    ai: AIConfig = Field(default_factory=AIConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    enforcement: EnforcementConfig = Field(default_factory=EnforcementConfig)
    default_ruleset: str = Field(default="dnd2024")
    character_directory: Optional[str] = Field(default=None)
    custom_content_directory: Optional[str] = Field(default=None)

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the configuration file path."""
        config_dir = Path(user_config_dir("dnd-manager", "dnd"))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.yaml"

    @classmethod
    def get_data_dir(cls) -> Path:
        """Get the data directory path."""
        data_dir = Path(user_data_dir("dnd-manager", "dnd"))
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file or create default."""
        config_path = cls.get_config_path()

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return cls.model_validate(data)

        # Create default config
        config = cls()
        config.save()
        return config

    def save(self) -> None:
        """Save configuration to file."""
        config_path = self.get_config_path()
        data = self.model_dump(mode="json")

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def get_character_directory(self) -> Path:
        """Get the character storage directory."""
        if self.character_directory:
            return Path(self.character_directory)
        return self.get_data_dir() / "characters"

    def get_custom_content_directory(self) -> Path:
        """Get the custom content directory."""
        if self.custom_content_directory:
            return Path(self.custom_content_directory)
        return self.get_data_dir() / "custom"


class ConfigManager:
    """Manages loading, saving, and accessing configuration via dotted keys."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the config manager.

        Args:
            config: Optional pre-loaded config (for testing)
        """
        self._config = config

    @property
    def config(self) -> Config:
        """Get the current config, loading if necessary."""
        if self._config is None:
            self._config = Config.load()
        return self._config

    def reload(self) -> Config:
        """Reload configuration from file."""
        self._config = Config.load()
        return self._config

    def save(self) -> None:
        """Save current configuration to file."""
        self.config.save()

    def get(self, key: str) -> Any:
        """Get a config value by dotted key path.

        Args:
            key: Dotted key path (e.g., "ai.gemini.api_key", "ui.theme")

        Returns:
            The config value, or None if not found
        """
        parts = key.split(".")
        obj: Any = self.config

        for part in parts:
            if isinstance(obj, BaseModel) and hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return None

        return obj

    def set(self, key: str, value: Any) -> bool:
        """Set a config value by dotted key path.

        Args:
            key: Dotted key path (e.g., "ai.gemini.api_key", "ui.theme")
            value: Value to set

        Returns:
            True if successful, False if key path is invalid
        """
        parts = key.split(".")
        if len(parts) < 1:
            return False

        obj: Any = self.config

        # Navigate to the parent object
        for part in parts[:-1]:
            if isinstance(obj, BaseModel) and hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return False

        # Set the final attribute
        final_key = parts[-1]
        if isinstance(obj, BaseModel) and hasattr(obj, final_key):
            # Type coercion for known types
            current_value = getattr(obj, final_key)
            if isinstance(current_value, bool) and isinstance(value, str):
                value = value.lower() in ("true", "1", "yes", "on")
            elif isinstance(current_value, int) and isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    return False

            setattr(obj, final_key, value)
            self.save()
            return True

        return False

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = Config()
        self.save()

    def list_settings(self, show_sensitive: bool = False) -> dict[str, Any]:
        """List all settings with their current values.

        Args:
            show_sensitive: If True, show full API keys; otherwise mask them

        Returns:
            Dictionary of all settings
        """
        result: dict[str, Any] = {}
        config_dict = self.config.model_dump()

        def flatten(d: dict[str, Any], prefix: str = "") -> None:
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    flatten(value, full_key)
                else:
                    if full_key in SENSITIVE_KEYS and not show_sensitive:
                        if value:
                            result[full_key] = _mask_key(str(value))
                        else:
                            result[full_key] = None
                    else:
                        result[full_key] = value

        flatten(config_dict)
        return result

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider, checking config then environment.

        Args:
            provider: Provider name (gemini, anthropic, openai)

        Returns:
            API key if found, None otherwise
        """
        # Check config first
        key = self.get(f"ai.{provider}.api_key")
        if key:
            return str(key)

        # Fall back to environment variables
        env_vars: dict[str, list[str]] = {
            "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
            "anthropic": ["ANTHROPIC_API_KEY"],
            "openai": ["OPENAI_API_KEY"],
        }

        for env_var in env_vars.get(provider, []):
            value = os.environ.get(env_var)
            if value:
                return value

        return None


def _mask_key(key: str) -> str:
    """Mask an API key for display."""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> Config:
    """Get the current configuration."""
    return get_config_manager().config
