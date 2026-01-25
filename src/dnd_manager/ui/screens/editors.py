"""Editor screens for the D&D Manager application."""

from typing import TYPE_CHECKING, Optional, Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static

from dnd_manager.models.character import Alignment
from dnd_manager.ui.screens.base import ListNavigationMixin
from dnd_manager.ui.screens.widgets import ClickableListItem

if TYPE_CHECKING:
    from dnd_manager.models.character import Character


class CharacterEditorScreen(Screen):
    """Screen for editing character attributes."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save Changes"),
        Binding("1", "edit_abilities", "Edit Abilities"),
        Binding("2", "edit_hp", "Edit HP"),
        Binding("3", "edit_info", "Edit Info"),
        Binding("4", "edit_custom_stats", "Custom Stats"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Edit Character - {self.character.name}", classes="title"),
            Static("\\[1] Abilities  \\[2] HP  \\[3] Info  \\[4] Custom Stats  \\[S] Save  \\[Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("ABILITY SCORES", classes="panel-title"),
                    self._build_ability_editor(),
                    classes="panel editor-panel",
                ),
                Vertical(
                    Static("COMBAT STATS", classes="panel-title"),
                    self._build_combat_editor(),
                    Static(""),
                    Static("CHARACTER INFO", classes="panel-title"),
                    self._build_info_editor(),
                    classes="panel editor-panel",
                ),
                classes="editor-row",
            ),
            id="editor-container",
        )
        yield Footer()

    def _build_ability_editor(self) -> Vertical:
        """Build ability score editor."""
        container = Vertical(classes="ability-editor")
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = getattr(self.character.abilities, ability)
            container.compose_add_child(Static(
                f"  {ability[:3].upper()}: {score.base:2d} + {score.bonus:2d} = {score.total:2d} ({score.modifier_str})",
                classes="editor-row",
            ))
        container.compose_add_child(Static(""))
        container.compose_add_child(Static("  Use \\[1] to edit scores", classes="hint"))
        return container

    def _build_combat_editor(self) -> Vertical:
        """Build combat stats editor."""
        c = self.character
        hp = c.combat.hit_points
        container = Vertical(classes="combat-editor")
        container.compose_add_child(Static(f"  HP: {hp.current}/{hp.maximum} (temp: {hp.temporary})", classes="editor-row"))
        container.compose_add_child(Static(f"  AC: {c.combat.total_ac} (base: {c.combat.armor_class.base})", classes="editor-row"))
        container.compose_add_child(Static(f"  Speed: {c.combat.total_speed} ft", classes="editor-row"))
        container.compose_add_child(Static(f"  Hit Dice: {c.combat.hit_dice.remaining}/{c.combat.hit_dice.total}", classes="editor-row"))
        container.compose_add_child(Static(""))
        container.compose_add_child(Static("  Use \\[2] to edit HP", classes="hint"))
        return container

    def _build_info_editor(self) -> Vertical:
        """Build character info editor."""
        c = self.character
        container = Vertical(classes="info-editor")
        container.compose_add_child(Static(f"  Name: {c.name}", classes="editor-row"))
        container.compose_add_child(Static(f"  Class: {c.primary_class.name} {c.primary_class.level}", classes="editor-row"))
        container.compose_add_child(Static(f"  {c.get_species_term()}: {c.species or 'Not set'}", classes="editor-row"))
        container.compose_add_child(Static(f"  Background: {c.background or 'Not set'}", classes="editor-row"))
        container.compose_add_child(Static(f"  Alignment: {c.alignment.display_name}", classes="editor-row"))
        container.compose_add_child(Static(""))
        container.compose_add_child(Static("  Use \\[3] to edit info", classes="hint"))
        return container

    def action_edit_abilities(self) -> None:
        """Edit ability scores."""
        self.app.push_screen(AbilityEditorScreen(self.character))

    def action_edit_hp(self) -> None:
        """Edit HP values."""
        self.app.push_screen(HPEditorScreen(self.character))

    def action_edit_info(self) -> None:
        """Edit character info."""
        self.app.push_screen(InfoEditorScreen(self.character))

    def action_edit_custom_stats(self) -> None:
        """Edit custom stats (Luck, Renown, etc.)."""
        self.app.push_screen(CustomStatsScreen(self.character))

    def action_save(self) -> None:
        """Save character changes."""
        self.app.save_character()
        self.notify("Character saved!", severity="information")

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()


class CustomStatsScreen(Screen):
    """Screen for managing custom stats (Luck, Renown, Piety, etc.)."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("a", "add_stat", "Add Stat"),
        Binding("d", "delete_stat", "Delete"),
        Binding("t", "add_template", "Add Template"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_index = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Custom Stats", classes="title"),
            Static("↑/↓ Select  ←/→ Adjust Value  \\[A] Add  \\[D] Delete  \\[T] Templates  \\[Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("YOUR CUSTOM STATS", classes="panel-title"),
                    VerticalScroll(id="stats-list", classes="stats-list"),
                    classes="panel stats-panel",
                ),
                Vertical(
                    Static("STAT DETAILS", classes="panel-title"),
                    VerticalScroll(id="stat-details", classes="stat-details"),
                    Static(""),
                    Static("AVAILABLE TEMPLATES", classes="panel-title"),
                    VerticalScroll(id="templates-list", classes="templates-list"),
                    classes="panel details-panel",
                ),
                classes="stats-row",
            ),
            id="custom-stats-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load stats."""
        self._refresh_stats()
        self._refresh_templates()

    def _refresh_stats(self) -> None:
        """Refresh the custom stats list."""
        list_widget = self.query_one("#stats-list", VerticalScroll)
        list_widget.remove_children()

        if not self.character.custom_stats:
            list_widget.mount(Static("  (No custom stats)", classes="no-items"))
            list_widget.mount(Static("  Press \\[A] to add or \\[T] for templates", classes="hint"))
        else:
            for i, stat in enumerate(self.character.custom_stats):
                stat_class = "stat-row"
                if i == self.selected_index:
                    stat_class += " selected"

                # Build value display with bounds
                bounds = ""
                if stat.min_value is not None or stat.max_value is not None:
                    min_str = str(stat.min_value) if stat.min_value is not None else "-∞"
                    max_str = str(stat.max_value) if stat.max_value is not None else "∞"
                    bounds = f" ({min_str} to {max_str})"

                list_widget.mount(Static(
                    f"  {'▶ ' if i == self.selected_index else '  '}{stat.name}: {stat.value}{bounds}",
                    classes=stat_class,
                ))

        self._refresh_stat_details()

    def _refresh_stat_details(self) -> None:
        """Show details of the selected stat."""
        details_widget = self.query_one("#stat-details", VerticalScroll)
        details_widget.remove_children()

        if not self.character.custom_stats or self.selected_index >= len(self.character.custom_stats):
            details_widget.mount(Static("  Select a stat to see details", classes="hint"))
            return

        stat = self.character.custom_stats[self.selected_index]

        details_widget.mount(Static(f"  {stat.name}", classes="stat-name"))
        details_widget.mount(Static(f"  Current Value: {stat.value}", classes="stat-value"))

        if stat.min_value is not None:
            details_widget.mount(Static(f"  Minimum: {stat.min_value}", classes="stat-bound"))
        if stat.max_value is not None:
            details_widget.mount(Static(f"  Maximum: {stat.max_value}", classes="stat-bound"))

        if stat.description:
            details_widget.mount(Static(""))
            details_widget.mount(Static(f"  {stat.description}", classes="stat-desc"))

    def _refresh_templates(self) -> None:
        """Show available stat templates."""
        from dnd_manager.models.character import CUSTOM_STAT_TEMPLATES

        templates_widget = self.query_one("#templates-list", VerticalScroll)
        templates_widget.remove_children()

        for name, template in CUSTOM_STAT_TEMPLATES.items():
            # Check if already added
            already_has = any(s.name.lower() == template.name.lower() for s in self.character.custom_stats)
            status = " ✓" if already_has else ""
            templates_widget.mount(Static(f"  • {template.name}{status}", classes="template-item"))

    def key_up(self) -> None:
        """Move selection up."""
        if self.character.custom_stats and self.selected_index > 0:
            self.selected_index -= 1
            self._refresh_stats()

    def key_down(self) -> None:
        """Move selection down."""
        if self.character.custom_stats and self.selected_index < len(self.character.custom_stats) - 1:
            self.selected_index += 1
            self._refresh_stats()

    def key_left(self) -> None:
        """Decrease selected stat value."""
        if self.character.custom_stats and self.selected_index < len(self.character.custom_stats):
            stat = self.character.custom_stats[self.selected_index]
            stat.adjust(-1)
            self.app.save_character()
            self._refresh_stats()

    def key_right(self) -> None:
        """Increase selected stat value."""
        if self.character.custom_stats and self.selected_index < len(self.character.custom_stats):
            stat = self.character.custom_stats[self.selected_index]
            stat.adjust(1)
            self.app.save_character()
            self._refresh_stats()

    def action_add_stat(self) -> None:
        """Add a new custom stat."""
        from dnd_manager.models.character import CustomStat

        # Create a basic new stat
        new_stat = CustomStat(
            name=f"Custom Stat {len(self.character.custom_stats) + 1}",
            value=0,
            description="A custom stat"
        )
        self.character.custom_stats.append(new_stat)
        self.app.save_character()
        self.selected_index = len(self.character.custom_stats) - 1
        self._refresh_stats()
        self._refresh_templates()
        self.notify(f"Added: {new_stat.name}")

    def action_add_template(self) -> None:
        """Add a stat from templates."""
        from dnd_manager.models.character import CUSTOM_STAT_TEMPLATES, CustomStat

        # Find next template not already added
        for name, template in CUSTOM_STAT_TEMPLATES.items():
            already_has = any(s.name.lower() == template.name.lower() for s in self.character.custom_stats)
            if not already_has:
                # Create a copy of the template
                new_stat = CustomStat(
                    name=template.name,
                    value=template.value,
                    min_value=template.min_value,
                    max_value=template.max_value,
                    description=template.description,
                )
                self.character.custom_stats.append(new_stat)
                self.app.save_character()
                self.selected_index = len(self.character.custom_stats) - 1
                self._refresh_stats()
                self._refresh_templates()
                self.notify(f"Added template: {new_stat.name}")
                return

        self.notify("All templates already added!", severity="warning")

    def action_delete_stat(self) -> None:
        """Delete the selected stat."""
        if not self.character.custom_stats or self.selected_index >= len(self.character.custom_stats):
            self.notify("No stat selected", severity="warning")
            return

        stat = self.character.custom_stats.pop(self.selected_index)
        self.app.save_character()
        self.selected_index = max(0, self.selected_index - 1)
        self._refresh_stats()
        self._refresh_templates()
        self.notify(f"Deleted: {stat.name}")

    def action_back(self) -> None:
        """Return to editor."""
        self.app.pop_screen()


