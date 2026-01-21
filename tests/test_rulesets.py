"""Tests for ruleset implementations."""

import pytest

from dnd_manager.rulesets.base import (
    RulesetRegistry,
    CharacterCreationStep,
    SubclassProgression,
    CasterType,
    FULL_CASTER_SLOTS,
    HALF_CASTER_SLOTS,
    WARLOCK_PACT_SLOTS,
)
from dnd_manager.rulesets.dnd2024 import DnD2024Ruleset
from dnd_manager.rulesets.dnd2014 import DnD2014Ruleset
from dnd_manager.rulesets.tov import TalesOfTheValiantRuleset


class TestRulesetRegistry:
    """Tests for the ruleset registry."""

    def test_rulesets_registered(self):
        """Test that all rulesets are registered."""
        ids = RulesetRegistry.get_ids()
        assert "dnd2024" in ids
        assert "dnd2014" in ids
        assert "tov" in ids

    def test_get_ruleset(self):
        """Test getting a ruleset by ID."""
        ruleset = RulesetRegistry.get("dnd2024")
        assert ruleset is not None
        assert ruleset.id == "dnd2024"

    def test_get_invalid_ruleset(self):
        """Test getting non-existent ruleset returns None."""
        assert RulesetRegistry.get("invalid") is None


class TestDnD2024Ruleset:
    """Tests for D&D 2024 ruleset."""

    @pytest.fixture
    def ruleset(self):
        return DnD2024Ruleset()

    def test_basic_properties(self, ruleset):
        """Test basic ruleset properties."""
        assert ruleset.id == "dnd2024"
        assert ruleset.name == "D&D 5e (2024)"
        assert ruleset.species_term == "Species"
        assert ruleset.subspecies_term == "Subspecies"

    def test_ability_score_source(self, ruleset):
        """Test that 2024 gets ability bonuses from background."""
        assert ruleset.get_ability_score_source() == "background"

    def test_has_origin_feats(self, ruleset):
        """Test that 2024 has origin feats."""
        assert ruleset.has_origin_feats() is True

    def test_creation_order_starts_with_class(self, ruleset):
        """Test that 2024 creation starts with class."""
        order = ruleset.creation_order
        assert order[0] == CharacterCreationStep.CLASS
        assert CharacterCreationStep.BACKGROUND in order
        assert CharacterCreationStep.SPECIES in order

    def test_all_subclasses_at_level_3(self, ruleset):
        """Test that all 2024 classes get subclass at level 3."""
        for class_name in ruleset.get_available_classes():
            prog = ruleset.get_subclass_progression(class_name)
            assert prog.selection_level == 3, f"{class_name} should get subclass at 3"

    def test_standardized_subclass_progression(self, ruleset):
        """Test that 2024 has standardized subclass feature levels."""
        for class_name in ruleset.get_available_classes():
            prog = ruleset.get_subclass_progression(class_name)
            assert prog.feature_levels == [3, 6, 10, 14], f"{class_name}"

    def test_12_classes_available(self, ruleset):
        """Test that 2024 has 12 classes."""
        classes = ruleset.get_available_classes()
        assert len(classes) == 12
        assert "Wizard" in classes
        assert "Fighter" in classes

    def test_class_definitions(self, ruleset):
        """Test class definitions are complete."""
        wizard = ruleset.get_class_definition("Wizard")
        assert wizard is not None
        assert wizard.hit_die == 6
        assert wizard.caster_type == CasterType.FULL
        assert wizard.spellcasting_ability == "Intelligence"

    def test_species_no_ability_bonuses(self, ruleset):
        """Test that 2024 species don't have ability bonuses."""
        for species_name in ruleset.get_available_species():
            species = ruleset.get_species_definition(species_name)
            assert species is not None
            # 2024 species have no ability_increases
            assert len(species.ability_increases) == 0

    def test_backgrounds_have_ability_options(self, ruleset):
        """Test that 2024 backgrounds have ability score options."""
        for bg_name in ruleset.get_available_backgrounds():
            bg = ruleset.get_background_definition(bg_name)
            assert bg is not None
            assert len(bg.ability_score_options) == 3, f"{bg_name}"
            assert bg.origin_feat is not None, f"{bg_name}"

    def test_asi_levels(self, ruleset):
        """Test ASI levels are correct."""
        assert ruleset.get_asi_levels() == [4, 8, 12, 16, 19]


