"""Tests for AI character creation tools."""

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
    suggest_build,
    create_advancement_plan,
    get_creation_session,
    clear_creation_session,
)


class TestCreationSession:
    """Tests for creation session management."""

    def test_get_creates_new_session(self):
        """Test that get_creation_session creates a new session if none exists."""
        clear_creation_session("test_new")
        session = get_creation_session("test_new")
        assert session is not None
        assert session.ruleset is None

    def test_clear_removes_session(self):
        """Test that clear_creation_session removes the session."""
        get_creation_session("test_clear")
        clear_creation_session("test_clear")
        # Getting again should create a fresh session
        session = get_creation_session("test_clear")
        assert session.ruleset is None


class TestCreateCharacter:
    """Tests for create_character tool."""

    @pytest.mark.asyncio
    async def test_create_character_sets_ruleset(self):
        """Test that create_character sets the ruleset."""
        clear_creation_session("test_ruleset")
        result = await create_character(ruleset="dnd2024", session_id="test_ruleset")

        assert result["data"]["ruleset"] == "dnd2024"
        session = get_creation_session("test_ruleset")
        assert session.ruleset == "dnd2024"

    @pytest.mark.asyncio
    async def test_create_character_clears_previous(self):
        """Test that create_character clears any previous session."""
        # Set up a previous session
        session = get_creation_session("test_clear_prev")
        session.name = "Old Character"

        # Create new character
        await create_character(ruleset="dnd2014", session_id="test_clear_prev")

        session = get_creation_session("test_clear_prev")
        assert session.name is None  # Should be cleared


class TestSetCharacterAttributes:
    """Tests for setting character attributes."""

    @pytest.fixture
    def session_id(self):
        """Provide a unique session ID and clean up."""
        sid = "test_attrs"
        clear_creation_session(sid)
        return sid

    @pytest.mark.asyncio
    async def test_set_name(self, session_id):
        """Test setting character name."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_character_name(name="Thorin", session_id=session_id)

        assert result["data"]["name"] == "Thorin"
        session = get_creation_session(session_id)
        assert session.name == "Thorin"

    @pytest.mark.asyncio
    async def test_set_class(self, session_id):
        """Test setting character class."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_character_class(class_name="Fighter", session_id=session_id)

        assert result["data"]["class"] == "Fighter"
        assert result["data"]["hit_die"] == "d10"
        session = get_creation_session(session_id)
        assert session.class_name == "Fighter"

    @pytest.mark.asyncio
    async def test_set_invalid_class_raises(self, session_id):
        """Test that setting invalid class raises error."""
        await create_character(ruleset="dnd2024", session_id=session_id)

        with pytest.raises(ValueError, match="Unknown class"):
            await set_character_class(class_name="InvalidClass", session_id=session_id)

    @pytest.mark.asyncio
    async def test_set_species(self, session_id):
        """Test setting character species."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_character_species(species="Dwarf", session_id=session_id)

        assert result["data"]["species"] == "Dwarf"
        session = get_creation_session(session_id)
        assert session.species_name == "Dwarf"

    @pytest.mark.asyncio
    async def test_set_species_with_subspecies(self, session_id):
        """Test setting species with subspecies."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_character_species(
            species="Dwarf", subspecies="Hill Dwarf", session_id=session_id
        )

        assert result["data"]["subspecies"] == "Hill Dwarf"
        session = get_creation_session(session_id)
        assert session.subspecies_name == "Hill Dwarf"

    @pytest.mark.asyncio
    async def test_set_background(self, session_id):
        """Test setting character background."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_character_background(background="Soldier", session_id=session_id)

        assert result["data"]["background"] == "Soldier"
        session = get_creation_session(session_id)
        assert session.background_name == "Soldier"


class TestAbilityScores:
    """Tests for ability score assignment."""

    @pytest.fixture
    def session_id(self):
        sid = "test_abilities"
        clear_creation_session(sid)
        return sid

    @pytest.mark.asyncio
    async def test_assign_ability_scores(self, session_id):
        """Test assigning ability scores."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await assign_ability_scores(
            strength=15, dexterity=14, constitution=13,
            intelligence=12, wisdom=10, charisma=8,
            session_id=session_id
        )

        assert result["data"]["scores"]["strength"] == 15
        assert result["data"]["modifiers"]["strength"] == 2
        assert result["data"]["modifiers"]["charisma"] == -1

    @pytest.mark.asyncio
    async def test_set_ability_bonuses(self, session_id):
        """Test setting ability bonuses."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        await assign_ability_scores(
            strength=15, dexterity=14, constitution=13,
            intelligence=12, wisdom=10, charisma=8,
            session_id=session_id
        )
        result = await set_ability_bonuses(
            bonuses={"strength": 2, "constitution": 1},
            session_id=session_id
        )

        assert result["data"]["new_totals"]["strength"] == 17
        assert result["data"]["new_totals"]["constitution"] == 14


class TestSkillsAndSpells:
    """Tests for skill and spell selection."""

    @pytest.fixture
    def session_id(self):
        sid = "test_skills_spells"
        clear_creation_session(sid)
        return sid

    @pytest.mark.asyncio
    async def test_add_skill_proficiency(self, session_id):
        """Test adding skill proficiency."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)

        result = await add_skill_proficiency(skill="Athletics", session_id=session_id)

        assert result["data"]["skill"] == "Athletics"
        assert result["data"]["total_skills"] == 1

    @pytest.mark.asyncio
    async def test_add_duplicate_skill_raises(self, session_id):
        """Test that adding duplicate skill raises error."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)
        await add_skill_proficiency(skill="Athletics", session_id=session_id)

        with pytest.raises(ValueError, match="Already proficient"):
            await add_skill_proficiency(skill="Athletics", session_id=session_id)

    @pytest.mark.asyncio
    async def test_select_cantrips(self, session_id):
        """Test selecting cantrips."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await select_cantrips(
            cantrips=["Fire Bolt", "Mage Hand"],
            session_id=session_id
        )

        assert result["data"]["count"] == 2
        session = get_creation_session(session_id)
        assert "Fire Bolt" in session.cantrips

    @pytest.mark.asyncio
    async def test_select_spells(self, session_id):
        """Test selecting spells."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await select_spells(
            spells=["Magic Missile", "Shield"],
            session_id=session_id
        )

        assert result["data"]["count"] == 2
        session = get_creation_session(session_id)
        assert "Magic Missile" in session.spells


class TestCharacterPreviewAndFinalize:
    """Tests for preview and finalize."""

    @pytest.fixture
    def session_id(self):
        sid = "test_finalize"
        clear_creation_session(sid)
        return sid

    @pytest.mark.asyncio
    async def test_preview_incomplete_character(self, session_id):
        """Test preview shows missing fields."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_name(name="Test", session_id=session_id)

        result = await get_character_preview(session_id=session_id)

        assert result["data"]["is_complete"] is False
        assert "class" in result["data"]["missing_fields"]

    @pytest.mark.asyncio
    async def test_finalize_incomplete_raises(self, session_id):
        """Test finalizing incomplete character raises error."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_name(name="Test", session_id=session_id)

        with pytest.raises(ValueError, match="Cannot finalize"):
            await finalize_character(confirm=True, session_id=session_id)

    @pytest.mark.asyncio
    async def test_finalize_without_confirm_does_nothing(self, session_id):
        """Test finalize with confirm=False doesn't create character."""
        await create_character(ruleset="dnd2024", session_id=session_id)

        result = await finalize_character(confirm=False, session_id=session_id)

        assert result["data"]["confirmed"] is False
        assert "character" not in result


