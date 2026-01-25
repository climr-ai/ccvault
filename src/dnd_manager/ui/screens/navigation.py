"""Navigation screens for the D&D Manager application."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.message import Message
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Input, Static

from dnd_manager.ui.screens.base import ListNavigationMixin

if TYPE_CHECKING:
    pass  # Forward references handled with lazy imports


class WelcomeScreen(Screen):
    """Welcome screen shown when no character is loaded."""

    BINDINGS = [
        Binding("n", "new_character", "New Character"),
        Binding("o", "open_character", "Open Character"),
        Binding("r", "resume_draft", "Resume Draft", show=False),
        Binding("a", "ai_chat", "AI Chat"),
        Binding("q", "quit", "Quit"),
        Binding("left", "prev_button", "Previous", show=False),
        Binding("right", "next_button", "Next", show=False),
        Binding("enter", "select_button", "Select", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selected_index = 0
        self.button_ids = ["btn-new", "btn-open", "btn-ai", "btn-quit"]
        self._draft_store = None
        self._has_draft = False

    @property
    def draft_store(self):
        """Lazy-load draft store."""
        if self._draft_store is None:
            from dnd_manager.storage.yaml_store import get_default_draft_store
            self._draft_store = get_default_draft_store()
        return self._draft_store

    def _get_version(self) -> str:
        """Get the application version from package metadata."""
        try:
            from importlib.metadata import version, PackageNotFoundError
            return version("ccvault")
        except PackageNotFoundError:
            return "dev"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("CCVault", id="title", classes="title"),
            Static(f"v{self._get_version()}", id="version", classes="version-label"),
            Static("CLI Character Vault for D&D 5e", classes="subtitle"),
            Static(id="draft-notice", classes="draft-notice"),
            Horizontal(
                Button("New Character", id="btn-new", variant="primary"),
                Button("Resume Draft", id="btn-resume", variant="success"),
                Button("Open Character", id="btn-open", variant="default"),
                Button("AI Chat", id="btn-ai", variant="warning"),
                Button("Quit", id="btn-quit", variant="error"),
                classes="button-row",
            ),
            id="welcome-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Check for drafts and update UI."""
        self._check_for_draft()
        self._update_button_focus()

    def _check_for_draft(self) -> None:
        """Check if there's a draft to resume."""
        draft_info = self.draft_store.get_draft_info()
        resume_btn = self.query_one("#btn-resume", Button)
        notice = self.query_one("#draft-notice", Static)

        if draft_info:
            self._has_draft = True
            self.button_ids = ["btn-new", "btn-resume", "btn-open", "btn-ai", "btn-quit"]
            resume_btn.display = True
            # Show draft info
            notice.update(f"Draft: {draft_info['name']} ({draft_info['class']} {draft_info['species']}) - Press \\[R] to resume")
            notice.display = True
        else:
            self._has_draft = False
            self.button_ids = ["btn-new", "btn-open", "btn-ai", "btn-quit"]
            resume_btn.display = False
            notice.display = False

    def _update_button_focus(self) -> None:
        """Update which button appears focused."""
        for i, btn_id in enumerate(self.button_ids):
            try:
                btn = self.query_one(f"#{btn_id}", Button)
                if btn.display:  # Only focus visible buttons
                    if i == self.selected_index:
                        btn.focus()
            except NoMatches:
                pass

    def action_prev_button(self) -> None:
        """Move to previous button."""
        self.selected_index = (self.selected_index - 1) % len(self.button_ids)
        self._update_button_focus()

    def action_next_button(self) -> None:
        """Move to next button."""
        self.selected_index = (self.selected_index + 1) % len(self.button_ids)
        self._update_button_focus()

    def action_select_button(self) -> None:
        """Activate the currently selected button."""
        btn_id = self.button_ids[self.selected_index]
        if btn_id == "btn-new":
            self.action_new_character()
        elif btn_id == "btn-resume":
            self.action_resume_draft()
        elif btn_id == "btn-open":
            self.action_open_character()
        elif btn_id == "btn-ai":
            self.action_ai_chat()
        elif btn_id == "btn-quit":
            self.action_quit()

    def action_new_character(self) -> None:
        """Create a new character (clears any existing draft)."""
        if self._has_draft:
            self.draft_store.clear_draft()
        self.app.action_new_character()

    def action_resume_draft(self) -> None:
        """Resume character creation from draft."""
        # Lazy import to avoid circular dependency
        from dnd_manager.app import CharacterCreationScreen

        draft_data = self.draft_store.load_draft()
        if draft_data:
            self.app.push_screen(CharacterCreationScreen(draft_data=draft_data))
            self.notify(f"Resuming: {draft_data.get('name', 'Unknown')}")
        else:
            self.notify("No draft found", severity="warning")
            self._check_for_draft()

    def action_open_character(self) -> None:
        """Open an existing character."""
        self.app.action_open_character(return_to_dashboard=False)

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_ai_chat(self) -> None:
        """Open unified AI assistant."""
        # Lazy import to avoid circular dependency
        from dnd_manager.app import AIOverlayScreen

        context = {
            "screen_type": "Welcome Screen",
            "description": "Home screen - starting point for the application",
        }
        self.app.push_screen(AIOverlayScreen(screen_context=context))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-new":
            self.action_new_character()
        elif event.button.id == "btn-resume":
            self.action_resume_draft()
        elif event.button.id == "btn-open":
            self.action_open_character()
        elif event.button.id == "btn-ai":
            self.action_ai_chat()
        elif event.button.id == "btn-quit":
            self.action_quit()


