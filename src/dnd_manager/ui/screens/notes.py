"""Notes screens for the D&D Manager application."""

import asyncio
from datetime import date
from typing import TYPE_CHECKING, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from dnd_manager.config import get_config_manager
from dnd_manager.ui.screens.base import ListNavigationMixin
from dnd_manager.ui.screens.widgets import ClickableListItem

if TYPE_CHECKING:
    from dnd_manager.models.character import Character


class NotesScreen(Screen):
    """Screen for viewing and editing character notes."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("e", "edit_notes", "Edit Notes"),
        Binding("b", "edit_backstory", "Edit Backstory"),
        Binding("s", "session_notes", "Session Notes"),
    ]

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Notes - {self.character.name}", classes="title"),
            Static("\\[E] Edit Notes  \\[B] Edit Backstory  \\[S] Session Notes  \\[Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("BACKSTORY", classes="panel-title"),
                    VerticalScroll(
                        Static(
                            self.character.backstory or "(No backstory yet - press B to add)",
                            id="backstory-content",
                            classes="notes-content",
                        ),
                        id="backstory-scroll",
                    ),
                    classes="panel notes-panel",
                ),
                Vertical(
                    Static("SESSION NOTES", classes="panel-title"),
                    VerticalScroll(
                        id="notes-scroll",
                    ),
                    classes="panel notes-panel",
                ),
                classes="notes-row",
            ),
            id="notes-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Populate notes on mount."""
        notes_scroll = self.query_one("#notes-scroll", VerticalScroll)
        if self.character.notes:
            for note in self.character.notes:
                notes_scroll.mount(Static(f"• {note}", classes="note-item"))
        else:
            notes_scroll.mount(Static(
                "(No notes yet - press E to add)",
                classes="notes-content",
            ))

    def _get_editor(self) -> str:
        """Get the editor to use."""
        import os
        manager = get_config_manager()
        editor = manager.get("ui.notes_editor")
        if editor:
            return editor
        return os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))

    async def _edit_text(self, current_text: str, title: str) -> Optional[str]:
        """Open external editor and return edited text."""
        import os
        import tempfile
        import subprocess

        editor = self._get_editor()

        # Create temp file with current content
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".md",
            prefix=f"dnd_{title}_",
            delete=False,
        ) as f:
            f.write(current_text or "")
            temp_path = f.name

        try:
            # Suspend the TUI and run editor
            with self.app.suspend():
                result = subprocess.run([editor, temp_path])

            if result.returncode == 0:
                with open(temp_path) as f:
                    return f.read()
            return None
        finally:
            os.unlink(temp_path)

    async def action_edit_backstory(self) -> None:
        """Edit backstory in external editor."""
        new_text = await self._edit_text(
            self.character.backstory or "",
            "backstory",
        )
        if new_text is not None:
            self.character.backstory = new_text.strip()
            self.app.save_character()
            # Update display
            content = self.query_one("#backstory-content", Static)
            content.update(self.character.backstory or "(No backstory yet - press B to add)")
            self.notify("Backstory updated!")

    async def action_edit_notes(self) -> None:
        """Edit notes in external editor."""
        # Join existing notes for editing
        current_notes = "\n".join(self.character.notes) if self.character.notes else ""
        new_text = await self._edit_text(current_notes, "notes")

        if new_text is not None:
            # Split by lines, filter empty
            self.character.notes = [
                line.strip() for line in new_text.strip().split("\n")
                if line.strip()
            ]
            self.app.save_character()

            # Refresh display
            notes_scroll = self.query_one("#notes-scroll", VerticalScroll)
            notes_scroll.remove_children()
            if self.character.notes:
                for note in self.character.notes:
                    notes_scroll.mount(Static(f"• {note}", classes="note-item"))
            else:
                notes_scroll.mount(Static(
                    "(No notes yet - press E to add)",
                    classes="notes-content",
                ))
            self.notify("Notes updated!")

    def action_session_notes(self) -> None:
        """Open session notes screen."""
        self.app.push_screen(SessionNotesScreen(self.character))

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()


