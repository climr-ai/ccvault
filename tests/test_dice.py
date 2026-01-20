"""Tests for dice rolling system."""

import random
import pytest

from dnd_manager.dice import parse_dice_notation, DiceRoller, RollResult
from dnd_manager.dice.parser import DiceModifier, DiceExpression, is_valid_dice_notation


class TestDiceParser:
    """Tests for dice notation parsing."""

    def test_simple_dice(self):
        """Test parsing simple dice notation."""
        expr = parse_dice_notation("1d20")
        assert len(expr.groups) == 1
        assert expr.groups[0].count == 1
        assert expr.groups[0].sides == 20

    def test_implicit_count(self):
        """Test parsing dice without count (d20 = 1d20)."""
        expr = parse_dice_notation("d20")
        assert expr.groups[0].count == 1
        assert expr.groups[0].sides == 20

    def test_multiple_dice(self):
        """Test parsing multiple dice."""
        expr = parse_dice_notation("4d6")
        assert expr.groups[0].count == 4
        assert expr.groups[0].sides == 6

    def test_with_modifier(self):
        """Test parsing dice with flat modifier."""
        expr = parse_dice_notation("1d20+5")
        assert expr.groups[0].count == 1
        assert expr.groups[0].sides == 20
        assert expr.flat_modifier == 5

    def test_with_negative_modifier(self):
        """Test parsing dice with negative modifier."""
        expr = parse_dice_notation("1d20-3")
        assert expr.flat_modifier == -3

    def test_keep_highest(self):
        """Test parsing keep highest notation."""
        expr = parse_dice_notation("4d6kh3")
        assert expr.groups[0].count == 4
        assert expr.groups[0].modifier == DiceModifier.KEEP_HIGHEST
        assert expr.groups[0].modifier_value == 3

    def test_drop_lowest(self):
        """Test parsing drop lowest notation."""
        expr = parse_dice_notation("4d6dl1")
        assert expr.groups[0].modifier == DiceModifier.DROP_LOWEST
        assert expr.groups[0].modifier_value == 1

    def test_advantage_shortcut(self):
        """Test advantage shortcut."""
        expr = parse_dice_notation("adv")
        assert expr.advantage is True
        assert expr.groups[0].count == 2
        assert expr.groups[0].sides == 20
        assert expr.groups[0].modifier == DiceModifier.KEEP_HIGHEST

    def test_disadvantage_shortcut(self):
        """Test disadvantage shortcut."""
        expr = parse_dice_notation("dis")
        assert expr.disadvantage is True
        assert expr.groups[0].modifier == DiceModifier.KEEP_LOWEST

    def test_stats_shortcut(self):
        """Test stats shortcut (4d6 drop lowest)."""
        expr = parse_dice_notation("stats")
        assert expr.groups[0].count == 4
        assert expr.groups[0].sides == 6
        assert expr.groups[0].modifier == DiceModifier.DROP_LOWEST

    def test_compound_expression(self):
        """Test compound dice expression."""
        expr = parse_dice_notation("2d6+1d4+5")
        assert len(expr.groups) == 2
        assert expr.groups[0].count == 2
        assert expr.groups[0].sides == 6
        assert expr.groups[1].count == 1
        assert expr.groups[1].sides == 4
        assert expr.flat_modifier == 5

    def test_is_valid_dice_notation(self):
        """Test validation function."""
        assert is_valid_dice_notation("1d20")
        assert is_valid_dice_notation("4d6kh3")
        assert is_valid_dice_notation("2d6+5")
        assert not is_valid_dice_notation("hello")
        assert not is_valid_dice_notation("")


