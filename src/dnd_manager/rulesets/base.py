"""Base ruleset interface and common definitions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CharacterCreationStep(str, Enum):
    """Steps in character creation process."""

    CONCEPT = "concept"
    CLASS = "class"
    RACE = "race"  # 2014 terminology
    SPECIES = "species"  # 2024 terminology
    LINEAGE = "lineage"  # ToV terminology
    HERITAGE = "heritage"  # ToV - cultural background
    BACKGROUND = "background"
    ABILITY_SCORES = "ability_scores"
    ALIGNMENT = "alignment"
    EQUIPMENT = "equipment"
    SUBCLASS = "subclass"
    SPELLS = "spells"
    FEATURES = "features"
    PERSONALITY = "personality"
    FINISHING = "finishing"


class CasterType(str, Enum):
    """Types of spellcasters."""

    NONE = "none"
    FULL = "full"  # Wizard, Cleric, Druid, Bard, Sorcerer
    HALF = "half"  # Paladin, Ranger
    THIRD = "third"  # Eldritch Knight, Arcane Trickster
    PACT = "pact"  # Warlock (unique progression)


@dataclass
class SubclassProgression:
    """Defines when a class gets subclass features."""

    selection_level: int  # When you choose your subclass
    feature_levels: list[int]  # Levels when you get subclass features

    def has_subclass_at(self, level: int) -> bool:
        """Check if subclass is selected at this level."""
        return level >= self.selection_level

    def gets_feature_at(self, level: int) -> bool:
        """Check if a subclass feature is gained at this level."""
        return level in self.feature_levels


@dataclass
class ClassDefinition:
    """Core class definition."""

    name: str
    hit_die: int  # d6, d8, d10, d12
    primary_ability: str  # Main ability for the class
    saving_throws: list[str]  # Two saving throw proficiencies
    skill_choices: int  # Number of skills to choose
    skill_options: list[str]  # Available skill choices
    armor_proficiencies: list[str]
    weapon_proficiencies: list[str]
    tool_proficiencies: list[str] = field(default_factory=list)
    caster_type: CasterType = CasterType.NONE
    spellcasting_ability: Optional[str] = None
    subclass_progression: SubclassProgression = field(
        default_factory=lambda: SubclassProgression(3, [3, 6, 10, 14])
    )


@dataclass
class SpellSlotProgression:
    """Spell slot table for a caster type."""

    # slots[level][spell_level] = number of slots
    # Level 0 is unused, levels 1-20
    slots: dict[int, dict[int, int]] = field(default_factory=dict)

    def get_slots(self, character_level: int) -> dict[int, int]:
        """Get spell slots for a character level."""
        if character_level < 1:
            return {}
        if character_level > 20:
            character_level = 20
        return self.slots.get(character_level, {})


# Standard full caster spell slot progression
FULL_CASTER_SLOTS = SpellSlotProgression(slots={
    1: {1: 2},
    2: {1: 3},
    3: {1: 4, 2: 2},
    4: {1: 4, 2: 3},
    5: {1: 4, 2: 3, 3: 2},
    6: {1: 4, 2: 3, 3: 3},
    7: {1: 4, 2: 3, 3: 3, 4: 1},
    8: {1: 4, 2: 3, 3: 3, 4: 2},
    9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
})

# Half caster progression (Paladin, Ranger)
HALF_CASTER_SLOTS = SpellSlotProgression(slots={
    1: {},
    2: {1: 2},
    3: {1: 3},
    4: {1: 3},
    5: {1: 4, 2: 2},
    6: {1: 4, 2: 2},
    7: {1: 4, 2: 3},
    8: {1: 4, 2: 3},
    9: {1: 4, 2: 3, 3: 2},
    10: {1: 4, 2: 3, 3: 2},
    11: {1: 4, 2: 3, 3: 3},
    12: {1: 4, 2: 3, 3: 3},
    13: {1: 4, 2: 3, 3: 3, 4: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 2},
    16: {1: 4, 2: 3, 3: 3, 4: 2},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
})

# Third caster progression (Eldritch Knight, Arcane Trickster)
THIRD_CASTER_SLOTS = SpellSlotProgression(slots={
    1: {},
    2: {},
    3: {1: 2},
    4: {1: 3},
    5: {1: 3},
    6: {1: 3},
    7: {1: 4, 2: 2},
    8: {1: 4, 2: 2},
    9: {1: 4, 2: 2},
    10: {1: 4, 2: 3},
    11: {1: 4, 2: 3},
    12: {1: 4, 2: 3},
    13: {1: 4, 2: 3, 3: 2},
    14: {1: 4, 2: 3, 3: 2},
    15: {1: 4, 2: 3, 3: 2},
    16: {1: 4, 2: 3, 3: 3},
    17: {1: 4, 2: 3, 3: 3},
    18: {1: 4, 2: 3, 3: 3},
    19: {1: 4, 2: 3, 3: 3, 4: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 1},
})

# Warlock Pact Magic progression
WARLOCK_PACT_SLOTS = SpellSlotProgression(slots={
    1: {1: 1},
    2: {1: 2},
    3: {2: 2},
    4: {2: 2},
    5: {3: 2},
    6: {3: 2},
    7: {4: 2},
    8: {4: 2},
    9: {5: 2},
    10: {5: 2},
    11: {5: 3},
    12: {5: 3},
    13: {5: 3},
    14: {5: 3},
    15: {5: 3},
    16: {5: 3},
    17: {5: 4},
    18: {5: 4},
    19: {5: 4},
    20: {5: 4},
})


@dataclass
class AbilityScoreIncrease:
    """Represents an ability score increase option."""

    options: list[str]  # Which abilities can be increased
    amount: int  # How much to increase by
    choose: int = 1  # How many to choose from options


@dataclass
class BackgroundDefinition:
    """Background definition with ruleset-specific features."""

    name: str
    description: str
    skill_proficiencies: list[str]
    tool_proficiencies: list[str] = field(default_factory=list)
    languages: int = 0  # Number of languages to choose
    equipment: list[str] = field(default_factory=list)
    starting_gold: int = 0

    # 2024-specific
    ability_score_options: list[str] = field(default_factory=list)  # 3 options
    origin_feat: Optional[str] = None

    # Feature (2014-style)
    feature_name: Optional[str] = None
    feature_description: Optional[str] = None


@dataclass
class SpeciesDefinition:
    """Species/Race/Lineage definition."""

    name: str
    description: str
    size: str = "Medium"
    speed: int = 30

    # Ability score increases (2014 style)
    ability_increases: list[AbilityScoreIncrease] = field(default_factory=list)

    # Traits
    traits: list[str] = field(default_factory=list)

    # Proficiencies
    skill_proficiencies: list[str] = field(default_factory=list)
    weapon_proficiencies: list[str] = field(default_factory=list)
    armor_proficiencies: list[str] = field(default_factory=list)
    tool_proficiencies: list[str] = field(default_factory=list)

    # Languages
    languages: list[str] = field(default_factory=list)
    bonus_languages: int = 0

    # Darkvision
    darkvision: int = 0  # Range in feet, 0 = none

    # Subspecies/subrace options
    subspecies: list[str] = field(default_factory=list)


class Ruleset(ABC):
    """Abstract base class for ruleset implementations."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for this ruleset."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name for this ruleset."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of this ruleset."""
        pass

    @property
    @abstractmethod
    def creation_order(self) -> list[CharacterCreationStep]:
        """Order of steps in character creation."""
        pass

    @property
    @abstractmethod
    def species_term(self) -> str:
        """What to call species (race, species, lineage)."""
        pass

    @property
    @abstractmethod
    def subspecies_term(self) -> str:
        """What to call subspecies (subrace, subspecies, heritage)."""
        pass

    @abstractmethod
    def get_ability_score_source(self) -> str:
        """Where ability score bonuses come from (race, background, etc)."""
        pass

    @abstractmethod
    def get_subclass_progression(self, class_name: str) -> SubclassProgression:
        """Get subclass progression for a class."""
        pass

    @abstractmethod
    def get_class_definition(self, class_name: str) -> Optional[ClassDefinition]:
        """Get class definition by name."""
        pass

    @abstractmethod
    def get_available_classes(self) -> list[str]:
        """Get list of available class names."""
        pass

    @abstractmethod
    def get_species_definition(self, species_name: str) -> Optional[SpeciesDefinition]:
        """Get species/race definition by name."""
        pass

    @abstractmethod
    def get_available_species(self) -> list[str]:
        """Get list of available species names."""
        pass

    @abstractmethod
    def get_background_definition(self, background_name: str) -> Optional[BackgroundDefinition]:
        """Get background definition by name."""
        pass

    @abstractmethod
    def get_available_backgrounds(self) -> list[str]:
        """Get list of available background names."""
        pass

    @abstractmethod
    def has_origin_feats(self) -> bool:
        """Whether this ruleset uses origin feats."""
        pass

    @abstractmethod
    def get_asi_levels(self) -> list[int]:
        """Get levels where ASI/feats are available."""
        pass

    def get_spell_slots(self, class_name: str, level: int) -> dict[int, int]:
        """Get spell slots for a class at a level."""
        class_def = self.get_class_definition(class_name)
        if not class_def:
            return {}

        if class_def.caster_type == CasterType.FULL:
            return FULL_CASTER_SLOTS.get_slots(level)
        elif class_def.caster_type == CasterType.HALF:
            return HALF_CASTER_SLOTS.get_slots(level)
        elif class_def.caster_type == CasterType.THIRD:
            return THIRD_CASTER_SLOTS.get_slots(level)
        elif class_def.caster_type == CasterType.PACT:
            return WARLOCK_PACT_SLOTS.get_slots(level)

        return {}

    def calculate_hit_points(
        self,
        class_name: str,
        level: int,
        con_modifier: int,
        method: str = "average"
    ) -> int:
        """Calculate hit points for a class at a level.

        Args:
            class_name: The character's class
            level: Character level
            con_modifier: Constitution modifier
            method: "average" or "max" (for level 1)
        """
        class_def = self.get_class_definition(class_name)
        if not class_def:
            return 1

        hit_die = class_def.hit_die

        # Level 1: Max hit die + CON mod
        hp = hit_die + con_modifier

        # Subsequent levels: average or rolled
        if level > 1:
            if method == "average":
                # Average is (die / 2) + 1
                avg_roll = (hit_die // 2) + 1
            else:
                avg_roll = hit_die  # Max for "max" method

            hp += (level - 1) * (avg_roll + con_modifier)

        return max(1, hp)  # Minimum 1 HP


class RulesetRegistry:
    """Registry of available rulesets."""

    _rulesets: dict[str, Ruleset] = {}

    @classmethod
    def register(cls, ruleset: Ruleset) -> None:
        """Register a ruleset."""
        cls._rulesets[ruleset.id] = ruleset

    @classmethod
    def get(cls, ruleset_id: str) -> Optional[Ruleset]:
        """Get a ruleset by ID."""
        return cls._rulesets.get(ruleset_id)

    @classmethod
    def get_all(cls) -> list[Ruleset]:
        """Get all registered rulesets."""
        return list(cls._rulesets.values())

    @classmethod
    def get_ids(cls) -> list[str]:
        """Get all registered ruleset IDs."""
        return list(cls._rulesets.keys())
