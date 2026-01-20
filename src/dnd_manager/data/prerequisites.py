"""Structured prerequisite system for D&D content validation.

This module provides a unified way to define and validate prerequisites
for feats, magic items, spells, and other content that has requirements.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from dnd_manager.models.character import Character


class ProficiencyType(Enum):
    """Types of proficiency requirements."""
    LIGHT_ARMOR = "light_armor"
    MEDIUM_ARMOR = "medium_armor"
    HEAVY_ARMOR = "heavy_armor"
    SHIELDS = "shields"
    SIMPLE_WEAPONS = "simple_weapons"
    MARTIAL_WEAPONS = "martial_weapons"
    SPECIFIC_WEAPON = "specific_weapon"
    TOOL = "tool"
    SKILL = "skill"


@dataclass
class AbilityRequirement:
    """Requirement for a minimum ability score."""
    ability: str  # strength, dexterity, constitution, intelligence, wisdom, charisma
    minimum: int  # Minimum score required (typically 13)

    def check(self, character: "Character") -> tuple[bool, str]:
        """Check if character meets this requirement."""
        ability_lower = self.ability.lower()
        if hasattr(character.abilities, ability_lower):
            ability_obj = getattr(character.abilities, ability_lower)
            current = ability_obj.total if hasattr(ability_obj, 'total') else ability_obj
            if current >= self.minimum:
                return True, ""
            return False, f"Requires {self.ability.title()} {self.minimum}+ (you have {current})"
        return False, f"Unknown ability: {self.ability}"


@dataclass
class LevelRequirement:
    """Requirement for a minimum character or class level."""
    minimum: int
    class_name: Optional[str] = None  # If None, checks total character level

    def check(self, character: "Character") -> tuple[bool, str]:
        """Check if character meets this requirement."""
        if self.class_name:
            # Check specific class level
            class_lower = self.class_name.lower()
            if character.primary_class and character.primary_class.name.lower() == class_lower:
                if character.primary_class.level >= self.minimum:
                    return True, ""
            # Check multiclass
            for mc in character.multiclass:
                if mc.name.lower() == class_lower:
                    if mc.level >= self.minimum:
                        return True, ""
            return False, f"Requires {self.class_name} level {self.minimum}+"
        else:
            # Check total character level
            total_level = character.level
            if total_level >= self.minimum:
                return True, ""
            return False, f"Requires character level {self.minimum}+ (you are level {total_level})"


@dataclass
class ProficiencyRequirement:
    """Requirement for a specific proficiency."""
    proficiency_type: ProficiencyType
    specific: Optional[str] = None  # For specific weapon/tool/skill names

    def check(self, character: "Character") -> tuple[bool, str]:
        """Check if character meets this requirement."""
        profs = character.proficiencies

        if self.proficiency_type == ProficiencyType.LIGHT_ARMOR:
            if "Light" in profs.armor or "All" in profs.armor:
                return True, ""
            return False, "Requires light armor proficiency"

        elif self.proficiency_type == ProficiencyType.MEDIUM_ARMOR:
            if "Medium" in profs.armor or "All" in profs.armor:
                return True, ""
            return False, "Requires medium armor proficiency"

        elif self.proficiency_type == ProficiencyType.HEAVY_ARMOR:
            if "Heavy" in profs.armor or "All" in profs.armor:
                return True, ""
            return False, "Requires heavy armor proficiency"

        elif self.proficiency_type == ProficiencyType.SHIELDS:
            if "Shields" in profs.armor:
                return True, ""
            return False, "Requires shield proficiency"

        elif self.proficiency_type == ProficiencyType.SIMPLE_WEAPONS:
            if "Simple" in profs.weapons or "All" in profs.weapons:
                return True, ""
            return False, "Requires simple weapon proficiency"

        elif self.proficiency_type == ProficiencyType.MARTIAL_WEAPONS:
            if "Martial" in profs.weapons or "All" in profs.weapons:
                return True, ""
            return False, "Requires martial weapon proficiency"

        elif self.proficiency_type == ProficiencyType.SPECIFIC_WEAPON:
            if self.specific:
                # Check for specific weapon or category that includes it
                if self.specific in profs.weapons:
                    return True, ""
                # Martial weapons include all martial, Simple includes all simple
                if "Martial" in profs.weapons or "Simple" in profs.weapons or "All" in profs.weapons:
                    return True, ""
            return False, f"Requires proficiency with {self.specific or 'specific weapon'}"

        elif self.proficiency_type == ProficiencyType.TOOL:
            if self.specific and self.specific in profs.tools:
                return True, ""
            return False, f"Requires proficiency with {self.specific or 'tools'}"

        elif self.proficiency_type == ProficiencyType.SKILL:
            if self.specific and self.specific in profs.skills:
                return True, ""
            return False, f"Requires proficiency in {self.specific or 'skill'}"

        return False, "Unknown proficiency requirement"


@dataclass
class SpellcastingRequirement:
    """Requirement for spellcasting ability."""
    requires_spellcasting: bool = True
    requires_pact_magic: bool = False  # Warlock pact magic specifically
    min_spell_level: Optional[int] = None  # Minimum spell level access

    def check(self, character: "Character") -> tuple[bool, str]:
        """Check if character meets this requirement."""
        has_spellcasting = character.spellcasting.ability is not None

        if self.requires_pact_magic:
            # Check for Warlock specifically
            is_warlock = (
                (character.primary_class and character.primary_class.name == "Warlock") or
                any(mc.name == "Warlock" for mc in character.multiclass)
            )
            if is_warlock or has_spellcasting:
                return True, ""
            return False, "Requires Spellcasting or Pact Magic feature"

        if self.requires_spellcasting and not has_spellcasting:
            return False, "Requires the ability to cast at least one spell"

        if self.min_spell_level:
            # Check if character has access to spells of this level
            max_slot_level = max(
                (level for level, slots in character.spellcasting.spell_slots.items()
                 if slots.total > 0),
                default=0
            )
            if max_slot_level < self.min_spell_level:
                return False, f"Requires access to level {self.min_spell_level} spells"

        return True, ""


@dataclass
class ClassRequirement:
    """Requirement for a specific class."""
    class_names: list[str]  # List of acceptable classes (OR logic)
    min_level: int = 1

    def check(self, character: "Character") -> tuple[bool, str]:
        """Check if character meets this requirement."""
        classes_lower = [c.lower() for c in self.class_names]

        # Check primary class
        if character.primary_class:
            if character.primary_class.name.lower() in classes_lower:
                if character.primary_class.level >= self.min_level:
                    return True, ""

        # Check multiclass
        for mc in character.multiclass:
            if mc.name.lower() in classes_lower:
                if mc.level >= self.min_level:
                    return True, ""

        class_list = ", ".join(self.class_names)
        if self.min_level > 1:
            return False, f"Requires {class_list} level {self.min_level}+"
        return False, f"Requires {class_list} class"


@dataclass
class FeatRequirement:
    """Requirement for having another feat."""
    feat_name: str

    def check(self, character: "Character") -> tuple[bool, str]:
        """Check if character has the required feat."""
        feat_lower = self.feat_name.lower()
        for feat in character.feats:
            if feat.name.lower() == feat_lower:
                return True, ""
        return False, f"Requires {self.feat_name} feat"


@dataclass
class Prerequisite:
    """A complete prerequisite that may contain multiple requirements.

    Requirements within a Prerequisite use AND logic by default.
    For OR logic (e.g., STR 13 OR DEX 13), use alternative_abilities.
    """
    # Ability score requirements (all must be met)
    abilities: list[AbilityRequirement] = field(default_factory=list)

    # Alternative ability requirements (any one must be met)
    # Used for cases like "Strength 13 or Dexterity 13"
    alternative_abilities: list[AbilityRequirement] = field(default_factory=list)

    # Level requirements
    level: Optional[LevelRequirement] = None

    # Proficiency requirements (all must be met)
    proficiencies: list[ProficiencyRequirement] = field(default_factory=list)

    # Spellcasting requirement
    spellcasting: Optional[SpellcastingRequirement] = None

    # Class requirements
    class_req: Optional[ClassRequirement] = None

    # Feat requirements (all must be met)
    feats: list[FeatRequirement] = field(default_factory=list)

    # Original string for display (human-readable version)
    description: str = ""

    def check(self, character: "Character") -> tuple[bool, list[str]]:
        """Check all requirements against a character.

        Returns:
            Tuple of (all_met, list_of_failure_reasons)
        """
        failures: list[str] = []

        # Check required abilities (AND logic)
        for ability_req in self.abilities:
            met, reason = ability_req.check(character)
            if not met:
                failures.append(reason)

        # Check alternative abilities (OR logic)
        if self.alternative_abilities:
            any_met = False
            alt_reasons = []
            for ability_req in self.alternative_abilities:
                met, reason = ability_req.check(character)
                if met:
                    any_met = True
                    break
                alt_reasons.append(reason)
            if not any_met:
                # Show first requirement as the failure
                failures.append(alt_reasons[0] if alt_reasons else "Alternative ability requirement not met")

        # Check level
        if self.level:
            met, reason = self.level.check(character)
            if not met:
                failures.append(reason)

        # Check proficiencies (AND logic)
        for prof_req in self.proficiencies:
            met, reason = prof_req.check(character)
            if not met:
                failures.append(reason)

        # Check spellcasting
        if self.spellcasting:
            met, reason = self.spellcasting.check(character)
            if not met:
                failures.append(reason)

        # Check class
        if self.class_req:
            met, reason = self.class_req.check(character)
            if not met:
                failures.append(reason)

        # Check feats (AND logic)
        for feat_req in self.feats:
            met, reason = feat_req.check(character)
            if not met:
                failures.append(reason)

        return len(failures) == 0, failures

    def check_simple(self, character: "Character") -> tuple[bool, str]:
        """Simplified check returning single failure reason."""
        met, failures = self.check(character)
        if met:
            return True, ""
        return False, failures[0] if failures else "Prerequisite not met"


# =============================================================================
# PREREQUISITE BUILDERS - Convenience functions for common patterns
# =============================================================================

def ability_prereq(ability: str, minimum: int = 13) -> Prerequisite:
    """Create a simple ability score prerequisite."""
    return Prerequisite(
        abilities=[AbilityRequirement(ability, minimum)],
        description=f"{ability.title()} {minimum} or higher"
    )


def dual_ability_prereq(ability1: str, min1: int, ability2: str, min2: int) -> Prerequisite:
    """Create a prerequisite requiring two ability scores."""
    return Prerequisite(
        abilities=[
            AbilityRequirement(ability1, min1),
            AbilityRequirement(ability2, min2),
        ],
        description=f"{ability1.title()} {min1}+ and {ability2.title()} {min2}+"
    )


def either_ability_prereq(ability1: str, ability2: str, minimum: int = 13) -> Prerequisite:
    """Create a prerequisite for either of two ability scores."""
    return Prerequisite(
        alternative_abilities=[
            AbilityRequirement(ability1, minimum),
            AbilityRequirement(ability2, minimum),
        ],
        description=f"{ability1.title()} {minimum}+ or {ability2.title()} {minimum}+"
    )


def level_prereq(level: int, class_name: Optional[str] = None) -> Prerequisite:
    """Create a level prerequisite."""
    if class_name:
        return Prerequisite(
            level=LevelRequirement(level, class_name),
            description=f"{class_name} level {level}+"
        )
    return Prerequisite(
        level=LevelRequirement(level),
        description=f"Character level {level}+"
    )


def proficiency_prereq(prof_type: ProficiencyType, specific: Optional[str] = None) -> Prerequisite:
    """Create a proficiency prerequisite."""
    req = ProficiencyRequirement(prof_type, specific)
    if specific:
        desc = f"Proficiency with {specific}"
    else:
        desc = f"Proficiency with {prof_type.value.replace('_', ' ')}"
    return Prerequisite(
        proficiencies=[req],
        description=desc
    )


def spellcasting_prereq(pact_magic_ok: bool = True) -> Prerequisite:
    """Create a spellcasting prerequisite."""
    return Prerequisite(
        spellcasting=SpellcastingRequirement(
            requires_spellcasting=True,
            requires_pact_magic=pact_magic_ok
        ),
        description="The ability to cast at least one spell"
    )


def class_prereq(class_names: list[str], min_level: int = 1) -> Prerequisite:
    """Create a class prerequisite."""
    class_list = " or ".join(class_names)
    if min_level > 1:
        desc = f"{class_list} level {min_level}+"
    else:
        desc = f"{class_list}"
    return Prerequisite(
        class_req=ClassRequirement(class_names, min_level),
        description=desc
    )


def feat_prereq(feat_name: str) -> Prerequisite:
    """Create a feat prerequisite."""
    return Prerequisite(
        feats=[FeatRequirement(feat_name)],
        description=f"{feat_name} feat"
    )


def combine_prereqs(*prereqs: Prerequisite) -> Prerequisite:
    """Combine multiple prerequisites into one (AND logic)."""
    combined = Prerequisite()
    descriptions = []

    for p in prereqs:
        combined.abilities.extend(p.abilities)
        combined.alternative_abilities.extend(p.alternative_abilities)
        if p.level and not combined.level:
            combined.level = p.level
        combined.proficiencies.extend(p.proficiencies)
        if p.spellcasting and not combined.spellcasting:
            combined.spellcasting = p.spellcasting
        if p.class_req and not combined.class_req:
            combined.class_req = p.class_req
        combined.feats.extend(p.feats)
        if p.description:
            descriptions.append(p.description)

    combined.description = "; ".join(descriptions)
    return combined


# =============================================================================
# PRESET PREREQUISITES - Common prerequisites used across the system
# =============================================================================

# 2024 Martial Feat Prerequisites (used by GWM, Sharpshooter, PAM, etc.)
MARTIAL_FEAT_STR = combine_prereqs(
    ability_prereq("Strength", 13),
    proficiency_prereq(ProficiencyType.MARTIAL_WEAPONS)
)
MARTIAL_FEAT_STR.description = "Strength 13+; Proficiency with any martial weapon"

MARTIAL_FEAT_DEX = combine_prereqs(
    ability_prereq("Dexterity", 13),
    proficiency_prereq(ProficiencyType.MARTIAL_WEAPONS)
)
MARTIAL_FEAT_DEX.description = "Dexterity 13+; Proficiency with any martial weapon"

# Heavy Armor Master
HEAVY_ARMOR_PREREQ = proficiency_prereq(ProficiencyType.HEAVY_ARMOR)

# Medium Armor Master
MEDIUM_ARMOR_PREREQ = proficiency_prereq(ProficiencyType.MEDIUM_ARMOR)

# Spellcaster feats
SPELLCASTER_PREREQ = spellcasting_prereq(pact_magic_ok=True)

# Paladin-only (e.g., Holy Avenger)
PALADIN_PREREQ = class_prereq(["Paladin"])

# Druid/Ranger (e.g., Staff of the Wild Heart)
DRUID_RANGER_PREREQ = class_prereq(["Druid", "Ranger"])

# Common caster classes
ARCANE_CASTER_PREREQ = class_prereq(["Sorcerer", "Warlock", "Wizard"])
FULL_CASTER_PREREQ = class_prereq(["Bard", "Cleric", "Druid", "Sorcerer", "Warlock", "Wizard"])