class CharacterListItem(Static):
    """A single character in the selection list."""

    class Selected(Message):
        """Message sent when this character item is clicked."""
        def __init__(self, index: int) -> None:
            self.index = index
            super().__init__()

    def __init__(self, char_info: dict, index: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.char_info = char_info
        self.item_index = index

    def compose(self) -> ComposeResult:
        info = self.char_info
        class_info = f"Lv {info['level']} {info['class']}"
        if info.get("subclass"):
            class_info += f" ({info['subclass']})"

        species = info.get("species") or "Unknown"
        ruleset = info.get("ruleset", "dnd2024")

        yield Static(f"  {info['name']}", classes="char-name")
        yield Static(f"    {class_info} | {species} | {ruleset}", classes="char-details")

    def on_click(self) -> None:
        """Handle click by posting a Selected message."""
        self.post_message(self.Selected(self.item_index))


class DeleteCharacterModal(ModalScreen):
    """Modal confirmation for deleting a character."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Delete"),
    ]

    def __init__(self, character_name: str, on_confirm, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character_name = character_name
        self.on_confirm = on_confirm

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Delete Character", classes="title"),
            Static(
                f"Type the character name to confirm deletion:\n\n  {self.character_name}",
                classes="subtitle",
            ),
            Input(placeholder="Type character name...", id="delete-confirm-input"),
            Horizontal(
                Button("Cancel", id="btn-cancel", variant="default"),
                Button("Delete", id="btn-delete", variant="error"),
                classes="button-row",
            ),
            id="delete-confirm-container",
        )

    def on_mount(self) -> None:
        self.query_one("#delete-confirm-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-delete":
            self.action_confirm()

    def action_cancel(self) -> None:
        self.app.pop_screen()

    def action_confirm(self) -> None:
        value = self.query_one("#delete-confirm-input", Input).value.strip()
        if value != self.character_name:
            self.notify("Name does not match. Deletion cancelled.", severity="warning")
            return
        self.on_confirm()
        self.app.pop_screen()


class CharacterSelectScreen(ListNavigationMixin, Screen):
    """Screen for selecting a character to load."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("q", "cancel", "Cancel"),
        Binding("enter", "open", "Open"),
        Binding("n", "new_character", "New Character"),
        Binding("d", "delete_character", "Delete Character"),
    ]

    def __init__(self, characters: list[dict], return_to_dashboard: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.characters = characters
        self.selected_index = 0
        self._last_letter = ""
        self._last_letter_index = -1
        self._return_to_dashboard = return_to_dashboard

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Select a Character", classes="title"),
            Static("↑/↓ Navigate  Type to jump  Enter Select  D Delete  Esc Cancel", classes="subtitle"),
            VerticalScroll(id="character-list"),
            id="select-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Populate the character list."""
        self._refresh_character_list()

    def _refresh_character_list(self) -> None:
        """Refresh the character list display."""
        list_container = self.query_one("#character-list", VerticalScroll)
        list_container.remove_children()
        for i, char_info in enumerate(self.characters):
            item = CharacterListItem(char_info, index=i, classes="char-item")
            if i == 0:
                item.add_class("selected")
            list_container.mount(item)

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.characters

    def _get_item_name(self, item) -> str:
        return item.get("name", "")

    def _get_scroll_container(self):
        try:
            return self.query_one("#character-list", VerticalScroll)
        except NoMatches:
            return None

    def _get_item_widget_class(self) -> str:
        return "char-item"

    def _update_selection(self) -> None:
        """Update the visual selection."""
        items = list(self.query(".char-item"))
        for i, item in enumerate(items):
            if i == self.selected_index:
                item.add_class("selected")
            else:
                item.remove_class("selected")
        self.call_after_refresh(self._scroll_to_selection)

    def action_cancel(self) -> None:
        """Return to welcome screen."""
        # Lazy imports to avoid circular dependency
        from dnd_manager.app import MainDashboard

        self.app.pop_screen()
        if self._return_to_dashboard and not isinstance(self.app.screen, MainDashboard):
            if self.app.current_character:
                self.app.push_screen(MainDashboard(self.app.current_character))
            elif not isinstance(self.app.screen, WelcomeScreen):
                self.app.push_screen(WelcomeScreen())

    def action_new_character(self) -> None:
        """Create new character instead."""
        self.app.pop_screen()
        self.app.action_new_character()

    def action_delete_character(self) -> None:
        """Delete the selected character with confirmation."""
        if not self.characters:
            self.notify("No characters to delete", severity="warning")
            return
        selected = self.characters[self.selected_index]
        name = selected["name"]

        def on_confirm():
            deleted = self.app.store.delete(name)
            if deleted:
                if self.app.current_character and self.app.current_character.name == name:
                    self.app.current_character = None
                self.notify(f"Deleted character: {name}")
                self.characters = self.app.store.get_character_info()
                if self.selected_index >= len(self.characters):
                    self.selected_index = max(0, len(self.characters) - 1)
                self._refresh_character_list()
                if not self.characters:
                    self.app.pop_screen()
                    if self._return_to_dashboard:
                        self.app.push_screen(WelcomeScreen())
            else:
                self.notify("Character not found", severity="warning")

        self.app.push_screen(DeleteCharacterModal(name, on_confirm))

    def key_up(self) -> None:
        """Move selection up."""
        self._navigate_up()

    def key_down(self) -> None:
        """Move selection down."""
        self._navigate_down()

    def action_open(self) -> None:
        """Select and open the current character."""
        if self.characters:
            char_info = self.characters[self.selected_index]
            self.app.load_character(char_info["path"])

    def on_key(self, event) -> None:
        """Handle letter keys for jump navigation."""
        if self._handle_key_for_letter_jump(event.key):
            event.prevent_default()

    def on_character_list_item_selected(self, event: CharacterListItem.Selected) -> None:
        """Handle mouse click on a character item."""
        if 0 <= event.index < len(self.characters):
            self.selected_index = event.index
            self._update_selection()