class TestDnD2014Ruleset:
    """Tests for D&D 2014 ruleset."""

    @pytest.fixture
    def ruleset(self):
        return DnD2014Ruleset()

    def test_basic_properties(self, ruleset):
        """Test basic ruleset properties."""
        assert ruleset.id == "dnd2014"
        assert ruleset.name == "D&D 5e (2014)"
        assert ruleset.species_term == "Race"
        assert ruleset.subspecies_term == "Subspecies"

    def test_ability_score_source(self, ruleset):
        """Test that 2014 gets ability bonuses from race."""
        assert ruleset.get_ability_score_source() == "race"

    def test_no_origin_feats(self, ruleset):
        """Test that 2014 does not have origin feats."""
        assert ruleset.has_origin_feats() is False

    def test_creation_order_starts_with_race(self, ruleset):
        """Test that 2014 creation starts with race."""
        order = ruleset.creation_order
        assert order[0] == CharacterCreationStep.RACE
        assert CharacterCreationStep.CLASS in order

    def test_varied_subclass_levels(self, ruleset):
        """Test that 2014 has varied subclass selection levels."""
        # Cleric gets subclass at 1
        cleric_prog = ruleset.get_subclass_progression("Cleric")
        assert cleric_prog.selection_level == 1

        # Wizard gets subclass at 2
        wizard_prog = ruleset.get_subclass_progression("Wizard")
        assert wizard_prog.selection_level == 2

        # Fighter gets subclass at 3
        fighter_prog = ruleset.get_subclass_progression("Fighter")
        assert fighter_prog.selection_level == 3

    def test_races_have_ability_bonuses(self, ruleset):
        """Test that 2014 races have ability bonuses."""
        # High Elf gets +2 DEX, +1 INT
        high_elf = ruleset.get_species_definition("High Elf")
        assert high_elf is not None
        assert len(high_elf.ability_increases) > 0

        # Dragonborn gets +2 STR, +1 CHA
        dragonborn = ruleset.get_species_definition("Dragonborn")
        assert dragonborn is not None
        assert len(dragonborn.ability_increases) > 0

    def test_backgrounds_have_features(self, ruleset):
        """Test that 2014 backgrounds have features (not ability scores)."""
        sage = ruleset.get_background_definition("Sage")
        assert sage is not None
        assert sage.feature_name is not None
        assert len(sage.ability_score_options) == 0


class TestTalesOfTheValiantRuleset:
    """Tests for Tales of the Valiant ruleset."""

    @pytest.fixture
    def ruleset(self):
        return TalesOfTheValiantRuleset()

    def test_basic_properties(self, ruleset):
        """Test basic ruleset properties."""
        assert ruleset.id == "tov"
        assert ruleset.name == "Tales of the Valiant"
        assert ruleset.species_term == "Lineage"
        assert ruleset.subspecies_term == "Heritage"

    def test_ability_score_source_none(self, ruleset):
        """Test that ToV uses point buy only."""
        assert ruleset.get_ability_score_source() == "none"

    def test_no_origin_feats(self, ruleset):
        """Test that ToV does not have origin feats (uses talents)."""
        assert ruleset.has_origin_feats() is False

    def test_creation_order_has_lineage_and_heritage(self, ruleset):
        """Test that ToV creation has lineage and heritage steps."""
        order = ruleset.creation_order
        assert CharacterCreationStep.LINEAGE in order
        assert CharacterCreationStep.HERITAGE in order
        assert CharacterCreationStep.CONCEPT in order

    def test_13_classes_available(self, ruleset):
        """Test that ToV has 13 classes (including Mechanist)."""
        classes = ruleset.get_available_classes()
        assert len(classes) == 13
        assert "Mechanist" in classes

    def test_lineages_available(self, ruleset):
        """Test that lineages are available."""
        lineages = ruleset.get_available_species()
        assert "Beastkin" in lineages
        assert "Kobold" in lineages
        assert "Smallfolk" in lineages

    def test_heritages_available(self, ruleset):
        """Test that heritages are available."""
        heritages = ruleset.get_available_heritages()
        assert len(heritages) > 0
        assert "Cottage" in heritages
        assert "Nomadic" in heritages

    def test_talent_levels(self, ruleset):
        """Test talent levels are correct."""
        assert ruleset.get_talent_levels() == [4, 8, 12, 16, 19]


