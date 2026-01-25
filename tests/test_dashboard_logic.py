"""Tests for dashboard helpers, alignment, and weapon mastery logic."""

from dnd_manager.app import CharacterCreationScreen, apply_item_order, is_weapon_proficient
from dnd_manager.data import get_weapon_by_name
from dnd_manager.data.weapon_mastery import (
    get_weapon_mastery_for_weapon,
    get_weapon_mastery_limit_for_class,
)
from dnd_manager.models.character import Alignment, Character, CharacterClass, RulesetId


def test_apply_item_order_preserves_unknowns_at_end():
    items = ["alpha", "beta", "gamma"]
    order = ["gamma", "alpha", "missing"]
    result = apply_item_order(items, order, lambda v: v)
    assert result[:2] == ["gamma", "alpha"]
    assert "beta" in result[2:]


def test_is_weapon_proficient_rogue_2024_limits_to_light_or_finesse():
    char = Character(primary_class=CharacterClass(name="Rogue", level=1))
    char.meta.ruleset = RulesetId.DND_2024
    char.proficiencies.weapons = ["Simple", "Martial"]

    longsword = get_weapon_by_name("Longsword")
    shortsword = get_weapon_by_name("Shortsword")
    dagger = get_weapon_by_name("Dagger")

    assert longsword is not None
    assert shortsword is not None
    assert dagger is not None

    assert is_weapon_proficient(char, longsword) is False
    assert is_weapon_proficient(char, shortsword) is True
    assert is_weapon_proficient(char, dagger) is True


def test_is_weapon_proficient_standard_rules():
    char = Character(primary_class=CharacterClass(name="Fighter", level=1))
    char.meta.ruleset = RulesetId.DND_2014
    char.proficiencies.weapons = ["Martial"]

    longsword = get_weapon_by_name("Longsword")
    dagger = get_weapon_by_name("Dagger")

    assert longsword is not None
    assert dagger is not None

    assert is_weapon_proficient(char, longsword) is True
    assert is_weapon_proficient(char, dagger) is False


def test_weapon_mastery_lookup_and_limits():
    assert get_weapon_mastery_for_weapon("Longsword") == "Sap"
    assert get_weapon_mastery_limit_for_class("Fighter", 1) == 3
    assert get_weapon_mastery_limit_for_class("Fighter", 10) == 5


def test_character_weapon_mastery_limit_and_usage():
    char = Character(primary_class=CharacterClass(name="Fighter", level=1))
    char.meta.ruleset = RulesetId.DND_2024
    assert char.get_weapon_mastery_limit() == 3

    char.weapon_masteries = ["Longsword"]
    assert char.can_use_weapon_mastery("Longsword") is True
    assert char.can_use_weapon_mastery("Dagger") is False


def test_alignment_step_updates_char_data():
    from unittest.mock import patch

    screen = CharacterCreationScreen()
    screen.step = screen.steps.index("alignment")
    options = [a.display_name for a in Alignment]
    screen.current_options = options
    target = Alignment.CHAOTIC_NEUTRAL
    screen.selected_option = options.index(target.display_name)

    # Mock UI methods that require DOM access
    with patch.object(screen, '_show_step'), patch.object(screen, '_save_draft'):
        screen.action_next()

    assert screen.char_data["alignment"] == target.value
