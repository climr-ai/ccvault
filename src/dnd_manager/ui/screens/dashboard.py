"""Dashboard screens for the D&D Manager application."""

from typing import TYPE_CHECKING, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Static

from dnd_manager.config import get_config_manager
from dnd_manager.data import (
    get_skill_description,
    get_weapon_mastery_for_weapon,
    get_weapon_mastery_summary,
)
from dnd_manager.models.character import RulesetId
from dnd_manager.ui.screens.base import ListNavigationMixin, ScreenContextMixin, apply_item_order
from dnd_manager.ui.screens.panels import (
    AbilityBlock,
    ActionsPane,
    CharacterInfo,
    CombatStats,
    DashboardPanel,
    FeatsPane,
    InventoryPane,
    KnownSpells,
    PreparedSpells,
    QuickActions,
    SkillList,
    SpellSlots,
    WeaponsPane,
    is_weapon_proficient,
)
from dnd_manager.ui.screens.widgets import ClickableListItem

if TYPE_CHECKING:
    from dnd_manager.models.character import Character


# Panel definitions for dashboard layout
PANE_DEFS = {
    "abilities": ("Abilities", AbilityBlock, "panel ability-panel"),
    "character": ("Character", CharacterInfo, "panel char-info-panel"),
    "combat": ("Combat", CombatStats, "panel combat-panel"),
    "shortcuts": ("Shortcuts", QuickActions, "panel actions-panel"),
    "skills": ("Skills", SkillList, "panel skills-panel"),
    "spell_slots": ("Spell Slots", SpellSlots, "panel spells-panel"),
    "prepared_spells": ("Prepared Spells", PreparedSpells, "panel prepared-panel"),
    "known_spells": ("Known Spells", KnownSpells, "panel prepared-panel"),
    "weapons": ("Weapons", WeaponsPane, "panel skills-panel"),
    "feats": ("Feats", FeatsPane, "panel skills-panel"),
    "inventory": ("Inventory", InventoryPane, "panel skills-panel"),
    "actions": ("Actions", ActionsPane, "panel skills-panel"),
}

DASHBOARD_LAYOUT_PRESETS = {
    "balanced": {
        "label": "Balanced",
        "rows": [
            ["abilities", "character", "combat", "shortcuts"],
            ["skills", "spell_slots", "prepared_spells"],
        ],
    },
    "spellcaster": {
        "label": "Spellcaster",
        "rows": [
            ["abilities", "character", "combat", "shortcuts"],
            ["skills", "spell_slots", "known_spells"],
        ],
    },
    "martial": {
        "label": "Martial",
        "rows": [
            ["abilities", "character", "combat", "shortcuts"],
            ["skills", "weapons", "feats"],
        ],
    },
    "wide": {
        "label": "Wide",
        "rows": [
            ["abilities", "character", "combat", "shortcuts", "skills"],
            ["weapons", "feats", "inventory", "spell_slots", "prepared_spells"],
        ],
    },
}

ORDERABLE_PANELS = {
    "weapons": "Weapons",
    "skills": "Skills",
    "feats": "Feats",
    "inventory": "Inventory",
    "known_spells": "Known Spells",
    "prepared_spells": "Prepared Spells",
}


