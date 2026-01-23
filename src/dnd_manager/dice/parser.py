"""Dice notation parser for D&D-style dice expressions."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DiceParserError(ValueError):
    """Raised when dice notation parsing fails."""

    pass


class DiceLimitError(DiceParserError):
    """Raised when dice values exceed safety limits."""

    pass


# Safety limits to prevent resource exhaustion
MAX_DICE_COUNT = 100  # Maximum number of dice in a single group
MAX_DICE_SIDES = 1000  # Maximum sides on a die
MAX_FLAT_MODIFIER = 10000  # Maximum flat modifier (+/-)
MAX_MULTIPLIER = 10  # Maximum multiplier for crits
MAX_MODIFIER_VALUE = 100  # Maximum modifier value (e.g., keep highest N)


class DiceModifier(str, Enum):
    """Modifiers that can be applied to dice rolls."""

    KEEP_HIGHEST = "kh"  # Keep highest N dice
    KEEP_LOWEST = "kl"  # Keep lowest N dice
    DROP_HIGHEST = "dh"  # Drop highest N dice
    DROP_LOWEST = "dl"  # Drop lowest N dice
    REROLL_ONCE = "ro"  # Reroll dice once if below threshold
    REROLL = "rr"  # Reroll dice (recursive) if below threshold
    EXPLODE = "!"  # Exploding dice (roll again on max)


@dataclass
class DiceGroup:
    """A single group of dice (e.g., 2d6)."""

    count: int = 1  # Number of dice
    sides: int = 6  # Number of sides
    modifier: Optional[DiceModifier] = None
    modifier_value: Optional[int] = None  # e.g., keep highest 3

    def __str__(self) -> str:
        result = f"{self.count}d{self.sides}"
        if self.modifier:
            result += self.modifier.value
            if self.modifier_value is not None:
                result += str(self.modifier_value)
        return result


@dataclass
class DiceExpression:
    """A complete dice expression with multiple groups and flat modifiers."""

    groups: list[DiceGroup] = field(default_factory=list)
    flat_modifier: int = 0  # +5, -2, etc.
    multiplier: int = 1  # For critical damage (x2)
    original: str = ""  # Original expression string
    advantage: bool = False
    disadvantage: bool = False

    def __str__(self) -> str:
        parts = [str(g) for g in self.groups]
        if self.flat_modifier > 0:
            parts.append(f"+{self.flat_modifier}")
        elif self.flat_modifier < 0:
            parts.append(str(self.flat_modifier))
        result = "".join(parts)
        if self.multiplier > 1:
            result = f"({result})x{self.multiplier}"
        return result


# Regex patterns for parsing
DICE_PATTERN = re.compile(
    r"(\d+)?d(\d+)"  # NdX or dX (count optional, defaults to 1)
    r"(kh|kl|dh|dl|ro<|rr<|!)?(\d+)?"  # Optional modifier with value
)

MODIFIER_PATTERN = re.compile(r"([+-])(\d+)")


def parse_dice_notation(notation: str) -> DiceExpression:
    """Parse a dice notation string into a DiceExpression.

    Supported formats:
    - Basic: d20, 2d6, 4d6
    - Modifiers: 1d20+5, 2d6-2
    - Keep: 4d6kh3 (keep highest 3), 2d20kl1 (keep lowest 1)
    - Drop: 4d6dl1 (drop lowest 1)
    - Advantage: 2d20kh1, adv, advantage
    - Disadvantage: 2d20kl1, dis, disadvantage
    - Compound: 2d6+1d4+5
    - Multiply: (2d6+5)*2 for crits (simplified support)

    Args:
        notation: The dice notation string to parse

    Returns:
        A DiceExpression representing the parsed notation
    """
    original = notation
    notation = notation.lower().strip()

    # Handle shortcuts
    if notation in ("adv", "advantage"):
        return DiceExpression(
            groups=[DiceGroup(count=2, sides=20, modifier=DiceModifier.KEEP_HIGHEST, modifier_value=1)],
            original=original,
            advantage=True,
        )
    if notation in ("dis", "disadvantage"):
        return DiceExpression(
            groups=[DiceGroup(count=2, sides=20, modifier=DiceModifier.KEEP_LOWEST, modifier_value=1)],
            original=original,
            disadvantage=True,
        )
    if notation == "stats":
        # Return expression for rolling 4d6 drop lowest (for one ability score)
        return DiceExpression(
            groups=[DiceGroup(count=4, sides=6, modifier=DiceModifier.DROP_LOWEST, modifier_value=1)],
            original=original,
        )

    # Handle multiplier for critical damage
    multiplier = 1
    if notation.startswith("(") and ")*" in notation:
        # Extract multiplier
        mult_match = re.search(r"\)\*(\d+)", notation)
        if mult_match:
            multiplier = int(mult_match.group(1))
            if multiplier > MAX_MULTIPLIER:
                raise DiceLimitError(
                    f"Multiplier {multiplier} exceeds maximum of {MAX_MULTIPLIER}"
                )
            # Remove the multiplier wrapper
            notation = re.sub(r"^\(", "", notation)
            notation = re.sub(r"\)\*\d+$", "", notation)

    expression = DiceExpression(original=original, multiplier=multiplier)

    # Find all dice groups
    remaining = notation
    last_end = 0

    for match in DICE_PATTERN.finditer(notation):
        # Check for flat modifier before this dice group
        between = notation[last_end : match.start()]
        for mod_match in MODIFIER_PATTERN.finditer(between):
            sign = 1 if mod_match.group(1) == "+" else -1
            mod_value = int(mod_match.group(2))
            if mod_value > MAX_FLAT_MODIFIER:
                raise DiceLimitError(
                    f"Flat modifier {mod_value} exceeds maximum of {MAX_FLAT_MODIFIER}"
                )
            expression.flat_modifier += sign * mod_value

        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))

        # Validate dice count and sides
        if count > MAX_DICE_COUNT:
            raise DiceLimitError(
                f"Dice count {count} exceeds maximum of {MAX_DICE_COUNT}"
            )
        if count < 1:
            raise DiceParserError(f"Dice count must be at least 1, got {count}")
        if sides > MAX_DICE_SIDES:
            raise DiceLimitError(
                f"Dice sides {sides} exceeds maximum of {MAX_DICE_SIDES}"
            )
        if sides < 1:
            raise DiceParserError(f"Dice must have at least 1 side, got {sides}")

        modifier = None
        modifier_value = None

        if match.group(3):
            mod_str = match.group(3).rstrip("<")
            if mod_str == "kh":
                modifier = DiceModifier.KEEP_HIGHEST
            elif mod_str == "kl":
                modifier = DiceModifier.KEEP_LOWEST
            elif mod_str == "dh":
                modifier = DiceModifier.DROP_HIGHEST
            elif mod_str == "dl":
                modifier = DiceModifier.DROP_LOWEST
            elif mod_str == "ro":
                modifier = DiceModifier.REROLL_ONCE
            elif mod_str == "rr":
                modifier = DiceModifier.REROLL
            elif mod_str == "!":
                modifier = DiceModifier.EXPLODE

            if match.group(4):
                modifier_value = int(match.group(4))
                if modifier_value > MAX_MODIFIER_VALUE:
                    raise DiceLimitError(
                        f"Modifier value {modifier_value} exceeds maximum of {MAX_MODIFIER_VALUE}"
                    )
            elif modifier in (DiceModifier.KEEP_HIGHEST, DiceModifier.KEEP_LOWEST,
                            DiceModifier.DROP_HIGHEST, DiceModifier.DROP_LOWEST):
                modifier_value = 1  # Default to 1 for keep/drop

        expression.groups.append(
            DiceGroup(count=count, sides=sides, modifier=modifier, modifier_value=modifier_value)
        )
        last_end = match.end()

    # Check for trailing flat modifier
    remaining = notation[last_end:]
    for mod_match in MODIFIER_PATTERN.finditer(remaining):
        sign = 1 if mod_match.group(1) == "+" else -1
        mod_value = int(mod_match.group(2))
        if mod_value > MAX_FLAT_MODIFIER:
            raise DiceLimitError(
                f"Flat modifier {mod_value} exceeds maximum of {MAX_FLAT_MODIFIER}"
            )
        expression.flat_modifier += sign * mod_value

    # Detect advantage/disadvantage from expression
    if len(expression.groups) == 1:
        g = expression.groups[0]
        if g.count == 2 and g.sides == 20:
            if g.modifier == DiceModifier.KEEP_HIGHEST:
                expression.advantage = True
            elif g.modifier == DiceModifier.KEEP_LOWEST:
                expression.disadvantage = True

    return expression


def is_valid_dice_notation(notation: str) -> bool:
    """Check if a string is valid dice notation.

    Returns True only if the notation is both syntactically valid and within
    safety limits. Returns False for invalid syntax, limit violations, or
    empty expressions.
    """
    try:
        expr = parse_dice_notation(notation)
        return len(expr.groups) > 0
    except (DiceParserError, ValueError, TypeError):
        return False
