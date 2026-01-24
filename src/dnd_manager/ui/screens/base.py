"""Base classes and mixins for UI screens."""

from typing import Any, Callable, Optional

from textual.css.query import NoMatches
from textual.containers import VerticalScroll


# Ability Score Constants
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
POINT_BUY_COSTS = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
POINT_BUY_TOTAL = 27
POINT_BUY_MIN = 8
POINT_BUY_MAX = 15
ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
ABILITY_ABBREV = {
    "strength": "STR",
    "dexterity": "DEX",
    "constitution": "CON",
    "intelligence": "INT",
    "wisdom": "WIS",
    "charisma": "CHA",
}
RULESET_LABELS = {
    "dnd2024": "D&D 2024 (5.5e)",
    "dnd2014": "D&D 2014 (5e)",
    "tov": "Tales of the Valiant",
}


def apply_item_order(
    items: list[Any], order: Optional[list[str]], key_fn: Callable[[Any], str]
) -> list[Any]:
    """Return items ordered by a saved name list, keeping unknown items at the end.

    Args:
        items: List of items to order.
        order: List of names defining the desired order. Items matching these names
            appear first, in the order specified.
        key_fn: Function to extract the name/key from an item for ordering.

    Returns:
        New list with items ordered by the name list, unknown items at the end.
    """
    if not order:
        return list(items)

    # Build a dict mapping names to lists of matching items - O(n)
    order_set = set(order)
    items_by_name: dict[str, list[Any]] = {name: [] for name in order}
    unordered: list[Any] = []

    for item in items:
        key = key_fn(item)
        if key in order_set:
            items_by_name[key].append(item)
        else:
            unordered.append(item)

    # Flatten ordered items followed by unordered - O(n)
    result: list[Any] = []
    for name in order:
        result.extend(items_by_name[name])
    result.extend(unordered)
    return result


class ScreenContextMixin:
    """Mixin for screens to provide context to the AI overlay.

    Implement get_ai_context() to provide relevant context about
    what the user is currently viewing/doing.
    """

    def get_ai_context(self) -> dict:
        """Return context dictionary for AI.

        Override this to provide screen-specific context like:
        - screen_type: Name of what the screen shows
        - description: What the user is doing
        - character: Current character if any
        - data: Relevant data (items, spells, stats, etc.)
        """
        return {
            "screen_type": self.__class__.__name__,
            "description": "User is viewing the application",
        }


class ListNavigationMixin:
    """Mixin providing standard list navigation: letter jump and scroll-into-view.

    Subclasses must implement:
    - _get_list_items() -> list: Return the list of items
    - _get_item_name(item) -> str: Return the display name for an item
    - _get_scroll_container() -> VerticalScroll: Return the scrollable container
    - _update_selection(): Update the visual selection state
    - _get_item_widget_class() -> str: CSS class for list item widgets

    Subclasses should have:
    - self.selected_index: int tracking current selection
    - self._last_letter: str tracking last letter pressed (for cycling)
    - self._last_letter_index: int tracking position in letter matches
    """

    _last_letter: str = ""
    _last_letter_index: int = -1

    def _get_list_items(self) -> list:
        """Override to return the list of items."""
        return []

    def _get_item_name(self, item) -> str:
        """Override to return the display name for an item."""
        return str(item)

    def _get_scroll_container(self) -> Optional[VerticalScroll]:
        """Override to return the scrollable container widget."""
        return None

    def _get_item_widget_class(self) -> str:
        """Override to return the CSS class for item widgets."""
        return "selected"

    def _scroll_to_selection(self) -> None:
        """Scroll to keep the selected item centered in the viewport."""
        container = self._get_scroll_container()
        if container is None:
            return

        items = self._get_list_items()
        if not items or self.selected_index >= len(items):
            return

        try:
            # Find the selected widget
            item_class = self._get_item_widget_class()
            widgets = list(container.query(f".{item_class}")) if item_class else list(container.children)

            if self.selected_index < len(widgets):
                selected_widget = widgets[self.selected_index]
                # Center the selected item in the viewport
                container.scroll_to_center(selected_widget, animate=False)
        except NoMatches:
            # Widget not found - screen may not be fully mounted
            pass

    def _navigate_up(self) -> None:
        """Move selection up with scroll."""
        items = self._get_list_items()
        if self.selected_index > 0:
            self.selected_index -= 1
            self._update_selection()

    def _navigate_down(self) -> None:
        """Move selection down with scroll."""
        items = self._get_list_items()
        if self.selected_index < len(items) - 1:
            self.selected_index += 1
            self._update_selection()

    def _jump_to_letter(self, letter: str) -> bool:
        """Jump to next item starting with letter. Returns True if found."""
        items = self._get_list_items()
        if not items:
            return False

        letter = letter.lower()

        # Find all items starting with this letter
        matching_indices = []
        for i, item in enumerate(items):
            name = self._get_item_name(item).lower()
            if name.startswith(letter):
                matching_indices.append(i)

        if not matching_indices:
            return False

        # If same letter pressed again, cycle to next match
        if letter == self._last_letter and self._last_letter_index >= 0:
            # Find next match after current position
            next_matches = [i for i in matching_indices if i > self.selected_index]
            if next_matches:
                self.selected_index = next_matches[0]
                self._last_letter_index = matching_indices.index(next_matches[0])
            else:
                # Wrap to first match
                self.selected_index = matching_indices[0]
                self._last_letter_index = 0
        else:
            # New letter - jump to first match
            self.selected_index = matching_indices[0]
            self._last_letter = letter
            self._last_letter_index = 0

        self._update_selection()
        return True

    def _handle_key_for_letter_jump(self, key: str) -> bool:
        """Handle a key press for letter jumping. Returns True if handled."""
        # Only handle single letter keys
        if len(key) == 1 and key.isalpha():
            return self._jump_to_letter(key)
        return False