class AbilityEditorScreen(Screen):
    """Screen for editing ability scores."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save"),
        Binding("b", "manage_bonuses", "Manage Bonuses"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_ability = 0
        self.abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Edit Ability Scores", classes="title"),
            Static("↑/↓ Select  ←/→ Adjust  \\[B] Bonuses  \\[S] Save  \\[Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(id="ability-list", classes="panel ability-panel"),
                Vertical(id="bonus-details", classes="panel bonus-panel"),
                classes="ability-editor-row",
            ),
            id="ability-editor-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Populate ability list."""
        self._refresh_abilities()

    def _refresh_abilities(self) -> None:
        """Refresh the ability list display."""
        container = self.query_one("#ability-list", Vertical)
        container.remove_children()

        container.mount(Static("ABILITY SCORES", classes="panel-title"))
        container.mount(Static(""))

        for i, ability in enumerate(self.abilities):
            score = getattr(self.character.abilities, ability)
            selected = "▶ " if i == self.selected_ability else "  "

            # Count bonuses for this ability
            ability_bonuses = [b for b in self.character.stat_bonuses if b.ability.lower() == ability]
            bonus_marker = f" [{len(ability_bonuses)} bonus]" if ability_bonuses else ""

            container.mount(Static(
                f"{selected}{ability.upper():15} Base: {score.base:2d}  Bonus: {score.bonus:+2d}  Total: {score.total:2d} ({score.modifier_str}){bonus_marker}",
                classes=f"ability-edit-row {'selected' if i == self.selected_ability else ''}",
            ))

        self._refresh_bonus_details()

    def _refresh_bonus_details(self) -> None:
        """Refresh the bonus details panel."""
        details = self.query_one("#bonus-details", Vertical)
        details.remove_children()

        ability = self.abilities[self.selected_ability]
        ability_bonuses = [b for b in self.character.stat_bonuses if b.ability.lower() == ability]

        details.mount(Static(f"BONUSES FOR {ability.upper()}", classes="panel-title"))
        details.mount(Static(""))

        if ability_bonuses:
            for bonus in ability_bonuses:
                temp_mark = " (temp)" if bonus.temporary else ""
                if bonus.is_override:
                    details.mount(Static(f"  • {bonus.source}: SET TO {bonus.override_value}{temp_mark}"))
                else:
                    details.mount(Static(f"  • {bonus.source}: +{bonus.bonus}{temp_mark}"))
                if bonus.duration:
                    details.mount(Static(f"      Duration: {bonus.duration}", classes="bonus-duration"))
        else:
            details.mount(Static("  (No bonuses)", classes="no-items"))
            details.mount(Static(""))
            details.mount(Static("  Press \\[B] to add bonuses", classes="hint"))

    def key_up(self) -> None:
        """Move selection up."""
        self.selected_ability = (self.selected_ability - 1) % len(self.abilities)
        self._refresh_abilities()

    def key_down(self) -> None:
        """Move selection down."""
        self.selected_ability = (self.selected_ability + 1) % len(self.abilities)
        self._refresh_abilities()

    def key_left(self) -> None:
        """Decrease selected ability."""
        ability = self.abilities[self.selected_ability]
        score = getattr(self.character.abilities, ability)
        if score.base > 1:
            score.base -= 1
            self._refresh_abilities()

    def key_right(self) -> None:
        """Increase selected ability."""
        ability = self.abilities[self.selected_ability]
        score = getattr(self.character.abilities, ability)
        if score.base < 30:
            score.base += 1
            self._refresh_abilities()

    def action_manage_bonuses(self) -> None:
        """Open the stat bonus management screen."""
        ability = self.abilities[self.selected_ability]
        self.app.push_screen(StatBonusScreen(self.character, ability))

    def action_save(self) -> None:
        """Save and go back."""
        self.app.save_character()
        self.notify("Ability scores saved!")
        self.app.pop_screen()

    def action_back(self) -> None:
        """Go back without saving."""
        self.app.pop_screen()


