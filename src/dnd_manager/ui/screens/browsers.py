"""Browser screens for the D&D Manager application."""

from typing import TYPE_CHECKING, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static

from dnd_manager.ui.screens.base import ListNavigationMixin
from dnd_manager.ui.screens.widgets import ClickableListItem

if TYPE_CHECKING:
    from dnd_manager.models.character import Character


class LibraryBrowserScreen(ListNavigationMixin, Screen):
    """Screen for browsing the CLIMR Homebrew Library."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "view", "View Details"),
        Binding("/", "search", "Search"),
        Binding("f1", "filter_spells", "Spells"),
        Binding("f2", "filter_items", "Items"),
        Binding("f3", "filter_feats", "Feats"),
        Binding("f4", "filter_all", "All"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selected_index = 0
        self.items: list = []
        self.search_query = ""
        self.filter_type: Optional[str] = None
        self.sort_by = "rating"
        self._library = None
        self._last_letter = ""
        self._last_letter_index = -1

    @property
    def library(self):
        """Get the homebrew library."""
        if self._library is None:
            from dnd_manager.data.library import get_homebrew_library
            self._library = get_homebrew_library()
        return self._library

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("CLIMR Homebrew Library", classes="title"),
            Static("↑/↓ Navigate  Type to jump  / Search  \\[F1-F4] Filter", classes="subtitle"),
            Horizontal(
                Input(placeholder="Search library...", id="lib-search"),
                Static(id="filter-mode", classes="filter-mode"),
                classes="search-row",
            ),
            Horizontal(
                Vertical(
                    Static("CONTENT", classes="panel-title"),
                    VerticalScroll(id="lib-list", classes="lib-list"),
                    classes="panel lib-list-panel",
                ),
                Vertical(
                    Static("DETAILS", classes="panel-title"),
                    VerticalScroll(id="lib-details", classes="lib-details"),
                    classes="panel lib-details-panel",
                ),
                classes="library-row",
            ),
            id="library-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load content on mount."""
        self._update_filter_mode()
        self._load_content()

    def _update_filter_mode(self) -> None:
        """Update the filter mode indicator."""
        mode_widget = self.query_one("#filter-mode", Static)
        if self.filter_type:
            mode_widget.update(f"[Filter: {self.filter_type}]")
        else:
            mode_widget.update("[All Types]")

    def _load_content(self) -> None:
        """Load content from library."""
        from dnd_manager.data.library import ContentType, ContentStatus

        content_type = None
        if self.filter_type:
            try:
                content_type = ContentType(self.filter_type)
            except ValueError:
                pass

        if self.search_query:
            self.items = self.library.search(self.search_query, limit=50)
        else:
            self.items = self.library.browse(
                content_type=content_type,
                sort_by=self.sort_by,
                limit=50,
            )

        self._refresh_list()

    def _refresh_list(self) -> None:
        """Refresh the content list display."""
        list_widget = self.query_one("#lib-list", VerticalScroll)
        list_widget.remove_children()

        if not self.items:
            list_widget.mount(Static("  (No content found)", classes="no-items"))
            list_widget.mount(Static(""))
            list_widget.mount(Static("  Use 'ccvault library import' to add content", classes="hint"))
            self._show_details(None)
            return

        for i, item in enumerate(self.items):
            selected = "▶ " if i == self.selected_index else "  "
            stars = "★" * int(item.rating.average)
            installed = " ✓" if self.library.is_installed(item.id) else ""

            list_widget.mount(ClickableListItem(
                f"{selected}[{item.content_type.value}] {item.name}{installed}",
                index=i,
                classes=f"lib-item {'selected' if i == self.selected_index else ''}",
            ))

        if 0 <= self.selected_index < len(self.items):
            self._show_details(self.items[self.selected_index])

    def _show_details(self, item) -> None:
        """Show details of the selected item."""
        details_widget = self.query_one("#lib-details", VerticalScroll)
        details_widget.remove_children()

        if item is None:
            details_widget.mount(Static("  (Select an item to view)", classes="no-content"))
            return

        # Header
        details_widget.mount(Static(f"  {item.name}", classes="item-title"))
        details_widget.mount(Static(f"  Type: {item.content_type.value}", classes="item-meta"))
        details_widget.mount(Static(f"  Ruleset: {item.ruleset}", classes="item-meta"))

        # Rating
        stars = "★" * int(item.rating.average) + "☆" * (5 - int(item.rating.average))
        details_widget.mount(Static(
            f"  Rating: {stars} ({item.rating.average:.1f}/5, {item.rating.count} votes)",
            classes="item-rating",
        ))
        details_widget.mount(Static(f"  Downloads: {item.downloads}", classes="item-meta"))
        details_widget.mount(Static(f"  Author: {item.author.name}", classes="item-meta"))

        # Installation status
        if self.library.is_installed(item.id):
            details_widget.mount(Static("  \\[INSTALLED]", classes="installed-badge"))
        else:
            details_widget.mount(Static("  Press \\[I] to install", classes="hint"))

        details_widget.mount(Static(""))
        details_widget.mount(Static("  ─────────────────────", classes="separator"))

        # Description
        if item.description:
            details_widget.mount(Static(f"  {item.description}", classes="item-desc"))
        else:
            details_widget.mount(Static("  (No description)", classes="item-desc"))

        # Tags
        if item.tags:
            details_widget.mount(Static(""))
            details_widget.mount(Static(f"  Tags: {', '.join(item.tags)}", classes="item-tags"))

        # Content preview
        details_widget.mount(Static(""))
        details_widget.mount(Static("  Content Preview:", classes="section-header"))
        import json
        preview = json.dumps(item.content_data, indent=2)
        for line in preview.split("\n"):
            details_widget.mount(Static(f"    {line}", classes="content-preview"))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "lib-search":
            self.search_query = event.value
            self.selected_index = 0
            self._load_content()

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.items

    def _get_item_name(self, item) -> str:
        return item.name

    def _get_scroll_container(self):
        try:
            return self.query_one("#lib-list", VerticalScroll)
        except NoMatches:
            return None

    def _get_item_widget_class(self) -> str:
        return "lib-item"

    def _update_selection(self) -> None:
        """Update selection - refreshes the list display."""
        self._refresh_list()
        self.call_after_refresh(self._scroll_to_selection)

    def key_up(self) -> None:
        """Move selection up."""
        self._navigate_up()

    def key_down(self) -> None:
        """Move selection down."""
        self._navigate_down()

    def on_key(self, event) -> None:
        """Handle letter keys for jump navigation."""
        try:
            if self.query_one("#lib-search", Input).has_focus:
                return
        except NoMatches:
            pass
        if self._handle_key_for_letter_jump(event.key):
            event.prevent_default()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        """Handle mouse click on a list item."""
        if 0 <= event.index < len(self.items):
            self.selected_index = event.index
            self._update_selection()
            self._show_details(self.items[self.selected_index])

    def action_view(self) -> None:
        """View full details."""
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            self.notify(f"Viewing: {item.name}")
            # Could open a detail screen here

    def action_install(self) -> None:
        """Install selected content."""
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            if self.library.is_installed(item.id):
                self.notify(f"Already installed: {item.name}")
            else:
                self.library.install(item.id)
                self.notify(f"Installed: {item.name}")
                self._refresh_list()

    def action_uninstall(self) -> None:
        """Uninstall selected content."""
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            if not self.library.is_installed(item.id):
                self.notify(f"Not installed: {item.name}")
            else:
                self.library.uninstall(item.id)
                self.notify(f"Uninstalled: {item.name}")
                self._refresh_list()

    def action_rate(self) -> None:
        """Rate selected content."""
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            # For now, just cycle through ratings 1-5
            current = self.library.get_user_rating(item.id)
            new_rating = ((current.rating if current else 0) % 5) + 1
            self.library.rate(item.id, new_rating)
            self.notify(f"Rated {item.name}: {'★' * new_rating}")
            self._load_content()

    def action_search(self) -> None:
        """Focus search input."""
        self.query_one("#lib-search", Input).focus()

    def action_filter_spells(self) -> None:
        """Filter to spells only."""
        self.filter_type = "spell"
        self._update_filter_mode()
        self._load_content()
        self.notify("Filter: Spells")

    def action_filter_items(self) -> None:
        """Filter to magic items only."""
        self.filter_type = "magic_item"
        self._update_filter_mode()
        self._load_content()
        self.notify("Filter: Magic Items")

    def action_filter_feats(self) -> None:
        """Filter to feats only."""
        self.filter_type = "feat"
        self._update_filter_mode()
        self._load_content()
        self.notify("Filter: Feats")

    def action_filter_all(self) -> None:
        """Remove filter."""
        self.filter_type = None
        self._update_filter_mode()
        self._load_content()
        self.notify("Filter: All Types")

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


