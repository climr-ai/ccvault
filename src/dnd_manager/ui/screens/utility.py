"""Utility screens for the D&D Manager application."""

from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from dnd_manager.config import Config
from dnd_manager.models.character import Character


class DiceRollerScreen(Screen):
    """Screen for rolling dice."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("c", "clear", "Clear History"),
    ]

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self._roller = None

    @property
    def roller(self):
        if self._roller is None:
            from dnd_manager.dice import DiceRoller
            self._roller = DiceRoller()
        return self._roller

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Dice Roller", classes="title"),
            Static("Enter dice notation: 1d20, 2d6+5, 4d6kh3, adv, dis", classes="subtitle"),
            Horizontal(
                Input(placeholder="e.g., 1d20+5", id="dice-input"),
                Button("Roll", id="btn-roll", variant="primary"),
                classes="dice-input-row",
            ),
            Horizontal(
                Button("d4", id="btn-d4", classes="quick-die"),
                Button("d6", id="btn-d6", classes="quick-die"),
                Button("d8", id="btn-d8", classes="quick-die"),
                Button("d10", id="btn-d10", classes="quick-die"),
                Button("d12", id="btn-d12", classes="quick-die"),
                Button("d20", id="btn-d20", classes="quick-die"),
                Button("d100", id="btn-d100", classes="quick-die"),
                classes="quick-dice-row",
            ),
            Horizontal(
                Button("Adv", id="btn-adv", classes="quick-roll"),
                Button("Dis", id="btn-dis", classes="quick-roll"),
                Button("Stats", id="btn-stats", classes="quick-roll"),
                classes="quick-roll-row",
            ),
            Static("Roll History", classes="panel-title"),
            VerticalScroll(id="roll-history"),
            id="dice-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#dice-input", Input).focus()

    def _do_roll(self, notation: str) -> None:
        """Perform a dice roll and display result."""
        from dnd_manager.dice.parser import is_valid_dice_notation

        if not is_valid_dice_notation(notation):
            self.notify(f"Invalid dice notation: {notation}", severity="error")
            return

        result = self.roller.roll(notation)
        history = self.query_one("#roll-history", VerticalScroll)

        # Format result
        if result.is_natural_20:
            result_class = "crit-success"
            prefix = "🎯 "
        elif result.is_natural_1:
            result_class = "crit-fail"
            prefix = "💀 "
        else:
            result_class = "normal-roll"
            prefix = ""

        result_widget = Static(
            f"{prefix}{notation}: {result}",
            classes=f"roll-result {result_class}",
        )
        history.mount(result_widget)
        history.scroll_end()

        # Clear input
        self.query_one("#dice-input", Input).value = ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id
        if btn_id == "btn-roll":
            notation = self.query_one("#dice-input", Input).value.strip()
            if notation:
                self._do_roll(notation)
        elif btn_id and btn_id.startswith("btn-d"):
            die = btn_id.replace("btn-", "1")
            self._do_roll(die)
        elif btn_id == "btn-adv":
            self._do_roll("adv")
        elif btn_id == "btn-dis":
            self._do_roll("dis")
        elif btn_id == "btn-stats":
            # Roll 4d6kh3 six times for stats
            for i in range(6):
                self._do_roll("4d6kh3")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        if event.input.id == "dice-input" and event.value.strip():
            self._do_roll(event.value.strip())

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()

    def action_clear(self) -> None:
        """Clear roll history."""
        history = self.query_one("#roll-history", VerticalScroll)
        history.remove_children()
        self.notify("History cleared")


class HelpScreen(Screen):
    """Help screen with keyboard shortcuts and usage info."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("CLIMR Character Vault - Help", classes="title"),
            VerticalScroll(
                Static("""
[bold]DASHBOARD SHORTCUTS[/]
  [cyan]S[/]         Open Spells screen
  [cyan]I[/]         Open Inventory screen
  [cyan]F[/]         Open Features screen
  [cyan]N[/]         Open Notes screen
  [cyan]A[/]         Open AI Chat
  [cyan]R[/]         Open Dice Roller
  [cyan]H[/]         Open Homebrew Guidelines
  [cyan]E[/]         Edit character
  [cyan]?[/]         Show this help

[bold]FILE OPERATIONS[/]
  [cyan]Ctrl+S[/]    Save character
  [cyan]Ctrl+N[/]    New character
  [cyan]Ctrl+O[/]    Open character
  [cyan]Ctrl+Q[/]    Quit

[bold]DICE ROLLER[/]
  Basic:      1d20, 2d6, 1d8+5
  Advantage:  adv, 2d20kh1
  Disadvantage: dis, 2d20kl1
  Keep High:  4d6kh3 (stats)
  Drop Low:   4d6dl1

[bold]AI CHAT[/]
  Ask D&D rules questions
  Get character advice
  Roleplay scenarios
  Uses intelligent routing for free tier

[bold]NOTES[/]
  [cyan]E[/]         Edit notes in $EDITOR
  [cyan]B[/]         Edit backstory in $EDITOR

[bold]SPELLS[/]
  [cyan]C[/]         Cast (use spell slot)
  [cyan]P[/]         Toggle prepared
  [cyan]R[/]         Rest (recover slots)

[bold]CLI COMMANDS[/]
  ccvault                Run TUI
  ccvault list           List characters
  ccvault new <name>     Create character
  ccvault show <name>    Show character
  ccvault roll <dice>    Roll dice
  ccvault ask <question> Ask AI
  ccvault guidelines     View balance guidelines
  ccvault custom         Manage homebrew content
  ccvault export <name>  Export to Markdown

Press [cyan]Esc[/] or [cyan]Q[/] to close this help.
""", markup=True),
                id="help-content",
            ),
            id="help-container",
        )
        yield Footer()

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


