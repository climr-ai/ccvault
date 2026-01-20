# D&D Character Manager

A comprehensive CLI-based D&D 5e character manager supporting multiple rulesets with AI integration, dice rolling, and export capabilities.

## Features

- **Multi-Ruleset Support**: D&D 5e 2014, D&D 5e 2024, and Tales of the Valiant
- **Terminal UI**: Beautiful, responsive interface built with Textual
- **AI Integration**: Chat with AI assistants (Claude, GPT, Ollama) about your characters
- **YAML Storage**: Human-readable character files, git-friendly
- **Dice Roller**: Full notation support with history
- **Markdown Export**: Generate character sheets with Jinja2 templates
- **Custom Content**: Extensible system for homebrew content

## Installation

```bash
# Clone and install with uv (recommended)
git clone https://github.com/yourusername/dnd-manager
cd dnd-manager
uv venv && source .venv/bin/activate
uv pip install -e .

# Or with pip
pip install -e .
```

## Quick Start

```bash
# Launch the TUI
dnd

# Create a new character
dnd new "Gandalf" --class Wizard

# List all characters
dnd list

# Show character summary
dnd show Gandalf

# Export to Markdown
dnd export Gandalf -o gandalf.md

# Roll dice
dnd roll 2d6+5
dnd roll 4d6kh3        # Roll stats (keep highest 3)
dnd roll adv           # Roll with advantage
dnd roll 1d20+7 -n 5   # Roll 5 times
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `dnd` | Launch the TUI |
| `dnd run [file]` | Launch TUI with optional character file |
| `dnd new <name>` | Create a new character |
| `dnd list` | List all characters |
| `dnd show <name>` | Display character summary |
| `dnd export <name>` | Export character to Markdown |
| `dnd roll <dice>` | Roll dice (e.g., `2d6+5`) |

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

## License

MIT

## Acknowledgments

- [Textual](https://textual.textualize.io/) - TUI framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Jinja2](https://jinja.palletsprojects.com/) - Templating
- D&D 5e SRD - Open Gaming License content
- Kobold Press - Tales of the Valiant
