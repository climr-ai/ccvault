"""Tests for equipment-derived combat stats and item state."""

from dnd_manager.data import get_armor_by_name
from dnd_manager.models.character import AbilityScores, Character, CharacterClass, InventoryItem
from dnd_manager.models.abilities import AbilityScore


def _set_dex(character: Character, score: int) -> None:
    character.abilities.dexterity = AbilityScore(base=score)


def _expected_ac_for_armor(character: Character, armor_name: str, shield_name: str | None = None) -> int:
    armor = get_armor_by_name(armor_name)
    assert armor is not None
    dex_mod = character.abilities.dexterity.modifier
    if armor.armor_type.value == "Heavy":
        dex_bonus = 0
    elif armor.armor_type.value == "Medium":
        dex_bonus = min(dex_mod, armor.max_dex_bonus or 0)
    else:
        dex_bonus = dex_mod
    ac = armor.base_ac + dex_bonus
    if shield_name:
        shield = get_armor_by_name(shield_name)
        assert shield is not None
        ac += shield.base_ac
    return ac


def test_apply_equipment_effects_no_armor_uses_dex():
    char = Character(primary_class=CharacterClass(name="Fighter", level=1))
    _set_dex(char, 14)  # +2
    char.apply_equipment_effects()
    assert char.combat.armor_class == 12


def test_apply_equipment_effects_light_armor_and_shield():
    char = Character(primary_class=CharacterClass(name="Fighter", level=1))
    _set_dex(char, 16)  # +3
    char.equipment.items = [
        InventoryItem(name="Leather", equipped=True),
        InventoryItem(name="Shield", equipped=True),
    ]
    char.apply_equipment_effects()
    assert char.combat.armor_class == _expected_ac_for_armor(char, "Leather", "Shield")


def test_apply_equipment_effects_heavy_ignores_dex():
    char = Character(primary_class=CharacterClass(name="Fighter", level=1))
    _set_dex(char, 18)  # +4, should be ignored
    char.equipment.items = [
        InventoryItem(name="Chain Mail", equipped=True),
    ]
    char.apply_equipment_effects()
    assert char.combat.armor_class == _expected_ac_for_armor(char, "Chain Mail")
