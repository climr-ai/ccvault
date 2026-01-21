"""Tests for character model."""

import pytest
from datetime import datetime

from dnd_manager.models.character import (
    Character,
    CharacterClass,
    CharacterMeta,
    Combat,
    HitPoints,
    HitDice,
    DeathSaves,
    Proficiencies,
    Spellcasting,
    SpellSlot,
    RulesetId,
)
from dnd_manager.models.abilities import (
    Ability,
    AbilityScore,
    AbilityScores,
    Skill,
    SkillProficiency,
)


class TestCharacter:
    """Tests for Character model."""

    def test_default_character(self):
        """Test default character creation."""
        char = Character()
        assert char.name == "New Character"
        assert char.total_level == 1
        assert char.proficiency_bonus == 2

    def test_total_level_single_class(self):
        """Test total level calculation for single class."""
        char = Character(
            primary_class=CharacterClass(name="Wizard", level=5)
        )
        assert char.total_level == 5
        assert char.proficiency_bonus == 3

    def test_total_level_multiclass(self):
        """Test total level calculation for multiclass."""
        char = Character(
            primary_class=CharacterClass(name="Fighter", level=5),
            multiclass=[
                CharacterClass(name="Rogue", level=3),
                CharacterClass(name="Wizard", level=2),
            ]
        )
        assert char.total_level == 10
        assert char.proficiency_bonus == 4

    def test_skill_modifier_no_proficiency(self):
        """Test skill modifier without proficiency."""
        char = Character(
            abilities=AbilityScores(dexterity=AbilityScore(base=16))
        )
        # Stealth uses DEX, no proficiency
        mod = char.get_skill_modifier(Skill.STEALTH)
        assert mod == 3  # Just DEX modifier

    def test_skill_modifier_with_proficiency(self):
        """Test skill modifier with proficiency."""
        char = Character(
            abilities=AbilityScores(dexterity=AbilityScore(base=16)),
            proficiencies=Proficiencies(
                skills={Skill.STEALTH: SkillProficiency.PROFICIENT}
            )
        )
        mod = char.get_skill_modifier(Skill.STEALTH)
        assert mod == 5  # DEX (+3) + Prof (+2)

    def test_skill_modifier_with_expertise(self):
        """Test skill modifier with expertise."""
        char = Character(
            primary_class=CharacterClass(name="Rogue", level=5),
            abilities=AbilityScores(dexterity=AbilityScore(base=16)),
            proficiencies=Proficiencies(
                skills={Skill.STEALTH: SkillProficiency.EXPERTISE}
            )
        )
        mod = char.get_skill_modifier(Skill.STEALTH)
        assert mod == 9  # DEX (+3) + 2*Prof (+6)

    def test_save_modifier_not_proficient(self):
        """Test saving throw modifier without proficiency."""
        char = Character(
            abilities=AbilityScores(wisdom=AbilityScore(base=14))
        )
        mod = char.get_save_modifier(Ability.WISDOM)
        assert mod == 2  # Just WIS modifier

    def test_save_modifier_proficient(self):
        """Test saving throw modifier with proficiency."""
        char = Character(
            abilities=AbilityScores(wisdom=AbilityScore(base=14)),
            proficiencies=Proficiencies(saving_throws=[Ability.WISDOM])
        )
        mod = char.get_save_modifier(Ability.WISDOM)
        assert mod == 4  # WIS (+2) + Prof (+2)

    def test_initiative(self):
        """Test initiative calculation."""
        char = Character(
            abilities=AbilityScores(dexterity=AbilityScore(base=16)),
            combat=Combat(initiative_bonus=2)
        )
        assert char.get_initiative() == 5  # DEX (+3) + bonus (+2)

    def test_passive_perception(self):
        """Test passive perception calculation."""
        char = Character(
            abilities=AbilityScores(wisdom=AbilityScore(base=14)),
            proficiencies=Proficiencies(
                skills={Skill.PERCEPTION: SkillProficiency.PROFICIENT}
            )
        )
        assert char.get_passive_perception() == 14  # 10 + WIS (+2) + Prof (+2)

    def test_spell_save_dc(self):
        """Test spell save DC calculation."""
        char = Character(
            primary_class=CharacterClass(name="Wizard", level=5),
            abilities=AbilityScores(intelligence=AbilityScore(base=18)),
            spellcasting=Spellcasting(ability=Ability.INTELLIGENCE)
        )
        assert char.get_spell_save_dc() == 15  # 8 + INT (+4) + Prof (+3)

    def test_spell_attack_bonus(self):
        """Test spell attack bonus calculation."""
        char = Character(
            primary_class=CharacterClass(name="Wizard", level=5),
            abilities=AbilityScores(intelligence=AbilityScore(base=18)),
            spellcasting=Spellcasting(ability=Ability.INTELLIGENCE)
        )
        assert char.get_spell_attack_bonus() == 7  # INT (+4) + Prof (+3)


