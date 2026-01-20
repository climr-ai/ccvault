"""Tests for application startup and initialization.

These tests ensure the app can actually launch without errors.
"""

import pytest
from pathlib import Path


class TestAppStartup:
    """Test that the application can start without errors."""

    def test_app_module_imports(self):
        """Test that the main app module can be imported."""
        from dnd_manager import app
        assert hasattr(app, 'run_app')
        assert hasattr(app, 'DNDManagerApp')

    def test_main_module_imports(self):
        """Test that the main entry point can be imported."""
        from dnd_manager import main
        assert hasattr(main, 'main')

    def test_all_screens_importable(self):
        """Test that all screen classes can be imported."""
        from dnd_manager.app import (
            DNDManagerApp,
            WelcomeScreen,
            CharacterSelectScreen,
            MainDashboard,
            DiceRollerScreen,
            AIChatScreen,
            HelpScreen,
            SpellsScreen,
            InventoryScreen,
            FeaturesScreen,
            NotesScreen,
            CharacterEditorScreen,
        )
        # Just importing without error is the test
        assert DNDManagerApp is not None
        assert WelcomeScreen is not None

    def test_css_stylesheet_parseable(self):
        """Test that the CSS stylesheet exists and is readable."""
        css_path = Path(__file__).parent.parent / "src" / "dnd_manager" / "ui" / "styles" / "app.tcss"
        assert css_path.exists(), f"CSS file not found: {css_path}"

        css_content = css_path.read_text()
        assert len(css_content) > 0, "CSS file is empty"

        # Check for known invalid patterns
        assert "font-size:" not in css_content, "font-size is not supported in Textual CSS"
        assert "margin: 0 auto" not in css_content, "margin: auto is not supported in Textual CSS"

    def test_app_can_instantiate(self):
        """Test that the app can be instantiated."""
        from dnd_manager.app import DNDManagerApp

        # Just instantiate - don't run
        app = DNDManagerApp()
        assert app is not None

    def test_bindings_are_valid(self):
        """Test that all screen bindings are valid."""
        from dnd_manager.app import (
            WelcomeScreen,
            CharacterSelectScreen,
            MainDashboard,
            DiceRollerScreen,
            AIChatScreen,
            HelpScreen,
        )

        screens = [
            WelcomeScreen,
            CharacterSelectScreen,
            MainDashboard,
            DiceRollerScreen,
            AIChatScreen,
            HelpScreen,
        ]

        for screen_class in screens:
            bindings = getattr(screen_class, 'BINDINGS', [])
            for binding in bindings:
                # Check binding has valid key (not empty, not just comma)
                assert binding.key, f"Empty key in {screen_class.__name__}"
                assert binding.key.strip(), f"Whitespace-only key in {screen_class.__name__}"
                assert binding.key != ",", f"Bare comma key in {screen_class.__name__} - use 'comma' instead"


class TestModelsImport:
    """Test that all models can be imported."""

    def test_character_model_imports(self):
        """Test Character model imports."""
        from dnd_manager.models.character import (
            Character,
            CharacterClass,
            HitPoints,
            Combat,
            Equipment,
            Spellcasting,
        )
        assert Character is not None

    def test_abilities_model_imports(self):
        """Test abilities model imports."""
        from dnd_manager.models.abilities import (
            Ability,
            Skill,
            AbilityScore,
            AbilityScores,
            SkillProficiency,
        )
        assert Ability is not None
        assert len(list(Skill)) == 18  # 18 skills in D&D 5e


class TestAIModulesImport:
    """Test that AI modules can be imported."""

    def test_ai_base_imports(self):
        """Test AI base module imports."""
        from dnd_manager.ai.base import (
            AIProvider,
            AIMessage,
            AIResponse,
            MessageRole,
            ToolChoice,
        )
        assert AIProvider is not None

    def test_ai_context_imports(self):
        """Test AI context module imports."""
        from dnd_manager.ai.context import (
            CharacterContext,
            build_system_prompt,
        )
        assert CharacterContext is not None

    def test_ai_tools_imports(self):
        """Test AI tools module imports."""
        from dnd_manager.ai.tools import (
            get_tool_registry,
            ToolExecutor,
        )
        registry = get_tool_registry()
        assert registry is not None
        # Should have tools registered
        tools = registry.get_anthropic_tool_definitions()
        assert len(tools) > 0, "No tools registered"


class TestProvidersImport:
    """Test that AI providers can be imported (not configured, just importable)."""

    def test_gemini_provider_imports(self):
        """Test Gemini provider imports."""
        from dnd_manager.ai.gemini import GeminiProvider
        assert GeminiProvider is not None

    def test_anthropic_provider_imports(self):
        """Test Anthropic provider imports."""
        from dnd_manager.ai.anthropic_provider import AnthropicProvider
        assert AnthropicProvider is not None

    def test_openai_provider_imports(self):
        """Test OpenAI provider imports."""
        from dnd_manager.ai.openai_provider import OpenAIProvider
        assert OpenAIProvider is not None

    def test_ollama_provider_imports(self):
        """Test Ollama provider imports."""
        from dnd_manager.ai.ollama_provider import OllamaProvider
        assert OllamaProvider is not None
