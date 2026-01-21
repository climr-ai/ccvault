"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest
import yaml

from dnd_manager.config import (
    Config,
    ConfigManager,
    _mask_key,
    SENSITIVE_KEYS,
)


class TestConfig:
    """Tests for Config model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.ai.default_provider == "gemini"
        assert config.ai.gemini.enabled is True
        assert config.ai.gemini.auto_classify is True
        assert config.character_defaults.ruleset == "dnd2024"

    def test_config_to_dict(self):
        """Test converting config to dict."""
        config = Config()
        data = config.model_dump()
        assert "ai" in data
        assert "gemini" in data["ai"]
        assert "default_provider" in data["ai"]

    def test_config_save_load(self, tmp_path):
        """Test saving and loading config."""
        config_file = tmp_path / "config.yaml"

        # Create and save config
        config = Config()
        config.ai.default_provider = "anthropic"
        config.ai.gemini.api_key = "test-key-123"

        # Manually save to test path
        with open(config_file, "w") as f:
            yaml.dump(config.model_dump(), f)

        # Load it back
        with open(config_file) as f:
            data = yaml.safe_load(f)
        loaded = Config.model_validate(data)

        assert loaded.ai.default_provider == "anthropic"
        assert loaded.ai.gemini.api_key == "test-key-123"


class TestConfigManager:
    """Tests for ConfigManager."""

    def test_get_setting(self):
        """Test getting settings by dotted key."""
        config = Config()
        manager = ConfigManager(config=config)

        assert manager.get("ai.default_provider") == "gemini"
        assert manager.get("ai.gemini.enabled") is True
        assert manager.get("character_defaults.ruleset") == "dnd2024"

    def test_get_nested_setting(self):
        """Test getting deeply nested settings."""
        config = Config()
        manager = ConfigManager(config=config)

        assert manager.get("ai.gemini.auto_classify") is True
        assert manager.get("ai.ollama.base_url") == "http://localhost:11434"

    def test_get_invalid_key(self):
        """Test getting invalid keys returns None."""
        config = Config()
        manager = ConfigManager(config=config)

        assert manager.get("invalid.key") is None
        assert manager.get("ai.invalid") is None
        assert manager.get("ai.gemini.invalid") is None

    def test_set_setting(self, tmp_path):
        """Test setting values by dotted key."""
        config = Config()
        manager = ConfigManager(config=config)
        # Override save to avoid writing to real config
        manager._config_path = tmp_path / "config.yaml"

        result = manager.set("ai.default_provider", "anthropic")
        assert result is True
        assert manager.get("ai.default_provider") == "anthropic"

    def test_set_boolean_string(self, tmp_path):
        """Test setting boolean values from strings."""
        config = Config()
        manager = ConfigManager(config=config)
        manager._config_path = tmp_path / "config.yaml"

        manager.set("ai.gemini.auto_classify", "false")
        assert manager.get("ai.gemini.auto_classify") is False

        manager.set("ai.gemini.auto_classify", "true")
        assert manager.get("ai.gemini.auto_classify") is True

    def test_set_invalid_key(self, tmp_path):
        """Test setting invalid keys returns False."""
        config = Config()
        manager = ConfigManager(config=config)
        manager._config_path = tmp_path / "config.yaml"

        assert manager.set("invalid.key", "value") is False
        assert manager.set("ai.invalid", "value") is False

    def test_list_settings(self):
        """Test listing all settings."""
        config = Config()
        config.ai.gemini.api_key = "secret-key-123"
        manager = ConfigManager(config=config)

        settings = manager.list_settings(show_sensitive=False)

        assert "ai.default_provider" in settings
        assert "ai.gemini.api_key" in settings
        # API key should be masked
        assert settings["ai.gemini.api_key"] != "secret-key-123"
        assert "****" in settings["ai.gemini.api_key"]

    def test_list_settings_show_sensitive(self):
        """Test listing settings with sensitive keys visible."""
        config = Config()
        config.ai.gemini.api_key = "secret-key-123"
        manager = ConfigManager(config=config)

        settings = manager.list_settings(show_sensitive=True)

        assert settings["ai.gemini.api_key"] == "secret-key-123"

    def test_reset(self, tmp_path):
        """Test resetting config to defaults."""
        config = Config()
        config.ai.default_provider = "anthropic"
        manager = ConfigManager(config=config)
        manager._config_path = tmp_path / "config.yaml"

        manager.reset()

        assert manager.get("ai.default_provider") == "gemini"


class TestMaskKey:
    """Tests for API key masking."""

    def test_mask_short_key(self):
        """Test masking short keys."""
        assert _mask_key("abc") == "***"
        assert _mask_key("abcdefgh") == "********"

    def test_mask_long_key(self):
        """Test masking long keys."""
        masked = _mask_key("abcd1234efgh5678")
        assert masked.startswith("abcd")
        assert masked.endswith("5678")
        assert "****" in masked

    def test_sensitive_keys_defined(self):
        """Test that sensitive keys are defined."""
        assert "ai.gemini.api_key" in SENSITIVE_KEYS
        assert "ai.anthropic.api_key" in SENSITIVE_KEYS
        assert "ai.openai.api_key" in SENSITIVE_KEYS