class TestFullCharacterCreation:
    """End-to-end character creation tests."""

    @pytest.mark.asyncio
    async def test_create_fighter(self):
        """Test creating a complete Fighter character."""
        sid = "test_fighter_e2e"
        clear_creation_session(sid)

        await create_character(ruleset="dnd2024", session_id=sid)
        await set_character_name(name="Thorin", session_id=sid)
        await set_character_class(class_name="Fighter", session_id=sid)
        await set_character_species(species="Dwarf", session_id=sid)
        await set_character_background(background="Soldier", session_id=sid)
        await assign_ability_scores(
            strength=15, dexterity=10, constitution=14,
            intelligence=8, wisdom=12, charisma=13,
            session_id=sid
        )
        await set_ability_bonuses(bonuses={"strength": 2, "constitution": 1}, session_id=sid)
        await add_skill_proficiency(skill="Athletics", session_id=sid)
        await add_skill_proficiency(skill="Intimidation", session_id=sid)

        result = await finalize_character(confirm=True, session_id=sid)

        assert "character" in result
        char = result["character"]
        assert char.name == "Thorin"
        assert char.primary_class.name == "Fighter"
        assert char.species == "Dwarf"
        assert char.combat.hit_points.maximum == 12  # d10 + 2 CON
        assert char.abilities.strength.total == 17  # 15 + 2

    @pytest.mark.asyncio
    async def test_create_wizard(self):
        """Test creating a complete Wizard character with spells."""
        sid = "test_wizard_e2e"
        clear_creation_session(sid)

        await create_character(ruleset="dnd2024", session_id=sid)
        await set_character_name(name="Gandalf", session_id=sid)
        await set_character_class(class_name="Wizard", session_id=sid)
        await set_character_species(species="Human", session_id=sid)
        await set_character_background(background="Sage", session_id=sid)
        await assign_ability_scores(
            strength=8, dexterity=14, constitution=13,
            intelligence=15, wisdom=12, charisma=10,
            session_id=sid
        )
        await set_ability_bonuses(bonuses={"intelligence": 2, "constitution": 1}, session_id=sid)
        await add_skill_proficiency(skill="Arcana", session_id=sid)
        await add_skill_proficiency(skill="History", session_id=sid)
        await select_cantrips(cantrips=["Fire Bolt", "Mage Hand", "Prestidigitation"], session_id=sid)
        await select_spells(spells=["Magic Missile", "Shield", "Mage Armor"], session_id=sid)

        result = await finalize_character(confirm=True, session_id=sid)

        assert "character" in result
        char = result["character"]
        assert char.name == "Gandalf"
        assert char.primary_class.name == "Wizard"
        assert char.combat.hit_points.maximum == 8  # d6 + 2 CON
        assert "Fire Bolt" in char.spellcasting.cantrips
        assert "Magic Missile" in char.spellcasting.known


class TestQueryTools:
    """Tests for query tools (suggest_build, create_advancement_plan)."""

    @pytest.mark.asyncio
    async def test_suggest_build(self):
        """Test suggest_build returns concept info."""
        result = await suggest_build(concept="stealthy archer", optimization_focus="combat")

        assert result["data"]["concept"] == "stealthy archer"
        assert result["data"]["optimization_focus"] == "combat"

    @pytest.mark.asyncio
    async def test_create_advancement_plan(self):
        """Test create_advancement_plan returns planning info."""
        sid = "test_plan"
        clear_creation_session(sid)
        await create_character(ruleset="dnd2024", session_id=sid)
        await set_character_class(class_name="Fighter", session_id=sid)

        result = await create_advancement_plan(
            target_level=10,
            allow_multiclass=False,
            session_id=sid
        )

        assert result["data"]["current_class"] == "Fighter"
        assert result["data"]["target_level"] == 10
