"""Spell management tool handlers."""

from typing import Any, Optional

from dnd_manager.models.character import Character


async def add_spell(
    character: Character,
    spell_name: str,
    list_type: str = "known",
) -> dict[str, Any]:
    """Add a spell to a spell list."""
    if list_type == "cantrips":
        target_list = character.spellcasting.cantrips
    elif list_type == "known":
        target_list = character.spellcasting.known
    elif list_type == "prepared":
        target_list = character.spellcasting.prepared
    else:
        raise ValueError(f"Unknown list type: {list_type}")

    if spell_name in target_list:
        return {
            "data": {
                "spell_name": spell_name,
                "list_type": list_type,
                "already_present": True,
            },
            "changes": [f"{spell_name} is already in {list_type}"],
        }

    target_list.append(spell_name)
    character.update_modified()

    return {
        "data": {
            "spell_name": spell_name,
            "list_type": list_type,
            "total_in_list": len(target_list),
        },
        "changes": [f"Added {spell_name} to {list_type}"],
    }


async def remove_spell(
    character: Character,
    spell_name: str,
    list_type: str = "prepared",
) -> dict[str, Any]:
    """Remove a spell from a spell list."""
    if list_type == "cantrips":
        target_list = character.spellcasting.cantrips
    elif list_type == "known":
        target_list = character.spellcasting.known
    elif list_type == "prepared":
        target_list = character.spellcasting.prepared
    else:
        raise ValueError(f"Unknown list type: {list_type}")

    if spell_name not in target_list:
        raise ValueError(f"Spell '{spell_name}' not found in {list_type}")

    target_list.remove(spell_name)
    character.update_modified()

    return {
        "data": {
            "spell_name": spell_name,
            "list_type": list_type,
            "remaining_in_list": len(target_list),
        },
        "changes": [f"Removed {spell_name} from {list_type}"],
    }


async def use_spell_slot(
    character: Character,
    level: int,
) -> dict[str, Any]:
    """Use a spell slot of a specific level."""
    if level not in character.spellcasting.slots:
        raise ValueError(f"No spell slots of level {level}")

    slot = character.spellcasting.slots[level]
    if slot.remaining <= 0:
        raise ValueError(f"No level {level} spell slots remaining")

    slot.use()
    character.update_modified()

    return {
        "data": {
            "level": level,
            "slots_remaining": slot.remaining,
            "slots_total": slot.total,
        },
        "changes": [f"Used level {level} spell slot ({slot.remaining}/{slot.total} remaining)"],
    }


async def restore_spell_slot(
    character: Character,
    level: int,
    count: int = 1,
) -> dict[str, Any]:
    """Restore spell slots of a specific level."""
    if level not in character.spellcasting.slots:
        raise ValueError(f"No spell slots of level {level}")

    slot = character.spellcasting.slots[level]
    old_remaining = slot.remaining

    for _ in range(count):
        slot.restore()

    actual_restored = slot.remaining - old_remaining
    character.update_modified()

    return {
        "data": {
            "level": level,
            "slots_restored": actual_restored,
            "slots_remaining": slot.remaining,
            "slots_total": slot.total,
        },
        "changes": [f"Restored {actual_restored} level {level} spell slot(s) ({slot.remaining}/{slot.total})"],
    }
