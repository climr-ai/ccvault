"""Tests for AI character creation tools."""

from datetime import datetime, timedelta
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
    # Session management
    cleanup_expired_sessions,
    cleanup_oldest_sessions,
    get_session_count,
    clear_all_sessions,
    SESSION_TTL_HOURS,
    MAX_SESSIONS,
    _creation_sessions,
    # Extended creation tools
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


class TestSessionCleanup:
    """Tests for session cleanup and memory management."""

    def setup_method(self):
        """Clear all sessions before each test."""
        clear_all_sessions()

    def test_session_has_timestamps(self):
        """Test that sessions have created_at and last_accessed timestamps."""
        session = get_creation_session("test_timestamps")
        assert session.created_at is not None
        assert session.last_accessed is not None
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_accessed, datetime)

    def test_last_accessed_updates_on_access(self):
        """Test that last_accessed updates when session is retrieved."""
        session1 = get_creation_session("test_access")
        original_access = session1.last_accessed

        # Access again - last_accessed should update
        import time
        time.sleep(0.01)  # Small delay to ensure time difference
        session2 = get_creation_session("test_access")

        assert session2.last_accessed >= original_access

    def test_cleanup_expired_sessions(self):
        """Test that expired sessions are cleaned up."""
        # Create a session
        session = get_creation_session("test_expired")

        # Manually set last_accessed to be old
        session.last_accessed = datetime.now() - timedelta(hours=SESSION_TTL_HOURS + 1)

        # Run cleanup
        removed = cleanup_expired_sessions()

        assert removed == 1
        assert get_session_count() == 0

    def test_cleanup_keeps_recent_sessions(self):
        """Test that recent sessions are not cleaned up."""
        # Create a recent session
        get_creation_session("test_recent")

        # Run cleanup - should not remove
        removed = cleanup_expired_sessions()

        assert removed == 0
        assert get_session_count() == 1

    def test_cleanup_oldest_sessions(self):
        """Test that oldest sessions are removed when limit exceeded."""
        # Create many sessions
        for i in range(10):
            session = get_creation_session(f"test_oldest_{i}")
            # Stagger last_accessed times
            session.last_accessed = datetime.now() - timedelta(minutes=10 - i)

        assert get_session_count() == 10

        # Cleanup to keep only 5
        removed = cleanup_oldest_sessions(keep_count=5)

        assert removed == 5
        assert get_session_count() == 5

        # Verify oldest sessions were removed (0-4 should be gone)
        # and newest kept (5-9 should remain)
        assert "test_oldest_0" not in _creation_sessions
        assert "test_oldest_9" in _creation_sessions

    def test_get_session_count(self):
        """Test get_session_count returns correct count."""
        assert get_session_count() == 0

        get_creation_session("test_count_1")
        assert get_session_count() == 1

        get_creation_session("test_count_2")
        assert get_session_count() == 2

    def test_clear_all_sessions(self):
        """Test clear_all_sessions removes everything."""
        get_creation_session("test_all_1")
        get_creation_session("test_all_2")
        get_creation_session("test_all_3")

        count = clear_all_sessions()

        assert count == 3
        assert get_session_count() == 0

    def test_auto_cleanup_on_get_when_many_sessions(self):
        """Test that get_creation_session triggers cleanup when needed."""
        # Create sessions just over half the limit
        for i in range(MAX_SESSIONS // 2 + 5):
            session = get_creation_session(f"auto_cleanup_{i}")
            # Make some of them expired
            if i < 3:
                session.last_accessed = datetime.now() - timedelta(hours=SESSION_TTL_HOURS + 1)

        # Access a new session - should trigger cleanup
        get_creation_session("trigger_cleanup")

        # Expired sessions should have been cleaned
        assert "auto_cleanup_0" not in _creation_sessions


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


class TestExtendedCreationTools:
    """Tests for extended character creation tools."""

    @pytest.fixture
    def session_id(self):
        """Provide a unique session ID and clean up."""
        sid = "test_extended"
        clear_creation_session(sid)
        return sid

    @pytest.mark.asyncio
    async def test_set_class_levels_single_class(self, session_id):
        """Test setting class levels for a single class."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_class_levels(
            primary_class="Paladin",
            primary_level=6,
            primary_subclass="Oath of Devotion",
            session_id=session_id
        )

        assert result["data"]["primary_class"] == "Paladin"
        assert result["data"]["primary_level"] == 6
        assert result["data"]["total_level"] == 6

        session = get_creation_session(session_id)
        assert session.primary_level == 6
        assert session.primary_subclass == "Oath of Devotion"

    @pytest.mark.asyncio
    async def test_set_class_levels_multiclass(self, session_id):
        """Test setting class levels with multiclass."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_class_levels(
            primary_class="Paladin",
            primary_level=6,
            primary_subclass="Oath of Devotion",
            multiclass=[
                {"class": "Sorcerer", "level": 14, "subclass": "Divine Soul"}
            ],
            session_id=session_id
        )

        assert result["data"]["total_level"] == 20
        assert len(result["data"]["multiclass"]) == 1

        session = get_creation_session(session_id)
        assert session.multiclass_entries[0]["class"] == "Sorcerer"
        assert session.multiclass_entries[0]["level"] == 14

    @pytest.mark.asyncio
    async def test_set_class_levels_exceeds_20_raises(self, session_id):
        """Test that total level > 20 raises error."""
        await create_character(ruleset="dnd2024", session_id=session_id)

        with pytest.raises(ValueError, match="exceeds maximum"):
            await set_class_levels(
                primary_class="Fighter",
                primary_level=15,
                multiclass=[{"class": "Rogue", "level": 10}],
                session_id=session_id
            )

    @pytest.mark.asyncio
    async def test_set_combat_stats(self, session_id):
        """Test setting combat stats directly."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_combat_stats(
            max_hp=156,
            armor_class=24,
            speed=30,
            session_id=session_id
        )

        assert result["data"]["max_hp"] == 156
        assert result["data"]["armor_class"] == 24
        assert result["data"]["speed"] == 30

        session = get_creation_session(session_id)
        assert session.max_hp == 156
        assert session.armor_class == 24

    @pytest.mark.asyncio
    async def test_set_hit_dice_pool(self, session_id):
        """Test setting hit dice pool for multiclass."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_hit_dice_pool(
            pools={"d10": 6, "d6": 14},
            session_id=session_id
        )

        assert result["data"]["pools"]["d10"] == 6
        assert result["data"]["pools"]["d6"] == 14
        assert result["data"]["total"] == 20

    @pytest.mark.asyncio
    async def test_set_saving_throw_proficiencies(self, session_id):
        """Test setting saving throw proficiencies."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_saving_throw_proficiencies(
            saves=["wisdom", "charisma", "constitution"],
            session_id=session_id
        )

        assert len(result["data"]["saving_throws"]) == 3
        session = get_creation_session(session_id)
        assert "wisdom" in session.saving_throws

    @pytest.mark.asyncio
    async def test_set_proficiencies(self, session_id):
        """Test setting armor, weapons, tools, languages."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_proficiencies(
            armor=["Light Armor", "Heavy Armor"],
            weapons=["Simple Weapons", "Martial Weapons"],
            tools=["Playing Card Set"],
            languages=["Common", "Celestial"],
            session_id=session_id
        )

        assert "Light Armor" in result["data"]["armor"]
        assert "Martial Weapons" in result["data"]["weapons"]

    @pytest.mark.asyncio
    async def test_add_features(self, session_id):
        """Test adding multiple features."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await add_features(
            features=[
                {"name": "Divine Smite", "source": "Paladin 2", "description": "Extra radiant damage"},
                {"name": "Extra Attack", "source": "Paladin 5", "description": "Attack twice"},
                {"name": "Aura of Protection", "source": "Paladin 6", "description": "+CHA to saves"},
            ],
            session_id=session_id
        )

        assert result["data"]["count"] == 3
        assert result["data"]["total_features"] == 3

        session = get_creation_session(session_id)
        assert session.features[0]["name"] == "Divine Smite"

    @pytest.mark.asyncio
    async def test_set_spellcasting(self, session_id):
        """Test setting full spellcasting config."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_spellcasting(
            ability="charisma",
            cantrips=["Fire Bolt", "Light"],
            known=["Shield", "Misty Step", "Fireball"],
            prepared=["Bless", "Cure Wounds"],
            slots={1: 4, 2: 3, 3: 3},
            session_id=session_id
        )

        assert result["data"]["ability"] == "charisma"
        assert result["data"]["cantrips_count"] == 2
        assert result["data"]["known_count"] == 3
        assert result["data"]["prepared_count"] == 2

        session = get_creation_session(session_id)
        assert session.spell_slots[1] == 4
        assert session.spell_slots[2] == 3

    @pytest.mark.asyncio
    async def test_add_equipment(self, session_id):
        """Test adding equipment items."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await add_equipment(
            items=[
                {"name": "Holy Avenger", "equipped": True, "attuned": True},
                {"name": "+1 Plate Armor", "equipped": True},
                {"name": "Javelin", "quantity": 3},
            ],
            session_id=session_id
        )

        assert result["data"]["count"] == 3
        assert result["data"]["attuned_count"] == 1

    @pytest.mark.asyncio
    async def test_add_equipment_exceeds_attunement_raises(self, session_id):
        """Test that > 3 attuned items raises error."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        await add_equipment(
            items=[
                {"name": "Item 1", "attuned": True},
                {"name": "Item 2", "attuned": True},
                {"name": "Item 3", "attuned": True},
            ],
            session_id=session_id
        )

        with pytest.raises(ValueError, match="exceed limit"):
            await add_equipment(
                items=[{"name": "Item 4", "attuned": True}],
                session_id=session_id
            )

    @pytest.mark.asyncio
    async def test_set_currency(self, session_id):
        """Test setting currency."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_currency(
            pp=50, gp=2500, ep=0, sp=0, cp=0,
            session_id=session_id
        )

        assert result["data"]["currency"]["pp"] == 50
        assert result["data"]["currency"]["gp"] == 2500
        assert result["data"]["total_gp"] == 3000.0

    @pytest.mark.asyncio
    async def test_set_personality(self, session_id):
        """Test setting personality."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        result = await set_personality(
            traits=["I speak formally"],
            ideals=["Honor above all"],
            bonds=["My family"],
            flaws=["Too proud"],
            backstory="Born to nobility...",
            session_id=session_id
        )

        assert len(result["data"]["traits"]) == 1
        assert result["data"]["has_backstory"] is True

        session = get_creation_session(session_id)
        assert session.backstory == "Born to nobility..."


