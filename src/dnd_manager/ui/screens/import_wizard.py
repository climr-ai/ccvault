"""Import wizard screen for reviewing and editing imported character data."""

import asyncio
from pathlib import Path
from typing import Any, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, Footer, Header, Input, Static, OptionList, LoadingIndicator
from textual.widgets.option_list import Option
from textual.worker import Worker, get_current_worker

from dnd_manager.import_char.session import ImportSession, ParsedCharacterData
from dnd_manager.ui.screens.base import ScreenContextMixin, ListNavigationMixin
from dnd_manager.ui.screens.widgets import CreationOptionList


# Confidence thresholds
LOW_CONFIDENCE = 0.7
VERY_LOW_CONFIDENCE = 0.5


class ImportFilePickerScreen(Screen):
    """Screen for selecting a PDF file to import."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "Import"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source_type = "auto"
        self._is_importing = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Import Character from PDF", classes="title"),
            Static(
                "Enter the path to a PDF character sheet.\n"
                "Supported sources: D&D Beyond, Roll20, or generic character sheets.",
                classes="subtitle",
            ),
            Vertical(
                Static("PDF File Path:", classes="input-label"),
                Input(
                    placeholder="Enter path to PDF file...",
                    id="file-path-input",
                ),
                Static("Source Type:", classes="input-label"),
                Horizontal(
                    Button("Auto-detect", id="btn-auto", variant="primary"),
                    Button("D&D Beyond", id="btn-dndbeyond", variant="default"),
                    Button("Roll20", id="btn-roll20", variant="default"),
                    Button("Generic", id="btn-generic", variant="default"),
                    classes="source-row",
                ),
                Static(id="status-message", classes="status-message"),
                LoadingIndicator(id="loading", classes="hidden"),
                classes="import-form",
            ),
            Horizontal(
                Button("Cancel", id="btn-cancel", variant="error"),
                Button("Import", id="btn-import", variant="success"),
                classes="button-row",
            ),
            id="import-picker-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#file-path-input", Input).focus()
        self.query_one("#loading").display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id

        if btn_id == "btn-cancel":
            self.action_cancel()
        elif btn_id == "btn-import":
            self.action_submit()
        elif btn_id in ("btn-auto", "btn-dndbeyond", "btn-roll20", "btn-generic"):
            # Update source type selection
            self.source_type = {
                "btn-auto": "auto",
                "btn-dndbeyond": "dndbeyond",
                "btn-roll20": "roll20",
                "btn-generic": "generic",
            }[btn_id]
            # Update button styles
            for bid in ("btn-auto", "btn-dndbeyond", "btn-roll20", "btn-generic"):
                btn = self.query_one(f"#{bid}", Button)
                btn.variant = "primary" if bid == btn_id else "default"

    def action_cancel(self) -> None:
        self.app.pop_screen()

    def action_submit(self) -> None:
        if self._is_importing:
            return

        file_path = self.query_one("#file-path-input", Input).value.strip()
        status = self.query_one("#status-message", Static)

        if not file_path:
            status.update("[red]Please enter a file path[/]")
            return

        # Expand user path
        path = Path(file_path).expanduser()

        if not path.exists():
            status.update(f"[red]File not found: {path}[/]")
            return

        if not path.suffix.lower() == ".pdf":
            status.update("[red]File must be a PDF[/]")
            return

        # Start import process
        self._is_importing = True
        status.update("[cyan]Starting import...[/]")
        self.query_one("#loading").display = True
        self.query_one("#btn-import", Button).disabled = True

        # Run import in background worker
        self.run_worker(
            self._do_import(path, self.source_type),
            name="import_pdf",
            exclusive=True,
        )

    async def _do_import(self, path: Path, source_type: str) -> Optional[ImportSession]:
        """Perform the import in a background worker."""
        status = self.query_one("#status-message", Static)

        try:
            from dnd_manager.import_char import PDFReader, CharacterSheetParser, ImportSession

            # Step 1: Convert PDF to images
            status.update("[cyan]Converting PDF to images...[/]")
            reader = PDFReader(dpi=150)
            images = reader.convert_to_image_bytes(path)

            if not images:
                self.call_from_thread(
                    status.update, "[red]Failed to extract images from PDF[/]"
                )
                return None

            self.call_from_thread(
                status.update, f"[cyan]Extracted {len(images)} pages. Parsing with AI...[/]"
            )

            # Step 2: Parse with AI
            parser = CharacterSheetParser()
            parsed_data = await parser.parse_full_sheet(images, source_type)

            if not parsed_data.name and not parsed_data.class_name:
                self.call_from_thread(
                    status.update, "[red]Failed to parse character data from PDF[/]"
                )
                return None

            # Step 3: Create import session
            session = ImportSession(
                source_file=path,
                source_type=source_type,
                parsed_data=parsed_data,
            )

            return session

        except Exception as e:
            self.call_from_thread(
                status.update, f"[red]Import failed: {e}[/]"
            )
            return None

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.worker.name == "import_pdf":
            self.query_one("#loading").display = False
            self.query_one("#btn-import", Button).disabled = False
            self._is_importing = False

            if event.worker.is_finished and event.worker.result:
                session = event.worker.result
                # Push the wizard screen
                self.app.pop_screen()
                self.app.push_screen(ImportWizardScreen(session))


class FieldEditorModal(ModalScreen):
    """Modal for editing a single field value."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "Save"),
    ]

    def __init__(
        self,
        field_name: str,
        current_value: Any,
        field_type: str = "text",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.field_name = field_name
        self.current_value = current_value
        self.field_type = field_type
        self.result: Optional[Any] = None

    def compose(self) -> ComposeResult:
        display_name = self.field_name.replace("_", " ").title()
        yield Container(
            Static(f"Edit {display_name}", classes="modal-title"),
            Input(
                value=str(self.current_value) if self.current_value else "",
                placeholder=f"Enter {display_name.lower()}...",
                id="field-input",
            ),
            Horizontal(
                Button("Cancel", id="btn-cancel", variant="error"),
                Button("Save", id="btn-save", variant="success"),
                classes="button-row",
            ),
            id="editor-modal",
            classes="modal-content",
        )

    def on_mount(self) -> None:
        self.query_one("#field-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.action_submit()
        else:
            self.action_cancel()

    def action_submit(self) -> None:
        value = self.query_one("#field-input", Input).value
        # Convert value based on field type
        if self.field_type == "int":
            try:
                self.result = int(value) if value else None
            except ValueError:
                self.notify("Please enter a valid number", severity="error")
                return
        else:
            self.result = value if value else None
        self.dismiss(self.result)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ImportWizardScreen(Screen, ScreenContextMixin, ListNavigationMixin):
    """Multi-step wizard for reviewing and editing imported character data."""

    BINDINGS = [
        Binding("escape", "back_or_cancel", "Back/Cancel", priority=True),
        Binding("enter", "select", "Select/Edit"),
        Binding("up", "nav_up", "Up", show=False),
        Binding("down", "nav_down", "Down", show=False),
        Binding("left", "prev_step", "Previous Step", show=False),
        Binding("right", "next_step", "Next Step", show=False),
        Binding("tab", "focus_next", "Focus Next", show=False),
    ]

    # Steps in the wizard
    ALL_STEPS = [
        "overview",
        "identity",
        "abilities",
        "proficiencies",
        "features",
        "spells",
        "equipment",
        "confirm",
    ]

    def __init__(self, session: ImportSession, **kwargs):
        super().__init__(**kwargs)
        self.session = session
        self.step = 0
        self.selected_option = 0
        self.current_options: list[str] = []
        self._expected_highlight = 0

    @property
    def steps(self) -> list[str]:
        """Get active steps based on import data."""
        active = []
        for step in self.ALL_STEPS:
            # Skip spells step if no spellcasting data
            if step == "spells":
                data = self.session.parsed_data
                has_spells = (
                    data.cantrips or
                    data.spells_known or
                    data.spells_prepared or
                    data.spellcasting_ability
                )
                if not has_spells:
                    continue
            active.append(step)
        return active

    def get_ai_context(self) -> dict:
        """Provide import context for AI."""
        step_name = self.steps[self.step] if self.step < len(self.steps) else "unknown"
        return {
            "screen_type": "Import Review Wizard",
            "description": f"Reviewing imported character - {step_name}",
            "data": {
                "current_step": step_name,
                "source_type": self.session.source_type,
                "character_name": self.session.get_field("name"),
                "low_confidence_fields": self.session.parsed_data.get_low_confidence_fields(),
            },
        }

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Import Character", classes="title"),
            Static(id="step-indicator", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static(id="step-title", classes="panel-title"),
                    CreationOptionList(id="options-list", classes="options-list"),
                    Static(id="step-description"),
                    classes="panel creation-panel creation-left",
                ),
                VerticalScroll(
                    Static(id="detail-title", classes="panel-title"),
                    Static(id="detail-content"),
                    id="detail-panel",
                    classes="panel creation-panel creation-right",
                    can_focus=True,
                ),
                classes="creation-row",
            ),
            Horizontal(
                Button("Cancel", id="btn-cancel", variant="error"),
                Button("Back", id="btn-back", variant="default"),
                Button("Next", id="btn-next", variant="primary"),
                classes="button-row",
            ),
            id="import-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the first step."""
        self._show_step()
        try:
            self.query_one("#options-list", OptionList).focus()
        except NoMatches:
            pass

    def _show_step(self) -> None:
        """Display the current step."""
        step_name = self.steps[self.step]

        # Update step indicator
        indicator = self.query_one("#step-indicator", Static)
        total_steps = len(self.steps)
        current = self.step + 1

        step_icons = []
        step_labels = {
            "overview": "Overview",
            "identity": "Identity",
            "abilities": "Abilities",
            "proficiencies": "Proficiencies",
            "features": "Features",
            "spells": "Spells",
            "equipment": "Equipment",
            "confirm": "Confirm",
        }
        for i in range(len(self.steps)):
            if i < self.step:
                step_icons.append("[green]●[/]")
            elif i == self.step:
                step_icons.append("[cyan]◉[/]")
            else:
                step_icons.append("○")

        progress_bar = " ".join(step_icons)
        current_label = step_labels.get(step_name, step_name.title())
        indicator.update(f"{progress_bar}\nStep {current}/{total_steps}: {current_label}")

        title = self.query_one("#step-title", Static)
        description = self.query_one("#step-description", Static)

        # Update buttons
        back_btn = self.query_one("#btn-back", Button)
        next_btn = self.query_one("#btn-next", Button)
        back_btn.disabled = self.step == 0
        next_btn.label = "Save Character" if step_name == "confirm" else "Next"

        # Step-specific content
        if step_name == "overview":
            self._show_overview(title, description)
        elif step_name == "identity":
            self._show_identity(title, description)
        elif step_name == "abilities":
            self._show_abilities(title, description)
        elif step_name == "proficiencies":
            self._show_proficiencies(title, description)
        elif step_name == "features":
            self._show_features(title, description)
        elif step_name == "spells":
            self._show_spells(title, description)
        elif step_name == "equipment":
            self._show_equipment(title, description)
        elif step_name == "confirm":
            self._show_confirm(title, description)

    def _format_field_with_confidence(
        self, name: str, value: Any, section: str = ""
    ) -> str:
        """Format a field name with confidence indicator."""
        confidence = self.session.parsed_data.get_confidence(section or name)
        indicator = ""
        if confidence < VERY_LOW_CONFIDENCE:
            indicator = " [red]!![/]"
        elif confidence < LOW_CONFIDENCE:
            indicator = " [yellow]![/]"

        overridden = name in self.session.manual_overrides
        if overridden:
            indicator += " [cyan]*[/]"

        display_name = name.replace("_", " ").title()
        display_value = value if value is not None else "-"

        if isinstance(display_value, list):
            display_value = ", ".join(str(v) for v in display_value) or "-"

        return f"{display_name}: {display_value}{indicator}"

    def _show_overview(self, title: Static, description: Static) -> None:
        """Show overview of all parsed data."""
        title.update("IMPORT OVERVIEW")
        low_conf = self.session.parsed_data.get_low_confidence_fields()
        if low_conf:
            description.update(
                f"[yellow]Fields with low confidence:[/] {', '.join(low_conf)}\n"
                "Press Enter to review sections"
            )
        else:
            description.update("All fields parsed with good confidence")

        # Build summary options
        self.current_options = [
            "Character Summary",
            "Ability Scores",
            "Proficiencies",
            "Features & Traits",
            "Spellcasting",
            "Equipment",
        ]
        self._refresh_options()

    def _show_identity(self, title: Static, description: Static) -> None:
        """Show identity fields for review."""
        title.update("IDENTITY")
        description.update("Review character identity. Press Enter to edit a field.")

        data = self.session.parsed_data
        self.current_options = [
            self._format_field_with_confidence("name", self.session.get_field("name"), "identity"),
            self._format_field_with_confidence("class_name", self.session.get_field("class_name"), "identity"),
            self._format_field_with_confidence("level", self.session.get_field("level"), "identity"),
            self._format_field_with_confidence("subclass", self.session.get_field("subclass"), "identity"),
            self._format_field_with_confidence("species", self.session.get_field("species"), "identity"),
            self._format_field_with_confidence("subspecies", self.session.get_field("subspecies"), "identity"),
            self._format_field_with_confidence("background", self.session.get_field("background"), "identity"),
            self._format_field_with_confidence("alignment", self.session.get_field("alignment"), "identity"),
        ]
        self._refresh_options()

    def _show_abilities(self, title: Static, description: Static) -> None:
        """Show ability scores for review."""
        title.update("ABILITY SCORES")
        description.update("Review ability scores. Press Enter to edit.")

        self.current_options = [
            self._format_field_with_confidence("strength", self.session.get_field("strength"), "abilities"),
            self._format_field_with_confidence("dexterity", self.session.get_field("dexterity"), "abilities"),
            self._format_field_with_confidence("constitution", self.session.get_field("constitution"), "abilities"),
            self._format_field_with_confidence("intelligence", self.session.get_field("intelligence"), "abilities"),
            self._format_field_with_confidence("wisdom", self.session.get_field("wisdom"), "abilities"),
            self._format_field_with_confidence("charisma", self.session.get_field("charisma"), "abilities"),
        ]
        self._refresh_options()

    def _show_proficiencies(self, title: Static, description: Static) -> None:
        """Show proficiencies for review."""
        title.update("PROFICIENCIES")
        description.update("Review proficiencies. Press Enter to edit.")

        self.current_options = [
            self._format_field_with_confidence(
                "skill_proficiencies",
                self.session.get_field("skill_proficiencies"),
                "proficiencies"
            ),
            self._format_field_with_confidence(
                "saving_throw_proficiencies",
                self.session.get_field("saving_throw_proficiencies"),
                "proficiencies"
            ),
            self._format_field_with_confidence(
                "languages",
                self.session.get_field("languages"),
                "proficiencies"
            ),
            self._format_field_with_confidence(
                "armor_proficiencies",
                self.session.get_field("armor_proficiencies"),
                "proficiencies"
            ),
            self._format_field_with_confidence(
                "weapon_proficiencies",
                self.session.get_field("weapon_proficiencies"),
                "proficiencies"
            ),
            self._format_field_with_confidence(
                "tool_proficiencies",
                self.session.get_field("tool_proficiencies"),
                "proficiencies"
            ),
        ]
        self._refresh_options()

    def _show_features(self, title: Static, description: Static) -> None:
        """Show features for review."""
        title.update("FEATURES")
        description.update("Review class and racial features.")

        features = self.session.get_field("features") or []
        if features:
            self.current_options = [f["name"] for f in features]
        else:
            self.current_options = ["(No features parsed)"]
        self._refresh_options()

    def _show_spells(self, title: Static, description: Static) -> None:
        """Show spellcasting for review."""
        title.update("SPELLCASTING")
        description.update("Review spells and cantrips.")

        cantrips = self.session.get_field("cantrips") or []
        known = self.session.get_field("spells_known") or []
        prepared = self.session.get_field("spells_prepared") or []

        self.current_options = [
            f"Cantrips ({len(cantrips)})",
            f"Spells Known ({len(known)})",
            f"Prepared Spells ({len(prepared)})",
            self._format_field_with_confidence(
                "spellcasting_ability",
                self.session.get_field("spellcasting_ability"),
                "spellcasting"
            ),
        ]
        self._refresh_options()

    def _show_equipment(self, title: Static, description: Static) -> None:
        """Show equipment for review."""
        title.update("EQUIPMENT")
        description.update("Review equipment and currency.")

        equipment = self.session.get_field("equipment") or []
        currency = self.session.get_field("currency") or {}

        currency_str = ", ".join(
            f"{v} {k}" for k, v in currency.items() if v
        ) or "None"

        self.current_options = [
            f"Items ({len(equipment)})",
            f"Currency: {currency_str}",
        ]
        self._refresh_options()

    def _show_confirm(self, title: Static, description: Static) -> None:
        """Show final confirmation."""
        title.update("CONFIRM IMPORT")

        is_complete, missing = self.session.is_complete()
        if is_complete:
            description.update(
                "[green]Character is ready to save![/]\n"
                "Press Save Character to create the character."
            )
        else:
            description.update(
                f"[red]Missing required fields:[/] {', '.join(missing)}\n"
                "Go back to fill in the missing data."
            )

        self.current_options = [
            "Character Summary",
            "Save Character" if is_complete else "(Missing required data)",
        ]
        self._refresh_options()

    def _refresh_options(self) -> None:
        """Rebuild the options list."""
        try:
            options_list = self.query_one("#options-list", OptionList)
        except NoMatches:
            return

        options_list.clear_options()
        for i, option in enumerate(self.current_options):
            options_list.add_option(Option(option, id=f"opt_{i}"))

        if self.current_options and self.selected_option < len(self.current_options):
            self._expected_highlight = self.selected_option
            options_list.highlighted = self.selected_option
        else:
            self._expected_highlight = 0
            self.selected_option = 0

        self._refresh_details()

    def _refresh_details(self) -> None:
        """Update the detail panel."""
        try:
            detail_title = self.query_one("#detail-title", Static)
            detail_content = self.query_one("#detail-content", Static)
        except NoMatches:
            return

        step_name = self.steps[self.step] if self.step < len(self.steps) else ""

        if not self.current_options:
            detail_title.update("")
            detail_content.update("No data available")
            return

        if self.selected_option >= len(self.current_options):
            return

        selected = self.current_options[self.selected_option]

        if step_name == "overview":
            self._show_overview_detail(selected, detail_title, detail_content)
        elif step_name == "identity":
            self._show_identity_detail(selected, detail_title, detail_content)
        elif step_name == "abilities":
            self._show_ability_detail(selected, detail_title, detail_content)
        elif step_name == "proficiencies":
            self._show_proficiency_detail(selected, detail_title, detail_content)
        elif step_name == "features":
            self._show_feature_detail(selected, detail_title, detail_content)
        elif step_name == "spells":
            self._show_spell_detail(selected, detail_title, detail_content)
        elif step_name == "equipment":
            self._show_equipment_detail(selected, detail_title, detail_content)
        elif step_name == "confirm":
            self._show_confirm_detail(selected, detail_title, detail_content)

    def _show_overview_detail(
        self, selected: str, title: Static, content: Static
    ) -> None:
        """Show detail for overview section."""
        if "Summary" in selected:
            title.update("Character Summary")
            name = self.session.get_field("name") or "Unknown"
            cls = self.session.get_field("class_name") or "Unknown"
            level = self.session.get_field("level") or 1
            species = self.session.get_field("species") or "Unknown"
            bg = self.session.get_field("background") or "Unknown"

            content.update(
                f"[bold]{name}[/]\n\n"
                f"Level {level} {species} {cls}\n"
                f"Background: {bg}\n\n"
                f"Source: {self.session.source_type}\n"
                f"File: {self.session.source_file.name}"
            )
        elif "Ability" in selected:
            title.update("Ability Scores")
            abilities = []
            for ab in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                val = self.session.get_field(ab) or "-"
                abilities.append(f"{ab[:3].upper()}: {val}")
            content.update("\n".join(abilities))
        elif "Proficiencies" in selected:
            title.update("Proficiencies")
            skills = self.session.get_field("skill_proficiencies") or []
            saves = self.session.get_field("saving_throw_proficiencies") or []
            content.update(
                f"Skills: {', '.join(skills) or 'None'}\n\n"
                f"Saving Throws: {', '.join(saves) or 'None'}"
            )
        elif "Features" in selected:
            title.update("Features")
            features = self.session.get_field("features") or []
            if features:
                content.update("\n".join(f["name"] for f in features[:10]))
            else:
                content.update("No features parsed")
        elif "Spell" in selected:
            title.update("Spellcasting")
            cantrips = self.session.get_field("cantrips") or []
            known = self.session.get_field("spells_known") or []
            content.update(
                f"Cantrips: {len(cantrips)}\n"
                f"Spells: {len(known)}"
            )
        elif "Equipment" in selected:
            title.update("Equipment")
            equipment = self.session.get_field("equipment") or []
            content.update(f"{len(equipment)} items")

    def _show_identity_detail(
        self, selected: str, title: Static, content: Static
    ) -> None:
        """Show detail for identity field."""
        # Extract field name from formatted string
        field_name = selected.split(":")[0].lower().replace(" ", "_")
        confidence = self.session.parsed_data.get_confidence("identity")

        title.update(field_name.replace("_", " ").title())

        info = f"[bold]Current Value:[/] {self.session.get_field(field_name) or '-'}\n\n"
        info += f"Confidence: {confidence:.0%}\n"

        if field_name in self.session.manual_overrides:
            info += "[cyan]* Manually overridden[/]\n"

        info += "\n[dim]Press Enter to edit[/]"
        content.update(info)

    def _show_ability_detail(
        self, selected: str, title: Static, content: Static
    ) -> None:
        """Show detail for ability score."""
        field_name = selected.split(":")[0].lower().replace(" ", "_")
        value = self.session.get_field(field_name)
        confidence = self.session.parsed_data.get_confidence("abilities")

        title.update(field_name.title())

        modifier = (value - 10) // 2 if value else 0
        mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)

        info = f"[bold]Score:[/] {value or '-'}\n"
        info += f"[bold]Modifier:[/] {mod_str}\n\n"
        info += f"Confidence: {confidence:.0%}\n"

        if field_name in self.session.manual_overrides:
            info += "[cyan]* Manually overridden[/]\n"

        info += "\n[dim]Press Enter to edit[/]"
        content.update(info)

    def _show_proficiency_detail(
        self, selected: str, title: Static, content: Static
    ) -> None:
        """Show detail for proficiency list."""
        field_name = selected.split(":")[0].lower().replace(" ", "_")
        values = self.session.get_field(field_name) or []

        title.update(field_name.replace("_", " ").title())

        if values:
            info = "\n".join(f"- {v}" for v in values)
        else:
            info = "(None)"

        content.update(info)

    def _show_feature_detail(
        self, selected: str, title: Static, content: Static
    ) -> None:
        """Show detail for a feature."""
        features = self.session.get_field("features") or []
        feature = next((f for f in features if f["name"] == selected), None)

        if feature:
            title.update(feature["name"])
            info = f"[bold]Source:[/] {feature.get('source', 'Unknown')}\n\n"
            info += feature.get("description", "No description available")
        else:
            title.update(selected)
            info = "No details available"

        content.update(info)

    def _show_spell_detail(
        self, selected: str, title: Static, content: Static
    ) -> None:
        """Show detail for spells."""
        if "Cantrips" in selected:
            title.update("Cantrips")
            cantrips = self.session.get_field("cantrips") or []
            content.update("\n".join(f"- {c}" for c in cantrips) or "(None)")
        elif "Known" in selected:
            title.update("Spells Known")
            known = self.session.get_field("spells_known") or []
            content.update("\n".join(f"- {s}" for s in known) or "(None)")
        elif "Prepared" in selected:
            title.update("Prepared Spells")
            prepared = self.session.get_field("spells_prepared") or []
            content.update("\n".join(f"- {s}" for s in prepared) or "(None)")
        else:
            self._show_identity_detail(selected, title, content)

    def _show_equipment_detail(
        self, selected: str, title: Static, content: Static
    ) -> None:
        """Show detail for equipment."""
        if "Items" in selected:
            title.update("Equipment")
            equipment = self.session.get_field("equipment") or []
            if equipment:
                items = []
                for item in equipment[:20]:
                    name = item.get("name", "Unknown")
                    qty = item.get("quantity", 1)
                    if qty > 1:
                        items.append(f"- {name} x{qty}")
                    else:
                        items.append(f"- {name}")
                content.update("\n".join(items))
            else:
                content.update("(No items)")
        else:
            title.update("Currency")
            currency = self.session.get_field("currency") or {}
            lines = []
            for coin, amount in currency.items():
                if amount:
                    lines.append(f"{coin.upper()}: {amount}")
            content.update("\n".join(lines) or "(No currency)")

    def _show_confirm_detail(
        self, selected: str, title: Static, content: Static
    ) -> None:
        """Show detail for confirmation."""
        if "Summary" in selected:
            self._show_overview_detail("Character Summary", title, content)
        else:
            is_complete, missing = self.session.is_complete()
            title.update("Import Status")
            if is_complete:
                content.update(
                    "[green]Ready to save![/]\n\n"
                    "The character will be created with the imported data.\n"
                    "You can edit the character further after saving."
                )
            else:
                content.update(
                    "[red]Cannot save yet.[/]\n\n"
                    f"Missing required fields:\n" +
                    "\n".join(f"- {m}" for m in missing)
                )

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Handle option highlighting."""
        if event.option_list.id == "options-list":
            if event.option_index != self._expected_highlight:
                self.selected_option = event.option_index
                self._expected_highlight = event.option_index
                self._refresh_details()

    def action_nav_up(self) -> None:
        """Navigate up in the option list."""
        try:
            options_list = self.query_one("#options-list", OptionList)
            if options_list.option_count > 0:
                new_idx = (options_list.highlighted - 1) % options_list.option_count
                options_list.highlighted = new_idx
        except NoMatches:
            pass

    def action_nav_down(self) -> None:
        """Navigate down in the option list."""
        try:
            options_list = self.query_one("#options-list", OptionList)
            if options_list.option_count > 0:
                new_idx = (options_list.highlighted + 1) % options_list.option_count
                options_list.highlighted = new_idx
        except NoMatches:
            pass

    def action_select(self) -> None:
        """Select the current option (edit field or navigate)."""
        step_name = self.steps[self.step] if self.step < len(self.steps) else ""

        if step_name in ("identity", "abilities"):
            # Open editor for the field
            self._edit_current_field()
        elif step_name == "confirm":
            if self.selected_option == 1:
                # Save character
                self._save_character()
        else:
            # Show detail or navigate
            pass

    def _edit_current_field(self) -> None:
        """Open editor for current field."""
        step_name = self.steps[self.step]
        selected = self.current_options[self.selected_option]

        # Extract field name
        field_name = selected.split(":")[0].lower().replace(" ", "_")
        current_value = self.session.get_field(field_name)

        # Determine field type
        field_type = "text"
        if field_name in ("level", "strength", "dexterity", "constitution",
                          "intelligence", "wisdom", "charisma"):
            field_type = "int"

        def handle_result(result: Any) -> None:
            if result is not None:
                self.session.set_override(field_name, result)
                self._show_step()
                self.notify(f"Updated {field_name.replace('_', ' ')}")

        self.app.push_screen(
            FieldEditorModal(field_name, current_value, field_type),
            handle_result
        )

    def _save_character(self) -> None:
        """Save the imported character."""
        is_complete, missing = self.session.is_complete()
        if not is_complete:
            self.notify(f"Missing required fields: {', '.join(missing)}", severity="error")
            return

        try:
            character = self.session.to_character()

            # Save using the store
            from dnd_manager.storage import CharacterStore
            from dnd_manager.config import Config

            config = Config.load()
            store = CharacterStore(config.get_character_directory())
            store.save(character)

            self.notify(f"Character '{character.name}' saved!", severity="information")

            # Return to welcome screen
            self.app.pop_screen()

            # Load the new character
            self.app.load_character(store.get_character_path(character.name))

        except Exception as e:
            self.notify(f"Failed to save: {e}", severity="error")

    def action_prev_step(self) -> None:
        """Go to previous step."""
        if self.step > 0:
            self.step -= 1
            self.selected_option = 0
            self._show_step()

    def action_next_step(self) -> None:
        """Go to next step."""
        if self.step < len(self.steps) - 1:
            self.step += 1
            self.selected_option = 0
            self._show_step()

    def action_back_or_cancel(self) -> None:
        """Go back or cancel import."""
        if self.step > 0:
            self.action_prev_step()
        else:
            # Confirm cancel
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-back":
            self.action_prev_step()
        elif event.button.id == "btn-next":
            if self.steps[self.step] == "confirm":
                self._save_character()
            else:
                self.action_next_step()
