"""D&D 5e 2024 Player's Handbook ruleset implementation."""

from typing import Optional

from dnd_manager.rulesets.base import (
    Ruleset,
    CharacterCreationStep,
    SubclassProgression,
    ClassDefinition,
    SpeciesDefinition,
    BackgroundDefinition,
    AbilityScoreIncrease,
    CasterType,
)


class DnD2024Ruleset(Ruleset):
    """D&D 5e 2024 Player's Handbook ruleset.

    Key differences from 2014:
    - Character creation order: Class > Background > Species > Ability Scores
    - Ability score bonuses come from Background, not Species
    - Backgrounds provide Origin Feats
    - All subclasses gained at level 3
    - Standardized subclass progression (3, 6, 10, 14)
    - Species renamed from Race
    """

    # Class definitions
    CLASSES: dict[str, ClassDefinition] = {
        "Barbarian": ClassDefinition(
            name="Barbarian",
            hit_die=12,
            primary_ability="Strength",
            saving_throws=["Strength", "Constitution"],
            skill_choices=2,
            skill_options=["Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"],
            armor_proficiencies=["Light", "Medium", "Shields"],
            weapon_proficiencies=["Simple", "Martial"],
            caster_type=CasterType.NONE,
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Bard": ClassDefinition(
            name="Bard",
            hit_die=8,
            primary_ability="Charisma",
            saving_throws=["Dexterity", "Charisma"],
            skill_choices=3,
            skill_options=[
                "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
                "History", "Insight", "Intimidation", "Investigation", "Medicine",
                "Nature", "Perception", "Performance", "Persuasion", "Religion",
                "Sleight of Hand", "Stealth", "Survival"
            ],
            armor_proficiencies=["Light"],
            weapon_proficiencies=["Simple", "Hand Crossbows", "Longswords", "Rapiers", "Shortswords"],
            tool_proficiencies=["Three musical instruments"],
            caster_type=CasterType.FULL,
            spellcasting_ability="Charisma",
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Cleric": ClassDefinition(
            name="Cleric",
            hit_die=8,
            primary_ability="Wisdom",
            saving_throws=["Wisdom", "Charisma"],
            skill_choices=2,
            skill_options=["History", "Insight", "Medicine", "Persuasion", "Religion"],
            armor_proficiencies=["Light", "Medium", "Shields"],
            weapon_proficiencies=["Simple"],
            caster_type=CasterType.FULL,
            spellcasting_ability="Wisdom",
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Druid": ClassDefinition(
            name="Druid",
            hit_die=8,
            primary_ability="Wisdom",
            saving_throws=["Intelligence", "Wisdom"],
            skill_choices=2,
            skill_options=["Arcana", "Animal Handling", "Insight", "Medicine", "Nature", "Perception", "Religion", "Survival"],
            armor_proficiencies=["Light", "Medium", "Shields"],
            weapon_proficiencies=["Clubs", "Daggers", "Darts", "Javelins", "Maces", "Quarterstaffs", "Scimitars", "Sickles", "Slings", "Spears"],
            tool_proficiencies=["Herbalism kit"],
            caster_type=CasterType.FULL,
            spellcasting_ability="Wisdom",
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Fighter": ClassDefinition(
            name="Fighter",
            hit_die=10,
            primary_ability="Strength",
            saving_throws=["Strength", "Constitution"],
            skill_choices=2,
            skill_options=["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"],
            armor_proficiencies=["Light", "Medium", "Heavy", "Shields"],
            weapon_proficiencies=["Simple", "Martial"],
            caster_type=CasterType.NONE,  # Base class; Eldritch Knight is third-caster
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Monk": ClassDefinition(
            name="Monk",
            hit_die=8,
            primary_ability="Dexterity",
            saving_throws=["Strength", "Dexterity"],
            skill_choices=2,
            skill_options=["Acrobatics", "Athletics", "History", "Insight", "Religion", "Stealth"],
            armor_proficiencies=[],
            weapon_proficiencies=["Simple", "Shortswords"],
            caster_type=CasterType.NONE,
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Paladin": ClassDefinition(
            name="Paladin",
            hit_die=10,
            primary_ability="Strength",
            saving_throws=["Wisdom", "Charisma"],
            skill_choices=2,
            skill_options=["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"],
            armor_proficiencies=["Light", "Medium", "Heavy", "Shields"],
            weapon_proficiencies=["Simple", "Martial"],
            caster_type=CasterType.HALF,
            spellcasting_ability="Charisma",
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Ranger": ClassDefinition(
            name="Ranger",
            hit_die=10,
            primary_ability="Dexterity",
            saving_throws=["Strength", "Dexterity"],
            skill_choices=3,
            skill_options=["Animal Handling", "Athletics", "Insight", "Investigation", "Nature", "Perception", "Stealth", "Survival"],
            armor_proficiencies=["Light", "Medium", "Shields"],
            weapon_proficiencies=["Simple", "Martial"],
            caster_type=CasterType.HALF,
            spellcasting_ability="Wisdom",
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Rogue": ClassDefinition(
            name="Rogue",
            hit_die=8,
            primary_ability="Dexterity",
            saving_throws=["Dexterity", "Intelligence"],
            skill_choices=4,
            skill_options=["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation", "Perception", "Performance", "Persuasion", "Sleight of Hand", "Stealth"],
            armor_proficiencies=["Light"],
            weapon_proficiencies=["Simple", "Hand Crossbows", "Longswords", "Rapiers", "Shortswords"],
            tool_proficiencies=["Thieves' tools"],
            caster_type=CasterType.NONE,  # Arcane Trickster is third-caster
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Sorcerer": ClassDefinition(
            name="Sorcerer",
            hit_die=6,
            primary_ability="Charisma",
            saving_throws=["Constitution", "Charisma"],
            skill_choices=2,
            skill_options=["Arcana", "Deception", "Insight", "Intimidation", "Persuasion", "Religion"],
            armor_proficiencies=[],
            weapon_proficiencies=["Daggers", "Darts", "Slings", "Quarterstaffs", "Light Crossbows"],
            caster_type=CasterType.FULL,
            spellcasting_ability="Charisma",
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Warlock": ClassDefinition(
            name="Warlock",
            hit_die=8,
            primary_ability="Charisma",
            saving_throws=["Wisdom", "Charisma"],
            skill_choices=2,
            skill_options=["Arcana", "Deception", "History", "Intimidation", "Investigation", "Nature", "Religion"],
            armor_proficiencies=["Light"],
            weapon_proficiencies=["Simple"],
            caster_type=CasterType.PACT,
            spellcasting_ability="Charisma",
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Wizard": ClassDefinition(
            name="Wizard",
            hit_die=6,
            primary_ability="Intelligence",
            saving_throws=["Intelligence", "Wisdom"],
            skill_choices=2,
            skill_options=["Arcana", "History", "Insight", "Investigation", "Medicine", "Religion"],
            armor_proficiencies=[],
            weapon_proficiencies=["Daggers", "Darts", "Slings", "Quarterstaffs", "Light Crossbows"],
            caster_type=CasterType.FULL,
            spellcasting_ability="Intelligence",
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
    }

    # Species definitions (2024 no longer provides ability bonuses)
    SPECIES: dict[str, SpeciesDefinition] = {
        "Human": SpeciesDefinition(
            name="Human",
            description="Versatile and ambitious, humans are the most adaptable species.",
            size="Medium",
            speed=30,
            traits=["Resourceful", "Skillful", "Versatile"],
            languages=["Common"],
            bonus_languages=1,
        ),
        "Elf": SpeciesDefinition(
            name="Elf",
            description="Elves are a magical people of otherworldly grace.",
            size="Medium",
            speed=30,
            traits=["Darkvision", "Fey Ancestry", "Keen Senses", "Trance"],
            darkvision=60,
            skill_proficiencies=["Perception"],
            languages=["Common", "Elvish"],
            subspecies=["High Elf", "Wood Elf", "Drow"],
        ),
        "Dwarf": SpeciesDefinition(
            name="Dwarf",
            description="Bold and hardy, dwarves are known as skilled warriors and craftspeople.",
            size="Medium",
            speed=30,
            traits=["Darkvision", "Dwarven Resilience", "Dwarven Toughness", "Stonecunning"],
            darkvision=60,
            languages=["Common", "Dwarvish"],
        ),
        "Halfling": SpeciesDefinition(
            name="Halfling",
            description="The diminutive halflings survive in a world full of larger creatures.",
            size="Small",
            speed=30,
            traits=["Brave", "Halfling Nimbleness", "Lucky", "Naturally Stealthy"],
            languages=["Common", "Halfling"],
        ),
        "Gnome": SpeciesDefinition(
            name="Gnome",
            description="Gnomes are known for their endless curiosity and inventive spirit.",
            size="Small",
            speed=30,
            traits=["Darkvision", "Gnomish Cunning", "Gnomish Lineage"],
            darkvision=60,
            languages=["Common", "Gnomish"],
        ),
        "Half-Orc": SpeciesDefinition(
            name="Half-Orc",
            description="Half-orcs combine human versatility with orcish strength.",
            size="Medium",
            speed=30,
            traits=["Darkvision", "Adrenaline Rush", "Relentless Endurance", "Savage Attacks"],
            darkvision=60,
            languages=["Common", "Orc"],
        ),
        "Tiefling": SpeciesDefinition(
            name="Tiefling",
            description="Tieflings are derived from human bloodlines infused with infernal heritage.",
            size="Medium",
            speed=30,
            traits=["Darkvision", "Hellish Resistance", "Infernal Legacy"],
            darkvision=60,
            languages=["Common", "Infernal"],
        ),
        "Dragonborn": SpeciesDefinition(
            name="Dragonborn",
            description="Dragonborn look very much like dragons standing erect in humanoid form.",
            size="Medium",
            speed=30,
            traits=["Draconic Ancestry", "Breath Weapon", "Damage Resistance"],
            languages=["Common", "Draconic"],
        ),
        "Orc": SpeciesDefinition(
            name="Orc",
            description="Orcs are a hardy and powerful people.",
            size="Medium",
            speed=30,
            traits=["Darkvision", "Adrenaline Rush", "Powerful Build", "Relentless Endurance"],
            darkvision=60,
            languages=["Common", "Orc"],
        ),
        "Goliath": SpeciesDefinition(
            name="Goliath",
            description="Goliaths are massive humanoids who live at the highest mountain elevations.",
            size="Medium",
            speed=35,
            traits=["Giant Ancestry", "Large Form", "Powerful Build", "Stone's Endurance"],
            languages=["Common", "Giant"],
        ),
        "Aasimar": SpeciesDefinition(
            name="Aasimar",
            description="Aasimar are humans with celestial heritage.",
            size="Medium",
            speed=30,
            traits=["Celestial Resistance", "Darkvision", "Healing Hands", "Light Bearer", "Celestial Revelation"],
            darkvision=60,
            languages=["Common", "Celestial"],
        ),
    }

    # Backgrounds (2024 style with ability scores and origin feats)
    BACKGROUNDS: dict[str, BackgroundDefinition] = {
        "Acolyte": BackgroundDefinition(
            name="Acolyte",
            description="You have spent your life in the service of a temple.",
            skill_proficiencies=["Insight", "Religion"],
            languages=2,
            equipment=["Holy symbol", "Prayer book", "5 sticks of incense", "Vestments", "Common clothes"],
            starting_gold=15,
            ability_score_options=["Intelligence", "Wisdom", "Charisma"],
            origin_feat="Magic Initiate (Cleric)",
        ),
        "Artisan": BackgroundDefinition(
            name="Artisan",
            description="You are a skilled craftsperson.",
            skill_proficiencies=["Investigation", "Persuasion"],
            tool_proficiencies=["One artisan's tools"],
            equipment=["Artisan's tools", "Guild letter", "Traveler's clothes"],
            starting_gold=15,
            ability_score_options=["Strength", "Dexterity", "Intelligence"],
            origin_feat="Crafter",
        ),
        "Charlatan": BackgroundDefinition(
            name="Charlatan",
            description="You have always had a way with people.",
            skill_proficiencies=["Deception", "Sleight of Hand"],
            tool_proficiencies=["Forgery kit"],
            equipment=["Fine clothes", "Disguise kit", "Tools of the con"],
            starting_gold=15,
            ability_score_options=["Dexterity", "Constitution", "Charisma"],
            origin_feat="Skilled",
        ),
        "Criminal": BackgroundDefinition(
            name="Criminal",
            description="You have a history of breaking the law.",
            skill_proficiencies=["Sleight of Hand", "Stealth"],
            tool_proficiencies=["Thieves' tools"],
            equipment=["Crowbar", "Dark common clothes", "Thieves' tools"],
            starting_gold=15,
            ability_score_options=["Dexterity", "Constitution", "Intelligence"],
            origin_feat="Alert",
        ),
        "Entertainer": BackgroundDefinition(
            name="Entertainer",
            description="You thrive in front of an audience.",
            skill_proficiencies=["Acrobatics", "Performance"],
            tool_proficiencies=["One musical instrument"],
            equipment=["Musical instrument", "Costume", "Favor from admirer"],
            starting_gold=15,
            ability_score_options=["Strength", "Dexterity", "Charisma"],
            origin_feat="Musician",
        ),
        "Farmer": BackgroundDefinition(
            name="Farmer",
            description="You grew up working the land.",
            skill_proficiencies=["Animal Handling", "Nature"],
            tool_proficiencies=["Carpenter's tools"],
            equipment=["Sickle", "Carpenter's tools", "Traveler's clothes"],
            starting_gold=15,
            ability_score_options=["Strength", "Constitution", "Wisdom"],
            origin_feat="Tough",
        ),
        "Guard": BackgroundDefinition(
            name="Guard",
            description="You served as a guard or soldier.",
            skill_proficiencies=["Athletics", "Perception"],
            tool_proficiencies=["Gaming set"],
            equipment=["Insignia of rank", "Gaming set", "Common clothes"],
            starting_gold=15,
            ability_score_options=["Strength", "Intelligence", "Wisdom"],
            origin_feat="Alert",
        ),
        "Guide": BackgroundDefinition(
            name="Guide",
            description="You know the wilderness like the back of your hand.",
            skill_proficiencies=["Stealth", "Survival"],
            tool_proficiencies=["Cartographer's tools"],
            equipment=["Staff", "Hunting trap", "Traveler's clothes", "Map"],
            starting_gold=15,
            ability_score_options=["Dexterity", "Constitution", "Wisdom"],
            origin_feat="Magic Initiate (Druid)",
        ),
        "Hermit": BackgroundDefinition(
            name="Hermit",
            description="You lived in seclusion for a formative part of your life.",
            skill_proficiencies=["Medicine", "Religion"],
            tool_proficiencies=["Herbalism kit"],
            equipment=["Herbalism kit", "Winter blanket", "Common clothes"],
            starting_gold=15,
            ability_score_options=["Constitution", "Wisdom", "Charisma"],
            origin_feat="Healer",
        ),
        "Merchant": BackgroundDefinition(
            name="Merchant",
            description="You are a skilled trader.",
            skill_proficiencies=["Animal Handling", "Persuasion"],
            tool_proficiencies=["Navigator's tools"],
            equipment=["Mule", "Cart", "Trade goods"],
            starting_gold=15,
            ability_score_options=["Constitution", "Intelligence", "Charisma"],
            origin_feat="Lucky",
        ),
        "Noble": BackgroundDefinition(
            name="Noble",
            description="You come from a family of wealth and privilege.",
            skill_proficiencies=["History", "Persuasion"],
            tool_proficiencies=["Gaming set"],
            equipment=["Fine clothes", "Signet ring", "Scroll of pedigree"],
            starting_gold=25,
            ability_score_options=["Strength", "Intelligence", "Charisma"],
            origin_feat="Skilled",
        ),
        "Sage": BackgroundDefinition(
            name="Sage",
            description="You spent years learning the lore of the multiverse.",
            skill_proficiencies=["Arcana", "History"],
            languages=2,
            equipment=["Ink", "Quill", "Small knife", "Letter with question"],
            starting_gold=15,
            ability_score_options=["Constitution", "Intelligence", "Wisdom"],
            origin_feat="Magic Initiate (Wizard)",
        ),
        "Sailor": BackgroundDefinition(
            name="Sailor",
            description="You sailed on a seagoing vessel.",
            skill_proficiencies=["Acrobatics", "Perception"],
            tool_proficiencies=["Navigator's tools"],
            equipment=["Club", "Silk rope", "Lucky charm", "Common clothes"],
            starting_gold=15,
            ability_score_options=["Strength", "Dexterity", "Wisdom"],
            origin_feat="Tavern Brawler",
        ),
        "Scribe": BackgroundDefinition(
            name="Scribe",
            description="You spent formative years as a scribe.",
            skill_proficiencies=["Investigation", "Perception"],
            tool_proficiencies=["Calligrapher's supplies"],
            equipment=["Calligrapher's supplies", "Fine clothes", "Lamp"],
            starting_gold=15,
            ability_score_options=["Dexterity", "Intelligence", "Wisdom"],
            origin_feat="Skilled",
        ),
        "Soldier": BackgroundDefinition(
            name="Soldier",
            description="You were trained as a soldier.",
            skill_proficiencies=["Athletics", "Intimidation"],
            tool_proficiencies=["Gaming set"],
            equipment=["Insignia of rank", "Trophy from fallen enemy", "Gaming set"],
            starting_gold=15,
            ability_score_options=["Strength", "Dexterity", "Constitution"],
            origin_feat="Savage Attacker",
        ),
        "Wayfarer": BackgroundDefinition(
            name="Wayfarer",
            description="You grew up on the road.",
            skill_proficiencies=["Insight", "Stealth"],
            tool_proficiencies=["Thieves' tools"],
            equipment=["Bedroll", "Mess kit", "Traveler's clothes"],
            starting_gold=15,
            ability_score_options=["Dexterity", "Wisdom", "Charisma"],
            origin_feat="Lucky",
        ),
    }

    @property
    def id(self) -> str:
        return "dnd2024"

    @property
    def name(self) -> str:
        return "D&D 5e (2024)"

    @property
    def description(self) -> str:
        return "Dungeons & Dragons 5th Edition 2024 Player's Handbook"

    @property
    def creation_order(self) -> list[CharacterCreationStep]:
        return [
            CharacterCreationStep.CLASS,
            CharacterCreationStep.BACKGROUND,
            CharacterCreationStep.EQUIPMENT,
            CharacterCreationStep.SPECIES,
            CharacterCreationStep.ABILITY_SCORES,
            CharacterCreationStep.ALIGNMENT,
            CharacterCreationStep.SPELLS,
            CharacterCreationStep.PERSONALITY,
            CharacterCreationStep.FINISHING,
        ]

    @property
    def species_term(self) -> str:
        return "Species"

    @property
    def subspecies_term(self) -> str:
        return "Subspecies"

    def get_ability_score_source(self) -> str:
        return "background"

    def get_subclass_progression(self, class_name: str) -> SubclassProgression:
        # 2024: All classes get subclass at level 3
        return SubclassProgression(3, [3, 6, 10, 14])

    def get_class_definition(self, class_name: str) -> Optional[ClassDefinition]:
        return self.CLASSES.get(class_name)

    def get_available_classes(self) -> list[str]:
        return list(self.CLASSES.keys())

    def get_species_definition(self, species_name: str) -> Optional[SpeciesDefinition]:
        return self.SPECIES.get(species_name)

    def get_available_species(self) -> list[str]:
        return list(self.SPECIES.keys())

    def get_background_definition(self, background_name: str) -> Optional[BackgroundDefinition]:
        return self.BACKGROUNDS.get(background_name)

    def get_available_backgrounds(self) -> list[str]:
        return list(self.BACKGROUNDS.keys())

    def has_origin_feats(self) -> bool:
        return True

    def get_asi_levels(self) -> list[int]:
        return [4, 8, 12, 16, 19]
