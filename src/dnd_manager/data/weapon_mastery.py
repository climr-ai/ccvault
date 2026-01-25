"""Weapon mastery data for SRD 5.2 (2024).

Summaries are paraphrased to avoid copying SRD text verbatim.
"""

from __future__ import annotations

from typing import Optional


WEAPON_MASTERY_PROPERTIES = {
    "Cleave": "On a hit with a melee attack, you can strike a second nearby creature once per turn; the extra hit deals weapon damage without adding your ability modifier unless it is negative.",
    "Graze": "If you miss, you can still deal damage equal to the ability modifier used for the attack (minimum 0).",
    "Nick": "The extra Light-weapon attack can be made as part of the Attack action instead of using a Bonus Action (once per turn).",
    "Push": "On a hit, you can shove the target up to 10 feet straight away if it is Large or smaller.",
    "Sap": "On a hit, the target has disadvantage on its next attack roll before your next turn.",
    "Slow": "On a hit that deals damage, reduce the target's speed by 10 feet until your next turn (doesn't stack).",
    "Topple": "On a hit, the target makes a Constitution save (DC 8 + your proficiency bonus + attack ability modifier) or is knocked prone.",
    "Vex": "On a hit that deals damage, you gain advantage on your next attack against that target before your next turn ends.",
}


WEAPON_MASTERY_BY_WEAPON = {
    # Simple Melee
    "Club": "Slow",
    "Dagger": "Nick",
    "Greatclub": "Push",
    "Handaxe": "Vex",
    "Javelin": "Slow",
    "Light Hammer": "Nick",
    "Mace": "Sap",
    "Quarterstaff": "Topple",
    "Sickle": "Nick",
    "Spear": "Sap",
    # Simple Ranged
    "Dart": "Vex",
    "Light Crossbow": "Slow",
    "Shortbow": "Vex",
    "Sling": "Slow",
    # Martial Melee
    "Battleaxe": "Topple",
    "Flail": "Sap",
    "Glaive": "Graze",
    "Greataxe": "Cleave",
    "Greatsword": "Graze",
    "Halberd": "Cleave",
    "Lance": "Topple",
    "Longsword": "Sap",
    "Maul": "Topple",
    "Morningstar": "Sap",
    "Pike": "Push",
    "Rapier": "Vex",
    "Scimitar": "Nick",
    "Shortsword": "Vex",
    "Trident": "Topple",
    "Warhammer": "Push",
    "War Pick": "Sap",
    "Whip": "Slow",
    # Martial Ranged
    "Blowgun": "Vex",
    "Hand Crossbow": "Vex",
    "Heavy Crossbow": "Push",
    "Longbow": "Slow",
    "Musket": "Slow",
    "Pistol": "Vex",
}


WEAPON_MASTERY_PROGRESSIONS = {
    # class_name: list of (level_threshold, mastery_count)
    "Barbarian": [(1, 2), (4, 3), (10, 4)],
    "Fighter": [(1, 3), (4, 4), (10, 5), (16, 6)],
    "Paladin": [(1, 2)],
    "Ranger": [(1, 2)],
    "Rogue": [(1, 2)],
}


def get_weapon_mastery_for_weapon(name: str) -> Optional[str]:
    return WEAPON_MASTERY_BY_WEAPON.get(name)


def get_weapon_mastery_summary(property_name: str) -> Optional[str]:
    return WEAPON_MASTERY_PROPERTIES.get(property_name)


def get_weapon_mastery_limit_for_class(class_name: str, level: int) -> int:
    progression = WEAPON_MASTERY_PROGRESSIONS.get(class_name)
    if not progression:
        return 0
    limit = 0
    for threshold, count in progression:
        if level >= threshold:
            limit = count
    return limit

