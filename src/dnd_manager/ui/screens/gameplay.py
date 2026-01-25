"""Gameplay screens for the D&D Manager application."""

from typing import TYPE_CHECKING, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from dnd_manager.ui.screens.base import ListNavigationMixin, ScreenContextMixin
from dnd_manager.ui.screens.widgets import ClickableListItem

if TYPE_CHECKING:
    from dnd_manager.models.character import Character


class InventoryScreen(ScreenContextMixin, ListNavigationMixin, Screen):
    """Screen for managing equipment and inventory."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("+", "add_item", "Add Item"),
        Binding("-", "drop_item", "Drop Item"),
        Binding("enter", "equip_toggle", "Equip/Unequip"),
        Binding("g", "manage_gold", "Manage Gold"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_index = 0
        self._last_letter = ""
        self._last_letter_index = -1

    def get_ai_context(self) -> dict:
        """Provide inventory context for AI."""
        c = self.character
        items = [
            {"name": item.name, "equipped": item.equipped, "attuned": item.attuned}
            for item in c.inventory.items
        ]
        return {
            "screen_type": "Inventory Management",
            "description": f"Managing {c.name}'s equipment and items",
            "data": {
                "items": items[:20],  # Limit to prevent too much context
                "gold": c.inventory.currency.gp,
                "selected_item": items[self.selected_index]["name"] if items and self.selected_index < len(items) else None,
            },
            "character_obj": c,
        }

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Inventory - {self.character.name}", classes="title"),
            self._build_currency_bar(),
            Horizontal(
                Vertical(
                    Static("EQUIPMENT", classes="panel-title"),
                    VerticalScroll(id="equipment-list", classes="item-list"),
                    classes="panel inventory-panel",
                ),
                Vertical(
                    Static("ACTIONS", classes="panel-title"),
                    Static("\\[A] Add item"),
                    Static("\\[D] Drop selected"),
                    Static("\\[E] Equip/Unequip"),
                    Static("\\[G] Manage gold"),
                    Static(""),
                    Static("ENCUMBRANCE", classes="panel-title"),
                    Static(id="encumbrance-info"),
                    Static(""),
                    Static("ATTUNEMENT", classes="panel-title"),
                    Static(id="attunement-info"),
                    classes="panel actions-panel",
                ),
                classes="inventory-row",
            ),
            id="inventory-container",
        )
        yield Footer()

    def _build_currency_bar(self) -> Static:
        """Build the currency display bar."""
        c = self.character.equipment.currency
        return Static(
            f"💰 {c.pp}pp | {c.gp}gp | {c.ep}ep | {c.sp}sp | {c.cp}cp",
            classes="currency-bar",
        )

    def on_mount(self) -> None:
        """Populate inventory list."""
        self._refresh_inventory()
        self._refresh_info()

    def _refresh_inventory(self) -> None:
        """Refresh the equipment list."""
        list_widget = self.query_one("#equipment-list", VerticalScroll)
        list_widget.remove_children()

        items = self.character.equipment.items
        if not items:
            list_widget.mount(Static("  No items in inventory", classes="empty-state"))
            list_widget.mount(Static("  Press \\[+] to add items", classes="empty-state-hint"))
            return

        for i, item in enumerate(items):
            equipped = "◆" if item.equipped else "○"
            attuned = " ★" if item.attuned else ""
            qty = f" x{item.quantity}" if item.quantity > 1 else ""

            item_class = "item-row"
            if i == self.selected_index:
                item_class += " selected"
            if item.equipped:
                item_class += " equipped"

            list_widget.mount(ClickableListItem(
                f"  {equipped} {item.name}{qty}{attuned}",
                index=i,
                classes=item_class,
            ))

    def _refresh_info(self) -> None:
        """Refresh encumbrance and attunement info."""
        # Count attuned items
        attuned = sum(1 for item in self.character.equipment.items if item.attuned)
        attunement_widget = self.query_one("#attunement-info", Static)
        attunement_widget.update(f"  {attuned}/3 slots used")

        # Simple encumbrance (could be expanded)
        encumbrance_widget = self.query_one("#encumbrance-info", Static)
        str_score = self.character.abilities.strength.total
        carry_capacity = str_score * 15
        encumbrance_widget.update(f"  Carry: {carry_capacity} lbs")

    def action_add_item(self) -> None:
        """Add a new item (opens magic item browser)."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.browsers import MagicItemBrowserScreen
        self.app.push_screen(MagicItemBrowserScreen(self.character))

    def action_drop_item(self) -> None:
        """Drop the selected item."""
        items = self.character.equipment.items
        if items and 0 <= self.selected_index < len(items):
            item = items.pop(self.selected_index)
            self.app.save_character()
            self.notify(f"Dropped {item.name}")
            self.selected_index = max(0, self.selected_index - 1)
            self._refresh_inventory()

    def action_equip_toggle(self) -> None:
        """Toggle equipped status of selected item."""
        items = self.character.equipment.items
        if items and 0 <= self.selected_index < len(items):
            item = items[self.selected_index]
            item.equipped = not item.equipped
            self.app.save_character()
            status = "equipped" if item.equipped else "unequipped"
            self.notify(f"{item.name} {status}")
            self._refresh_inventory()

    def action_manage_gold(self) -> None:
        """Manage currency."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.editors import CurrencyEditorScreen
        self.app.push_screen(CurrencyEditorScreen(self.character, on_save=self._on_currency_saved))

    def _on_currency_saved(self) -> None:
        """Handle currency update callback."""
        self._refresh_currency_bar()
        self.app.save_character()

    def _refresh_currency_bar(self) -> None:
        """Refresh the currency display bar."""
        c = self.character.equipment.currency
        try:
            bar = self.query_one(".currency-bar", Static)
            bar.update(f"💰 {c.pp}pp | {c.gp}gp | {c.ep}ep | {c.sp}sp | {c.cp}cp")
        except NoMatches:
            pass

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.character.equipment.items

    def _get_item_name(self, item) -> str:
        return item.name

    def _get_scroll_container(self):
        try:
            return self.query_one("#equipment-list", VerticalScroll)
        except NoMatches:
            return None

    def _get_item_widget_class(self) -> str:
        return "item-row"

    def _update_selection(self) -> None:
        """Update selection - refreshes the inventory display."""
        self._refresh_inventory()
        self.call_after_refresh(self._scroll_to_selection)

    def key_up(self) -> None:
        """Move selection up."""
        self._navigate_up()

    def key_down(self) -> None:
        """Move selection down."""
        self._navigate_down()

    def on_key(self, event) -> None:
        """Handle letter keys for jump navigation."""
        if self._handle_key_for_letter_jump(event.key):
            event.prevent_default()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        """Handle mouse click on a list item."""
        items = self.character.equipment.items
        if 0 <= event.index < len(items):
            self.selected_index = event.index
            self._update_selection()

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()


class FeaturesScreen(Screen):
    """Screen for viewing class features, feats, and traits."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("u", "use_feature", "Use Feature"),
        Binding("r", "rest", "Rest (Recover Uses)"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Features & Traits - {self.character.name}", classes="title"),
            Static(f"Level {self.character.total_level} {self.character.primary_class.name}", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("CLASS FEATURES", classes="panel-title"),
                    VerticalScroll(id="class-features", classes="feature-list"),
                    classes="panel feature-panel",
                ),
                Vertical(
                    Static("RACIAL TRAITS", classes="panel-title"),
                    VerticalScroll(id="racial-traits", classes="feature-list"),
                    Static("FEATS", classes="panel-title"),
                    VerticalScroll(id="feats-list", classes="feature-list"),
                    classes="panel feature-panel",
                ),
                classes="features-row",
            ),
            id="features-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Populate feature lists."""
        self._refresh_features()

    def _refresh_features(self) -> None:
        """Refresh all feature lists."""
        from dnd_manager.data import get_features_up_to_level, get_subclass, get_subclass_features_up_to_level

        # Class features - pull from data module
        class_list = self.query_one("#class-features", VerticalScroll)
        class_list.remove_children()

        # Get class features from data
        class_name = self.character.primary_class.name
        level = self.character.total_level
        data_features = get_features_up_to_level(class_name, level)

        if data_features:
            class_list.mount(Static(f"  {class_name} Features (Level {level}):", classes="feature-header"))
            for feature in data_features:
                uses_str = ""
                if feature.uses:
                    uses_str = f" [{feature.uses} uses]"
                recharge_str = ""
                if feature.recharge:
                    recharge_str = f" ({feature.recharge})"
                class_list.mount(Static(
                    f"  • Lv{feature.level}: {feature.name}{uses_str}{recharge_str}",
                    classes="feature-item",
                ))
                if feature.description:
                    class_list.mount(Static(f"      {feature.description}", classes="feature-desc"))

        # Add subclass features if character has a subclass
        if self.character.primary_class.subclass:
            subclass = get_subclass(self.character.primary_class.subclass)
            if subclass:
                subclass_features = get_subclass_features_up_to_level(subclass, level)
                if subclass_features:
                    class_list.mount(Static(""))
                    class_list.mount(Static(f"  {subclass.name} Features:", classes="feature-header"))
                    for feature in subclass_features:
                        class_list.mount(Static(
                            f"  • Lv{feature.level}: {feature.name}",
                            classes="feature-item",
                        ))
                        if feature.description:
                            class_list.mount(Static(f"      {feature.description}", classes="feature-desc"))

        if not data_features:
            class_list.mount(Static(f"  (No features found for {class_name})", classes="no-items"))

        # Racial traits
        racial_list = self.query_one("#racial-traits", VerticalScroll)
        racial_list.remove_children()

        racial_features = [f for f in self.character.features if f.source == "racial"]
        if racial_features:
            for feature in racial_features:
                self._add_feature_widget(racial_list, feature)
        else:
            if self.character.species:
                racial_list.mount(Static(f"  {self.character.species} Traits:", classes="feature-header"))
                racial_list.mount(Static("  • Darkvision (if applicable)", classes="feature-item"))
                racial_list.mount(Static("  • Racial abilities", classes="feature-item"))
            else:
                racial_list.mount(Static("  (No species selected)", classes="no-items"))

        # Feats
        feats_list = self.query_one("#feats-list", VerticalScroll)
        feats_list.remove_children()

        feats = [f for f in self.character.features if f.source == "feat"]
        if feats:
            for feature in feats:
                self._add_feature_widget(feats_list, feature)
        else:
            feats_list.mount(Static("  (No feats)", classes="no-items"))

    def _add_feature_widget(self, container: VerticalScroll, feature) -> None:
        """Add a feature to the container."""
        # Show uses if applicable
        uses_str = ""
        if feature.uses:
            remaining = feature.uses - feature.used
            uses_str = f" [{remaining}/{feature.uses}]"

        container.mount(Static(
            f"  • {feature.name}{uses_str}",
            classes="feature-item",
        ))
        if feature.description:
            container.mount(Static(f"    {feature.description}", classes="feature-desc"))

    def action_use_feature(self) -> None:
        """Use a feature (expend a use)."""
        # Find features with uses remaining
        usable = [f for f in self.character.features if f.uses and f.used < f.uses]
        if usable:
            feature = usable[0]
            feature.used += 1
            self.app.save_character()
            remaining = feature.uses - feature.used
            self.notify(f"Used {feature.name} ({remaining} remaining)")
            self._refresh_features()
        else:
            self.notify("No usable features available", severity="warning")

    def action_rest(self) -> None:
        """Recover feature uses (long rest)."""
        recovered = 0
        for feature in self.character.features:
            if feature.uses and feature.used > 0:
                if feature.recharge in ("long rest", "long_rest", "daily"):
                    recovered += feature.used
                    feature.used = 0

        if recovered > 0:
            self.app.save_character()
            self.notify(f"Long rest: recovered {recovered} feature uses!")
            self._refresh_features()
        else:
            self.notify("No features to recover")

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()