class StatBonusScreen(Screen):
    """Screen for managing stat bonuses from various sources."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("a", "add_bonus", "Add Bonus"),
        Binding("d", "delete_bonus", "Delete"),
        Binding("t", "toggle_temporary", "Toggle Temp"),
        Binding("left", "dec_bonus", "Dec Bonus", show=False),
        Binding("right", "inc_bonus", "Inc Bonus", show=False),
    ]

    def __init__(self, character: "Character", ability: str = "strength", default_source: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.ability = ability
        self.default_source = default_source
        self.selected_index = 0
        self.bonuses: list = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Stat Bonuses - {self.ability.upper()}", classes="title"),
            Static("↑/↓ Select  ←/→ Adjust  \\[A] Add  \\[D] Delete  \\[T] Toggle Temp  \\[Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("ACTIVE BONUSES", classes="panel-title"),
                    VerticalScroll(id="bonus-list", classes="bonus-list"),
                    classes="panel bonus-list-panel",
                ),
                Vertical(
                    Static("BONUS DETAILS", classes="panel-title"),
                    VerticalScroll(id="bonus-details", classes="bonus-details-panel"),
                    Static(""),
                    Static("COMMON SOURCES", classes="panel-title"),
                    Static("  • Magic items (e.g., Belt of Giant Strength)"),
                    Static("  • Spells (e.g., Enhance Ability, Bull's Strength)"),
                    Static("  • Blessings/Boons (DM-granted)"),
                    Static("  • Racial abilities"),
                    Static("  • Feats (e.g., Resilient)"),
                    classes="panel details-panel",
                ),
                classes="bonus-row",
            ),
            id="stat-bonus-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load bonuses."""
        self._refresh_bonuses()

    def _refresh_bonuses(self) -> None:
        """Refresh the bonus list."""
        self.bonuses = [b for b in self.character.stat_bonuses if b.ability.lower() == self.ability]

        list_widget = self.query_one("#bonus-list", VerticalScroll)
        list_widget.remove_children()

        if not self.bonuses:
            list_widget.mount(Static("  (No bonuses)", classes="no-items"))
            list_widget.mount(Static(""))
            list_widget.mount(Static("  Press \\[A] to add a bonus", classes="hint"))
        else:
            for i, bonus in enumerate(self.bonuses):
                bonus_class = "bonus-row"
                if i == self.selected_index:
                    bonus_class += " selected"

                temp_mark = " ⏱" if bonus.temporary else ""
                selector = "▶ " if i == self.selected_index else "  "

                if bonus.is_override:
                    text = f"{selector}{bonus.source}: SET TO {bonus.override_value}{temp_mark}"
                else:
                    text = f"{selector}{bonus.source}: +{bonus.bonus}{temp_mark}"

                list_widget.mount(Static(text, classes=bonus_class))

        self._refresh_details()

    def _refresh_details(self) -> None:
        """Show details of selected bonus."""
        details = self.query_one("#bonus-details", VerticalScroll)
        details.remove_children()

        if not self.bonuses or self.selected_index >= len(self.bonuses):
            details.mount(Static("  Select a bonus to see details", classes="hint"))
            return

        bonus = self.bonuses[self.selected_index]

        details.mount(Static(f"  Source: {bonus.source}", classes="bonus-source"))
        details.mount(Static(f"  Ability: {bonus.ability.upper()}", classes="bonus-ability"))

        if bonus.is_override:
            details.mount(Static(f"  Type: Override (sets to {bonus.override_value})", classes="bonus-type"))
        else:
            details.mount(Static(f"  Type: Bonus (+{bonus.bonus})", classes="bonus-type"))

        details.mount(Static(f"  Temporary: {'Yes' if bonus.temporary else 'No'}", classes="bonus-temp"))

        if bonus.duration:
            details.mount(Static(f"  Duration: {bonus.duration}", classes="bonus-duration"))

        if bonus.notes:
            details.mount(Static(""))
            details.mount(Static(f"  Notes: {bonus.notes}", classes="bonus-notes"))

    def key_up(self) -> None:
        """Move selection up."""
        if self.bonuses and self.selected_index > 0:
            self.selected_index -= 1
            self._refresh_bonuses()

    def key_down(self) -> None:
        """Move selection down."""
        if self.bonuses and self.selected_index < len(self.bonuses) - 1:
            self.selected_index += 1
            self._refresh_bonuses()

    def action_add_bonus(self) -> None:
        """Add a new bonus."""
        from dnd_manager.models.character import StatBonus

        # Create a basic new bonus
        new_bonus = StatBonus(
            source=self.default_source or "New Bonus",
            ability=self.ability,
            bonus=1,
            temporary=False,
        )
        self.character.stat_bonuses.append(new_bonus)
        self.app.save_character()
        self._refresh_bonuses()
        self.selected_index = len(self.bonuses) - 1
        self._refresh_bonuses()
        self.notify("Added new bonus - edit the source name as needed")

    def action_delete_bonus(self) -> None:
        """Delete selected bonus."""
        if not self.bonuses or self.selected_index >= len(self.bonuses):
            self.notify("No bonus selected", severity="warning")
            return

        bonus = self.bonuses[self.selected_index]
        if bonus in self.character.stat_bonuses:
            self.character.stat_bonuses.remove(bonus)
            self.app.save_character()
            self.selected_index = max(0, self.selected_index - 1)
            self._refresh_bonuses()
            self.notify(f"Removed bonus: {bonus.source}")
        else:
            self._refresh_bonuses()
            self.notify("Bonus already removed", severity="warning")

    def action_toggle_temporary(self) -> None:
        """Toggle temporary status of selected bonus."""
        if not self.bonuses or self.selected_index >= len(self.bonuses):
            self.notify("No bonus selected", severity="warning")
            return

        bonus = self.bonuses[self.selected_index]
        bonus.temporary = not bonus.temporary
        self.app.save_character()
        status = "temporary" if bonus.temporary else "permanent"
        self.notify(f"{bonus.source} is now {status}")
        self._refresh_bonuses()

    def action_inc_bonus(self) -> None:
        """Increase selected bonus value."""
        if not self.bonuses or self.selected_index >= len(self.bonuses):
            return
        bonus = self.bonuses[self.selected_index]
        if bonus.is_override:
            bonus.override_value = (bonus.override_value or 0) + 1
        else:
            bonus.bonus += 1
        self.app.save_character()
        self._refresh_bonuses()

    def action_dec_bonus(self) -> None:
        """Decrease selected bonus value."""
        if not self.bonuses or self.selected_index >= len(self.bonuses):
            return
        bonus = self.bonuses[self.selected_index]
        if bonus.is_override:
            bonus.override_value = (bonus.override_value or 0) - 1
        else:
            bonus.bonus -= 1
        self.app.save_character()
        self._refresh_bonuses()

    def action_back(self) -> None:
        """Return to ability editor."""
        self.app.pop_screen()


