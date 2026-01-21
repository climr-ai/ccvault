"""Main Textual application for D&D Character Manager."""

import asyncio
from datetime import date
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Button, Label, Input, RichLog
from textual.screen import Screen
from textual.message import Message

from dnd_manager.config import Config, get_config_manager
from dnd_manager.models.character import Character, RulesetId, Feature
from dnd_manager.storage import CharacterStore
from dnd_manager.data import (
    get_all_species_names,
    get_species,
    get_subraces,
    get_origin_feats,
    get_all_background_names,
    get_background,
    get_class_info,
    get_feat,
)


class ClickableListItem(Static):
    """A clickable list item that emits a message when clicked."""

    class Selected(Message):
        """Message sent when this item is clicked."""
        def __init__(self, index: int) -> None:
            self.index = index
            super().__init__()

    def __init__(self, content: str, index: int, **kwargs) -> None:
        super().__init__(content, **kwargs)
        self.item_index = index

    def on_click(self) -> None:
        """Handle click by posting a Selected message."""
        self.post_message(self.Selected(self.item_index))


class ListNavigationMixin:
    """Mixin providing standard list navigation: letter jump and scroll-into-view.

    Subclasses must implement:
    - _get_list_items() -> list: Return the list of items
    - _get_item_name(item) -> str: Return the display name for an item
    - _get_scroll_container() -> VerticalScroll: Return the scrollable container
    - _update_selection(): Update the visual selection state
    - _get_item_widget_class() -> str: CSS class for list item widgets (e.g., "spell-browser-item")

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

    def _get_scroll_container(self):
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
        except Exception:
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


class CharacterCreationScreen(ListNavigationMixin, Screen):
    """Wizard for creating a new character."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "next", "Next/Confirm"),
        Binding("left", "prev_option", "Previous"),
        Binding("right", "next_option", "Next"),
    ]

    def __init__(self, draft_data: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        # Letter jump tracking
        self._last_letter: str = ""
        self._last_letter_index: int = -1
        # Dynamic steps - subspecies and origin_feat may be skipped
        self.all_steps = ["ruleset", "name", "class", "species", "subspecies", "background", "origin_feat", "abilities", "confirm"]

        # Get defaults from config
        config = get_config_manager().config
        defaults = config.character_defaults

        # Load from draft or use config defaults
        if draft_data:
            self.step = draft_data.get("_step", 0)
            self.char_data = {
                "name": draft_data.get("name", defaults.name),
                "class": draft_data.get("class", defaults.class_name),
                "species": draft_data.get("species", defaults.species),
                "subspecies": draft_data.get("subspecies"),
                "background": draft_data.get("background", defaults.background),
                "origin_feat": draft_data.get("origin_feat"),
                "ruleset": draft_data.get("ruleset", defaults.ruleset),
            }
        else:
            self.step = 0
            self.char_data = {
                "name": defaults.name,
                "class": defaults.class_name,
                "species": defaults.species,
                "subspecies": None,
                "background": defaults.background,
                "origin_feat": None,
                "ruleset": defaults.ruleset,
            }

        self.current_options: list[str] = []
        self.selected_option = 0
        self._draft_store = None

    @property
    def draft_store(self):
        """Lazy-load draft store."""
        if self._draft_store is None:
            from dnd_manager.storage.yaml_store import get_default_draft_store
            self._draft_store = get_default_draft_store()
        return self._draft_store

    def _save_draft(self) -> None:
        """Auto-save current progress as draft."""
        draft_data = {**self.char_data, "_step": self.step}
        self.draft_store.save_draft(draft_data)

    @property
    def steps(self) -> list[str]:
        """Return active steps, skipping inapplicable ones."""
        active = []
        for step in self.all_steps:
            if step == "subspecies":
                # Skip if selected species has no subraces
                subraces = get_subraces(self.char_data.get("species", ""))
                if not subraces:
                    continue
            elif step == "origin_feat":
                # Skip for 2014 rules (no origin feats)
                if self.char_data.get("ruleset") == "dnd2014":
                    continue
            active.append(step)
        return active

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create New Character", classes="title"),
            Static(id="step-indicator", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static(id="step-title", classes="panel-title"),
                    Input(placeholder="Enter name...", id="name-input"),
                    VerticalScroll(id="options-list", classes="options-list"),
                    Static(id="step-description"),
                    classes="panel creation-panel creation-left",
                ),
                VerticalScroll(
                    Static(id="detail-title", classes="panel-title"),
                    Static(id="detail-content"),
                    id="detail-panel",
                    classes="panel creation-panel creation-right",
                ),
                classes="creation-row",
            ),
            Horizontal(
                Button("Cancel", id="btn-cancel", variant="error"),
                Button("← Back", id="btn-back", variant="default"),
                Button("Next →", id="btn-next", variant="primary"),
                classes="button-row",
            ),
            id="creation-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the first step."""
        self._show_step()

    def _show_step(self) -> None:
        """Display the current step."""
        step_name = self.steps[self.step]

        # Update step indicator with visual progress
        indicator = self.query_one("#step-indicator", Static)
        total_steps = len(self.steps)
        current = self.step + 1

        # Build visual progress bar
        step_icons = []
        step_labels = {
            "ruleset": "Rules",
            "name": "Name",
            "class": "Class",
            "species": "Species",
            "subspecies": "Subrace",
            "background": "Background",
            "origin_feat": "Feat",
            "abilities": "Abilities",
            "confirm": "Confirm",
        }
        for i, step in enumerate(self.steps):
            if i < self.step:
                step_icons.append("●")  # Completed
            elif i == self.step:
                step_icons.append("◉")  # Current
            else:
                step_icons.append("○")  # Future

        progress_bar = " ".join(step_icons)
        current_label = step_labels.get(step_name, step_name.title())
        indicator.update(f"{progress_bar}\nStep {current}/{total_steps}: {current_label}")

        title = self.query_one("#step-title", Static)
        name_input = self.query_one("#name-input", Input)
        options_list = self.query_one("#options-list", VerticalScroll)
        description = self.query_one("#step-description", Static)

        # Hide/show elements based on step
        name_input.display = step_name == "name"
        options_list.display = step_name not in ("name", "confirm")

        # Update buttons
        back_btn = self.query_one("#btn-back", Button)
        next_btn = self.query_one("#btn-next", Button)
        back_btn.disabled = self.step == 0
        next_btn.label = "Create Character" if step_name == "confirm" else "Next →"

        if step_name == "ruleset":
            title.update("CHOOSE RULESET")
            description.update("Select which D&D rules system to use")
            self.current_options = ["D&D 2024 (5.5e)", "D&D 2014 (5e)", "Tales of the Valiant"]
            self._refresh_options()

        elif step_name == "name":
            title.update("CHARACTER NAME")
            description.update("Enter your character's name")
            name_input.value = self.char_data["name"]
            name_input.focus()

        elif step_name == "class":
            title.update("CHOOSE CLASS")
            description.update("Select your character's class - this determines your abilities and playstyle")
            self.current_options = [
                "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
                "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
            ]
            self._refresh_options()

        elif step_name == "species":
            title.update("CHOOSE SPECIES")
            description.update("Select your character's species")
            # Use dynamic species list from data module
            self.current_options = get_all_species_names()
            self._refresh_options()

        elif step_name == "subspecies":
            title.update("CHOOSE SUBSPECIES")
            species_name = self.char_data.get("species", "")
            species = get_species(species_name)
            if species:
                description.update(f"Select your {species_name}'s subspecies or heritage")
                self.current_options = [sr.name for sr in species.subraces]
            else:
                self.current_options = []
            self._refresh_options()

        elif step_name == "background":
            title.update("CHOOSE BACKGROUND")
            description.update("Select your character's background - this shapes their history and skills")
            # Use dynamic background list from data module
            self.current_options = get_all_background_names()
            self._refresh_options()

        elif step_name == "origin_feat":
            title.update("CHOOSE ORIGIN FEAT")
            description.update("Select a feat granted by your background (2024 rules)")
            # Get origin feats from data module
            origin_feats = get_origin_feats()
            self.current_options = [f.name for f in origin_feats]
            self._refresh_options()

        elif step_name == "abilities":
            title.update("ABILITY SCORES")
            description.update("Using Standard Array: 15, 14, 13, 12, 10, 8 (assigned automatically)")
            options_list.remove_children()
            options_list.mount(Static("  STR: 15  DEX: 14  CON: 13"))
            options_list.mount(Static("  INT: 12  WIS: 10  CHA: 8"))
            options_list.mount(Static(""))
            options_list.mount(Static("  (You can adjust these after creation)"))
            options_list.display = True

        elif step_name == "confirm":
            title.update("CONFIRM CHARACTER")
            options_list.remove_children()
            options_list.mount(Static(f"  Name: {self.char_data['name']}"))
            options_list.mount(Static(f"  Class: {self.char_data['class']}"))
            species_display = self.char_data['species']
            if self.char_data.get('subspecies'):
                species_display += f" ({self.char_data['subspecies']})"
            options_list.mount(Static(f"  Species: {species_display}"))
            options_list.mount(Static(f"  Background: {self.char_data['background']}"))
            if self.char_data.get('origin_feat'):
                options_list.mount(Static(f"  Origin Feat: {self.char_data['origin_feat']}"))
            options_list.mount(Static(""))
            options_list.mount(Static("  Press 'Create Character' to finish"))
            options_list.display = True
            description.update("")

    def _refresh_options(self) -> None:
        """Rebuild the options list. Only call on step transitions, not navigation."""
        try:
            options_list = self.query_one("#options-list", VerticalScroll)
        except Exception:
            # Screen not mounted yet
            return

        # Rebuild all widgets for the new step
        options_list.remove_children()
        for i, option in enumerate(self.current_options):
            selected = "▶ " if i == self.selected_option else "  "
            options_list.mount(ClickableListItem(
                f"{selected}{option}",
                index=i,
                classes=f"option-item {'selected' if i == self.selected_option else ''}",
            ))

        self._refresh_details()

    def _refresh_details(self) -> None:
        """Update the detail panel with information about the selected option."""
        try:
            detail_title = self.query_one("#detail-title", Static)
            detail_content = self.query_one("#detail-content", Static)
            detail_panel = self.query_one("#detail-panel", VerticalScroll)
        except Exception:
            return

        step_name = self.steps[self.step] if self.step < len(self.steps) else ""

        # Hide detail panel on steps without options
        if step_name in ("name", "abilities", "confirm"):
            detail_panel.display = False
            return

        detail_panel.display = True

        if not self.current_options or self.selected_option >= len(self.current_options):
            detail_title.update("")
            detail_content.update("Select an option to see details")
            return

        selected_name = self.current_options[self.selected_option]

        if step_name == "ruleset":
            self._show_ruleset_details(selected_name, detail_title, detail_content)
        elif step_name == "class":
            self._show_class_details(selected_name, detail_title, detail_content)
        elif step_name == "species":
            self._show_species_details(selected_name, detail_title, detail_content)
        elif step_name == "subspecies":
            self._show_subspecies_details(selected_name, detail_title, detail_content)
        elif step_name == "background":
            self._show_background_details(selected_name, detail_title, detail_content)
        elif step_name == "origin_feat":
            self._show_feat_details(selected_name, detail_title, detail_content)
        else:
            detail_title.update(selected_name)
            detail_content.update("")

    def _show_ruleset_details(self, ruleset_name: str, title: Static, content: Static) -> None:
        """Show details for a ruleset."""
        ruleset_info = {
            "D&D 2024 (5.5e)": {
                "title": "📖 D&D 2024 (5.5e)",
                "description": "The latest edition of Dungeons & Dragons, released in 2024.",
                "features": [
                    "Origin feats from backgrounds",
                    "Weapon mastery system",
                    "Updated class features",
                    "Flexible ability score increases",
                    "Revised spellcasting rules",
                ],
                "best_for": "Players who want the newest rules and features.",
            },
            "D&D 2014 (5e)": {
                "title": "📖 D&D 2014 (5e)",
                "description": "The classic 5th Edition rules that have been the standard for a decade.",
                "features": [
                    "Background features (not feats)",
                    "Fixed racial ability bonuses",
                    "Original class progression",
                    "Tried and tested balance",
                ],
                "best_for": "Players familiar with classic 5e or using older sourcebooks.",
            },
            "Tales of the Valiant": {
                "title": "📖 Tales of the Valiant",
                "description": "A 5e-compatible ruleset from Kobold Press with unique innovations.",
                "features": [
                    "Lineage + Heritage system",
                    "Luck mechanic",
                    "Talent trees",
                    "Compatible with 5e content",
                ],
                "best_for": "Players wanting fresh mechanics while staying 5e-compatible.",
            },
        }

        info = ruleset_info.get(ruleset_name, {})
        if not info:
            title.update(ruleset_name)
            content.update("No details available")
            return

        title.update(info["title"])

        lines = []
        lines.append(info["description"])
        lines.append("")
        lines.append("KEY FEATURES")
        for feature in info["features"]:
            lines.append(f"  • {feature}")
        lines.append("")
        lines.append(f"Best for: {info['best_for']}")

        content.update("\n".join(lines))

    def _show_class_details(self, class_name: str, title: Static, content: Static) -> None:
        """Show details for a class."""
        class_info = get_class_info(class_name)
        if not class_info:
            title.update(class_name)
            content.update("No details available")
            return

        title.update(f"⚔️ {class_name}")

        lines = []
        lines.append(f"Hit Die: {class_info.hit_die}")
        lines.append(f"Primary Ability: {class_info.primary_ability}")
        lines.append(f"Saves: {', '.join(class_info.saving_throws)}")
        lines.append("")
        lines.append("PROFICIENCIES")
        lines.append(f"  Armor: {', '.join(class_info.armor_proficiencies) or 'None'}")
        lines.append(f"  Weapons: {', '.join(class_info.weapon_proficiencies)}")
        lines.append(f"  Skills: Choose {class_info.skill_choices} from:")
        lines.append(f"    {', '.join(class_info.skill_options)}")

        if class_info.spellcasting_ability:
            lines.append("")
            lines.append(f"Spellcasting: {class_info.spellcasting_ability}")

        # Show level 1 features
        level_1_features = [f for f in class_info.features if f.level == 1]
        if level_1_features:
            lines.append("")
            lines.append("LEVEL 1 FEATURES")
            for feat in level_1_features:
                lines.append(f"  • {feat.name}")

        content.update("\n".join(lines))

    def _show_species_details(self, species_name: str, title: Static, content: Static) -> None:
        """Show details for a species."""
        species = get_species(species_name)
        if not species:
            title.update(species_name)
            content.update("No details available")
            return

        title.update(f"🧬 {species_name}")

        lines = []
        lines.append(species.description)
        lines.append("")
        lines.append(f"Size: {species.size}")
        lines.append(f"Speed: {species.speed} ft.")
        if species.darkvision:
            lines.append(f"Darkvision: {species.darkvision} ft.")
        lines.append(f"Languages: {', '.join(species.languages)}")

        if species.traits:
            lines.append("")
            lines.append("RACIAL TRAITS")
            for trait in species.traits:
                lines.append(f"  • {trait.name}")
                # Wrap long descriptions
                if len(trait.description) > 60:
                    lines.append(f"    {trait.description[:60]}...")
                else:
                    lines.append(f"    {trait.description}")

        if species.subraces:
            lines.append("")
            lines.append(f"Subraces: {', '.join(sr.name for sr in species.subraces)}")

        content.update("\n".join(lines))

    def _show_subspecies_details(self, subrace_name: str, title: Static, content: Static) -> None:
        """Show details for a subspecies."""
        species_name = self.char_data.get("species", "")
        species = get_species(species_name)
        if not species:
            title.update(subrace_name)
            content.update("No details available")
            return

        subrace = next((sr for sr in species.subraces if sr.name == subrace_name), None)
        if not subrace:
            title.update(subrace_name)
            content.update("No details available")
            return

        title.update(f"🧬 {subrace_name}")

        lines = []
        lines.append(subrace.description)

        if subrace.ability_bonuses:
            lines.append("")
            bonuses = [f"+{v} {k}" for k, v in subrace.ability_bonuses.items()]
            lines.append(f"Ability Bonuses: {', '.join(bonuses)}")

        if subrace.traits:
            lines.append("")
            lines.append("SUBRACE TRAITS")
            for trait in subrace.traits:
                lines.append(f"  • {trait.name}")
                lines.append(f"    {trait.description}")

        content.update("\n".join(lines))

    def _show_background_details(self, bg_name: str, title: Static, content: Static) -> None:
        """Show details for a background."""
        background = get_background(bg_name)
        if not background:
            title.update(bg_name)
            content.update("No details available")
            return

        title.update(f"📜 {bg_name}")

        lines = []
        lines.append(background.description)
        lines.append("")
        lines.append("PROFICIENCIES")
        lines.append(f"  Skills: {', '.join(background.skill_proficiencies)}")
        if background.tool_proficiencies:
            lines.append(f"  Tools: {', '.join(background.tool_proficiencies)}")
        if background.languages:
            lines.append(f"  Languages: {background.languages} of your choice")

        if background.equipment:
            lines.append("")
            lines.append("EQUIPMENT")
            for item in background.equipment:
                lines.append(f"  • {item}")

        if background.feature:
            lines.append("")
            lines.append(f"FEATURE: {background.feature.name}")
            lines.append(f"  {background.feature.description}")

        if background.origin_feat:
            lines.append("")
            lines.append(f"ORIGIN FEAT: {background.origin_feat}")

        if background.ability_score_options:
            lines.append("")
            lines.append(f"Ability Options: {', '.join(background.ability_score_options)}")

        content.update("\n".join(lines))

    def _show_feat_details(self, feat_name: str, title: Static, content: Static) -> None:
        """Show details for a feat."""
        feat = get_feat(feat_name)
        if not feat:
            title.update(feat_name)
            content.update("No details available")
            return

        title.update(f"✨ {feat_name}")

        lines = []
        lines.append(feat.description)

        if feat.prerequisites:
            lines.append("")
            lines.append(f"Prerequisites: {', '.join(feat.prerequisites)}")

        if feat.benefits:
            lines.append("")
            lines.append("BENEFITS")
            for benefit in feat.benefits:
                lines.append(f"  • {benefit}")

        content.update("\n".join(lines))

    # ListNavigationMixin implementation
    @property
    def selected_index(self) -> int:
        return self.selected_option

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        self.selected_option = value

    def _get_list_items(self) -> list:
        return self.current_options

    def _get_item_name(self, item) -> str:
        return str(item)

    def _get_scroll_container(self):
        try:
            return self.query_one("#options-list", VerticalScroll)
        except Exception:
            return None

    def _get_item_widget_class(self) -> str:
        return "option-item"

    def _update_selection_visual(self, old_index: int, new_index: int) -> None:
        """Update just the two widgets that changed during navigation."""
        try:
            options_list = self.query_one("#options-list", VerticalScroll)
            widgets = list(options_list.query(".option-item"))

            # Update old widget (remove selection)
            if 0 <= old_index < len(widgets):
                old_widget = widgets[old_index]
                old_widget.update(f"  {self.current_options[old_index]}")
                old_widget.remove_class("selected")

            # Update new widget (add selection)
            if 0 <= new_index < len(widgets):
                new_widget = widgets[new_index]
                new_widget.update(f"▶ {self.current_options[new_index]}")
                new_widget.add_class("selected")
                # Don't call scroll_visible - Textual auto-scrolls on widget update

            self._refresh_details()
        except Exception:
            pass

    def _update_selection(self) -> None:
        self._refresh_options()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-back":
            self._go_back()
        elif event.button.id == "btn-next":
            self.action_next()

    def _go_back(self) -> None:
        """Go to previous step."""
        if self.step > 0:
            self.step -= 1
            self.selected_option = 0
            self._show_step()
            self._save_draft()

    def action_next(self) -> None:
        """Go to next step or create character."""
        step_name = self.steps[self.step]

        # Save current step data
        if step_name == "ruleset":
            # Map display name to ruleset ID
            ruleset_map = {
                "D&D 2024 (5.5e)": "dnd2024",
                "D&D 2014 (5e)": "dnd2014",
                "Tales of the Valiant": "tov",
            }
            selected = self.current_options[self.selected_option]
            self.char_data["ruleset"] = ruleset_map.get(selected, "dnd2024")
        elif step_name == "name":
            name = self.query_one("#name-input", Input).value.strip()
            if not name:
                self.notify("Please enter a name", severity="warning")
                return
            self.char_data["name"] = name
        elif step_name == "class":
            self.char_data["class"] = self.current_options[self.selected_option]
        elif step_name == "species":
            self.char_data["species"] = self.current_options[self.selected_option]
            # Reset subspecies when species changes
            self.char_data["subspecies"] = None
        elif step_name == "subspecies":
            if self.current_options:
                self.char_data["subspecies"] = self.current_options[self.selected_option]
        elif step_name == "background":
            self.char_data["background"] = self.current_options[self.selected_option]
        elif step_name == "origin_feat":
            if self.current_options:
                self.char_data["origin_feat"] = self.current_options[self.selected_option]
        elif step_name == "confirm":
            self._create_character()
            return

        # Move to next step
        if self.step < len(self.steps) - 1:
            self.step += 1
            self.selected_option = 0
            self._show_step()
            self._save_draft()

    def _create_character(self) -> None:
        """Create the character and go to dashboard."""
        from dnd_manager.data import get_feat

        # Create character
        char = Character.create_new(
            name=self.char_data["name"],
            class_name=self.char_data["class"],
        )
        char.species = self.char_data["species"]
        char.subspecies = self.char_data.get("subspecies")
        char.background = self.char_data["background"]

        # Add origin feat if selected
        if self.char_data.get("origin_feat"):
            feat_name = self.char_data["origin_feat"]
            feat_data = get_feat(feat_name)
            if feat_data:
                char.features.append(Feature(
                    name=feat_name,
                    source="feat",
                    description=feat_data.description,
                ))

        # Add racial traits from species data
        species = get_species(self.char_data["species"])
        if species:
            for trait in species.traits:
                char.features.append(Feature(
                    name=trait.name,
                    source="racial",
                    description=trait.description,
                ))
            # Add subrace traits if applicable
            if self.char_data.get("subspecies"):
                for subrace in species.subraces:
                    if subrace.name == self.char_data["subspecies"]:
                        for trait in subrace.traits:
                            char.features.append(Feature(
                                name=trait.name,
                                source="racial",
                                description=trait.description,
                            ))
                        break

        # Save character and clear draft
        self.app.store.save(char)
        self.app.current_character = char
        self.draft_store.clear_draft()

        self.notify(f"Created {char.name}!")

        # Go to dashboard
        self.app.pop_screen()
        self.app.push_screen(MainDashboard(char))

    def action_prev_option(self) -> None:
        """Select previous option."""
        if self.current_options and self.selected_option > 0:
            old_index = self.selected_option
            self.selected_option -= 1
            self._update_selection_visual(old_index, self.selected_option)

    def action_next_option(self) -> None:
        """Select next option."""
        if self.current_options and self.selected_option < len(self.current_options) - 1:
            old_index = self.selected_option
            self.selected_option += 1
            self._update_selection_visual(old_index, self.selected_option)

    def key_up(self) -> None:
        """Move selection up."""
        self.action_prev_option()

    def key_down(self) -> None:
        """Move selection down."""
        self.action_next_option()

    def on_key(self, event) -> None:
        """Handle key presses for letter navigation."""
        step_name = self.steps[self.step] if self.step < len(self.steps) else ""
        # Only do letter jump on steps that show options list
        if step_name in ("class", "species", "subspecies", "background", "origin_feat"):
            if self._handle_key_for_letter_jump(event.key):
                event.prevent_default()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        """Handle mouse click on a list item."""
        if 0 <= event.index < len(self.current_options):
            old_index = self.selected_option
            self.selected_option = event.index
            self._update_selection_visual(old_index, self.selected_option)

    def action_cancel(self) -> None:
        """Cancel character creation - draft is auto-saved for resume."""
        self._save_draft()  # Ensure latest state is saved
        self.notify("Progress saved - you can resume anytime")
        self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input fields - proceed to next step."""
        if event.input.id == "name-input":
            self.action_next()


class WelcomeScreen(Screen):
    """Welcome screen shown when no character is loaded."""

    BINDINGS = [
        Binding("n", "new_character", "New Character"),
        Binding("o", "open_character", "Open Character"),
        Binding("r", "resume_draft", "Resume Draft", show=False),
        Binding("q", "quit", "Quit"),
        Binding("left", "prev_button", "Previous", show=False),
        Binding("right", "next_button", "Next", show=False),
        Binding("enter", "select_button", "Select", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selected_index = 0
        self.button_ids = ["btn-new", "btn-open", "btn-quit"]
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
        """Get the application version from package metadata or config."""
        try:
            from importlib.metadata import version
            return version("dnd-manager")
        except Exception:
            return get_config_manager().config.versions.app_version

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
            self.button_ids = ["btn-new", "btn-resume", "btn-open", "btn-quit"]
            resume_btn.display = True
            # Show draft info
            notice.update(f"Draft: {draft_info['name']} ({draft_info['class']} {draft_info['species']}) - Press [R] to resume")
            notice.display = True
        else:
            self._has_draft = False
            self.button_ids = ["btn-new", "btn-open", "btn-quit"]
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
            except Exception:
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
        elif btn_id == "btn-quit":
            self.action_quit()

    def action_new_character(self) -> None:
        """Create a new character (clears any existing draft)."""
        if self._has_draft:
            self.draft_store.clear_draft()
        self.app.action_new_character()

    def action_resume_draft(self) -> None:
        """Resume character creation from draft."""
        draft_data = self.draft_store.load_draft()
        if draft_data:
            self.app.push_screen(CharacterCreationScreen(draft_data=draft_data))
            self.notify(f"Resuming: {draft_data.get('name', 'Unknown')}")
        else:
            self.notify("No draft found", severity="warning")
            self._check_for_draft()

    def action_open_character(self) -> None:
        """Open an existing character."""
        self.app.action_open_character()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-new":
            self.action_new_character()
        elif event.button.id == "btn-resume":
            self.action_resume_draft()
        elif event.button.id == "btn-open":
            self.action_open_character()
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


class CharacterSelectScreen(ListNavigationMixin, Screen):
    """Screen for selecting a character to load."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("q", "cancel", "Cancel"),
        Binding("n", "new_character", "New Character"),
    ]

    def __init__(self, characters: list[dict], **kwargs) -> None:
        super().__init__(**kwargs)
        self.characters = characters
        self.selected_index = 0
        self._last_letter = ""
        self._last_letter_index = -1

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Select a Character", classes="title"),
            Static("↑/↓ Navigate  Type to jump  Enter Select  Esc Cancel", classes="subtitle"),
            VerticalScroll(id="character-list"),
            id="select-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Populate the character list."""
        list_container = self.query_one("#character-list", VerticalScroll)
        for i, char_info in enumerate(self.characters):
            item = CharacterListItem(char_info, index=i, id=f"char-{i}", classes="char-item")
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
        except Exception:
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
        self.app.pop_screen()

    def action_new_character(self) -> None:
        """Create new character instead."""
        self.app.pop_screen()
        self.app.action_new_character()

    def key_up(self) -> None:
        """Move selection up."""
        self._navigate_up()

    def key_down(self) -> None:
        """Move selection down."""
        self._navigate_down()

    def key_enter(self) -> None:
        """Select the current character."""
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


