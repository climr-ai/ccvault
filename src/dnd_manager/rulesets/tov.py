"""Tales of the Valiant (Kobold Press) ruleset implementation."""

from typing import Optional

from dnd_manager.rulesets.base import (
    Ruleset,
    CharacterCreationStep,
    SubclassProgression,
    ClassDefinition,
    SpeciesDefinition,
    BackgroundDefinition,
    CasterType,
)


class TalesOfTheValiantRuleset(Ruleset):
    """Tales of the Valiant ruleset from Kobold Press.

    Key characteristics:
    - Lineage (what you are) + Heritage (where you were raised)
    - Talents instead of Feats (1:1 swap with 5e feats)
    - Luck instead of Inspiration (can swap systems)
    - 13 base classes
    - Compatible with D&D 5e content
    - Creation order: Concept > Class > Abilities > Lineage > Heritage > Background
    """

    # Class definitions - ToV is 5e compatible with some enhancements
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
            caster_type=CasterType.NONE,
            subclass_progression=SubclassProgression(3, [3, 6, 10, 14]),
        ),
        "Mechanist": ClassDefinition(
            name="Mechanist",
            hit_die=8,
            primary_ability="Intelligence",
            saving_throws=["Constitution", "Intelligence"],
            skill_choices=2,
            skill_options=["Arcana", "History", "Investigation", "Medicine", "Nature", "Perception", "Sleight of Hand"],
            armor_proficiencies=["Light", "Medium", "Shields"],
            weapon_proficiencies=["Simple"],
            tool_proficiencies=["Thieves' tools", "Tinker's tools", "One artisan's tools"],
            caster_type=CasterType.HALF,
            spellcasting_ability="Intelligence",
            subclass_progression=SubclassProgression(3, [3, 5, 9, 15]),
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
            caster_type=CasterType.NONE,
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

    # Lineage definitions (what you ARE - biological)
    # In ToV, ability scores come from point buy/standard array, not lineage
    LINEAGES: dict[str, SpeciesDefinition] = {
        "Beastkin": SpeciesDefinition(
            name="Beastkin",
            description="Beastkin are bipedal humanoids with animalistic features.",
            size="Medium",
            speed=30,
            traits=["Animal Instincts", "Natural Weapons", "Beast Speech"],
            languages=["Common"],
            bonus_languages=1,
        ),
        "Dwarf": SpeciesDefinition(
            name="Dwarf",
            description="Dwarves are stout, hardy folk known for their craftsmanship.",
            size="Medium",
            speed=25,
            traits=["Darkvision", "Dwarven Resilience", "Stonecunning", "Dwarven Toughness"],
            darkvision=60,
            languages=["Common", "Dwarvish"],
        ),
        "Elf": SpeciesDefinition(
            name="Elf",
            description="Elves are graceful beings with a deep connection to magic.",
            size="Medium",
            speed=30,
            traits=["Darkvision", "Fey Ancestry", "Keen Senses", "Trance"],
            darkvision=60,
            skill_proficiencies=["Perception"],
            languages=["Common", "Elvish"],
        ),
        "Human": SpeciesDefinition(
            name="Human",
            description="Humans are versatile and ambitious.",
            size="Medium",
            speed=30,
            traits=["Ambitious", "Resourceful"],
            languages=["Common"],
            bonus_languages=1,
        ),
        "Kobold": SpeciesDefinition(
            name="Kobold",
            description="Kobolds are small, cunning reptilian humanoids.",
            size="Small",
            speed=30,
            traits=["Darkvision", "Draconic Cry", "Pack Tactics", "Sunlight Sensitivity"],
            darkvision=60,
            languages=["Common", "Draconic"],
        ),
        "Orc": SpeciesDefinition(
            name="Orc",
            description="Orcs are powerful and proud warriors.",
            size="Medium",
            speed=30,
            traits=["Darkvision", "Aggressive", "Powerful Build", "Relentless Endurance"],
            darkvision=60,
            languages=["Common", "Orc"],
        ),
        "Smallfolk": SpeciesDefinition(
            name="Smallfolk",
            description="Smallfolk include halflings and gnomes.",
            size="Small",
            speed=25,
            traits=["Brave", "Lucky", "Nimbleness"],
            languages=["Common"],
            bonus_languages=1,
        ),
        "Syderean": SpeciesDefinition(
            name="Syderean",
            description="Sydereans are beings with extraplanar heritage.",
            size="Medium",
            speed=30,
            traits=["Darkvision", "Celestial Resistance", "Planar Legacy"],
            darkvision=60,
            languages=["Common", "Celestial"],
        ),
    }

    # Heritages (where you were RAISED - cultural)
    # These provide additional traits based on upbringing
    HERITAGES: dict[str, BackgroundDefinition] = {
        "Cottage": BackgroundDefinition(
            name="Cottage",
            description="You grew up in a small rural community.",
            skill_proficiencies=["Animal Handling", "Nature"],
            feature_name="Rural Hospitality",
            feature_description="Country folk welcome you as one of their own.",
        ),
        "Diaspora": BackgroundDefinition(
            name="Diaspora",
            description="Your people are scattered, and you grew up among strangers.",
            skill_proficiencies=["Insight", "Persuasion"],
            languages=1,
            feature_name="Cultural Chameleon",
            feature_description="You can adapt to fit in with different groups.",
        ),
        "Grove": BackgroundDefinition(
            name="Grove",
            description="You were raised in a forest community.",
            skill_proficiencies=["Nature", "Stealth"],
            feature_name="Forest Wisdom",
            feature_description="You know the secrets of forest survival.",
        ),
        "Nomadic": BackgroundDefinition(
            name="Nomadic",
            description="Your people are wanderers who never stay in one place.",
            skill_proficiencies=["Survival", "Animal Handling"],
            feature_name="Pathfinder",
            feature_description="You can find safe routes through dangerous terrain.",
        ),
        "Slum": BackgroundDefinition(
            name="Slum",
            description="You grew up in the poorest parts of a city.",
            skill_proficiencies=["Sleight of Hand", "Stealth"],
            feature_name="Street Smart",
            feature_description="You know how to survive on the streets.",
        ),
        "Stone": BackgroundDefinition(
            name="Stone",
            description="You were raised underground in mountain halls.",
            skill_proficiencies=["History", "Perception"],
            feature_name="Underground Guide",
            feature_description="You know the ways of subterranean places.",
        ),
        "Supplicant": BackgroundDefinition(
            name="Supplicant",
            description="You were raised in a religious community.",
            skill_proficiencies=["Insight", "Religion"],
            feature_name="Temple Shelter",
            feature_description="You can find shelter in temples of your faith.",
        ),
        "Wildlands": BackgroundDefinition(
            name="Wildlands",
            description="You grew up far from civilization.",
            skill_proficiencies=["Perception", "Survival"],
            feature_name="Wild Instincts",
            feature_description="You have an innate sense for danger.",
        ),
    }

    # Backgrounds (occupation before adventuring)
    BACKGROUNDS: dict[str, BackgroundDefinition] = {
        "Acolyte": BackgroundDefinition(
            name="Acolyte",
            description="You served in a temple.",
            skill_proficiencies=["Insight", "Religion"],
            languages=2,
            starting_gold=15,
            feature_name="Shelter of the Faithful",
            feature_description="Temples provide you shelter and aid.",
        ),
        "Artisan": BackgroundDefinition(
            name="Artisan",
            description="You are a skilled craftsperson.",
            skill_proficiencies=["Investigation", "Persuasion"],
            tool_proficiencies=["One artisan's tools"],
            starting_gold=15,
            feature_name="Guild Connections",
            feature_description="You have contacts in the artisan community.",
        ),
        "Charlatan": BackgroundDefinition(
            name="Charlatan",
            description="You make your living through deception.",
            skill_proficiencies=["Deception", "Sleight of Hand"],
            tool_proficiencies=["Disguise kit", "Forgery kit"],
            starting_gold=15,
            feature_name="False Identity",
            feature_description="You have a second identity.",
        ),
        "Criminal": BackgroundDefinition(
            name="Criminal",
            description="You have a criminal past.",
            skill_proficiencies=["Deception", "Stealth"],
            tool_proficiencies=["Thieves' tools", "Gaming set"],
            starting_gold=15,
            feature_name="Criminal Contact",
            feature_description="You know contacts in the underworld.",
        ),
        "Entertainer": BackgroundDefinition(
            name="Entertainer",
            description="You perform for audiences.",
            skill_proficiencies=["Acrobatics", "Performance"],
            tool_proficiencies=["Disguise kit", "Musical instrument"],
            starting_gold=15,
            feature_name="By Popular Demand",
            feature_description="You can find venues to perform.",
        ),
        "Farmer": BackgroundDefinition(
            name="Farmer",
            description="You worked the land.",
            skill_proficiencies=["Animal Handling", "Nature"],
            tool_proficiencies=["Vehicles (land)"],
            starting_gold=10,
            feature_name="Rustic Hospitality",
            feature_description="Common folk offer you shelter.",
        ),
        "Noble": BackgroundDefinition(
            name="Noble",
            description="You come from wealth and privilege.",
            skill_proficiencies=["History", "Persuasion"],
            tool_proficiencies=["Gaming set"],
            languages=1,
            starting_gold=25,
            feature_name="Position of Privilege",
            feature_description="High society welcomes you.",
        ),
        "Sage": BackgroundDefinition(
            name="Sage",
            description="You are a scholar and researcher.",
            skill_proficiencies=["Arcana", "History"],
            languages=2,
            starting_gold=10,
            feature_name="Researcher",
            feature_description="You know where to find information.",
        ),
        "Sailor": BackgroundDefinition(
            name="Sailor",
            description="You worked on ships.",
            skill_proficiencies=["Athletics", "Perception"],
            tool_proficiencies=["Navigator's tools", "Vehicles (water)"],
            starting_gold=10,
            feature_name="Ship's Passage",
            feature_description="You can secure passage on ships.",
        ),
        "Soldier": BackgroundDefinition(
            name="Soldier",
            description="You served in the military.",
            skill_proficiencies=["Athletics", "Intimidation"],
            tool_proficiencies=["Gaming set", "Vehicles (land)"],
            starting_gold=10,
            feature_name="Military Rank",
            feature_description="Soldiers recognize your authority.",
        ),
    }

    @property
    def id(self) -> str:
        return "tov"

    @property
    def name(self) -> str:
        return "Tales of the Valiant"

    @property
    def description(self) -> str:
        return "Tales of the Valiant RPG by Kobold Press (5e compatible)"

    @property
    def creation_order(self) -> list[CharacterCreationStep]:
        return [
            CharacterCreationStep.CONCEPT,
            CharacterCreationStep.CLASS,
            CharacterCreationStep.ABILITY_SCORES,
            CharacterCreationStep.LINEAGE,
            CharacterCreationStep.HERITAGE,
            CharacterCreationStep.BACKGROUND,
            CharacterCreationStep.EQUIPMENT,
            CharacterCreationStep.SPELLS,
            CharacterCreationStep.PERSONALITY,
            CharacterCreationStep.FINISHING,
        ]

    @property
    def species_term(self) -> str:
        return "Lineage"

    @property
    def subspecies_term(self) -> str:
        return "Heritage"

    def get_ability_score_source(self) -> str:
        return "none"  # ToV uses point buy/standard array only

    def get_subclass_progression(self, class_name: str) -> SubclassProgression:
        class_def = self.CLASSES.get(class_name)
        if class_def:
            return class_def.subclass_progression
        return SubclassProgression(3, [3, 6, 10, 14])

    def get_class_definition(self, class_name: str) -> Optional[ClassDefinition]:
        return self.CLASSES.get(class_name)

    def get_available_classes(self) -> list[str]:
        return list(self.CLASSES.keys())

    def get_species_definition(self, species_name: str) -> Optional[SpeciesDefinition]:
        # In ToV, this returns Lineage definitions
        return self.LINEAGES.get(species_name)

    def get_available_species(self) -> list[str]:
        return list(self.LINEAGES.keys())

    def get_heritage_definition(self, heritage_name: str) -> Optional[BackgroundDefinition]:
        """Get heritage definition (ToV-specific)."""
        return self.HERITAGES.get(heritage_name)

    def get_available_heritages(self) -> list[str]:
        """Get available heritages (ToV-specific)."""
        return list(self.HERITAGES.keys())

    def get_background_definition(self, background_name: str) -> Optional[BackgroundDefinition]:
        return self.BACKGROUNDS.get(background_name)

    def get_available_backgrounds(self) -> list[str]:
        return list(self.BACKGROUNDS.keys())

    def has_origin_feats(self) -> bool:
        return False  # ToV uses Talents instead

    def get_asi_levels(self) -> list[int]:
        return [4, 8, 12, 16, 19]

    def get_talent_levels(self) -> list[int]:
        """Get levels where talents are available (ToV-specific)."""
        return [4, 8, 12, 16, 19]  # Same as ASI, can take talent instead