class SessionNotesScreen(ListNavigationMixin, Screen):
    """Screen for managing session notes with vector search."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "edit_note", "Edit Note"),
        Binding("+", "new_note", "New Note"),
        Binding("-", "delete_note", "Delete Note"),
        Binding("/", "search", "Search"),
    ]

    def __init__(self, character: Optional["Character"] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_index = 0
        self.notes: list = []
        self.search_query = ""
        self.use_semantic = True
        self._store = None
        self._last_letter = ""
        self._last_letter_index = -1

    @property
    def store(self):
        """Get the notes store."""
        if self._store is None:
            from dnd_manager.storage.notes import get_notes_store
            self._store = get_notes_store()
        return self._store

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Session Notes", classes="title"),
            Static("\\[N] New  \\[E] Edit  \\[D] Delete  / Search  \\[S] Toggle Semantic", classes="subtitle"),
            Horizontal(
                Input(placeholder="Search notes...", id="notes-search"),
                Static(id="search-mode", classes="search-mode"),
                classes="search-row",
            ),
            Horizontal(
                Vertical(
                    Static("NOTES", classes="panel-title"),
                    VerticalScroll(id="notes-list", classes="notes-list"),
                    classes="panel notes-list-panel",
                ),
                Vertical(
                    Static("NOTE CONTENT", classes="panel-title"),
                    VerticalScroll(id="note-content", classes="note-content-panel"),
                    classes="panel note-detail-panel",
                ),
                classes="session-notes-row",
            ),
            id="session-notes-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load notes on mount."""
        self._update_search_mode()
        self._load_notes()

    def _update_search_mode(self) -> None:
        """Update the search mode indicator."""
        mode_widget = self.query_one("#search-mode", Static)
        if self.store.embedding_engine.is_available() and self.use_semantic:
            mode_widget.update("[Semantic Search]")
        else:
            mode_widget.update("[Keyword Search]")

    def _load_notes(self) -> None:
        """Load notes from storage."""
        character_id = None
        if self.character:
            character_id = self.character.meta.id if hasattr(self.character.meta, 'id') else None

        if self.search_query:
            # Search notes
            results = self.store.search(
                self.search_query,
                use_semantic=self.use_semantic,
            )
            self.notes = [r.note for r in results]
        else:
            # Get all notes
            self.notes = self.store.get_all(character_id=character_id, limit=100)

        self._refresh_list()

    def _refresh_list(self) -> None:
        """Refresh the notes list display."""
        list_widget = self.query_one("#notes-list", VerticalScroll)
        list_widget.remove_children()

        if not self.notes:
            list_widget.mount(Static("  (No notes found)", classes="no-items"))
            self._show_note_content(None)
            return

        for i, note in enumerate(self.notes):
            selected = "▶ " if i == self.selected_index else "  "
            date_str = note.session_date.strftime("%Y-%m-%d") if note.session_date else "No date"
            title = note.title if note.title else "(Untitled)"

            list_widget.mount(ClickableListItem(
                f"{selected}{date_str} - {title}",
                index=i,
                classes=f"note-list-item {'selected' if i == self.selected_index else ''}",
            ))

        # Show content of selected note
        if 0 <= self.selected_index < len(self.notes):
            self._show_note_content(self.notes[self.selected_index])

    def _show_note_content(self, note) -> None:
        """Show content of the selected note."""
        content_widget = self.query_one("#note-content", VerticalScroll)
        content_widget.remove_children()

        if note is None:
            content_widget.mount(Static("  (Select a note to view)", classes="no-content"))
            return

        content_widget.mount(Static(f"  {note.title}", classes="note-title"))
        content_widget.mount(Static(f"  Date: {note.session_date}", classes="note-meta"))

        if note.campaign:
            content_widget.mount(Static(f"  Campaign: {note.campaign}", classes="note-meta"))

        if note.tags:
            content_widget.mount(Static(f"  Tags: {', '.join(note.tags)}", classes="note-meta"))

        content_widget.mount(Static("  ─────────────────────────────────", classes="separator"))
        content_widget.mount(Static(""))

        # Word wrap content
        for line in note.content.split("\n"):
            content_widget.mount(Static(f"  {line}", classes="note-text"))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "notes-search":
            self.search_query = event.value
            self.selected_index = 0
            self._load_notes()

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.notes

    def _get_item_name(self, item) -> str:
        return item.title or ""

    def _get_scroll_container(self):
        try:
            return self.query_one("#notes-list", VerticalScroll)
        except NoMatches:
            return None

    def _get_item_widget_class(self) -> str:
        return "note-list-item"

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
            if self.query_one("#notes-search", Input).has_focus:
                return
        except NoMatches:
            pass
        if self._handle_key_for_letter_jump(event.key):
            event.prevent_default()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        """Handle mouse click on a list item."""
        if 0 <= event.index < len(self.notes):
            self.selected_index = event.index
            self._update_selection()

    async def action_new_note(self) -> None:
        """Create a new note."""
        self.app.push_screen(NoteEditorScreen(character=self.character, on_save=self._on_note_saved))

    def _on_note_saved(self) -> None:
        """Callback when a note is saved."""
        self._load_notes()

    async def action_edit_note(self) -> None:
        """Edit the selected note."""
        if 0 <= self.selected_index < len(self.notes):
            note = self.notes[self.selected_index]
            self.app.push_screen(NoteEditorScreen(
                character=self.character,
                note=note,
                on_save=self._on_note_saved,
            ))

    def action_delete_note(self) -> None:
        """Delete the selected note."""
        if 0 <= self.selected_index < len(self.notes):
            note = self.notes[self.selected_index]
            if note.id:
                self.store.delete(note.id)
                self.notify(f"Deleted note: {note.title}")
                self.selected_index = max(0, self.selected_index - 1)
                self._load_notes()

    def action_search(self) -> None:
        """Focus search input."""
        self.query_one("#notes-search", Input).focus()

    def action_toggle_semantic(self) -> None:
        """Toggle semantic search."""
        if self.store.embedding_engine.is_available():
            self.use_semantic = not self.use_semantic
            self._update_search_mode()
            if self.search_query:
                self._load_notes()
            mode = "Semantic" if self.use_semantic else "Keyword"
            self.notify(f"Search mode: {mode}")
        else:
            self.notify("Semantic search not available (install sentence-transformers)", severity="warning")

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


