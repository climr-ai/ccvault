"""Shared widget classes for UI screens."""

from typing import TYPE_CHECKING

from textual.widgets import Static, OptionList
from textual.message import Message

if TYPE_CHECKING:
    from dnd_manager.app import CharacterCreationScreen


class ClickableListItem(Static):
    """A clickable list item that emits a message when clicked."""

    class Selected(Message):
        """Message sent when this item is clicked."""

        def __init__(self, item: "ClickableListItem", index: int) -> None:
            self.item = item
            self.index = index
            super().__init__()

        @property
        def control(self) -> "ClickableListItem":
            """The ClickableListItem that was selected."""
            return self.item

    class Activated(Message):
        """Message sent when this item is activated (double-click)."""

        bubble = True

        def __init__(self, item: "ClickableListItem", index: int) -> None:
            self.item = item
            self.index = index
            super().__init__()

        @property
        def control(self) -> "ClickableListItem":
            """The ClickableListItem that was activated."""
            return self.item

    def __init__(self, content: str, index: int, **kwargs) -> None:
        super().__init__(content, **kwargs)
        self.item_index = index

    def on_click(self, event) -> None:
        """Handle click by posting a Selected message."""
        self.post_message(self.Selected(self, self.item_index))
        if getattr(event, "chain", 1) >= 2:
            self.post_message(self.Activated(self, self.item_index))


class CreationOptionList(OptionList):
    """OptionList with custom key handling for character creation."""

    def on_key(self, event) -> None:
        # Import here to avoid circular imports
        from dnd_manager.app import CharacterCreationScreen

        screen = self.app.screen
        if isinstance(screen, CharacterCreationScreen):
            step_name = screen.steps[screen.step] if screen.step < len(screen.steps) else ""
            if step_name == "skills":
                if event.key == "space":
                    screen._toggle_skill()
                    event.prevent_default()
                    return
                if event.key.lower() == "c":
                    screen._clear_skills()
                    event.prevent_default()
                    return
            if step_name == "spells":
                if event.key == "space":
                    screen._toggle_spell()
                    event.prevent_default()
                    return
                if event.key.lower() == "c":
                    screen._clear_spells()
                    event.prevent_default()
                    return
        # Let OptionList handle all other keys (navigation, etc.)