class AbilityBlock(Static):
    """Widget displaying ability scores with color-coded modifiers."""

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def _get_modifier_class(self, modifier: int) -> str:
        """Get CSS class based on modifier value."""
        if modifier >= 3:
            return "ability-high"
        elif modifier >= 1:
            return "ability-positive"
        elif modifier == 0:
            return "ability-neutral"
        elif modifier >= -2:
            return "ability-negative"
        else:
            return "ability-low"

    def compose(self) -> ComposeResult:
        yield Static("ABILITIES", classes="panel-title")
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = getattr(self.character.abilities, ability)
            abbr = ability[:3].upper()
            modifier_class = self._get_modifier_class(score.modifier)
            yield Static(
                f"{abbr} {score.total:2d} ({score.modifier_str})",
                classes=f"ability-row {modifier_class}",
            )


class CharacterInfo(Static):
    """Widget displaying character identity info."""

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        c = self.character
        ruleset = c.get_ruleset()

        yield Static("CHARACTER", classes="panel-title")

        # Class info
        class_info = f"{c.primary_class.name} {c.primary_class.level}"
        if c.primary_class.subclass:
            class_info += f" ({c.primary_class.subclass})"
        yield Static(class_info)

        # Species/Race (use ruleset terminology)
        species_term = c.get_species_term()
        if c.species:
            species_info = c.species
            if c.subspecies:
                species_info += f" ({c.subspecies})"
            yield Static(f"{species_term}: {species_info}")
        else:
            yield Static(f"{species_term}: Not selected")

        # Background
        if c.background:
            yield Static(f"Background: {c.background}")

        # Alignment
        yield Static(f"Alignment: {c.alignment.display_name}")

        # Ruleset indicator
        if ruleset:
            yield Static(f"Ruleset: {ruleset.name}", classes="ruleset-info")


