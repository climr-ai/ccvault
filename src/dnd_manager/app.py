"""Main Textual application for D&D Character Manager."""

import asyncio
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from dnd_manager.data.items import Weapon

from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Button, Label, Input, RichLog, OptionList
from textual.widgets.option_list import Option
from textual.screen import Screen, ModalScreen
from textual.message import Message
from rich.text import Text

from dnd_manager.config import Config, get_config_manager
from dnd_manager.models.character import Character, RulesetId, Feature, Alignment
from dnd_manager.storage import CharacterStore
from dnd_manager.data import (
    get_all_species_names,
    get_species,
    get_subraces,
    get_origin_feats,
    get_general_feats,
    get_all_background_names,
    get_background,
    get_class_info,
    get_feat,
    get_skill_description,
    species_grants_feat,
    skill_name_to_enum,
    get_weapon_mastery_for_weapon,
    get_weapon_mastery_summary,
)
from dnd_manager.data.backgrounds import get_origin_feat_for_background

# Import shared components from ui.screens module
from dnd_manager.ui.screens.base import (
    ABILITIES,
    ABILITY_ABBREV,
    POINT_BUY_COSTS,
    POINT_BUY_MAX,
    POINT_BUY_MIN,
    POINT_BUY_TOTAL,
    RULESET_LABELS,
    STANDARD_ARRAY,
    ListNavigationMixin,
    ScreenContextMixin,
    apply_item_order,
)
from dnd_manager.ui.screens.widgets import ClickableListItem, CreationOptionList
from dnd_manager.ui.screens.panels import (
    DashboardPanel,
    AbilityBlock,
    CharacterInfo,
    CombatStats,
    QuickActions,
    SkillList,
    SpellSlots,
    PreparedSpells,
    KnownSpells,
    WeaponsPane,
    FeatsPane,
    InventoryPane,
    ActionsPane,
    is_weapon_proficient,
)
from dnd_manager.ui.screens.utility import (
    DiceRollerScreen,
    HelpScreen,
    SettingsScreen,
)
from dnd_manager.ui.screens.navigation import (
    WelcomeScreen,
    CharacterListItem,
    DeleteCharacterModal,
    CharacterSelectScreen,
)
from dnd_manager.ui.screens.ai import (
    AIChatScreen,
    AIOverlayScreen,
    HomebrewScreen,
    HomebrewChatScreen,
)
from dnd_manager.ui.screens.browsers import (
    LibraryBrowserScreen,
    MagicItemBrowserScreen,
    SpellBrowserScreen,
)
from dnd_manager.ui.screens.level import (
    MulticlassSelectScreen,
    LevelManagementScreen,
    FeatPickerScreen,
    SubclassPickerScreen,
)
from dnd_manager.ui.screens.editors import (
    CharacterEditorScreen,
    CustomStatsScreen,
    AbilityEditorScreen,
    StatBonusScreen,
    HPEditorScreen,
    AbilityPickScreen,
    InfoEditorScreen,
    CurrencyEditorScreen,
)
from dnd_manager.ui.screens.gameplay import (
    InventoryScreen,
    FeaturesScreen,
    SpellsScreen,
)
from dnd_manager.ui.screens.notes import (
    NotesScreen,
    SessionNotesScreen,
    NoteEditorScreen,
)
from dnd_manager.ui.screens.rest import (
    ShortRestScreen,
    LongRestScreen,
)
from dnd_manager.ui.screens.dashboard import (
    PANE_DEFS,
    DASHBOARD_LAYOUT_PRESETS,
    ORDERABLE_PANELS,
    MainDashboard,
    DashboardLayoutScreen,
    WeaponMasteryScreen,
    PanelOrderScreen,
    DetailOverlay,
)
from dnd_manager.ui.screens.creation import CharacterCreationScreen
from dnd_manager.ui.screens.import_wizard import ImportWizardScreen, ImportFilePickerScreen



def _get_app_version() -> str:
    """Get the application version from package metadata."""
    try:
        from importlib.metadata import version, PackageNotFoundError
        return version("ccvault")
    except PackageNotFoundError:
        return "dev"


class DNDManagerApp(App):
    """CCVault - CLI Character Vault application."""

    TITLE = f"CCVault v{_get_app_version()}"
    SUB_TITLE = "CLI Character Vault for D&D 5e"
    CSS_PATH = "ui/styles/app.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+a", "ai_overlay", "AI Assistant", show=True),
    ]

    def __init__(self, character_path: Optional[Path] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = Config.load()
        self.store = CharacterStore(self.config.get_character_directory())
        self.current_character: Optional[Character] = None
        self.character_path = character_path

    def on_mount(self) -> None:
        """Handle app mount."""
        if self.character_path:
            char = self.store.load_path(self.character_path)
            if char:
                self.current_character = char
                self.push_screen(MainDashboard(char))
                return

        # Show welcome screen
        self.push_screen(WelcomeScreen())

    def action_new_character(self) -> None:
        """Open character creation wizard."""
        self.push_screen(CharacterCreationScreen())

    def action_open_character(self, return_to_dashboard: bool = False) -> None:
        """Open character selection screen."""
        char_info = self.store.get_character_info()
        if not char_info:
            self.notify("No characters found. Create one first!", severity="warning")
            return

        self.push_screen(CharacterSelectScreen(char_info, return_to_dashboard=return_to_dashboard))

    def load_character(self, path: Path) -> None:
        """Load a character from a path and switch to dashboard."""
        char = self.store.load_path(path)
        if char:
            self.current_character = char
            # Remove all screens except the base, then push dashboard
            while len(self.screen_stack) > 1:
                self.pop_screen()
            self.push_screen(MainDashboard(char))
        else:
            self.notify("Failed to load character", severity="error")

    def save_character(self) -> None:
        """Save the current character."""
        if self.current_character:
            self.store.save(self.current_character)

    def action_ai_overlay(self) -> None:
        """Open the AI assistant overlay with context from current screen."""
        # Get context from current screen if it supports it
        current_screen = self.screen
        context = {}

        # Check if screen implements ScreenContextMixin
        if hasattr(current_screen, 'get_ai_context'):
            context = current_screen.get_ai_context()
        else:
            # Default context with screen name
            context = {
                "screen_type": current_screen.__class__.__name__,
                "description": "User is viewing the application",
            }

        # Add character if available
        if self.current_character:
            context["character_obj"] = self.current_character
            context["character"] = {
                "name": self.current_character.name,
                "class": self.current_character.primary_class.name if self.current_character.primary_class else None,
                "level": self.current_character.primary_class.level if self.current_character.primary_class else 1,
                "species": self.current_character.species,
                "background": self.current_character.background,
            }

        self.push_screen(AIOverlayScreen(screen_context=context))


def run_app(character_path: Optional[Path] = None) -> None:
    """Run the D&D Character Manager application."""
    app = DNDManagerApp(character_path=character_path)
    app.run()
