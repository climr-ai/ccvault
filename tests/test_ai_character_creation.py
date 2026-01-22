"""Tests for AI-driven character creation using creation tools.

This module tests the character creation workflow as it would be used by an AI:
1. Initialize creation session
2. Set character attributes in sequence
3. Finalize and validate the character

These tests demonstrate that the AI tools are sufficient for character creation
and can be called in the correct sequence to produce a valid character.
"""

import pytest
from dnd_manager.ai.tools.handlers.creation_handlers import (
    create_character,
    set_character_name,
    set_character_class,
    set_character_species,
    set_character_background,
    assign_ability_scores,
    set_ability_bonuses,
    add_skill_proficiency,
    select_cantrips,
    select_spells,
    select_origin_feat,
    get_character_preview,
    finalize_character,
    get_creation_session,
    clear_creation_session,
    # Extended tools for full character building
    set_class_levels,
    set_combat_stats,
    set_hit_dice_pool,
    set_saving_throw_proficiencies,
    set_proficiencies,
    add_features,
    set_spellcasting,
    add_equipment,
    set_currency,
    set_personality,
)
from dnd_manager.models.abilities import Ability, Skill, SkillProficiency


class TestAICharacterCreationWorkflow:
    """Test the full AI character creation workflow.

    These tests simulate an AI calling tools in sequence to create characters.
    They validate that the tool chain works correctly.
    """

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clear sessions before and after each test."""
        clear_creation_session("ai_test")
        yield
        clear_creation_session("ai_test")

    @pytest.mark.asyncio
    async def test_create_paladin_valeria_concept(self):
        """Test creating a level 1 Paladin based on Valeria's concept.

        This simulates an AI creating a character following a user request
        for a "noble Aasimar paladin with divine powers".
        """
        session_id = "ai_test"

        # Step 1: Initialize session with 2024 rules
        result = await create_character(ruleset="dnd2024", session_id=session_id)
        assert result["data"]["ruleset"] == "dnd2024"
        assert result["data"]["session_started"] is True

        # Step 2: Set name
        result = await set_character_name(name="Valeria Sunforge", session_id=session_id)
        assert result["data"]["name"] == "Valeria Sunforge"

        # Step 3: Set class
        result = await set_character_class(class_name="Paladin", session_id=session_id)
        assert result["data"]["class"] == "Paladin"
        assert result["data"]["hit_die"] == "d10"
        assert "Charisma" in result["data"]["saving_throws"] or "charisma" in str(result["data"]["saving_throws"]).lower()

        # Step 4: Set species
        result = await set_character_species(species="Aasimar", session_id=session_id)
        assert result["data"]["species"] == "Aasimar"

        # Step 5: Set background (required for 2024)
        result = await set_character_background(background="Noble", session_id=session_id)
        assert result["data"]["background"] == "Noble"

        # Step 6: Assign ability scores (point buy values for paladin)
        # Prioritize CHA and STR for a paladin
        result = await assign_ability_scores(
            strength=15,
            dexterity=10,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=15,
            session_id=session_id
        )
        assert result["data"]["scores"]["strength"] == 15
        assert result["data"]["scores"]["charisma"] == 15
        assert result["data"]["modifiers"]["strength"] == 2

        # Step 7: Apply background bonuses (+2/+1 for 2024 rules)
        result = await set_ability_bonuses(
            bonuses={"strength": 2, "charisma": 1},
            session_id=session_id
        )
        assert result["data"]["new_totals"]["strength"] == 17
        assert result["data"]["new_totals"]["charisma"] == 16

        # Step 8: Add skill proficiencies (Paladin gets 2)
        result = await add_skill_proficiency(skill="Athletics", session_id=session_id)
        assert result["data"]["skill"] == "Athletics"
        assert result["data"]["total_skills"] == 1

        result = await add_skill_proficiency(skill="Persuasion", session_id=session_id)
        assert result["data"]["skill"] == "Persuasion"
        assert result["data"]["total_skills"] == 2

        # Step 9: Preview character before finalizing
        result = await get_character_preview(session_id=session_id)
        assert result["data"]["is_complete"] is True
        assert result["data"]["missing_fields"] == []
        preview = result["data"]["preview"]
        assert preview["name"] == "Valeria Sunforge"
        assert preview["class"] == "Paladin"
        assert preview["species"] == "Aasimar"

        # Step 10: Finalize character
        result = await finalize_character(confirm=True, session_id=session_id)
        assert result["data"]["character_created"] is True
        assert "character" in result

        # Validate the created character
        char = result["character"]
        assert char.name == "Valeria Sunforge"
        assert char.primary_class.name == "Paladin"
        assert char.primary_class.level == 1
        assert char.species == "Aasimar"
        assert char.background == "Noble"

        # Check ability scores with bonuses
        assert char.abilities.strength.total == 17  # 15 + 2
        assert char.abilities.charisma.total == 16  # 15 + 1
        assert char.abilities.constitution.total == 14

        # Check proficiencies
        assert Skill.ATHLETICS in char.proficiencies.skills
        assert Skill.PERSUASION in char.proficiencies.skills

        # Check HP calculation (d10 max + CON mod)
        assert char.combat.hit_points.maximum == 12  # 10 + 2 CON

    @pytest.mark.asyncio
    async def test_create_wizard_with_spells(self):
        """Test creating a Wizard with cantrips and spells."""
        session_id = "ai_test"

        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_name(name="Gandalf the Grey", session_id=session_id)
        await set_character_class(class_name="Wizard", session_id=session_id)
        await set_character_species(species="Human", session_id=session_id)
        await set_character_background(background="Sage", session_id=session_id)
        await assign_ability_scores(
            strength=8, dexterity=14, constitution=13,
            intelligence=15, wisdom=12, charisma=10,
            session_id=session_id
        )
        await set_ability_bonuses(bonuses={"intelligence": 2, "constitution": 1}, session_id=session_id)
        await add_skill_proficiency(skill="Arcana", session_id=session_id)
        await add_skill_proficiency(skill="History", session_id=session_id)

        # Wizard gets cantrips and spells
        result = await select_cantrips(
            cantrips=["Fire Bolt", "Mage Hand", "Prestidigitation"],
            session_id=session_id
        )
        assert result["data"]["count"] == 3

        result = await select_spells(
            spells=["Magic Missile", "Shield", "Mage Armor"],
            session_id=session_id
        )
        assert result["data"]["count"] == 3

        # Finalize
        result = await finalize_character(confirm=True, session_id=session_id)
        char = result["character"]

        assert char.name == "Gandalf the Grey"
        assert char.primary_class.name == "Wizard"
        assert "Fire Bolt" in char.spellcasting.cantrips
        assert "Magic Missile" in char.spellcasting.known
        assert char.spellcasting.ability == Ability.INTELLIGENCE

    @pytest.mark.asyncio
    async def test_create_fighter_simple(self):
        """Test creating a simple non-caster Fighter."""
        session_id = "ai_test"

        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_name(name="Conan", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)
        await set_character_species(species="Human", session_id=session_id)
        await set_character_background(background="Soldier", session_id=session_id)
        await assign_ability_scores(
            strength=15, dexterity=14, constitution=14,
            intelligence=10, wisdom=12, charisma=8,
            session_id=session_id
        )
        await set_ability_bonuses(bonuses={"strength": 2, "constitution": 1}, session_id=session_id)
        await add_skill_proficiency(skill="Athletics", session_id=session_id)
        await add_skill_proficiency(skill="Intimidation", session_id=session_id)

        result = await finalize_character(confirm=True, session_id=session_id)
        char = result["character"]

        assert char.name == "Conan"
        assert char.primary_class.name == "Fighter"
        assert char.abilities.strength.total == 17
        assert char.combat.hit_points.maximum == 12  # d10 + 2 CON

    @pytest.mark.asyncio
    async def test_tool_sequence_validation(self):
        """Test that tools validate state correctly."""
        session_id = "ai_test"

        # Can't finalize without creating session first
        await create_character(ruleset="dnd2024", session_id=session_id)

        # Preview shows incomplete
        result = await get_character_preview(session_id=session_id)
        assert result["data"]["is_complete"] is False
        assert "name" in result["data"]["missing_fields"]

        # Can't finalize incomplete character
        with pytest.raises(ValueError, match="Cannot finalize"):
            await finalize_character(confirm=True, session_id=session_id)

        # Add required fields
        await set_character_name(name="Test", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)
        await set_character_species(species="Human", session_id=session_id)
        await set_character_background(background="Soldier", session_id=session_id)
        await assign_ability_scores(
            strength=15, dexterity=14, constitution=13,
            intelligence=12, wisdom=10, charisma=8,
            session_id=session_id
        )

        # Now preview shows complete
        result = await get_character_preview(session_id=session_id)
        assert result["data"]["is_complete"] is True

        # Now can finalize
        result = await finalize_character(confirm=True, session_id=session_id)
        assert result["data"]["character_created"] is True

    @pytest.mark.asyncio
    async def test_invalid_inputs_raise_errors(self):
        """Test that invalid inputs raise appropriate errors."""
        session_id = "ai_test"
        await create_character(ruleset="dnd2024", session_id=session_id)

        # Invalid class
        with pytest.raises(ValueError, match="Unknown class"):
            await set_character_class(class_name="Jedi", session_id=session_id)

        # Invalid species
        with pytest.raises(ValueError, match="Unknown species"):
            await set_character_species(species="Vulcan", session_id=session_id)

        # Invalid skill
        with pytest.raises(ValueError, match="Unknown skill"):
            await add_skill_proficiency(skill="Hacking", session_id=session_id)

    @pytest.mark.asyncio
    async def test_duplicate_skill_error(self):
        """Test that adding duplicate skill raises error."""
        session_id = "ai_test"
        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)
        await add_skill_proficiency(skill="Athletics", session_id=session_id)

        with pytest.raises(ValueError, match="Already proficient"):
            await add_skill_proficiency(skill="Athletics", session_id=session_id)


class TestAIWorkflowVariations:
    """Test different character creation variations an AI might attempt."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        clear_creation_session("ai_var_test")
        yield
        clear_creation_session("ai_var_test")

    @pytest.mark.asyncio
    async def test_2014_rules_no_background_required(self):
        """Test that 2014 rules don't require background."""
        session_id = "ai_var_test"

        await create_character(ruleset="dnd2014", session_id=session_id)
        await set_character_name(name="Old School Hero", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)
        await set_character_species(species="Human", session_id=session_id)
        await assign_ability_scores(
            strength=15, dexterity=14, constitution=13,
            intelligence=12, wisdom=10, charisma=8,
            session_id=session_id
        )

        # Preview should be complete without background for 2014
        result = await get_character_preview(session_id=session_id)
        assert result["data"]["is_complete"] is True

        result = await finalize_character(confirm=True, session_id=session_id)
        assert result["data"]["character_created"] is True

    @pytest.mark.asyncio
    async def test_change_class_clears_skills(self):
        """Test that changing class clears previously selected skills."""
        session_id = "ai_var_test"

        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)
        await add_skill_proficiency(skill="Athletics", session_id=session_id)

        # Verify skill added
        session = get_creation_session(session_id)
        assert "Athletics" in session.skill_proficiencies

        # Change class - should clear skills
        await set_character_class(class_name="Wizard", session_id=session_id)

        session = get_creation_session(session_id)
        assert len(session.skill_proficiencies) == 0

    @pytest.mark.asyncio
    async def test_subspecies_validation(self):
        """Test subspecies validation."""
        session_id = "ai_var_test"

        await create_character(ruleset="dnd2024", session_id=session_id)

        # Invalid subspecies for species
        with pytest.raises(ValueError, match="Unknown subspecies"):
            await set_character_species(
                species="Dwarf",
                subspecies="Moon Elf",  # Wrong subspecies
                session_id=session_id
            )

    @pytest.mark.asyncio
    async def test_finalize_without_confirm(self):
        """Test that finalize with confirm=False doesn't create character."""
        session_id = "ai_var_test"

        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_name(name="Test", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)
        await set_character_species(species="Human", session_id=session_id)
        await set_character_background(background="Soldier", session_id=session_id)
        await assign_ability_scores(
            strength=15, dexterity=14, constitution=13,
            intelligence=12, wisdom=10, charisma=8,
            session_id=session_id
        )

        # Finalize without confirm
        result = await finalize_character(confirm=False, session_id=session_id)
        assert result["data"]["confirmed"] is False
        assert "character" not in result