class MagicItemBrowserScreen(ListNavigationMixin, Screen):
    """Screen for browsing and adding magic items from the SRD."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "add_item", "Add to Inventory"),
        Binding("/", "search", "Search"),
        Binding("6", "filter_common", "Common"),
        Binding("7", "filter_uncommon", "Uncommon"),
        Binding("8", "filter_rare", "Rare"),
        Binding("9", "filter_very_rare", "Very Rare"),
        Binding("0", "filter_legendary", "Legendary"),
        Binding("-", "filter_all", "All Rarities"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_index = 0
        self.search_query = ""
        self.rarity_filter: str | None = None
        self.filtered_items: list = []
        self._last_letter = ""
        self._last_letter_index = -1

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Magic Item Browser", classes="title"),
            Static("↑/↓ Navigate  Type to jump  / Search  \\[6-0] Rarity  \\[-] All", classes="subtitle"),
            Horizontal(
                Input(placeholder="Search magic items...", id="item-search"),
                classes="search-row",
            ),
            Horizontal(
                Vertical(
                    Static("MAGIC ITEMS", classes="panel-title"),
                    Static(id="filter-info", classes="filter-info"),
                    VerticalScroll(id="item-list", classes="item-browser-list"),
                    classes="panel browser-panel",
                ),
                Vertical(
                    Static("ITEM DETAILS", classes="panel-title"),
                    VerticalScroll(id="item-details", classes="item-details"),
                    classes="panel browser-panel",
                ),
                classes="browser-row",
            ),
            id="magic-item-browser-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load magic items."""
        self._refresh_item_list()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "item-search":
            self.search_query = event.value.lower()
            self.selected_index = 0
            self._refresh_item_list()

    def _refresh_item_list(self) -> None:
        """Refresh the item list based on filters."""
        from dnd_manager.data import ALL_MAGIC_ITEMS, get_magic_items_by_rarity

        # Get items based on rarity filter
        if self.rarity_filter:
            items = get_magic_items_by_rarity(self.rarity_filter)
        else:
            items = ALL_MAGIC_ITEMS

        # Apply search filter
        if self.search_query:
            self.filtered_items = [
                item for item in items
                if self.search_query in item.name.lower()
                or self.search_query in item.description.lower()
                or self.search_query in item.item_type.lower()
            ]
        else:
            self.filtered_items = list(items)

        # Sort by name
        self.filtered_items.sort(key=lambda x: x.name)

        # Update filter info
        filter_widget = self.query_one("#filter-info", Static)
        filter_text = f"  Showing: {self.rarity_filter or 'All'} ({len(self.filtered_items)} items)"
        filter_widget.update(filter_text)

        # Update list
        list_widget = self.query_one("#item-list", VerticalScroll)
        list_widget.remove_children()

        for i, item in enumerate(self.filtered_items):
            rarity_colors = {
                "common": "",
                "uncommon": "🟢 ",
                "rare": "🔵 ",
                "very rare": "🟣 ",
                "legendary": "🟠 ",
            }
            rarity_mark = rarity_colors.get(item.rarity.lower(), "")
            attune_mark = " ✦" if item.requires_attunement else ""

            item_class = "item-row"
            if i == self.selected_index:
                item_class += " selected"

            list_widget.mount(ClickableListItem(
                f"  {rarity_mark}{item.name}{attune_mark}",
                index=i,
                classes=item_class,
            ))

        if not self.filtered_items:
            list_widget.mount(Static("  (No items found)", classes="no-items"))

        self._refresh_item_details()

    def _refresh_item_details(self) -> None:
        """Show details of the selected item."""
        details_widget = self.query_one("#item-details", VerticalScroll)
        details_widget.remove_children()

        if not self.filtered_items or self.selected_index >= len(self.filtered_items):
            details_widget.mount(Static("  Select an item to see details", classes="hint"))
            return

        item = self.filtered_items[self.selected_index]

        details_widget.mount(Static(f"  {item.name}", classes="item-name"))
        details_widget.mount(Static(f"  {item.item_type} | {item.rarity.title()}", classes="item-type"))

        if item.requires_attunement:
            attune_text = "  Requires Attunement"
            if item.attunement_requirements:
                attune_text += f" ({item.attunement_requirements})"
            details_widget.mount(Static(attune_text, classes="attunement-req"))

        details_widget.mount(Static(""))
        details_widget.mount(Static("  Description:", classes="section-header"))

        # Word wrap description
        desc = item.description
        words = desc.split()
        lines = []
        current_line = "    "
        for word in words:
            if len(current_line) + len(word) + 1 > 55:
                lines.append(current_line)
                current_line = "    " + word
            else:
                current_line += " " + word if current_line.strip() else "    " + word
        if current_line.strip():
            lines.append(current_line)
        for line in lines:
            details_widget.mount(Static(line, classes="item-desc"))

        if item.charges:
            details_widget.mount(Static(""))
            details_widget.mount(Static(f"  Charges: {item.charges}", classes="charges-info"))

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.filtered_items

    def _get_item_name(self, item) -> str:
        return item.name

    def _get_scroll_container(self):
        try:
            return self.query_one("#item-list", VerticalScroll)
        except NoMatches:
            return None

    def _get_item_widget_class(self) -> str:
        return "item-row"

    def _update_selection(self) -> None:
        """Update selection - refreshes the list display."""
        self._refresh_item_list()
        self.call_after_refresh(self._scroll_to_selection)

    def key_up(self) -> None:
        """Move selection up."""
        self._navigate_up()

    def key_down(self) -> None:
        """Move selection down."""
        self._navigate_down()

    def on_key(self, event) -> None:
        """Handle letter keys for jump navigation."""
        try:
            if self.query_one("#item-search", Input).has_focus:
                return
        except NoMatches:
            pass
        if self._handle_key_for_letter_jump(event.key):
            event.prevent_default()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        """Handle mouse click on a list item."""
        if 0 <= event.index < len(self.filtered_items):
            self.selected_index = event.index
            self._update_selection()

    def action_search(self) -> None:
        """Focus the search input."""
        self.query_one("#item-search", Input).focus()

    def action_filter_all(self) -> None:
        """Show all rarities."""
        self.rarity_filter = None
        self.selected_index = 0
        self._refresh_item_list()
        self.notify("Showing all rarities")

    def action_filter_common(self) -> None:
        """Filter to common items."""
        self.rarity_filter = "common"
        self.selected_index = 0
        self._refresh_item_list()
        self.notify("Showing common items")

    def action_filter_uncommon(self) -> None:
        """Filter to uncommon items."""
        self.rarity_filter = "uncommon"
        self.selected_index = 0
        self._refresh_item_list()
        self.notify("Showing uncommon items")

    def action_filter_rare(self) -> None:
        """Filter to rare items."""
        self.rarity_filter = "rare"
        self.selected_index = 0
        self._refresh_item_list()
        self.notify("Showing rare items")

    def action_filter_very_rare(self) -> None:
        """Filter to very rare items."""
        self.rarity_filter = "very rare"
        self.selected_index = 0
        self._refresh_item_list()
        self.notify("Showing very rare items")

    def action_filter_legendary(self) -> None:
        """Filter to legendary items."""
        self.rarity_filter = "legendary"
        self.selected_index = 0
        self._refresh_item_list()
        self.notify("Showing legendary items")

    def action_add_item(self) -> None:
        """Add the selected item to inventory."""
        if not self.filtered_items or self.selected_index >= len(self.filtered_items):
            self.notify("No item selected", severity="warning")
            return

        item = self.filtered_items[self.selected_index]

        # Check attunement limit
        if item.requires_attunement:
            attuned_count = sum(1 for i in self.character.equipment.items if i.attuned)
            if attuned_count >= 3:
                self.notify("Warning: Already at attunement limit (3 items)", severity="warning")

        # Create inventory item
        from dnd_manager.models.character import InventoryItem

        inv_item = InventoryItem(
            name=item.name,
            quantity=1,
            weight=0.0,  # Magic items don't always have weight in SRD
            description=item.description,
            equipped=False,
            attuned=False,
        )

        self.character.equipment.items.append(inv_item)
        self.app.save_character()

        self.notify(f"Added {item.name} to inventory!", severity="information")

    def action_back(self) -> None:
        """Return to inventory."""
        self.app.pop_screen()


