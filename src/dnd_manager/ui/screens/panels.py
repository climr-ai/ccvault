"""Dashboard panel widgets for the main character view."""

from typing import TYPE_CHECKING, Optional

from textual.containers import VerticalScroll
from textual.widgets import Static
from textual.app import ComposeResult

from dnd_manager.models.character import Character, RulesetId
from dnd_manager.ui.screens.base import apply_item_order
from dnd_manager.ui.screens.widgets import ClickableListItem

if TYPE_CHECKING:
    from dnd_manager.data.items import Weapon


def _has_weapon_category_proficiency(proficiencies: list[str], category: str) -> bool:
    """Check if proficiencies include a weapon category (e.g., 'Simple', 'Martial').

    Handles both exact matches ('Simple') and prefix matches ('Simple Weapons').
    """
    return category in proficiencies or any(p.startswith(category) for p in proficiencies)


def is_weapon_proficient(character: Character, weapon: "Weapon") -> bool:
    """Determine if a character is proficient with a specific weapon.

    Args:
        character: The character to check proficiency for.
        weapon: The weapon to check proficiency with.

    Returns:
        True if the character is proficient with the weapon.
    """
    profs = character.proficiencies.weapons

    # Direct proficiency checks
    if "All" in profs or weapon.name in profs:
        return True

    # Check category proficiency (Simple/Martial)
    weapon_category = weapon.category.split()[0]  # Get "Simple" or "Martial"
    has_category_prof = _has_weapon_category_proficiency(profs, weapon_category)

    # D&D 2024 Rogue special rule: only proficient with Finesse or Light weapons
    if character.meta.ruleset == RulesetId.DND_2024 and character.primary_class.name == "Rogue":
        has_any_weapon_prof = (
            _has_weapon_category_proficiency(profs, "Simple")
            or _has_weapon_category_proficiency(profs, "Martial")
        )
        if has_any_weapon_prof:
            is_finesse_or_light = "Finesse" in weapon.properties or "Light" in weapon.properties
            return is_finesse_or_light

    return has_category_prof


