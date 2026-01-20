"""Ability scores and skills models for D&D 5e."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class Ability(str, Enum):
    """The six core ability scores in D&D 5e."""

    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"

    @property
    def abbreviation(self) -> str:
        """Return 3-letter abbreviation (STR, DEX, etc.)."""
        return self.value[:3].upper()

    @property
    def display_name(self) -> str:
        """Return title-case display name."""
        return self.value.title()

    @classmethod
    def from_abbr(cls, abbr: str) -> "Ability":
        """Get ability from abbreviation."""
        abbr_map = {a.abbreviation: a for a in cls}
        return abbr_map[abbr.upper()]


class Skill(str, Enum):
    """The 18 skills in D&D 5e."""

    # Strength
    ATHLETICS = "athletics"
    # Dexterity
    ACROBATICS = "acrobatics"
    SLEIGHT_OF_HAND = "sleight_of_hand"
    STEALTH = "stealth"
    # Intelligence
    ARCANA = "arcana"
    HISTORY = "history"
    INVESTIGATION = "investigation"
    NATURE = "nature"
    RELIGION = "religion"
    # Wisdom
    ANIMAL_HANDLING = "animal_handling"
    INSIGHT = "insight"
    MEDICINE = "medicine"
    PERCEPTION = "perception"
    SURVIVAL = "survival"
    # Charisma
    DECEPTION = "deception"
    INTIMIDATION = "intimidation"
    PERFORMANCE = "performance"
    PERSUASION = "persuasion"

    @property
    def display_name(self) -> str:
        """Return human-readable name."""
        return self.value.replace("_", " ").title()


# Mapping of skills to their governing ability
SKILL_ABILITY_MAP: dict[Skill, Ability] = {
    # Strength
    Skill.ATHLETICS: Ability.STRENGTH,
    # Dexterity
    Skill.ACROBATICS: Ability.DEXTERITY,
    Skill.SLEIGHT_OF_HAND: Ability.DEXTERITY,
    Skill.STEALTH: Ability.DEXTERITY,
    # Intelligence
    Skill.ARCANA: Ability.INTELLIGENCE,
    Skill.HISTORY: Ability.INTELLIGENCE,
    Skill.INVESTIGATION: Ability.INTELLIGENCE,
    Skill.NATURE: Ability.INTELLIGENCE,
    Skill.RELIGION: Ability.INTELLIGENCE,
    # Wisdom
    Skill.ANIMAL_HANDLING: Ability.WISDOM,
    Skill.INSIGHT: Ability.WISDOM,
    Skill.MEDICINE: Ability.WISDOM,
    Skill.PERCEPTION: Ability.WISDOM,
    Skill.SURVIVAL: Ability.WISDOM,
    # Charisma
    Skill.DECEPTION: Ability.CHARISMA,
    Skill.INTIMIDATION: Ability.CHARISMA,
    Skill.PERFORMANCE: Ability.CHARISMA,
    Skill.PERSUASION: Ability.CHARISMA,
}

# Organized list of skills by ability for UI display
SKILLS: dict[Ability, list[Skill]] = {
    Ability.STRENGTH: [Skill.ATHLETICS],
    Ability.DEXTERITY: [Skill.ACROBATICS, Skill.SLEIGHT_OF_HAND, Skill.STEALTH],
    Ability.CONSTITUTION: [],  # No skills use Constitution
    Ability.INTELLIGENCE: [
        Skill.ARCANA,
        Skill.HISTORY,
        Skill.INVESTIGATION,
        Skill.NATURE,
        Skill.RELIGION,
    ],
    Ability.WISDOM: [
        Skill.ANIMAL_HANDLING,
        Skill.INSIGHT,
        Skill.MEDICINE,
        Skill.PERCEPTION,
        Skill.SURVIVAL,
    ],
    Ability.CHARISMA: [
        Skill.DECEPTION,
        Skill.INTIMIDATION,
        Skill.PERFORMANCE,
        Skill.PERSUASION,
    ],
}


class AbilityScore(BaseModel):
    """A single ability score with base value, bonuses, and optional override."""

    base: int = Field(default=10, ge=1, le=30, description="Base ability score (1-30)")
    bonus: int = Field(default=0, description="Bonus from items, effects, etc.")
    override: Optional[int] = Field(
        default=None, ge=1, le=30, description="Manual override value"
    )

    @computed_field
    @property
    def total(self) -> int:
        """Calculate total score (override if set, otherwise base + bonus)."""
        if self.override is not None:
            return self.override
        return self.base + self.bonus

    @computed_field
    @property
    def modifier(self) -> int:
        """Calculate ability modifier: floor((score - 10) / 2)."""
        return (self.total - 10) // 2

    @property
    def modifier_str(self) -> str:
        """Return modifier as string with sign (+3, -1, etc.)."""
        mod = self.modifier
        return f"+{mod}" if mod >= 0 else str(mod)


class AbilityScores(BaseModel):
    """All six ability scores for a character."""

    strength: AbilityScore = Field(default_factory=AbilityScore)
    dexterity: AbilityScore = Field(default_factory=AbilityScore)
    constitution: AbilityScore = Field(default_factory=AbilityScore)
    intelligence: AbilityScore = Field(default_factory=AbilityScore)
    wisdom: AbilityScore = Field(default_factory=AbilityScore)
    charisma: AbilityScore = Field(default_factory=AbilityScore)

    def get(self, ability: Ability) -> AbilityScore:
        """Get ability score by Ability enum."""
        return getattr(self, ability.value)

    def get_modifier(self, ability: Ability) -> int:
        """Get ability modifier by Ability enum."""
        return self.get(ability).modifier

    @classmethod
    def from_array(cls, scores: list[int]) -> "AbilityScores":
        """Create from list of 6 scores in standard order (STR, DEX, CON, INT, WIS, CHA)."""
        if len(scores) != 6:
            raise ValueError("Must provide exactly 6 ability scores")
        return cls(
            strength=AbilityScore(base=scores[0]),
            dexterity=AbilityScore(base=scores[1]),
            constitution=AbilityScore(base=scores[2]),
            intelligence=AbilityScore(base=scores[3]),
            wisdom=AbilityScore(base=scores[4]),
            charisma=AbilityScore(base=scores[5]),
        )

    @classmethod
    def standard_array(cls) -> "AbilityScores":
        """Create with standard array values (15, 14, 13, 12, 10, 8) unassigned."""
        # Returns default 10s - user assigns standard array values
        return cls()


class SkillProficiency(str, Enum):
    """Level of proficiency in a skill."""

    NONE = "none"
    PROFICIENT = "proficient"
    EXPERTISE = "expertise"  # Double proficiency bonus


def calculate_skill_modifier(
    ability_modifier: int,
    proficiency_bonus: int,
    proficiency: SkillProficiency = SkillProficiency.NONE,
) -> int:
    """Calculate skill modifier based on ability mod and proficiency."""
    if proficiency == SkillProficiency.NONE:
        return ability_modifier
    elif proficiency == SkillProficiency.PROFICIENT:
        return ability_modifier + proficiency_bonus
    elif proficiency == SkillProficiency.EXPERTISE:
        return ability_modifier + (proficiency_bonus * 2)
    return ability_modifier  # fallback


def get_proficiency_bonus(level: int) -> int:
    """Get proficiency bonus for a given character level."""
    if level < 1:
        raise ValueError("Level must be at least 1")
    if level > 20:
        level = 20  # Cap at 20 for standard play
    # Proficiency bonus = 2 + floor((level - 1) / 4)
    return 2 + ((level - 1) // 4)
