# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Skills Auto-Load

The `/dev-rules` skill is **automatically loaded** via SessionStart hook (configured in `.claude/settings.json`).

This enforces:
- Commit discipline (never commit without user request, run tests first)
- No hardcoded secrets
- No workarounds or hacks
- Proper code integration

The skill content is in `.claude/skills/dev-rules/SKILL.md` and is injected into every session automatically.

## Project Overview

CCVault is a CLI-based D&D 5e character manager with multi-ruleset support (D&D 2014, D&D 2024, Tales of the Valiant), built with Textual TUI framework and featuring AI integration for chat assistance and PDF character import.

## Development Commands

### Setup
```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Running
```bash
# Run the TUI application
python -m dnd_manager.main
# Or after installation:
ccvault
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_character.py

# Run with coverage
pytest --cov=dnd_manager

# Run specific test
pytest tests/test_dice.py::TestDiceRoller::test_advantage

# Verbose output
pytest -v
```

### Code Quality
```bash
# Type checking
mypy src/

# Linting
ruff check src/

# Format check
ruff format --check src/
```

## Architecture

### Core Design Patterns

**Ruleset Abstraction**: The system uses an abstract base class `Ruleset` (in `rulesets/base.py`) that defines a common interface for all D&D rulesets. Each ruleset implementation (DND2014, DND2024, ToV) provides its own logic for:
- Character creation steps and terminology (Race/Species/Lineage)
- Ability score assignment rules (racial bonuses, standard array, point buy)
- Subclass selection timing (varies by class and edition)
- Hit point calculation
- Spell slot progression
- Class/subclass availability

**AI Tool Registry**: The AI system uses a registry pattern for tool-calling capabilities. Tools are defined as schemas in `ai/tools/definitions/` with corresponding handlers in `ai/tools/handlers/`. The `ToolRegistry` singleton manages registration and discovery. Tool categories include:
- Query tools (read character data)
- Combat tools (damage, healing, rests)
- Character tools (leveling, ability scores, features)
- Spell tools (learning/preparing spells, spell slots)
- Inventory tools (adding/removing/equipping items)
- Creation tools (character creation assistance)
- Ruleset tools (ruleset-specific queries)

**Data Layer**: Game content (spells, items, classes, species, etc.) lives in `data/` as Python modules exposing query functions. Custom content extends the base system through `data/custom.py` and the homebrew library (`data/library.py`).

**Storage**: Characters are persisted as YAML files via `YAMLStore` generic class in `storage/yaml_store.py`. The system includes automatic backup/recovery, filename sanitization, and migration support. Character data directory defaults to `~/Library/Application Support/ccvault/characters/` on macOS.

### Key Components

**Character Model** (`models/character.py`): The `Character` class is a Pydantic model representing all character data:
- `meta`: Ruleset, version, timestamps, sync ID, dashboard customization
- `primary_class`/`multiclass`: Class levels and subclasses
- `abilities`: Ability scores with bonuses and overrides
- `combat`: HP, AC, initiative, death saves, conditions
- `spellcasting`: Spell lists, slots, prepared spells
- `inventory`: Items, equipment, currency, attunement
- `features`: Class features, feats, racial traits
- `proficiencies`: Skills, saves, weapons, armor, tools

**Textual UI** (`ui/screens/`): The TUI is built with Textual screens and widgets:
- `dashboard.py`: Main character view with customizable panels
- `creation.py`: Step-by-step character creation wizard
- `ai.py`: AI chat interface with tool-calling display
- `editors.py`: In-place editing screens for character data
- `browsers.py`: Searchable libraries (spells, magic items, etc.)
- `level.py`: Level-up wizard with multiclass support
- `panels.py`: Reusable dashboard panel widgets

**AI Integration** (`ai/`): Multi-provider AI system with vision support:
- `providers.py`: Provider registry (Gemini, Claude, GPT, Ollama)
- `base.py`: Common `AIProvider` interface
- `router.py`: Provider-specific tool schema conversion
- `context.py`: Character context generation for AI
- Provider-specific implementations: `gemini.py`, `anthropic_provider.py`, `openai_provider.py`, `ollama_provider.py`

**Character Import** (`import_char/`): AI-powered PDF character sheet parsing:
- `parser.py`: Vision model orchestration for sheet extraction
- `prompts.py`: Structured prompts for different sheet types
- `pdf_reader.py`: PDF to image conversion
- `session.py`: Multi-step import wizard state management

**Dice System** (`dice/`): Full D&D notation parser and roller:
- `parser.py`: Parses notation like `4d6kh3`, `2d20kl1`, `adv`, `dis`
- `roller.py`: Executes rolls with modifiers, advantage/disadvantage, keep/drop

### Data Flow

1. **Character Loading**: `CharacterStore.load(name)` → `YAMLStore.load()` → YAML parsing → Pydantic validation → `Character` instance
2. **Character Saving**: `Character` instance → Pydantic serialization → YAML dumping → automatic backup creation → `YAMLStore.save()`
3. **AI Chat**: User message → `AIProvider.chat()` → tool calls → `ToolExecutor.execute()` → handler functions modify Character → response with results
4. **Character Creation**: Multi-step wizard (`creation.py`) → user choices per ruleset → `Character.create_new()` → initial state → save to YAML
5. **PDF Import**: Upload PDF → `pdf_reader.py` converts to images → `CharacterSheetParser` uses vision model → structured `ParsedCharacterData` → wizard review → Character creation

### Configuration

Configuration lives in `config.py` using `platformdirs` for XDG compliance:
- Config file: `~/.config/ccvault/config.yaml` (macOS: `~/Library/Application Support/ccvault/config.yaml`)
- Stores: AI API keys, default provider, TUI theme, storage settings, dashboard layout preferences
- `ConfigManager` singleton provides typed access to config with auto-save

### Testing Patterns

Tests use pytest with fixtures for common setups:
- Character fixtures create test characters for various rulesets
- Ruleset tests verify interface compliance across all implementations
- UI tests use Textual's `pilot` for interaction simulation
- Tool tests mock Character instances and verify tool handlers work correctly
- Dice tests verify parser correctness and roll statistics

## Important Conventions

### Ability Scores
Ability scores have three components tracked separately:
- `base`: The base score (typically 8-15 after creation)
- `bonuses`: List of named bonuses (e.g., from items, spells)
- `override`: Optional override value (e.g., Belt of Giant Strength)

Always use `get_score()` to get the final computed score. Never modify `base` after character creation unless explicitly rolling stats.

### Spell Management
Spell handling varies by ruleset and class:
- **Known spells**: Classes that learn spells permanently (Bard, Sorcerer, Ranger)
- **Prepared spells**: Classes that prepare from their full list (Cleric, Druid, Wizard)
- **Always prepared**: Some spells are always prepared and don't count against limits

Use `character.spellcasting.known_spells` for the character's spell repertoire and `prepared_spells` for what's currently prepared.

### Multiclassing
Multiclass characters are supported with:
- `primary_class`: Main class (first class taken)
- `multiclass`: List of additional class levels
- Total character level computed across all classes
- Spell slots calculated based on caster level (full/half/third caster formula)
- Hit dice tracked per class in `combat.hit_dice.pools` dict

### Rulesets
Always check the character's `meta.ruleset` when implementing features. Terminology and mechanics vary:
- **2014**: "Race" provides ability bonuses, varied subclass timing
- **2024**: "Species" is cosmetic, Backgrounds provide ability scores (+2/+1) and Origin Feat, all subclasses at level 3
- **ToV**: "Lineage" + "Heritage", Talents instead of Feats, 13 classes (includes Mechanist)

Use `RulesetRegistry.get(character.meta.ruleset)` to get the appropriate ruleset implementation.

### File Naming
Character files use sanitized names: spaces become underscores, special chars removed, `.yaml` extension. The `_sanitize_filename()` method in `YAMLStore` handles this. Always use character's `name` field for display, not filename.

### Dashboard Customization
Dashboard layout can be customized per-character or globally:
- `character.meta.dashboard_layout`: Layout preset name
- `character.meta.dashboard_panels`: List of panel IDs to display
- `character.meta.panel_item_orders`: Dict mapping panel IDs to ordered item lists (for reorderable panels like inventory)

## Common Tasks

### Adding a New Ruleset
1. Create new file in `rulesets/` implementing `Ruleset` abstract class
2. Define all required methods (ability score methods, class/subclass methods, HP calculation)
3. Register in `RulesetRegistry` in `rulesets/__init__.py`
4. Add ruleset ID to `RulesetId` enum in `models/character.py`
5. Add data for classes/species/backgrounds in `data/` (or reuse existing)

### Adding a New AI Tool
1. Define schema in `ai/tools/definitions/<category>_tools.py` as a `ToolDefinition`
2. Implement handler in `ai/tools/handlers/<category>_handlers.py`
3. Register tool and handler in `ToolRegistry._register_builtin_tools()` in `ai/tools/registry.py`
4. Tool will be automatically available in AI chat

### Adding a New Dashboard Panel
1. Create widget class in `ui/screens/panels.py` extending `DashboardPanel`
2. Implement `compose()` to build panel UI
3. Implement `update_data()` to refresh with character data
4. Add panel to `PANEL_REGISTRY` dict with unique ID
5. Panel becomes available in dashboard customization

### Modifying Character Data
Always use the appropriate methods rather than direct field assignment:
- Use `set_ability_score()` for ability changes (validates range)
- Use `add_feature()` / `remove_feature()` for features
- Use `gain_hp()` / `lose_hp()` for HP changes
- Use `add_item()` / `remove_item()` for inventory
- After modifications, call `character_store.save(character)` to persist

## External Dependencies

- **Textual**: TUI framework, see https://textual.textualize.io/
- **Pydantic**: Data validation, models define schemas with validation
- **PyYAML**: Character serialization
- **Jinja2**: Template engine for Markdown/PDF export
- **google-genai, anthropic, openai, ollama**: AI provider SDKs
- **weasyprint** (optional): PDF export, requires system dependencies
- **pdf2image, PyMuPDF** (optional): PDF import support