class CombatStats(Static):
    """Widget displaying combat statistics."""

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        c = self.character
        hp = c.combat.hit_points

        yield Static("COMBAT", classes="panel-title")
        yield Static(f"AC: {c.combat.total_ac}    Init: {c.get_initiative():+d}")
        yield Static(f"Speed: {c.combat.total_speed}ft")

        # HP bar
        hp_pct = hp.current / hp.maximum if hp.maximum > 0 else 0
        bar_width = 16
        filled = int(hp_pct * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        yield Static(f"HP: {bar} {hp.current}/{hp.maximum}")

        yield Static(f"Hit Dice: {c.combat.get_hit_dice_display()}")
        yield Static(f"Prof Bonus: +{c.proficiency_bonus}")

        # Spellcasting info if applicable
        if c.spellcasting.ability:
            dc = c.get_spell_save_dc()
            atk = c.get_spell_attack_bonus()
            yield Static(f"Spell DC: {dc}  Atk: +{atk}")


class QuickActions(Static):
    """Widget with quick action buttons."""

    def compose(self) -> ComposeResult:
        yield Static("QUICK ACTIONS", classes="panel-title")
        yield Static("[S]pells  [I]nventory")
        yield Static("[F]eats   [N]otes")
        yield Static("[A]I Chat [R]oll")
        yield Static("[H]omebrew Guidelines")
        yield Static("")
        yield Static("[E]dit Character")
        yield Static("[L]evel Up")


class SkillList(Static):
    """Widget displaying skills."""

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        from dnd_manager.models.abilities import Skill, SkillProficiency, SKILL_ABILITY_MAP

        yield Static("SKILLS", classes="panel-title")

        for skill in Skill:
            ability = SKILL_ABILITY_MAP[skill]
            prof = self.character.proficiencies.get_skill_proficiency(skill)
            mod = self.character.get_skill_modifier(skill)

            # Proficiency indicator
            if prof == SkillProficiency.EXPERTISE:
                indicator = "◆"
            elif prof == SkillProficiency.PROFICIENT:
                indicator = "●"
            else:
                indicator = "○"

            yield Static(
                f"{indicator} {skill.display_name} ({ability.abbreviation}) {mod:+d}",
                classes="skill-row",
            )


class SpellSlots(Static):
    """Widget displaying spell slots."""

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        yield Static("SPELL SLOTS", classes="panel-title")

        slots = self.character.spellcasting.slots
        if not slots:
            yield Static("No spellcasting", classes="no-spells")
            return

        for level in sorted(slots.keys()):
            slot = slots[level]
            if slot.total > 0:
                filled = "●" * slot.remaining + "○" * slot.used
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(level, "th")
                yield Static(f"{level}{suffix}: {filled} ({slot.remaining}/{slot.total})")


class PreparedSpells(Static):
    """Widget displaying prepared spells."""

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        yield Static("PREPARED SPELLS", classes="panel-title")

        prepared = self.character.spellcasting.prepared
        if not prepared:
            yield Static("No spells prepared", classes="empty-state")
            yield Static("Press [S] to browse spells", classes="empty-state-hint")
            return

        # Show up to 10 prepared spells
        for spell in prepared[:10]:
            yield Static(f"• {spell}")

        if len(prepared) > 10:
            yield Static(f"  ... +{len(prepared) - 10} more")


class DiceRollerScreen(Screen):
    """Screen for rolling dice."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("c", "clear", "Clear History"),
    ]

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self._roller = None

    @property
    def roller(self):
        if self._roller is None:
            from dnd_manager.dice import DiceRoller
            self._roller = DiceRoller()
        return self._roller

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Dice Roller", classes="title"),
            Static("Enter dice notation: 1d20, 2d6+5, 4d6kh3, adv, dis", classes="subtitle"),
            Horizontal(
                Input(placeholder="e.g., 1d20+5", id="dice-input"),
                Button("Roll", id="btn-roll", variant="primary"),
                classes="dice-input-row",
            ),
            Horizontal(
                Button("d4", id="btn-d4", classes="quick-die"),
                Button("d6", id="btn-d6", classes="quick-die"),
                Button("d8", id="btn-d8", classes="quick-die"),
                Button("d10", id="btn-d10", classes="quick-die"),
                Button("d12", id="btn-d12", classes="quick-die"),
                Button("d20", id="btn-d20", classes="quick-die"),
                Button("d100", id="btn-d100", classes="quick-die"),
                classes="quick-dice-row",
            ),
            Horizontal(
                Button("Adv", id="btn-adv", classes="quick-roll"),
                Button("Dis", id="btn-dis", classes="quick-roll"),
                Button("Stats", id="btn-stats", classes="quick-roll"),
                classes="quick-roll-row",
            ),
            Static("Roll History", classes="panel-title"),
            VerticalScroll(id="roll-history"),
            id="dice-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#dice-input", Input).focus()

    def _do_roll(self, notation: str) -> None:
        """Perform a dice roll and display result."""
        from dnd_manager.dice.parser import is_valid_dice_notation

        if not is_valid_dice_notation(notation):
            self.notify(f"Invalid dice notation: {notation}", severity="error")
            return

        result = self.roller.roll(notation)
        history = self.query_one("#roll-history", VerticalScroll)

        # Format result
        if result.is_natural_20:
            result_class = "crit-success"
            prefix = "🎯 "
        elif result.is_natural_1:
            result_class = "crit-fail"
            prefix = "💀 "
        else:
            result_class = "normal-roll"
            prefix = ""

        result_widget = Static(
            f"{prefix}{notation}: {result}",
            classes=f"roll-result {result_class}",
        )
        history.mount(result_widget)
        history.scroll_end()

        # Clear input
        self.query_one("#dice-input", Input).value = ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id
        if btn_id == "btn-roll":
            notation = self.query_one("#dice-input", Input).value.strip()
            if notation:
                self._do_roll(notation)
        elif btn_id and btn_id.startswith("btn-d"):
            die = btn_id.replace("btn-", "1")
            self._do_roll(die)
        elif btn_id == "btn-adv":
            self._do_roll("adv")
        elif btn_id == "btn-dis":
            self._do_roll("dis")
        elif btn_id == "btn-stats":
            # Roll 4d6kh3 six times for stats
            for i in range(6):
                self._do_roll("4d6kh3")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        if event.input.id == "dice-input" and event.value.strip():
            self._do_roll(event.value.strip())

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()

    def action_clear(self) -> None:
        """Clear roll history."""
        history = self.query_one("#roll-history", VerticalScroll)
        history.remove_children()
        self.notify("History cleared")


class AIChatScreen(Screen):
    """Screen for AI chat assistant."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("ctrl+l", "clear", "Clear Chat"),
        Binding("m", "switch_mode", "Switch Mode"),
    ]

    MODES = [
        ("assistant", "General D&D Assistant"),
        ("dm", "Dungeon Master"),
        ("roleplay", "Roleplay Helper"),
        ("rules", "Rules Expert"),
        ("homebrew", "Homebrew Creator"),
    ]

    def __init__(self, character: Optional[Character] = None, mode: str = "assistant", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.current_mode = mode
        self._messages: list = []
        self._provider = None

    def compose(self) -> ComposeResult:
        char_name = self.character.name if self.character else "No character"
        mode_name = dict(self.MODES).get(self.current_mode, "Assistant")
        yield Header()
        yield Container(
            Static(f"AI {mode_name} - {char_name}", id="chat-title", classes="title"),
            Static("[M] Switch Mode  [Ctrl+L] Clear  [Esc] Back", classes="subtitle"),
            Horizontal(
                *[Button(name, id=f"mode-{mode}", variant="primary" if mode == self.current_mode else "default", classes="mode-btn")
                  for mode, name in self.MODES],
                classes="mode-row",
            ),
            RichLog(id="chat-log", wrap=True, markup=True),
            Horizontal(
                Input(placeholder="Ask a question...", id="chat-input"),
                Button("Send", id="btn-send", variant="primary"),
                classes="chat-input-row",
            ),
            id="chat-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize chat on mount."""
        self.query_one("#chat-input", Input).focus()
        self._show_mode_intro()

    def _show_mode_intro(self) -> None:
        """Show introduction for current mode."""
        log = self.query_one("#chat-log", RichLog)
        mode_name = dict(self.MODES).get(self.current_mode, "Assistant")
        log.write(f"[bold cyan]{mode_name} ready![/]")

        if self.current_mode == "assistant":
            log.write("Ask about D&D rules, character builds, or anything else.")
        elif self.current_mode == "dm":
            log.write("Get help with encounters, NPCs, worldbuilding, and more.")
        elif self.current_mode == "roleplay":
            log.write("I'll help you roleplay your character authentically.")
        elif self.current_mode == "rules":
            log.write("Ask me about mechanics, edge cases, and rule clarifications.")
        elif self.current_mode == "homebrew":
            log.write("Describe your homebrew concept and I'll help balance it.")
            log.write("Examples: custom spells, magic items, races, classes, feats...")

        log.write("")

    def _update_mode_buttons(self) -> None:
        """Update mode button styles."""
        for mode, _ in self.MODES:
            btn = self.query_one(f"#mode-{mode}", Button)
            btn.variant = "primary" if mode == self.current_mode else "default"

        # Update title
        char_name = self.character.name if self.character else "No character"
        mode_name = dict(self.MODES).get(self.current_mode, "Assistant")
        self.query_one("#chat-title", Static).update(f"AI {mode_name} - {char_name}")

    async def _get_provider(self):
        """Get the AI provider."""
        if self._provider is None:
            from dnd_manager.ai import get_provider
            manager = get_config_manager()
            provider_name = manager.get("ai.default_provider") or "gemini"
            self._provider = get_provider(provider_name)
        return self._provider

    async def _send_message(self, message: str) -> None:
        """Send a message to the AI."""
        from dnd_manager.ai import build_system_prompt
        from dnd_manager.ai.context import build_homebrew_system_prompt
        from dnd_manager.ai.base import AIMessage, MessageRole

        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold green]You:[/] {message}")

        provider = await self._get_provider()
        if not provider:
            log.write("[bold red]Error:[/] No AI provider configured.")
            log.write("Run: ccvault config set ai.gemini.api_key YOUR_KEY")
            return

        if not provider.is_configured():
            log.write(f"[bold red]Error:[/] {provider.name} not configured.")
            log.write(f"Run: ccvault config set ai.{provider.name}.api_key YOUR_KEY")
            return

        # Build system prompt based on mode
        if self.current_mode == "homebrew":
            system_prompt = build_homebrew_system_prompt(
                content_type="",  # General homebrew mode
                character=self.character,
            )
        else:
            system_prompt = build_system_prompt(self.character, mode=self.current_mode)

        self._messages.append(AIMessage(role=MessageRole.USER, content=message))

        all_messages = [
            AIMessage(role=MessageRole.SYSTEM, content=system_prompt),
            *self._messages,
        ]

        log.write("[bold blue]Assistant:[/] ", end="")

        try:
            response_text = ""
            async for chunk in provider.chat_stream(all_messages):
                log.write(chunk, end="")
                response_text += chunk
            log.write("")  # Newline after response

            # Save assistant response
            self._messages.append(AIMessage(role=MessageRole.ASSISTANT, content=response_text))

        except Exception as e:
            log.write(f"\n[bold red]Error:[/] {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id
        if btn_id == "btn-send":
            self._submit_message()
        elif btn_id and btn_id.startswith("mode-"):
            mode = btn_id.replace("mode-", "")
            self._switch_to_mode(mode)

    def _switch_to_mode(self, mode: str) -> None:
        """Switch to a different chat mode."""
        if mode != self.current_mode:
            self.current_mode = mode
            self._messages.clear()
            self._update_mode_buttons()
            log = self.query_one("#chat-log", RichLog)
            log.clear()
            self._show_mode_intro()
            self.notify(f"Switched to {dict(self.MODES).get(mode, mode)} mode")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key."""
        if event.input.id == "chat-input":
            self._submit_message()

    def _submit_message(self) -> None:
        """Submit the current message."""
        input_widget = self.query_one("#chat-input", Input)
        message = input_widget.value.strip()
        if message:
            input_widget.value = ""
            asyncio.create_task(self._send_message(message))

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()

    def action_switch_mode(self) -> None:
        """Cycle to the next mode."""
        mode_ids = [m[0] for m in self.MODES]
        current_idx = mode_ids.index(self.current_mode)
        next_idx = (current_idx + 1) % len(mode_ids)
        self._switch_to_mode(mode_ids[next_idx])

    def action_clear(self) -> None:
        """Clear chat history."""
        self._messages.clear()
        log = self.query_one("#chat-log", RichLog)
        log.clear()
        self._show_mode_intro()
        self.notify("Chat cleared")


class HelpScreen(Screen):
    """Help screen with keyboard shortcuts and usage info."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("CLIMR Character Vault - Help", classes="title"),
            VerticalScroll(
                Static("""
[bold]DASHBOARD SHORTCUTS[/]
  [cyan]S[/]         Open Spells screen
  [cyan]I[/]         Open Inventory screen
  [cyan]F[/]         Open Features screen
  [cyan]N[/]         Open Notes screen
  [cyan]A[/]         Open AI Chat
  [cyan]R[/]         Open Dice Roller
  [cyan]H[/]         Open Homebrew Guidelines
  [cyan]E[/]         Edit character
  [cyan]?[/]         Show this help

[bold]FILE OPERATIONS[/]
  [cyan]Ctrl+S[/]    Save character
  [cyan]Ctrl+N[/]    New character
  [cyan]Ctrl+O[/]    Open character
  [cyan]Ctrl+Q[/]    Quit

[bold]DICE ROLLER[/]
  Basic:      1d20, 2d6, 1d8+5
  Advantage:  adv, 2d20kh1
  Disadvantage: dis, 2d20kl1
  Keep High:  4d6kh3 (stats)
  Drop Low:   4d6dl1

[bold]AI CHAT[/]
  Ask D&D rules questions
  Get character advice
  Roleplay scenarios
  Uses intelligent routing for free tier

[bold]NOTES[/]
  [cyan]E[/]         Edit notes in $EDITOR
  [cyan]B[/]         Edit backstory in $EDITOR

[bold]SPELLS[/]
  [cyan]C[/]         Cast (use spell slot)
  [cyan]P[/]         Toggle prepared
  [cyan]R[/]         Rest (recover slots)

[bold]CLI COMMANDS[/]
  ccvault                Run TUI
  ccvault list           List characters
  ccvault new <name>     Create character
  ccvault show <name>    Show character
  ccvault roll <dice>    Roll dice
  ccvault ask <question> Ask AI
  ccvault guidelines     View balance guidelines
  ccvault custom         Manage homebrew content
  ccvault export <name>  Export to Markdown

Press [cyan]Esc[/] or [cyan]Q[/] to close this help.
""", markup=True),
                id="help-content",
            ),
            id="help-container",
        )
        yield Footer()

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


class HomebrewScreen(Screen):
    """Screen for viewing balance guidelines and creating homebrew content."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back"),
        Binding("1", "show_spells", "Spells"),
        Binding("2", "show_items", "Magic Items"),
        Binding("3", "show_races", "Races"),
        Binding("4", "show_classes", "Classes"),
        Binding("5", "show_feats", "Feats"),
        Binding("a", "ai_homebrew", "AI Homebrew Chat"),
        Binding("l", "library", "Library"),
    ]

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.current_type = "spell"
        self.content_types = [
            ("spell", "Spells"),
            ("magic_item", "Magic Items"),
            ("race", "Races/Species"),
            ("class", "Classes"),
            ("subclass", "Subclasses"),
            ("feat", "Feats"),
            ("background", "Backgrounds"),
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Homebrew Balance Guidelines", classes="title"),
            Static("[1-5] Switch Type  [A] AI Chat  [L] Library  [Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("CONTENT TYPES", classes="panel-title"),
                    VerticalScroll(id="type-list", classes="type-list"),
                    classes="panel type-panel",
                ),
                Vertical(
                    Static(id="guidelines-title", classes="panel-title"),
                    VerticalScroll(id="guidelines-content", classes="guidelines-content"),
                    classes="panel guidelines-panel wide",
                ),
                classes="homebrew-row",
            ),
            id="homebrew-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen."""
        self._refresh_type_list()
        self._load_guidelines()

    def _refresh_type_list(self) -> None:
        """Refresh the content type list."""
        type_list = self.query_one("#type-list", VerticalScroll)
        type_list.remove_children()

        for i, (type_id, type_name) in enumerate(self.content_types):
            selected = "▶ " if type_id == self.current_type else "  "
            type_list.mount(Static(
                f"{selected}[{i+1}] {type_name}",
                classes=f"type-item {'selected' if type_id == self.current_type else ''}",
            ))

    def _load_guidelines(self) -> None:
        """Load and display guidelines for the current content type."""
        try:
            from dnd_manager.data.balance import get_balance_guidelines

            guidelines = get_balance_guidelines()

            # Update title
            title = self.query_one("#guidelines-title", Static)
            type_name = dict(self.content_types).get(self.current_type, self.current_type)
            title.update(f"{type_name.upper()} BALANCE GUIDELINES")

            # Get guidelines content
            content = self.query_one("#guidelines-content", VerticalScroll)
            content.remove_children()

            # Get the specific guidelines for this content type
            prompt = guidelines.get_prompt_for_content_type(self.current_type)

            if prompt:
                # Split into lines and display
                for line in prompt.split("\n"):
                    content.mount(Static(f"  {line}", classes="guideline-line"))
            else:
                content.mount(Static("  No specific guidelines found for this content type.", classes="no-content"))
                content.mount(Static(""))
                content.mount(Static("  Use the AI Homebrew Chat [A] to create balanced content", classes="hint"))
                content.mount(Static("  with AI assistance.", classes="hint"))

            # Add general tips at the bottom
            content.mount(Static(""))
            content.mount(Static("  ─────────────────────────────────────────", classes="separator"))
            content.mount(Static("  TIPS FOR BALANCED HOMEBREW:", classes="section-header"))
            content.mount(Static("  • Compare to similar official content", classes="tip"))
            content.mount(Static("  • Start conservative, buff if needed", classes="tip"))
            content.mount(Static("  • Consider edge cases and combos", classes="tip"))
            content.mount(Static("  • Playtest before finalizing", classes="tip"))
            content.mount(Static(""))
            content.mount(Static("  Press [A] to start an AI-assisted homebrew session", classes="hint"))

        except Exception as e:
            content = self.query_one("#guidelines-content", VerticalScroll)
            content.remove_children()
            content.mount(Static(f"  Error loading guidelines: {e}", classes="error"))
            content.mount(Static(""))
            content.mount(Static("  You can still use AI Homebrew Chat [A] for assistance.", classes="hint"))

    def _switch_type(self, type_id: str) -> None:
        """Switch to a different content type."""
        self.current_type = type_id
        self._refresh_type_list()
        self._load_guidelines()

    def action_show_spells(self) -> None:
        """Show spell guidelines."""
        self._switch_type("spell")

    def action_show_items(self) -> None:
        """Show magic item guidelines."""
        self._switch_type("magic_item")

    def action_show_races(self) -> None:
        """Show race/species guidelines."""
        self._switch_type("race")

    def action_show_classes(self) -> None:
        """Show class guidelines."""
        self._switch_type("class")

    def action_show_feats(self) -> None:
        """Show feat guidelines."""
        self._switch_type("feat")

    def action_ai_homebrew(self) -> None:
        """Open AI chat in homebrew mode."""
        self.app.push_screen(HomebrewChatScreen(self.character, self.current_type))

    def action_library(self) -> None:
        """Open the homebrew library browser."""
        self.app.push_screen(LibraryBrowserScreen())

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


class HomebrewChatScreen(Screen):
    """Screen for AI-assisted homebrew creation."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("ctrl+l", "clear", "Clear Chat"),
    ]

    def __init__(
        self,
        character: Optional[Character] = None,
        content_type: str = "spell",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.content_type = content_type
        self._messages: list = []
        self._provider = None

    def compose(self) -> ComposeResult:
        type_name = self.content_type.replace("_", " ").title()
        yield Header()
        yield Container(
            Static(f"AI Homebrew Assistant - {type_name}", classes="title"),
            Static("Create balanced homebrew content with AI guidance", classes="subtitle"),
            RichLog(id="chat-log", wrap=True, markup=True),
            Horizontal(
                Input(placeholder="Describe your homebrew idea...", id="chat-input"),
                Button("Send", id="btn-send", variant="primary"),
                classes="chat-input-row",
            ),
            id="chat-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize chat on mount."""
        self.query_one("#chat-input", Input).focus()
        log = self.query_one("#chat-log", RichLog)

        type_name = self.content_type.replace("_", " ").title()
        log.write(f"[bold cyan]AI Homebrew Assistant - {type_name}[/]")
        log.write("")
        log.write("I'll help you create balanced homebrew content. Tell me about")
        log.write("your concept and I'll guide you through the design process.")
        log.write("")
        log.write("[bold]Example prompts:[/]")

        if self.content_type == "spell":
            log.write("• 'Create a 3rd level fire spell that also slows enemies'")
            log.write("• 'I want a cantrip that creates a small light construct'")
        elif self.content_type == "magic_item":
            log.write("• 'A rare sword that deals extra damage to undead'")
            log.write("• 'A cloak that grants limited invisibility'")
        elif self.content_type == "race":
            log.write("• 'A race of living crystals with psychic abilities'")
            log.write("• 'Small fey creatures with illusion magic'")
        elif self.content_type == "class":
            log.write("• 'A half-caster focused on time manipulation'")
            log.write("• 'A martial class that uses cooking as magic'")
        elif self.content_type == "feat":
            log.write("• 'A feat for characters who fight with two shields'")
            log.write("• 'A feat that improves counterspelling'")
        else:
            log.write("• Describe your concept and desired power level")
            log.write("• I'll suggest mechanics and balance considerations")

        log.write("")

    async def _get_provider(self):
        """Get the AI provider."""
        if self._provider is None:
            from dnd_manager.ai import get_provider
            manager = get_config_manager()
            provider_name = manager.get("ai.default_provider") or "gemini"
            self._provider = get_provider(provider_name)
        return self._provider

    async def _send_message(self, message: str) -> None:
        """Send a message to the AI."""
        from dnd_manager.ai.context import build_homebrew_system_prompt
        from dnd_manager.ai.base import AIMessage, MessageRole

        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold green]You:[/] {message}")

        provider = await self._get_provider()
        if not provider:
            log.write("[bold red]Error:[/] No AI provider configured.")
            log.write("Run: ccvault config set ai.gemini.api_key YOUR_KEY")
            return

        if not provider.is_configured():
            log.write(f"[bold red]Error:[/] {provider.name} not configured.")
            log.write(f"Run: ccvault config set ai.{provider.name}.api_key YOUR_KEY")
            return

        # Build homebrew-specific system prompt
        system_prompt = build_homebrew_system_prompt(
            content_type=self.content_type,
            character=self.character,
        )
        self._messages.append(AIMessage(role=MessageRole.USER, content=message))

        all_messages = [
            AIMessage(role=MessageRole.SYSTEM, content=system_prompt),
            *self._messages,
        ]

        log.write("[bold blue]Assistant:[/] ", end="")

        try:
            response_text = ""
            async for chunk in provider.chat_stream(all_messages):
                log.write(chunk, end="")
                response_text += chunk
            log.write("")  # Newline after response

            # Save assistant response
            self._messages.append(AIMessage(role=MessageRole.ASSISTANT, content=response_text))

        except Exception as e:
            log.write(f"\n[bold red]Error:[/] {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle send button."""
        if event.button.id == "btn-send":
            self._submit_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key."""
        if event.input.id == "chat-input":
            self._submit_message()

    def _submit_message(self) -> None:
        """Submit the current message."""
        input_widget = self.query_one("#chat-input", Input)
        message = input_widget.value.strip()
        if message:
            input_widget.value = ""
            asyncio.create_task(self._send_message(message))

    def action_back(self) -> None:
        """Return to homebrew screen."""
        self.app.pop_screen()

    def action_clear(self) -> None:
        """Clear chat history."""
        self._messages.clear()
        log = self.query_one("#chat-log", RichLog)
        log.clear()
        log.write("[bold cyan]Chat cleared![/]")
        log.write("Describe your homebrew concept to get started.\n")
        self.notify("Chat cleared")


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
            Static("↑/↓ Navigate  Type to jump  [/] Search  [F1-F4] Filter", classes="subtitle"),
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
                f"{selected}[{item.content_type.value[:6]}] {item.name[:25]}{installed}",
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
            details_widget.mount(Static("  [INSTALLED]", classes="installed-badge"))
        else:
            details_widget.mount(Static("  Press [I] to install", classes="hint"))

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
        for line in preview.split("\n")[:10]:
            details_widget.mount(Static(f"    {line}", classes="content-preview"))
        if len(preview.split("\n")) > 10:
            details_widget.mount(Static("    ...", classes="content-preview"))

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
        except Exception:
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
        except Exception:
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


class MulticlassSelectScreen(Screen):
    """Screen for selecting which class to level in (multiclassing)."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
        Binding("up", "prev", "Previous"),
        Binding("down", "next", "Next"),
        Binding("p", "select_primary", "Primary Class"),
    ]

    def __init__(self, character: Character, on_select, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.on_select = on_select
        self.selected_idx = 0
        self.classes: list[tuple[str, str, bool]] = []  # (name, status, can_mc)
        self._build_class_list()

    def _build_class_list(self) -> None:
        """Build list of available classes for multiclassing."""
        from dnd_manager.data import ALL_CLASSES, MULTICLASS_REQUIREMENTS
        from dnd_manager.config import get_config_manager

        config = get_config_manager().config
        enforce = config.enforcement.enforce_multiclass_requirements

        # Add primary class first (always available)
        self.classes.append((
            self.character.primary_class.name,
            f"(Primary - Level {self.character.primary_class.level})",
            True,
        ))

        # Add existing multiclass entries
        for mc in self.character.multiclass:
            self.classes.append((
                mc.name,
                f"(Level {mc.level})",
                True,
            ))

        # Add all other classes
        existing = {self.character.primary_class.name} | {mc.name for mc in self.character.multiclass}
        for class_name in sorted(ALL_CLASSES.keys()):
            if class_name not in existing:
                can_mc, reason = self.character.can_multiclass_into(class_name, enforce)
                if can_mc:
                    status = "(New multiclass)"
                else:
                    status = f"({reason})"
                self.classes.append((class_name, status, can_mc))

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Select Class to Level In", classes="title"),
            Static("Choose which class to gain a level in", classes="subtitle"),
            VerticalScroll(id="class-list", classes="options-list"),
            Static("", id="req-info"),
            Static(""),
            Static("  [P] Primary Class  [Enter] Select  [Esc] Cancel", classes="hint"),
            id="multiclass-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the display."""
        self._refresh_list()
        self._show_requirements()

    def _refresh_list(self) -> None:
        """Refresh the class list display."""
        class_list = self.query_one("#class-list", VerticalScroll)
        class_list.remove_children()

        for i, (name, status, can_mc) in enumerate(self.classes):
            selected = "▶ " if i == self.selected_idx else "  "
            style = "" if can_mc else "dim"
            class_list.mount(Static(
                f"{selected}{name} {status}",
                classes=f"option-item {style}",
            ))

    def _show_requirements(self) -> None:
        """Show multiclass requirements for selected class."""
        from dnd_manager.data import MULTICLASS_REQUIREMENTS

        req_info = self.query_one("#req-info", Static)

        if self.selected_idx >= len(self.classes):
            req_info.update("")
            return

        class_name, _, _ = self.classes[self.selected_idx]
        reqs = MULTICLASS_REQUIREMENTS.get(class_name, {})

        if not reqs:
            req_info.update(f"  {class_name}: No requirements")
            return

        req_strs = []
        for ability, minimum in reqs.items():
            current = getattr(self.character.abilities, ability, None)
            current_val = current.base if current else 0
            met = "✓" if current_val >= minimum else "✗"
            req_strs.append(f"{ability.title()} {minimum} {met}")

        req_info.update(f"  Requirements: {', '.join(req_strs)}")

    def action_prev(self) -> None:
        """Select previous class."""
        if self.selected_idx > 0:
            self.selected_idx -= 1
            self._refresh_list()
            self._show_requirements()

    def action_next(self) -> None:
        """Select next class."""
        if self.selected_idx < len(self.classes) - 1:
            self.selected_idx += 1
            self._refresh_list()
            self._show_requirements()

    def action_select(self) -> None:
        """Select the highlighted class."""
        if self.selected_idx >= len(self.classes):
            return

        class_name, _, can_mc = self.classes[self.selected_idx]

        if not can_mc:
            self.notify("Cannot multiclass into this class - requirements not met", severity="error")
            return

        # If selecting primary class, return None
        if class_name == self.character.primary_class.name:
            self.on_select(None)
        else:
            self.on_select(class_name)

        self.app.pop_screen()

    def action_select_primary(self) -> None:
        """Quick select primary class."""
        self.on_select(None)
        self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel without selecting."""
        self.app.pop_screen()


class LevelManagementScreen(Screen):
    """Screen for managing character level - both up and down.

    Supports multiclassing - press [c] to choose which class to level in.
    """

    BINDINGS = [
        Binding("escape", "back", "Back (No Changes)"),
        Binding("enter", "save_changes", "Save Changes"),
        Binding("up", "level_up", "Level Up"),
        Binding("down", "level_down", "Level Down"),
        Binding("+", "level_up", "+1 Level"),
        Binding("-", "level_down", "-1 Level"),
        Binding("c", "choose_class", "Choose Class"),
        Binding("r", "roll_hp", "Roll HP"),
        Binding("a", "average_hp", "Average HP"),
        Binding("f", "choose_feat", "Choose Feat"),
        Binding("1", "asi_strength", "+1 STR"),
        Binding("2", "asi_dexterity", "+1 DEX"),
        Binding("3", "asi_constitution", "+1 CON"),
        Binding("4", "asi_intelligence", "+1 INT"),
        Binding("5", "asi_wisdom", "+1 WIS"),
        Binding("6", "asi_charisma", "+1 CHA"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.original_level = character.total_level
        self.target_level = character.total_level
        self.has_changes = False

        # Multiclass support - which class to level in
        # None = primary class, otherwise the class name
        self.leveling_class: str | None = None

        # Level up tracking (for each level gained)
        self.hp_choices: dict[int, int] = {}  # level -> hp gain
        self.asi_choices: dict[int, list[str]] = {}  # level -> [abilities] or ["feat:name"]

        # Current level being configured (for HP/ASI choices)
        self.configuring_level: int | None = None

        # Confirmation state - requires double-press of Enter for safety
        self.confirming: bool = False

    def compose(self) -> ComposeResult:
        c = self.character
        yield Header()
        yield Container(
            Static(f"Level Management - {c.name}", classes="title"),
            Static("", id="level-subtitle", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("LEVEL ADJUSTMENT", classes="panel-title"),
                    Static("", id="level-display"),
                    Static("", id="class-display"),
                    Static(""),
                    Static("  [↑/+] Increase Level", classes="option"),
                    Static("  [↓/-] Decrease Level", classes="option"),
                    Static("  [C]   Choose Class (Multiclass)", classes="option"),
                    Static(""),
                    Static("", id="hp-section"),
                    Static(""),
                    Static("", id="asi-section"),
                    classes="panel level-panel",
                ),
                Vertical(
                    Static("CHANGES PREVIEW", classes="panel-title"),
                    VerticalScroll(id="changes-preview", classes="changes-list"),
                    classes="panel preview-panel",
                ),
                classes="level-mgmt-row",
            ),
            Static("", id="warning-section", classes="warning-section"),
            Static(""),
            Static("  [Enter] Save Changes  [Esc] Cancel", id="hint-text", classes="hint"),
            id="level-mgmt-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize display."""
        self._refresh_display()

    def _get_leveling_class_name(self) -> str:
        """Get the display name for the class being leveled."""
        if self.leveling_class:
            return self.leveling_class
        return self.character.primary_class.name

    def _refresh_display(self) -> None:
        """Refresh all display elements."""
        c = self.character
        level_diff = self.target_level - self.original_level

        # Update subtitle
        subtitle = self.query_one("#level-subtitle", Static)
        if level_diff > 0:
            subtitle.update(f"Level {self.original_level} → {self.target_level} (+{level_diff})")
        elif level_diff < 0:
            subtitle.update(f"Level {self.original_level} → {self.target_level} ({level_diff})")
        else:
            subtitle.update(f"Current Level: {self.original_level}")

        # Update level display
        level_display = self.query_one("#level-display", Static)
        level_display.update(f"  Current: {self.original_level}  →  Target: {self.target_level}")

        # Update class display (for multiclassing)
        class_display = self.query_one("#class-display", Static)
        leveling_class = self._get_leveling_class_name()
        if self.leveling_class and self.leveling_class != c.primary_class.name:
            class_display.update(f"  Leveling in: {leveling_class} (multiclass)")
        else:
            class_display.update(f"  Leveling in: {leveling_class}")

        # Update HP section
        self._update_hp_section()

        # Update ASI section
        self._update_asi_section()

        # Update changes preview
        self._update_changes_preview()

        # Update warning section
        self._update_warning_section()

        self.has_changes = (self.target_level != self.original_level)

        # Update hint text based on confirmation state
        hint_widget = self.query_one("#hint-text", Static)
        if self.confirming:
            hint_widget.update("  ⚠ Press [Enter] again to CONFIRM changes  [Esc] Cancel")
        else:
            hint_widget.update("  [Enter] Save Changes  [Esc] Cancel")

    def _update_hp_section(self) -> None:
        """Update HP configuration section."""
        hp_widget = self.query_one("#hp-section", Static)

        if self.target_level <= self.original_level:
            hp_widget.update("")
            return

        # Show HP choices needed for levels gained
        lines = ["  HP FOR LEVELS GAINED:"]
        for level in range(self.original_level + 1, self.target_level + 1):
            if level in self.hp_choices:
                lines.append(f"    Level {level}: +{self.hp_choices[level]} HP ✓")
            else:
                lines.append(f"    Level {level}: (choose) [R]oll or [A]verage")
                self.configuring_level = level
                break
        else:
            self.configuring_level = None

        hp_widget.update("\n".join(lines))

    def _update_asi_section(self) -> None:
        """Update ASI/Feat section."""
        asi_widget = self.query_one("#asi-section", Static)

        if self.target_level <= self.original_level:
            asi_widget.update("")
            return

        ruleset = self.character.get_ruleset()
        if not ruleset:
            asi_widget.update("")
            return

        asi_levels = ruleset.get_asi_levels(self.character.primary_class.name)
        needed_asis = [lvl for lvl in range(self.original_level + 1, self.target_level + 1) if lvl in asi_levels]

        if not needed_asis:
            asi_widget.update("")
            return

        lines = ["  ASI/FEAT CHOICES:"]
        for level in needed_asis:
            if level in self.asi_choices:
                choice = self.asi_choices[level]
                if choice and choice[0].startswith("feat:"):
                    lines.append(f"    Level {level}: Feat - {choice[0][5:]} ✓")
                else:
                    abilities = ", ".join(a.upper() for a in choice)
                    lines.append(f"    Level {level}: +1 to {abilities} ✓")
            else:
                lines.append(f"    Level {level}: [F] Feat or [1-6] Abilities")

        lines.append("")
        lines.append("  [1]STR [2]DEX [3]CON [4]INT [5]WIS [6]CHA")

        asi_widget.update("\n".join(lines))

    def _update_changes_preview(self) -> None:
        """Update the changes preview panel."""
        from dnd_manager.data import get_features_at_level

        preview = self.query_one("#changes-preview", VerticalScroll)
        preview.remove_children()

        level_diff = self.target_level - self.original_level

        if level_diff == 0:
            preview.mount(Static("  No changes", classes="no-changes"))
            return

        if level_diff > 0:
            preview.mount(Static("  GAINING:", classes="gain-header"))
            total_hp = sum(self.hp_choices.values())
            if total_hp:
                preview.mount(Static(f"    +{total_hp} HP"))
            preview.mount(Static(f"    +{level_diff} Hit Dice"))

            for level in range(self.original_level + 1, self.target_level + 1):
                features = get_features_at_level(self.character.primary_class.name, level)
                if features:
                    for f in features:
                        preview.mount(Static(f"    • {f.name} (Lv{level})"))

        else:  # level_diff < 0
            preview.mount(Static("  LOSING:", classes="lose-header"))

            # Calculate HP loss
            die_value = int(self.character.combat.hit_dice.die.replace("d", ""))
            con_mod = self.character.abilities.constitution.modifier
            avg_hp = (die_value // 2) + 1 + con_mod
            total_hp_loss = abs(level_diff) * max(1, avg_hp)
            preview.mount(Static(f"    -{total_hp_loss} HP (estimated)"))
            preview.mount(Static(f"    -{abs(level_diff)} Hit Dice"))

            for level in range(self.original_level, self.target_level, -1):
                features = get_features_at_level(self.character.primary_class.name, level)
                if features:
                    for f in features:
                        preview.mount(Static(f"    • {f.name} (Lv{level})"))

    def _update_warning_section(self) -> None:
        """Update warning section for level down."""
        warning = self.query_one("#warning-section", Static)

        if self.target_level < self.original_level:
            lines = [
                "",
                "  ⚠ WARNING: Reducing level will:",
                "    • Remove HP, hit dice, and features gained at those levels",
                "    • Remove any ASIs or feats selected at those levels",
                "    • This change CANNOT be undone automatically",
                "",
            ]
            warning.update("\n".join(lines))
        else:
            warning.update("")

    def action_level_up(self) -> None:
        """Increase target level."""
        if self.target_level < 20:
            self.target_level += 1
            self.confirming = False  # Reset confirmation on change
            self._refresh_display()

    def action_level_down(self) -> None:
        """Decrease target level."""
        if self.target_level > 1:
            self.target_level -= 1
            # Clear HP/ASI choices for removed levels
            self.hp_choices = {k: v for k, v in self.hp_choices.items() if k <= self.target_level}
            self.asi_choices = {k: v for k, v in self.asi_choices.items() if k <= self.target_level}
            self.confirming = False  # Reset confirmation on change
            self._refresh_display()

    def action_choose_class(self) -> None:
        """Open class selection for multiclassing."""
        if self.target_level <= self.original_level:
            self.notify("Select a higher target level first to multiclass", severity="warning")
            return

        def on_class_selected(class_name: str | None):
            self.leveling_class = class_name
            self._refresh_display()

        self.app.push_screen(MulticlassSelectScreen(self.character, on_select=on_class_selected))

    def _get_hit_die_value(self) -> int:
        """Get the numeric value of the hit die."""
        return int(self.character.combat.hit_dice.die.replace("d", ""))

    def action_roll_hp(self) -> None:
        """Roll HP for current configuring level."""
        if self.configuring_level is None:
            self.notify("No level needs HP configuration", severity="warning")
            return

        from dnd_manager.dice import DiceRoller

        die_value = self._get_hit_die_value()
        con_mod = self.character.abilities.constitution.modifier

        roller = DiceRoller()
        result = roller.roll(f"1d{die_value}")
        roll = result.total
        hp_gain = max(1, roll + con_mod)

        self.hp_choices[self.configuring_level] = hp_gain
        self.notify(f"Level {self.configuring_level}: Rolled {roll} + {con_mod} = +{hp_gain} HP")
        self._refresh_display()

    def action_average_hp(self) -> None:
        """Take average HP for current configuring level."""
        if self.configuring_level is None:
            self.notify("No level needs HP configuration", severity="warning")
            return

        die_value = self._get_hit_die_value()
        con_mod = self.character.abilities.constitution.modifier
        average = (die_value // 2) + 1
        hp_gain = max(1, average + con_mod)

        self.hp_choices[self.configuring_level] = hp_gain
        self.notify(f"Level {self.configuring_level}: Average {average} + {con_mod} = +{hp_gain} HP")
        self._refresh_display()

    def _get_current_asi_level(self) -> int | None:
        """Get the ASI level currently needing configuration."""
        ruleset = self.character.get_ruleset()
        if not ruleset:
            return None

        asi_levels = ruleset.get_asi_levels(self.character.primary_class.name)
        for level in range(self.original_level + 1, self.target_level + 1):
            if level in asi_levels and level not in self.asi_choices:
                return level
        return None

    def _apply_asi(self, ability: str) -> None:
        """Apply an ASI to an ability."""
        level = self._get_current_asi_level()
        if level is None:
            self.notify("No ASI available to configure", severity="warning")
            return

        if level not in self.asi_choices:
            self.asi_choices[level] = []

        choices = self.asi_choices[level]
        if choices and choices[0].startswith("feat:"):
            self.notify("Already selected a feat for this level", severity="warning")
            return

        if len(choices) < 2:
            choices.append(ability)
            self.notify(f"Level {level}: +1 {ability.upper()}")
            self._refresh_display()

    def action_asi_strength(self) -> None:
        self._apply_asi("strength")

    def action_asi_dexterity(self) -> None:
        self._apply_asi("dexterity")

    def action_asi_constitution(self) -> None:
        self._apply_asi("constitution")

    def action_asi_intelligence(self) -> None:
        self._apply_asi("intelligence")

    def action_asi_wisdom(self) -> None:
        self._apply_asi("wisdom")

    def action_asi_charisma(self) -> None:
        self._apply_asi("charisma")

    def action_choose_feat(self) -> None:
        """Open feat picker."""
        level = self._get_current_asi_level()
        if level is None:
            self.notify("No ASI available to configure", severity="warning")
            return

        def on_feat_selected(feat):
            self.asi_choices[level] = [f"feat:{feat.name}"]
            self._refresh_display()

        self.app.push_screen(FeatPickerScreen(self.character, on_select=on_feat_selected))

    def action_save_changes(self) -> None:
        """Save the level changes with confirmation."""
        if not self.has_changes:
            self.notify("No changes to save")
            self.app.pop_screen()
            return

        level_diff = self.target_level - self.original_level

        # First press: enter confirmation mode
        if not self.confirming:
            # Validate level up requirements before confirming
            if level_diff > 0:
                # Check HP choices
                for level in range(self.original_level + 1, self.target_level + 1):
                    if level not in self.hp_choices:
                        self.notify(f"Choose HP for level {level} first ([R]oll or [A]verage)", severity="error")
                        return

                # Check ASI choices
                ruleset = self.character.get_ruleset()
                if ruleset:
                    asi_levels = ruleset.get_asi_levels(self.character.primary_class.name)
                    for level in range(self.original_level + 1, self.target_level + 1):
                        if level in asi_levels:
                            if level not in self.asi_choices or len(self.asi_choices[level]) < 2:
                                if level not in self.asi_choices or not self.asi_choices[level][0].startswith("feat:"):
                                    self.notify(f"Complete ASI for level {level} (need 2 abilities or a feat)", severity="error")
                                    return

            # Enter confirmation mode
            self.confirming = True
            self._refresh_display()
            self.notify("Press Enter again to confirm level changes", severity="warning")
            return

        # Second press: apply changes
        # Validate level up requirements
        if level_diff > 0:
            # Check HP choices
            for level in range(self.original_level + 1, self.target_level + 1):
                if level not in self.hp_choices:
                    self.notify(f"Choose HP for level {level} first ([R]oll or [A]verage)", severity="error")
                    return

            # Check ASI choices
            ruleset = self.character.get_ruleset()
            if ruleset:
                asi_levels = ruleset.get_asi_levels(self.character.primary_class.name)
                for level in range(self.original_level + 1, self.target_level + 1):
                    if level in asi_levels:
                        if level not in self.asi_choices or len(self.asi_choices[level]) < 2:
                            if level not in self.asi_choices or not self.asi_choices[level][0].startswith("feat:"):
                                self.notify(f"Complete ASI for level {level} (need 2 abilities or a feat)", severity="error")
                                return

        # Apply changes
        c = self.character
        from dnd_manager.data import get_features_at_level
        from dnd_manager.models.character import Feature

        if level_diff > 0:
            # Level UP - determine which class to level in
            leveling_class_name = self.leveling_class or c.primary_class.name
            is_multiclass = self.leveling_class and self.leveling_class != c.primary_class.name

            # If multiclassing into a new class, validate requirements
            from dnd_manager.config import get_config_manager
            config = get_config_manager().config
            if is_multiclass:
                can_mc, reason = c.can_multiclass_into(
                    leveling_class_name,
                    enforce=config.enforcement.enforce_multiclass_requirements
                )
                if not can_mc:
                    self.notify(f"Cannot multiclass: {reason}", severity="error")
                    return

            for level in range(self.original_level + 1, self.target_level + 1):
                # Apply level to the correct class
                if is_multiclass:
                    # Check if already have levels in this class
                    existing_mc = next((mc for mc in c.multiclass if mc.name == leveling_class_name), None)
                    if existing_mc:
                        existing_mc.level += 1
                    else:
                        # Add new multiclass entry
                        from dnd_manager.models.character import CharacterClass
                        c.multiclass.append(CharacterClass(name=leveling_class_name, level=1))
                else:
                    c.primary_class.level += 1

                # Add HP
                hp_gain = self.hp_choices.get(level, 0)
                c.combat.hit_points.maximum += hp_gain
                c.combat.hit_points.current += hp_gain

                # Add hit die
                c.combat.hit_dice.total += 1
                c.combat.hit_dice.remaining += 1

                # Apply ASI
                if level in self.asi_choices:
                    choices = self.asi_choices[level]
                    if choices and choices[0].startswith("feat:"):
                        # Add feat
                        feat_name = choices[0][5:]
                        from dnd_manager.data import get_feat
                        feat_data = get_feat(feat_name)
                        if feat_data:
                            c.features.append(Feature(
                                name=feat_name,
                                source="feat",
                                description=feat_data.description,
                            ))
                    else:
                        # Apply ability increases
                        for ability in choices:
                            score = getattr(c.abilities, ability)
                            score.base = min(20, score.base + 1)

                # Add class features for the class being leveled
                # Get current level in that class
                if is_multiclass:
                    mc_class = next((mc for mc in c.multiclass if mc.name == leveling_class_name), None)
                    class_level = mc_class.level if mc_class else 1
                else:
                    class_level = c.primary_class.level

                class_features = get_features_at_level(leveling_class_name, class_level)
                if class_features:
                    for cf in class_features:
                        if not any(f.name == cf.name for f in c.features):
                            c.features.append(Feature(
                                name=cf.name,
                                source="class",
                                description=cf.description,
                                uses=cf.uses,
                                recharge=cf.recharge,
                            ))

            # Rebuild hit dice pool to match class composition (fixes multiclass)
            c.sync_hit_dice()

        else:
            # Level DOWN
            leveling_class_name = self.leveling_class or c.primary_class.name
            is_multiclass_down = self.leveling_class and self.leveling_class != c.primary_class.name

            for level in range(self.original_level, self.target_level, -1):
                # Get hit die for the class being de-leveled
                ruleset = c.get_ruleset()
                if ruleset:
                    class_def = ruleset.get_class_definition(leveling_class_name)
                    die_value = class_def.hit_die if class_def else 8
                else:
                    die_value = self._get_hit_die_value()

                # Calculate HP loss
                con_mod = c.abilities.constitution.modifier
                avg_hp = (die_value // 2) + 1
                hp_loss = max(1, avg_hp + con_mod)

                # Decrement the correct class
                if is_multiclass_down:
                    mc = next((m for m in c.multiclass if m.name == leveling_class_name), None)
                    if mc:
                        mc.level -= 1
                        if mc.level <= 0:
                            c.multiclass.remove(mc)
                else:
                    c.primary_class.level -= 1

                c.combat.hit_points.maximum = max(1, c.combat.hit_points.maximum - hp_loss)
                c.combat.hit_points.current = min(c.combat.hit_points.current, c.combat.hit_points.maximum)

                # Get current class level for feature removal
                if is_multiclass_down:
                    mc = next((m for m in c.multiclass if m.name == leveling_class_name), None)
                    class_level_for_features = (mc.level + 1) if mc else 1
                else:
                    class_level_for_features = c.primary_class.level + 1

                # Remove features from this class level
                features_at_level = get_features_at_level(leveling_class_name, class_level_for_features)
                if features_at_level:
                    for f in features_at_level:
                        c.features = [feat for feat in c.features if feat.name != f.name]

            # Rebuild hit dice pool to match class composition
            c.sync_hit_dice()

            # Check subclass removal for the class being leveled down
            ruleset = c.get_ruleset()
            if ruleset:
                if is_multiclass_down:
                    # Check if multiclass lost its subclass level
                    mc = next((m for m in c.multiclass if m.name == leveling_class_name), None)
                    if mc:
                        subclass_level = ruleset.get_subclass_level(leveling_class_name)
                        if mc.level < subclass_level and mc.subclass:
                            mc.subclass = None
                else:
                    subclass_level = ruleset.get_subclass_level(c.primary_class.name)
                    if c.primary_class.level < subclass_level and c.primary_class.subclass:
                        c.primary_class.subclass = None

        # Sync spell slots
        c.sync_spell_slots()

        # Save
        self.app.save_character()

        if level_diff > 0:
            self.notify(f"Leveled up to {c.total_level}!", severity="information")
        else:
            self.notify(f"Leveled down to {c.total_level}", severity="warning")

        # Refresh dashboard
        self.app.pop_screen()
        self.app.pop_screen()
        self.app.push_screen(MainDashboard(c))

    def action_back(self) -> None:
        """Cancel - if confirming, cancel confirmation; otherwise go back."""
        if self.confirming:
            self.confirming = False
            self._refresh_display()
            self.notify("Confirmation cancelled")
            return
        if self.has_changes:
            self.notify("Changes discarded")
        self.app.pop_screen()

    def _get_hit_die_value(self) -> int:
        """Get the numeric value of the hit die."""
        die = self.character.combat.hit_dice.die
        return int(die.replace("d", ""))

    def action_roll_hp(self) -> None:
        """Roll for HP increase."""
        from dnd_manager.dice import DiceRoller

        die_value = self._get_hit_die_value()
        con_mod = self.character.abilities.constitution.modifier

        roller = DiceRoller()
        result = roller.roll(f"1d{die_value}")
        roll = result.total
        self.hp_gain = max(1, roll + con_mod)  # Minimum 1 HP
        self.hp_rolled = True

        hp_widget = self.query_one("#hp-result", Static)
        hp_widget.update(f"  HP Roll: {roll} + {con_mod} (CON) = +{self.hp_gain} HP")
        self.notify(f"Rolled {roll} on d{die_value}!")

    def action_average_hp(self) -> None:
        """Take average HP increase."""
        die_value = self._get_hit_die_value()
        con_mod = self.character.abilities.constitution.modifier

        # Average is (die_value / 2) + 1, rounded up
        average = (die_value // 2) + 1
        self.hp_gain = max(1, average + con_mod)
        self.hp_rolled = True

        hp_widget = self.query_one("#hp-result", Static)
        hp_widget.update(f"  HP Average: {average} + {con_mod} (CON) = +{self.hp_gain} HP")
        self.notify(f"Taking average: {average}")

    def _apply_asi(self, ability: str) -> None:
        """Apply an ASI to an ability."""
        if not self.is_asi_level:
            return

        if self.asi_choice == "feat":
            self.notify("Already selected a feat!", severity="warning")
            return

        self.asi_choice = "asi"

        if len(self.asi_abilities) < 2:
            self.asi_abilities.append(ability)
            self.notify(f"+1 {ability.upper()}")
            self._update_asi_display()

            if len(self.asi_abilities) == 2:
                self.notify("ASI complete! Press Enter to confirm.", severity="information")

    def action_asi_strength(self) -> None:
        self._apply_asi("strength")

    def action_asi_dexterity(self) -> None:
        self._apply_asi("dexterity")

    def action_asi_constitution(self) -> None:
        self._apply_asi("constitution")

    def action_asi_intelligence(self) -> None:
        self._apply_asi("intelligence")

    def action_asi_wisdom(self) -> None:
        self._apply_asi("wisdom")

    def action_asi_charisma(self) -> None:
        self._apply_asi("charisma")

    def action_choose_feat(self) -> None:
        """Open feat picker."""
        if not self.is_asi_level:
            self.notify("No ASI available at this level", severity="warning")
            return

        if self.asi_choice == "asi" and self.asi_abilities:
            self.notify("Already chose ASI! Clear with new level up.", severity="warning")
            return

        def on_feat_selected(feat):
            self.asi_choice = "feat"
            self.feat_selected = feat.name
            self._update_asi_display()

        self.app.push_screen(FeatPickerScreen(self.character, on_select=on_feat_selected))

    def action_confirm(self) -> None:
        """Confirm the level up."""
        if not self.hp_rolled:
            self.notify("Choose HP method first: [R]oll or [A]verage", severity="warning")
            return

        # Check ASI requirements
        if self.is_asi_level:
            if self.asi_choice == "asi" and len(self.asi_abilities) < 2:
                self.notify("Complete your ASI: choose 2 ability increases or select a feat", severity="warning")
                return
            if self.asi_choice is None:
                self.notify("Choose ASI (+2 to abilities) or a Feat before confirming", severity="warning")
                return

        c = self.character

        # Increase level
        c.primary_class.level += 1

        # Increase HP
        c.combat.hit_points.maximum += self.hp_gain
        c.combat.hit_points.current += self.hp_gain

        # Increase hit dice
        c.combat.hit_dice.total += 1
        c.combat.hit_dice.remaining += 1

        # Apply ASI if chosen
        if self.asi_choice == "asi":
            for ability in self.asi_abilities:
                score = getattr(c.abilities, ability)
                score.base = min(20, score.base + 1)  # Cap at 20

        # Add class features gained at this level
        from dnd_manager.data import get_features_at_level
        from dnd_manager.models.character import Feature

        class_features = get_features_at_level(c.primary_class.name, c.total_level)
        if class_features:
            for cf in class_features:
                # Check if feature already exists (avoid duplicates)
                if not any(f.name == cf.name for f in c.features):
                    c.features.append(Feature(
                        name=cf.name,
                        source="class",
                        description=cf.description,
                        uses=cf.uses,
                        recharge=cf.recharge,
                    ))

        # Sync spell slots
        c.sync_spell_slots()

        # Save
        self.app.save_character()

        self.notify(f"Level up complete! Now level {c.total_level}", severity="information")

        # Check if subclass selection is needed
        if self.needs_subclass:
            self.app.pop_screen()
            self.app.pop_screen()
            self.app.push_screen(MainDashboard(c))
            self.app.push_screen(SubclassPickerScreen(c))
        else:
            self.app.pop_screen()
            # Refresh the dashboard
            self.app.pop_screen()
            self.app.push_screen(MainDashboard(c))

    def action_cancel(self) -> None:
        """Cancel level up."""
        self.app.pop_screen()


class FeatPickerScreen(ListNavigationMixin, Screen):
    """Screen for selecting a feat during level up or character creation."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select Feat"),
        Binding("/", "search", "Search"),
    ]

    def __init__(self, character: Character, on_select: callable = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.on_select = on_select
        self.selected_index = 0
        self.search_query = ""
        self.filtered_feats: list = []
        self._last_letter = ""
        self._last_letter_index = -1

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Select a Feat", classes="title"),
            Static("↑/↓ Navigate  Type to jump  [/] Search  Enter Select", classes="subtitle"),
            Horizontal(
                Input(placeholder="Search feats...", id="feat-search"),
                classes="search-row",
            ),
            Horizontal(
                Vertical(
                    Static("AVAILABLE FEATS", classes="panel-title"),
                    VerticalScroll(id="feat-list", classes="feat-browser-list"),
                    classes="panel browser-panel",
                ),
                Vertical(
                    Static("FEAT DETAILS", classes="panel-title"),
                    VerticalScroll(id="feat-details", classes="feat-details"),
                    classes="panel browser-panel",
                ),
                classes="browser-row",
            ),
            id="feat-picker-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load feats."""
        self._refresh_feat_list()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "feat-search":
            self.search_query = event.value.lower()
            self.selected_index = 0
            self._refresh_feat_list()

    def _refresh_feat_list(self) -> None:
        """Refresh the feat list."""
        from dnd_manager.data import ALL_FEATS, GENERAL_FEATS

        # Use general feats for ASI selection
        feats = GENERAL_FEATS

        # Filter by search query
        if self.search_query:
            self.filtered_feats = [
                f for f in feats
                if self.search_query in f.name.lower()
                or self.search_query in f.description.lower()
            ]
        else:
            self.filtered_feats = list(feats)

        # Sort alphabetically
        self.filtered_feats.sort(key=lambda f: f.name)

        # Update list
        list_widget = self.query_one("#feat-list", VerticalScroll)
        list_widget.remove_children()

        for i, feat in enumerate(self.filtered_feats):
            # Check prerequisites
            can_take, reason = self._can_take_feat(feat)
            prereq_mark = "" if can_take else " ✗"

            feat_class = "feat-row"
            if i == self.selected_index:
                feat_class += " selected"
            if not can_take:
                feat_class += " unavailable"

            list_widget.mount(ClickableListItem(
                f"  {feat.name}{prereq_mark}",
                index=i,
                classes=feat_class,
            ))

        if not self.filtered_feats:
            list_widget.mount(Static("  (No feats found)", classes="no-items"))

        self._refresh_feat_details()

    def _can_take_feat(self, feat) -> tuple[bool, str]:
        """Check if the character can take this feat."""
        if not feat.prerequisites:
            return True, ""

        c = self.character

        for prereq in feat.prerequisites:
            prereq_lower = prereq.lower()

            # Check ability score prerequisites
            for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                if ability in prereq_lower:
                    # Extract required value (e.g., "Strength 13" -> 13)
                    import re
                    match = re.search(r'(\d+)', prereq)
                    if match:
                        required = int(match.group(1))
                        current = getattr(c.abilities, ability).total
                        if current < required:
                            return False, prereq

            # Check spellcasting prerequisite
            if "spellcasting" in prereq_lower or "cast a spell" in prereq_lower:
                if not c.spellcasting.ability:
                    return False, prereq

            # Check proficiency prerequisites
            if "proficiency" in prereq_lower:
                if "armor" in prereq_lower:
                    if "heavy" in prereq_lower and "Heavy" not in c.proficiencies.armor:
                        return False, prereq

        return True, ""

    def _refresh_feat_details(self) -> None:
        """Show details of the selected feat."""
        details_widget = self.query_one("#feat-details", VerticalScroll)
        details_widget.remove_children()

        if not self.filtered_feats or self.selected_index >= len(self.filtered_feats):
            details_widget.mount(Static("  Select a feat to see details", classes="hint"))
            return

        feat = self.filtered_feats[self.selected_index]

        details_widget.mount(Static(f"  {feat.name}", classes="feat-name"))
        details_widget.mount(Static(f"  Category: {feat.category}", classes="feat-category"))

        if feat.prerequisites:
            details_widget.mount(Static(""))
            details_widget.mount(Static("  Prerequisites:", classes="section-header"))
            for prereq in feat.prerequisites:
                can_meet = "✓" if self._can_take_feat(feat)[0] else "✗"
                details_widget.mount(Static(f"    {can_meet} {prereq}", classes="prereq-item"))

        details_widget.mount(Static(""))
        details_widget.mount(Static("  Description:", classes="section-header"))
        # Word wrap description
        desc = feat.description
        words = desc.split()
        lines = []
        current_line = "    "
        for word in words:
            if len(current_line) + len(word) + 1 > 60:
                lines.append(current_line)
                current_line = "    " + word
            else:
                current_line += " " + word if current_line.strip() else "    " + word
        if current_line.strip():
            lines.append(current_line)
        for line in lines:
            details_widget.mount(Static(line, classes="feat-desc"))

        if feat.benefits:
            details_widget.mount(Static(""))
            details_widget.mount(Static("  Benefits:", classes="section-header"))
            for benefit in feat.benefits:
                details_widget.mount(Static(f"    • {benefit}", classes="benefit-item"))

        if feat.ability_increase:
            details_widget.mount(Static(""))
            details_widget.mount(Static(f"  Ability Increase: {feat.ability_increase}", classes="ability-inc"))

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.filtered_feats

    def _get_item_name(self, item) -> str:
        return item.name

    def _get_scroll_container(self):
        try:
            return self.query_one("#feat-list", VerticalScroll)
        except Exception:
            return None

    def _get_item_widget_class(self) -> str:
        return "feat-row"

    def _update_selection(self) -> None:
        """Update selection - refreshes the list display."""
        self._refresh_feat_list()
        self.call_after_refresh(self._scroll_to_selection)

    def key_up(self) -> None:
        """Move selection up."""
        self._navigate_up()

    def key_down(self) -> None:
        """Move selection down."""
        self._navigate_down()

    def on_key(self, event) -> None:
        """Handle letter keys for jump navigation."""
        # Don't jump if search input is focused
        try:
            if self.query_one("#feat-search", Input).has_focus:
                return
        except Exception:
            pass
        if self._handle_key_for_letter_jump(event.key):
            event.prevent_default()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        """Handle mouse click on a list item."""
        if 0 <= event.index < len(self.filtered_feats):
            self.selected_index = event.index
            self._update_selection()

    def action_search(self) -> None:
        """Focus the search input."""
        self.query_one("#feat-search", Input).focus()

    def action_select(self) -> None:
        """Select the current feat."""
        if not self.filtered_feats or self.selected_index >= len(self.filtered_feats):
            self.notify("No feat selected", severity="warning")
            return

        feat = self.filtered_feats[self.selected_index]
        can_take, reason = self._can_take_feat(feat)

        if not can_take:
            self.notify(f"Cannot take this feat: {reason}", severity="error")
            return

        # Add feat to character
        from dnd_manager.models.character import Feature
        self.character.features.append(Feature(
            name=feat.name,
            source="feat",
            description=feat.description,
        ))

        self.app.save_character()
        self.notify(f"Added feat: {feat.name}", severity="information")

        if self.on_select:
            self.on_select(feat)

        self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel feat selection."""
        self.app.pop_screen()


class SubclassPickerScreen(ListNavigationMixin, Screen):
    """Screen for selecting a subclass."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select Subclass"),
    ]

    def __init__(self, character: Character, on_select: callable = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.on_select = on_select
        self.selected_index = 0
        self.subclasses: list = []
        self._last_letter = ""
        self._last_letter_index = -1

    def compose(self) -> ComposeResult:
        class_name = self.character.primary_class.name
        yield Header()
        yield Container(
            Static(f"Choose Your {class_name} Subclass", classes="title"),
            Static("↑/↓ Navigate  Type to jump  Enter Select", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("AVAILABLE SUBCLASSES", classes="panel-title"),
                    VerticalScroll(id="subclass-list", classes="subclass-browser-list"),
                    classes="panel browser-panel",
                ),
                Vertical(
                    Static("SUBCLASS DETAILS", classes="panel-title"),
                    VerticalScroll(id="subclass-details", classes="subclass-details"),
                    classes="panel browser-panel",
                ),
                classes="browser-row",
            ),
            id="subclass-picker-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load subclasses."""
        self._refresh_subclass_list()

    def _refresh_subclass_list(self) -> None:
        """Refresh the subclass list."""
        from dnd_manager.data import get_subclasses_for_class

        class_name = self.character.primary_class.name
        self.subclasses = get_subclasses_for_class(class_name)

        list_widget = self.query_one("#subclass-list", VerticalScroll)
        list_widget.remove_children()

        for i, subclass in enumerate(self.subclasses):
            subclass_class = "subclass-row"
            if i == self.selected_index:
                subclass_class += " selected"

            list_widget.mount(ClickableListItem(
                f"  {subclass.name}",
                index=i,
                classes=subclass_class,
            ))

        if not self.subclasses:
            list_widget.mount(Static(f"  (No subclasses found for {class_name})", classes="no-items"))

        self._refresh_subclass_details()

    def _refresh_subclass_details(self) -> None:
        """Show details of the selected subclass."""
        details_widget = self.query_one("#subclass-details", VerticalScroll)
        details_widget.remove_children()

        if not self.subclasses or self.selected_index >= len(self.subclasses):
            details_widget.mount(Static("  Select a subclass to see details", classes="hint"))
            return

        subclass = self.subclasses[self.selected_index]

        details_widget.mount(Static(f"  {subclass.name}", classes="subclass-name"))
        details_widget.mount(Static(f"  For: {subclass.class_name}", classes="subclass-class"))
        details_widget.mount(Static(""))

        if subclass.description:
            details_widget.mount(Static("  Description:", classes="section-header"))
            desc = subclass.description[:200] + "..." if len(subclass.description) > 200 else subclass.description
            details_widget.mount(Static(f"    {desc}", classes="subclass-desc"))

        details_widget.mount(Static(""))
        details_widget.mount(Static("  Features:", classes="section-header"))
        for feature in subclass.features[:5]:  # Show first 5 features
            details_widget.mount(Static(f"    Lv{feature.level}: {feature.name}", classes="feature-item"))

        if len(subclass.features) > 5:
            details_widget.mount(Static(f"    ... and {len(subclass.features) - 5} more", classes="hint"))

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.subclasses

    def _get_item_name(self, item) -> str:
        return item.name

    def _get_scroll_container(self):
        try:
            return self.query_one("#subclass-list", VerticalScroll)
        except Exception:
            return None

    def _get_item_widget_class(self) -> str:
        return "subclass-row"

    def _update_selection(self) -> None:
        """Update selection - refreshes the list display."""
        self._refresh_subclass_list()
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
        if 0 <= event.index < len(self.subclasses):
            self.selected_index = event.index
            self._update_selection()

    def action_select(self) -> None:
        """Select the current subclass."""
        if not self.subclasses or self.selected_index >= len(self.subclasses):
            self.notify("No subclass selected", severity="warning")
            return

        subclass = self.subclasses[self.selected_index]
        self.character.primary_class.subclass = subclass.name

        self.app.save_character()
        self.notify(f"Selected subclass: {subclass.name}", severity="information")

        if self.on_select:
            self.on_select(subclass)

        self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel subclass selection."""
        self.app.pop_screen()


class CharacterEditorScreen(Screen):
    """Screen for editing character attributes."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save Changes"),
        Binding("1", "edit_abilities", "Edit Abilities"),
        Binding("2", "edit_hp", "Edit HP"),
        Binding("3", "edit_info", "Edit Info"),
        Binding("4", "edit_custom_stats", "Custom Stats"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Edit Character - {self.character.name}", classes="title"),
            Static("[1] Abilities  [2] HP  [3] Info  [4] Custom Stats  [S] Save  [Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("ABILITY SCORES", classes="panel-title"),
                    self._build_ability_editor(),
                    classes="panel editor-panel",
                ),
                Vertical(
                    Static("COMBAT STATS", classes="panel-title"),
                    self._build_combat_editor(),
                    Static(""),
                    Static("CHARACTER INFO", classes="panel-title"),
                    self._build_info_editor(),
                    classes="panel editor-panel",
                ),
                classes="editor-row",
            ),
            id="editor-container",
        )
        yield Footer()

    def _build_ability_editor(self) -> Vertical:
        """Build ability score editor."""
        container = Vertical(classes="ability-editor")
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = getattr(self.character.abilities, ability)
            container.compose_add_child(Static(
                f"  {ability[:3].upper()}: {score.base:2d} + {score.bonus:2d} = {score.total:2d} ({score.modifier_str})",
                classes="editor-row",
            ))
        container.compose_add_child(Static(""))
        container.compose_add_child(Static("  Use [1] to edit scores", classes="hint"))
        return container

    def _build_combat_editor(self) -> Vertical:
        """Build combat stats editor."""
        c = self.character
        hp = c.combat.hit_points
        container = Vertical(classes="combat-editor")
        container.compose_add_child(Static(f"  HP: {hp.current}/{hp.maximum} (temp: {hp.temporary})", classes="editor-row"))
        container.compose_add_child(Static(f"  AC: {c.combat.total_ac} (base: {c.combat.armor_class.base})", classes="editor-row"))
        container.compose_add_child(Static(f"  Speed: {c.combat.total_speed} ft", classes="editor-row"))
        container.compose_add_child(Static(f"  Hit Dice: {c.combat.hit_dice.remaining}/{c.combat.hit_dice.total}", classes="editor-row"))
        container.compose_add_child(Static(""))
        container.compose_add_child(Static("  Use [2] to edit HP", classes="hint"))
        return container

    def _build_info_editor(self) -> Vertical:
        """Build character info editor."""
        c = self.character
        container = Vertical(classes="info-editor")
        container.compose_add_child(Static(f"  Name: {c.name}", classes="editor-row"))
        container.compose_add_child(Static(f"  Class: {c.primary_class.name} {c.primary_class.level}", classes="editor-row"))
        container.compose_add_child(Static(f"  {c.get_species_term()}: {c.species or 'Not set'}", classes="editor-row"))
        container.compose_add_child(Static(f"  Background: {c.background or 'Not set'}", classes="editor-row"))
        container.compose_add_child(Static(f"  Alignment: {c.alignment.display_name}", classes="editor-row"))
        container.compose_add_child(Static(""))
        container.compose_add_child(Static("  Use [3] to edit info", classes="hint"))
        return container

    def action_edit_abilities(self) -> None:
        """Edit ability scores."""
        self.app.push_screen(AbilityEditorScreen(self.character))

    def action_edit_hp(self) -> None:
        """Edit HP values."""
        self.app.push_screen(HPEditorScreen(self.character))

    def action_edit_info(self) -> None:
        """Edit character info."""
        self.notify("Info editor coming soon!", severity="information")

    def action_edit_custom_stats(self) -> None:
        """Edit custom stats (Luck, Renown, etc.)."""
        self.app.push_screen(CustomStatsScreen(self.character))

    def action_save(self) -> None:
        """Save character changes."""
        self.app.save_character()
        self.notify("Character saved!", severity="information")

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()


class CustomStatsScreen(Screen):
    """Screen for managing custom stats (Luck, Renown, Piety, etc.)."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("a", "add_stat", "Add Stat"),
        Binding("d", "delete_stat", "Delete"),
        Binding("t", "add_template", "Add Template"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_index = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Custom Stats", classes="title"),
            Static("↑/↓ Select  ←/→ Adjust Value  [A] Add  [D] Delete  [T] Templates  [Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("YOUR CUSTOM STATS", classes="panel-title"),
                    VerticalScroll(id="stats-list", classes="stats-list"),
                    classes="panel stats-panel",
                ),
                Vertical(
                    Static("STAT DETAILS", classes="panel-title"),
                    VerticalScroll(id="stat-details", classes="stat-details"),
                    Static(""),
                    Static("AVAILABLE TEMPLATES", classes="panel-title"),
                    VerticalScroll(id="templates-list", classes="templates-list"),
                    classes="panel details-panel",
                ),
                classes="stats-row",
            ),
            id="custom-stats-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load stats."""
        self._refresh_stats()
        self._refresh_templates()

    def _refresh_stats(self) -> None:
        """Refresh the custom stats list."""
        list_widget = self.query_one("#stats-list", VerticalScroll)
        list_widget.remove_children()

        if not self.character.custom_stats:
            list_widget.mount(Static("  (No custom stats)", classes="no-items"))
            list_widget.mount(Static("  Press [A] to add or [T] for templates", classes="hint"))
        else:
            for i, stat in enumerate(self.character.custom_stats):
                stat_class = "stat-row"
                if i == self.selected_index:
                    stat_class += " selected"

                # Build value display with bounds
                bounds = ""
                if stat.min_value is not None or stat.max_value is not None:
                    min_str = str(stat.min_value) if stat.min_value is not None else "-∞"
                    max_str = str(stat.max_value) if stat.max_value is not None else "∞"
                    bounds = f" ({min_str} to {max_str})"

                list_widget.mount(Static(
                    f"  {'▶ ' if i == self.selected_index else '  '}{stat.name}: {stat.value}{bounds}",
                    classes=stat_class,
                ))

        self._refresh_stat_details()

    def _refresh_stat_details(self) -> None:
        """Show details of the selected stat."""
        details_widget = self.query_one("#stat-details", VerticalScroll)
        details_widget.remove_children()

        if not self.character.custom_stats or self.selected_index >= len(self.character.custom_stats):
            details_widget.mount(Static("  Select a stat to see details", classes="hint"))
            return

        stat = self.character.custom_stats[self.selected_index]

        details_widget.mount(Static(f"  {stat.name}", classes="stat-name"))
        details_widget.mount(Static(f"  Current Value: {stat.value}", classes="stat-value"))

        if stat.min_value is not None:
            details_widget.mount(Static(f"  Minimum: {stat.min_value}", classes="stat-bound"))
        if stat.max_value is not None:
            details_widget.mount(Static(f"  Maximum: {stat.max_value}", classes="stat-bound"))

        if stat.description:
            details_widget.mount(Static(""))
            details_widget.mount(Static(f"  {stat.description}", classes="stat-desc"))

    def _refresh_templates(self) -> None:
        """Show available stat templates."""
        from dnd_manager.models.character import CUSTOM_STAT_TEMPLATES

        templates_widget = self.query_one("#templates-list", VerticalScroll)
        templates_widget.remove_children()

        for name, template in CUSTOM_STAT_TEMPLATES.items():
            # Check if already added
            already_has = any(s.name.lower() == template.name.lower() for s in self.character.custom_stats)
            status = " ✓" if already_has else ""
            templates_widget.mount(Static(f"  • {template.name}{status}", classes="template-item"))

    def key_up(self) -> None:
        """Move selection up."""
        if self.character.custom_stats and self.selected_index > 0:
            self.selected_index -= 1
            self._refresh_stats()

    def key_down(self) -> None:
        """Move selection down."""
        if self.character.custom_stats and self.selected_index < len(self.character.custom_stats) - 1:
            self.selected_index += 1
            self._refresh_stats()

    def key_left(self) -> None:
        """Decrease selected stat value."""
        if self.character.custom_stats and self.selected_index < len(self.character.custom_stats):
            stat = self.character.custom_stats[self.selected_index]
            stat.adjust(-1)
            self.app.save_character()
            self._refresh_stats()

    def key_right(self) -> None:
        """Increase selected stat value."""
        if self.character.custom_stats and self.selected_index < len(self.character.custom_stats):
            stat = self.character.custom_stats[self.selected_index]
            stat.adjust(1)
            self.app.save_character()
            self._refresh_stats()

    def action_add_stat(self) -> None:
        """Add a new custom stat."""
        from dnd_manager.models.character import CustomStat

        # Create a basic new stat
        new_stat = CustomStat(
            name=f"Custom Stat {len(self.character.custom_stats) + 1}",
            value=0,
            description="A custom stat"
        )
        self.character.custom_stats.append(new_stat)
        self.app.save_character()
        self.selected_index = len(self.character.custom_stats) - 1
        self._refresh_stats()
        self._refresh_templates()
        self.notify(f"Added: {new_stat.name}")

    def action_add_template(self) -> None:
        """Add a stat from templates."""
        from dnd_manager.models.character import CUSTOM_STAT_TEMPLATES, CustomStat

        # Find next template not already added
        for name, template in CUSTOM_STAT_TEMPLATES.items():
            already_has = any(s.name.lower() == template.name.lower() for s in self.character.custom_stats)
            if not already_has:
                # Create a copy of the template
                new_stat = CustomStat(
                    name=template.name,
                    value=template.value,
                    min_value=template.min_value,
                    max_value=template.max_value,
                    description=template.description,
                )
                self.character.custom_stats.append(new_stat)
                self.app.save_character()
                self.selected_index = len(self.character.custom_stats) - 1
                self._refresh_stats()
                self._refresh_templates()
                self.notify(f"Added template: {new_stat.name}")
                return

        self.notify("All templates already added!", severity="warning")

    def action_delete_stat(self) -> None:
        """Delete the selected stat."""
        if not self.character.custom_stats or self.selected_index >= len(self.character.custom_stats):
            self.notify("No stat selected", severity="warning")
            return

        stat = self.character.custom_stats.pop(self.selected_index)
        self.app.save_character()
        self.selected_index = max(0, self.selected_index - 1)
        self._refresh_stats()
        self._refresh_templates()
        self.notify(f"Deleted: {stat.name}")

    def action_back(self) -> None:
        """Return to editor."""
        self.app.pop_screen()


class AbilityEditorScreen(Screen):
    """Screen for editing ability scores."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save"),
        Binding("b", "manage_bonuses", "Manage Bonuses"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_ability = 0
        self.abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Edit Ability Scores", classes="title"),
            Static("↑/↓ Select  ←/→ Adjust  [B] Bonuses  [S] Save  [Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(id="ability-list", classes="panel ability-panel"),
                Vertical(id="bonus-details", classes="panel bonus-panel"),
                classes="ability-editor-row",
            ),
            id="ability-editor-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Populate ability list."""
        self._refresh_abilities()

    def _refresh_abilities(self) -> None:
        """Refresh the ability list display."""
        container = self.query_one("#ability-list", Vertical)
        container.remove_children()

        container.mount(Static("ABILITY SCORES", classes="panel-title"))
        container.mount(Static(""))

        for i, ability in enumerate(self.abilities):
            score = getattr(self.character.abilities, ability)
            selected = "▶ " if i == self.selected_ability else "  "

            # Count bonuses for this ability
            ability_bonuses = [b for b in self.character.stat_bonuses if b.ability.lower() == ability]
            bonus_marker = f" [{len(ability_bonuses)} bonus]" if ability_bonuses else ""

            container.mount(Static(
                f"{selected}{ability.upper():15} Base: {score.base:2d}  Bonus: {score.bonus:+2d}  Total: {score.total:2d} ({score.modifier_str}){bonus_marker}",
                classes=f"ability-edit-row {'selected' if i == self.selected_ability else ''}",
            ))

        self._refresh_bonus_details()

    def _refresh_bonus_details(self) -> None:
        """Refresh the bonus details panel."""
        details = self.query_one("#bonus-details", Vertical)
        details.remove_children()

        ability = self.abilities[self.selected_ability]
        ability_bonuses = [b for b in self.character.stat_bonuses if b.ability.lower() == ability]

        details.mount(Static(f"BONUSES FOR {ability.upper()}", classes="panel-title"))
        details.mount(Static(""))

        if ability_bonuses:
            for bonus in ability_bonuses:
                temp_mark = " (temp)" if bonus.temporary else ""
                if bonus.is_override:
                    details.mount(Static(f"  • {bonus.source}: SET TO {bonus.override_value}{temp_mark}"))
                else:
                    details.mount(Static(f"  • {bonus.source}: +{bonus.bonus}{temp_mark}"))
                if bonus.duration:
                    details.mount(Static(f"      Duration: {bonus.duration}", classes="bonus-duration"))
        else:
            details.mount(Static("  (No bonuses)", classes="no-items"))
            details.mount(Static(""))
            details.mount(Static("  Press [B] to add bonuses", classes="hint"))

    def key_up(self) -> None:
        """Move selection up."""
        self.selected_ability = (self.selected_ability - 1) % len(self.abilities)
        self._refresh_abilities()

    def key_down(self) -> None:
        """Move selection down."""
        self.selected_ability = (self.selected_ability + 1) % len(self.abilities)
        self._refresh_abilities()

    def key_left(self) -> None:
        """Decrease selected ability."""
        ability = self.abilities[self.selected_ability]
        score = getattr(self.character.abilities, ability)
        if score.base > 1:
            score.base -= 1
            self._refresh_abilities()

    def key_right(self) -> None:
        """Increase selected ability."""
        ability = self.abilities[self.selected_ability]
        score = getattr(self.character.abilities, ability)
        if score.base < 30:
            score.base += 1
            self._refresh_abilities()

    def action_manage_bonuses(self) -> None:
        """Open the stat bonus management screen."""
        ability = self.abilities[self.selected_ability]
        self.app.push_screen(StatBonusScreen(self.character, ability))

    def action_save(self) -> None:
        """Save and go back."""
        self.app.save_character()
        self.notify("Ability scores saved!")
        self.app.pop_screen()

    def action_back(self) -> None:
        """Go back without saving."""
        self.app.pop_screen()


class StatBonusScreen(Screen):
    """Screen for managing stat bonuses from various sources."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("a", "add_bonus", "Add Bonus"),
        Binding("d", "delete_bonus", "Delete"),
        Binding("t", "toggle_temporary", "Toggle Temp"),
    ]

    def __init__(self, character: Character, ability: str = "strength", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.ability = ability
        self.selected_index = 0
        self.bonuses: list = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Stat Bonuses - {self.ability.upper()}", classes="title"),
            Static("↑/↓ Select  [A] Add  [D] Delete  [T] Toggle Temp  [Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("ACTIVE BONUSES", classes="panel-title"),
                    VerticalScroll(id="bonus-list", classes="bonus-list"),
                    classes="panel bonus-list-panel",
                ),
                Vertical(
                    Static("BONUS DETAILS", classes="panel-title"),
                    VerticalScroll(id="bonus-details", classes="bonus-details-panel"),
                    Static(""),
                    Static("COMMON SOURCES", classes="panel-title"),
                    Static("  • Magic items (e.g., Belt of Giant Strength)"),
                    Static("  • Spells (e.g., Enhance Ability, Bull's Strength)"),
                    Static("  • Blessings/Boons (DM-granted)"),
                    Static("  • Racial abilities"),
                    Static("  • Feats (e.g., Resilient)"),
                    classes="panel details-panel",
                ),
                classes="bonus-row",
            ),
            id="stat-bonus-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load bonuses."""
        self._refresh_bonuses()

    def _refresh_bonuses(self) -> None:
        """Refresh the bonus list."""
        self.bonuses = [b for b in self.character.stat_bonuses if b.ability.lower() == self.ability]

        list_widget = self.query_one("#bonus-list", VerticalScroll)
        list_widget.remove_children()

        if not self.bonuses:
            list_widget.mount(Static("  (No bonuses)", classes="no-items"))
            list_widget.mount(Static(""))
            list_widget.mount(Static("  Press [A] to add a bonus", classes="hint"))
        else:
            for i, bonus in enumerate(self.bonuses):
                bonus_class = "bonus-row"
                if i == self.selected_index:
                    bonus_class += " selected"

                temp_mark = " ⏱" if bonus.temporary else ""
                selector = "▶ " if i == self.selected_index else "  "

                if bonus.is_override:
                    text = f"{selector}{bonus.source}: SET TO {bonus.override_value}{temp_mark}"
                else:
                    text = f"{selector}{bonus.source}: +{bonus.bonus}{temp_mark}"

                list_widget.mount(Static(text, classes=bonus_class))

        self._refresh_details()

    def _refresh_details(self) -> None:
        """Show details of selected bonus."""
        details = self.query_one("#bonus-details", VerticalScroll)
        details.remove_children()

        if not self.bonuses or self.selected_index >= len(self.bonuses):
            details.mount(Static("  Select a bonus to see details", classes="hint"))
            return

        bonus = self.bonuses[self.selected_index]

        details.mount(Static(f"  Source: {bonus.source}", classes="bonus-source"))
        details.mount(Static(f"  Ability: {bonus.ability.upper()}", classes="bonus-ability"))

        if bonus.is_override:
            details.mount(Static(f"  Type: Override (sets to {bonus.override_value})", classes="bonus-type"))
        else:
            details.mount(Static(f"  Type: Bonus (+{bonus.bonus})", classes="bonus-type"))

        details.mount(Static(f"  Temporary: {'Yes' if bonus.temporary else 'No'}", classes="bonus-temp"))

        if bonus.duration:
            details.mount(Static(f"  Duration: {bonus.duration}", classes="bonus-duration"))

        if bonus.notes:
            details.mount(Static(""))
            details.mount(Static(f"  Notes: {bonus.notes}", classes="bonus-notes"))

    def key_up(self) -> None:
        """Move selection up."""
        if self.bonuses and self.selected_index > 0:
            self.selected_index -= 1
            self._refresh_bonuses()

    def key_down(self) -> None:
        """Move selection down."""
        if self.bonuses and self.selected_index < len(self.bonuses) - 1:
            self.selected_index += 1
            self._refresh_bonuses()

    def action_add_bonus(self) -> None:
        """Add a new bonus."""
        from dnd_manager.models.character import StatBonus

        # Create a basic new bonus
        new_bonus = StatBonus(
            source="New Bonus",
            ability=self.ability,
            bonus=1,
            temporary=False,
        )
        self.character.stat_bonuses.append(new_bonus)
        self.app.save_character()
        self._refresh_bonuses()
        self.selected_index = len(self.bonuses) - 1
        self._refresh_bonuses()
        self.notify("Added new bonus - edit the source name as needed")

    def action_delete_bonus(self) -> None:
        """Delete selected bonus."""
        if not self.bonuses or self.selected_index >= len(self.bonuses):
            self.notify("No bonus selected", severity="warning")
            return

        bonus = self.bonuses[self.selected_index]
        self.character.stat_bonuses.remove(bonus)
        self.app.save_character()
        self.selected_index = max(0, self.selected_index - 1)
        self._refresh_bonuses()
        self.notify(f"Removed bonus: {bonus.source}")

    def action_toggle_temporary(self) -> None:
        """Toggle temporary status of selected bonus."""
        if not self.bonuses or self.selected_index >= len(self.bonuses):
            self.notify("No bonus selected", severity="warning")
            return

        bonus = self.bonuses[self.selected_index]
        bonus.temporary = not bonus.temporary
        self.app.save_character()
        status = "temporary" if bonus.temporary else "permanent"
        self.notify(f"{bonus.source} is now {status}")
        self._refresh_bonuses()

    def action_back(self) -> None:
        """Return to ability editor."""
        self.app.pop_screen()


class HPEditorScreen(Screen):
    """Screen for editing HP values."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save"),
        Binding("h", "heal", "Heal"),
        Binding("d", "damage", "Take Damage"),
        Binding("t", "temp_hp", "Add Temp HP"),
        Binding("m", "set_max", "Set Max HP"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        hp = self.character.combat.hit_points
        yield Header()
        yield Container(
            Static("Edit Hit Points", classes="title"),
            Static("[H] Heal  [D] Damage  [T] Temp HP  [M] Set Max  [S] Save", classes="subtitle"),
            Vertical(
                Static(f"Current HP: {hp.current}", id="current-hp", classes="hp-display"),
                Static(f"Maximum HP: {hp.maximum}", id="max-hp", classes="hp-display"),
                Static(f"Temporary HP: {hp.temporary}", id="temp-hp", classes="hp-display"),
                Static(""),
                Horizontal(
                    Input(placeholder="Amount", id="hp-amount", type="integer"),
                    classes="hp-input-row",
                ),
                classes="panel hp-editor-panel",
            ),
            id="hp-editor-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus the input."""
        self.query_one("#hp-amount", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key - default to heal (most common action)."""
        if event.input.id == "hp-amount":
            amount = self._get_amount()
            if amount > 0:
                self.action_heal()
            else:
                self.notify("Enter an amount, then press Enter to heal or use H/D/T/M keys")

    def _get_amount(self) -> int:
        """Get the amount from the input."""
        try:
            return int(self.query_one("#hp-amount", Input).value or "0")
        except ValueError:
            return 0

    def _refresh_display(self) -> None:
        """Refresh HP display."""
        hp = self.character.combat.hit_points
        self.query_one("#current-hp", Static).update(f"Current HP: {hp.current}")
        self.query_one("#max-hp", Static).update(f"Maximum HP: {hp.maximum}")
        self.query_one("#temp-hp", Static).update(f"Temporary HP: {hp.temporary}")
        self.query_one("#hp-amount", Input).value = ""

    def action_heal(self) -> None:
        """Heal the character."""
        amount = self._get_amount()
        if amount > 0:
            hp = self.character.combat.hit_points
            hp.current = min(hp.current + amount, hp.maximum)
            self.notify(f"Healed {amount} HP")
            self._refresh_display()

    def action_damage(self) -> None:
        """Apply damage to the character."""
        amount = self._get_amount()
        if amount > 0:
            hp = self.character.combat.hit_points
            # Temp HP absorbs damage first
            if hp.temporary > 0:
                absorbed = min(hp.temporary, amount)
                hp.temporary -= absorbed
                amount -= absorbed
            hp.current = max(hp.current - amount, 0)
            self.notify(f"Took {self._get_amount()} damage")
            self._refresh_display()

    def action_temp_hp(self) -> None:
        """Add temporary HP."""
        amount = self._get_amount()
        if amount > 0:
            hp = self.character.combat.hit_points
            hp.temporary = max(hp.temporary, amount)  # Temp HP doesn't stack
            self.notify(f"Added {amount} temporary HP")
            self._refresh_display()

    def action_set_max(self) -> None:
        """Set maximum HP."""
        amount = self._get_amount()
        if amount > 0:
            hp = self.character.combat.hit_points
            hp.maximum = amount
            hp.current = min(hp.current, hp.maximum)
            self.notify(f"Max HP set to {amount}")
            self._refresh_display()

    def action_save(self) -> None:
        """Save and go back."""
        self.app.save_character()
        self.notify("HP saved!")
        self.app.pop_screen()

    def action_back(self) -> None:
        """Go back."""
        self.app.pop_screen()


class InventoryScreen(ListNavigationMixin, Screen):
    """Screen for managing equipment and inventory."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("+", "add_item", "Add Item"),
        Binding("-", "drop_item", "Drop Item"),
        Binding("enter", "equip_toggle", "Equip/Unequip"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_index = 0
        self._last_letter = ""
        self._last_letter_index = -1

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
                    Static("[A] Add item"),
                    Static("[D] Drop selected"),
                    Static("[E] Equip/Unequip"),
                    Static("[G] Manage gold"),
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
            list_widget.mount(Static("  Press [+] to add items", classes="empty-state-hint"))
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
        self.notify("Currency management coming soon!", severity="information")

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.character.equipment.items

    def _get_item_name(self, item) -> str:
        return item.name

    def _get_scroll_container(self):
        try:
            return self.query_one("#equipment-list", VerticalScroll)
        except Exception:
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

    def __init__(self, character: Character, **kwargs) -> None:
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
            Static("↑/↓ Navigate  Type to jump  [/] Search  [6-0] Rarity  [-] All", classes="subtitle"),
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
        for line in lines[:15]:  # Limit to first 15 lines
            details_widget.mount(Static(line, classes="item-desc"))
        if len(lines) > 15:
            details_widget.mount(Static("    ...", classes="item-desc"))

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
        except Exception:
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
        except Exception:
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


class FeaturesScreen(Screen):
    """Screen for viewing class features, feats, and traits."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("u", "use_feature", "Use Feature"),
        Binding("r", "rest", "Rest (Recover Uses)"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
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
                # Show description (truncated)
                if feature.description:
                    desc = feature.description[:80] + "..." if len(feature.description) > 80 else feature.description
                    class_list.mount(Static(f"      {desc}", classes="feature-desc"))

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
                            desc = feature.description[:80] + "..." if len(feature.description) > 80 else feature.description
                            class_list.mount(Static(f"      {desc}", classes="feature-desc"))

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
            # Show truncated description
            desc = feature.description[:60] + "..." if len(feature.description) > 60 else feature.description
            container.mount(Static(f"    {desc}", classes="feature-desc"))

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


class SpellBrowserScreen(ListNavigationMixin, Screen):
    """Screen for browsing and adding SRD spells."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "add_spell", "Add Spell"),
        Binding("/", "search", "Search"),
    ]

    def __init__(self, character: Character, spell_type: str = "known", **kwargs) -> None:
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
            Static("↑/↓ Navigate  Type to jump  [/] Search  Enter Add", classes="subtitle"),
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
        except Exception:
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
        except Exception:
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


class SpellsScreen(Screen):
    """Screen for managing spells."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("c", "cast", "Cast Spell"),
        Binding("p", "toggle_prepared", "Toggle Prepared"),
        Binding("r", "rest", "Rest (Recover Slots)"),
        Binding("/", "search", "Search"),
        Binding("b", "browse", "Browse Spells"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.selected_spell: Optional[str] = None
        self.selected_level: int = 0

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
                    Static("[C] Cast selected spell"),
                    Static("[P] Toggle prepared"),
                    Static("[R] Short/Long rest"),
                    Static("[/] Search spells"),
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

        if not known:
            spells_list.mount(Static("  No spells known yet", classes="empty-state"))
            spells_list.mount(Static("  Press [B] to browse spells", classes="empty-state-hint"))
        else:
            # Group by level (simple approach - just list them)
            for spell in sorted(known):
                is_prepared = spell in prepared
                prefix = "◆" if is_prepared else "○"
                spell_class = "spell-item prepared" if is_prepared else "spell-item"
                spells_list.mount(Static(f"  {prefix} {spell}", classes=spell_class))

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

    def action_toggle_prepared(self) -> None:
        """Toggle prepared status of a spell."""
        self.notify("Select a spell to toggle (feature coming soon)", severity="information")

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
        self.app.push_screen(SpellBrowserScreen(self.character))

    def action_browse(self) -> None:
        """Browse and add spells."""
        self.app.push_screen(SpellBrowserScreen(self.character))

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()


class NotesScreen(Screen):
    """Screen for viewing and editing character notes."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("e", "edit_notes", "Edit Notes"),
        Binding("b", "edit_backstory", "Edit Backstory"),
        Binding("s", "session_notes", "Session Notes"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Notes - {self.character.name}", classes="title"),
            Static("[E] Edit Notes  [B] Edit Backstory  [S] Session Notes  [Esc] Back", classes="subtitle"),
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

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
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
            Static("[N] New  [E] Edit  [D] Delete  [/] Search  [S] Toggle Semantic", classes="subtitle"),
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
            title = note.title[:30] if note.title else "(Untitled)"
            if len(note.title) > 30:
                title += "..."

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
        except Exception:
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
        except Exception:
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
        character: Optional[Character] = None,
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
            Static("[Ctrl+S] Save  [Esc] Cancel", classes="subtitle"),
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


class MainDashboard(Screen):
    """Main character dashboard screen."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
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
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character

    def compose(self) -> ComposeResult:
        c = self.character

        yield Header()
        yield Container(
            # Top row: Abilities, Character Info, Combat, Quick Actions
            Horizontal(
                AbilityBlock(c, classes="panel ability-panel"),
                CharacterInfo(c, classes="panel char-info-panel"),
                CombatStats(c, classes="panel combat-panel"),
                QuickActions(classes="panel actions-panel"),
                classes="top-row",
            ),
            # Bottom row: Skills, Spell Slots, Prepared Spells
            Horizontal(
                SkillList(c, classes="panel skills-panel"),
                Vertical(
                    SpellSlots(c, classes="panel spells-panel"),
                    PreparedSpells(c, classes="panel prepared-panel"),
                    classes="spells-column",
                ),
                classes="bottom-row",
            ),
            id="dashboard",
        )
        yield Footer()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_save(self) -> None:
        """Save the current character."""
        self.app.save_character()
        self.notify("Character saved!", severity="information")

    def action_new_character(self) -> None:
        """Create a new character."""
        self.app.action_new_character()

    def action_open_character(self) -> None:
        """Open an existing character."""
        self.app.action_open_character()

    def action_spells(self) -> None:
        """Open spells screen."""
        self.app.push_screen(SpellsScreen(self.character))

    def action_inventory(self) -> None:
        """Open inventory screen."""
        self.app.push_screen(InventoryScreen(self.character))

    def action_features(self) -> None:
        """Open features screen."""
        self.app.push_screen(FeaturesScreen(self.character))

    def action_notes(self) -> None:
        """Open notes screen."""
        self.app.push_screen(NotesScreen(self.character))

    def action_ai_chat(self) -> None:
        """Open AI chat screen."""
        self.app.push_screen(AIChatScreen(self.character))

    def action_roll(self) -> None:
        """Open dice roller."""
        self.app.push_screen(DiceRollerScreen(self.character))

    def action_edit(self) -> None:
        """Edit character."""
        self.app.push_screen(CharacterEditorScreen(self.character))

    def action_level(self) -> None:
        """Open level management screen."""
        self.app.push_screen(LevelManagementScreen(self.character))

    def action_help(self) -> None:
        """Show help."""
        self.app.push_screen(HelpScreen())

    def action_homebrew(self) -> None:
        """Open homebrew guidelines screen."""
        self.app.push_screen(HomebrewScreen(self.character))

    def action_settings(self) -> None:
        """Open settings screen."""
        self.app.push_screen(SettingsScreen())

    def action_short_rest(self) -> None:
        """Open short rest screen."""
        self.app.push_screen(ShortRestScreen(self.character))

    def action_long_rest(self) -> None:
        """Open long rest screen."""
        self.app.push_screen(LongRestScreen(self.character))


class ShortRestScreen(Screen):
    """Screen for taking a short rest with hit dice spending."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm Rest"),
        Binding("y", "confirm_yes", "Yes, Rest"),
        Binding("r", "roll_hit_die", "Roll Hit Die"),
        Binding("+", "add_die", "Spend +1 Die"),
        Binding("-", "remove_die", "Spend -1 Die"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.dice_to_spend = 0
        self.healing_rolls: list[int] = []
        self.total_healing = 0
        self.awaiting_confirmation = False

    def compose(self) -> ComposeResult:
        c = self.character
        hp = c.combat.hit_points
        hd_display = c.combat.get_hit_dice_display()

        yield Header()
        yield Container(
            Static("Short Rest", classes="title"),
            Static(f"{c.name} - HP: {hp.current}/{hp.maximum}", classes="subtitle"),
            Vertical(
                Static("SHORT REST OPTIONS", classes="panel-title"),
                Static(f"  Hit Dice Available: {hd_display}", id="hd-info"),
                Static(f"  CON Modifier: +{c.abilities.constitution.modifier}", id="con-info"),
                Static(""),
                Static("  Dice to Spend: 0", id="dice-count"),
                Static(""),
                Static("  [+] Add a die  [-] Remove a die", classes="option"),
                Static("  [R] Roll selected dice", classes="option"),
                Static(""),
                Static("  HEALING ROLLS:", classes="section-header"),
                VerticalScroll(id="healing-rolls", classes="healing-list"),
                Static(""),
                Static("  Total Healing: 0", id="total-healing"),
                Static(""),
                Static("", id="confirm-prompt"),
                classes="panel rest-panel",
            ),
            id="short-rest-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize display."""
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Refresh all display elements."""
        pool = self.character.combat.hit_dice_pool
        hd = self.character.combat.hit_dice

        # Update dice count
        dice_widget = self.query_one("#dice-count", Static)
        dice_widget.update(f"  Dice to Spend: {self.dice_to_spend}")

        # Update hit dice info
        hd_widget = self.query_one("#hd-info", Static)
        if pool and pool.pools:
            # Show pool format for multiclass
            total_remaining = pool.remaining - self.dice_to_spend
            hd_widget.update(f"  Hit Dice Available: {total_remaining}/{pool.total} ({pool.get_display_string()})")
        else:
            available = hd.remaining - self.dice_to_spend
            hd_widget.update(f"  Hit Dice Available: {available}/{hd.total} ({hd.die})")

        # Update healing rolls
        rolls_widget = self.query_one("#healing-rolls", VerticalScroll)
        rolls_widget.remove_children()
        if self.healing_rolls:
            con_mod = self.character.abilities.constitution.modifier
            for i, roll_data in enumerate(self.healing_rolls):
                # Handle both old format (int) and new format (int, die)
                if isinstance(roll_data, tuple):
                    roll, die = roll_data
                    total = max(1, roll + con_mod)
                    rolls_widget.mount(Static(f"    {die}: {roll} + {con_mod} (CON) = {total} HP"))
                else:
                    roll = roll_data
                    total = max(1, roll + con_mod)
                    rolls_widget.mount(Static(f"    Die {i+1}: {roll} + {con_mod} (CON) = {total} HP"))
        else:
            rolls_widget.mount(Static("    (No dice rolled yet)"))

        # Update total healing
        total_widget = self.query_one("#total-healing", Static)
        total_widget.update(f"  Total Healing: {self.total_healing}")

        # Update confirm prompt
        confirm_widget = self.query_one("#confirm-prompt", Static)
        if self.awaiting_confirmation:
            confirm_widget.update("  ➤ Take short rest? Press [Y] to confirm, [Esc] to cancel")
        else:
            confirm_widget.update("  Press [Enter] to take short rest  [Esc] to cancel")

    def action_add_die(self) -> None:
        """Add a hit die to spend."""
        pool = self.character.combat.hit_dice_pool
        hd = self.character.combat.hit_dice

        # Check actual available dice (pool if multiclass, simple hd otherwise)
        available = pool.remaining if (pool and pool.pools) else hd.remaining

        if self.dice_to_spend < available:
            self.dice_to_spend += 1
            self._refresh_display()
        else:
            self.notify("No more hit dice available!", severity="warning")

    def action_remove_die(self) -> None:
        """Remove a hit die from spending."""
        if self.dice_to_spend > 0:
            self.dice_to_spend -= 1
            self._refresh_display()

    def action_roll_hit_die(self) -> None:
        """Roll the selected hit dice for healing."""
        if self.dice_to_spend == 0:
            self.notify("Add dice to spend first! Press [+]", severity="warning")
            return

        from dnd_manager.dice import DiceRoller

        roller = DiceRoller()
        con_mod = self.character.abilities.constitution.modifier
        pool = self.character.combat.hit_dice_pool

        # Roll each die
        self.healing_rolls = []
        self.total_healing = 0

        # Track remaining dice during roll preview (don't modify actual pool yet)
        if pool and pool.pools:
            temp_remaining = {die: p.remaining for die, p in pool.pools.items()}
        else:
            temp_remaining = None

        for _ in range(self.dice_to_spend):
            # For multiclass, use pool (largest die first); else use simple die
            if temp_remaining is not None:
                # Get largest available die type from temp tracking
                die = None
                for d in sorted(temp_remaining.keys(), key=lambda x: int(x[1:]), reverse=True):
                    if temp_remaining[d] > 0:
                        die = d
                        temp_remaining[d] -= 1  # Track that we're using this die
                        break
                if die is None:
                    # No dice available - shouldn't happen if add_die validates correctly
                    self.notify("No hit dice available!", severity="error")
                    return
            else:
                die = self.character.combat.hit_dice.die

            result = roller.roll(f"1{die}")
            roll = result.total
            self.healing_rolls.append((roll, die))  # Track die type used
            healing = max(1, roll + con_mod)  # Minimum 1 HP per die
            self.total_healing += healing

        self.notify(f"Rolled {self.dice_to_spend} hit dice for {self.total_healing} HP!")
        self._refresh_display()

    def action_confirm(self) -> None:
        """Show confirmation prompt."""
        self.awaiting_confirmation = True
        self._refresh_display()

    def action_confirm_yes(self) -> None:
        """Actually execute the short rest after confirmation."""
        if not self.awaiting_confirmation:
            return

        c = self.character

        # Apply healing
        if self.total_healing > 0:
            hp = c.combat.hit_points
            old_hp = hp.current
            hp.current = min(hp.maximum, hp.current + self.total_healing)
            actual_healing = hp.current - old_hp

            # Spend hit dice (from pool if multiclassed)
            pool = c.combat.hit_dice_pool
            if pool and pool.pools:
                # Spend each die that was rolled
                for roll_data in self.healing_rolls:
                    if isinstance(roll_data, tuple):
                        _, die = roll_data
                        pool.spend(die)
                # Sync simple hit_dice for backward compat
                c.combat.hit_dice = pool.to_single()
            else:
                c.combat.hit_dice.remaining -= self.dice_to_spend

            self.notify(f"Short rest complete! Healed {actual_healing} HP", severity="information")
        else:
            self.notify("Short rest complete!", severity="information")

        # Recover short rest features
        for feature in c.features:
            if feature.uses and feature.recharge in ("short rest", "short_rest"):
                feature.used = 0

        self.app.save_character()
        self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel the short rest."""
        if self.awaiting_confirmation:
            self.awaiting_confirmation = False
            self._refresh_display()
        else:
            self.app.pop_screen()


class LongRestScreen(Screen):
    """Screen for taking a long rest with full recovery summary."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm Rest"),
        Binding("y", "confirm_yes", "Yes, Rest"),
    ]

    def __init__(self, character: Character, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.awaiting_confirmation = False

    def compose(self) -> ComposeResult:
        c = self.character
        hp = c.combat.hit_points
        pool = c.combat.hit_dice_pool
        hd = c.combat.hit_dice

        # Calculate hit dice info
        if pool and pool.pools:
            hd_total = pool.total
            hd_display = c.combat.get_hit_dice_display()
        else:
            hd_total = hd.total
            hd_display = f"{hd.remaining}/{hd.total}{hd.die}"

        yield Header()
        yield Container(
            Static("Long Rest", classes="title"),
            Static(f"{c.name} - Level {c.total_level} {c.primary_class.name}", classes="subtitle"),
            Vertical(
                Static("LONG REST RECOVERY", classes="panel-title"),
                Static(""),
                Static("  The following will be restored:", classes="section-header"),
                Static(""),
                Static(f"  ♥ HP: {hp.current} → {hp.maximum} (full)", id="hp-restore"),
                Static(f"  ⬡ Hit Dice: +{max(1, hd_total // 2)} (current: {hd_display})", id="hd-restore"),
                Static(id="spell-restore"),
                Static(id="feature-restore"),
                Static(""),
                Static("  Temporary HP will be cleared", classes="note"),
                Static("  Death saves will be reset", classes="note"),
                Static(""),
                Static("", id="confirm-prompt"),
                classes="panel rest-panel",
            ),
            id="long-rest-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Calculate and display restoration summary."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the display with restoration info."""
        c = self.character

        # Spell slots restoration
        spell_widget = self.query_one("#spell-restore", Static)
        if c.spellcasting.ability:
            spell_widget.update("  ✦ All spell slots restored")
        else:
            spell_widget.update("  ✦ (No spellcasting)")

        # Features restoration
        feature_widget = self.query_one("#feature-restore", Static)
        long_rest_features = [
            f.name for f in c.features
            if f.uses and f.recharge in ("long rest", "long_rest", "daily")
            and f.used > 0
        ]
        if long_rest_features:
            if len(long_rest_features) <= 3:
                feature_widget.update(f"  ★ Features: {', '.join(long_rest_features)}")
            else:
                feature_widget.update(f"  ★ {len(long_rest_features)} features with uses restored")
        else:
            feature_widget.update("  ★ All feature uses restored")

        # Update confirm prompt
        confirm_widget = self.query_one("#confirm-prompt", Static)
        if self.awaiting_confirmation:
            confirm_widget.update("  ➤ Take long rest? Press [Y] to confirm, [Esc] to cancel")
        else:
            confirm_widget.update("  Press [Enter] to take long rest  [Esc] to cancel")

    def action_confirm(self) -> None:
        """Show confirmation prompt."""
        self.awaiting_confirmation = True
        self._update_display()

    def action_confirm_yes(self) -> None:
        """Actually execute the long rest after confirmation."""
        if not self.awaiting_confirmation:
            return

        c = self.character
        pool = c.combat.hit_dice_pool
        hd = c.combat.hit_dice

        # Store old values for summary (check pool for multiclass)
        old_hp = c.combat.hit_points.current
        old_hd = pool.remaining if (pool and pool.pools) else hd.remaining

        # Apply long rest
        c.long_rest()

        # Save
        self.app.save_character()

        # Calculate actual restoration (check pool for multiclass)
        pool = c.combat.hit_dice_pool  # Refresh reference after long_rest
        hd = c.combat.hit_dice
        new_hd = pool.remaining if (pool and pool.pools) else hd.remaining
        hp_healed = c.combat.hit_points.current - old_hp
        hd_restored = new_hd - old_hd

        self.notify(f"Long rest complete! HP +{hp_healed}, Hit Dice +{hd_restored}", severity="information")
        self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel the long rest."""
        if self.awaiting_confirmation:
            self.awaiting_confirmation = False
            self._update_display()
        else:
            self.app.pop_screen()


class SettingsScreen(Screen):
    """Screen for configuring app settings and rule enforcement."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("r", "reset", "Reset to Defaults"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = Config.load()
        self.selected_index = 0
        self.settings_list: list[tuple[str, str, bool]] = []  # (key, description, value)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Settings & Rule Enforcement", classes="title"),
            Static("↑/↓ Navigate  [Enter/Space] Toggle  [R] Reset  [Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("ENFORCEMENT OPTIONS", classes="panel-title"),
                    VerticalScroll(id="settings-list", classes="settings-list"),
                    classes="panel settings-panel",
                ),
                Vertical(
                    Static("DESCRIPTION", classes="panel-title"),
                    VerticalScroll(id="setting-details", classes="setting-details"),
                    classes="panel details-panel",
                ),
                classes="settings-row",
            ),
            id="settings-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load settings."""
        self._build_settings_list()
        self._refresh_settings()

    def _build_settings_list(self) -> None:
        """Build the list of toggleable settings."""
        e = self.config.enforcement
        self.settings_list = [
            # Ability Scores
            ("enforce_ability_limits", "Enforce 1-30 ability score range", e.enforce_ability_limits),
            ("enforce_ability_cap_20", "Enforce 20 as max ability (before items)", e.enforce_ability_cap_20),
            # Equipment
            ("enforce_item_rarity", "Warn on items above character tier", e.enforce_item_rarity),
            ("enforce_attunement_limit", "Enforce attunement limit", e.enforce_attunement_limit),
            ("enforce_armor_proficiency", "Warn on armor without proficiency", e.enforce_armor_proficiency),
            ("enforce_weapon_proficiency", "Warn on weapons without proficiency", e.enforce_weapon_proficiency),
            ("enforce_encumbrance", "Track carrying capacity", e.enforce_encumbrance),
            # Leveling
            ("enforce_level_limits", "Enforce 1-20 level range", e.enforce_level_limits),
            ("enforce_multiclass_requirements", "Enforce multiclass ability requirements", e.enforce_multiclass_requirements),
            # Spellcasting
            ("enforce_spell_slots", "Track spell slot usage", e.enforce_spell_slots),
            ("enforce_spell_preparation", "Enforce prepared spell limits", e.enforce_spell_preparation),
            ("enforce_spell_components", "Track material components", e.enforce_spell_components),
            ("enforce_concentration", "Warn about concentration conflicts", e.enforce_concentration),
            # Combat
            ("enforce_action_economy", "Track actions per turn", e.enforce_action_economy),
            # General
            ("strict_mode", "Strict mode (prevent invalid saves)", e.strict_mode),
        ]

    def _refresh_settings(self) -> None:
        """Refresh the settings display."""
        list_widget = self.query_one("#settings-list", VerticalScroll)
        list_widget.remove_children()

        for i, (key, desc, value) in enumerate(self.settings_list):
            setting_class = "setting-row"
            if i == self.selected_index:
                setting_class += " selected"

            check = "✓" if value else "○"
            selector = "▶ " if i == self.selected_index else "  "

            list_widget.mount(Static(
                f"{selector}[{check}] {desc}",
                classes=setting_class,
            ))

        self._refresh_details()

    def _refresh_details(self) -> None:
        """Show details of the selected setting."""
        details_widget = self.query_one("#setting-details", VerticalScroll)
        details_widget.remove_children()

        if self.selected_index < len(self.settings_list):
            key, desc, value = self.settings_list[self.selected_index]

            details_widget.mount(Static(f"  {desc}", classes="setting-name"))
            details_widget.mount(Static(""))
            details_widget.mount(Static(f"  Key: enforcement.{key}", classes="setting-key"))
            details_widget.mount(Static(f"  Current: {'Enabled' if value else 'Disabled'}", classes="setting-value"))
            details_widget.mount(Static(""))

            # Add explanatory text
            explanations = {
                "enforce_ability_limits": "Prevents ability scores from going below 1 or above 30.",
                "enforce_ability_cap_20": "Prevents base ability scores from exceeding 20 (magic items can still increase).",
                "enforce_item_rarity": "Shows warnings when adding magic items above the recommended tier for character level.",
                "enforce_attunement_limit": "Prevents attuning to more than 3 magic items (default D&D limit).",
                "enforce_armor_proficiency": "Shows warnings when equipping armor without proficiency.",
                "enforce_weapon_proficiency": "Shows warnings when using weapons without proficiency.",
                "enforce_encumbrance": "Tracks weight carried and warns when exceeding carrying capacity.",
                "enforce_level_limits": "Prevents character level from going below 1 or above 20.",
                "enforce_multiclass_requirements": "Checks ability score requirements when multiclassing.",
                "enforce_spell_slots": "Tracks spell slot usage and prevents casting without slots.",
                "enforce_spell_preparation": "Limits prepared spells based on class rules.",
                "enforce_spell_components": "Tracks material components and spell focus requirements.",
                "enforce_concentration": "Warns when casting a concentration spell while concentrating.",
                "enforce_action_economy": "Tracks actions, bonus actions, and reactions per turn.",
                "strict_mode": "Prevents saving characters that violate any enabled enforcement rules.",
            }

            if key in explanations:
                details_widget.mount(Static(f"  {explanations[key]}", classes="setting-explain"))

    def key_up(self) -> None:
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1
            self._refresh_settings()

    def key_down(self) -> None:
        """Move selection down."""
        if self.selected_index < len(self.settings_list) - 1:
            self.selected_index += 1
            self._refresh_settings()

    def key_enter(self) -> None:
        """Toggle the selected setting."""
        self._toggle_current()

    def key_space(self) -> None:
        """Toggle the selected setting."""
        self._toggle_current()

    def _toggle_current(self) -> None:
        """Toggle the currently selected setting."""
        if self.selected_index < len(self.settings_list):
            key, desc, value = self.settings_list[self.selected_index]
            new_value = not value

            # Update config
            setattr(self.config.enforcement, key, new_value)
            self.config.save()

            # Update local list
            self.settings_list[self.selected_index] = (key, desc, new_value)

            status = "enabled" if new_value else "disabled"
            self.notify(f"{desc}: {status}")
            self._refresh_settings()

    def action_reset(self) -> None:
        """Reset all enforcement settings to defaults."""
        from dnd_manager.config import EnforcementConfig
        self.config.enforcement = EnforcementConfig()
        self.config.save()
        self._build_settings_list()
        self._refresh_settings()
        self.notify("Settings reset to defaults")

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


def _get_app_version() -> str:
    """Get the application version from package metadata or config."""
    try:
        from importlib.metadata import version
        return version("dnd-manager")
    except Exception:
        # Fallback to config version
        return get_config_manager().config.versions.app_version


class DNDManagerApp(App):
    """CCVault - CLI Character Vault application."""

    TITLE = f"CCVault v{_get_app_version()}"
    SUB_TITLE = "CLI Character Vault for D&D 5e"
    CSS_PATH = "ui/styles/app.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
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

    def action_open_character(self) -> None:
        """Open character selection screen."""
        char_info = self.store.get_character_info()
        if not char_info:
            self.notify("No characters found. Create one first!", severity="warning")
            return

        self.push_screen(CharacterSelectScreen(char_info))

    def load_character(self, path: Path) -> None:
        """Load a character from a path and switch to dashboard."""
        char = self.store.load_path(path)
        if char:
            self.current_character = char
            # Remove all screens and push dashboard
            while len(self.screen_stack) > 1:
                self.pop_screen()
            self.pop_screen()
            self.push_screen(MainDashboard(char))
        else:
            self.notify("Failed to load character", severity="error")

    def save_character(self) -> None:
        """Save the current character."""
        if self.current_character:
            self.store.save(self.current_character)


def run_app(character_path: Optional[Path] = None) -> None:
    """Run the D&D Character Manager application."""
    app = DNDManagerApp(character_path=character_path)
    app.run()
