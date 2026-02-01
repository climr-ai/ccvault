"""Level management and picker screens for the D&D Manager application."""

from typing import TYPE_CHECKING, Callable, Optional

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


class MulticlassSelectScreen(Screen):
    """Screen for selecting which class to level in (multiclassing)."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
        Binding("up", "prev", "Previous"),
        Binding("down", "next", "Next"),
        Binding("p", "select_primary", "Primary Class"),
    ]

    def __init__(self, character: "Character", on_select: Callable, **kwargs) -> None:
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
            Static("  \\[P] Primary Class  \\[Enter] Select  \\[Esc] Cancel", classes="hint"),
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

    def __init__(self, character: "Character", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self._pane_focus_index = 0
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
                    Static("  \\[↑/+] Increase Level", classes="option"),
                    Static("  \\[↓/-] Decrease Level", classes="option"),
                    Static("  \\[C]   Choose Class (Multiclass)", classes="option"),
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
            Static("  \\[Enter] Save Changes  \\[Esc] Cancel", id="hint-text", classes="hint"),
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
            hint_widget.update("  ⚠ Press \\[Enter] again to CONFIRM changes  \\[Esc] Cancel")
        else:
            hint_widget.update("  \\[Enter] Save Changes  \\[Esc] Cancel")

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

        asi_levels = ruleset.get_asi_levels()
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

        asi_levels = ruleset.get_asi_levels()
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
                    asi_levels = ruleset.get_asi_levels()
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
        self._apply_level_changes(level_diff)

    def _apply_level_changes(self, level_diff: int) -> None:
        """Apply the level changes to the character."""
        # Lazy import to avoid circular dependency
        from dnd_manager.app import MainDashboard

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


class FeatPickerScreen(ListNavigationMixin, Screen):
    """Screen for selecting a feat during level up or character creation."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select Feat"),
        Binding("/", "search", "Search"),
    ]

    def __init__(self, character: "Character", on_select: Optional[Callable] = None, **kwargs) -> None:
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
            Static("↑/↓ Navigate  Type to jump  / Search  Enter Select", classes="subtitle"),
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
        except NoMatches:
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
        except NoMatches:
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

    def __init__(self, character: "Character", on_select: Optional[Callable] = None, **kwargs) -> None:
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
            details_widget.mount(Static(f"    {subclass.description}", classes="subclass-desc"))

        details_widget.mount(Static(""))
        details_widget.mount(Static("  Features:", classes="section-header"))
        for feature in subclass.features:
            details_widget.mount(Static(f"    Lv{feature.level}: {feature.name}", classes="feature-item"))

    # ListNavigationMixin implementation
    def _get_list_items(self) -> list:
        return self.subclasses

    def _get_item_name(self, item) -> str:
        return item.name

    def _get_scroll_container(self):
        try:
            return self.query_one("#subclass-list", VerticalScroll)
        except NoMatches:
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
