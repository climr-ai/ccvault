"""Query tool handlers (read-only operations)."""

from typing import Any, Optional

from dnd_manager.models.character import Character


async def get_character_summary(
    character: Character,
    include_equipment: bool = False,
    include_spells: bool = False,
) -> dict[str, Any]:
    """Get comprehensive character summary."""
    hp = character.combat.hit_points
    hd = character.combat.hit_dice

    summary = {
        "name": character.name,
        "class": character.primary_class.name,
        "subclass": character.primary_class.subclass,
        "level": character.total_level,
        "species": character.species,
        "background": character.background,
        "hp": {
            "current": hp.current,
            "maximum": hp.maximum,
            "temporary": hp.temporary,
        },
        "ac": character.combat.total_ac,
        "speed": character.combat.total_speed,
        "proficiency_bonus": character.proficiency_bonus,
        "hit_dice": {
            "remaining": hd.remaining,
            "total": hd.total,
            "die": hd.die,
        },
    }

    # Add multiclass info if applicable
    if character.multiclass:
        summary["multiclass"] = [
            {"name": mc.name, "level": mc.level, "subclass": mc.subclass}
            for mc in character.multiclass
        ]

    # Add equipment if requested
    if include_equipment:
        summary["equipped_items"] = [
            item.name for item in character.equipment.items if item.equipped
        ]
        summary["currency"] = {
            "cp": character.equipment.currency.cp,
            "sp": character.equipment.currency.sp,
            "ep": character.equipment.currency.ep,
            "gp": character.equipment.currency.gp,
            "pp": character.equipment.currency.pp,
        }

    # Add spells if requested
    if include_spells and character.spellcasting.ability:
        summary["spellcasting"] = {
            "ability": character.spellcasting.ability.value if character.spellcasting.ability else None,
            "spell_save_dc": character.get_spell_save_dc(),
            "spell_attack_bonus": character.get_spell_attack_bonus(),
            "cantrips": character.spellcasting.cantrips,
            "prepared": character.spellcasting.prepared[:10],  # Limit for readability
        }

    return {
        "data": summary,
        "changes": [],
    }


async def get_ability_scores(character: Character) -> dict[str, Any]:
    """Get all ability scores with modifiers."""
    abilities = {}
    for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        score = getattr(character.abilities, ability_name)
        abilities[ability_name] = {
            "base": score.base,
            "bonus": score.bonus,
            "total": score.total,
            "modifier": score.modifier,
        }

    return {
        "data": abilities,
        "changes": [],
    }


async def get_spell_slots(character: Character) -> dict[str, Any]:
    """Get current spell slot availability."""
    slots = {}
    spell_slots = character.spellcasting.slots if character.spellcasting and character.spellcasting.slots else {}
    for level, slot in spell_slots.items():
        slots[f"level_{level}"] = {
            "total": slot.total,
            "used": slot.used,
            "remaining": slot.remaining,
        }

    has_spellcasting = character.spellcasting and character.spellcasting.ability is not None

    return {
        "data": {
            "slots": slots,
            "has_spellcasting": has_spellcasting,
        },
        "changes": [],
    }


async def get_inventory(
    character: Character,
    filter_equipped: bool = False,
    filter_attuned: bool = False,
) -> dict[str, Any]:
    """Get character inventory."""
    items = character.equipment.items if character.equipment and character.equipment.items else []

    if filter_equipped:
        items = [i for i in items if i.equipped]
    if filter_attuned:
        items = [i for i in items if i.attuned]

    return {
        "data": {
            "items": [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "weight": item.weight,
                    "equipped": item.equipped,
                    "attuned": item.attuned,
                    "description": item.description,
                }
                for item in items
            ],
            "currency": {
                "cp": character.equipment.currency.cp,
                "sp": character.equipment.currency.sp,
                "ep": character.equipment.currency.ep,
                "gp": character.equipment.currency.gp,
                "pp": character.equipment.currency.pp,
                "total_gp": character.equipment.currency.total_gp,
            },
            "total_weight": character.equipment.total_weight,
            "attuned_count": character.equipment.attuned_count,
        },
        "changes": [],
    }


async def check_multiclass_requirements(
    character: Character,
    target_class: str,
) -> dict[str, Any]:
    """Check multiclass requirements for a class."""
    can_multiclass, reason = character.can_multiclass_into(target_class)

    return {
        "data": {
            "target_class": target_class,
            "can_multiclass": can_multiclass,
            "reason": reason,
            "current_level": character.total_level,
        },
        "changes": [],
    }