class DashboardPanel(VerticalScroll):
    """Focusable, scrollable dashboard panel."""

    can_focus = True
    # Clear inherited scroll bindings so arrow keys bubble up to MainDashboard
    BINDINGS = []

    def __init__(self, character: Optional[Character] = None, pane_id: Optional[str] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.pane_id = pane_id
        self.selected_index = 0

    def on_click(self) -> None:
        self.focus()

    def on_clickable_list_item_selected(self, event: ClickableListItem.Selected) -> None:
        """Handle mouse selection within the panel."""
        self.selected_index = event.index
        self.focus()
        # Don't recompose on click - it would destroy widgets before Activated message bubbles.
        # Visual marker update happens on arrow key navigation or next compose.
        event.stop()

    def on_clickable_list_item_activated(self, event: ClickableListItem.Activated) -> None:
        """Handle mouse activation within the panel (double-click opens detail)."""
        self.selected_index = event.index
        self.focus()
        # Don't stop - let it bubble up to MainDashboard to open DetailOverlay.

    def get_items(self) -> list:
        """Return selectable items for this panel."""
        return []

    def get_selected_item(self):
        items = self.get_items()
        if not items:
            return None
        return items[min(self.selected_index, len(items) - 1)]

    async def move_selection(self, delta: int) -> None:
        items = self.get_items()
        if not items:
            # No selectable items - just scroll the pane content
            scroll_amount = 2  # Lines to scroll per key press
            if delta < 0:
                self.scroll_y = max(0, self.scroll_y - scroll_amount)
            else:
                self.scroll_y = self.scroll_y + scroll_amount
            return
        self.selected_index = max(0, min(len(items) - 1, self.selected_index + delta))
        await self.recompose()
        # Schedule scroll after widgets are mounted
        self.call_after_refresh(self._scroll_to_selected)

    def _scroll_to_selected(self) -> None:
        """Scroll to keep the selected item visible in the viewport."""
        # Find clickable items (those with selection markers)
        clickable_items = list(self.query(ClickableListItem))
        if self.selected_index < len(clickable_items):
            selected_widget = clickable_items[self.selected_index]
            # Calculate scroll position to center the item
            viewport_height = self.size.height
            if viewport_height > 0:
                # Get widget's position relative to scroll container
                widget_y = selected_widget.region.y
                # Center the item in viewport
                target_scroll = max(0, widget_y - viewport_height // 2)
                self.scroll_y = target_scroll
            else:
                self.scroll_to_center(selected_widget, animate=False)


class AbilityBlock(DashboardPanel):
    """Widget displaying ability scores with color-coded modifiers."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

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
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        self._abilities_cache = abilities
        for index, ability in enumerate(abilities):
            score = getattr(self.character.abilities, ability)
            abbr = ability[:3].upper()
            modifier_class = self._get_modifier_class(score.modifier)
            selected = "▶" if index == self.selected_index else " "
            yield ClickableListItem(
                f"{selected} {abbr} {score.total:2d} ({score.modifier_str})",
                index=index,
                classes=f"ability-row {modifier_class} selected-row" if selected == "▶" else f"ability-row {modifier_class}",
            )

    def get_items(self) -> list:
        return getattr(self, "_abilities_cache", [])


class CharacterInfo(DashboardPanel):
    """Widget displaying character identity info."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

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


class CombatStats(DashboardPanel):
    """Widget displaying combat statistics."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

    def compose(self) -> ComposeResult:
        c = self.character
        hp = c.combat.hit_points

        yield Static("COMBAT", classes="panel-title")
        yield Static(f"AC: {c.combat.total_ac}    Init: {c.get_initiative():+d}")
        yield Static(f"Speed: {c.combat.total_speed}ft")
        yield Static(f"HP: {hp.current}/{hp.maximum} T: {hp.temporary}", classes="hp-line")

        yield Static(f"Hit Dice: {c.combat.get_hit_dice_display()}")
        yield Static(f"Prof Bonus: +{c.proficiency_bonus}")

        # Spellcasting info if applicable
        if c.spellcasting.ability:
            dc = c.get_spell_save_dc()
            atk = c.get_spell_attack_bonus()
            yield Static(f"Spell DC: {dc}  Atk: +{atk}")


class QuickActions(DashboardPanel):
    """Widget with quick action buttons."""

    def compose(self) -> ComposeResult:
        actions = [
            ("Spells", "s"),
            ("Inventory", "i"),
            ("Feats", "f"),
            ("Notes", "n"),
            ("AI Chat", "a"),
            ("Roll", "r"),
            ("Homebrew Guidelines", "h"),
            ("Mastery", "m"),
            ("Edit Character", "e"),
        ]
        self._actions_cache = actions
        yield Static("QUICK ACTIONS", classes="panel-title")
        for index, (label, key) in enumerate(actions):
            selected = "▶" if index == self.selected_index else " "
            line = f"{selected} \\[{key.upper()}]{label}"
            yield ClickableListItem(line, index=index, classes="selected-row" if selected == "▶" else "")

    def get_items(self) -> list:
        return getattr(self, "_actions_cache", [])


class SkillList(DashboardPanel):
    """Widget displaying skills."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

    def compose(self) -> ComposeResult:
        from dnd_manager.models.abilities import Skill, SkillProficiency, SKILL_ABILITY_MAP

        yield Static("SKILLS", classes="panel-title")

        skills = list(Skill)
        skills = apply_item_order(
            skills,
            self.character.meta.panel_item_orders.get("skills"),
            lambda s: s.display_name,
        )
        self._skills_cache = skills
        for index, skill in enumerate(skills):
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

            selected = "▶" if skill == self.get_selected_item() else " "
            yield ClickableListItem(
                f"{selected} {indicator} {skill.display_name} ({ability.abbreviation}) {mod:+d}",
                index=index,
                classes="skill-row selected-row" if selected == "▶" else "skill-row",
            )

    def get_items(self) -> list:
        from dnd_manager.models.abilities import Skill
        return getattr(self, "_skills_cache", list(Skill))


class SpellSlots(DashboardPanel):
    """Widget displaying spell slots."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

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


class PreparedSpells(DashboardPanel):
    """Widget displaying prepared spells."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

    def compose(self) -> ComposeResult:
        yield Static("PREPARED SPELLS", classes="panel-title")

        prepared = apply_item_order(
            self.character.spellcasting.prepared,
            self.character.meta.panel_item_orders.get("prepared_spells"),
            lambda s: s,
        )
        self._prepared_cache = prepared
        if not prepared:
            yield Static("No spells prepared", classes="empty-state")
            yield Static("Press \\[S] to browse spells", classes="empty-state-hint")
            return

        for index, spell in enumerate(prepared):
            selected = "▶" if index == self.selected_index else " "
            yield ClickableListItem(
                f"{selected} {spell}",
                index=index,
                classes="selected-row" if selected == "▶" else "",
            )

    def get_items(self) -> list:
        return getattr(self, "_prepared_cache", [])


class KnownSpells(DashboardPanel):
    """Widget displaying known spells."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

    def compose(self) -> ComposeResult:
        yield Static("KNOWN SPELLS", classes="panel-title")
        known = apply_item_order(
            self.character.spellcasting.known,
            self.character.meta.panel_item_orders.get("known_spells"),
            lambda s: s,
        )
        self._known_cache = known
        if not known:
            yield Static("No known spells", classes="empty-state")
            return
        for index, spell in enumerate(known):
            selected = "▶" if index == self.selected_index else " "
            yield ClickableListItem(
                f"{selected} {spell}",
                index=index,
                classes="selected-row" if selected == "▶" else "",
            )

    def get_items(self) -> list:
        return getattr(self, "_known_cache", [])


class WeaponsPane(DashboardPanel):
    """Widget displaying weapons and equipped items."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

    def _is_weapon_proficient(self, weapon) -> bool:
        return is_weapon_proficient(self.character, weapon)

    def _ability_modifier_for_weapon(self, weapon) -> int:
        str_mod = self.character.abilities.strength.modifier
        dex_mod = self.character.abilities.dexterity.modifier
        if "Finesse" in weapon.properties:
            return max(str_mod, dex_mod)
        if "Ranged" in weapon.category:
            return dex_mod
        return str_mod

    def _format_damage(self, damage_die: str, bonus: int) -> str:
        if bonus == 0:
            return damage_die
        sign = "+" if bonus > 0 else "-"
        return f"{damage_die}{sign}{abs(bonus)}"

    def _versatile_die(self, damage_die: str) -> Optional[str]:
        import re

        match = re.match(r"^(\d+)d(\d+)$", damage_die)
        if not match:
            return None
        count, die_size = int(match.group(1)), int(match.group(2))
        if count != 1:
            return None
        step_map = {4: 6, 6: 8, 8: 10, 10: 12}
        new_size = step_map.get(die_size)
        if not new_size:
            return None
        return f"{count}d{new_size}"

    def _weapon_description(self, weapon) -> str:
        category = "weapon"
        if "Melee" in weapon.category:
            category = "melee weapon"
        elif "Ranged" in weapon.category:
            category = "ranged weapon"
        tier = "Simple" if "Simple" in weapon.category else "Martial"
        return f"{tier} {category} dealing {weapon.damage} {weapon.damage_type} damage."

    def compose(self) -> ComposeResult:
        from dnd_manager.data import get_weapon_by_name, get_weapon_mastery_for_weapon, get_weapon_mastery_summary

        yield Static("WEAPONS", classes="panel-title")
        items = self.character.equipment.items
        weapons = []
        for item in items:
            if get_weapon_by_name(item.name):
                weapons.append(item)
        weapons = apply_item_order(weapons, self.character.meta.panel_item_orders.get("weapons"), lambda i: i.name)
        self._weapons_cache = weapons
        if not weapons:
            yield Static("No weapons in inventory", classes="empty-state")
            return
        for index, item in enumerate(weapons):
            weapon = get_weapon_by_name(item.name)
            if not weapon:
                continue
            equipped = True if item.equipped else False
            marker = "★" if equipped else " "
            qty = f"x{item.quantity}" if item.quantity > 1 else ""
            selected = "▶" if index == self.selected_index else " "
            proficient = self._is_weapon_proficient(weapon)
            ability_mod = self._ability_modifier_for_weapon(weapon)
            magic_bonus = item.attack_bonus if hasattr(item, 'attack_bonus') else 0
            attack_bonus = ability_mod + (self.character.proficiency_bonus if proficient else 0) + magic_bonus
            damage = self._format_damage(weapon.damage, ability_mod + magic_bonus)
            versatile = self._versatile_die(weapon.damage) if "Versatile" in weapon.properties else None
            range_text = None
            if weapon.range_normal:
                if weapon.range_long:
                    range_text = f"Range {weapon.range_normal}/{weapon.range_long}"
                else:
                    range_text = f"Range {weapon.range_normal}"

            status = []
            if item.attuned:
                status.append("A")
            if item.bonded:
                status.append("B")
            if item.held:
                status.append(item.held[0].upper())
            status_text = f"[{''.join(status)}]" if status else ""
            # Show magic bonus in item name
            magic_label = ""
            if magic_bonus > 0:
                magic_label = f" +{magic_bonus}"
            yield ClickableListItem(
                f"{selected} {marker} {item.name}{magic_label} {qty} {status_text}".strip(),
                index=index,
                classes="selected-row" if selected == "▶" else "",
            )
            prof_label = "" if proficient else " (no prof)"
            yield Static(f"  {attack_bonus:+d} to hit{prof_label}, {damage} {weapon.damage_type}")

            # Build compact info line: Range, Versatile damage, Mastery
            info_parts = []
            if range_text:
                info_parts.append(range_text)
            if versatile:
                info_parts.append(f"Versatile ({self._format_damage(versatile, ability_mod + magic_bonus)})")
            # Check for mastery
            mastery = None
            if self.character.meta.ruleset == RulesetId.DND_2024 and self.character.can_use_weapon_mastery(weapon.name):
                mastery = get_weapon_mastery_for_weapon(weapon.name)
            if mastery:
                info_parts.append(mastery)
            if info_parts:
                yield Static("  " + " • ".join(info_parts))

    def get_items(self) -> list:
        return getattr(self, "_weapons_cache", [])


class FeatsPane(DashboardPanel):
    """Widget displaying feats."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

    def compose(self) -> ComposeResult:
        yield Static("FEATS", classes="panel-title")
        feats = [f for f in self.character.features if f.source == "feat"]
        feats = apply_item_order(
            feats,
            self.character.meta.panel_item_orders.get("feats"),
            lambda f: f.name,
        )
        self._feats_cache = feats
        if not feats:
            yield Static("No feats", classes="empty-state")
            return
        for index, feat in enumerate(feats):
            selected = "▶" if index == self.selected_index else " "
            yield ClickableListItem(
                f"{selected} {feat.name}",
                index=index,
                classes="selected-row" if selected == "▶" else "",
            )

    def get_items(self) -> list:
        return getattr(self, "_feats_cache", [])


class InventoryPane(DashboardPanel):
    """Widget displaying inventory summary."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

    def compose(self) -> ComposeResult:
        yield Static("INVENTORY", classes="panel-title")
        items = apply_item_order(
            self.character.equipment.items,
            self.character.meta.panel_item_orders.get("inventory"),
            lambda i: i.name,
        )
        self._inventory_cache = items
        if not items:
            yield Static("No items", classes="empty-state")
        for index, item in enumerate(items):
            selected = "▶" if index == self.selected_index else " "
            qty = f"x{item.quantity}" if item.quantity > 1 else ""
            status = []
            if item.equipped:
                status.append("E")
            if item.attuned:
                status.append("A")
            if item.bonded:
                status.append("B")
            if item.held:
                status.append(item.held[0].upper())
            status_text = f"[{''.join(status)}]" if status else ""
            yield ClickableListItem(
                f"{selected} {item.name} {qty} {status_text}".strip(),
                index=index,
                classes="selected-row" if selected == "▶" else "",
            )
        currency = self.character.equipment.currency
        yield Static("")
        yield Static(f"Gold: {currency.gp}  Silver: {currency.sp}  Copper: {currency.cp}")

    def get_items(self) -> list:
        return getattr(self, "_inventory_cache", [])


class ArmorPane(DashboardPanel):
    """Widget displaying armor and shields."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

    def compose(self) -> ComposeResult:
        from dnd_manager.data import get_armor_by_name

        yield Static("ARMOR", classes="panel-title")
        items = self.character.equipment.items
        armor_items = []
        for item in items:
            armor = get_armor_by_name(item.name)
            if armor:
                armor_items.append((item, armor))
        armor_items = apply_item_order(
            armor_items,
            self.character.meta.panel_item_orders.get("armor"),
            lambda x: x[0].name,
        )
        self._armor_cache = [x[0] for x in armor_items]

        if not armor_items:
            yield Static("No armor", classes="empty-state")
            return

        for index, (item, armor) in enumerate(armor_items):
            selected = "▶" if index == self.selected_index else " "
            equipped_marker = "★" if item.equipped else " "
            # Calculate AC with bonuses
            base_ac = armor.base_ac
            magic_bonus = item.ac_bonus if hasattr(item, 'ac_bonus') else 0
            total_ac = base_ac + magic_bonus
            # Magic label
            magic_label = f" +{magic_bonus}" if magic_bonus > 0 else ""
            yield ClickableListItem(
                f"{selected} {equipped_marker} {item.name}{magic_label}",
                index=index,
                classes="selected-row" if selected == "▶" else "",
            )
            # AC info
            ac_str = f"AC {total_ac}" if magic_bonus == 0 else f"AC {base_ac}+{magic_bonus}={total_ac}"
            yield Static(f"  {ac_str} ({armor.armor_type.value})")

    def get_items(self) -> list:
        return getattr(self, "_armor_cache", [])


class ActionsPane(DashboardPanel):
    """Widget displaying actionable features."""

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(character=character, **kwargs)

    def compose(self) -> ComposeResult:
        yield Static("ACTIONS & FEATURES", classes="panel-title")
        actions = [f for f in self.character.features if f.uses or f.recharge]
        if not actions:
            yield Static("No tracked actions", classes="empty-state")
            return
        for feat in actions:
            uses = ""
            if feat.uses:
                remaining = max(0, feat.uses - feat.used)
                uses = f" [{remaining}/{feat.uses}]"
            yield Static(f"• {feat.name}{uses}")
