"""Configuration management for D&D Character Manager.

Handles user settings, API keys, and preferences stored in a YAML config file.
Config location: ~/.config/dnd-manager/config.yaml (or OS-appropriate equivalent)
"""

import logging
import os
import threading
from pathlib import Path
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field, field_validator
from platformdirs import user_config_dir, user_data_dir
import yaml

logger = logging.getLogger(__name__)

# Current config schema version - increment when making breaking changes
CONFIG_SCHEMA_VERSION = 2


# Settings that contain sensitive data (shown masked in list)
SENSITIVE_KEYS = {
    "ai.gemini.api_key",
    "ai.anthropic.api_key",
    "ai.openai.api_key",
}


class CharacterDefaults(BaseModel):
    """Default values for new characters with validation."""

    name: str = Field(default="New Hero", min_length=1, max_length=100, description="Default character name")
    class_name: str = Field(default="Fighter", min_length=1, max_length=50, description="Default class")
    species: str = Field(default="Human", min_length=1, max_length=50, description="Default species")
    background: str = Field(default="Soldier", min_length=1, max_length=50, description="Default background")
    ruleset: str = Field(default="dnd2024", description="Default ruleset (dnd2014, dnd2024, tov)")

    @field_validator("ruleset")
    @classmethod
    def validate_ruleset(cls, v: str) -> str:
        """Validate that ruleset is a known value."""
        valid_rulesets = {"dnd2014", "dnd2024", "tov"}
        if v.lower() not in valid_rulesets:
            raise ValueError(f"Invalid ruleset '{v}', must be one of: {', '.join(sorted(valid_rulesets))}")
        return v.lower()


class GameRules(BaseModel):
    """D&D game rule constants with validation."""

    max_level: int = Field(default=20, ge=1, le=30, description="Maximum character level")
    min_level: int = Field(default=1, ge=1, le=20, description="Minimum character level")
    base_ability_score: int = Field(default=10, ge=1, le=30, description="Default ability score value")
    min_ability_score: int = Field(default=1, ge=1, le=10, description="Minimum ability score")
    max_ability_score: int = Field(default=30, ge=20, le=50, description="Maximum ability score (with magic)")
    standard_ability_cap: int = Field(default=20, ge=15, le=30, description="Ability score cap before magic items")
    default_ac: int = Field(default=10, ge=0, le=30, description="Default armor class")
    default_speed: int = Field(default=30, ge=0, le=120, description="Default movement speed in feet")
    death_saves_required: int = Field(default=3, ge=1, le=5, description="Death saves needed to stabilize/die")
    default_hit_die: str = Field(default="d8", description="Default hit die if not specified")

    @field_validator("default_hit_die")
    @classmethod
    def validate_hit_die(cls, v: str) -> str:
        """Validate that hit die is a valid die notation."""
        valid_dice = {"d4", "d6", "d8", "d10", "d12", "d20"}
        if v.lower() not in valid_dice:
            raise ValueError(f"Invalid hit die '{v}', must be one of: {', '.join(sorted(valid_dice))}")
        return v.lower()


