"""UI Screen modules for the D&D Manager application.

This package contains all screen classes organized by functionality.
"""

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
from dnd_manager.ui.screens.widgets import (
    ClickableListItem,
    CreationOptionList,
)
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

__all__ = [
    # Constants
    "ABILITIES",
    "ABILITY_ABBREV",
    "POINT_BUY_COSTS",
    "POINT_BUY_MAX",
    "POINT_BUY_MIN",
    "POINT_BUY_TOTAL",
    "RULESET_LABELS",
    "STANDARD_ARRAY",
    # Mixins
    "ListNavigationMixin",
    "ScreenContextMixin",
    # Functions
    "apply_item_order",
    "is_weapon_proficient",
    # Widgets
    "ClickableListItem",
    "CreationOptionList",
    # Dashboard Panels
    "DashboardPanel",
    "AbilityBlock",
    "CharacterInfo",
    "CombatStats",
    "QuickActions",
    "SkillList",
    "SpellSlots",
    "PreparedSpells",
    "KnownSpells",
    "WeaponsPane",
    "FeatsPane",
    "InventoryPane",
    "ActionsPane",
    # Gameplay Screens
    "InventoryScreen",
    "FeaturesScreen",
    "SpellsScreen",
    # Notes Screens
    "NotesScreen",
    "SessionNotesScreen",
    "NoteEditorScreen",
    # Rest Screens
    "ShortRestScreen",
    "LongRestScreen",
    # Dashboard Screens
    "PANE_DEFS",
    "DASHBOARD_LAYOUT_PRESETS",
    "ORDERABLE_PANELS",
    "MainDashboard",
    "DashboardLayoutScreen",
    "WeaponMasteryScreen",
    "PanelOrderScreen",
    "DetailOverlay",
    # Character Creation
    "CharacterCreationScreen",
]