class TestHitPoints:
    """Tests for HitPoints model."""

    def test_effective_hp(self):
        """Test effective HP includes temp HP."""
        hp = HitPoints(maximum=30, current=25, temporary=5)
        assert hp.effective == 30

    def test_bloodied(self):
        """Test bloodied condition."""
        hp = HitPoints(maximum=30, current=15)
        assert hp.is_bloodied
        hp.current = 16
        assert not hp.is_bloodied

    def test_unconscious(self):
        """Test unconscious at 0 HP."""
        hp = HitPoints(maximum=30, current=0)
        assert hp.is_unconscious
        hp.current = 1
        assert not hp.is_unconscious


class TestDeathSaves:
    """Tests for DeathSaves model."""

    def test_stable(self):
        """Test stable at 3 successes."""
        ds = DeathSaves(successes=3, failures=0)
        assert ds.is_stable
        assert not ds.is_dead

    def test_dead(self):
        """Test dead at 3 failures."""
        ds = DeathSaves(successes=0, failures=3)
        assert not ds.is_stable
        assert ds.is_dead

    def test_reset(self):
        """Test reset clears saves."""
        ds = DeathSaves(successes=2, failures=1)
        ds.reset()
        assert ds.successes == 0
        assert ds.failures == 0


class TestDamageAndHealing:
    """Tests for damage and healing."""

    def test_take_damage(self):
        """Test taking damage."""
        char = Character(
            combat=Combat(hit_points=HitPoints(maximum=30, current=30))
        )
        char.take_damage(10)
        assert char.combat.hit_points.current == 20

    def test_take_damage_temp_hp_first(self):
        """Test temp HP absorbs damage first."""
        char = Character(
            combat=Combat(hit_points=HitPoints(maximum=30, current=30, temporary=5))
        )
        char.take_damage(8)
        assert char.combat.hit_points.temporary == 0
        assert char.combat.hit_points.current == 27

    def test_heal(self):
        """Test healing."""
        char = Character(
            combat=Combat(hit_points=HitPoints(maximum=30, current=20))
        )
        char.heal(15)
        assert char.combat.hit_points.current == 30  # Capped at max

    def test_heal_resets_death_saves(self):
        """Test healing from 0 resets death saves."""
        char = Character(
            combat=Combat(
                hit_points=HitPoints(maximum=30, current=0),
                death_saves=DeathSaves(successes=2, failures=1)
            )
        )
        char.heal(5)
        assert char.combat.death_saves.successes == 0
        assert char.combat.death_saves.failures == 0


class TestSpellSlots:
    """Tests for SpellSlot model."""

    def test_remaining(self):
        """Test remaining slots calculation."""
        slot = SpellSlot(total=4, used=1)
        assert slot.remaining == 3

    def test_use_slot(self):
        """Test using a spell slot."""
        slot = SpellSlot(total=4, used=0)
        assert slot.use() is True
        assert slot.used == 1
        assert slot.remaining == 3

    def test_use_slot_empty(self):
        """Test using slot when empty."""
        slot = SpellSlot(total=2, used=2)
        assert slot.use() is False
        assert slot.used == 2

    def test_restore(self):
        """Test restoring slots."""
        slot = SpellSlot(total=4, used=3)
        slot.restore(2)
        assert slot.used == 1

    def test_restore_all(self):
        """Test restoring all slots."""
        slot = SpellSlot(total=4, used=4)
        slot.restore_all()
        assert slot.used == 0


class TestRests:
    """Tests for rest functionality."""

    def test_long_rest(self):
        """Test long rest restores HP and slots."""
        char = Character(
            combat=Combat(
                hit_points=HitPoints(maximum=30, current=15, temporary=5),
                hit_dice=HitDice(total=5, remaining=2, die="d8"),
            ),
            spellcasting=Spellcasting(
                ability=Ability.INTELLIGENCE,
                slots={
                    1: SpellSlot(total=4, used=3),
                    2: SpellSlot(total=3, used=2),
                }
            )
        )

        char.long_rest()

        # HP fully restored
        assert char.combat.hit_points.current == 30
        assert char.combat.hit_points.temporary == 0

        # Hit dice partially restored (max half)
        assert char.combat.hit_dice.remaining == 4  # 2 + max(1, 5//2)

        # Spell slots fully restored
        assert char.spellcasting.slots[1].used == 0
        assert char.spellcasting.slots[2].used == 0


