# CCVault - D&D Character Manager

A comprehensive CLI-based D&D 5e character manager supporting multiple rulesets with AI integration, dice rolling, and export capabilities.

## Features

- **Multi-Ruleset Support**: D&D 5e 2014, D&D 5e 2024, and Tales of the Valiant
- **Terminal UI**: Beautiful, responsive interface built with Textual
- **AI Integration**: Chat with AI assistants (Gemini, Claude, GPT, Ollama) with full tool-calling
- **YAML Storage**: Human-readable character files, git-friendly
- **Dice Roller**: Full notation support with history
- **PDF/Markdown Export**: Generate character sheets
- **Custom Content**: Extensible system for homebrew content

## Installation

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/jaredgiosinuff/dnd-manager/main/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/jaredgiosinuff/dnd-manager/main/install.ps1 | iex
```

### Manual Install

```bash
# If you have uv installed:
uv tool install git+https://github.com/jaredgiosinuff/dnd-manager

# Or with pipx:
pipx install git+https://github.com/jaredgiosinuff/dnd-manager

# With PDF export support (requires system dependencies):
uv tool install "ccvault[pdf] @ git+https://github.com/jaredgiosinuff/dnd-manager"
```

### For Development

```bash
git clone https://github.com/jaredgiosinuff/dnd-manager
cd dnd-manager
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Uninstall

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/jaredgiosinuff/dnd-manager/main/uninstall.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/jaredgiosinuff/dnd-manager/main/uninstall.ps1 | iex
```

## Usage

```bash
ccvault
```

That's it! The app will launch and guide you through setup.

## Quick Start

```bash
# Launch the app
ccvault

# Or with specific commands:
ccvault new "Gandalf" --class Wizard   # Create a character
ccvault list                            # List all characters
ccvault show Gandalf                    # Show character summary
ccvault export Gandalf -o gandalf.md    # Export to Markdown
ccvault roll 2d6+5                      # Roll dice
ccvault ask "How does sneak attack work?"  # Ask the AI
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `ccvault` | Launch the TUI |
| `ccvault new <name>` | Create a new character |
| `ccvault list` | List all characters |
| `ccvault show <name>` | Display character summary |
| `ccvault export <name>` | Export to Markdown/PDF |
| `ccvault roll <dice>` | Roll dice (e.g., `2d6+5`) |
| `ccvault ask <question>` | Ask the AI assistant |

## Keyboard Shortcuts (TUI)

| Key | Action |
|-----|--------|
| `s` | Spells screen |
| `i` | Inventory screen |
| `f` | Features/Feats |
| `n` | Notes |
| `a` | AI Chat |
| `r` | Roll Dice |
| `e` | Edit Character |
| `?` | Help |
| `Ctrl+S` | Save |
| `Ctrl+N` | New Character |
| `Ctrl+O` | Open Character |
| `Ctrl+Q` | Quit |

## Dice Notation

Full D&D dice notation support:

| Notation | Description | Example |
|----------|-------------|---------|
| `NdX` | Roll N dice with X sides | `2d6`, `1d20` |
| `NdX+M` | Add modifier | `1d20+5`, `2d6-2` |
| `NdXkh(Y)` | Keep highest Y dice | `4d6kh3` (stats) |
| `NdXkl(Y)` | Keep lowest Y dice | `2d20kl1` (disadvantage) |
| `NdXdl(Y)` | Drop lowest Y dice | `4d6dl1` |
| `NdXdh(Y)` | Drop highest Y dice | `4d6dh1` |
| `adv` | Advantage (2d20kh1) | `adv` |
| `dis` | Disadvantage (2d20kl1) | `dis` |
| `stats` | Roll for ability score | `stats` (4d6dl1) |

Compound expressions: `2d6+1d4+5`

## Rulesets

### D&D 5e 2014
The original 5th edition rules:
- Races provide ability score bonuses
- Subclass selection varies by class (Level 1-3)
- Backgrounds are primarily roleplay features
- 12 core classes