class TestDiceRoller:
    """Tests for dice rolling."""

    @pytest.fixture
    def seeded_roller(self):
        """Create a roller with a seeded RNG for reproducible tests."""
        return DiceRoller(rng=random.Random(42))

    def test_basic_roll(self, seeded_roller):
        """Test basic dice roll."""
        result = seeded_roller.roll("1d20")
        assert 1 <= result.total <= 20
        assert len(result.group_results) == 1

    def test_roll_with_modifier(self, seeded_roller):
        """Test roll with modifier."""
        result = seeded_roller.roll("1d20+5")
        # Total includes the +5 modifier
        assert result.expression.flat_modifier == 5

    def test_roll_multiple_dice(self, seeded_roller):
        """Test rolling multiple dice."""
        result = seeded_roller.roll("3d6")
        assert len(result.group_results[0].rolls) == 3
        assert 3 <= result.total <= 18

    def test_keep_highest(self, seeded_roller):
        """Test keep highest mechanic."""
        result = seeded_roller.roll("4d6kh3")
        rolls = result.group_results[0].rolls

        # Should have 4 rolls
        assert len(rolls) == 4

        # Should have 3 kept
        kept = [r for r in rolls if r.kept]
        dropped = [r for r in rolls if not r.kept]
        assert len(kept) == 3
        assert len(dropped) == 1

        # Dropped should be the lowest
        assert all(k.value >= dropped[0].value for k in kept)

    def test_drop_lowest(self, seeded_roller):
        """Test drop lowest mechanic."""
        result = seeded_roller.roll("4d6dl1")
        rolls = result.group_results[0].rolls

        kept = [r for r in rolls if r.kept]
        assert len(kept) == 3

    def test_advantage(self, seeded_roller):
        """Test advantage roll."""
        result = seeded_roller.roll("adv")
        assert result.expression.advantage is True
        assert len(result.group_results[0].rolls) == 2
        kept = [r for r in result.group_results[0].rolls if r.kept]
        assert len(kept) == 1

    def test_disadvantage(self, seeded_roller):
        """Test disadvantage roll."""
        result = seeded_roller.roll("dis")
        assert result.expression.disadvantage is True

    def test_natural_20_detection(self):
        """Test natural 20 detection."""
        # Create roller that always rolls 20
        class Fixed20Roller(DiceRoller):
            def _roll_die(self, sides: int) -> int:
                return 20

        roller = Fixed20Roller()
        result = roller.roll("1d20")
        assert result.natural_20 is True
        assert result.natural_1 is False

    def test_natural_1_detection(self):
        """Test natural 1 detection."""
        class Fixed1Roller(DiceRoller):
            def _roll_die(self, sides: int) -> int:
                return 1

        roller = Fixed1Roller()
        result = roller.roll("1d20")
        assert result.natural_1 is True
        assert result.natural_20 is False

    def test_history(self, seeded_roller):
        """Test roll history tracking."""
        seeded_roller.roll("1d20")
        seeded_roller.roll("2d6")
        assert len(seeded_roller.history) == 2

        seeded_roller.clear_history()
        assert len(seeded_roller.history) == 0

    def test_attack_roll(self, seeded_roller):
        """Test attack roll convenience method."""
        result = seeded_roller.attack(5)
        assert result.label == "Attack Roll"
        assert result.expression.flat_modifier == 5

    def test_damage_roll(self, seeded_roller):
        """Test damage roll."""
        result = seeded_roller.damage("2d6+3")
        assert result.label == "Damage"
        assert 5 <= result.total <= 15

    def test_critical_damage(self, seeded_roller):
        """Test critical damage doubles dice."""
        result = seeded_roller.damage("2d6+3", critical=True)
        assert "Critical" in result.label
        # Should have rolled 4 dice (2x2d6)
        assert len(result.group_results[0].rolls) == 4

    def test_ability_scores(self, seeded_roller):
        """Test ability score generation."""
        results = seeded_roller.ability_scores()
        assert len(results) == 6
        for r in results:
            assert 3 <= r.total <= 18

    def test_compound_roll(self, seeded_roller):
        """Test compound dice expression."""
        result = seeded_roller.roll("2d6+1d4+5")
        assert len(result.group_results) == 2


class TestRollResult:
    """Tests for RollResult formatting."""

    def test_result_string(self):
        """Test result string formatting."""
        roller = DiceRoller(rng=random.Random(42))
        result = roller.roll("2d6+5")
        result_str = str(result)
        assert "2d6" in result_str
        assert "+" in result_str
        assert "=" in result_str

    def test_multiplier_in_string(self):
        """Test multiplier in result string."""
        expr = parse_dice_notation("(2d6)*2")
        assert expr.multiplier == 2