class NoteEditorScreen(Screen):
    """Screen for editing a session note."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(
        self,
        character: Optional["Character"] = None,
        note=None,
        on_save=None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.note = note
        self.on_save = on_save
        self._store = None

    @property
    def store(self):
        """Get the notes store."""
        if self._store is None:
            from dnd_manager.storage.notes import get_notes_store
            self._store = get_notes_store()
        return self._store

    def compose(self) -> ComposeResult:
        title = "Edit Note" if self.note else "New Note"
        yield Header()
        yield Container(
            Static(title, classes="title"),
            Static("\\[Ctrl+S] Save  \\[Esc] Cancel", classes="subtitle"),
            Vertical(
                Static("Title:", classes="field-label"),
                Input(
                    value=self.note.title if self.note else "",
                    placeholder="Note title...",
                    id="note-title-input",
                ),
                Horizontal(
                    Vertical(
                        Static("Date:", classes="field-label"),
                        Input(
                            value=str(self.note.session_date) if self.note else str(date.today()),
                            placeholder="YYYY-MM-DD",
                            id="note-date-input",
                        ),
                        classes="field-half",
                    ),
                    Vertical(
                        Static("Campaign:", classes="field-label"),
                        Input(
                            value=self.note.campaign if self.note and self.note.campaign else "",
                            placeholder="Campaign name...",
                            id="note-campaign-input",
                        ),
                        classes="field-half",
                    ),
                    classes="field-row",
                ),
                Static("Tags (comma-separated):", classes="field-label"),
                Input(
                    value=", ".join(self.note.tags) if self.note and self.note.tags else "",
                    placeholder="combat, roleplay, loot...",
                    id="note-tags-input",
                ),
                Static("Content:", classes="field-label"),
                Input(
                    value=self.note.content if self.note else "",
                    placeholder="Note content... (Press E to open in editor)",
                    id="note-content-input",
                ),
                Static(""),
                Button("Open in External Editor", id="btn-editor", variant="default"),
                Static(""),
                Horizontal(
                    Button("Save", id="btn-save", variant="primary"),
                    Button("Cancel", id="btn-cancel", variant="error"),
                    classes="button-row",
                ),
                classes="panel note-editor-panel",
            ),
            id="note-editor-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus title input on mount."""
        self.query_one("#note-title-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key - save the note."""
        # Enter in any field saves the note (Ctrl+S also works)
        self.action_save()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-save":
            self.action_save()
        elif event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-editor":
            asyncio.create_task(self._open_editor())

    async def _open_editor(self) -> None:
        """Open content in external editor."""
        import os
        import tempfile
        import subprocess

        manager = get_config_manager()
        editor = manager.get("ui.notes_editor")
        if not editor:
            editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))

        current_content = self.query_one("#note-content-input", Input).value

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".md",
            prefix="session_note_",
            delete=False,
        ) as f:
            f.write(current_content)
            temp_path = f.name

        try:
            with self.app.suspend():
                subprocess.run([editor, temp_path])

            with open(temp_path) as f:
                new_content = f.read()

            self.query_one("#note-content-input", Input).value = new_content.strip()
            self.notify("Content updated from editor")
        finally:
            os.unlink(temp_path)

    def action_save(self) -> None:
        """Save the note."""
        from dnd_manager.storage.notes import SessionNote
        from datetime import date as date_type

        title = self.query_one("#note-title-input", Input).value.strip()
        date_str = self.query_one("#note-date-input", Input).value.strip()
        campaign = self.query_one("#note-campaign-input", Input).value.strip() or None
        tags_str = self.query_one("#note-tags-input", Input).value.strip()
        content = self.query_one("#note-content-input", Input).value.strip()

        if not title:
            self.notify("Title is required", severity="error")
            return

        if not content:
            self.notify("Content is required", severity="error")
            return

        # Parse date
        try:
            session_date = date_type.fromisoformat(date_str)
        except ValueError:
            session_date = date_type.today()

        # Parse tags
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        # Get character ID
        character_id = None
        if self.character:
            character_id = self.character.meta.id if hasattr(self.character.meta, 'id') else None

        if self.note:
            # Update existing
            self.note.title = title
            self.note.session_date = session_date
            self.note.campaign = campaign
            self.note.tags = tags
            self.note.content = content
            self.store.update(self.note)
            self.notify("Note updated!")
        else:
            # Create new
            new_note = SessionNote(
                title=title,
                session_date=session_date,
                campaign=campaign,
                character_id=character_id,
                tags=tags,
                content=content,
            )
            self.store.add(new_note)
            self.notify("Note created!")

        if self.on_save:
            self.on_save()

        self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel editing."""
        self.app.pop_screen()