class SettingsScreen(Screen):
    """Screen for configuring app settings and rule enforcement."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("r", "reset", "Reset to Defaults"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = Config.load()
        self.selected_index = 0
        self.settings_list: list[tuple[str, str, bool]] = []  # (key, description, value)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Settings & Rule Enforcement", classes="title"),
            Static("↑/↓ Navigate  \\[Enter/Space] Toggle  \\[R] Reset  \\[Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("ENFORCEMENT OPTIONS", classes="panel-title"),
                    VerticalScroll(id="settings-list", classes="settings-list"),
                    classes="panel settings-panel",
                ),
                Vertical(
                    Static("DESCRIPTION", classes="panel-title"),
                    VerticalScroll(id="setting-details", classes="setting-details"),
                    classes="panel details-panel",
                ),
                classes="settings-row",
            ),
            id="settings-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load settings."""
        self._build_settings_list()
        self._refresh_settings()

    def _build_settings_list(self) -> None:
        """Build the list of toggleable settings."""
        e = self.config.enforcement
        self.settings_list = [
            # Ability Scores
            ("enforce_ability_limits", "Enforce 1-30 ability score range", e.enforce_ability_limits),
            ("enforce_ability_cap_20", "Enforce 20 as max ability (before items)", e.enforce_ability_cap_20),
            # Equipment
            ("enforce_item_rarity", "Warn on items above character tier", e.enforce_item_rarity),
            ("enforce_attunement_limit", "Enforce attunement limit", e.enforce_attunement_limit),
            ("enforce_armor_proficiency", "Warn on armor without proficiency", e.enforce_armor_proficiency),
            ("enforce_weapon_proficiency", "Warn on weapons without proficiency", e.enforce_weapon_proficiency),
            ("enforce_encumbrance", "Track carrying capacity", e.enforce_encumbrance),
            # Leveling
            ("enforce_level_limits", "Enforce 1-20 level range", e.enforce_level_limits),
            ("enforce_multiclass_requirements", "Enforce multiclass ability requirements", e.enforce_multiclass_requirements),
            # Spellcasting
            ("enforce_spell_slots", "Track spell slot usage", e.enforce_spell_slots),
            ("enforce_spell_preparation", "Enforce prepared spell limits", e.enforce_spell_preparation),
            ("enforce_spell_components", "Track material components", e.enforce_spell_components),
            ("enforce_concentration", "Warn about concentration conflicts", e.enforce_concentration),
            # Combat
            ("enforce_action_economy", "Track actions per turn", e.enforce_action_economy),
            # General
            ("strict_mode", "Strict mode (prevent invalid saves)", e.strict_mode),
        ]

    def _refresh_settings(self) -> None:
        """Refresh the settings display."""
        list_widget = self.query_one("#settings-list", VerticalScroll)
        list_widget.remove_children()

        for i, (key, desc, value) in enumerate(self.settings_list):
            setting_class = "setting-row"
            if i == self.selected_index:
                setting_class += " selected"

            check = "✓" if value else "○"
            selector = "▶ " if i == self.selected_index else "  "

            list_widget.mount(Static(
                f"{selector}[{check}] {desc}",
                classes=setting_class,
            ))

        self._refresh_details()

    def _refresh_details(self) -> None:
        """Show details of the selected setting."""
        details_widget = self.query_one("#setting-details", VerticalScroll)
        details_widget.remove_children()

        if self.selected_index < len(self.settings_list):
            key, desc, value = self.settings_list[self.selected_index]

            details_widget.mount(Static(f"  {desc}", classes="setting-name"))
            details_widget.mount(Static(""))
            details_widget.mount(Static(f"  Key: enforcement.{key}", classes="setting-key"))
            details_widget.mount(Static(f"  Current: {'Enabled' if value else 'Disabled'}", classes="setting-value"))
            details_widget.mount(Static(""))

            # Add explanatory text
            explanations = {
                "enforce_ability_limits": "Prevents ability scores from going below 1 or above 30.",
                "enforce_ability_cap_20": "Prevents base ability scores from exceeding 20 (magic items can still increase).",
                "enforce_item_rarity": "Shows warnings when adding magic items above the recommended tier for character level.",
                "enforce_attunement_limit": "Prevents attuning to more than 3 magic items (default D&D limit).",
                "enforce_armor_proficiency": "Shows warnings when equipping armor without proficiency.",
                "enforce_weapon_proficiency": "Shows warnings when using weapons without proficiency.",
                "enforce_encumbrance": "Tracks weight carried and warns when exceeding carrying capacity.",
                "enforce_level_limits": "Prevents character level from going below 1 or above 20.",
                "enforce_multiclass_requirements": "Checks ability score requirements when multiclassing.",
                "enforce_spell_slots": "Tracks spell slot usage and prevents casting without slots.",
                "enforce_spell_preparation": "Limits prepared spells based on class rules.",
                "enforce_spell_components": "Tracks material components and spell focus requirements.",
                "enforce_concentration": "Warns when casting a concentration spell while concentrating.",
                "enforce_action_economy": "Tracks actions, bonus actions, and reactions per turn.",
                "strict_mode": "Prevents saving characters that violate any enabled enforcement rules.",
            }

            if key in explanations:
                details_widget.mount(Static(f"  {explanations[key]}", classes="setting-explain"))

    def key_up(self) -> None:
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1
            self._refresh_settings()

    def key_down(self) -> None:
        """Move selection down."""
        if self.selected_index < len(self.settings_list) - 1:
            self.selected_index += 1
            self._refresh_settings()

    def key_enter(self) -> None:
        """Toggle the selected setting."""
        self._toggle_current()

    def key_space(self) -> None:
        """Toggle the selected setting."""
        self._toggle_current()

    def _toggle_current(self) -> None:
        """Toggle the currently selected setting."""
        if self.selected_index < len(self.settings_list):
            key, desc, value = self.settings_list[self.selected_index]
            new_value = not value

            # Update config
            setattr(self.config.enforcement, key, new_value)
            self.config.save()

            # Update local list
            self.settings_list[self.selected_index] = (key, desc, new_value)

            status = "enabled" if new_value else "disabled"
            self.notify(f"{desc}: {status}")
            self._refresh_settings()

    def action_reset(self) -> None:
        """Reset all enforcement settings to defaults."""
        from dnd_manager.config import EnforcementConfig
        self.config.enforcement = EnforcementConfig()
        self.config.save()
        self._build_settings_list()
        self._refresh_settings()
        self.notify("Settings reset to defaults")

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()
