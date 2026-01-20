"""Custom stat and personality tool handlers."""

from datetime import datetime
from typing import Any, Optional

from dnd_manager.models.character import Character, CustomStat, Note


async def modify_custom_stat(
    character: Character,
    stat_name: str,
    amount: Optional[int] = None,
    set_value: Optional[int] = None,
) -> dict[str, Any]:
    """Modify a custom campaign stat."""
    # Find existing stat
    stat = next(
        (s for s in character.custom_stats if s.name.lower() == stat_name.lower()),
        None
    )

    if stat is None:
        # Create new stat
        initial_value = set_value if set_value is not None else (amount or 0)
        stat = CustomStat(name=stat_name, value=initial_value)
        character.custom_stats.append(stat)
        changes = [f"Created custom stat '{stat_name}' with value {initial_value}"]
    else:
        old_value = stat.value
        if set_value is not None:
            # Set to specific value
            stat.value = set_value
            if stat.min_value is not None:
                stat.value = max(stat.min_value, stat.value)
            if stat.max_value is not None:
                stat.value = min(stat.max_value, stat.value)
            changes = [f"Set {stat_name} from {old_value} to {stat.value}"]
        elif amount is not None:
            # Adjust by amount
            stat.adjust(amount)
            changes = [f"Adjusted {stat_name} by {amount:+d} (now {stat.value})"]
        else:
            changes = [f"{stat_name} unchanged (no amount or set_value provided)"]

    character.update_modified()

    return {
        "data": {
            "stat_name": stat.name,
            "value": stat.value,
            "min_value": stat.min_value,
            "max_value": stat.max_value,
        },
        "changes": changes,
    }


async def add_note(
    character: Character,
    title: str,
    content: str,
    tags: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Add a note to the character."""
    note = Note(
        title=title,
        content=content,
        tags=tags or [],
        created=datetime.now(),
    )

    character.notes.append(note)
    character.update_modified()

    return {
        "data": {
            "title": title,
            "tags": tags or [],
            "total_notes": len(character.notes),
        },
        "changes": [f"Added note: {title}"],
    }


async def set_personality_trait(
    character: Character,
    trait_type: str,
    value: str,
    action: str = "add",
) -> dict[str, Any]:
    """Set or add a personality trait."""
    personality = character.personality

    if trait_type == "trait":
        target_list = personality.traits
    elif trait_type == "ideal":
        target_list = personality.ideals
    elif trait_type == "bond":
        target_list = personality.bonds
    elif trait_type == "flaw":
        target_list = personality.flaws
    else:
        raise ValueError(f"Unknown trait type: {trait_type}")

    if action == "replace":
        target_list.clear()

    if value not in target_list:
        target_list.append(value)

    character.update_modified()

    return {
        "data": {
            "trait_type": trait_type,
            "value": value,
            "action": action,
            "all_values": list(target_list),
        },
        "changes": [
            f"{'Replaced all with' if action == 'replace' else 'Added'} {trait_type}: {value}"
        ],
    }