class MainDashboard(ScreenContextMixin, Screen):
    """Main character dashboard screen."""

    BINDINGS = [
        Binding("tab", "next_pane", "Next Pane"),
        Binding("shift+tab", "prev_pane", "Prev Pane"),
        Binding("backtab", "prev_pane", "Prev Pane"),
        Binding("up", "pane_up", "Up", show=False, priority=True),
        Binding("down", "pane_down", "Down", show=False, priority=True),
        Binding("enter", "pane_select", "Select", show=False),
        Binding("escape", "back", "Back"),
        Binding("q", "home", "Home"),
        Binding("?", "help", "Help"),
        Binding("v", "layout", "Layout"),
        Binding("o", "order", "Order"),
        Binding("m", "mastery", "Mastery"),
        Binding("s", "spells", "Spells"),
        Binding("i", "inventory", "Inventory"),
        Binding("f", "features", "Features"),
        Binding("n", "notes", "Notes"),
        Binding("a", "ai_chat", "AI Chat"),
        Binding("r", "roll", "Roll Dice"),
        Binding("e", "edit", "Edit"),
        Binding("l", "level", "Level"),
        Binding("h", "homebrew", "Homebrew"),
        Binding(".", "settings", "Settings"),
        Binding("t", "short_rest", "Short Rest"),
        Binding("T", "long_rest", "Long Rest"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+n", "new_character", "New"),
        Binding("ctrl+o", "open_character", "Open"),
        Binding("ctrl+r", "resume_draft", "Resume Draft"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self._pane_focus_index = 0

    def get_ai_context(self) -> dict:
        """Provide character context for AI."""
        c = self.character
        return {
            "screen_type": "Character Dashboard",
            "description": f"Viewing {c.name}'s character sheet",
            "character": {
                "name": c.name,
                "class": c.primary_class.name if c.primary_class else None,
                "level": c.primary_class.level if c.primary_class else 1,
                "species": c.species,
                "background": c.background,
                "hp": f"{c.combat.hit_points.current}/{c.combat.hit_points.maximum}",
                "abilities": {
                    "str": c.abilities.strength.total,
                    "dex": c.abilities.dexterity.total,
                    "con": c.abilities.constitution.total,
                    "int": c.abilities.intelligence.total,
                    "wis": c.abilities.wisdom.total,
                    "cha": c.abilities.charisma.total,
                },
            },
            "character_obj": c,
        }

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            *self._build_dashboard_rows(),
            id="dashboard",
        )
        yield Footer()

    def _get_layout_state(self) -> tuple[str, list[str] | None]:
        """Resolve dashboard layout and optional panels override."""
        config = get_config_manager().config
        layout = self.character.meta.dashboard_layout or config.ui.dashboard_layout or "balanced"
        panels = self.character.meta.dashboard_panels
        if panels is None:
            panels = config.ui.dashboard_panels
        return layout, panels

    def _build_dashboard_rows(self) -> list[Horizontal]:
        """Build dashboard rows based on layout settings."""
        layout_name, panels = self._get_layout_state()
        if panels:
            layout_name = "custom"

        if layout_name in DASHBOARD_LAYOUT_PRESETS:
            rows = DASHBOARD_LAYOUT_PRESETS[layout_name]["rows"]
        else:
            panels = panels or DASHBOARD_LAYOUT_PRESETS["balanced"]["rows"][0] + DASHBOARD_LAYOUT_PRESETS["balanced"]["rows"][1]
            rows = [panels[:4], panels[4:8]]

        row_widgets: list[Horizontal] = []
        self._pane_order: list[DashboardPanel] = []
        for idx, row in enumerate(rows):
            widgets = []
            for pane_id in row:
                pane_def = PANE_DEFS.get(pane_id)
                if not pane_def:
                    continue
                _, pane_cls, pane_classes = pane_def
                pane = pane_cls(character=self.character, pane_id=pane_id, classes=pane_classes)
                widgets.append(pane)
                self._pane_order.append(pane)
            row_class = "top-row" if idx == 0 else "bottom-row"
            if layout_name == "wide":
                row_class = "wide-row"
            row_widgets.append(Horizontal(*widgets, classes=row_class))
        return row_widgets

    def on_mount(self) -> None:
        """Focus the first pane on mount."""
        self._focus_pane(0)

    def _focus_pane(self, index: int) -> None:
        if not getattr(self, "_pane_order", None):
            return
        self._pane_focus_index = max(0, min(len(self._pane_order) - 1, index))
        pane = self._pane_order[self._pane_focus_index]
        try:
            pane.focus()
        except (NoMatches, AttributeError):
            # Widget may not be mounted or focusable
            pass

    def action_save(self) -> None:
        """Save the current character."""
        self.app.save_character()
        self.notify("Character saved!", severity="information")

    def action_new_character(self) -> None:
        """Create a new character."""
        self.app.action_new_character()

    def action_open_character(self) -> None:
        """Open an existing character."""
        self.app.action_open_character(return_to_dashboard=True)

    def action_back(self) -> None:
        """Return to the previous screen."""
        self.app.pop_screen()

    def action_home(self) -> None:
        """Return to the welcome screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.navigation import WelcomeScreen

        while len(self.app.screen_stack) > 1 and not isinstance(self.app.screen, WelcomeScreen):
            self.app.pop_screen()
        if not isinstance(self.app.screen, WelcomeScreen):
            self.app.push_screen(WelcomeScreen())

    def action_next_pane(self) -> None:
        """Move focus to next pane."""
        if not getattr(self, "_pane_order", None):
            return
        next_index = (self._pane_focus_index + 1) % len(self._pane_order)
        self._focus_pane(next_index)

    def action_prev_pane(self) -> None:
        """Move focus to previous pane."""
        if not getattr(self, "_pane_order", None):
            return
        next_index = (self._pane_focus_index - 1) % len(self._pane_order)
        self._focus_pane(next_index)

    def action_pane_up(self) -> None:
        """Move selection up within focused pane."""
        pane = self._pane_order[self._pane_focus_index] if getattr(self, "_pane_order", None) else None
        if pane:
            pane.move_selection(-1)

    def action_pane_down(self) -> None:
        """Move selection down within focused pane."""
        pane = self._pane_order[self._pane_focus_index] if getattr(self, "_pane_order", None) else None
        if pane:
            pane.move_selection(1)

    def action_pane_select(self) -> None:
        """Open detail overlay for selected item or trigger quick action."""
        pane = self._pane_order[self._pane_focus_index] if getattr(self, "_pane_order", None) else None
        if not pane:
            return
        if pane.pane_id == "shortcuts":
            action = pane.get_selected_item()
            if not action:
                return
            label, key = action
            key = key.lower()
            if key == "s":
                self.action_spells()
            elif key == "i":
                self.action_inventory()
            elif key == "f":
                self.action_features()
            elif key == "n":
                self.action_notes()
            elif key == "a":
                self.action_ai_chat()
            elif key == "r":
                self.action_roll()
            elif key == "h":
                self.action_homebrew()
            elif key == "m":
                self.action_mastery()
            elif key == "e":
                self.action_edit()
            return

        item = pane.get_selected_item()
        if item is None:
            return
        self.app.push_screen(DetailOverlay(self.character, pane.pane_id, item))

    def on_clickable_list_item_activated(self, event: ClickableListItem.Activated) -> None:
        """Open details on double-click."""
        pane = event.control
        while pane and not isinstance(pane, DashboardPanel):
            pane = pane.parent
        if not pane:
            return
        if getattr(self, "_pane_order", None) and pane in self._pane_order:
            self._focus_pane(self._pane_order.index(pane))
        self.action_pane_select()
        event.stop()

    def action_resume_draft(self) -> None:
        """Resume character creation draft."""
        from dnd_manager.storage.yaml_store import get_default_draft_store

        # Lazy import to avoid circular dependency
        from dnd_manager.app import CharacterCreationScreen

        draft_data = get_default_draft_store().load_draft()
        if draft_data:
            self.app.push_screen(CharacterCreationScreen(draft_data=draft_data))
            self.notify(f"Resuming: {draft_data.get('name', 'Unknown')}")
        else:
            self.notify("No draft found", severity="warning")

    def action_layout(self) -> None:
        """Open dashboard layout settings."""
        self.app.push_screen(DashboardLayoutScreen(self.character))

    def action_order(self) -> None:
        """Open per-panel ordering screen."""
        self.app.push_screen(PanelOrderScreen(self.character))

    def action_mastery(self) -> None:
        """Open weapon mastery selection."""
        self.app.push_screen(WeaponMasteryScreen(self.character))

    def action_spells(self) -> None:
        """Open spells screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.gameplay import SpellsScreen
        self.app.push_screen(SpellsScreen(self.character))

    def action_inventory(self) -> None:
        """Open inventory screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.gameplay import InventoryScreen
        self.app.push_screen(InventoryScreen(self.character))

    def action_features(self) -> None:
        """Open features screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.gameplay import FeaturesScreen
        self.app.push_screen(FeaturesScreen(self.character))

    def action_notes(self) -> None:
        """Open notes screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.notes import NotesScreen
        self.app.push_screen(NotesScreen(self.character))

    def action_ai_chat(self) -> None:
        """Open AI assistant."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.ai import AIOverlayScreen
        context = {
            "screen_type": "Character Dashboard",
            "description": f"Viewing {self.character.name}'s character sheet",
            "character": {
                "name": self.character.name,
                "class": self.character.primary_class.name if self.character.primary_class else "Unknown",
                "level": self.character.total_level,
            },
            "character_obj": self.character,
        }
        self.app.push_screen(AIOverlayScreen(screen_context=context))

    def action_roll(self) -> None:
        """Open dice roller."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.utility import DiceRollerScreen
        self.app.push_screen(DiceRollerScreen(self.character))

    def action_edit(self) -> None:
        """Edit character."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.editors import CharacterEditorScreen
        self.app.push_screen(CharacterEditorScreen(self.character))

    def action_level(self) -> None:
        """Open level management screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.level import LevelManagementScreen
        self.app.push_screen(LevelManagementScreen(self.character))

    def action_help(self) -> None:
        """Show help."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.utility import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_homebrew(self) -> None:
        """Open homebrew guidelines screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.ai import HomebrewScreen
        self.app.push_screen(HomebrewScreen(self.character))

    def action_settings(self) -> None:
        """Open settings screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.utility import SettingsScreen
        self.app.push_screen(SettingsScreen())

    def action_short_rest(self) -> None:
        """Open short rest screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.rest import ShortRestScreen
        self.app.push_screen(ShortRestScreen(self.character))

    def action_long_rest(self) -> None:
        """Open long rest screen."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.rest import LongRestScreen
        self.app.push_screen(LongRestScreen(self.character))


class DashboardLayoutScreen(Screen):
    """Configure dashboard layout presets and panels."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("tab", "switch_column", "Switch Column"),
        Binding("up", "up", "Up", show=False),
        Binding("down", "down", "Down", show=False),
        Binding("enter", "select", "Select/Toggle"),
        Binding("space", "select", "Select/Toggle"),
        Binding("g", "apply_global", "Apply Global"),
        Binding("c", "apply_character", "Apply Character"),
        Binding("r", "reset_character", "Reset Character"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_column = "layouts"  # layouts | panes
        self.layout_index = 0
        self.pane_index = 0
        self.layout_names = list(DASHBOARD_LAYOUT_PRESETS.keys()) + ["custom"]
        self.pane_ids = list(PANE_DEFS.keys())
        self.current_layout, self.current_panels = self._load_current_settings()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Dashboard Layout", classes="title"),
            Static("Tab switch column • Enter/Space select • G global • C character • R reset", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("LAYOUTS", classes="panel-title"),
                    VerticalScroll(id="layout-list", classes="settings-list"),
                    classes="panel settings-panel",
                ),
                Vertical(
                    Static("PANES", classes="panel-title"),
                    VerticalScroll(id="pane-list", classes="settings-list"),
                    classes="panel settings-panel",
                ),
                classes="settings-row",
            ),
            id="layout-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._sync_indices()
        self._refresh_lists()

    def _load_current_settings(self) -> tuple[str, list[str]]:
        config = get_config_manager().config
        layout = self.character.meta.dashboard_layout or config.ui.dashboard_layout or "balanced"
        panels = self.character.meta.dashboard_panels
        if panels is None:
            panels = config.ui.dashboard_panels
        if panels:
            return "custom", list(panels)
        preset = DASHBOARD_LAYOUT_PRESETS.get(layout)
        if preset:
            flat = [p for row in preset["rows"] for p in row]
            return layout, flat
        flat = [p for row in DASHBOARD_LAYOUT_PRESETS["balanced"]["rows"] for p in row]
        return "balanced", flat

    def _sync_indices(self) -> None:
        if self.current_layout in self.layout_names:
            self.layout_index = self.layout_names.index(self.current_layout)

    def _refresh_lists(self) -> None:
        self._refresh_layout_list()
        self._refresh_pane_list()

    def _refresh_layout_list(self) -> None:
        list_widget = self.query_one("#layout-list", VerticalScroll)
        list_widget.remove_children()
        for i, layout in enumerate(self.layout_names):
            label = DASHBOARD_LAYOUT_PRESETS.get(layout, {}).get("label", "Custom")
            selector = "▶ " if self.selected_column == "layouts" and i == self.layout_index else "  "
            check = "✓" if layout == self.current_layout else "○"
            list_widget.mount(Static(f"{selector}[{check}] {label}", classes="setting-row"))

    def _refresh_pane_list(self) -> None:
        list_widget = self.query_one("#pane-list", VerticalScroll)
        list_widget.remove_children()
        for i, pane_id in enumerate(self.pane_ids):
            label = PANE_DEFS[pane_id][0]
            selector = "▶ " if self.selected_column == "panes" and i == self.pane_index else "  "
            check = "✓" if pane_id in self.current_panels else "○"
            list_widget.mount(Static(f"{selector}[{check}] {label}", classes="setting-row"))

    def action_switch_column(self) -> None:
        self.selected_column = "panes" if self.selected_column == "layouts" else "layouts"
        self._refresh_lists()

    def action_up(self) -> None:
        if self.selected_column == "layouts":
            self.layout_index = (self.layout_index - 1) % len(self.layout_names)
        else:
            self.pane_index = (self.pane_index - 1) % len(self.pane_ids)
        self._refresh_lists()

    def action_down(self) -> None:
        if self.selected_column == "layouts":
            self.layout_index = (self.layout_index + 1) % len(self.layout_names)
        else:
            self.pane_index = (self.pane_index + 1) % len(self.pane_ids)
        self._refresh_lists()

    def action_select(self) -> None:
        if self.selected_column == "layouts":
            chosen = self.layout_names[self.layout_index]
            if chosen != "custom":
                preset = DASHBOARD_LAYOUT_PRESETS[chosen]
                self.current_panels = [p for row in preset["rows"] for p in row]
            self.current_layout = chosen
        else:
            pane = self.pane_ids[self.pane_index]
            if pane in self.current_panels:
                self.current_panels.remove(pane)
            else:
                self.current_panels.append(pane)
            self.current_layout = "custom"
        self._refresh_lists()

    def action_apply_global(self) -> None:
        config = get_config_manager().config
        if self.current_layout == "custom":
            config.ui.dashboard_layout = "custom"
            config.ui.dashboard_panels = list(self.current_panels)
        else:
            config.ui.dashboard_layout = self.current_layout
            config.ui.dashboard_panels = None
        config.save()
        self.notify("Saved as global default", severity="information")
        self._close_and_refresh_dashboard()

    def action_apply_character(self) -> None:
        if self.current_layout == "custom":
            self.character.meta.dashboard_layout = "custom"
            self.character.meta.dashboard_panels = list(self.current_panels)
        else:
            self.character.meta.dashboard_layout = self.current_layout
            self.character.meta.dashboard_panels = None
        self.app.save_character()
        self.notify("Saved for this character", severity="information")
        self._close_and_refresh_dashboard()

    def action_reset_character(self) -> None:
        self.character.meta.dashboard_layout = None
        self.character.meta.dashboard_panels = None
        self.app.save_character()
        self.notify("Character override cleared", severity="information")
        self._close_and_refresh_dashboard()

    def _close_and_refresh_dashboard(self) -> None:
        self.app.pop_screen()
        self.app.pop_screen()
        self.app.push_screen(MainDashboard(self.character))

    def action_back(self) -> None:
        self.app.pop_screen()


class WeaponMasteryScreen(ListNavigationMixin, Screen):
    """Screen for selecting weapon masteries."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("up", "up", "Up", show=False),
        Binding("down", "down", "Down", show=False),
        Binding("space", "toggle", "Toggle"),
        Binding("enter", "toggle", "Toggle"),
        Binding("c", "clear", "Clear"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_index = 0
        self._last_letter = ""
        self._last_letter_index = -1
        self.available_weapons: list = []
        self.mastery_limit = self.character.get_weapon_mastery_limit()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Weapon Mastery", classes="title"),
            Static(id="mastery-count", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("WEAPONS", classes="panel-title"),
                    VerticalScroll(id="mastery-weapon-list", classes="feat-browser-list"),
                    classes="panel browser-panel",
                ),
                Vertical(
                    Static("DETAILS", classes="panel-title"),
                    VerticalScroll(id="mastery-details", classes="feat-details"),
                    classes="panel browser-panel",
                ),
                classes="browser-row",
            ),
            id="mastery-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_weapon_list()

    def _update_count(self) -> None:
        count = len(self.character.weapon_masteries)
        limit = self.mastery_limit
        suffix = f"{count}/{limit} selected" if limit else "No mastery available"
        self.query_one("#mastery-count", Static).update(suffix)

    def _refresh_weapon_list(self) -> None:
        from dnd_manager.data import ALL_WEAPONS

        list_widget = self.query_one("#mastery-weapon-list", VerticalScroll)
        list_widget.remove_children()
        self.mastery_limit = self.character.get_weapon_mastery_limit()

        if self.mastery_limit <= 0:
            list_widget.mount(Static("  (No weapon mastery for this character)", classes="no-items"))
            self._refresh_details()
            self._update_count()
            return

        weapons = []
        for weapon in ALL_WEAPONS:
            if get_weapon_mastery_for_weapon(weapon.name) and is_weapon_proficient(self.character, weapon):
                weapons.append(weapon)
        weapons.sort(key=lambda w: w.name)
        self.available_weapons = weapons

        # Drop invalid selections
        valid_names = {w.name for w in weapons}
        self.character.weapon_masteries = [w for w in self.character.weapon_masteries if w in valid_names]

        if not weapons:
            list_widget.mount(Static("  (No eligible weapons)", classes="no-items"))
            self._refresh_details()
            self._update_count()
            return

        self.selected_index = min(self.selected_index, len(weapons) - 1)
        owned = {i.name for i in self.character.equipment.items}

        for i, weapon in enumerate(weapons):
            checked = "x" if weapon.name in self.character.weapon_masteries else " "
            marker = "★" if weapon.name in owned else " "
            row = f"  [{checked}] {marker} {weapon.name}"
            row_class = "feat-row"
            if i == self.selected_index:
                row_class += " selected"
            list_widget.mount(ClickableListItem(row, index=i, classes=row_class))

        self._refresh_details()
        self._update_count()

    def _refresh_details(self) -> None:
        details = self.query_one("#mastery-details", VerticalScroll)
        details.remove_children()
        if not self.available_weapons:
            return

        weapon = self.available_weapons[self.selected_index]
        mastery = get_weapon_mastery_for_weapon(weapon.name)
        summary = get_weapon_mastery_summary(mastery) if mastery else None

        details.mount(Static(weapon.name, classes="panel-title"))
        details.mount(Static(f"Damage: {weapon.damage} {weapon.damage_type}"))
        if weapon.properties:
            details.mount(Static("Properties: " + ", ".join(weapon.properties)))
        if weapon.range_normal:
            if weapon.range_long:
                details.mount(Static(f"Range: {weapon.range_normal}/{weapon.range_long}"))
            else:
                details.mount(Static(f"Range: {weapon.range_normal}"))
        if mastery:
            details.mount(Static(f"Mastery: {mastery}"))
            if summary:
                details.mount(Static(summary))

    def action_toggle(self) -> None:
        if self.mastery_limit <= 0 or not self.available_weapons:
            return
        weapon = self.available_weapons[self.selected_index]
        if weapon.name in self.character.weapon_masteries:
            self.character.weapon_masteries.remove(weapon.name)
        else:
            if len(self.character.weapon_masteries) >= self.mastery_limit:
                self.notify(f"Select up to {self.mastery_limit} weapons", severity="warning")
                return
            self.character.weapon_masteries.append(weapon.name)
        self.app.save_character()
        self._refresh_weapon_list()

    def action_clear(self) -> None:
        if not self.character.weapon_masteries:
            return
        self.character.weapon_masteries = []
        self.app.save_character()
        self._refresh_weapon_list()

    def action_up(self) -> None:
        self._navigate_up()

    def action_down(self) -> None:
        self._navigate_down()

    def on_key(self, event) -> None:
        if self._handle_key_for_letter_jump(event.key):
            event.prevent_default()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        self.selected_index = event.index
        self._refresh_weapon_list()

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.available_weapons

    def _get_item_name(self, item) -> str:
        return item.name

    def _get_scroll_container(self):
        try:
            return self.query_one("#mastery-weapon-list", VerticalScroll)
        except NoMatches:
            return None

    def _update_selection(self) -> None:
        self._refresh_weapon_list()

    def _get_item_widget_class(self) -> str:
        return "feat-row"

    def action_back(self) -> None:
        self.app.pop_screen()


class PanelOrderScreen(Screen):
    """Reorder items within dashboard panels."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("tab", "switch_column", "Switch Column"),
        Binding("up", "up", "Up", show=False),
        Binding("down", "down", "Down", show=False),
        Binding("[", "move_up", "Move Up"),
        Binding("]", "move_down", "Move Down"),
        Binding("r", "reset_order", "Reset"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.panel_ids = list(ORDERABLE_PANELS.keys())
        self.selected_panel_index = 0
        self.selected_item_index = 0
        self.active_column = "panels"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Reorder Panel Items", classes="title"),
            Static("Tab switch column • [ ] move item • R reset • Esc back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("PANELS", classes="panel-title"),
                    VerticalScroll(id="order-panel-list", classes="order-list"),
                    classes="panel browser-panel",
                ),
                Vertical(
                    Static("ITEMS", classes="panel-title"),
                    VerticalScroll(id="order-item-list", classes="order-list"),
                    classes="panel browser-panel",
                ),
                classes="browser-row",
            ),
            id="order-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_panels()
        self._refresh_items()

    def _get_panel_id(self) -> str:
        if not self.panel_ids:
            return ""
        return self.panel_ids[self.selected_panel_index]

    def _get_panel_items(self, panel_id: str) -> list[str]:
        from dnd_manager.data import get_weapon_by_name
        from dnd_manager.models.abilities import Skill

        if panel_id == "weapons":
            items = [i.name for i in self.character.equipment.items if get_weapon_by_name(i.name)]
        elif panel_id == "skills":
            items = [s.display_name for s in Skill]
        elif panel_id == "feats":
            items = [f.name for f in self.character.features if f.source == "feat"]
        elif panel_id == "inventory":
            items = [i.name for i in self.character.equipment.items]
        elif panel_id == "known_spells":
            items = list(self.character.spellcasting.known)
        elif panel_id == "prepared_spells":
            items = list(self.character.spellcasting.prepared)
        else:
            items = []
        return items

    def _normalize_order(self, panel_id: str, items: list[str]) -> list[str]:
        order = self.character.meta.panel_item_orders.get(panel_id, [])
        return apply_item_order(items, order, lambda s: s)

    def _save_order(self, panel_id: str, items: list[str]) -> None:
        self.character.meta.panel_item_orders[panel_id] = list(items)
        self.app.save_character()

    def _refresh_panels(self) -> None:
        panel_list = self.query_one("#order-panel-list", VerticalScroll)
        panel_list.remove_children()
        for i, panel_id in enumerate(self.panel_ids):
            label = ORDERABLE_PANELS[panel_id]
            classes = "order-row order-panel-row"
            if i == self.selected_panel_index and self.active_column == "panels":
                classes += " selected"
            panel_list.mount(ClickableListItem(f"  {label}", index=i, classes=classes))

    def _refresh_items(self) -> None:
        item_list = self.query_one("#order-item-list", VerticalScroll)
        item_list.remove_children()
        panel_id = self._get_panel_id()
        items = self._normalize_order(panel_id, self._get_panel_items(panel_id))
        if not items:
            item_list.mount(Static("  (No items)", classes="no-items"))
            return
        self.selected_item_index = min(self.selected_item_index, max(0, len(items) - 1))
        for i, item in enumerate(items):
            classes = "order-row order-item-row"
            if i == self.selected_item_index and self.active_column == "items":
                classes += " selected"
            item_list.mount(ClickableListItem(f"  {item}", index=i, classes=classes))

    def action_switch_column(self) -> None:
        self.active_column = "items" if self.active_column == "panels" else "panels"
        self._refresh_panels()
        self._refresh_items()

    def action_up(self) -> None:
        if self.active_column == "panels":
            self.selected_panel_index = max(0, self.selected_panel_index - 1)
            self.selected_item_index = 0
            self._refresh_panels()
            self._refresh_items()
        else:
            self.selected_item_index = max(0, self.selected_item_index - 1)
            self._refresh_items()

    def action_down(self) -> None:
        if self.active_column == "panels":
            self.selected_panel_index = min(len(self.panel_ids) - 1, self.selected_panel_index + 1)
            self.selected_item_index = 0
            self._refresh_panels()
            self._refresh_items()
        else:
            panel_id = self._get_panel_id()
            items = self._normalize_order(panel_id, self._get_panel_items(panel_id))
            self.selected_item_index = min(len(items) - 1, self.selected_item_index + 1)
            self._refresh_items()

    def action_move_up(self) -> None:
        if self.active_column != "items":
            return
        panel_id = self._get_panel_id()
        items = self._normalize_order(panel_id, self._get_panel_items(panel_id))
        if self.selected_item_index <= 0:
            return
        items[self.selected_item_index - 1], items[self.selected_item_index] = (
            items[self.selected_item_index],
            items[self.selected_item_index - 1],
        )
        self.selected_item_index -= 1
        self._save_order(panel_id, items)
        self._refresh_items()

    def action_move_down(self) -> None:
        if self.active_column != "items":
            return
        panel_id = self._get_panel_id()
        items = self._normalize_order(panel_id, self._get_panel_items(panel_id))
        if self.selected_item_index >= len(items) - 1:
            return
        items[self.selected_item_index + 1], items[self.selected_item_index] = (
            items[self.selected_item_index],
            items[self.selected_item_index + 1],
        )
        self.selected_item_index += 1
        self._save_order(panel_id, items)
        self._refresh_items()

    def action_reset_order(self) -> None:
        panel_id = self._get_panel_id()
        if panel_id in self.character.meta.panel_item_orders:
            del self.character.meta.panel_item_orders[panel_id]
            self.app.save_character()
        self._refresh_items()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        if "order-panel-row" in event.sender.classes:
            self.selected_panel_index = event.index
            self.selected_item_index = 0
            self.active_column = "panels"
            self._refresh_panels()
            self._refresh_items()
        elif "order-item-row" in event.sender.classes:
            self.selected_item_index = event.index
            self.active_column = "items"
            self._refresh_items()
            self._refresh_panels()

    def action_back(self) -> None:
        self.app.pop_screen()


class DetailOverlay(ModalScreen):
    """Modal overlay for viewing and interacting with a selected item."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Done"),
        Binding("e", "toggle_equipped", "Equip"),
        Binding("a", "toggle_attuned", "Attune"),
        Binding("b", "toggle_bonded", "Bond"),
        Binding("1", "hold_main", "Hold Main"),
        Binding("2", "hold_off", "Hold Off"),
        Binding("3", "hold_two", "Hold Two-Handed"),
        Binding("h", "hp", "HP"),
        Binding("t", "temp_hp", "Temp HP"),
        Binding("s", "bonuses", "Bonuses"),
        # Magic item properties
        Binding("m", "toggle_magical", "Magic"),
        Binding("r", "toggle_requires_attunement", "Req. Attune"),
        Binding("plus", "increase_ac_bonus", "+AC", show=False),
        Binding("equals", "increase_ac_bonus", "+AC", show=False),
        Binding("minus", "decrease_ac_bonus", "-AC", show=False),
        Binding("bracketright", "increase_attack_bonus", "+Atk", show=False),
        Binding("bracketleft", "decrease_attack_bonus", "-Atk", show=False),
        Binding("c", "use_charge", "Use Charge"),
        Binding("C", "add_charge", "Add Charge", show=False),
    ]

    def __init__(self, character: "Character", pane_id: str, item, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.pane_id = pane_id
        self.item = item
        self._dirty = False
        self._snapshot = self._snapshot_item()

    def _snapshot_item(self) -> dict:
        if hasattr(self.item, "model_dump"):
            return dict(self.item.model_dump())
        return {}

    def _restore_item(self) -> None:
        if not self._snapshot or not hasattr(self.item, "model_dump"):
            return
        for key, value in self._snapshot.items():
            setattr(self.item, key, value)

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Details", id="detail-overlay-title", classes="title"),
            VerticalScroll(id="detail-overlay-body", classes="panel details-panel"),
            Horizontal(
                Button("Cancel", id="btn-cancel", variant="error"),
                Button("Done", id="btn-done", variant="primary"),
                classes="button-row",
            ),
            id="detail-overlay-container",
        )

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        body = self.query_one("#detail-overlay-body", VerticalScroll)
        body.remove_children()

        if self.pane_id in ("weapons", "inventory"):
            self._render_inventory_item(body)
        elif self.pane_id == "skills":
            self._render_skill(body)
        elif self.pane_id == "abilities":
            self._render_ability(body)
        elif self.pane_id == "feats":
            self._render_feat(body)
        elif self.pane_id in ("known_spells", "prepared_spells"):
            self._render_spell(body)
        else:
            body.mount(Static("No details available."))

        done_btn = self.query_one("#btn-done", Button)
        done_btn.label = "Save" if self._dirty else "Done"

    def _render_inventory_item(self, body: VerticalScroll) -> None:
        from dnd_manager.data import get_weapon_by_name, get_equipment_by_name, get_armor_by_name

        item = self.item
        # Title with rarity if magical
        title = item.name
        if item.magical and item.rarity:
            title += f" ({item.rarity})"
        elif item.magical:
            title += " (Magic)"
        body.mount(Static(title, classes="panel-title"))

        # Basic item info
        body.mount(Static(f"Qty: {item.quantity}"))
        status_parts = []
        if item.equipped:
            status_parts.append("Equipped")
        if item.attuned:
            status_parts.append("Attuned")
        if item.bonded:
            status_parts.append("Bonded")
        if item.held:
            status_parts.append(f"Held ({item.held})")
        if status_parts:
            body.mount(Static(" • ".join(status_parts)))

        # Magic item properties
        if item.magical or item.ac_bonus or item.attack_bonus or item.requires_attunement:
            body.mount(Static(""))
            body.mount(Static("— Magic Properties —", classes="hint"))
            if item.requires_attunement:
                attune_status = "Yes (Attuned)" if item.attuned else "Yes (Not Attuned)"
                body.mount(Static(f"Requires Attunement: {attune_status}"))
            if item.ac_bonus:
                body.mount(Static(f"AC Bonus: +{item.ac_bonus}"))
            if item.attack_bonus:
                body.mount(Static(f"Attack/Damage Bonus: +{item.attack_bonus}"))
            if item.max_charges is not None:
                body.mount(Static(f"Charges: {item.charges or 0}/{item.max_charges}"))
            if item.stat_bonuses:
                body.mount(Static(f"Stat Bonuses: {len(item.stat_bonuses)} effect(s)"))

        weapon = get_weapon_by_name(item.name)
        armor = get_armor_by_name(item.name)
        equipment = get_equipment_by_name(item.name)

        if weapon:
            body.mount(Static(""))
            damage_str = f"{weapon.damage} {weapon.damage_type}"
            if item.attack_bonus:
                damage_str += f" (+{item.attack_bonus} bonus)"
            body.mount(Static(f"Damage: {damage_str}"))
            if weapon.properties:
                body.mount(Static("Properties: " + ", ".join(weapon.properties)))
            if weapon.range_normal:
                if weapon.range_long:
                    body.mount(Static(f"Range: {weapon.range_normal}/{weapon.range_long}"))
                else:
                    body.mount(Static(f"Range: {weapon.range_normal}"))
            mastery = None
            if self.character.meta.ruleset == RulesetId.DND_2024 and self.character.can_use_weapon_mastery(weapon.name):
                mastery = get_weapon_mastery_for_weapon(weapon.name)
            if mastery:
                body.mount(Static(f"Mastery: {mastery}"))
                summary = get_weapon_mastery_summary(mastery)
                if summary:
                    body.mount(Static(summary))
        elif armor:
            body.mount(Static(""))
            body.mount(Static(f"Armor: {armor.armor_type.value}"))
            total_ac = armor.base_ac + item.ac_bonus
            if item.ac_bonus:
                body.mount(Static(f"Base AC: {armor.base_ac} (+{item.ac_bonus} magic = {total_ac})"))
            else:
                body.mount(Static(f"Base AC: {armor.base_ac}"))
        elif equipment:
            if equipment.description:
                body.mount(Static(""))
                body.mount(Static(equipment.description))

        if item.description:
            body.mount(Static(""))
            body.mount(Static(item.description))

        body.mount(Static(""))
        body.mount(Static("— Actions —", classes="hint"))
        body.mount(Static("[E]quip [A]ttune [B]ond [1][2][3]Hold [M]agic [R]eq.Attune"))
        body.mount(Static("[+/-]AC  []/[]Atk  [C]harge  [S]tat Bonuses  [H]P"))

    def _render_skill(self, body: VerticalScroll) -> None:
        from dnd_manager.models.abilities import SKILL_ABILITY_MAP
        skill = self.item
        ability = SKILL_ABILITY_MAP[skill]
        body.mount(Static(skill.display_name, classes="panel-title"))
        body.mount(Static(f"Ability: {ability.display_name}"))
        body.mount(Static(f"Modifier: {self.character.get_skill_modifier(skill):+d}"))
        ruleset = self.character.meta.ruleset.value if hasattr(self.character.meta.ruleset, "value") else "dnd2024"
        description = get_skill_description(skill.display_name, ruleset)
        if description:
            body.mount(Static(""))
            body.mount(Static(description))

    def _render_ability(self, body: VerticalScroll) -> None:
        ability_key = self.item
        score = getattr(self.character.abilities, ability_key)
        body.mount(Static(ability_key.title(), classes="panel-title"))
        body.mount(Static(f"Score: {score.total} (base {score.base}, bonus {score.bonus:+d})"))
        body.mount(Static(f"Modifier: {score.modifier:+d}"))
        body.mount(Static(""))
        body.mount(Static("Actions: [S] Bonuses"))

    def _render_feat(self, body: VerticalScroll) -> None:
        feat = self.item
        body.mount(Static(feat.name, classes="panel-title"))
        if feat.description:
            body.mount(Static(feat.description))

    def _render_spell(self, body: VerticalScroll) -> None:
        from dnd_manager.data import get_spell_by_name
        spell_name = self.item
        body.mount(Static(spell_name, classes="panel-title"))
        spell = get_spell_by_name(spell_name)
        if spell:
            body.mount(Static(f"Level {spell.level} • {spell.school}"))
            if spell.components:
                body.mount(Static(f"Components: {spell.components}"))
            if spell.range:
                body.mount(Static(f"Range: {spell.range}"))
            if spell.duration:
                body.mount(Static(f"Duration: {spell.duration}"))
            if spell.description:
                body.mount(Static(""))
                body.mount(Static(spell.description))
        body.mount(Static(""))
        body.mount(Static("Actions: [H] HP  [T] Temp HP"))

    def action_toggle_equipped(self) -> None:
        if not hasattr(self.item, "equipped"):
            return
        self.item.equipped = not self.item.equipped
        self.character.apply_equipment_effects()
        self._dirty = True
        self._refresh()

    def action_toggle_attuned(self) -> None:
        if not hasattr(self.item, "attuned"):
            return
        self.item.attuned = not self.item.attuned
        if self.item.attuned and self.character.equipment.attuned_count > 3:
            self.notify("Attunement limit exceeded (3).", severity="warning")
        self._dirty = True
        self._refresh()

    def action_toggle_bonded(self) -> None:
        if not hasattr(self.item, "bonded"):
            return
        self.item.bonded = not self.item.bonded
        self._dirty = True
        self._refresh()

    def _set_held(self, value: Optional[str]) -> None:
        if not hasattr(self.item, "held"):
            return
        if value:
            for item in self.character.equipment.items:
                if item is not self.item and item.held == value:
                    item.held = None
        self.item.held = value
        self._dirty = True
        self._refresh()

    def action_hold_main(self) -> None:
        self._set_held("main")

    def action_hold_off(self) -> None:
        self._set_held("off")

    def action_hold_two(self) -> None:
        self._set_held("two")

    def action_hp(self) -> None:
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.editors import HPEditorScreen
        self.app.push_screen(HPEditorScreen(self.character))

    def action_temp_hp(self) -> None:
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.editors import HPEditorScreen
        self.app.push_screen(HPEditorScreen(self.character))

    def action_bonuses(self) -> None:
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.editors import StatBonusScreen, AbilityPickScreen

        if self.pane_id == "abilities":
            self.app.push_screen(StatBonusScreen(self.character, self.item))
            return
        if self.pane_id in ("weapons", "inventory", "known_spells", "prepared_spells"):
            source = self.item.name if hasattr(self.item, "name") else str(self.item)
            self.app.push_screen(AbilityPickScreen(self.character, default_source=source))

    # Magic item property actions
    def action_toggle_magical(self) -> None:
        if not hasattr(self.item, "magical"):
            return
        self.item.magical = not self.item.magical
        self._dirty = True
        self._refresh()

    def action_toggle_requires_attunement(self) -> None:
        if not hasattr(self.item, "requires_attunement"):
            return
        self.item.requires_attunement = not self.item.requires_attunement
        self._dirty = True
        self._refresh()

    def action_increase_ac_bonus(self) -> None:
        if not hasattr(self.item, "ac_bonus"):
            return
        self.item.ac_bonus = min(5, self.item.ac_bonus + 1)  # Cap at +5
        self.item.magical = True
        self.character.apply_equipment_effects()
        self._dirty = True
        self._refresh()

    def action_decrease_ac_bonus(self) -> None:
        if not hasattr(self.item, "ac_bonus"):
            return
        self.item.ac_bonus = max(0, self.item.ac_bonus - 1)
        self.character.apply_equipment_effects()
        self._dirty = True
        self._refresh()

    def action_increase_attack_bonus(self) -> None:
        if not hasattr(self.item, "attack_bonus"):
            return
        self.item.attack_bonus = min(5, self.item.attack_bonus + 1)  # Cap at +5
        self.item.magical = True
        self._dirty = True
        self._refresh()

    def action_decrease_attack_bonus(self) -> None:
        if not hasattr(self.item, "attack_bonus"):
            return
        self.item.attack_bonus = max(0, self.item.attack_bonus - 1)
        self._dirty = True
        self._refresh()

    def action_use_charge(self) -> None:
        if not hasattr(self.item, "charges") or self.item.charges is None:
            # Initialize charges if item has max_charges but no current charges
            if hasattr(self.item, "max_charges") and self.item.max_charges:
                self.item.charges = self.item.max_charges
            else:
                return
        if self.item.charges > 0:
            self.item.charges -= 1
            self._dirty = True
            self._refresh()

    def action_add_charge(self) -> None:
        if not hasattr(self.item, "charges"):
            return
        max_charges = self.item.max_charges or 10
        self.item.charges = min(max_charges, (self.item.charges or 0) + 1)
        self._dirty = True
        self._refresh()

    def action_confirm(self) -> None:
        if self._dirty:
            self.character.apply_all_effects()
            self.app.save_character()
        self.app.pop_screen()

    def action_cancel(self) -> None:
        if self._dirty:
            self._restore_item()
            self.character.apply_all_effects()
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-done":
            self.action_confirm()