### D&D 5e 2024
The revised 5th edition rules:
- Species no longer provide ability bonuses
- Backgrounds provide ability scores (+2/+1) and Origin Feats
- All subclasses selected at Level 3
- Standardized subclass progression (3, 6, 10, 14)
- 12 core classes

### Tales of the Valiant
Kobold Press's 5e-compatible system:
- Lineage: What you are (Elf, Dwarf, Beastkin, etc.)
- Heritage: Where/how you were raised
- Talents instead of Feats
- 13 classes (includes Mechanist)

## Project Structure

```
dnd-manager/
├── src/dnd_manager/
│   ├── models/          # Data models (Character, Abilities, etc.)
│   ├── rulesets/         # Ruleset implementations
│   │   ├── base.py       # Abstract interface
│   │   ├── dnd2014.py    # D&D 5e 2014
│   │   ├── dnd2024.py    # D&D 5e 2024
│   │   └── tov.py        # Tales of the Valiant
│   ├── ui/               # Textual UI components
│   ├── dice/             # Dice rolling system
│   ├── export/           # Markdown/PDF export
│   ├── storage/          # YAML persistence
│   └── app.py            # Main application
├── tests/                # Test suite
└── characters/           # Character storage (created on first use)
```

## Character Data

Characters are stored as human-readable YAML files:

```yaml
meta:
  version: "1.0"
  ruleset: dnd2024
  created: 2025-01-17T12:00:00
  modified: 2025-01-17T14:30:00

name: Gandalf
player: Jared

primary_class:
  name: Wizard
  subclass: School of Evocation
  level: 5

species: Human
background: Sage
alignment: neutral_good

abilities:
  strength: {base: 8}
  dexterity: {base: 14}
  constitution: {base: 13}
  intelligence: {base: 17}
  wisdom: {base: 12}
  charisma: {base: 10}

spellcasting:
  ability: intelligence
  prepared:
    - Fireball
    - Counterspell
    - Shield
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=dnd_manager

# Type checking
mypy src/

# Linting
ruff check src/
```

## API Usage

```python
from dnd_manager.models import Character, RulesetId
from dnd_manager.storage import CharacterStore
from dnd_manager.dice import DiceRoller, roll
from dnd_manager.export import export_to_markdown

# Create a character with ruleset defaults
char = Character.create_new(
    name="Gandalf",
    class_name="Wizard",
    ruleset_id=RulesetId.DND_2024,
)

# Character properties
print(f"HP: {char.combat.hit_points.maximum}")
print(f"Spell DC: {char.get_spell_save_dc()}")
print(f"Spell slots: {char.get_expected_spell_slots()}")

# Dice rolling
result = roll("4d6kh3")
print(f"Rolled: {result.total}")

roller = DiceRoller()
attack = roller.attack(modifier=7, advantage=True)
damage = roller.damage("2d6+4", critical=attack.natural_20)

# Export to Markdown
export_to_markdown(char, Path("character.md"))
```

## Ruleset API

```python
from dnd_manager.rulesets.base import RulesetRegistry

# Get a ruleset
ruleset = RulesetRegistry.get("dnd2024")

# Query ruleset info
print(ruleset.species_term)  # "Species"
print(ruleset.get_available_classes())  # ["Barbarian", "Bard", ...]
print(ruleset.get_subclass_progression("Wizard"))  # Level 3

# Calculate values
hp = ruleset.calculate_hit_points("Wizard", level=5, con_modifier=2)
slots = ruleset.get_spell_slots("Wizard", level=5)
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_rulesets.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_dice.py::TestDiceRoller::test_advantage
```

## Versioning

CCVault uses semantic versioning: `MAJOR.MINOR.PATCH`

- **0.x.y** - Pre-release development (current)
- **MINOR (x)** - New features or significant changes
- **PATCH (y)** - Bug fixes, incremented with each code push

Current version: **0.1.2**

Check your version: The version is displayed on the welcome screen (e.g., "v0.1.1").

## License

MIT

## Acknowledgments

- [Textual](https://textual.textualize.io/) - TUI framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Jinja2](https://jinja.palletsprojects.com/) - Templating
- D&D 5e SRD - Open Gaming License content
- Kobold Press - Tales of the Valiant
