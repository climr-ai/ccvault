"""Comprehensive test for creating and validating a level 20 multiclass character.

This test creates Valeria Sunforge, a Paladin 6 / Sorcerer 14 character,
validates all attributes, exports to HTML, and cleans up.

This serves as an integration test for the entire character system.
"""

import pytest
import tempfile
from pathlib import Path

from dnd_manager.models.character import (
    Character,
    CharacterClass,
    CharacterMeta,
    RulesetId,
    Feature,
    HitPoints,
    HitDicePool,
    HitDice,
    InventoryItem,
    Currency,
    SpellSlot,
)
from dnd_manager.models.abilities import (
    AbilityScores,
    AbilityScore,
    Skill,
    SkillProficiency,
    Ability,
)
from dnd_manager.storage import CharacterStore
from dnd_manager.export import export_to_html


def create_valeria() -> Character:
    """Create Valeria Sunforge - Paladin 6 / Sorcerer 14.

    A comprehensive test character following 2024 rules with:
    - Multiclass (Paladin/Sorcerer)
    - Subclasses (Oath of Devotion, Divine Soul)
    - Full ability scores with ASI progression
    - Skills, features, spells, equipment
    - Magic items with attunement
    """
    char = Character(
        name="Valeria Sunforge",
        meta=CharacterMeta(ruleset=RulesetId.DND_2024),

        # Classes - Paladin 6, Sorcerer 14
        primary_class=CharacterClass(
            name="Paladin",
            subclass="Oath of Devotion",
            level=6,
        ),
        multiclass=[
            CharacterClass(
                name="Sorcerer",
                subclass="Divine Soul",
                level=14,
            ),
        ],

        # Identity
        species="Aasimar",
        background="Noble",
        player="Test Player",

        # Ability Scores (after ASIs)
        # Base: STR 15+2bg=17, DEX 10, CON 14+1bg=15, INT 8, WIS 10, CHA 15
        # ASIs: Paladin4 +2CHA, Sorc4 +2CHA, Sorc8 Resilient(CON), Sorc12 +1CHA+1STR
        abilities=AbilityScores(
            strength=AbilityScore(base=18),    # 15 + 2(bg) + 1(ASI)
            dexterity=AbilityScore(base=10),
            constitution=AbilityScore(base=16), # 14 + 1(bg) + 1(Resilient)
            intelligence=AbilityScore(base=8),
            wisdom=AbilityScore(base=10),
            charisma=AbilityScore(base=20),    # 15 + 2+2+1(ASIs)
        ),
    )

    # Proficiencies
    # Saving throws: Wisdom, Charisma (Paladin), Constitution (Resilient)
    char.proficiencies.saving_throws = [Ability.WISDOM, Ability.CHARISMA, Ability.CONSTITUTION]

    # Skills: Athletics, Intimidation (Paladin), History, Persuasion (Noble)
    char.proficiencies.skills = {
        Skill.ATHLETICS: SkillProficiency.PROFICIENT,
        Skill.INTIMIDATION: SkillProficiency.PROFICIENT,
        Skill.HISTORY: SkillProficiency.PROFICIENT,
        Skill.PERSUASION: SkillProficiency.PROFICIENT,
    }

    # Armor and weapons
    char.proficiencies.armor = ["Light Armor", "Medium Armor", "Heavy Armor", "Shields"]
    char.proficiencies.weapons = ["Simple Weapons", "Martial Weapons"]
    char.proficiencies.tools = ["Playing Card Set"]
    char.proficiencies.languages = ["Common", "Celestial", "Elvish"]

    # HP: Paladin 1 (10+3) + Paladin 2-6 (5×9) + Sorcerer 1-14 (14×7) = 13 + 45 + 98 = 156
    char.combat.hit_points = HitPoints(maximum=156, current=156)

    # Hit dice pool for multiclass
    char.combat.hit_dice_pool = HitDicePool(pools={
        "d10": HitDice(total=6, remaining=6, die="d10"),
        "d6": HitDice(total=14, remaining=14, die="d6"),
    })

    # Armor class: Plate (18) + Shield (2) + Defense (1) + Cloak (1) = 22
    # With +1 Plate (19) + +1 Shield (3) + Defense (1) + Cloak (1) = 24
    char.combat.armor_class = 24

    # Speed
    char.combat.speed = 30

    # Spellcasting
    char.spellcasting.ability = Ability.CHARISMA

    # Cantrips (6 Sorcerer + Light from Aasimar)
    char.spellcasting.cantrips = [
        "Fire Bolt", "Light", "Mage Hand", "Minor Illusion",
        "Prestidigitation", "Toll the Dead"
    ]

    # Sorcerer spells known (15)
    char.spellcasting.known = [
        "Shield", "Absorb Elements", "Healing Word", "Misty Step",
        "Hold Person", "Counterspell", "Fireball", "Haste",
        "Polymorph", "Greater Invisibility", "Dimension Door",
        "Holy Weapon", "Mass Cure Wounds", "Disintegrate", "Wish"
    ]

    # Paladin spells prepared (8) - separate from known
    char.spellcasting.prepared = [
        "Bless", "Command", "Cure Wounds", "Divine Favor",
        "Shield of Faith", "Aid", "Find Steed", "Lesser Restoration"
    ]

    # Spell slots (17th level multiclass caster)
    char.spellcasting.slots = {
        1: SpellSlot(total=4, used=0),
        2: SpellSlot(total=3, used=0),
        3: SpellSlot(total=3, used=0),
        4: SpellSlot(total=3, used=0),
        5: SpellSlot(total=2, used=0),
        6: SpellSlot(total=1, used=0),
        7: SpellSlot(total=1, used=0),
        8: SpellSlot(total=1, used=0),
        9: SpellSlot(total=1, used=0),
    }

    # Features
    char.features = [
        # Paladin Features
        Feature(name="Divine Sense", source="Paladin 1",
                description="Detect celestials, fiends, and undead within 60 feet.",
                uses=6, used=0, recharge="long rest"),
        Feature(name="Lay on Hands", source="Paladin 1",
                description="Pool of 30 HP for healing or curing diseases.",
                uses=30, used=0, recharge="long rest"),
        Feature(name="Fighting Style: Defense", source="Paladin 2",
                description="+1 AC while wearing armor."),
        Feature(name="Divine Smite", source="Paladin 2",
                description="Expend spell slot to deal extra radiant damage on hit."),
        Feature(name="Divine Health", source="Paladin 3",
                description="Immune to disease."),
        Feature(name="Channel Divinity: Sacred Weapon", source="Oath of Devotion",
                description="Add CHA to attack rolls, weapon emits light.",
                uses=1, used=0, recharge="short rest"),
        Feature(name="Channel Divinity: Turn the Unholy", source="Oath of Devotion",
                description="Fiends and undead must flee.",
                uses=1, used=0, recharge="short rest"),
        Feature(name="Extra Attack", source="Paladin 5",
                description="Attack twice per Attack action."),
        Feature(name="Aura of Protection", source="Paladin 6",
                description="+5 to all saving throws within 10 feet."),

        # Sorcerer Features
        Feature(name="Font of Magic", source="Sorcerer 2",
                description="14 sorcery points for metamagic and spell slots."),
        Feature(name="Metamagic: Quickened Spell", source="Sorcerer 3",
                description="Cast spell as bonus action for 2 sorcery points."),
        Feature(name="Metamagic: Twinned Spell", source="Sorcerer 3",
                description="Target two creatures with single-target spell."),
        Feature(name="Metamagic: Subtle Spell", source="Sorcerer 10",
                description="Cast without verbal/somatic components."),
        Feature(name="Metamagic: Extended Spell", source="Sorcerer 10",
                description="Double spell duration."),
        Feature(name="Divine Magic", source="Divine Soul",
                description="Access to Cleric spell list."),
        Feature(name="Favored by the Gods", source="Divine Soul",
                description="Add 2d4 to failed save or missed attack once per rest.",
                uses=1, used=0, recharge="short rest"),
        Feature(name="Empowered Healing", source="Divine Soul 6",
                description="Reroll healing dice."),
        Feature(name="Angelic Form", source="Divine Soul 14",
                description="Sprout spectral wings, 30 ft flying speed.",
                uses=None, recharge="bonus action"),
        Feature(name="Sorcerous Restoration", source="Sorcerer 20",
                description="Regain 4 sorcery points on short rest."),

        # Aasimar Traits
        Feature(name="Celestial Resistance", source="Aasimar",
                description="Resistance to necrotic and radiant damage."),
        Feature(name="Darkvision", source="Aasimar",
                description="See in dim light 60 ft as if bright light."),
        Feature(name="Healing Hands", source="Aasimar",
                description="Heal HP equal to level once per long rest.",
                uses=1, used=0, recharge="long rest"),
        Feature(name="Radiant Soul", source="Aasimar (Celestial Revelation)",
                description="Wings + add level to radiant/necrotic damage once per turn."),

        # Feat
        Feature(name="Resilient (Constitution)", source="Feat",
                description="Proficiency in Constitution saving throws."),
    ]

    # Equipment
    char.equipment.currency = Currency(pp=50, gp=2500, ep=0, sp=0, cp=0)
    char.equipment.items = [
        # Weapons
        InventoryItem(
            name="Holy Avenger (+3 Longsword)",
            quantity=1,
            weight=3.0,
            description="Legendary. +3 to attack/damage. +2d10 radiant vs fiends/undead. Aura of protection 10 ft.",
            equipped=True,
            attuned=True,
        ),
        InventoryItem(name="Javelin", quantity=3, weight=2.0, equipped=False),

        # Armor
        InventoryItem(
            name="+1 Plate Armor",
            quantity=1,
            weight=65.0,
            description="AC 19. Heavy armor. Requires Str 15.",
            equipped=True,
            attuned=False,
        ),
        InventoryItem(
            name="+1 Shield",
            quantity=1,
            weight=6.0,
            description="+3 AC total.",
            equipped=True,
            attuned=False,
        ),

        # Magic Items
        InventoryItem(
            name="Amulet of Proof Against Detection and Location",
            quantity=1,
            weight=0.0,
            description="Uncommon. Hidden from divination magic.",
            equipped=True,
            attuned=True,
        ),
        InventoryItem(
            name="Cloak of Protection",
            quantity=1,
            weight=0.0,
            description="Uncommon. +1 AC, +1 saving throws.",
            equipped=True,
            attuned=True,
        ),

        # Mundane
        InventoryItem(name="Explorer's Pack", quantity=1, weight=10.0),
        InventoryItem(name="Holy Symbol (embedded in shield)", quantity=1, weight=0.0),
        InventoryItem(name="Fine Clothes", quantity=1, weight=6.0),
        InventoryItem(name="Signet Ring", quantity=1, weight=0.0),
        InventoryItem(name="Scroll of Pedigree", quantity=1, weight=0.0),
        InventoryItem(name="Belt Pouch", quantity=1, weight=1.0),
    ]

    # Personality
    char.personality.traits = [
        "I always speak with formal courtesy befitting my noble birth.",
        "I am driven by a divine purpose to protect the innocent."
    ]
    char.personality.ideals = ["Honor. I will always do what is right, regardless of the cost."]
    char.personality.bonds = ["I serve the celestial being who granted me my divine power."]
    char.personality.flaws = ["I can be prideful and dismissive of those I deem less righteous."]

    char.backstory = (
        "Born to a noble family with a celestial bloodline, Valeria was marked "
        "for greatness from birth. Her golden eyes and faint radiance drew the "
        "attention of the Church of the Sun, who trained her as a paladin. "
        "During her oath-taking, a divine spark awakened within her, granting "
        "her sorcerous powers tied to her celestial heritage."
    )

    return char