class TestAIToolDataQuality:
    """Test that tools return quality data for AI consumption."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        clear_creation_session("ai_data_test")
        yield
        clear_creation_session("ai_data_test")

    @pytest.mark.asyncio
    async def test_class_info_includes_all_needed_data(self):
        """Test that set_class returns all info AI needs."""
        session_id = "ai_data_test"
        await create_character(ruleset="dnd2024", session_id=session_id)

        result = await set_character_class(class_name="Paladin", session_id=session_id)

        # AI needs this data to guide further choices
        assert "hit_die" in result["data"]
        assert "saving_throws" in result["data"]
        assert "skill_choices" in result["data"]
        assert "skill_options" in result["data"]
        assert "is_caster" in result["data"]

    @pytest.mark.asyncio
    async def test_background_info_includes_features(self):
        """Test that set_background returns feature info."""
        session_id = "ai_data_test"
        await create_character(ruleset="dnd2024", session_id=session_id)

        result = await set_character_background(background="Noble", session_id=session_id)

        # AI needs feature info for character description
        assert "feature_name" in result["data"]
        assert "skill_proficiencies" in result["data"]
        assert "ability_score_options" in result["data"]

    @pytest.mark.asyncio
    async def test_preview_includes_calculated_values(self):
        """Test that preview includes HP and modifiers."""
        session_id = "ai_data_test"

        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)
        await assign_ability_scores(
            strength=15, dexterity=14, constitution=14,
            intelligence=10, wisdom=12, charisma=8,
            session_id=session_id
        )

        result = await get_character_preview(session_id=session_id)
        preview = result["data"]["preview"]

        # Should include calculated HP
        assert "hp" in preview
        assert preview["hp"] == 12  # d10 + 2 CON

        # Should include modifier calculations
        assert preview["ability_scores"]["strength"]["modifier"] == 2
        assert preview["ability_scores"]["constitution"]["modifier"] == 2


# Tests for future AI integration (requires actual AI provider)
class TestAIIntegrationPlaceholder:
    """Placeholder tests for future AI integration testing.

    These tests document what a full AI integration test would look like.
    They are skipped by default as they require API keys.
    """

    @pytest.mark.skip(reason="Requires AI provider API key")
    @pytest.mark.asyncio
    async def test_ai_creates_character_from_prompt(self):
        """Test actual AI creating character from natural language.

        This would:
        1. Initialize ToolSession with a real AI provider
        2. Send prompt: "Create an Aasimar Paladin named Valeria"
        3. Let AI call tools autonomously
        4. Validate the created character
        """
        # from dnd_manager.ai.anthropic_provider import AnthropicProvider
        # from dnd_manager.ai.tools.session import ToolSession
        #
        # provider = AnthropicProvider(api_key="...")
        # session = ToolSession(provider=provider)
        #
        # response = await session.chat(
        #     "Create a new character: an Aasimar Paladin named Valeria Sunforge "
        #     "with the Noble background. She should prioritize Strength and Charisma."
        # )
        #
        # # Check that character was created
        # creation_session = get_creation_session()
        # assert creation_session.character is not None
        # assert creation_session.character.name == "Valeria Sunforge"
        pass

    @pytest.mark.skip(reason="Requires AI provider API key")
    @pytest.mark.asyncio
    async def test_ai_handles_errors_gracefully(self):
        """Test that AI handles tool errors and retries.

        This would test the AI's ability to:
        - Receive tool error messages
        - Understand what went wrong
        - Try alternative approaches
        """
        pass


class TestValeriaFullCreation:
    """Test creating complete level 20 Valeria using all extended AI tools.

    This is a comprehensive integration test that validates the full character
    creation workflow for a complex multiclass character based on the spec in:
    tests/fixtures/test_character_valeria.md
    """

    @pytest.fixture(autouse=True)
    def cleanup(self):
        clear_creation_session("valeria_full")
        yield
        clear_creation_session("valeria_full")

    @pytest.mark.asyncio
    async def test_create_valeria_full(self):
        """Test creating complete level 20 Valeria Sunforge.

        Valeria is a Paladin 6 / Sorcerer 14 multiclass (Sorcadin) designed
        to test all character systems including:
        - Multiclass class levels and subclasses
        - Combat stats (HP, AC, speed)
        - Hit dice pools for multiclass
        - Full proficiencies (saves, armor, weapons, tools, languages)
        - Batch features
        - Full spellcasting (cantrips, known, prepared, slots)
        - Equipment with attunement
        - Currency
        - Personality and backstory
        """
        session_id = "valeria_full"

        # Step 1: Initialize session
        result = await create_character(ruleset="dnd2024", session_id=session_id)
        assert result["data"]["session_started"] is True

        # Step 2: Set name
        result = await set_character_name(name="Valeria Sunforge", session_id=session_id)
        assert result["data"]["name"] == "Valeria Sunforge"

        # Step 3: Set multiclass levels (Paladin 6 / Sorcerer 14)
        result = await set_class_levels(
            primary_class="Paladin",
            primary_level=6,
            primary_subclass="Oath of Devotion",
            multiclass=[{
                "class": "Sorcerer",
                "level": 14,
                "subclass": "Divine Soul"
            }],
            session_id=session_id
        )
        assert result["data"]["total_level"] == 20
        assert result["data"]["primary_class"] == "Paladin"
        assert result["data"]["primary_level"] == 6
        assert len(result["data"]["multiclass"]) == 1
        assert result["data"]["multiclass"][0]["class"] == "Sorcerer"

        # Step 4: Set species
        result = await set_character_species(species="Aasimar", session_id=session_id)
        assert result["data"]["species"] == "Aasimar"

        # Step 5: Set background
        result = await set_character_background(background="Noble", session_id=session_id)
        assert result["data"]["background"] == "Noble"

        # Step 6: Assign final ability scores (after all ASIs at level 20)
        result = await assign_ability_scores(
            strength=18,
            dexterity=10,
            constitution=16,
            intelligence=8,
            wisdom=10,
            charisma=20,
            session_id=session_id
        )
        assert result["data"]["scores"]["strength"] == 18
        assert result["data"]["scores"]["charisma"] == 20

        # Step 7: Set combat stats directly
        result = await set_combat_stats(
            max_hp=156,
            armor_class=24,
            speed=30,
            session_id=session_id
        )
        assert result["data"]["max_hp"] == 156
        assert result["data"]["armor_class"] == 24
        assert result["data"]["speed"] == 30

        # Step 8: Set multiclass hit dice pools
        result = await set_hit_dice_pool(
            pools={"d10": 6, "d6": 14},
            session_id=session_id
        )
        assert result["data"]["pools"]["d10"] == 6
        assert result["data"]["pools"]["d6"] == 14

        # Step 9: Set saving throw proficiencies
        result = await set_saving_throw_proficiencies(
            saves=["wisdom", "charisma", "constitution"],
            session_id=session_id
        )
        assert set(result["data"]["saving_throws"]) == {"wisdom", "charisma", "constitution"}

        # Step 10: Set all proficiencies
        result = await set_proficiencies(
            armor=["Light Armor", "Medium Armor", "Heavy Armor", "Shields"],
            weapons=["Simple Weapons", "Martial Weapons"],
            tools=["Playing Card Set"],
            languages=["Common", "Celestial", "Elvish"],
            session_id=session_id
        )
        assert len(result["data"]["armor"]) == 4
        assert "Heavy Armor" in result["data"]["armor"]
        assert len(result["data"]["weapons"]) == 2
        assert "Playing Card Set" in result["data"]["tools"]
        assert "Celestial" in result["data"]["languages"]

        # Step 11: Add skill proficiencies
        for skill in ["Athletics", "Intimidation", "History", "Persuasion"]:
            await add_skill_proficiency(skill=skill, session_id=session_id)

        # Step 12: Add all class features
        result = await add_features(
            features=[
                # Paladin features
                {"name": "Divine Sense", "source": "Paladin 1",
                 "description": "Detect celestials, fiends, and undead within 60 feet"},
                {"name": "Lay on Hands", "source": "Paladin 1",
                 "description": "Heal HP from a pool equal to 5 × paladin level",
                 "uses": 30, "recharge": "long rest"},
                {"name": "Fighting Style: Defense", "source": "Paladin 2",
                 "description": "+1 AC while wearing armor"},
                {"name": "Divine Smite", "source": "Paladin 2",
                 "description": "Expend spell slot to deal extra radiant damage on hit"},
                {"name": "Divine Health", "source": "Paladin 3",
                 "description": "Immunity to disease"},
                {"name": "Sacred Oath: Oath of Devotion", "source": "Paladin 3",
                 "description": "Tenets: Honesty, Courage, Compassion, Honor, Duty"},
                {"name": "Channel Divinity", "source": "Paladin 3",
                 "description": "Sacred Weapon or Turn the Unholy",
                 "uses": 1, "recharge": "short rest"},
                {"name": "Extra Attack", "source": "Paladin 5",
                 "description": "Attack twice when taking the Attack action"},
                {"name": "Aura of Protection", "source": "Paladin 6",
                 "description": "+CHA modifier to all saving throws within 10 feet"},
                # Sorcerer features
                {"name": "Font of Magic", "source": "Sorcerer 2",
                 "description": "14 sorcery points for Metamagic",
                 "uses": 14, "recharge": "long rest"},
                {"name": "Metamagic: Quickened Spell", "source": "Sorcerer 3",
                 "description": "Cast spell as bonus action for 2 sorcery points"},
                {"name": "Metamagic: Twinned Spell", "source": "Sorcerer 3",
                 "description": "Target second creature with single-target spell"},
                {"name": "Metamagic: Subtle Spell", "source": "Sorcerer 10",
                 "description": "Cast without verbal or somatic components"},
                {"name": "Metamagic: Extended Spell", "source": "Sorcerer 10",
                 "description": "Double spell duration"},
                # Divine Soul features
                {"name": "Divine Magic", "source": "Divine Soul 1",
                 "description": "Access to Cleric spell list"},
                {"name": "Favored by the Gods", "source": "Divine Soul 1",
                 "description": "Add 2d4 to failed save or missed attack",
                 "uses": 1, "recharge": "short rest"},
                {"name": "Empowered Healing", "source": "Divine Soul 6",
                 "description": "Reroll healing dice for 1 sorcery point"},
                {"name": "Angelic Form", "source": "Divine Soul 14",
                 "description": "Spectral wings grant 30 ft fly speed as bonus action"},
                {"name": "Sorcerous Restoration", "source": "Sorcerer 20",
                 "description": "Regain 4 sorcery points on short rest"},
                # Aasimar features
                {"name": "Celestial Resistance", "source": "Aasimar",
                 "description": "Resistance to necrotic and radiant damage"},
                {"name": "Darkvision", "source": "Aasimar",
                 "description": "See in dim light within 60 feet as bright light"},
                {"name": "Healing Hands", "source": "Aasimar",
                 "description": "Heal HP equal to your level once per long rest",
                 "uses": 1, "recharge": "long rest"},
                {"name": "Light Bearer", "source": "Aasimar",
                 "description": "Know the Light cantrip"},
                {"name": "Radiant Soul", "source": "Aasimar",
                 "description": "Celestial revelation: wings and radiant damage bonus",
                 "uses": 1, "recharge": "long rest"},
            ],
            session_id=session_id
        )
        assert result["data"]["count"] == 24
        assert result["data"]["total_features"] == 24

        # Step 13: Set full spellcasting
        result = await set_spellcasting(
            ability="charisma",
            cantrips=["Fire Bolt", "Light", "Mage Hand", "Minor Illusion",
                     "Prestidigitation", "Toll the Dead"],
            known=["Shield", "Absorb Elements", "Healing Word", "Misty Step",
                   "Hold Person", "Counterspell", "Fireball", "Haste",
                   "Polymorph", "Greater Invisibility", "Dimension Door",
                   "Holy Weapon", "Mass Cure Wounds", "Disintegrate", "Wish"],
            prepared=["Bless", "Command", "Cure Wounds", "Divine Favor",
                     "Shield of Faith", "Aid", "Find Steed", "Lesser Restoration"],
            slots={1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
            session_id=session_id
        )
        assert result["data"]["ability"] == "charisma"
        assert result["data"]["cantrips_count"] == 6
        assert result["data"]["known_count"] == 15
        assert result["data"]["prepared_count"] == 8
        assert result["data"]["slots"][9] == 1  # 9th level slot

        # Step 14: Add equipment with attunement
        result = await add_equipment(
            items=[
                # Weapons
                {"name": "Holy Avenger (+3 Longsword)", "quantity": 1, "weight": 3.0,
                 "description": "+3 longsword, +2d10 radiant vs fiends/undead, aura of protection",
                 "equipped": True, "attuned": True},
                {"name": "Javelin", "quantity": 3, "weight": 2.0,
                 "description": "Thrown (30/120), 1d6 piercing",
                 "equipped": True, "attuned": False},
                # Armor
                {"name": "+1 Plate Armor", "quantity": 1, "weight": 65.0,
                 "description": "AC 19, heavy armor",
                 "equipped": True, "attuned": False},
                {"name": "+1 Shield", "quantity": 1, "weight": 6.0,
                 "description": "+3 AC total with magic bonus",
                 "equipped": True, "attuned": False},
                # Magic items (attuned)
                {"name": "Amulet of Proof Against Detection and Location", "quantity": 1, "weight": 0.5,
                 "description": "Hidden from divination magic",
                 "equipped": True, "attuned": True},
                {"name": "Cloak of Protection", "quantity": 1, "weight": 1.0,
                 "description": "+1 AC and saving throws",
                 "equipped": True, "attuned": True},
                # Other gear
                {"name": "Explorer's Pack", "quantity": 1, "weight": 59.0,
                 "description": "Backpack, bedroll, mess kit, tinderbox, torches, rations, waterskin, rope"},
                {"name": "Holy Symbol (Shield)", "quantity": 1, "weight": 0.0,
                 "description": "Embedded in shield"},
                {"name": "Fine Clothes", "quantity": 1, "weight": 6.0,
                 "description": "Noble attire"},
                {"name": "Signet Ring", "quantity": 1, "weight": 0.0,
                 "description": "Sunforge family seal"},
                {"name": "Scroll of Pedigree", "quantity": 1, "weight": 0.0,
                 "description": "Proof of noble lineage"},
            ],
            session_id=session_id
        )
        assert result["data"]["count"] == 11
        assert result["data"]["attuned_count"] == 3

        # Step 15: Set currency
        result = await set_currency(
            pp=50,
            gp=2500,
            ep=0,
            sp=0,
            cp=0,
            session_id=session_id
        )
        assert result["data"]["currency"]["pp"] == 50
        assert result["data"]["currency"]["gp"] == 2500
        # 50 PP = 500 GP equivalent, total = 3000 GP equivalent
        assert result["data"]["total_gp"] == 3000.0

        # Step 16: Set personality
        result = await set_personality(
            traits=[
                "I always speak with formal courtesy, befitting my noble station.",
                "I believe in leading by example and inspiring others through action."
            ],
            ideals=[
                "Honor: I will always do what is right, regardless of personal cost."
            ],
            bonds=[
                "I serve the celestial being who blessed my bloodline.",
                "I must protect the innocent and uphold justice in my family's name."
            ],
            flaws=[
                "I can be prideful and sometimes underestimate my opponents.",
                "I struggle to forgive those who have wronged my family."
            ],
            backstory=(
                "Born to the noble Sunforge family, Valeria was blessed at birth by a "
                "celestial patron who sensed great destiny in her bloodline. Raised with "
                "the values of honor and duty, she trained as a paladin but her innate "
                "divine magic manifested as sorcerous power. Now she walks the path of "
                "both oath-bound warrior and conduit of celestial energy, seeking to "
                "bring light to the darkest corners of the realm."
            ),
            session_id=session_id
        )
        assert len(result["data"]["traits"]) == 2
        assert len(result["data"]["ideals"]) == 1
        assert len(result["data"]["bonds"]) == 2
        assert len(result["data"]["flaws"]) == 2
        assert result["data"]["has_backstory"] is True

        # Step 17: Preview before finalizing
        result = await get_character_preview(session_id=session_id)
        assert result["data"]["is_complete"] is True
        preview = result["data"]["preview"]
        assert preview["name"] == "Valeria Sunforge"
        assert preview["class"] == "Paladin"  # Primary class

        # Step 18: Finalize character
        result = await finalize_character(confirm=True, session_id=session_id)
        assert result["data"]["character_created"] is True
        char = result["character"]

        # === VALIDATION ===
        # Basic info
        assert char.name == "Valeria Sunforge"
        assert char.species == "Aasimar"
        assert char.background == "Noble"

        # Class levels
        assert char.primary_class.name == "Paladin"
        assert char.primary_class.level == 6
        assert char.primary_class.subclass == "Oath of Devotion"
        assert char.total_level == 20
        assert char.is_multiclass() is True

        # Multiclass validation
        multiclass_names = [c.name for c in char.multiclass]
        assert "Sorcerer" in multiclass_names
        sorcerer = next(c for c in char.multiclass if c.name == "Sorcerer")
        assert sorcerer.level == 14
        assert sorcerer.subclass == "Divine Soul"

        # Ability scores (final values)
        assert char.abilities.strength.total == 18
        assert char.abilities.dexterity.total == 10
        assert char.abilities.constitution.total == 16
        assert char.abilities.intelligence.total == 8
        assert char.abilities.wisdom.total == 10
        assert char.abilities.charisma.total == 20

        # Combat stats
        assert char.combat.hit_points.maximum == 156
        assert char.combat.armor_class == 24
        assert char.combat.speed == 30

        # Hit dice pools
        assert char.combat.hit_dice_pool.pools["d10"].total == 6
        assert char.combat.hit_dice_pool.pools["d6"].total == 14

        # Saving throw proficiencies
        assert Ability.WISDOM in char.proficiencies.saving_throws
        assert Ability.CHARISMA in char.proficiencies.saving_throws
        assert Ability.CONSTITUTION in char.proficiencies.saving_throws

        # Skill proficiencies
        assert Skill.ATHLETICS in char.proficiencies.skills
        assert Skill.INTIMIDATION in char.proficiencies.skills
        assert Skill.HISTORY in char.proficiencies.skills
        assert Skill.PERSUASION in char.proficiencies.skills

        # Armor/weapon proficiencies
        assert "Heavy Armor" in char.proficiencies.armor
        assert "Shields" in char.proficiencies.armor
        assert "Martial Weapons" in char.proficiencies.weapons

        # Tool proficiencies and languages
        assert "Playing Card Set" in char.proficiencies.tools
        assert "Common" in char.proficiencies.languages
        assert "Celestial" in char.proficiencies.languages

        # Features
        feature_names = [f.name for f in char.features]
        assert "Divine Smite" in feature_names
        assert "Aura of Protection" in feature_names
        assert "Extra Attack" in feature_names
        assert "Metamagic: Quickened Spell" in feature_names
        assert "Angelic Form" in feature_names
        assert len(char.features) == 24

        # Spellcasting
        assert char.spellcasting.ability == Ability.CHARISMA
        assert len(char.spellcasting.cantrips) == 6
        assert "Fire Bolt" in char.spellcasting.cantrips
        assert "Wish" in char.spellcasting.known
        assert "Bless" in char.spellcasting.prepared
        assert char.spellcasting.slots[9].total == 1  # 9th level slot

        # Equipment
        item_names = [item.name for item in char.equipment.items]
        assert "Holy Avenger (+3 Longsword)" in item_names
        assert "+1 Plate Armor" in item_names
        assert "Cloak of Protection" in item_names
        attuned_items = [item for item in char.equipment.items if item.attuned]
        assert len(attuned_items) == 3

        # Currency
        assert char.equipment.currency.pp == 50
        assert char.equipment.currency.gp == 2500

        # Personality
        assert len(char.personality.traits) == 2
        assert len(char.personality.ideals) == 1
        assert len(char.personality.bonds) == 2
        assert len(char.personality.flaws) == 2
        assert "celestial" in char.backstory.lower()

    @pytest.mark.asyncio
    async def test_valeria_validation_checklist(self):
        """Validate specific checklist items from test_character_valeria.md."""
        session_id = "valeria_full"

        # Create Valeria using abbreviated setup
        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_name(name="Valeria Sunforge", session_id=session_id)
        await set_class_levels(
            primary_class="Paladin", primary_level=6, primary_subclass="Oath of Devotion",
            multiclass=[{"class": "Sorcerer", "level": 14, "subclass": "Divine Soul"}],
            session_id=session_id
        )
        await set_character_species(species="Aasimar", session_id=session_id)
        await set_character_background(background="Noble", session_id=session_id)
        await assign_ability_scores(
            strength=18, dexterity=10, constitution=16,
            intelligence=8, wisdom=10, charisma=20,
            session_id=session_id
        )
        await set_combat_stats(max_hp=156, armor_class=24, speed=30, session_id=session_id)
        await set_hit_dice_pool(pools={"d10": 6, "d6": 14}, session_id=session_id)
        await set_saving_throw_proficiencies(
            saves=["wisdom", "charisma", "constitution"],
            session_id=session_id
        )
        await set_proficiencies(
            armor=["Light Armor", "Medium Armor", "Heavy Armor", "Shields"],
            weapons=["Simple Weapons", "Martial Weapons"],
            tools=["Playing Card Set"],
            languages=["Common", "Celestial", "Elvish"],
            session_id=session_id
        )
        for skill in ["Athletics", "Intimidation", "History", "Persuasion"]:
            await add_skill_proficiency(skill=skill, session_id=session_id)
        await set_spellcasting(
            ability="charisma",
            cantrips=["Fire Bolt", "Light", "Mage Hand", "Minor Illusion", "Prestidigitation", "Toll the Dead"],
            known=["Shield", "Absorb Elements", "Healing Word", "Misty Step", "Hold Person",
                   "Counterspell", "Fireball", "Haste", "Polymorph", "Greater Invisibility",
                   "Dimension Door", "Holy Weapon", "Mass Cure Wounds", "Disintegrate", "Wish"],
            prepared=["Bless", "Command", "Cure Wounds", "Divine Favor", "Shield of Faith",
                     "Aid", "Find Steed", "Lesser Restoration"],
            slots={1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
            session_id=session_id
        )
        await set_currency(pp=50, gp=2500, session_id=session_id)

        result = await finalize_character(confirm=True, session_id=session_id)
        char = result["character"]

        # Validation checklist from test_character_valeria.md
        assert char.name == "Valeria Sunforge", "Name check"
        assert char.species == "Aasimar", "Species check"
        assert char.background == "Noble", "Background check"
        assert char.total_level == 20, "Total level check"
        assert char.primary_class.level == 6, "Paladin level check"
        sorcerer = next(c for c in char.multiclass if c.name == "Sorcerer")
        assert sorcerer.level == 14, "Sorcerer level check"
        assert char.abilities.strength.total == 18, "STR check"
        assert char.abilities.dexterity.total == 10, "DEX check"
        assert char.abilities.constitution.total == 16, "CON check"
        assert char.abilities.intelligence.total == 8, "INT check"
        assert char.abilities.wisdom.total == 10, "WIS check"
        assert char.abilities.charisma.total == 20, "CHA check"
        assert char.combat.hit_points.maximum == 156, "HP check"
        assert "Heavy Armor" in char.proficiencies.armor, "Heavy armor proficiency check"
        assert len(char.spellcasting.cantrips) == 6, "Cantrip count check"
        assert len(char.spellcasting.prepared) == 8, "Paladin prepared spells check"
        assert len(char.spellcasting.known) == 15, "Sorcerer spells known check"
        # 17th level caster slot check
        assert char.spellcasting.slots[9].total == 1, "9th level slot check"
        # Currency check: 50 PP + 2500 GP = 2550 GP equivalent (or 3000 counting PP as 10 GP each)
        assert char.equipment.currency.pp == 50, "PP check"
        assert char.equipment.currency.gp == 2500, "GP check"