class SpellBrowserScreen(ListNavigationMixin, Screen):
    """Screen for browsing and adding SRD spells."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "add_spell", "Add Spell"),
        Binding("/", "search", "Search"),
    ]

    def __init__(self, character: "Character", spell_type: str = "known", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.spell_type = spell_type  # "known", "prepared", or "cantrips"
        self.selected_index = 0
        self.filtered_spells: list = []
        self.search_query = ""
        self._last_letter = ""
        self._last_letter_index = -1

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Spell Browser - Add Spells", classes="title"),
            Static("↑/↓ Navigate  Type to jump  / Search  Enter Add", classes="subtitle"),
            Horizontal(
                Input(placeholder="Search spells...", id="spell-search"),
                classes="search-row",
            ),
            Horizontal(
                Vertical(
                    Static("AVAILABLE SPELLS", classes="panel-title"),
                    VerticalScroll(id="spell-list", classes="spell-browser-list"),
                    classes="panel browser-panel",
                ),
                Vertical(
                    Static("SPELL DETAILS", classes="panel-title"),
                    VerticalScroll(id="spell-details", classes="spell-details"),
                    classes="panel browser-panel",
                ),
                classes="browser-row",
            ),
            id="browser-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load spells on mount."""
        self._load_spells()
        self._refresh_list()

    def _load_spells(self) -> None:
        """Load available spells for this character's class."""
        from dnd_manager.data import get_spells_by_class, ALL_SPELLS

        class_name = self.character.primary_class.name

        # Check for Magic Initiate feat if primary class has no spells
        if not get_spells_by_class(class_name):
            # Look for Magic Initiate feat
            for feature in self.character.features:
                if feature.name.startswith("Magic Initiate"):
                    # Extract class name from feat (e.g., "Magic Initiate (Druid)" -> "Druid")
                    if "(" in feature.name and ")" in feature.name:
                        feat_class = feature.name.split("(")[1].split(")")[0].strip()
                        class_name = feat_class
                        break

        # Get spells for this class
        class_spells = get_spells_by_class(class_name)

        # Filter by type
        if self.spell_type == "cantrips":
            self.filtered_spells = [s for s in class_spells if s.level == 0]
        else:
            # Get character's max spell level based on class level
            level = self.character.primary_class.level
            max_spell_level = min((level + 1) // 2, 9)  # Rough approximation
            self.filtered_spells = [
                s for s in class_spells
                if 0 < s.level <= max_spell_level
            ]

        # Sort by level, then name
        self.filtered_spells.sort(key=lambda s: (s.level, s.name))

    def _refresh_list(self) -> None:
        """Refresh the spell list display."""
        list_widget = self.query_one("#spell-list", VerticalScroll)
        list_widget.remove_children()

        # Filter by search query
        spells = self.filtered_spells
        if self.search_query:
            query = self.search_query.lower()
            spells = [s for s in spells if query in s.name.lower()]

        if not spells:
            list_widget.mount(Static("  No spells found", classes="no-items"))
            return

        for i, spell in enumerate(spells):
            level_str = "Cantrip" if spell.level == 0 else f"Level {spell.level}"
            selected = "▶ " if i == self.selected_index else "  "
            list_widget.mount(ClickableListItem(
                f"{selected}{spell.name} ({level_str})",
                index=i,
                classes=f"spell-browser-item {'selected' if i == self.selected_index else ''}",
            ))

        self._show_spell_details()

    def _show_spell_details(self) -> None:
        """Show details for the selected spell."""
        details_widget = self.query_one("#spell-details", VerticalScroll)
        details_widget.remove_children()

        spells = self.filtered_spells
        if self.search_query:
            query = self.search_query.lower()
            spells = [s for s in spells if query in s.name.lower()]

        if not spells or self.selected_index >= len(spells):
            return

        spell = spells[self.selected_index]

        details_widget.mount(Static(f"  {spell.name}", classes="spell-name"))
        level_str = "Cantrip" if spell.level == 0 else f"Level {spell.level}"
        details_widget.mount(Static(f"  {level_str} {spell.school}", classes="spell-school"))
        details_widget.mount(Static(""))
        details_widget.mount(Static(f"  Casting Time: {spell.casting_time}"))
        details_widget.mount(Static(f"  Range: {spell.range}"))
        details_widget.mount(Static(f"  Components: {spell.components}"))
        details_widget.mount(Static(f"  Duration: {spell.duration}"))
        if spell.concentration:
            details_widget.mount(Static("  (Concentration)", classes="spell-tag"))
        if spell.ritual:
            details_widget.mount(Static("  (Ritual)", classes="spell-tag"))
        details_widget.mount(Static(""))
        # Word wrap description
        desc = spell.description
        while desc:
            details_widget.mount(Static(f"  {desc[:50]}"))
            desc = desc[50:]

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "spell-search":
            self.search_query = event.value
            self.selected_index = 0
            self._refresh_list()

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        spells = self.filtered_spells
        if self.search_query:
            query = self.search_query.lower()
            spells = [s for s in spells if query in s.name.lower()]
        return spells

    def _get_item_name(self, item) -> str:
        return item.name

    def _get_scroll_container(self):
        try:
            return self.query_one("#spell-list", VerticalScroll)
        except NoMatches:
            return None

    def _get_item_widget_class(self) -> str:
        return "spell-browser-item"

    def _update_selection(self) -> None:
        """Update selection - refreshes the list display."""
        self._refresh_list()
        self.call_after_refresh(self._scroll_to_selection)

    def key_up(self) -> None:
        """Move selection up."""
        self._navigate_up()

    def key_down(self) -> None:
        """Move selection down."""
        self._navigate_down()

    def on_key(self, event) -> None:
        """Handle letter keys for jump navigation."""
        try:
            if self.query_one("#spell-search", Input).has_focus:
                return
        except NoMatches:
            pass
        if self._handle_key_for_letter_jump(event.key):
            event.prevent_default()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        """Handle mouse click on a list item."""
        spells = self.filtered_spells
        if self.search_query:
            query = self.search_query.lower()
            spells = [s for s in spells if query in s.name.lower()]
        if 0 <= event.index < len(spells):
            self.selected_index = event.index
            self._update_selection()

    def action_add_spell(self) -> None:
        """Add the selected spell to the character."""
        spells = self.filtered_spells
        if self.search_query:
            query = self.search_query.lower()
            spells = [s for s in spells if query in s.name.lower()]

        if not spells or self.selected_index >= len(spells):
            return

        spell = spells[self.selected_index]

        # Add to appropriate list
        if spell.level == 0:
            if spell.name not in self.character.spellcasting.cantrips:
                self.character.spellcasting.cantrips.append(spell.name)
                self.app.save_character()
                self.notify(f"Added cantrip: {spell.name}")
            else:
                self.notify(f"Already know {spell.name}", severity="warning")
        else:
            if spell.name not in (self.character.spellcasting.known or []):
                if self.character.spellcasting.known is None:
                    self.character.spellcasting.known = []
                self.character.spellcasting.known.append(spell.name)
                self.app.save_character()
                self.notify(f"Added spell: {spell.name}")
            else:
                self.notify(f"Already know {spell.name}", severity="warning")

    def action_search(self) -> None:
        """Focus search input."""
        self.query_one("#spell-search", Input).focus()

    def action_back(self) -> None:
        """Return to spells screen."""
        self.app.pop_screen()