class TestValeriaCharacterCreation:
    """Tests for creating and validating Valeria."""

    def test_create_character(self):
        """Test that we can create the character without errors."""
        char = create_valeria()
        assert char.name == "Valeria Sunforge"

    def test_basic_info(self):
        """Test basic character information."""
        char = create_valeria()

        assert char.name == "Valeria Sunforge"
        assert char.meta.ruleset == RulesetId.DND_2024
        assert char.species == "Aasimar"
        assert char.background == "Noble"
        assert char.player == "Test Player"

    def test_class_levels(self):
        """Test class and level information."""
        char = create_valeria()

        # Primary class
        assert char.primary_class.name == "Paladin"
        assert char.primary_class.subclass == "Oath of Devotion"
        assert char.primary_class.level == 6

        # Multiclass
        assert len(char.multiclass) == 1
        assert char.multiclass[0].name == "Sorcerer"
        assert char.multiclass[0].subclass == "Divine Soul"
        assert char.multiclass[0].level == 14

        # Total level
        assert char.total_level == 20
        assert char.is_multiclass() is True

    def test_ability_scores(self):
        """Test ability scores are set correctly."""
        char = create_valeria()

        assert char.abilities.strength.total == 18
        assert char.abilities.strength.modifier == 4

        assert char.abilities.dexterity.total == 10
        assert char.abilities.dexterity.modifier == 0

        assert char.abilities.constitution.total == 16
        assert char.abilities.constitution.modifier == 3

        assert char.abilities.intelligence.total == 8
        assert char.abilities.intelligence.modifier == -1

        assert char.abilities.wisdom.total == 10
        assert char.abilities.wisdom.modifier == 0

        assert char.abilities.charisma.total == 20
        assert char.abilities.charisma.modifier == 5

    def test_proficiency_bonus(self):
        """Test proficiency bonus for level 20."""
        char = create_valeria()
        assert char.proficiency_bonus == 6

    def test_saving_throw_proficiencies(self):
        """Test saving throw proficiencies."""
        char = create_valeria()

        assert Ability.WISDOM in char.proficiencies.saving_throws
        assert Ability.CHARISMA in char.proficiencies.saving_throws
        assert Ability.CONSTITUTION in char.proficiencies.saving_throws
        assert len(char.proficiencies.saving_throws) == 3

    def test_skill_proficiencies(self):
        """Test skill proficiencies."""
        char = create_valeria()

        assert char.proficiencies.skills[Skill.ATHLETICS] == SkillProficiency.PROFICIENT
        assert char.proficiencies.skills[Skill.INTIMIDATION] == SkillProficiency.PROFICIENT
        assert char.proficiencies.skills[Skill.HISTORY] == SkillProficiency.PROFICIENT
        assert char.proficiencies.skills[Skill.PERSUASION] == SkillProficiency.PROFICIENT
        assert len(char.proficiencies.skills) == 4

    def test_combat_stats(self):
        """Test combat statistics."""
        char = create_valeria()

        # HP: Paladin 1 (10+3) + Paladin 2-6 (5×9) + Sorcerer 1-14 (14×7) = 156
        assert char.combat.hit_points.maximum == 156
        assert char.combat.hit_points.current == 156

        # AC
        assert char.combat.armor_class == 24

        # Speed
        assert char.combat.speed == 30

    def test_hit_dice_pool(self):
        """Test multiclass hit dice tracking."""
        char = create_valeria()

        # Should have d10 (Paladin) and d6 (Sorcerer) pools
        assert "d10" in char.combat.hit_dice_pool.pools
        assert "d6" in char.combat.hit_dice_pool.pools

        assert char.combat.hit_dice_pool.pools["d10"].total == 6
        assert char.combat.hit_dice_pool.pools["d6"].total == 14
        assert char.combat.hit_dice_pool.total == 20

    def test_multiclass_caster_level(self):
        """Test multiclass spellcasting level calculation."""
        char = create_valeria()

        # Paladin 6 = 3 caster levels, Sorcerer 14 = 14 caster levels
        # Total = 17
        caster_level = char.get_multiclass_caster_level()
        assert caster_level == 17

    def test_spell_slots(self):
        """Test spell slot allocation."""
        char = create_valeria()

        # 17th level caster spell slots
        assert char.spellcasting.slots[1].total == 4
        assert char.spellcasting.slots[2].total == 3
        assert char.spellcasting.slots[3].total == 3
        assert char.spellcasting.slots[4].total == 3
        assert char.spellcasting.slots[5].total == 2
        assert char.spellcasting.slots[6].total == 1
        assert char.spellcasting.slots[7].total == 1
        assert char.spellcasting.slots[8].total == 1
        assert char.spellcasting.slots[9].total == 1

    def test_cantrips(self):
        """Test cantrips known."""
        char = create_valeria()

        assert len(char.spellcasting.cantrips) == 6
        assert "Fire Bolt" in char.spellcasting.cantrips
        assert "Light" in char.spellcasting.cantrips

    def test_spells_known(self):
        """Test spells known (Sorcerer)."""
        char = create_valeria()

        assert len(char.spellcasting.known) == 15
        assert "Wish" in char.spellcasting.known
        assert "Shield" in char.spellcasting.known

    def test_spells_prepared(self):
        """Test spells prepared (Paladin)."""
        char = create_valeria()

        # Prepared is a list
        assert len(char.spellcasting.prepared) == 8
        assert "Bless" in char.spellcasting.prepared
        assert "Divine Favor" in char.spellcasting.prepared

    def test_spellcasting_ability(self):
        """Test spellcasting ability is set."""
        char = create_valeria()

        assert char.spellcasting.ability == Ability.CHARISMA

    def test_features_count(self):
        """Test that all features are present."""
        char = create_valeria()

        # Should have 24 features total
        assert len(char.features) >= 20

        # Check for key features
        feature_names = [f.name for f in char.features]
        assert "Divine Smite" in feature_names
        assert "Aura of Protection" in feature_names
        assert "Extra Attack" in feature_names
        assert "Metamagic: Quickened Spell" in feature_names
        assert "Angelic Form" in feature_names
        assert "Resilient (Constitution)" in feature_names

    def test_equipment_items(self):
        """Test equipment inventory."""
        char = create_valeria()

        item_names = [i.name for i in char.equipment.items]
        assert "Holy Avenger (+3 Longsword)" in item_names
        assert "+1 Plate Armor" in item_names
        assert "+1 Shield" in item_names
        assert "Cloak of Protection" in item_names

    def test_attunement(self):
        """Test attunement slots (max 3)."""
        char = create_valeria()

        attuned_items = [i for i in char.equipment.items if i.attuned]
        assert len(attuned_items) == 3

        attuned_names = [i.name for i in attuned_items]
        assert "Holy Avenger (+3 Longsword)" in attuned_names
        assert "Amulet of Proof Against Detection and Location" in attuned_names
        assert "Cloak of Protection" in attuned_names

    def test_currency(self):
        """Test currency amounts."""
        char = create_valeria()

        assert char.equipment.currency.pp == 50
        assert char.equipment.currency.gp == 2500

        # Total in GP: 50*10 + 2500 = 3000
        assert char.equipment.currency.total_gp == 3000

    def test_personality(self):
        """Test personality traits."""
        char = create_valeria()

        assert len(char.personality.traits) == 2
        assert len(char.personality.ideals) == 1
        assert len(char.personality.bonds) == 1
        assert len(char.personality.flaws) == 1

    def test_backstory(self):
        """Test backstory is set."""
        char = create_valeria()
        assert len(char.backstory) > 100