class HPEditorScreen(Screen):
    """Screen for editing HP values."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save"),
        Binding("h", "heal", "Heal"),
        Binding("d", "damage", "Take Damage"),
        Binding("t", "temp_hp", "Add Temp HP"),
        Binding("m", "set_max", "Set Max HP"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        hp = self.character.combat.hit_points
        yield Header()
        yield Container(
            Static("Edit Hit Points", classes="title"),
            Static("\\[H] Heal  \\[D] Damage  \\[T] Temp HP  \\[M] Set Max  \\[S] Save", classes="subtitle"),
            Vertical(
                Static(f"Current HP: {hp.current}", id="current-hp", classes="hp-display"),
                Static(f"Maximum HP: {hp.maximum}", id="max-hp", classes="hp-display"),
                Static(f"Temporary HP: {hp.temporary}", id="temp-hp", classes="hp-display"),
                Static(""),
                Horizontal(
                    Input(placeholder="Amount", id="hp-amount", type="integer"),
                    classes="hp-input-row",
                ),
                classes="panel hp-editor-panel",
            ),
            id="hp-editor-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus the input."""
        self.query_one("#hp-amount", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key - default to heal (most common action)."""
        if event.input.id == "hp-amount":
            amount = self._get_amount()
            if amount > 0:
                self.action_heal()
            else:
                self.notify("Enter an amount, then press Enter to heal or use H/D/T/M keys")

    def _get_amount(self) -> int:
        """Get the amount from the input."""
        try:
            return int(self.query_one("#hp-amount", Input).value or "0")
        except ValueError:
            return 0

    def _refresh_display(self) -> None:
        """Refresh HP display."""
        hp = self.character.combat.hit_points
        self.query_one("#current-hp", Static).update(f"Current HP: {hp.current}")
        self.query_one("#max-hp", Static).update(f"Maximum HP: {hp.maximum}")
        self.query_one("#temp-hp", Static).update(f"Temporary HP: {hp.temporary}")
        self.query_one("#hp-amount", Input).value = ""

    def action_heal(self) -> None:
        """Heal the character."""
        amount = self._get_amount()
        if amount > 0:
            hp = self.character.combat.hit_points
            hp.current = min(hp.current + amount, hp.maximum)
            self.notify(f"Healed {amount} HP")
            self._refresh_display()

    def action_damage(self) -> None:
        """Apply damage to the character."""
        amount = self._get_amount()
        if amount > 0:
            hp = self.character.combat.hit_points
            # Temp HP absorbs damage first
            if hp.temporary > 0:
                absorbed = min(hp.temporary, amount)
                hp.temporary -= absorbed
                amount -= absorbed
            hp.current = max(hp.current - amount, 0)
            self.notify(f"Took {self._get_amount()} damage")
            self._refresh_display()

    def action_temp_hp(self) -> None:
        """Add temporary HP."""
        amount = self._get_amount()
        if amount > 0:
            hp = self.character.combat.hit_points
            hp.temporary = max(hp.temporary, amount)  # Temp HP doesn't stack
            self.notify(f"Added {amount} temporary HP")
            self._refresh_display()

    def action_set_max(self) -> None:
        """Set maximum HP."""
        amount = self._get_amount()
        if amount > 0:
            hp = self.character.combat.hit_points
            hp.maximum = amount
            hp.current = min(hp.current, hp.maximum)
            self.notify(f"Max HP set to {amount}")
            self._refresh_display()

    def action_save(self) -> None:
        """Save and go back."""
        self.app.save_character()
        self.notify("HP saved!")
        self.app.pop_screen()

    def action_back(self) -> None:
        """Go back."""
        self.app.pop_screen()


class AbilityPickScreen(ListNavigationMixin, Screen):
    """Pick an ability for applying a stat bonus."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "select", "Select"),
        Binding("up", "up", "Up", show=False),
        Binding("down", "down", "Down", show=False),
    ]

    def __init__(self, character: "Character", default_source: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.default_source = default_source
        self.abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        self.selected_index = 0
        self._last_letter = ""
        self._last_letter_index = -1

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Choose Ability", classes="title"),
            Static("↑/↓ Select  Enter Apply  Esc Back", classes="subtitle"),
            VerticalScroll(id="ability-pick-list", classes="bonus-list"),
            id="ability-pick-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_list()

    def _refresh_list(self) -> None:
        list_widget = self.query_one("#ability-pick-list", VerticalScroll)
        list_widget.remove_children()
        for i, ability in enumerate(self.abilities):
            label = ability.title()
            classes = "bonus-row"
            if i == self.selected_index:
                classes += " selected"
            list_widget.mount(ClickableListItem(f"  {label}", index=i, classes=classes))

    def action_up(self) -> None:
        self._navigate_up()

    def action_down(self) -> None:
        self._navigate_down()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        self.selected_index = event.index
        self._refresh_list()

    def action_select(self) -> None:
        ability = self.abilities[self.selected_index]
        self.app.push_screen(StatBonusScreen(self.character, ability, default_source=self.default_source))

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.abilities

    def _get_item_name(self, item) -> str:
        return item

    def _get_scroll_container(self):
        try:
            return self.query_one("#ability-pick-list", VerticalScroll)
        except NoMatches:
            return None

    def _update_selection(self) -> None:
        self._refresh_list()

    def _get_item_widget_class(self) -> str:
        return "bonus-row"

    def action_back(self) -> None:
        self.app.pop_screen()


class InfoEditorScreen(Screen):
    """Screen for editing character info (name, alignment)."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save"),
        Binding("up", "prev_alignment", "Prev Alignment", show=False),
        Binding("down", "next_alignment", "Next Alignment", show=False),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.edited_name = character.name
        self.edited_alignment = character.alignment
        self._alignments = list(Alignment)
        self._alignment_index = self._alignments.index(character.alignment)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Edit Character Info", classes="title"),
            Static("\\[S] Save  \\[Esc] Cancel", classes="subtitle"),
            Vertical(
                Static("Name:", classes="panel-title"),
                Input(value=self.character.name, id="name-input"),
                Static(""),
                Static("Alignment: (use ↑↓ to change)", classes="panel-title"),
                Static(self.edited_alignment.display_name, id="alignment-display", classes="hp-display"),
                Static(""),
                Static(f"Class: {self.character.primary_class.name} {self.character.primary_class.level}", classes="hint"),
                Static(f"{self.character.get_species_term()}: {self.character.species or 'Not set'}", classes="hint"),
                Static(f"Background: {self.character.background or 'Not set'}", classes="hint"),
                classes="panel hp-editor-panel",
            ),
            id="editor-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus the name input."""
        self.query_one("#name-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Track name changes."""
        if event.input.id == "name-input":
            self.edited_name = event.value

    def action_prev_alignment(self) -> None:
        """Cycle to previous alignment."""
        self._alignment_index = (self._alignment_index - 1) % len(self._alignments)
        self.edited_alignment = self._alignments[self._alignment_index]
        self.query_one("#alignment-display", Static).update(self.edited_alignment.display_name)

    def action_next_alignment(self) -> None:
        """Cycle to next alignment."""
        self._alignment_index = (self._alignment_index + 1) % len(self._alignments)
        self.edited_alignment = self._alignments[self._alignment_index]
        self.query_one("#alignment-display", Static).update(self.edited_alignment.display_name)

    def action_save(self) -> None:
        """Save character info changes."""
        name = self.edited_name.strip()
        if not name:
            self.notify("Name cannot be empty", severity="error")
            return

        self.character.name = name
        self.character.alignment = self.edited_alignment
        self.app.save_character()
        self.notify("Character info saved!")
        self.app.pop_screen()

    def action_back(self) -> None:
        """Go back without saving."""
        self.app.pop_screen()


class CurrencyEditorScreen(Screen):
    """Screen for managing currency (gold, silver, copper, etc.)."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save"),
    ]

    def __init__(self, character: "Character", on_save: Optional[Callable] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.on_save = on_save
        # Track edited values
        self.edited_currency = {
            "pp": character.equipment.currency.pp,
            "gp": character.equipment.currency.gp,
            "ep": character.equipment.currency.ep,
            "sp": character.equipment.currency.sp,
            "cp": character.equipment.currency.cp,
        }

    def compose(self) -> ComposeResult:
        c = self.character.equipment.currency
        yield Header()
        yield Container(
            Static("Manage Currency", classes="title"),
            Static("\\[S] Save  \\[Esc] Cancel", classes="subtitle"),
            Vertical(
                Horizontal(
                    Static("Platinum (pp):", classes="currency-label"),
                    Input(value=str(c.pp), id="input-pp", type="integer"),
                    classes="currency-input-row",
                ),
                Horizontal(
                    Static("Gold (gp):    ", classes="currency-label"),
                    Input(value=str(c.gp), id="input-gp", type="integer"),
                    classes="currency-input-row",
                ),
                Horizontal(
                    Static("Electrum (ep):", classes="currency-label"),
                    Input(value=str(c.ep), id="input-ep", type="integer"),
                    classes="currency-input-row",
                ),
                Horizontal(
                    Static("Silver (sp):  ", classes="currency-label"),
                    Input(value=str(c.sp), id="input-sp", type="integer"),
                    classes="currency-input-row",
                ),
                Horizontal(
                    Static("Copper (cp):  ", classes="currency-label"),
                    Input(value=str(c.cp), id="input-cp", type="integer"),
                    classes="currency-input-row",
                ),
                Static("", classes="spacer"),
                Static(id="total-display", classes="currency-total"),
                classes="panel currency-editor-panel",
            ),
            id="currency-editor-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus first input and update total."""
        self.query_one("#input-pp", Input).focus()
        self._update_total()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes - update total display."""
        self._update_total()

    def _update_total(self) -> None:
        """Update the total gold value display."""
        try:
            pp = int(self.query_one("#input-pp", Input).value or 0)
            gp = int(self.query_one("#input-gp", Input).value or 0)
            ep = int(self.query_one("#input-ep", Input).value or 0)
            sp = int(self.query_one("#input-sp", Input).value or 0)
            cp = int(self.query_one("#input-cp", Input).value or 0)

            total = (pp * 10) + gp + (ep * 0.5) + (sp * 0.1) + (cp * 0.01)
            self.query_one("#total-display", Static).update(f"Total value: {total:.2f} gp")
        except (ValueError, Exception):
            pass

    def action_save(self) -> None:
        """Save currency changes."""
        try:
            pp = max(0, int(self.query_one("#input-pp", Input).value or 0))
            gp = max(0, int(self.query_one("#input-gp", Input).value or 0))
            ep = max(0, int(self.query_one("#input-ep", Input).value or 0))
            sp = max(0, int(self.query_one("#input-sp", Input).value or 0))
            cp = max(0, int(self.query_one("#input-cp", Input).value or 0))

            self.character.equipment.currency.pp = pp
            self.character.equipment.currency.gp = gp
            self.character.equipment.currency.ep = ep
            self.character.equipment.currency.sp = sp
            self.character.equipment.currency.cp = cp

            self.notify("Currency updated!")
            if self.on_save:
                self.on_save()
            self.app.pop_screen()
        except ValueError:
            self.notify("Invalid currency values", severity="error")

    def action_back(self) -> None:
        """Go back without saving."""
        self.app.pop_screen()
