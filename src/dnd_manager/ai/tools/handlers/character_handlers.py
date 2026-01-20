"""Character modification tool handlers."""

from typing import Any, Optional

from dnd_manager.models.character import Character, CharacterClass, Feature, StatBonus


async def set_ability_score(
    character: Character,
    ability: str,
    value: int,
) -> dict[str, Any]:
    """Set base ability score."""
    score = getattr(character.abilities, ability)
    old_value = score.base
    old_total = score.total

    score.base = value
    character.update_modified()

    new_total = score.total

    return {
        "data": {
            "ability": ability,
            "old_base": old_value,
            "new_base": value,
            "old_total": old_total,
            "new_total": new_total,
            "new_modifier": score.modifier,
        },
        "changes": [
            f"Set {ability.title()} base from {old_value} to {value}",
            f"New total: {new_total} (modifier: {score.modifier:+d})",
        ],
    }


async def add_ability_bonus(
    character: Character,
    ability: str,
    bonus: int,
    source: str,
    is_override: bool = False,
    override_value: Optional[int] = None,
) -> dict[str, Any]:
    """Add tracked bonus to ability score."""
    stat_bonus = StatBonus(
        source=source,
        ability=ability,
        bonus=bonus,
        is_override=is_override,
        override_value=override_value,
    )

    character.stat_bonuses.append(stat_bonus)
    character.update_modified()

    score = getattr(character.abilities, ability)

    return {
        "data": {
            "ability": ability,
            "bonus_added": bonus,
            "source": source,
            "is_override": is_override,
            "override_value": override_value,
            "current_total": score.total,
            "current_modifier": score.modifier,
        },
        "changes": [
            f"Added {bonus:+d} to {ability.title()} from {source}"
            if not is_override else
            f"Set {ability.title()} to {override_value} from {source}",
        ],
    }


async def level_up(
    character: Character,
    class_name: Optional[str] = None,
    hp_method: str = "average",
) -> dict[str, Any]:
    """Level up the character."""
    target_class = class_name or character.primary_class.name
    old_level = character.total_level

    # Check level cap
    if old_level >= 20:
        raise ValueError("Character is already at maximum level (20)")

    # Check multiclass requirements if different from primary
    if target_class != character.primary_class.name:
        can_mc, reason = character.can_multiclass_into(target_class, enforce=True)
        if not can_mc:
            raise ValueError(f"Cannot multiclass: {reason}")

    # Get hit die for the class
    ruleset = character.get_ruleset()
    if ruleset:
        class_def = ruleset.get_class_definition(target_class)
        hit_die = class_def.hit_die if class_def else 8
    else:
        # Default hit dice by class
        hit_dice = {
            "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
            "Bard": 8, "Cleric": 8, "Druid": 8, "Monk": 8, "Rogue": 8, "Warlock": 8,
            "Sorcerer": 6, "Wizard": 6,
        }
        hit_die = hit_dice.get(target_class, 8)

    # Calculate HP gain
    con_mod = character.abilities.constitution.modifier
    if hp_method == "max":
        hp_gain = hit_die + con_mod
    else:  # average
        hp_gain = (hit_die // 2) + 1 + con_mod
    hp_gain = max(1, hp_gain)

    # Apply level up
    if target_class == character.primary_class.name:
        character.primary_class.level += 1
    else:
        # Find or create multiclass entry
        mc_entry = next(
            (mc for mc in character.multiclass if mc.name == target_class),
            None
        )
        if mc_entry:
            mc_entry.level += 1
        else:
            character.multiclass.append(CharacterClass(name=target_class, level=1))

    # Apply HP
    character.combat.hit_points.maximum += hp_gain
    character.combat.hit_points.current += hp_gain

    # Sync everything
    character.sync_with_ruleset(recalc_hp=False)

    return {
        "data": {
            "old_level": old_level,
            "new_level": character.total_level,
            "class_leveled": target_class,
            "hp_gained": hp_gain,
            "new_max_hp": character.combat.hit_points.maximum,
        },
        "changes": [
            f"Leveled up to {target_class} {character.get_class_levels().get(target_class, 1)}",
            f"Total level: {character.total_level}",
            f"Gained {hp_gain} HP (now {character.combat.hit_points.maximum} max)",
        ],
    }


async def add_feature(
    character: Character,
    name: str,
    source: str,
    description: str,
    uses: Optional[int] = None,
    recharge: Optional[str] = None,
) -> dict[str, Any]:
    """Add a feature to the character."""
    feature = Feature(
        name=name,
        source=source,
        description=description,
        uses=uses,
        used=0,
        recharge=recharge,
    )

    character.features.append(feature)
    character.update_modified()

    return {
        "data": {
            "name": name,
            "source": source,
            "uses": uses,
            "recharge": recharge,
            "total_features": len(character.features),
        },
        "changes": [f"Added feature: {name} ({source})"],
    }


async def remove_feature(
    character: Character,
    name: str,
) -> dict[str, Any]:
    """Remove a feature by name."""
    original_count = len(character.features)
    character.features = [f for f in character.features if f.name != name]
    removed = original_count - len(character.features)

    if removed == 0:
        raise ValueError(f"Feature '{name}' not found")

    character.update_modified()

    return {
        "data": {
            "name": name,
            "removed_count": removed,
            "remaining_features": len(character.features),
        },
        "changes": [f"Removed feature: {name}"],
    }