class TestRulesetIntegration:
    """Tests for ruleset integration with character model."""

    def test_get_ruleset_2024(self):
        """Test getting 2024 ruleset."""
        char = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2024))
        ruleset = char.get_ruleset()
        assert ruleset is not None
        assert ruleset.id == "dnd2024"

    def test_get_ruleset_2014(self):
        """Test getting 2014 ruleset."""
        char = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2014))
        ruleset = char.get_ruleset()
        assert ruleset is not None
        assert ruleset.id == "dnd2014"

    def test_get_ruleset_tov(self):
        """Test getting ToV ruleset."""
        char = Character(meta=CharacterMeta(ruleset=RulesetId.TALES_OF_VALIANT))
        ruleset = char.get_ruleset()
        assert ruleset is not None
        assert ruleset.id == "tov"

    def test_species_term_by_ruleset(self):
        """Test species terminology varies by ruleset."""
        char_2024 = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2024))
        assert char_2024.get_species_term() == "Species"

        char_2014 = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2014))
        assert char_2014.get_species_term() == "Race"

        char_tov = Character(meta=CharacterMeta(ruleset=RulesetId.TALES_OF_VALIANT))
        assert char_tov.get_species_term() == "Lineage"

    def test_subspecies_term_by_ruleset(self):
        """Test subspecies terminology varies by ruleset."""
        char_2024 = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2024))
        assert char_2024.get_subspecies_term() == "Subspecies"

        char_2014 = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2014))
        assert char_2014.get_subspecies_term() == "Subspecies"

        char_tov = Character(meta=CharacterMeta(ruleset=RulesetId.TALES_OF_VALIANT))
        assert char_tov.get_subspecies_term() == "Heritage"

    def test_subclass_level_2024(self):
        """Test all 2024 classes get subclass at level 3."""
        char = Character(
            meta=CharacterMeta(ruleset=RulesetId.DND_2024),
            primary_class=CharacterClass(name="Wizard", level=5),
        )
        assert char.get_subclass_level() == 3
        assert char.get_subclass_level("Fighter") == 3
        assert char.get_subclass_level("Cleric") == 3

    def test_subclass_level_2014_varies(self):
        """Test 2014 has varied subclass levels."""
        char = Character(
            meta=CharacterMeta(ruleset=RulesetId.DND_2014),
            primary_class=CharacterClass(name="Cleric", level=1),
        )
        assert char.get_subclass_level("Cleric") == 1  # Cleric at 1
        assert char.get_subclass_level("Wizard") == 2  # Wizard at 2
        assert char.get_subclass_level("Fighter") == 3  # Fighter at 3

    def test_has_subclass_available(self):
        """Test checking if subclass is available."""
        char = Character(
            meta=CharacterMeta(ruleset=RulesetId.DND_2024),
            primary_class=CharacterClass(name="Wizard", level=2),
        )
        assert not char.has_subclass_available()  # Level 2, need 3

        char.primary_class.level = 3
        assert char.has_subclass_available()  # Level 3, can pick subclass

    def test_calculate_max_hp_wizard_level_1(self):
        """Test HP calculation for level 1 wizard."""
        char = Character(
            meta=CharacterMeta(ruleset=RulesetId.DND_2024),
            primary_class=CharacterClass(name="Wizard", level=1),
            abilities=AbilityScores(constitution=AbilityScore(base=14)),  # +2 CON
        )
        # Wizard d6: 6 + 2 (CON) = 8 HP at level 1
        assert char.calculate_max_hp() == 8

    def test_calculate_max_hp_fighter_level_5(self):
        """Test HP calculation for level 5 fighter."""
        char = Character(
            meta=CharacterMeta(ruleset=RulesetId.DND_2024),
            primary_class=CharacterClass(name="Fighter", level=5),
            abilities=AbilityScores(constitution=AbilityScore(base=14)),  # +2 CON
        )
        # Fighter d10: 10 + 2 = 12 at level 1
        # Levels 2-5: 4 * (6 + 2) = 32 (avg d10 = 6)
        # Total: 12 + 32 = 44
        assert char.calculate_max_hp() == 44

    def test_sync_spell_slots_wizard(self):
        """Test syncing spell slots for a wizard."""
        char = Character(
            meta=CharacterMeta(ruleset=RulesetId.DND_2024),
            primary_class=CharacterClass(name="Wizard", level=5),
        )
        char.sync_spell_slots()

        # Level 5 wizard should have: 4 1st, 3 2nd, 2 3rd
        assert char.spellcasting.slots[1].total == 4
        assert char.spellcasting.slots[2].total == 3
        assert char.spellcasting.slots[3].total == 2
        assert 4 not in char.spellcasting.slots  # No 4th level slots yet

    def test_sync_spell_slots_fighter(self):
        """Test syncing spell slots for non-caster."""
        char = Character(
            meta=CharacterMeta(ruleset=RulesetId.DND_2024),
            primary_class=CharacterClass(name="Fighter", level=5),
        )
        char.sync_spell_slots()

        # Fighter has no spell slots
        assert len(char.spellcasting.slots) == 0

    def test_sync_hit_dice(self):
        """Test syncing hit dice with class."""
        char = Character(
            meta=CharacterMeta(ruleset=RulesetId.DND_2024),
            primary_class=CharacterClass(name="Barbarian", level=5),
        )
        char.sync_hit_dice()

        assert char.combat.hit_dice.total == 5
        assert char.combat.hit_dice.die == "d12"  # Barbarian d12

    def test_sync_with_ruleset(self):
        """Test full sync with ruleset."""
        char = Character(
            meta=CharacterMeta(ruleset=RulesetId.DND_2024),
            primary_class=CharacterClass(name="Cleric", level=3),
            abilities=AbilityScores(constitution=AbilityScore(base=14)),
        )
        char.sync_with_ruleset()

        # Check HP was calculated
        # Cleric d8: 8 + 2 = 10 at level 1
        # Levels 2-3: 2 * (5 + 2) = 14 (avg d8 = 5)
        # Total: 10 + 14 = 24
        assert char.combat.hit_points.maximum == 24

        # Check spell slots
        assert char.spellcasting.slots[1].total == 4
        assert char.spellcasting.slots[2].total == 2

        # Check hit dice
        assert char.combat.hit_dice.total == 3
        assert char.combat.hit_dice.die == "d8"

    def test_create_new_character_2024(self):
        """Test creating new character with 2024 ruleset."""
        char = Character.create_new(
            name="Test Wizard",
            ruleset_id=RulesetId.DND_2024,
            class_name="Wizard",
            player="Tester",
        )

        assert char.name == "Test Wizard"
        assert char.player == "Tester"
        assert char.primary_class.name == "Wizard"
        assert char.meta.ruleset == RulesetId.DND_2024

        # Check wizard defaults
        assert Ability.INTELLIGENCE in char.proficiencies.saving_throws
        assert Ability.WISDOM in char.proficiencies.saving_throws
        assert char.spellcasting.ability == Ability.INTELLIGENCE
        assert char.combat.hit_dice.die == "d6"

    def test_create_new_character_tov(self):
        """Test creating new character with ToV ruleset."""
        char = Character.create_new(
            name="Test Mechanist",
            ruleset_id=RulesetId.TALES_OF_VALIANT,
            class_name="Mechanist",
        )

        assert char.name == "Test Mechanist"
        assert char.primary_class.name == "Mechanist"
        assert char.meta.ruleset == RulesetId.TALES_OF_VALIANT
        assert char.combat.hit_dice.die == "d8"

    def test_get_available_classes(self):
        """Test getting available classes."""
        char = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2024))
        classes = char.get_available_classes()
        assert len(classes) == 12
        assert "Wizard" in classes
        assert "Fighter" in classes

    def test_get_available_species(self):
        """Test getting available species."""
        char = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2024))
        species = char.get_available_species()
        assert "Human" in species
        assert "Elf" in species

    def test_get_available_backgrounds(self):
        """Test getting available backgrounds."""
        char = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2024))
        backgrounds = char.get_available_backgrounds()
        assert "Sage" in backgrounds
        assert "Noble" in backgrounds

    def test_get_asi_levels(self):
        """Test getting ASI levels."""
        char = Character(meta=CharacterMeta(ruleset=RulesetId.DND_2024))
        levels = char.get_asi_levels()
        assert levels == [4, 8, 12, 16, 19]