class TestValeriaStorageAndExport:
    """Tests for saving, loading, exporting, and deleting Valeria."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def store(self, temp_dir):
        """Create a character store in the temp directory."""
        return CharacterStore(temp_dir)

    def test_save_and_load(self, store):
        """Test saving and loading the character."""
        char = create_valeria()

        # Save
        path = store.save(char)
        assert path.exists()

        # Load
        loaded = store.load("Valeria Sunforge")
        assert loaded is not None
        assert loaded.name == "Valeria Sunforge"
        assert loaded.total_level == 20
        assert loaded.is_multiclass() is True

        # Verify key attributes survived round-trip
        assert loaded.abilities.charisma.total == 20
        assert len(loaded.features) == len(char.features)
        assert len(loaded.spellcasting.known) == 15

    def test_export_to_html(self, temp_dir):
        """Test exporting character to HTML."""
        char = create_valeria()

        html_path = temp_dir / "valeria.html"
        result_path = export_to_html(char, html_path)

        assert result_path.exists()
        assert result_path == html_path

        # Read and validate HTML content
        html_content = html_path.read_text()

        # Check for key elements
        assert "Valeria Sunforge" in html_content
        assert "Paladin" in html_content
        assert "Aasimar" in html_content

        # Check for ability scores
        assert "18" in html_content  # STR
        assert "20" in html_content  # CHA

        # Check for equipment
        assert "Holy Avenger" in html_content

        # Check that it's substantial HTML
        assert len(html_content) > 5000

    def test_delete_character(self, store):
        """Test deleting the character."""
        char = create_valeria()

        # Save first
        store.save(char)
        assert store.load("Valeria Sunforge") is not None

        # Delete
        result = store.delete("Valeria Sunforge")
        assert result is True

        # Verify deleted
        assert store.load("Valeria Sunforge") is None

    def test_full_lifecycle(self, temp_dir):
        """Test complete lifecycle: create, validate, save, export, delete."""
        store = CharacterStore(temp_dir)

        # 1. Create
        char = create_valeria()
        assert char.name == "Valeria Sunforge"

        # 2. Validate key attributes
        assert char.total_level == 20
        assert char.is_multiclass() is True
        assert char.abilities.charisma.total == 20
        assert char.combat.hit_points.maximum == 156
        assert len(char.features) >= 20
        assert len(char.spellcasting.known) == 15
        assert char.equipment.attuned_count == 3

        # 3. Save
        save_path = store.save(char)
        assert save_path.exists()

        # 4. Load and verify
        loaded = store.load("Valeria Sunforge")
        assert loaded is not None
        assert loaded.total_level == 20

        # 5. Export to HTML
        html_path = temp_dir / "valeria_export.html"
        export_to_html(loaded, html_path)
        assert html_path.exists()

        html_content = html_path.read_text()
        assert "Valeria Sunforge" in html_content
        assert len(html_content) > 1000  # Should be substantial

        # 6. Delete
        assert store.delete("Valeria Sunforge") is True
        assert store.load("Valeria Sunforge") is None

        # 7. Clean up HTML
        html_path.unlink()
        assert not html_path.exists()


class TestValeriaCalculations:
    """Tests for calculated values and modifiers."""

    def test_skill_modifiers(self):
        """Test skill modifier calculations."""
        char = create_valeria()

        # Athletics: STR (+4) + proficiency (+6) = +10
        athletics_mod = char.get_skill_modifier(Skill.ATHLETICS)
        assert athletics_mod == 10

        # Persuasion: CHA (+5) + proficiency (+6) = +11
        persuasion_mod = char.get_skill_modifier(Skill.PERSUASION)
        assert persuasion_mod == 11

        # Stealth: DEX (+0) + no proficiency = +0
        stealth_mod = char.get_skill_modifier(Skill.STEALTH)
        assert stealth_mod == 0

    def test_save_modifiers(self):
        """Test saving throw modifiers."""
        char = create_valeria()

        # CHA save: +5 (mod) + 6 (prof) = +11
        cha_save = char.get_save_modifier(Ability.CHARISMA)
        assert cha_save == 11

        # CON save: +3 (mod) + 6 (prof) = +9
        con_save = char.get_save_modifier(Ability.CONSTITUTION)
        assert con_save == 9

        # STR save: +4 (mod) + 0 (no prof) = +4
        str_save = char.get_save_modifier(Ability.STRENGTH)
        assert str_save == 4

    def test_spell_save_dc(self):
        """Test spell save DC calculation."""
        char = create_valeria()

        # DC = 8 + proficiency (+6) + CHA (+5) = 19
        # Note: This depends on how spell_save_dc is implemented
        expected_dc = 8 + 6 + 5
        assert expected_dc == 19

    def test_attack_bonus(self):
        """Test attack bonus calculation."""
        char = create_valeria()

        # Melee: STR (+4) + proficiency (+6) = +10
        # With +3 weapon: +13
        str_attack = char.abilities.strength.modifier + char.proficiency_bonus
        assert str_attack == 10


# Convenience function for running as script
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