class TestExtendedCharacterFinalization:
    """Test finalize_character with extended fields."""

    @pytest.fixture
    def session_id(self):
        sid = "test_finalize_ext"
        clear_creation_session(sid)
        return sid

    @pytest.mark.asyncio
    async def test_finalize_multiclass_character(self, session_id):
        """Test finalizing a multiclass character."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_name(name="Valeria", session_id=session_id)
        await set_class_levels(
            primary_class="Paladin",
            primary_level=6,
            primary_subclass="Oath of Devotion",
            multiclass=[{"class": "Sorcerer", "level": 4, "subclass": "Divine Soul"}],
            session_id=session_id
        )
        await set_character_species(species="Human", session_id=session_id)
        await set_character_background(background="Noble", session_id=session_id)
        await assign_ability_scores(
            strength=16, dexterity=10, constitution=14,
            intelligence=8, wisdom=10, charisma=18,
            session_id=session_id
        )
        await set_combat_stats(max_hp=75, armor_class=20, session_id=session_id)
        await set_hit_dice_pool(pools={"d10": 6, "d6": 4}, session_id=session_id)
        await set_saving_throw_proficiencies(
            saves=["wisdom", "charisma"],
            session_id=session_id
        )

        result = await finalize_character(confirm=True, session_id=session_id)

        assert result["data"]["character_created"] is True
        assert result["data"]["total_level"] == 10
        assert "Paladin 6 / Sorcerer 4" in result["data"]["class"]

        char = result["character"]
        assert char.name == "Valeria"
        assert char.total_level == 10
        assert char.is_multiclass() is True
        assert char.combat.hit_points.maximum == 75
        assert char.combat.armor_class == 20
        assert "d10" in char.combat.hit_dice_pool.pools
        assert "d6" in char.combat.hit_dice_pool.pools

    @pytest.mark.asyncio
    async def test_finalize_with_spellcasting(self, session_id):
        """Test finalizing a character with spellcasting."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_name(name="Wizard", session_id=session_id)
        await set_character_class(class_name="Wizard", session_id=session_id)
        await set_character_species(species="Elf", session_id=session_id)
        await set_character_background(background="Sage", session_id=session_id)
        await assign_ability_scores(
            strength=8, dexterity=14, constitution=12,
            intelligence=17, wisdom=10, charisma=10,
            session_id=session_id
        )
        await set_spellcasting(
            ability="intelligence",
            cantrips=["Fire Bolt", "Light", "Mage Hand"],
            known=["Magic Missile", "Shield"],
            prepared=["Detect Magic"],
            slots={1: 4, 2: 3},
            session_id=session_id
        )

        result = await finalize_character(confirm=True, session_id=session_id)

        char = result["character"]
        assert len(char.spellcasting.cantrips) == 3
        assert "Magic Missile" in char.spellcasting.known
        assert "Detect Magic" in char.spellcasting.prepared
        assert char.spellcasting.slots[1].total == 4

    @pytest.mark.asyncio
    async def test_finalize_with_equipment(self, session_id):
        """Test finalizing a character with equipment."""
        await create_character(ruleset="dnd2024", session_id=session_id)
        await set_character_name(name="Fighter", session_id=session_id)
        await set_character_class(class_name="Fighter", session_id=session_id)
        await set_character_species(species="Human", session_id=session_id)
        await set_character_background(background="Soldier", session_id=session_id)
        await assign_ability_scores(
            strength=16, dexterity=14, constitution=14,
            intelligence=10, wisdom=10, charisma=10,
            session_id=session_id
        )
        await add_equipment(
            items=[
                {"name": "Longsword", "equipped": True},
                {"name": "Shield", "equipped": True},
                {"name": "Chain Mail", "equipped": True},
            ],
            session_id=session_id
        )
        await set_currency(gp=100, session_id=session_id)

        result = await finalize_character(confirm=True, session_id=session_id)

        char = result["character"]
        assert len(char.equipment.items) == 3
        assert char.equipment.currency.gp == 100
        assert any(i.name == "Longsword" for i in char.equipment.items)