class AIGenerationConfig(BaseModel):
    """AI text generation parameters with validation."""

    max_tokens: int = Field(default=1024, ge=1, le=32000, description="Maximum tokens in AI response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="AI temperature (0.0-2.0)")


class StorageConfig(BaseModel):
    """Storage and backup settings."""

    max_backups: int = Field(default=3, description="Maximum backup files to keep per character")
    backup_dir_name: str = Field(default=".backups", description="Name of backup subdirectory")


def _get_app_version() -> str:
    """Get version from package metadata."""
    try:
        from importlib.metadata import version
        return version("ccvault")
    except Exception:
        return "dev"


class VersionInfo(BaseModel):
    """Version information."""

    app_version: str = Field(default_factory=_get_app_version, description="Application version")
    schema_version: str = Field(default="1.0", description="Character data schema version")


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
    fallback_editor: str = Field(default="nano", description="Editor when $EDITOR/$VISUAL not set")
    dashboard_layout: str = Field(default="balanced", description="Default dashboard layout preset")
    dashboard_panels: Optional[list[str]] = Field(default=None, description="Custom dashboard panels (overrides preset)")


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


# =============================================================================
# Config Migrations
# =============================================================================


def migrate_v1_to_v2(data: dict) -> dict:
    """Migrate config from version 1 to version 2.

    Changes in v2:
    - Added config_version field
    - Restructured AI config with provider-specific settings
    - Added enforcement config section
    """
    # Ensure AI config structure exists
    if "ai" not in data:
        data["ai"] = {}

    ai = data["ai"]

    # Migrate old flat API key structure to nested provider config
    # Old: ai.gemini_api_key -> New: ai.gemini.api_key
    for provider in ["gemini", "anthropic", "openai"]:
        old_key = f"{provider}_api_key"
        if old_key in ai:
            if provider not in ai:
                ai[provider] = {}
            ai[provider]["api_key"] = ai.pop(old_key)

    # Migrate old model setting
    if "default_model" in ai and "gemini" in ai:
        if "preferred_model" not in ai["gemini"]:
            ai["gemini"]["preferred_model"] = ai.get("default_model")

    # Ensure enforcement section exists (new in v2)
    if "enforcement" not in data:
        data["enforcement"] = {}

    data["config_version"] = 2
    return data


# Migration registry: version -> migration function
MIGRATIONS: dict[int, Callable[[dict], dict]] = {
    1: migrate_v1_to_v2,
}


def migrate_config(data: dict) -> dict:
    """Run all necessary migrations on config data.

    Args:
        data: Raw config data from YAML

    Returns:
        Migrated config data
    """
    current_version = data.get("config_version", 1)

    if current_version >= CONFIG_SCHEMA_VERSION:
        return data

    logger.info(f"Migrating config from v{current_version} to v{CONFIG_SCHEMA_VERSION}")

    # Run migrations in order
    for version in range(current_version, CONFIG_SCHEMA_VERSION):
        if version in MIGRATIONS:
            logger.debug(f"Running migration v{version} -> v{version + 1}")
            data = MIGRATIONS[version](data)

    return data


class Config(BaseModel):
    """Application configuration."""

    # Schema version for migrations
    config_version: int = Field(default=CONFIG_SCHEMA_VERSION)

    # Core settings
    character_defaults: CharacterDefaults = Field(default_factory=CharacterDefaults)
    game_rules: GameRules = Field(default_factory=GameRules)
    versions: VersionInfo = Field(default_factory=VersionInfo)

    # AI settings
    ai: AIConfig = Field(default_factory=AIConfig)
    ai_generation: AIGenerationConfig = Field(default_factory=AIGenerationConfig)

    # UI and storage
    ui: UIConfig = Field(default_factory=UIConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)

    # Rule enforcement
    enforcement: EnforcementConfig = Field(default_factory=EnforcementConfig)

    # Directory overrides (None = use defaults)
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
        """Load configuration from file or create default.

        Automatically runs migrations if the config version is outdated.
        """
        config_path = cls.get_config_path()

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Create backup BEFORE validation/migration in case something goes wrong
            import shutil
            backup_path = config_path.with_suffix(".yaml.pre_load_backup")
            try:
                shutil.copy2(config_path, backup_path)
            except (OSError, IOError) as backup_error:
                logger.warning(f"Failed to create pre-load backup: {backup_error}")

            # Run migrations if needed
            data = migrate_config(data)

            try:
                config = cls.model_validate(data)
            except (ValueError, TypeError) as e:
                # Validation error - config data is invalid, use defaults
                logger.warning(f"Config validation failed: {e}. Using defaults.")
                logger.info(f"Original config preserved at: {backup_path}")
                config = cls()

            # Save if migrations were applied
            if data.get("config_version", 1) != CONFIG_SCHEMA_VERSION:
                config.save()

            return config

        # Create default config
        config = cls()
        config.save()
        return config

    def save(self) -> None:
        """Save configuration to file with backup and atomic write."""
        import shutil
        import tempfile

        config_path = self.get_config_path()
        data = self.model_dump(mode="json")

        # Create backup of existing config if it exists
        if config_path.exists():
            backup_path = config_path.with_suffix(".yaml.bak")
            try:
                shutil.copy2(config_path, backup_path)
            except (OSError, IOError) as e:
                logger.warning(f"Failed to create config backup: {e}")

        # Write to temp file first, then atomic rename
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            # Write to temp file in same directory for atomic rename
            fd, temp_path = tempfile.mkstemp(
                dir=config_path.parent,
                prefix=".config_",
                suffix=".yaml.tmp"
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                # Atomic rename
                Path(temp_path).replace(config_path)
            except Exception:
                # Clean up temp file on error
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                raise
        except (OSError, IOError) as e:
            logger.error(f"Failed to save config: {e}")
            raise

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

        # Validate no part accesses private/protected attributes
        for part in parts:
            if part.startswith("_"):
                logger.warning(f"Attempted to access private attribute: {key}")
                return None

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

        # Validate no part accesses private/protected attributes
        for part in parts:
            if part.startswith("_"):
                logger.warning(f"Attempted to set private attribute: {key}")
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


# Global config manager instance with thread-safe initialization
_config_manager: Optional[ConfigManager] = None
_config_manager_lock = threading.Lock()


def get_config_manager() -> ConfigManager:
    """Get the global config manager instance (thread-safe)."""
    global _config_manager

    with _config_manager_lock:
        if _config_manager is None:
            _config_manager = ConfigManager()
        return _config_manager


def get_config() -> Config:
    """Get the current configuration."""
    return get_config_manager().config
