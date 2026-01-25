"""Character creation screen for the D&D Manager application."""

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, OptionList, Static
from textual.widgets.option_list import Option
from rich.text import Text

from dnd_manager.config import get_config_manager
from dnd_manager.data import (
    get_all_background_names,
    get_all_species_names,
    get_background,
    get_class_info,
    get_feat,
    get_general_feats,
    get_origin_feats,
    get_species,
    get_subraces,
    skill_name_to_enum,
    species_grants_feat,
)
from dnd_manager.data.backgrounds import get_origin_feat_for_background
from dnd_manager.models.character import Alignment, Character, Feature, RulesetId
from dnd_manager.storage import CharacterStore
from dnd_manager.ui.screens.base import (
    ABILITIES,
    ABILITY_ABBREV,
    ListNavigationMixin,
    POINT_BUY_COSTS,
    POINT_BUY_MAX,
    POINT_BUY_MIN,
    POINT_BUY_TOTAL,
    RULESET_LABELS,
    ScreenContextMixin,
    STANDARD_ARRAY,
)
from dnd_manager.ui.screens.widgets import CreationOptionList

if TYPE_CHECKING:
    pass


class CharacterCreationScreen(ScreenContextMixin, ListNavigationMixin, Screen):
    """Wizard for creating a new character."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "next", "Next/Confirm"),
        Binding("left", "prev_option", "Previous"),
        Binding("right", "next_option", "Next"),
        Binding("?", "ai_help", "AI Help"),
    ]

    def __init__(self, draft_data: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        # Letter jump tracking
        self._last_letter: str = ""
        self._last_letter_index: int = -1
        self._last_key: str = ""
        # Dynamic steps - subspecies, species_feat, and origin_feat may be skipped
        self.all_steps = [
            "ruleset",
            "name",
            "class",
            "species",
            "subspecies",
            "species_feat",
            "background",
            "alignment",
            "origin_feat",
            "abilities",
            "skills",
            "spells",
            "confirm",
        ]

        # Get defaults from config
        config = get_config_manager().config
        defaults = config.character_defaults

        # Ability step state (initialize before draft restore)
        self.ability_sub_step = "method_select"  # method_select | generate | assign | bonuses
        self.ability_method = "standard_array"   # standard_array | point_buy | roll
        self.base_scores = list(STANDARD_ARRAY)  # Generated/configured scores
        self.roll_results: list[dict] = []       # For roll method: [{rolls, total}, ...]
        self.point_buy_scores = {a: 8 for a in ABILITIES}  # For point buy
        self.score_assignments: dict[str, int | None] = {a: None for a in ABILITIES}  # ability -> score index
        self.bonus_plus_2: str | None = None     # For 2024: ability name for +2
        self.bonus_plus_1: str | None = None     # For 2024: ability name for +1
        self.bonus_mode: str = "split"           # For 2024: "split" (+2/+1) or "spread" (+1/+1/+1)
        self.ability_selected_index = 0          # Current selection in ability lists

        # Load from draft or use config defaults
        if draft_data:
            self.step = draft_data.get("_step", 0)
            self.char_data = {
                "name": draft_data.get("name", defaults.name),
                "class": draft_data.get("class", defaults.class_name),
                "species": draft_data.get("species", defaults.species),
                "subspecies": draft_data.get("subspecies"),
                "species_feat": draft_data.get("species_feat"),
                "background": draft_data.get("background", defaults.background),
                "alignment": draft_data.get("alignment", Alignment.TRUE_NEUTRAL.value),
                "origin_feat": draft_data.get("origin_feat"),
                "ruleset": draft_data.get("ruleset", defaults.ruleset),
                "skills": draft_data.get("skills", []),
                "cantrips": draft_data.get("cantrips", []),
                "spells": draft_data.get("spells", []),
                "ability_state": draft_data.get("ability_state"),
            }
            # Restore skill/spell state
            self.selected_skills = self.char_data.get("skills", [])
            self.selected_cantrips = self.char_data.get("cantrips", [])
            self.selected_spells = self.char_data.get("spells", [])
            # Restore ability state if present
            ability_state = self.char_data.get("ability_state") or {}
            if ability_state:
                self.base_scores = list(ability_state.get("base_scores", self.base_scores))
                self.score_assignments = dict(ability_state.get("score_assignments", self.score_assignments))
                self.ability_method = ability_state.get("ability_method", self.ability_method)
                self.bonus_mode = ability_state.get("bonus_mode", self.bonus_mode)
                self.bonus_plus_2 = ability_state.get("bonus_plus_2", self.bonus_plus_2)
                self.bonus_plus_1 = ability_state.get("bonus_plus_1", self.bonus_plus_1)
        else:
            self.step = 0
            self.char_data = {
                "name": defaults.name,
                "class": defaults.class_name,
                "species": defaults.species,
                "subspecies": None,
                "species_feat": None,
                "background": defaults.background,
                "alignment": Alignment.TRUE_NEUTRAL.value,
                "origin_feat": None,
                "ruleset": defaults.ruleset,
                "skills": [],
                "cantrips": [],
                "spells": [],
                "ability_state": None,
            }

        self.current_options: list[str] = []
        self.selected_option = 0
        self._draft_store = None
        self._expected_highlight = 0  # Track expected highlight to ignore spurious events

        # Skill selection state
        self.selected_skills: list[str] = []     # Skills chosen by user
        self.skill_selected_index = 0            # Current selection in skill list

        # Spell selection state (for casters)
        self.selected_cantrips: list[str] = []   # Cantrips chosen
        self.selected_spells: list[str] = []     # 1st level spells chosen
        self.spell_selected_index = 0            # Current selection in spell list
        self.spell_selection_phase = "cantrips"  # "cantrips" or "spells"

    @property
    def draft_store(self):
        """Lazy-load draft store."""
        if self._draft_store is None:
            from dnd_manager.storage.yaml_store import get_default_draft_store
            self._draft_store = get_default_draft_store()
        return self._draft_store

    def _save_draft(self) -> None:
        """Auto-save current progress as draft."""
        self._persist_ability_state()
        draft_data = {**self.char_data, "_step": self.step}
        self.draft_store.save_draft(draft_data)

    @property
    def steps(self) -> list[str]:
        """Return active steps, skipping inapplicable ones."""
        active = []
        for step in self.all_steps:
            if step == "subspecies":
                # Skip if selected species has no subspecies
                subspecies_list = get_subraces(self.char_data.get("species", ""))
                if not subspecies_list:
                    continue
            elif step == "species_feat":
                # Skip if species/subspecies doesn't grant a feat choice
                species_name = self.char_data.get("species", "")
                subspecies_name = self.char_data.get("subspecies")
                if not species_grants_feat(species_name, subspecies_name):
                    continue
            elif step == "origin_feat":
                # Skip for 2014 rules (no origin feats)
                if self.char_data.get("ruleset") == "dnd2014":
                    continue
            elif step == "spells":
                # Skip for non-casters
                class_name = self.char_data.get("class", "")
                class_info = get_class_info(class_name)
                if not class_info or not class_info.spellcasting_ability:
                    continue
            active.append(step)
        return active

    def get_ai_context(self) -> dict:
        """Provide character creation context for AI."""
        step_names = {
            "ruleset": "Selecting ruleset",
            "name": "Choosing name",
            "class": "Selecting class",
            "species": "Selecting species/race",
            "subspecies": "Selecting subspecies",
            "species_feat": "Selecting species feat",
            "background": "Selecting background",
            "alignment": "Selecting alignment",
            "origin_feat": "Selecting origin feat",
            "abilities": "Assigning ability scores",
            "skills": "Selecting skill proficiencies",
            "spells": "Selecting spells",
            "confirm": "Reviewing and confirming",
        }
        # Safely get current step
        current_step = "unknown"
        if hasattr(self, 'char_data') and hasattr(self, 'step'):
            steps = self.steps
            if self.step < len(steps):
                current_step = steps[self.step]

        # Safely get char_data
        char_data = getattr(self, 'char_data', {})

        return {
            "screen_type": "Character Creation Wizard",
            "description": f"Creating a character - {step_names.get(current_step, current_step)}",
            "data": {
                "current_step": current_step,
                "choices_so_far": {
                    "ruleset": char_data.get("ruleset"),
                    "name": char_data.get("name"),
                    "class": char_data.get("class"),
                    "species": char_data.get("species"),
                    "subspecies": char_data.get("subspecies"),
            "background": char_data.get("background"),
            "alignment": char_data.get("alignment"),
                    "selected_skills": getattr(self, "selected_skills", []),
                },
            },
        }

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create New Character", classes="title"),
            Static(id="step-indicator", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static(id="step-title", classes="panel-title"),
                    Input(placeholder="Enter name...", id="name-input"),
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
        # Set default focus to the options list
        try:
            self.query_one("#options-list", OptionList).focus()
        except NoMatches:
            pass

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
            "subspecies": "Subspecies",
            "species_feat": "Bonus Feat",
            "background": "Background",
            "alignment": "Alignment",
            "origin_feat": "Origin Feat",
            "abilities": "Abilities",
            "skills": "Skills",
            "spells": "Spells",
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
        options_list = self.query_one("#options-list", OptionList)
        description = self.query_one("#step-description", Static)

        # Hide/show elements based on step
        name_input.display = step_name == "name"
        options_list.display = step_name != "name"

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
                self.current_options = [sr.name for sr in species.subspecies]
            else:
                self.current_options = []
            self._refresh_options()

        elif step_name == "species_feat":
            title.update("BONUS FEAT")
            species_name = self.char_data.get("species", "")
            subspecies_name = self.char_data.get("subspecies")
            source = subspecies_name if subspecies_name else species_name
            description.update(f"Your {source} grants you a feat of your choice:")
            # Get general feats (no prerequisites for level 1 character)
            general_feats = get_general_feats()
            self.current_options = sorted([f.name for f in general_feats if not f.prerequisites])
            self._refresh_options()

        elif step_name == "background":
            title.update("CHOOSE BACKGROUND")
            description.update("Select your character's background - this shapes their history and skills")
            # Use dynamic background list from data module
            self.current_options = get_all_background_names()
            self._refresh_options()

        elif step_name == "alignment":
            title.update("CHOOSE ALIGNMENT")
            description.update("Select your character's alignment")
            self.current_options = [a.display_name for a in Alignment]
            current_alignment = self.char_data.get("alignment")
            if current_alignment:
                try:
                    current_display = Alignment(current_alignment).display_name
                    if current_display in self.current_options:
                        self.selected_option = self.current_options.index(current_display)
                except ValueError:
                    pass  # Invalid alignment value stored
            self._refresh_options()

        elif step_name == "origin_feat":
            title.update("ORIGIN FEAT")
            # Get the specific origin feat for the selected background
            background_name = self.char_data.get("background", "")
            origin_feat = get_origin_feat_for_background(background_name)
            if origin_feat:
                description.update(f"Your background ({background_name}) grants this feat:")
                self.current_options = [origin_feat.name]
            else:
                description.update("No origin feat for this background")
                self.current_options = []
            self._refresh_options()

        elif step_name == "abilities":
            self._show_ability_substep()

        elif step_name == "skills":
            self._show_skills()

        elif step_name == "spells":
            self._show_spells()

        elif step_name == "confirm":
            title.update("CONFIRM CHARACTER")
            description.update("Select a section to review. Press Create Character to finish.")
            self.current_options = self._build_confirm_sections()
            self.selected_option = min(self.selected_option, max(0, len(self.current_options) - 1))
            self._refresh_options()
            options_list.display = True

    def _refresh_options(self) -> None:
        """Rebuild the options list. Only call on step transitions, not navigation."""
        try:
            options_list = self.query_one("#options-list", OptionList)
        except NoMatches:
            # Screen not mounted yet
            return

        # Clear and rebuild options
        options_list.clear_options()
        for i, option in enumerate(self.current_options):
            options_list.add_option(Option(option, id=f"opt_{i}"))

        # Set highlighted option and track expected value
        if self.current_options and self.selected_option < len(self.current_options):
            self._expected_highlight = self.selected_option
            options_list.highlighted = self.selected_option
        else:
            self._expected_highlight = 0

        self._refresh_details()

    def _refresh_details(self) -> None:
        """Update the detail panel with information about the selected option."""
        try:
            detail_title = self.query_one("#detail-title", Static)
            detail_content = self.query_one("#detail-content", Static)
            detail_panel = self.query_one("#detail-panel", VerticalScroll)
        except NoMatches:
            return

        step_name = self.steps[self.step] if self.step < len(self.steps) else ""

        # Hide detail panel on steps without options
        if step_name in ("name", "abilities"):
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
        elif step_name == "species_feat":
            self._show_feat_details(selected_name, detail_title, detail_content)
        elif step_name == "background":
            self._show_background_details(selected_name, detail_title, detail_content)
        elif step_name == "origin_feat":
            self._show_feat_details(selected_name, detail_title, detail_content)
        elif step_name == "alignment":
            detail_title.update(selected_name)
            detail_content.update("Alignment reflects your character's moral and ethical outlook.")
        elif step_name == "skills":
            ruleset = self.char_data.get("ruleset")
            skill_name = self.current_options[self.selected_option]
            description = get_skill_description(skill_name, ruleset)
            skill_enum = skill_name_to_enum(skill_name)
            if skill_enum:
                from dnd_manager.models.abilities import SKILL_ABILITY_MAP

                ability = SKILL_ABILITY_MAP[skill_enum].abbreviation
                detail_title.update(f"{skill_name} ({ability})")
            else:
                detail_title.update(skill_name)
            detail_content.update(description or "No description available.")
        elif step_name == "confirm":
            section = self.current_options[self.selected_option]
            detail_title.update(section)
            detail_content.update(self._build_confirm_detail(section))
        else:
            detail_title.update(selected_name)
            detail_content.update("")

    def _build_confirm_sections(self) -> list[str]:
        """Build the left-pane section list for the confirm step."""
        sections = [
            "Overall Summary",
            "Ruleset",
            "Name",
            "Class",
            "Species",
            "Background",
            "Alignment",
            "Abilities",
            "Skills",
        ]
        class_info = get_class_info(self.char_data.get("class", ""))
        if class_info and class_info.spellcasting_ability:
            sections.append("Spells")
        sections.extend(["Proficiencies", "Equipment"])
        return sections

    def _get_ruleset_label(self) -> str:
        """Return a display label for the selected ruleset."""
        ruleset = self.char_data.get("ruleset", "dnd2024")
        return RULESET_LABELS.get(ruleset, ruleset)

    def _get_ability_bonuses(self, ability_state: Optional[dict] = None) -> dict[str, int]:
        """Calculate ability bonuses based on ruleset and selections."""
        ruleset = self.char_data.get("ruleset", "dnd2024")
        state = ability_state or self._get_active_ability_state()
        bonuses: dict[str, int] = {}
        if ruleset == "dnd2014":
            bonuses = self._get_racial_bonuses()
        elif ruleset == "dnd2024":
            bonus_mode = state.get("bonus_mode", self.bonus_mode)
            bonus_plus_2 = state.get("bonus_plus_2", self.bonus_plus_2)
            bonus_plus_1 = state.get("bonus_plus_1", self.bonus_plus_1)
            if bonus_mode == "spread":
                for opt in self._get_background_bonus_options():
                    bonuses[opt.lower()] = 1
            else:
                if bonus_plus_2:
                    bonuses[bonus_plus_2.lower()] = 2
                if bonus_plus_1:
                    bonuses[bonus_plus_1.lower()] = 1
        return bonuses

    def _get_ability_summary_line(self) -> str:
        """Return a compact ability summary string."""
        ability_state = self._get_active_ability_state()
        bonuses = self._get_ability_bonuses(ability_state)
        scores_parts = []
        for ability in ABILITIES:
            idx = ability_state["score_assignments"].get(ability)
            if idx is not None and idx < len(ability_state["base_scores"]):
                base = ability_state["base_scores"][idx]
                bonus = bonuses.get(ability, 0)
                total = base + bonus
                abbrev = ABILITY_ABBREV[ability]
                if bonus > 0:
                    scores_parts.append(f"{abbrev}:{total}(+{bonus})")
                else:
                    scores_parts.append(f"{abbrev}:{total}")
        return f"Abilities: {' '.join(scores_parts)}" if scores_parts else "Abilities: -"

    def _get_hp_summary_line(self) -> Optional[str]:
        """Return an HP preview line if possible."""
        class_info = get_class_info(self.char_data.get("class", ""))
        if not class_info:
            return None
        hit_die_size = int(class_info.hit_die[1:])
        ability_state = self._get_active_ability_state()
        con_idx = ability_state["score_assignments"].get("constitution")
        if con_idx is None or con_idx >= len(ability_state["base_scores"]):
            return None
        bonuses = self._get_ability_bonuses(ability_state)
        base_con = ability_state["base_scores"][con_idx]
        con_bonus = bonuses.get("constitution", 0)
        total_con = base_con + con_bonus
        con_mod = (total_con - 10) // 2
        max_hp = max(1, hit_die_size + con_mod)
        return f"HP: {max_hp} ({class_info.hit_die} + {con_mod} CON)"

    def _persist_ability_state(self) -> None:
        """Persist ability assignment state into char_data for later review."""
        self.char_data["ability_state"] = {
            "base_scores": list(self.base_scores),
            "score_assignments": dict(self.score_assignments),
            "ability_method": self.ability_method,
            "bonus_mode": self.bonus_mode,
            "bonus_plus_2": self.bonus_plus_2,
            "bonus_plus_1": self.bonus_plus_1,
        }

    def _get_active_ability_state(self) -> dict:
        """Return ability state, preferring current in-memory data, with saved fallback."""
        has_assignments = any(v is not None for v in self.score_assignments.values())
        if has_assignments and len(self.base_scores) == len(ABILITIES):
            return {
                "base_scores": list(self.base_scores),
                "score_assignments": dict(self.score_assignments),
                "ability_method": self.ability_method,
                "bonus_mode": self.bonus_mode,
                "bonus_plus_2": self.bonus_plus_2,
                "bonus_plus_1": self.bonus_plus_1,
            }
        saved = self.char_data.get("ability_state")
        if saved:
            return {
                "base_scores": list(saved.get("base_scores", self.base_scores)),
                "score_assignments": dict(saved.get("score_assignments", self.score_assignments)),
                "ability_method": saved.get("ability_method", self.ability_method),
                "bonus_mode": saved.get("bonus_mode", self.bonus_mode),
                "bonus_plus_2": saved.get("bonus_plus_2", self.bonus_plus_2),
                "bonus_plus_1": saved.get("bonus_plus_1", self.bonus_plus_1),
            }
        return {
            "base_scores": list(self.base_scores),
            "score_assignments": dict(self.score_assignments),
            "ability_method": self.ability_method,
            "bonus_mode": self.bonus_mode,
            "bonus_plus_2": self.bonus_plus_2,
            "bonus_plus_1": self.bonus_plus_1,
        }

    def _build_confirm_detail(self, section: str) -> str:
        """Build the right-pane content for confirm sections."""
        lines: list[str] = []
        class_name = self.char_data.get("class", "")
        class_info = get_class_info(class_name)

        if section == "Overall Summary":
            lines.append(f"Ruleset: {self._get_ruleset_label()}")
            lines.append(f"Name: {self.char_data.get('name', '')}")
            lines.append(f"Class: {self.char_data.get('class', '')}")
            species_display = self.char_data.get("species", "")
            if self.char_data.get("subspecies"):
                species_display += f" ({self.char_data.get('subspecies')})"
            lines.append(f"Species: {species_display}")
            if self.char_data.get("species_feat"):
                lines.append(f"Bonus Feat: {self.char_data.get('species_feat')}")
            lines.append(f"Background: {self.char_data.get('background', '')}")
            alignment_value = self.char_data.get("alignment")
            if alignment_value:
                try:
                    lines.append(f"Alignment: {Alignment(alignment_value).display_name}")
                except ValueError:
                    lines.append(f"Alignment: {alignment_value}")
            if self.char_data.get("origin_feat"):
                lines.append(f"Origin Feat: {self.char_data.get('origin_feat')}")
            lines.append(self._get_ability_summary_line())
            hp_line = self._get_hp_summary_line()
            if hp_line:
                lines.append(hp_line)
            lines.append(f"Skills: {', '.join(self.selected_skills) if self.selected_skills else 'None'}")
            if class_info and class_info.spellcasting_ability:
                lines.append(f"Cantrips: {', '.join(self.selected_cantrips) if self.selected_cantrips else 'None'}")
                lines.append(f"Spells: {', '.join(self.selected_spells) if self.selected_spells else 'None'}")
            if class_info:
                lines.append(f"Saving Throws: {', '.join(class_info.saving_throws)}")
                if class_info.armor_proficiencies:
                    lines.append(f"Armor: {', '.join(class_info.armor_proficiencies)}")
                if class_info.weapon_proficiencies:
                    lines.append(f"Weapons: {', '.join(class_info.weapon_proficiencies)}")
                equipment = self._get_starting_equipment(class_name)
                lines.append(f"Equipment: {', '.join(equipment) if equipment else 'None'}")
                lines.append("Starting Gold: 10 gp")
            return "\n".join(lines)

        if section == "Ruleset":
            lines.append(self._get_ruleset_label())
        elif section == "Name":
            lines.append(self.char_data.get("name", ""))
        elif section == "Class":
            lines.append(self.char_data.get("class", ""))
        elif section == "Species":
            species_display = self.char_data.get("species", "")
            if self.char_data.get("subspecies"):
                species_display += f" ({self.char_data.get('subspecies')})"
            lines.append(species_display)
            if self.char_data.get("species_feat"):
                lines.append(f"Bonus Feat: {self.char_data.get('species_feat')}")
        elif section == "Background":
            lines.append(self.char_data.get("background", ""))
            if self.char_data.get("origin_feat"):
                lines.append(f"Origin Feat: {self.char_data.get('origin_feat')}")
        elif section == "Alignment":
            alignment_value = self.char_data.get("alignment")
            if alignment_value:
                try:
                    lines.append(Alignment(alignment_value).display_name)
                except ValueError:
                    lines.append(alignment_value)
            else:
                lines.append("Not set")
        elif section == "Abilities":
            lines.append(self._get_ability_summary_line())
            hp_line = self._get_hp_summary_line()
            if hp_line:
                lines.append(hp_line)
        elif section == "Skills":
            lines.append(", ".join(self.selected_skills) if self.selected_skills else "None selected.")
        elif section == "Spells":
            lines.append(f"Cantrips: {', '.join(self.selected_cantrips) if self.selected_cantrips else 'None'}")
            lines.append(f"Spells: {', '.join(self.selected_spells) if self.selected_spells else 'None'}")
        elif section == "Proficiencies":
            if class_info:
                lines.append(f"Saving Throws: {', '.join(class_info.saving_throws)}")
                if class_info.armor_proficiencies:
                    lines.append(f"Armor: {', '.join(class_info.armor_proficiencies)}")
                if class_info.weapon_proficiencies:
                    lines.append(f"Weapons: {', '.join(class_info.weapon_proficiencies)}")
            else:
                lines.append("No class proficiencies available.")
        elif section == "Equipment":
            equipment = self._get_starting_equipment(class_name)
            lines.append(", ".join(equipment) if equipment else "None")
            lines.append("Starting Gold: 10 gp")

        return "\n".join(lines)

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
        ruleset = self.char_data.get("ruleset", "dnd2024")
        lines.append(f"Speed: {species.get_speed(ruleset)} ft.")
        if species.darkvision:
            lines.append(f"Darkvision: {species.darkvision} ft.")
        lines.append(f"Languages: {', '.join(species.languages)}")

        # Only show ability bonuses for 2014 ruleset (2024 uses background bonuses)
        if ruleset == "dnd2014" and species.ability_bonuses:
            bonuses = [f"+{v} {k}" for k, v in species.ability_bonuses.items()]
            lines.append(f"Ability Bonuses: {', '.join(bonuses)}")

        if species.traits:
            lines.append("")
            lines.append("RACIAL TRAITS")
            for trait in species.traits:
                lines.append(f"  • {trait.name}")
                lines.append(f"    {trait.description}")

        if species.subspecies:
            lines.append("")
            lines.append(f"Subspecies: {', '.join(sr.name for sr in species.subspecies)}")

        content.update("\n".join(lines))

    def _show_subspecies_details(self, subspecies_name: str, title: Static, content: Static) -> None:
        """Show details for a subspecies."""
        species_name = self.char_data.get("species", "")
        species = get_species(species_name)
        if not species:
            title.update(subspecies_name)
            content.update("No details available")
            return

        subsp = next((sr for sr in species.subspecies if sr.name == subspecies_name), None)
        if not subsp:
            title.update(subspecies_name)
            content.update("No details available")
            return

        title.update(f"🧬 {subspecies_name}")

        lines = []
        lines.append(subsp.description)

        # Only show ability bonuses for 2014 ruleset (2024 uses background bonuses)
        ruleset = self.char_data.get("ruleset", "dnd2024")
        if ruleset == "dnd2014" and subsp.ability_bonuses:
            lines.append("")
            bonuses = [f"+{v} {k}" for k, v in subsp.ability_bonuses.items()]
            lines.append(f"Ability Bonuses: {', '.join(bonuses)}")

        if subsp.traits:
            lines.append("")
            lines.append("SUBSPECIES TRAITS")
            for trait in subsp.traits:
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

    # =========================================================================
    # ABILITY SCORE SUB-STEP METHODS
    # =========================================================================

    def _show_ability_substep(self) -> None:
        """Display the current ability configuration sub-step."""
        if self.ability_sub_step == "method_select":
            self._show_ability_method_select()
        elif self.ability_sub_step == "generate":
            self._show_ability_generate()
        elif self.ability_sub_step == "assign":
            self._show_ability_assign()
        elif self.ability_sub_step == "bonuses":
            self._show_ability_bonuses()

    def _show_ability_method_select(self) -> None:
        """Display method selection for ability score generation."""
        title = self.query_one("#step-title", Static)
        options_list = self.query_one("#options-list", OptionList)
        description = self.query_one("#step-description", Static)
        detail_panel = self.query_one("#detail-panel", VerticalScroll)

        title.update("ABILITY SCORES - Choose Method")
        description.update("Select how to generate your ability scores")
        detail_panel.display = False

        self.current_options = [
            "Standard Array (15, 14, 13, 12, 10, 8)",
            "Point Buy (27 points)",
            "Roll (4d6 drop lowest)",
        ]
        # Map current method to index
        method_to_index = {"standard_array": 0, "point_buy": 1, "roll": 2}
        self.selected_option = method_to_index.get(self.ability_method, 0)
        self._refresh_options()
        options_list.display = True

    def _show_ability_generate(self) -> None:
        """Display score generation based on selected method."""
        if self.ability_method == "standard_array":
            self._show_generate_standard_array()
        elif self.ability_method == "point_buy":
            self._show_generate_point_buy()
        elif self.ability_method == "roll":
            self._show_generate_roll()

    def _show_generate_standard_array(self) -> None:
        """Display Standard Array scores."""
        title = self.query_one("#step-title", Static)
        options_list = self.query_one("#options-list", OptionList)
        description = self.query_one("#step-description", Static)
        detail_panel = self.query_one("#detail-panel", VerticalScroll)

        title.update("ABILITY SCORES - Standard Array")
        self.base_scores = list(STANDARD_ARRAY)

        # Show the scores
        scores_display = "  ".join(str(s) for s in self.base_scores)
        description.update(f"Your scores to assign:\n\n  {scores_display}\n\nPress Next to assign scores to abilities.")

        options_list.display = False
        detail_panel.display = False

    def _show_generate_point_buy(self) -> None:
        """Display Point Buy interface."""
        title = self.query_one("#step-title", Static)
        options_list = self.query_one("#options-list", OptionList)
        description = self.query_one("#step-description", Static)
        detail_panel = self.query_one("#detail-panel", VerticalScroll)

        remaining = self._calculate_point_buy_remaining()
        title.update(f"ABILITY SCORES - Point Buy ({remaining}/{POINT_BUY_TOTAL} points)")

        # Build display of current scores
        lines = ["←→ adjust (8-15), \\[X] reset all to 8", ""]
        for i, ability in enumerate(ABILITIES):
            score = self.point_buy_scores[ability]
            cost = POINT_BUY_COSTS.get(score, 0)
            abbrev = ABILITY_ABBREV[ability]
            marker = "▶" if i == self.ability_selected_index else " "
            lines.append(f"{marker} {abbrev}: {score:2d}  (cost: {cost})")

        description.update("\n".join(lines))
        options_list.display = False
        detail_panel.display = False

    def _show_generate_roll(self) -> None:
        """Display rolling interface."""
        title = self.query_one("#step-title", Static)
        options_list = self.query_one("#options-list", OptionList)
        description = self.query_one("#step-description", Static)
        detail_panel = self.query_one("#detail-panel", VerticalScroll)

        title.update("ABILITY SCORES - Roll 4d6 Drop Lowest")

        lines = ["\\[R] Roll next  \\[A] Roll all  \\[C] Clear all", ""]

        for i in range(6):
            if i < len(self.roll_results):
                result = self.roll_results[i]
                rolls_str = ", ".join(str(r) for r in result["rolls"])
                lines.append(f"Roll {i+1}: [{rolls_str}] → {result['total']}")
            else:
                lines.append(f"Roll {i+1}: --")

        if len(self.roll_results) == 6:
            lines.append("")
            self.base_scores = [r["total"] for r in self.roll_results]
            lines.append(f"Scores: {', '.join(str(s) for s in self.base_scores)}")

        description.update("\n".join(lines))
        options_list.display = False
        detail_panel.display = False

    def _show_ability_assign(self) -> None:
        """Display score assignment interface."""
        title = self.query_one("#step-title", Static)
        options_list = self.query_one("#options-list", OptionList)
        description = self.query_one("#step-description", Static)
        detail_panel = self.query_one("#detail-panel", VerticalScroll)

        title.update("ABILITY SCORES - Assign Scores")

        # Show available scores with assignment status
        assigned_indices = set(v for v in self.score_assignments.values() if v is not None)
        scores_display = []
        for i, score in enumerate(self.base_scores):
            if i in assigned_indices:
                scores_display.append(f"[{score}]")  # Assigned
            else:
                scores_display.append(f" {score} ")  # Available
        scores_line = " ".join(scores_display)

        lines = [f"Scores: {scores_line}", "", "←→ cycle scores, \\[C] clear current, \\[X] clear all", ""]

        for i, ability in enumerate(ABILITIES):
            abbrev = ABILITY_ABBREV[ability]
            assigned_idx = self.score_assignments[ability]
            marker = "▶" if i == self.ability_selected_index else " "

            if assigned_idx is not None:
                score = self.base_scores[assigned_idx]
                modifier = (score - 10) // 2
                mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                lines.append(f"{marker} {abbrev}: {score:2d} ({mod_str})")
            else:
                lines.append(f"{marker} {abbrev}: --")

        description.update("\n".join(lines))
        options_list.display = False
        detail_panel.display = False

    def _show_ability_bonuses(self) -> None:
        """Display bonus application based on ruleset."""
        ruleset = self.char_data.get("ruleset", "dnd2024")

        if ruleset == "dnd2014":
            self._show_bonuses_2014()
        elif ruleset == "dnd2024":
            self._show_bonuses_2024()
        else:  # ToV
            self._show_bonuses_tov()

    def _show_bonuses_2014(self) -> None:
        """Display fixed racial bonuses for 2014 rules."""
        title = self.query_one("#step-title", Static)
        description = self.query_one("#step-description", Static)
        options_list = self.query_one("#options-list", OptionList)
        detail_panel = self.query_one("#detail-panel", VerticalScroll)

        title.update("ABILITY SCORES - Racial Bonuses")

        # Get racial bonuses
        bonuses = self._get_racial_bonuses()
        species_name = self.char_data.get("species", "")
        subspecies_name = self.char_data.get("subspecies")

        lines = []
        if bonuses:
            source = subspecies_name if subspecies_name else species_name
            lines.append(f"Your {source} grants:")
            for ability, bonus in bonuses.items():
                sign = "+" if bonus > 0 else ""
                lines.append(f"  {sign}{bonus} {ability.title()}")
            lines.append("")

        lines.append("Final Scores:")
        for ability in ABILITIES:
            assigned_idx = self.score_assignments[ability]
            if assigned_idx is not None:
                base = self.base_scores[assigned_idx]
                bonus = bonuses.get(ability, 0)
                total = base + bonus
                modifier = (total - 10) // 2
                mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                bonus_str = f" (+{bonus})" if bonus > 0 else ""
                lines.append(f"  {ABILITY_ABBREV[ability]}: {total}{bonus_str} ({mod_str})")

        description.update("\n".join(lines))
        options_list.display = False
        detail_panel.display = False

    def _show_bonuses_2024(self) -> None:
        """Display bonus selection for 2024 rules (background provides +2/+1 or +1/+1/+1 choice)."""
        title = self.query_one("#step-title", Static)
        description = self.query_one("#step-description", Static)
        options_list = self.query_one("#options-list", OptionList)
        detail_panel = self.query_one("#detail-panel", VerticalScroll)

        title.update("ABILITY SCORES - Background Bonuses")

        background_name = self.char_data.get("background", "")
        options = self._get_background_bonus_options()

        if not options:
            # Default to all abilities if no specific options
            options = [a.title() for a in ABILITIES]

        # Step 0: Choose bonus mode
        if self.ability_selected_index == 0:
            lines = [
                f"Your background ({background_name}) allows:",
                f"  Options: {', '.join(options)}",
                "",
                "Choose how to distribute bonuses:",
            ]
            self.current_options = [
                "+2 to one, +1 to another",
                "+1 to all three",
            ]
            description.update("\n".join(lines))
            self._refresh_options()
            options_list.display = True
            detail_panel.display = False
            return

        # Step 1+: Apply bonuses based on mode
        if self.bonus_mode == "spread":
            # +1/+1/+1 mode - show confirmation
            lines = [
                f"Your background ({background_name}) bonuses:",
                "",
                "+1 to each of:",
            ]
            for opt in options:
                lines.append(f"  • {opt}")
            lines.append("")
            lines.append("Press Next to confirm")
            description.update("\n".join(lines))
            options_list.display = False
            detail_panel.display = False
        else:
            # +2/+1 split mode
            lines = [
                f"Your background ({background_name}) allows:",
                "  +2 to one ability, +1 to another",
                "",
                "\\[C] clear current, \\[X] clear all",
                "",
            ]

            # Show selection state
            if self.ability_selected_index == 1:
                lines.append("Select +2 bonus:")
                self.current_options = options
            else:
                lines.append(f"+2 bonus: {self.bonus_plus_2 or '--'}")
                lines.append("")
                lines.append("Select +1 bonus:")
                # Exclude the +2 choice
                self.current_options = [o for o in options if o != self.bonus_plus_2]

            description.update("\n".join(lines))
            self._refresh_options()
            options_list.display = True
            detail_panel.display = False

    def _show_bonuses_tov(self) -> None:
        """Display final scores for ToV (no bonuses)."""
        title = self.query_one("#step-title", Static)
        description = self.query_one("#step-description", Static)
        options_list = self.query_one("#options-list", OptionList)
        detail_panel = self.query_one("#detail-panel", VerticalScroll)

        title.update("ABILITY SCORES - Final Review")

        lines = ["Tales of the Valiant uses base scores only.", "No racial or background bonuses apply.", ""]
        lines.append("Final Scores:")

        for ability in ABILITIES:
            assigned_idx = self.score_assignments[ability]
            if assigned_idx is not None:
                score = self.base_scores[assigned_idx]
                modifier = (score - 10) // 2
                mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                lines.append(f"  {ABILITY_ABBREV[ability]}: {score} ({mod_str})")

        description.update("\n".join(lines))
        options_list.display = False
        detail_panel.display = False

    # Ability step helper methods

    def _calculate_point_buy_remaining(self) -> int:
        """Calculate remaining points for Point Buy."""
        spent = sum(POINT_BUY_COSTS.get(s, 0) for s in self.point_buy_scores.values())
        return POINT_BUY_TOTAL - spent

    def _adjust_point_buy(self, delta: int) -> None:
        """Adjust the selected ability score in Point Buy."""
        ability = ABILITIES[self.ability_selected_index]
        current = self.point_buy_scores[ability]
        new_score = current + delta

        # Check bounds
        if new_score < POINT_BUY_MIN or new_score > POINT_BUY_MAX:
            return

        # Check if we have enough points
        old_cost = POINT_BUY_COSTS.get(current, 0)
        new_cost = POINT_BUY_COSTS.get(new_score, 0)
        cost_diff = new_cost - old_cost

        if cost_diff > self._calculate_point_buy_remaining():
            self.notify("Not enough points!", severity="warning")
            return

        self.point_buy_scores[ability] = new_score
        self._show_generate_point_buy()

    def _roll_one_ability(self) -> dict:
        """Roll 4d6 drop lowest for one ability score."""
        import random
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls_sorted = sorted(rolls)
        kept = rolls_sorted[1:]  # Drop lowest
        total = sum(kept)
        return {"rolls": rolls, "kept": kept, "total": total}

    def _roll_all_abilities(self) -> None:
        """Roll all 6 ability scores."""
        self.roll_results = [self._roll_one_ability() for _ in range(6)]
        self.base_scores = [r["total"] for r in self.roll_results]

    def _get_racial_bonuses(self) -> dict[str, int]:
        """Get racial ability bonuses for 2014 rules."""
        species_name = self.char_data.get("species", "")
        subspecies_name = self.char_data.get("subspecies")

        bonuses: dict[str, int] = {}

        species = get_species(species_name)
        if species:
            for ability, bonus in species.ability_bonuses.items():
                bonuses[ability.lower()] = bonuses.get(ability.lower(), 0) + bonus

            if subspecies_name:
                for subsp in species.subspecies:
                    if subsp.name == subspecies_name:
                        for ability, bonus in subsp.ability_bonuses.items():
                            bonuses[ability.lower()] = bonuses.get(ability.lower(), 0) + bonus
                        break

        return bonuses

    def _get_background_bonus_options(self) -> list[str]:
        """Get ability score bonus options for 2024 background."""
        background_name = self.char_data.get("background", "")
        background = get_background(background_name)

        if background and hasattr(background, "ability_score_options") and background.ability_score_options:
            return background.ability_score_options

        # Default: any three abilities
        return ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

    def _advance_ability_substep(self) -> bool:
        """Advance to next ability sub-step. Returns True if successful."""
        if self.ability_sub_step == "method_select":
            # Save selected method
            method_map = {0: "standard_array", 1: "point_buy", 2: "roll"}
            self.ability_method = method_map.get(self.selected_option, "standard_array")
            self.ability_sub_step = "generate"
            self.ability_selected_index = 0
            self._show_ability_substep()
            return True

        elif self.ability_sub_step == "generate":
            if self.ability_method == "point_buy":
                # Set base_scores from point buy
                self.base_scores = [self.point_buy_scores[a] for a in ABILITIES]
                # Pre-assign scores since point buy already assigns to abilities
                for i, ability in enumerate(ABILITIES):
                    self.score_assignments[ability] = i
                # Skip assignment, go to bonuses
                self.ability_sub_step = "bonuses"
            elif self.ability_method == "roll":
                if len(self.roll_results) < 6:
                    self.notify("Roll all 6 ability scores first!", severity="warning")
                    return False
                self.ability_sub_step = "assign"
            else:  # standard_array
                self.ability_sub_step = "assign"

            self.ability_selected_index = 0
            self._show_ability_substep()
            return True

        elif self.ability_sub_step == "assign":
            # Validate all abilities are assigned
            unassigned = [a for a, v in self.score_assignments.items() if v is None]
            if unassigned:
                self.notify(f"Assign scores to: {', '.join(ABILITY_ABBREV[a] for a in unassigned)}", severity="warning")
                return False
            self.ability_sub_step = "bonuses"
            self.ability_selected_index = 0
            self._show_ability_substep()
            return True

        elif self.ability_sub_step == "bonuses":
            ruleset = self.char_data.get("ruleset", "dnd2024")
            if ruleset == "dnd2024":
                if self.ability_selected_index == 0:
                    # Step 0: Select mode (split vs spread)
                    if self.selected_option == 0:
                        self.bonus_mode = "split"
                        self.ability_selected_index = 1  # Go to +2 selection
                    else:
                        self.bonus_mode = "spread"
                        self.ability_selected_index = 1  # Go to confirmation
                    self.selected_option = 0
                    self._show_ability_substep()
                    return True
                elif self.bonus_mode == "spread":
                    # Spread mode confirmation - done
                    pass  # Fall through to completion
                elif self.ability_selected_index == 1:
                    # Split mode: Selecting +2 - save and move to +1
                    if self.current_options and self.selected_option < len(self.current_options):
                        self.bonus_plus_2 = self.current_options[self.selected_option]
                        self.ability_selected_index = 2
                        self.selected_option = 0
                        self._show_ability_substep()
                        return True
                    return False
                else:
                    # Split mode: Selecting +1 - save and finish
                    if self.current_options and self.selected_option < len(self.current_options):
                        self.bonus_plus_1 = self.current_options[self.selected_option]
                    else:
                        return False

            # Done with abilities
            self.ability_sub_step = None  # Signal completion
            return True

        return False

    def _go_back_ability_substep(self) -> bool:
        """Go back to previous ability sub-step. Returns True if handled within abilities."""
        if self.ability_sub_step == "method_select":
            return False  # Go to previous wizard step

        elif self.ability_sub_step == "generate":
            self.ability_sub_step = "method_select"
            self._show_ability_substep()
            return True

        elif self.ability_sub_step == "assign":
            self.ability_sub_step = "generate"
            self._show_ability_substep()
            return True

        elif self.ability_sub_step == "bonuses":
            ruleset = self.char_data.get("ruleset", "dnd2024")
            if ruleset == "dnd2024":
                if self.ability_selected_index == 2:
                    # Go back from +1 selection to +2 selection
                    self.ability_selected_index = 1
                    self.bonus_plus_1 = None
                    self._show_ability_substep()
                    return True
                elif self.ability_selected_index == 1:
                    # Go back from +2/spread confirmation to mode selection
                    self.ability_selected_index = 0
                    self.bonus_plus_2 = None
                    self.bonus_plus_1 = None
                    self._show_ability_substep()
                    return True
                # Index 0 falls through to go back to previous step

            if self.ability_method == "point_buy":
                # Point buy skips assign, go back to generate
                self.ability_sub_step = "generate"
            else:
                self.ability_sub_step = "assign"
            self._show_ability_substep()
            return True

        return False

    # ==================== Skill Selection Methods ====================

    def _show_skills(self) -> None:
        """Show the skill proficiency selection step."""
        title = self.query_one("#step-title", Static)
        description = self.query_one("#step-description", Static)
        options_list = self.query_one("#options-list", OptionList)

        class_name = self.char_data.get("class", "")
        class_info = get_class_info(class_name)

        if not class_info:
            # Skip if no class info
            title.update("SKILLS - No class data")
            description.update("")
            self.current_options = []
            options_list.display = False
            return

        num_choices = class_info.skill_choices
        skill_options = class_info.skill_options

        title.update(f"SKILL PROFICIENCIES - Choose {num_choices}")

        # Build the display using OptionList options (Textual doesn't render mounted children here)
        options_list.clear_options()
        options_list.remove_children()

        for i, skill in enumerate(skill_options):
            is_selected = skill in self.selected_skills
            prefix = r"\[X]" if is_selected else r"\[ ]"
            options_list.add_option(Option(f"{prefix} {skill}", id=f"skill_{i}"))

        if skill_options:
            self.selected_option = min(self.skill_selected_index, len(skill_options) - 1)
            self._expected_highlight = self.skill_selected_index
            options_list.highlighted = self.skill_selected_index

        options_list.display = True
        self.current_options = skill_options
        selected_count = len(self.selected_skills)
        hint = "↑↓ navigate, Space to toggle, Enter to continue, C clear all."
        if selected_count == num_choices:
            hint = f"{hint}\nPress Next to continue."
        description.update(f"Selected: {selected_count}/{num_choices}\n{hint}")
        self._refresh_details()

    def _toggle_skill(self) -> None:
        """Toggle the currently highlighted skill selection."""
        class_name = self.char_data.get("class", "")
        class_info = get_class_info(class_name)
        if not class_info:
            return

        skill_options = class_info.skill_options
        if self.skill_selected_index >= len(skill_options):
            return

        skill = skill_options[self.skill_selected_index]
        num_choices = class_info.skill_choices

        if skill in self.selected_skills:
            # Deselect
            self.selected_skills.remove(skill)
        else:
            # Select if we haven't reached the limit
            if len(self.selected_skills) < num_choices:
                self.selected_skills.append(skill)
            else:
                self.notify(f"Already selected {num_choices} skills. Deselect one first.", severity="warning")
                return

        self._show_skills()

    def _clear_skills(self) -> None:
        """Clear all skill selections."""
        self.selected_skills = []
        self._show_skills()

    # ==================== Spell Selection Methods ====================

    def _show_spells(self) -> None:
        """Show the spell selection step for casters."""
        title = self.query_one("#step-title", Static)
        description = self.query_one("#step-description", Static)
        options_list = self.query_one("#options-list", OptionList)

        class_name = self.char_data.get("class", "")
        class_info = get_class_info(class_name)

        if not class_info or not class_info.spellcasting_ability:
            # Not a caster, skip this step
            title.update("SPELLS - Not a spellcaster")
            description.update("This class does not cast spells at level 1.")
            options_list.display = False
            self.current_options = []
            return

        # Get available spells for this class
        from dnd_manager.data import get_spells_by_class
        available_spells = get_spells_by_class(class_name)

        # Filter for cantrips and 1st level spells
        cantrips = [s for s in available_spells if s.level == 0]
        level1_spells = [s for s in available_spells if s.level == 1]

        # Determine how many cantrips/spells based on class
        # Using typical values: most casters get 2-3 cantrips and 2-4 known spells at level 1
        cantrips_known = self._get_cantrips_known(class_name)
        spells_known = self._get_spells_known(class_name)

        # Clear both native options and mounted children
        options_list.clear_options()
        options_list.remove_children()

        if self.spell_selection_phase == "cantrips":
            title.update(f"CANTRIPS - Choose {cantrips_known}")
            cantrip_names = [s.name for s in cantrips]

            for i, spell in enumerate(cantrips):
                is_selected = spell.name in self.selected_cantrips
                prefix = r"\[X]" if is_selected else r"\[ ]"
                options_list.add_option(Option(f"{prefix} {spell.name}", id=f"cantrip_{i}"))

            if cantrips:
                self.selected_option = min(self.spell_selected_index, len(cantrips) - 1)
                self._expected_highlight = self.spell_selected_index
                options_list.highlighted = self.spell_selected_index

            self.current_options = cantrip_names
            selected = len(self.selected_cantrips)
            hint = "↑↓ navigate, Space to toggle, Enter to continue, C clear all."
            if selected >= cantrips_known:
                hint = f"{hint}\nPress Next to continue to spells."
            description.update(f"Selected: {selected}/{cantrips_known}\n{hint}")

        else:  # spell_selection_phase == "spells"
            title.update(f"1ST LEVEL SPELLS - Choose {spells_known}")
            spell_names = [s.name for s in level1_spells]

            for i, spell in enumerate(level1_spells):
                is_selected = spell.name in self.selected_spells
                prefix = r"\[X]" if is_selected else r"\[ ]"
                options_list.add_option(Option(f"{prefix} {spell.name}", id=f"spell_{i}"))

            if level1_spells:
                self.selected_option = min(self.spell_selected_index, len(level1_spells) - 1)
                self._expected_highlight = self.spell_selected_index
                options_list.highlighted = self.spell_selected_index

            self.current_options = spell_names
            selected = len(self.selected_spells)
            hint = "↑↓ navigate, Space to toggle, Enter to continue, C clear all."
            if selected >= spells_known:
                hint = f"{hint}\nPress Next to continue."
            description.update(f"Selected: {selected}/{spells_known}\n{hint}")

        options_list.display = True

    def _get_cantrips_known(self, class_name: str) -> int:
        """Get number of cantrips known at level 1."""
        # Level 1 cantrips by class (from PHB)
        cantrips_at_1 = {
            "Bard": 2,
            "Cleric": 3,
            "Druid": 2,
            "Sorcerer": 4,
            "Warlock": 2,
            "Wizard": 3,
        }
        return cantrips_at_1.get(class_name, 2)

    def _get_spells_known(self, class_name: str) -> int:
        """Get number of spells known/prepared at level 1."""
        # Level 1 spells by class (from PHB)
        # Note: Clerics/Druids/Paladins prepare spells (WIS/CHA mod + level)
        # For simplicity, using typical values assuming +3 modifier
        spells_at_1 = {
            "Bard": 4,      # Spells known
            "Cleric": 4,    # Prepared (1 + WIS mod, assume +3)
            "Druid": 4,     # Prepared (1 + WIS mod, assume +3)
            "Sorcerer": 2,  # Spells known
            "Warlock": 2,   # Spells known
            "Wizard": 6,    # Spellbook has 6, prepare INT mod + 1
        }
        return spells_at_1.get(class_name, 2)

    def _toggle_spell(self) -> None:
        """Toggle the currently highlighted spell selection."""
        class_name = self.char_data.get("class", "")
        class_info = get_class_info(class_name)
        if not class_info or not class_info.spellcasting_ability:
            return

        from dnd_manager.data import get_spells_by_class
        available_spells = get_spells_by_class(class_name)

        if self.spell_selection_phase == "cantrips":
            cantrips = [s for s in available_spells if s.level == 0]
            if self.spell_selected_index >= len(cantrips):
                return
            spell_name = cantrips[self.spell_selected_index].name
            max_selections = self._get_cantrips_known(class_name)

            if spell_name in self.selected_cantrips:
                self.selected_cantrips.remove(spell_name)
            else:
                if len(self.selected_cantrips) < max_selections:
                    self.selected_cantrips.append(spell_name)
                else:
                    self.notify(f"Already selected {max_selections} cantrips. Deselect one first.", severity="warning")
                    return
        else:
            level1_spells = [s for s in available_spells if s.level == 1]
            if self.spell_selected_index >= len(level1_spells):
                return
            spell_name = level1_spells[self.spell_selected_index].name
            max_selections = self._get_spells_known(class_name)

            if spell_name in self.selected_spells:
                self.selected_spells.remove(spell_name)
            else:
                if len(self.selected_spells) < max_selections:
                    self.selected_spells.append(spell_name)
                else:
                    self.notify(f"Already selected {max_selections} spells. Deselect one first.", severity="warning")
                    return

        self._show_spells()

    def _clear_spells(self) -> None:
        """Clear spell selections for current phase."""
        if self.spell_selection_phase == "cantrips":
            self.selected_cantrips = []
        else:
            self.selected_spells = []
        self._show_spells()

    # ==================== Equipment Methods ====================

    def _get_starting_equipment(self, class_name: str) -> list[str]:
        """Get basic starting equipment for a class."""
        # Basic starting equipment by class (simplified SRD equipment)
        equipment_map = {
            "Barbarian": ["Greataxe", "Handaxe", "Handaxe", "Explorer's Pack", "Javelin", "Javelin", "Javelin", "Javelin"],
            "Bard": ["Rapier", "Leather Armor", "Dagger", "Entertainer's Pack", "Lute"],
            "Cleric": ["Mace", "Scale Mail", "Shield", "Light Crossbow", "Crossbow Bolts (20)", "Priest's Pack", "Holy Symbol"],
            "Druid": ["Wooden Shield", "Scimitar", "Leather Armor", "Explorer's Pack", "Druidic Focus"],
            "Fighter": ["Chain Mail", "Longsword", "Shield", "Light Crossbow", "Crossbow Bolts (20)", "Dungeoneer's Pack"],
            "Monk": ["Shortsword", "Dungeoneer's Pack", "Dart", "Dart", "Dart", "Dart", "Dart", "Dart", "Dart", "Dart", "Dart", "Dart"],
            "Paladin": ["Chain Mail", "Longsword", "Shield", "Javelin", "Javelin", "Javelin", "Javelin", "Javelin", "Priest's Pack", "Holy Symbol"],
            "Ranger": ["Scale Mail", "Shortsword", "Shortsword", "Longbow", "Arrows (20)", "Dungeoneer's Pack"],
            "Rogue": ["Rapier", "Shortbow", "Arrows (20)", "Burglar's Pack", "Leather Armor", "Dagger", "Dagger", "Thieves' Tools"],
            "Sorcerer": ["Light Crossbow", "Crossbow Bolts (20)", "Arcane Focus", "Dungeoneer's Pack", "Dagger", "Dagger"],
            "Warlock": ["Light Crossbow", "Crossbow Bolts (20)", "Arcane Focus", "Scholar's Pack", "Leather Armor", "Dagger", "Dagger"],
            "Wizard": ["Quarterstaff", "Arcane Focus", "Scholar's Pack", "Spellbook"],
        }
        return equipment_map.get(class_name, ["Backpack", "Bedroll", "Rations (1 day)", "Waterskin"])

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
        # OptionList handles its own scrolling
        return None

    def _get_item_widget_class(self) -> str:
        return "option-list--option"  # OptionList's internal class

    def _update_selection(self) -> None:
        """Update the OptionList to reflect current selection."""
        try:
            options_list = self.query_one("#options-list", OptionList)
            if self.selected_option < len(self.current_options):
                options_list.highlighted = self.selected_option
                options_list.scroll_to_highlight()
            self._refresh_details()
        except NoMatches:
            # Screen not mounted yet
            pass

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
        step_name = self.steps[self.step] if self.step < len(self.steps) else ""

        # Handle ability sub-step navigation
        if step_name == "abilities":
            if self._go_back_ability_substep():
                return  # Handled within abilities step

        # Handle spells step - go back from spells to cantrips
        if step_name == "spells":
            class_name = self.char_data.get("class", "")
            class_info = get_class_info(class_name)
            if class_info and class_info.spellcasting_ability:
                if self.spell_selection_phase == "spells":
                    # Go back to cantrips
                    self.spell_selection_phase = "cantrips"
                    self.spell_selected_index = 0
                    self._show_spells()
                    return

        if self.step > 0:
            self.step -= 1
            self.selected_option = 0
            # Reset skill/spell indices when going back
            self.skill_selected_index = 0
            self.spell_selected_index = 0
            self.spell_selection_phase = "cantrips"
            self._show_step()
            self._save_draft()

    def action_next(self) -> None:
        """Go to next step or create character."""
        step_name = self.steps[self.step]

        # Sync selected_option with OptionList's actual highlighted item
        # This ensures clicking Next button uses the correct selection
        try:
            options_list = self.query_one("#options-list", OptionList)
            if options_list.highlighted is not None:
                self.selected_option = options_list.highlighted
        except NoMatches:
            pass  # OptionList might not exist on some steps

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
            # Reset subspecies and species_feat when species changes
            self.char_data["subspecies"] = None
            self.char_data["species_feat"] = None
        elif step_name == "subspecies":
            if self.current_options:
                self.char_data["subspecies"] = self.current_options[self.selected_option]
                # Reset species_feat when subspecies changes (it may affect feat eligibility)
                self.char_data["species_feat"] = None
        elif step_name == "species_feat":
            if self.current_options:
                self.char_data["species_feat"] = self.current_options[self.selected_option]
        elif step_name == "background":
            self.char_data["background"] = self.current_options[self.selected_option]
        elif step_name == "alignment":
            selected = self.current_options[self.selected_option]
            for alignment in Alignment:
                if alignment.display_name == selected:
                    self.char_data["alignment"] = alignment.value
                    break
        elif step_name == "origin_feat":
            if self.current_options:
                self.char_data["origin_feat"] = self.current_options[self.selected_option]
        elif step_name == "abilities":
            # Handle abilities sub-step navigation
            if not self._advance_ability_substep():
                return  # Stay on current sub-step
            if self.ability_sub_step is None:
                self._persist_ability_state()
                # Finished abilities, move to next step
                self.ability_sub_step = "method_select"  # Reset for potential re-entry
                self.step += 1
                self.selected_option = 0
                self._show_step()
                self._save_draft()
            return
        elif step_name == "skills":
            # Validate skill selection
            class_name = self.char_data.get("class", "")
            class_info = get_class_info(class_name)
            if class_info:
                if len(self.selected_skills) < class_info.skill_choices:
                    self.notify(f"Select {class_info.skill_choices} skills to continue", severity="warning")
                    return
            # Save skills and advance
            self.char_data["skills"] = list(self.selected_skills)
            self.step += 1
            self.selected_option = 0
            self.spell_selected_index = 0
            self.spell_selection_phase = "cantrips"
            self._show_step()
            self._save_draft()
            return
        elif step_name == "spells":
            # Check if this is a caster
            class_name = self.char_data.get("class", "")
            class_info = get_class_info(class_name)
            if not class_info or not class_info.spellcasting_ability:
                # Not a caster, just advance
                self.step += 1
                self.selected_option = 0
                self._show_step()
                self._save_draft()
                return

            # Validate spell selections based on phase
            if self.spell_selection_phase == "cantrips":
                cantrips_needed = self._get_cantrips_known(class_name)
                if len(self.selected_cantrips) < cantrips_needed:
                    self.notify(f"Select {cantrips_needed} cantrips to continue", severity="warning")
                    return
                # Move to spell selection
                self.spell_selection_phase = "spells"
                self.spell_selected_index = 0
                self._show_spells()
                return
            else:  # spells phase
                spells_needed = self._get_spells_known(class_name)
                if len(self.selected_spells) < spells_needed:
                    self.notify(f"Select {spells_needed} spells to continue", severity="warning")
                    return
                # Save spells and advance
                self.char_data["cantrips"] = list(self.selected_cantrips)
                self.char_data["spells"] = list(self.selected_spells)
                self.step += 1
                self.selected_option = 0
                self._show_step()
                self._save_draft()
                return
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
        from dnd_manager.models.abilities import AbilityScores, AbilityScore

        # Create character
        char = Character.create_new(
            name=self.char_data["name"],
            class_name=self.char_data["class"],
        )
        char.species = self.char_data["species"]
        char.subspecies = self.char_data.get("subspecies")
        char.background = self.char_data["background"]
        if self.char_data.get("alignment"):
            try:
                char.alignment = Alignment(self.char_data["alignment"])
            except ValueError:
                pass  # Invalid alignment value

        # Set ability scores from wizard data
        ruleset = self.char_data.get("ruleset", "dnd2024")

        ability_state = self._get_active_ability_state()
        # Get base scores from assignments
        base_scores = {}
        assignments = ability_state["score_assignments"]
        base_scores_list = ability_state["base_scores"]
        for ability in ABILITIES:
            idx = assignments.get(ability)
            if idx is not None and idx < len(base_scores_list):
                base_scores[ability] = base_scores_list[idx]
            else:
                base_scores[ability] = 10  # Default

        # Get bonuses based on ruleset
        bonuses = self._get_ability_bonuses(ability_state)

        # Create ability scores with bonuses applied
        char.abilities = AbilityScores(
            strength=AbilityScore(base=base_scores["strength"], bonus=bonuses.get("strength", 0)),
            dexterity=AbilityScore(base=base_scores["dexterity"], bonus=bonuses.get("dexterity", 0)),
            constitution=AbilityScore(base=base_scores["constitution"], bonus=bonuses.get("constitution", 0)),
            intelligence=AbilityScore(base=base_scores["intelligence"], bonus=bonuses.get("intelligence", 0)),
            wisdom=AbilityScore(base=base_scores["wisdom"], bonus=bonuses.get("wisdom", 0)),
            charisma=AbilityScore(base=base_scores["charisma"], bonus=bonuses.get("charisma", 0)),
        )

        # Calculate HP at level 1: max hit die + CON modifier
        class_def = get_class_info(self.char_data["class"])
        if class_def:
            # Parse hit die (e.g., "d10" -> 10)
            hit_die_size = int(class_def.hit_die[1:])  # Remove 'd' prefix
            con_mod = char.abilities.constitution.modifier
            max_hp = max(1, hit_die_size + con_mod)  # Minimum 1 HP
            char.combat.hit_points.maximum = max_hp
            char.combat.hit_points.current = max_hp

        # Add species feat if selected (from Variant Human or Human ToV)
        if self.char_data.get("species_feat"):
            feat_name = self.char_data["species_feat"]
            feat_data = get_feat(feat_name)
            if feat_data:
                char.features.append(Feature(
                    name=feat_name,
                    source="feat",
                    description=feat_data.description,
                ))

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

        # Add skill proficiencies
        from dnd_manager.models.abilities import Skill, SkillProficiency, Ability as AbilityEnum

        skills = self.selected_skills or self.char_data.get("skills", [])
        for skill_name in skills:
            # Convert skill name to Skill enum
            skill_key = skill_name.lower().replace(" ", "_")
            try:
                skill_enum = Skill(skill_key)
                char.proficiencies.skills[skill_enum] = SkillProficiency.PROFICIENT
            except ValueError:
                pass  # Skip if not a valid skill

        # Add saving throw proficiencies from class
        class_data = get_class_info(self.char_data["class"])
        if class_data:
            for save_name in class_data.saving_throws:
                try:
                    ability_enum = AbilityEnum(save_name.lower())
                    if ability_enum not in char.proficiencies.saving_throws:
                        char.proficiencies.saving_throws.append(ability_enum)
                except ValueError:
                    pass

            # Add weapon and armor proficiencies from class
            char.proficiencies.weapons = class_data.weapon_proficiencies.copy()
            char.proficiencies.armor = class_data.armor_proficiencies.copy()

        # Add cantrips and spells for casters
        class_info = get_class_info(self.char_data["class"])
        if class_info and class_info.spellcasting_ability:
            from dnd_manager.models.abilities import Ability as AbilityEnum
            # Set spellcasting ability
            ability_name = class_info.spellcasting_ability.lower()
            try:
                char.spellcasting.ability = AbilityEnum(ability_name)
            except ValueError:
                pass

            # Add cantrips and spells
            char.spellcasting.cantrips = list(self.selected_cantrips)
            char.spellcasting.known = list(self.selected_spells)

        # Add racial traits from species data
        species = get_species(self.char_data["species"])
        if species:
            # Set speed from species (ruleset-aware)
            char.combat.speed = species.get_speed(ruleset)

            for trait in species.traits:
                char.features.append(Feature(
                    name=trait.name,
                    source="racial",
                    description=trait.description,
                ))
            # Add subspecies traits if applicable
            if self.char_data.get("subspecies"):
                for subsp in species.subspecies:
                    if subsp.name == self.char_data["subspecies"]:
                        for trait in subsp.traits:
                            char.features.append(Feature(
                                name=trait.name,
                                source="racial",
                                description=trait.description,
                            ))
                        break

        # Add basic starting equipment based on class
        from dnd_manager.models.character import InventoryItem
        starting_equipment = self._get_starting_equipment(self.char_data["class"])
        for item_name in starting_equipment:
            char.equipment.items.append(InventoryItem(name=item_name))
        # Add starting gold
        char.equipment.currency.gp = 10

        # Save character and clear draft
        self.app.store.save(char)
        self.app.current_character = char
        self.draft_store.clear_draft()

        self.notify(f"Created {char.name}!")

        # Go to dashboard
        self.app.pop_screen()
        self.app.push_screen(MainDashboard(char))


    def on_key(self, event) -> None:
        """Handle key presses for navigation and special actions."""
        step_name = self.steps[self.step] if self.step < len(self.steps) else ""
        self._last_key = event.key

        # Handle ability step special keys
        if step_name == "abilities":
            if self._handle_ability_key(event.key):
                event.prevent_default()
                return

        # Handle skills step navigation
        if step_name == "skills":
            if self._handle_skills_key(event.key):
                event.prevent_default()
                return

        # Handle spells step navigation
        if step_name == "spells":
            if self._handle_spells_key(event.key):
                event.prevent_default()
                return

        # Only do letter jump on steps that show options list
        if step_name in ("class", "species", "subspecies", "species_feat", "background", "origin_feat"):
            if self._handle_key_for_letter_jump(event.key):
                event.prevent_default()

    def _handle_ability_key(self, key: str) -> bool:
        """Handle special keys for ability step. Returns True if handled."""
        if self.ability_sub_step == "generate":
            if self.ability_method == "point_buy":
                if key == "up":
                    if self.ability_selected_index > 0:
                        self.ability_selected_index -= 1
                        self._show_generate_point_buy()
                    return True
                elif key == "down":
                    if self.ability_selected_index < len(ABILITIES) - 1:
                        self.ability_selected_index += 1
                        self._show_generate_point_buy()
                    return True
                elif key == "left":
                    self._adjust_point_buy(-1)
                    return True
                elif key == "right":
                    self._adjust_point_buy(1)
                    return True
                elif key.lower() == "x":
                    # Reset all to 8
                    self.point_buy_scores = {a: 8 for a in ABILITIES}
                    self._show_generate_point_buy()
                    return True

            elif self.ability_method == "roll":
                if key.lower() == "r":
                    # Roll next
                    if len(self.roll_results) < 6:
                        self.roll_results.append(self._roll_one_ability())
                        self._show_generate_roll()
                    return True
                elif key.lower() == "a":
                    # Roll all
                    self._roll_all_abilities()
                    self._show_generate_roll()
                    return True
                elif key.lower() == "c":
                    # Clear all
                    self.roll_results = []
                    self._show_generate_roll()
                    return True

        elif self.ability_sub_step == "assign":
            if key == "up":
                if self.ability_selected_index > 0:
                    self.ability_selected_index -= 1
                    self._show_ability_assign()
                return True
            elif key == "down":
                if self.ability_selected_index < len(ABILITIES) - 1:
                    self.ability_selected_index += 1
                    self._show_ability_assign()
                return True
            elif key in ("left", "right"):
                # Cycle through available scores for current ability
                self._cycle_assignment(1 if key == "right" else -1)
                return True
            elif key.lower() == "c" or key == "backspace":
                # Clear current assignment
                ability = ABILITIES[self.ability_selected_index]
                self.score_assignments[ability] = None
                self._show_ability_assign()
                return True
            elif key.lower() == "x":
                # Clear all assignments
                for ability in ABILITIES:
                    self.score_assignments[ability] = None
                self._show_ability_assign()
                return True

        elif self.ability_sub_step == "bonuses":
            ruleset = self.char_data.get("ruleset", "dnd2024")
            if ruleset == "dnd2024" and self.bonus_mode == "split":
                if key.lower() == "c" or key == "backspace":
                    # Clear current bonus selection
                    if self.ability_selected_index == 2:
                        # Clear +1
                        self.bonus_plus_1 = None
                    elif self.ability_selected_index == 1:
                        # Clear +2
                        self.bonus_plus_2 = None
                    self._show_ability_substep()
                    return True
                elif key.lower() == "x":
                    # Clear all bonus selections and go back to mode selection
                    self.bonus_plus_2 = None
                    self.bonus_plus_1 = None
                    self.ability_selected_index = 0
                    self._show_ability_substep()
                    return True

        return False

    def _handle_skills_key(self, key: str) -> bool:
        """Handle special keys for skills step. Returns True if handled."""
        if key == "space":
            self._toggle_skill()
            return True
        elif key.lower() == "c":
            self._clear_skills()
            return True

        return False

    def _handle_spells_key(self, key: str) -> bool:
        """Handle special keys for spells step. Returns True if handled."""
        class_name = self.char_data.get("class", "")
        class_info = get_class_info(class_name)
        if not class_info or not class_info.spellcasting_ability:
            return False

        if key == "space":
            self._toggle_spell()
            return True
        elif key.lower() == "c":
            self._clear_spells()
            return True

        return False

    def _cycle_assignment(self, direction: int) -> None:
        """Cycle through available scores for the selected ability."""
        ability = ABILITIES[self.ability_selected_index]
        current_idx = self.score_assignments[ability]

        # Find available score indices (not assigned to other abilities)
        assigned_indices = {v for k, v in self.score_assignments.items() if v is not None and k != ability}
        available = [i for i in range(len(self.base_scores)) if i not in assigned_indices]

        if not available:
            return

        if current_idx is None:
            # Assign first/last available
            new_idx = available[0] if direction > 0 else available[-1]
        else:
            # Find current position in available and cycle
            if current_idx in available:
                pos = available.index(current_idx)
                new_pos = (pos + direction) % len(available)
                new_idx = available[new_pos]
            else:
                new_idx = available[0] if direction > 0 else available[-1]

        self.score_assignments[ability] = new_idx
        self._show_ability_assign()

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Handle option highlight change (keyboard navigation)."""
        import datetime
        log_file = "/tmp/dnd_scroll_debug.log"

        if event.option_list.id == "options-list":
            new_index = event.option_index
            old_index = self.selected_option

            # Ignore spurious highlight events that try to reset to 0
            # These happen when OptionList rebuilds and auto-highlights first item
            if new_index == 0 and old_index != 0 and self._expected_highlight != 0:
                with open(log_file, "a") as f:
                    f.write(f"{datetime.datetime.now()} highlighted: IGNORED spurious 0 (was {old_index}, expected {self._expected_highlight})\n")
                return

            self.selected_option = new_index
            self._expected_highlight = new_index  # Update expected for future events
            step_name = self.steps[self.step] if self.step < len(self.steps) else ""
            if step_name == "skills":
                self.skill_selected_index = new_index
            elif step_name == "spells":
                self.spell_selected_index = new_index
            self._refresh_details()

            # Scroll to center the highlighted item
            options_list = event.option_list
            viewport_height = options_list.size.height
            if viewport_height > 0:
                # Each option is 1 line tall in OptionList
                target_scroll = max(0, new_index - viewport_height // 2)
                options_list.scroll_y = target_scroll

                with open(log_file, "a") as f:
                    f.write(f"{datetime.datetime.now()} highlighted: {old_index}→{new_index}, scroll_y={target_scroll} (vh={viewport_height})\n")
            else:
                with open(log_file, "a") as f:
                    f.write(f"{datetime.datetime.now()} highlighted: {old_index}→{self.selected_option}\n")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection (Enter key or click)."""
        if event.option_list.id == "options-list":
            step_name = self.steps[self.step] if self.step < len(self.steps) else ""
            if step_name == "skills" and self._last_key == "space":
                self._toggle_skill()
                event.stop()
                return
            self.selected_option = event.option_index
            self.action_next()  # Proceed to next step

    def action_cancel(self) -> None:
        """Cancel character creation - draft is auto-saved for resume."""
        self._save_draft()  # Ensure latest state is saved
        self.notify("Progress saved - you can resume anytime")
        self.app.pop_screen()

    def action_ai_help(self) -> None:
        """Open AI assistant for help with character creation."""
        # Build context about current step
        step_name = self.steps[self.step] if self.step < len(self.steps) else "unknown"
        step_descriptions = {
            "ruleset": "choosing which D&D ruleset to use",
            "name": "choosing a character name",
            "class": "choosing a class",
            "species": "choosing a species/race",
            "subspecies": "choosing a subspecies/subrace",
            "species_feat": "choosing a bonus feat",
            "background": "choosing a background",
            "origin_feat": "choosing an origin feat",
            "abilities": "assigning ability scores",
            "skills": "choosing skill proficiencies",
            "spells": "selecting cantrips and spells",
            "confirm": "reviewing their character",
        }
        step_description = step_descriptions.get(step_name, "creating a character")

        # Include current selections for context
        current_info = []
        if self.char_data.get("class"):
            current_info.append(f"Class: {self.char_data['class']}")
        if self.char_data.get("species"):
            current_info.append(f"Species: {self.char_data['species']}")
        if self.char_data.get("background"):
            current_info.append(f"Background: {self.char_data['background']}")

        context = {
            "screen_type": "Character Creation",
            "description": f"User is {step_description}",
            "data": ", ".join(current_info) if current_info else "No selections yet",
        }
        self.app.push_screen(AIOverlayScreen(screen_context=context))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input fields - proceed to next step."""
        if event.input.id == "name-input":
            self.action_next()