class SpellsScreen(ScreenContextMixin, Screen):
    """Screen for managing spells."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("c", "cast", "Cast Spell"),
        Binding("p", "toggle_prepared", "Toggle Prepared"),
        Binding("r", "rest", "Rest (Recover Slots)"),
        Binding("/", "search", "Search"),
        Binding("b", "browse", "Browse Spells"),
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("j", "move_down", "Down", show=False),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_spell: Optional[str] = None
        self.selected_level: int = 0
        self.selected_spell_index: int = 0
        self._spell_list: list[str] = []  # Current list of spells for selection

    def get_ai_context(self) -> dict:
        """Provide spell context for AI."""
        c = self.character
        return {
            "screen_type": "Spell Management",
            "description": f"Managing {c.name}'s spells",
            "data": {
                "cantrips": c.spellcasting.cantrips,
                "known_spells": c.spellcasting.known,
                "prepared": list(c.spellcasting.prepared),
                "selected_spell": self.selected_spell,
            },
            "character_obj": c,
        }

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Spells - {self.character.name}", classes="title"),
            self._build_spell_slots_bar(),
            Horizontal(
                Vertical(
                    Static("CANTRIPS", classes="panel-title"),
                    VerticalScroll(id="cantrips-list", classes="spell-list"),
                    classes="panel spell-level-panel",
                ),
                Vertical(
                    Static("SPELLS BY LEVEL", classes="panel-title"),
                    VerticalScroll(id="spells-list", classes="spell-list"),
                    classes="panel spell-level-panel wide",
                ),
                Vertical(
                    Static("ACTIONS", classes="panel-title"),
                    Static("\\[C] Cast selected spell"),
                    Static("\\[P] Toggle prepared"),
                    Static("\\[R] Short/Long rest"),
                    Static("/ Search spells"),
                    Static(""),
                    Static("SPELL SLOTS", classes="panel-title"),
                    Static(id="slots-detail"),
                    classes="panel actions-panel",
                ),
                classes="spells-row",
            ),
            id="spells-container",
        )
        yield Footer()

    def _build_spell_slots_bar(self) -> Static:
        """Build the spell slots summary bar."""
        slots = self.character.spellcasting.slots
        if not slots:
            return Static("No spellcasting", classes="slots-bar")

        parts = []
        for level in sorted(slots.keys()):
            slot = slots[level]
            if slot.total > 0:
                filled = "●" * slot.remaining + "○" * slot.used
                parts.append(f"{level}: {filled}")

        return Static("  ".join(parts), classes="slots-bar")

    def on_mount(self) -> None:
        """Populate spell lists."""
        self._refresh_spells()
        self._refresh_slots_detail()

    def _refresh_spells(self) -> None:
        """Refresh the spell lists."""
        # Cantrips
        cantrips_list = self.query_one("#cantrips-list", VerticalScroll)
        cantrips_list.remove_children()
        cantrips = self.character.spellcasting.cantrips
        if cantrips:
            for spell in cantrips:
                cantrips_list.mount(Static(f"  {spell}", classes="spell-item cantrip"))
        else:
            cantrips_list.mount(Static("  (None)", classes="no-spells"))

        # Spells by level
        spells_list = self.query_one("#spells-list", VerticalScroll)
        spells_list.remove_children()

        known = self.character.spellcasting.known or []
        prepared = set(self.character.spellcasting.prepared or [])

        # Update spell list for selection tracking
        self._spell_list = sorted(known) if known else []
        if self._spell_list and self.selected_spell_index >= len(self._spell_list):
            self.selected_spell_index = len(self._spell_list) - 1

        if not known:
            spells_list.mount(Static("  No spells known yet", classes="empty-state"))
            spells_list.mount(Static("  Press \\[B] to browse spells", classes="empty-state-hint"))
        else:
            # Group by level (simple approach - just list them)
            for idx, spell in enumerate(self._spell_list):
                is_prepared = spell in prepared
                is_selected = idx == self.selected_spell_index
                prefix = "◆" if is_prepared else "○"
                select_marker = "▶" if is_selected else " "
                spell_class = "spell-item prepared" if is_prepared else "spell-item"
                if is_selected:
                    spell_class += " selected"
                spells_list.mount(Static(f"{select_marker} {prefix} {spell}", classes=spell_class))

    def _refresh_slots_detail(self) -> None:
        """Refresh the spell slots detail panel."""
        slots = self.character.spellcasting.slots
        detail = self.query_one("#slots-detail", Static)

        if not slots:
            detail.update("No spell slots")
            return

        lines = []
        for level in sorted(slots.keys()):
            slot = slots[level]
            if slot.total > 0:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(level, "th")
                lines.append(f"{level}{suffix}: {slot.remaining}/{slot.total}")

        detail.update("\n".join(lines))

    def action_cast(self) -> None:
        """Cast a spell (use a spell slot)."""
        slots = self.character.spellcasting.slots
        if not slots:
            self.notify("No spell slots available", severity="warning")
            return

        # Find lowest available slot
        for level in sorted(slots.keys()):
            slot = slots[level]
            if slot.remaining > 0:
                slot.remaining -= 1
                self.app.save_character()
                self.notify(f"Cast using level {level} slot ({slot.remaining} remaining)")
                self._refresh_slots_detail()
                # Refresh the slots bar
                self.query_one(".slots-bar", Static).update(
                    self._build_spell_slots_bar().renderable
                )
                return

        self.notify("No spell slots remaining!", severity="error")

    def action_move_up(self) -> None:
        """Move selection up in the spell list."""
        if self._spell_list and self.selected_spell_index > 0:
            self.selected_spell_index -= 1
            self._refresh_spells()

    def action_move_down(self) -> None:
        """Move selection down in the spell list."""
        if self._spell_list and self.selected_spell_index < len(self._spell_list) - 1:
            self.selected_spell_index += 1
            self._refresh_spells()

    def action_toggle_prepared(self) -> None:
        """Toggle prepared status of the selected spell."""
        if not self._spell_list:
            self.notify("No spells to prepare", severity="warning")
            return

        spell_name = self._spell_list[self.selected_spell_index]
        prepared = self.character.spellcasting.prepared or []

        if spell_name in prepared:
            # Remove from prepared
            prepared.remove(spell_name)
            self.character.spellcasting.prepared = prepared
            self.app.save_character()
            self.notify(f"Unprepared: {spell_name}")
        else:
            # Add to prepared
            prepared.append(spell_name)
            self.character.spellcasting.prepared = prepared
            self.app.save_character()
            self.notify(f"Prepared: {spell_name}")

        self._refresh_spells()

    def action_rest(self) -> None:
        """Recover spell slots (long rest)."""
        slots = self.character.spellcasting.slots
        if not slots:
            self.notify("No spell slots to recover", severity="warning")
            return

        recovered = 0
        for slot in slots.values():
            if slot.remaining < slot.total:
                recovered += slot.total - slot.remaining
                slot.remaining = slot.total

        if recovered > 0:
            self.app.save_character()
            self.notify(f"Long rest: recovered {recovered} spell slots!")
            self._refresh_slots_detail()
            self.query_one(".slots-bar", Static).update(
                self._build_spell_slots_bar().renderable
            )
        else:
            self.notify("All spell slots already full")

    def action_search(self) -> None:
        """Search/browse spells."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.browsers import SpellBrowserScreen
        self.app.push_screen(SpellBrowserScreen(self.character))

    def action_browse(self) -> None:
        """Browse and add spells."""
        # Lazy import to avoid circular dependency
        from dnd_manager.ui.screens.browsers import SpellBrowserScreen
        self.app.push_screen(SpellBrowserScreen(self.character))

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()
