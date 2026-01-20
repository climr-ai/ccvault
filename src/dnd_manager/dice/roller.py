"""Dice roller implementation for D&D 5e."""

import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from dnd_manager.dice.parser import DiceExpression, DiceGroup, DiceModifier, parse_dice_notation


@dataclass
class SingleDieResult:
    """Result of rolling a single die."""

    value: int
    kept: bool = True  # Whether this die was kept (not dropped)
    rerolled: bool = False  # Whether this die was rerolled
    exploded: bool = False  # Whether this die caused an explosion


@dataclass
class GroupResult:
    """Result of rolling a dice group."""

    group: DiceGroup
    rolls: list[SingleDieResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Sum of kept dice."""
        return sum(r.value for r in self.rolls if r.kept)

    @property
    def all_rolls(self) -> list[int]:
        """All roll values."""
        return [r.value for r in self.rolls]

    @property
    def kept_rolls(self) -> list[int]:
        """Values of kept dice only."""
        return [r.value for r in self.rolls if r.kept]

    def __str__(self) -> str:
        parts = []
        for r in self.rolls:
            val = str(r.value)
            if not r.kept:
                val = f"~~{val}~~"
            elif r.rerolled:
                val = f"*{val}"
            elif r.exploded:
                val = f"{val}!"
            parts.append(val)
        return f"[{', '.join(parts)}]"


@dataclass
class RollResult:
    """Complete result of a dice roll."""

    expression: DiceExpression
    group_results: list[GroupResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    label: Optional[str] = None  # e.g., "Attack Roll", "Fireball Damage"
    natural_20: bool = False  # For d20 rolls
    natural_1: bool = False  # For d20 rolls

    @property
    def subtotal(self) -> int:
        """Sum of all groups before multiplier."""
        return sum(g.total for g in self.group_results) + self.expression.flat_modifier

    @property
    def total(self) -> int:
        """Final total with multiplier."""
        return self.subtotal * self.expression.multiplier

    def __str__(self) -> str:
        parts = []
        for gr in self.group_results:
            parts.append(f"{gr.group}: {gr}")
        result = " + ".join(parts)
        if self.expression.flat_modifier:
            if self.expression.flat_modifier > 0:
                result += f" + {self.expression.flat_modifier}"
            else:
                result += f" - {abs(self.expression.flat_modifier)}"
        if self.expression.multiplier > 1:
            result = f"({result}) x {self.expression.multiplier}"
        result += f" = {self.total}"

        if self.natural_20:
            result += " (NAT 20!)"
        elif self.natural_1:
            result += " (NAT 1)"

        return result


class DiceRoller:
    """Dice rolling engine with support for D&D 5e mechanics."""

    def __init__(self, rng: Optional[random.Random] = None):
        """Initialize the roller.

        Args:
            rng: Optional random number generator for reproducible rolls
        """
        self.rng = rng or random.Random()
        self.history: list[RollResult] = []
        self.max_history = 100

    def roll(self, notation: str, label: Optional[str] = None) -> RollResult:
        """Roll dice using standard notation.

        Args:
            notation: Dice notation string (e.g., "2d6+5", "4d6kh3")
            label: Optional label for the roll

        Returns:
            RollResult with all details
        """
        expression = parse_dice_notation(notation)
        return self.roll_expression(expression, label)

    def roll_expression(
        self, expression: DiceExpression, label: Optional[str] = None
    ) -> RollResult:
        """Roll a parsed dice expression.

        Args:
            expression: The parsed DiceExpression
            label: Optional label for the roll

        Returns:
            RollResult with all details
        """
        result = RollResult(expression=expression, label=label)

        for group in expression.groups:
            group_result = self._roll_group(group)
            result.group_results.append(group_result)

        # Check for natural 20/1 on d20 rolls
        if len(expression.groups) == 1:
            g = expression.groups[0]
            gr = result.group_results[0]
            if g.sides == 20 and len(gr.kept_rolls) == 1:
                kept_value = gr.kept_rolls[0]
                if kept_value == 20:
                    result.natural_20 = True
                elif kept_value == 1:
                    result.natural_1 = True

        # Add to history
        self.history.append(result)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

        return result

    def _roll_group(self, group: DiceGroup) -> GroupResult:
        """Roll a single dice group."""
        result = GroupResult(group=group)
        rolls: list[SingleDieResult] = []

        # Initial rolls
        for _ in range(group.count):
            value = self._roll_die(group.sides)
            rolls.append(SingleDieResult(value=value))

        # Handle exploding dice
        if group.modifier == DiceModifier.EXPLODE:
            i = 0
            while i < len(rolls):
                if rolls[i].value == group.sides:
                    rolls[i].exploded = True
                    new_roll = self._roll_die(group.sides)
                    rolls.append(SingleDieResult(value=new_roll))
                i += 1

        # Handle reroll once (ro<N)
        if group.modifier == DiceModifier.REROLL_ONCE and group.modifier_value:
            threshold = group.modifier_value
            for r in rolls:
                if r.value < threshold:
                    r.rerolled = True
                    r.value = self._roll_die(group.sides)

        # Handle reroll recursive (rr<N)
        if group.modifier == DiceModifier.REROLL and group.modifier_value:
            threshold = group.modifier_value
            for r in rolls:
                while r.value < threshold:
                    r.rerolled = True
                    r.value = self._roll_die(group.sides)

        # Handle keep highest
        if group.modifier == DiceModifier.KEEP_HIGHEST and group.modifier_value:
            keep_count = group.modifier_value
            sorted_rolls = sorted(rolls, key=lambda r: r.value, reverse=True)
            for i, r in enumerate(sorted_rolls):
                r.kept = i < keep_count

        # Handle keep lowest
        if group.modifier == DiceModifier.KEEP_LOWEST and group.modifier_value:
            keep_count = group.modifier_value
            sorted_rolls = sorted(rolls, key=lambda r: r.value)
            for i, r in enumerate(sorted_rolls):
                r.kept = i < keep_count

        # Handle drop highest
        if group.modifier == DiceModifier.DROP_HIGHEST and group.modifier_value:
            drop_count = group.modifier_value
            sorted_rolls = sorted(rolls, key=lambda r: r.value, reverse=True)
            for i, r in enumerate(sorted_rolls):
                r.kept = i >= drop_count

        # Handle drop lowest
        if group.modifier == DiceModifier.DROP_LOWEST and group.modifier_value:
            drop_count = group.modifier_value
            sorted_rolls = sorted(rolls, key=lambda r: r.value)
            for i, r in enumerate(sorted_rolls):
                r.kept = i >= drop_count

        result.rolls = rolls
        return result

    def _roll_die(self, sides: int) -> int:
        """Roll a single die."""
        return self.rng.randint(1, sides)

    # Convenience methods for common D&D rolls

    def d20(self, modifier: int = 0, advantage: bool = False, disadvantage: bool = False) -> RollResult:
        """Roll a d20 with optional modifier and advantage/disadvantage."""
        if advantage and not disadvantage:
            result = self.roll("2d20kh1")
        elif disadvantage and not advantage:
            result = self.roll("2d20kl1")
        else:
            result = self.roll("1d20")

        result.expression.flat_modifier = modifier
        return result

    def attack(self, modifier: int, advantage: bool = False, disadvantage: bool = False) -> RollResult:
        """Make an attack roll."""
        result = self.d20(modifier, advantage, disadvantage)
        result.label = "Attack Roll"
        return result

    def damage(self, notation: str, critical: bool = False) -> RollResult:
        """Roll damage, optionally as a critical hit."""
        if critical:
            # Double the dice (not the modifier)
            expr = parse_dice_notation(notation)
            for group in expr.groups:
                group.count *= 2
            result = self.roll_expression(expr)
        else:
            result = self.roll(notation)
        result.label = "Damage" + (" (Critical!)" if critical else "")
        return result

    def saving_throw(self, modifier: int, advantage: bool = False, disadvantage: bool = False) -> RollResult:
        """Roll a saving throw."""
        result = self.d20(modifier, advantage, disadvantage)
        result.label = "Saving Throw"
        return result

    def ability_check(self, modifier: int, advantage: bool = False, disadvantage: bool = False) -> RollResult:
        """Roll an ability check."""
        result = self.d20(modifier, advantage, disadvantage)
        result.label = "Ability Check"
        return result

    def ability_scores(self) -> list[RollResult]:
        """Roll 4d6 drop lowest 6 times for ability scores."""
        results = []
        for i in range(6):
            result = self.roll("4d6dl1", label=f"Ability Score {i + 1}")
            results.append(result)
        return results

    def clear_history(self) -> None:
        """Clear roll history."""
        self.history.clear()


# Global default roller
_default_roller: Optional[DiceRoller] = None


def get_roller() -> DiceRoller:
    """Get the default dice roller instance."""
    global _default_roller
    if _default_roller is None:
        _default_roller = DiceRoller()
    return _default_roller


def roll(notation: str, label: Optional[str] = None) -> RollResult:
    """Quick roll using the default roller."""
    return get_roller().roll(notation, label)
