"""Combat tool handlers."""

from typing import Any, Optional

from dnd_manager.models.character import Character


async def deal_damage(
    character: Character,
    amount: int,
    damage_type: Optional[str] = None,
    source: Optional[str] = None,
) -> dict[str, Any]:
    """Apply damage to character."""
    old_hp = character.combat.hit_points.current
    old_temp = character.combat.hit_points.temporary

    character.take_damage(amount)

    new_hp = character.combat.hit_points.current
    new_temp = character.combat.hit_points.temporary

    changes = []
    temp_absorbed = old_temp - new_temp
    if temp_absorbed > 0:
        changes.append(f"Absorbed {temp_absorbed} damage with temporary HP")
    hp_damage = old_hp - new_hp
    if hp_damage > 0:
        changes.append(f"Took {hp_damage} damage to HP")

    source_str = f" from {source}" if source else ""
    damage_str = f" {damage_type}" if damage_type else ""

    return {
        "data": {
            "previous_hp": old_hp,
            "current_hp": new_hp,
            "maximum_hp": character.combat.hit_points.maximum,
            "damage_dealt": amount,
            "damage_type": damage_type,
            "source": source,
            "is_unconscious": character.combat.hit_points.is_unconscious,
            "is_bloodied": character.combat.hit_points.is_bloodied,
        },
        "changes": changes or [f"Dealt {amount}{damage_str} damage{source_str}"],
    }


async def heal_character(
    character: Character,
    amount: int,
    source: Optional[str] = None,
) -> dict[str, Any]:
    """Heal the character."""
    old_hp = character.combat.hit_points.current
    was_unconscious = character.combat.hit_points.is_unconscious

    character.heal(amount)

    new_hp = character.combat.hit_points.current
    actual_healed = new_hp - old_hp

    changes = [f"Healed {actual_healed} HP"]
    if was_unconscious and not character.combat.hit_points.is_unconscious:
        changes.append("Character regained consciousness")
        changes.append("Death saves reset")

    return {
        "data": {
            "previous_hp": old_hp,
            "current_hp": new_hp,
            "maximum_hp": character.combat.hit_points.maximum,
            "amount_healed": actual_healed,
            "source": source,
        },
        "changes": changes,
    }


async def take_short_rest(character: Character) -> dict[str, Any]:
    """Apply short rest effects."""
    # Track restored features
    restored_features = []
    for feature in character.features:
        if feature.uses and feature.recharge in ("short rest", "short_rest"):
            if feature.used > 0:
                restored_features.append(feature.name)

    character.short_rest()

    return {
        "data": {
            "features_restored": restored_features,
            "hit_dice_available": character.combat.hit_dice.remaining,
        },
        "changes": [
            f"Restored {len(restored_features)} short-rest features"
            if restored_features else "Short rest completed",
        ],
    }


async def take_long_rest(character: Character) -> dict[str, Any]:
    """Apply long rest effects."""
    old_hp = character.combat.hit_points.current
    old_hd = character.combat.hit_dice.remaining

    character.long_rest()

    hp_restored = character.combat.hit_points.current - old_hp
    hd_restored = character.combat.hit_dice.remaining - old_hd

    return {
        "data": {
            "hp_restored": hp_restored,
            "hit_dice_restored": hd_restored,
            "current_hp": character.combat.hit_points.current,
            "hit_dice_remaining": character.combat.hit_dice.remaining,
            "spell_slots_restored": True,
        },
        "changes": [
            f"Restored HP to maximum ({character.combat.hit_points.maximum})",
            f"Restored {hd_restored} hit dice",
            "Restored all spell slots",
            "Reset death saves",
        ],
    }


async def spend_hit_die(
    character: Character,
    die_type: Optional[str] = None,
    count: int = 1,
) -> dict[str, Any]:
    """Spend hit dice to heal."""
    from dnd_manager.dice import DiceRoller

    roller = DiceRoller()
    pool = character.combat.hit_dice_pool
    hd = character.combat.hit_dice
    con_mod = character.abilities.constitution.modifier

    total_healed = 0
    dice_spent = []

    for _ in range(count):
        # Get die to spend
        if pool and pool.pools:
            # Multiclass: use pool
            if die_type:
                if not pool.spend(die_type):
                    break
                spent_die = die_type
            else:
                spent_die = pool.spend_any()
                if not spent_die:
                    break
        else:
            # Single class: use simple tracking
            if hd.remaining <= 0:
                break
            hd.remaining -= 1
            spent_die = hd.die

        # Roll the hit die
        roll_result = roller.roll(f"1{spent_die}")
        healing = max(1, roll_result.total + con_mod)
        total_healed += healing
        dice_spent.append({
            "die": spent_die,
            "roll": roll_result.total,
            "con_mod": con_mod,
            "healing": healing,
        })

    # Apply healing
    if total_healed > 0:
        character.heal(total_healed)

    # Sync hit dice if using pool
    if pool and pool.pools:
        character.combat.hit_dice = pool.to_single()

    return {
        "data": {
            "dice_spent": len(dice_spent),
            "rolls": dice_spent,
            "total_healed": total_healed,
            "current_hp": character.combat.hit_points.current,
            "hit_dice_remaining": pool.remaining if (pool and pool.pools) else hd.remaining,
        },
        "changes": [
            f"Spent {len(dice_spent)} hit dice",
            f"Healed {total_healed} HP",
        ] if dice_spent else ["No hit dice available to spend"],
    }


async def modify_death_saves(
    character: Character,
    action: str,
) -> dict[str, Any]:
    """Modify death saving throws."""
    ds = character.combat.death_saves
    old_successes = ds.successes
    old_failures = ds.failures

    if action == "add_success":
        ds.successes = min(3, ds.successes + 1)
    elif action == "add_failure":
        ds.failures = min(3, ds.failures + 1)
    elif action == "add_crit_success":
        # Nat 20: regain 1 HP, reset death saves
        character.heal(1)
        ds.reset()
    elif action == "add_crit_failure":
        # Nat 1: counts as 2 failures
        ds.failures = min(3, ds.failures + 2)
    elif action == "reset":
        ds.reset()

    character.update_modified()

    return {
        "data": {
            "successes": ds.successes,
            "failures": ds.failures,
            "is_stable": ds.is_stable,
            "is_dead": ds.is_dead,
            "action_taken": action,
        },
        "changes": [
            f"Death saves: {ds.successes} successes, {ds.failures} failures"
            + (" (STABLE)" if ds.is_stable else "")
            + (" (DEAD)" if ds.is_dead else "")
        ],
    }
