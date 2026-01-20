"""Tests for ability score models."""

import pytest

from dnd_manager.models.abilities import (
    Ability,
    AbilityScore,
    AbilityScores,
    Skill,
    SkillProficiency,
    SKILL_ABILITY_MAP,
    calculate_skill_modifier,
    get_proficiency_bonus,
)


class TestAbilityScore:
    """Tests for AbilityScore model."""

    def test_default_values(self):
        """Test default ability score values."""
        score = AbilityScore()
        assert score.base == 10
        assert score.bonus == 0
        assert score.override is None
        assert score.total == 10
        assert score.modifier == 0

    def test_modifier_calculation(self):
        """Test ability modifier calculation."""
        # Test various scores and expected modifiers
        test_cases = [
            (1, -5),
            (2, -4),
            (3, -4),
            (4, -3),
            (5, -3),
            (6, -2),
            (7, -2),
            (8, -1),
            (9, -1),
            (10, 0),
            (11, 0),
            (12, 1),
            (13, 1),
            (14, 2),
            (15, 2),
            (16, 3),
            (17, 3),
            (18, 4),
            (19, 4),
            (20, 5),
            (30, 10),
        ]

        for base, expected_mod in test_cases:
            score = AbilityScore(base=base)
            assert score.modifier == expected_mod, f"Score {base} should have modifier {expected_mod}"

    def test_total_with_bonus(self):
        """Test total calculation with bonus."""
        score = AbilityScore(base=14, bonus=2)
        assert score.total == 16
        assert score.modifier == 3

    def test_override(self):
        """Test override functionality."""
        score = AbilityScore(base=10, bonus=5, override=18)
        assert score.total == 18
        assert score.modifier == 4

    def test_modifier_string(self):
        """Test modifier string formatting."""
        assert AbilityScore(base=14).modifier_str == "+2"
        assert AbilityScore(base=8).modifier_str == "-1"
        assert AbilityScore(base=10).modifier_str == "+0"


class TestAbilityScores:
    """Tests for AbilityScores collection."""

    def test_from_array(self):
        """Test creating from standard array."""
        scores = AbilityScores.from_array([15, 14, 13, 12, 10, 8])
        assert scores.strength.base == 15
        assert scores.dexterity.base == 14
        assert scores.constitution.base == 13
        assert scores.intelligence.base == 12
        assert scores.wisdom.base == 10
        assert scores.charisma.base == 8

    def test_from_array_invalid(self):
        """Test from_array with wrong number of scores."""
        with pytest.raises(ValueError):
            AbilityScores.from_array([15, 14, 13])

    def test_get_by_enum(self):
        """Test getting ability by enum."""
        scores = AbilityScores(strength=AbilityScore(base=16))
        assert scores.get(Ability.STRENGTH).base == 16

    def test_get_modifier(self):
        """Test getting modifier by enum."""
        scores = AbilityScores(dexterity=AbilityScore(base=18))
        assert scores.get_modifier(Ability.DEXTERITY) == 4


class TestProficiencyBonus:
    """Tests for proficiency bonus calculation."""

    def test_proficiency_by_level(self):
        """Test proficiency bonus for each level."""
        expected = {
            1: 2, 2: 2, 3: 2, 4: 2,
            5: 3, 6: 3, 7: 3, 8: 3,
            9: 4, 10: 4, 11: 4, 12: 4,
            13: 5, 14: 5, 15: 5, 16: 5,
            17: 6, 18: 6, 19: 6, 20: 6,
        }

        for level, expected_bonus in expected.items():
            assert get_proficiency_bonus(level) == expected_bonus, f"Level {level}"

    def test_invalid_level(self):
        """Test that level 0 raises error."""
        with pytest.raises(ValueError):
            get_proficiency_bonus(0)


class TestSkillModifier:
    """Tests for skill modifier calculation."""

    def test_no_proficiency(self):
        """Test skill modifier without proficiency."""
        mod = calculate_skill_modifier(3, 2, SkillProficiency.NONE)
        assert mod == 3

    def test_proficient(self):
        """Test skill modifier with proficiency."""
        mod = calculate_skill_modifier(3, 2, SkillProficiency.PROFICIENT)
        assert mod == 5

    def test_expertise(self):
        """Test skill modifier with expertise."""
        mod = calculate_skill_modifier(3, 2, SkillProficiency.EXPERTISE)
        assert mod == 7


class TestSkillAbilityMapping:
    """Tests for skill to ability mappings."""

    def test_all_skills_mapped(self):
        """Ensure all skills have an ability mapping."""
        for skill in Skill:
            assert skill in SKILL_ABILITY_MAP

    def test_strength_skills(self):
        """Test Strength skill mappings."""
        assert SKILL_ABILITY_MAP[Skill.ATHLETICS] == Ability.STRENGTH

    def test_dexterity_skills(self):
        """Test Dexterity skill mappings."""
        assert SKILL_ABILITY_MAP[Skill.ACROBATICS] == Ability.DEXTERITY
        assert SKILL_ABILITY_MAP[Skill.STEALTH] == Ability.DEXTERITY

    def test_intelligence_skills(self):
        """Test Intelligence skill mappings."""
        assert SKILL_ABILITY_MAP[Skill.ARCANA] == Ability.INTELLIGENCE
        assert SKILL_ABILITY_MAP[Skill.HISTORY] == Ability.INTELLIGENCE

    def test_wisdom_skills(self):
        """Test Wisdom skill mappings."""
        assert SKILL_ABILITY_MAP[Skill.PERCEPTION] == Ability.WISDOM
        assert SKILL_ABILITY_MAP[Skill.INSIGHT] == Ability.WISDOM

    def test_charisma_skills(self):
        """Test Charisma skill mappings."""
        assert SKILL_ABILITY_MAP[Skill.PERSUASION] == Ability.CHARISMA
        assert SKILL_ABILITY_MAP[Skill.DECEPTION] == Ability.CHARISMA