class TestSpellSlotProgressions:
    """Tests for spell slot progressions."""

    def test_full_caster_level_1(self):
        """Test full caster slots at level 1."""
        slots = FULL_CASTER_SLOTS.get_slots(1)
        assert slots == {1: 2}

    def test_full_caster_level_5(self):
        """Test full caster slots at level 5."""
        slots = FULL_CASTER_SLOTS.get_slots(5)
        assert slots == {1: 4, 2: 3, 3: 2}

    def test_full_caster_level_20(self):
        """Test full caster slots at level 20."""
        slots = FULL_CASTER_SLOTS.get_slots(20)
        assert slots[9] == 1  # 1 9th level slot
        assert slots[1] == 4  # 4 1st level slots

    def test_half_caster_level_1(self):
        """Test half caster has no slots at level 1."""
        slots = HALF_CASTER_SLOTS.get_slots(1)
        assert slots == {}

    def test_half_caster_level_2(self):
        """Test half caster gets slots at level 2."""
        slots = HALF_CASTER_SLOTS.get_slots(2)
        assert slots == {1: 2}

    def test_warlock_pact_magic(self):
        """Test warlock pact magic progression."""
        # Level 1: 1 1st-level slot
        slots = WARLOCK_PACT_SLOTS.get_slots(1)
        assert slots == {1: 1}

        # Level 11: 3 5th-level slots
        slots = WARLOCK_PACT_SLOTS.get_slots(11)
        assert slots == {5: 3}


class TestSubclassProgression:
    """Tests for SubclassProgression."""

    def test_has_subclass_at(self):
        """Test checking if subclass is available."""
        prog = SubclassProgression(3, [3, 6, 10, 14])
        assert not prog.has_subclass_at(1)
        assert not prog.has_subclass_at(2)
        assert prog.has_subclass_at(3)
        assert prog.has_subclass_at(10)

    def test_gets_feature_at(self):
        """Test checking for subclass feature levels."""
        prog = SubclassProgression(3, [3, 6, 10, 14])
        assert prog.gets_feature_at(3)
        assert not prog.gets_feature_at(4)
        assert prog.gets_feature_at(6)
        assert not prog.gets_feature_at(7)


class TestHitPointCalculation:
    """Tests for HP calculation."""

    def test_wizard_level_1(self):
        """Test wizard HP at level 1."""
        ruleset = DnD2024Ruleset()
        hp = ruleset.calculate_hit_points("Wizard", 1, con_modifier=2)
        # 6 (d6 max) + 2 (CON) = 8
        assert hp == 8

    def test_barbarian_level_1(self):
        """Test barbarian HP at level 1."""
        ruleset = DnD2024Ruleset()
        hp = ruleset.calculate_hit_points("Barbarian", 1, con_modifier=3)
        # 12 (d12 max) + 3 (CON) = 15
        assert hp == 15

    def test_fighter_level_5_average(self):
        """Test fighter HP at level 5 with average rolls."""
        ruleset = DnD2024Ruleset()
        hp = ruleset.calculate_hit_points("Fighter", 5, con_modifier=2, method="average")
        # Level 1: 10 + 2 = 12
        # Levels 2-5: 4 * (6 + 2) = 32  [avg d10 = 6]
        # Total: 12 + 32 = 44
        assert hp == 44

    def test_minimum_hp(self):
        """Test that HP is minimum 1."""
        ruleset = DnD2024Ruleset()
        hp = ruleset.calculate_hit_points("Wizard", 1, con_modifier=-5)
        assert hp == 1
