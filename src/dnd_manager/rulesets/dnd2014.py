"""D&D 5e 2014 Player's Handbook ruleset implementation."""

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


class DnD2014Ruleset(Ruleset):
    """D&D 5e 2014 Player's Handbook ruleset.

    Key characteristics:
    - Character creation order: Race > Class > Ability Scores > Background
    - Ability score bonuses come from Race
    - Subclass selection varies by class (1, 2, or 3)
    - No origin feats (feats are optional, replace ASI)
    - Uses "Race" terminology
    """

    # Class definitions with 2014-specific subclass progressions
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
            subclass_progression=SubclassProgression(3, [3, 6, 14]),  # 2014: No feature at 10
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
            subclass_progression=SubclassProgression(1, [1, 2, 6, 8, 17]),  # 2014: Subclass at 1
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
            subclass_progression=SubclassProgression(2, [2, 6, 10, 14]),  # 2014: Subclass at 2
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
            subclass_progression=SubclassProgression(3, [3, 7, 10, 15, 18]),
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
            subclass_progression=SubclassProgression(3, [3, 6, 11, 17]),
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
            subclass_progression=SubclassProgression(3, [3, 7, 15, 20]),
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
            subclass_progression=SubclassProgression(3, [3, 7, 11, 15]),
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
            subclass_progression=SubclassProgression(3, [3, 9, 13, 17]),
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
            subclass_progression=SubclassProgression(1, [1, 6, 14, 18]),  # 2014: Subclass at 1
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
            subclass_progression=SubclassProgression(1, [1, 6, 10, 14]),  # 2014: Subclass at 1
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
            subclass_progression=SubclassProgression(2, [2, 6, 10, 14]),  # 2014: Subclass at 2
        ),
    }

    # Race definitions with ability score bonuses (2014 style)
    RACES: dict[str, SpeciesDefinition] = {
        "Human": SpeciesDefinition(
            name="Human",
            description="Humans are the most adaptable and ambitious people.",
            size="Medium",
            speed=30,
            ability_increases=[
                AbilityScoreIncrease(
                    options=["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"],
                    amount=1,
                    choose=6,  # +1 to all
                )
            ],
            traits=["Extra Language", "Extra Skill"],
            languages=["Common"],
            bonus_languages=1,
        ),
        "Variant Human": SpeciesDefinition(
            name="Variant Human",
            description="Variant humans trade versatility for focused ability.",
            size="Medium",
            speed=30,
            ability_increases=[
                AbilityScoreIncrease(
                    options=["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"],
                    amount=1,
                    choose=2,  # +1 to two different abilities
                )
            ],
            traits=["Feat", "Extra Skill"],
            languages=["Common"],
            bonus_languages=1,
        ),
        "Elf": SpeciesDefinition(
            name="Elf",
            description="Elves are a magical people of otherworldly grace.",
            size="Medium",
            speed=30,
            ability_increases=[
                AbilityScoreIncrease(options=["Dexterity"], amount=2, choose=1)
            ],
            traits=["Darkvision", "Fey Ancestry", "Keen Senses", "Trance"],
            darkvision=60,
            skill_proficiencies=["Perception"],
            languages=["Common", "Elvish"],
            subspecies=["High Elf", "Wood Elf", "Dark Elf"],
        ),
        "High Elf": SpeciesDefinition(
            name="High Elf",
            description="High elves have a keen mind and mastery of basic magic.",
            size="Medium",
            speed=30,
            ability_increases=[
                AbilityScoreIncrease(options=["Dexterity"], amount=2, choose=1),
                AbilityScoreIncrease(options=["Intelligence"], amount=1, choose=1),
            ],
            traits=["Darkvision", "Fey Ancestry", "Keen Senses", "Trance", "Cantrip", "Extra Language"],
            darkvision=60,
            skill_proficiencies=["Perception"],
            weapon_proficiencies=["Longsword", "Shortsword", "Shortbow", "Longbow"],
            languages=["Common", "Elvish"],
            bonus_languages=1,
        ),
        "Wood Elf": SpeciesDefinition(
            name="Wood Elf",
            description="Wood elves are fleet of foot and stealthy.",
            size="Medium",
            speed=35,
            ability_increases=[
                AbilityScoreIncrease(options=["Dexterity"], amount=2, choose=1),
                AbilityScoreIncrease(options=["Wisdom"], amount=1, choose=1),
            ],
            traits=["Darkvision", "Fey Ancestry", "Keen Senses", "Trance", "Fleet of Foot", "Mask of the Wild"],
            darkvision=60,
            skill_proficiencies=["Perception"],
            weapon_proficiencies=["Longsword", "Shortsword", "Shortbow", "Longbow"],
            languages=["Common", "Elvish"],
        ),
        "Dwarf": SpeciesDefinition(
            name="Dwarf",
            description="Bold and hardy, dwarves are known as skilled warriors.",
            size="Medium",
            speed=25,
            ability_increases=[
                AbilityScoreIncrease(options=["Constitution"], amount=2, choose=1)
            ],
            traits=["Darkvision", "Dwarven Resilience", "Stonecunning"],
            darkvision=60,
            weapon_proficiencies=["Battleaxe", "Handaxe", "Light Hammer", "Warhammer"],
            languages=["Common", "Dwarvish"],
            subspecies=["Hill Dwarf", "Mountain Dwarf"],
        ),
        "Hill Dwarf": SpeciesDefinition(
            name="Hill Dwarf",
            description="Hill dwarves have keen senses and remarkable resilience.",
            size="Medium",
            speed=25,
            ability_increases=[
                AbilityScoreIncrease(options=["Constitution"], amount=2, choose=1),
                AbilityScoreIncrease(options=["Wisdom"], amount=1, choose=1),
            ],
            traits=["Darkvision", "Dwarven Resilience", "Stonecunning", "Dwarven Toughness"],
            darkvision=60,
            weapon_proficiencies=["Battleaxe", "Handaxe", "Light Hammer", "Warhammer"],
            languages=["Common", "Dwarvish"],
        ),
        "Mountain Dwarf": SpeciesDefinition(
            name="Mountain Dwarf",
            description="Mountain dwarves are strong and hardy.",
            size="Medium",
            speed=25,
            ability_increases=[
                AbilityScoreIncrease(options=["Constitution"], amount=2, choose=1),
                AbilityScoreIncrease(options=["Strength"], amount=2, choose=1),
            ],
            traits=["Darkvision", "Dwarven Resilience", "Stonecunning", "Dwarven Armor Training"],
            darkvision=60,
            weapon_proficiencies=["Battleaxe", "Handaxe", "Light Hammer", "Warhammer"],
            armor_proficiencies=["Light", "Medium"],
            languages=["Common", "Dwarvish"],
        ),
        "Halfling": SpeciesDefinition(
            name="Halfling",
            description="Halflings are small folk who survive by being clever.",
            size="Small",
            speed=25,
            ability_increases=[
                AbilityScoreIncrease(options=["Dexterity"], amount=2, choose=1)
            ],
            traits=["Lucky", "Brave", "Halfling Nimbleness"],
            languages=["Common", "Halfling"],
            subspecies=["Lightfoot Halfling", "Stout Halfling"],
        ),
        "Lightfoot Halfling": SpeciesDefinition(
            name="Lightfoot Halfling",
            description="Lightfoot halflings are naturally stealthy.",
            size="Small",
            speed=25,
            ability_increases=[
                AbilityScoreIncrease(options=["Dexterity"], amount=2, choose=1),
                AbilityScoreIncrease(options=["Charisma"], amount=1, choose=1),
            ],
            traits=["Lucky", "Brave", "Halfling Nimbleness", "Naturally Stealthy"],
            languages=["Common", "Halfling"],
        ),
        "Dragonborn": SpeciesDefinition(
            name="Dragonborn",
            description="Dragonborn look like humanoid dragons.",
            size="Medium",
            speed=30,
            ability_increases=[
                AbilityScoreIncrease(options=["Strength"], amount=2, choose=1),
                AbilityScoreIncrease(options=["Charisma"], amount=1, choose=1),
            ],
            traits=["Draconic Ancestry", "Breath Weapon", "Damage Resistance"],
            languages=["Common", "Draconic"],
        ),
        "Gnome": SpeciesDefinition(
            name="Gnome",
            description="Gnomes are known for their curiosity and invention.",
            size="Small",
            speed=25,
            ability_increases=[
                AbilityScoreIncrease(options=["Intelligence"], amount=2, choose=1)
            ],
            traits=["Darkvision", "Gnome Cunning"],
            darkvision=60,
            languages=["Common", "Gnomish"],
            subspecies=["Forest Gnome", "Rock Gnome"],
        ),
        "Half-Elf": SpeciesDefinition(
            name="Half-Elf",
            description="Half-elves combine human and elven features.",
            size="Medium",
            speed=30,
            ability_increases=[
                AbilityScoreIncrease(options=["Charisma"], amount=2, choose=1),
                AbilityScoreIncrease(
                    options=["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom"],
                    amount=1,
                    choose=2,
                ),
            ],
            traits=["Darkvision", "Fey Ancestry", "Skill Versatility"],
            darkvision=60,
            languages=["Common", "Elvish"],
            bonus_languages=1,
        ),
        "Half-Orc": SpeciesDefinition(
            name="Half-Orc",
            description="Half-orcs combine human and orc heritage.",
            size="Medium",
            speed=30,
            ability_increases=[
                AbilityScoreIncrease(options=["Strength"], amount=2, choose=1),
                AbilityScoreIncrease(options=["Constitution"], amount=1, choose=1),
            ],
            traits=["Darkvision", "Menacing", "Relentless Endurance", "Savage Attacks"],
            darkvision=60,
            skill_proficiencies=["Intimidation"],
            languages=["Common", "Orc"],
        ),
        "Tiefling": SpeciesDefinition(
            name="Tiefling",
            description="Tieflings have infernal heritage.",
            size="Medium",
            speed=30,
            ability_increases=[
                AbilityScoreIncrease(options=["Charisma"], amount=2, choose=1),
                AbilityScoreIncrease(options=["Intelligence"], amount=1, choose=1),
            ],
            traits=["Darkvision", "Hellish Resistance", "Infernal Legacy"],
            darkvision=60,
            languages=["Common", "Infernal"],
        ),
    }

    # Backgrounds (2014 style - no ability scores or origin feats)
    BACKGROUNDS: dict[str, BackgroundDefinition] = {
        "Acolyte": BackgroundDefinition(
            name="Acolyte",
            description="You have spent your life in the service of a temple.",
            skill_proficiencies=["Insight", "Religion"],
            languages=2,
            equipment=["Holy symbol", "Prayer book", "5 sticks of incense", "Vestments", "Common clothes"],
            starting_gold=15,
            feature_name="Shelter of the Faithful",
            feature_description="You and your companions can receive free healing and care at temples of your faith.",
        ),
        "Charlatan": BackgroundDefinition(
            name="Charlatan",
            description="You have always had a way with people.",
            skill_proficiencies=["Deception", "Sleight of Hand"],
            tool_proficiencies=["Disguise kit", "Forgery kit"],
            equipment=["Fine clothes", "Disguise kit", "Tools of the con"],
            starting_gold=15,
            feature_name="False Identity",
            feature_description="You have created a second identity including documentation and contacts.",
        ),
        "Criminal": BackgroundDefinition(
            name="Criminal",
            description="You have a history of breaking the law.",
            skill_proficiencies=["Deception", "Stealth"],
            tool_proficiencies=["Gaming set", "Thieves' tools"],
            equipment=["Crowbar", "Dark common clothes", "Belt pouch"],
            starting_gold=15,
            feature_name="Criminal Contact",
            feature_description="You have a reliable and trustworthy contact in the criminal underworld.",
        ),
        "Entertainer": BackgroundDefinition(
            name="Entertainer",
            description="You thrive in front of an audience.",
            skill_proficiencies=["Acrobatics", "Performance"],
            tool_proficiencies=["Disguise kit", "One musical instrument"],
            equipment=["Musical instrument", "Costume", "Favor from admirer"],
            starting_gold=15,
            feature_name="By Popular Demand",
            feature_description="You can always find a place to perform for lodging and food.",
        ),
        "Folk Hero": BackgroundDefinition(
            name="Folk Hero",
            description="You come from a humble background but are destined for greatness.",
            skill_proficiencies=["Animal Handling", "Survival"],
            tool_proficiencies=["Artisan's tools", "Vehicles (land)"],
            equipment=["Artisan's tools", "Shovel", "Iron pot", "Common clothes"],
            starting_gold=10,
            feature_name="Rustic Hospitality",
            feature_description="Common folk will shelter you from the law and those who hunt you.",
        ),
        "Guild Artisan": BackgroundDefinition(
            name="Guild Artisan",
            description="You are a skilled craftsperson and guild member.",
            skill_proficiencies=["Insight", "Persuasion"],
            tool_proficiencies=["Artisan's tools"],
            languages=1,
            equipment=["Artisan's tools", "Guild letter", "Traveler's clothes"],
            starting_gold=15,
            feature_name="Guild Membership",
            feature_description="Your guild provides lodging and support.",
        ),
        "Hermit": BackgroundDefinition(
            name="Hermit",
            description="You lived in seclusion for a formative part of your life.",
            skill_proficiencies=["Medicine", "Religion"],
            tool_proficiencies=["Herbalism kit"],
            languages=1,
            equipment=["Herbalism kit", "Winter blanket", "Common clothes"],
            starting_gold=5,
            feature_name="Discovery",
            feature_description="You have discovered a unique and powerful truth about the cosmos.",
        ),
        "Noble": BackgroundDefinition(
            name="Noble",
            description="You come from a family of wealth and privilege.",
            skill_proficiencies=["History", "Persuasion"],
            tool_proficiencies=["Gaming set"],
            languages=1,
            equipment=["Fine clothes", "Signet ring", "Scroll of pedigree"],
            starting_gold=25,
            feature_name="Position of Privilege",
            feature_description="You are welcome in high society.",
        ),
        "Outlander": BackgroundDefinition(
            name="Outlander",
            description="You grew up in the wilds, far from civilization.",
            skill_proficiencies=["Athletics", "Survival"],
            tool_proficiencies=["One musical instrument"],
            languages=1,
            equipment=["Staff", "Hunting trap", "Trophy from animal", "Traveler's clothes"],
            starting_gold=10,
            feature_name="Wanderer",
            feature_description="You have an excellent memory for maps and can always find food and fresh water.",
        ),
        "Sage": BackgroundDefinition(
            name="Sage",
            description="You spent years learning the lore of the multiverse.",
            skill_proficiencies=["Arcana", "History"],
            languages=2,
            equipment=["Ink", "Quill", "Small knife", "Letter with question"],
            starting_gold=10,
            feature_name="Researcher",
            feature_description="You know where and from whom to obtain information.",
        ),
        "Sailor": BackgroundDefinition(
            name="Sailor",
            description="You sailed on a seagoing vessel.",
            skill_proficiencies=["Athletics", "Perception"],
            tool_proficiencies=["Navigator's tools", "Vehicles (water)"],
            equipment=["Club", "Silk rope", "Lucky charm", "Common clothes"],
            starting_gold=10,
            feature_name="Ship's Passage",
            feature_description="You can secure free passage on a sailing ship.",
        ),
        "Soldier": BackgroundDefinition(
            name="Soldier",
            description="You were trained as a soldier.",
            skill_proficiencies=["Athletics", "Intimidation"],
            tool_proficiencies=["Gaming set", "Vehicles (land)"],
            equipment=["Insignia of rank", "Trophy from fallen enemy", "Gaming set"],
            starting_gold=10,
            feature_name="Military Rank",
            feature_description="Soldiers loyal to your former organization recognize your authority.",
        ),
        "Urchin": BackgroundDefinition(
            name="Urchin",
            description="You grew up on the streets.",
            skill_proficiencies=["Sleight of Hand", "Stealth"],
            tool_proficiencies=["Disguise kit", "Thieves' tools"],
            equipment=["Small knife", "Map of your city", "Pet mouse", "Token from parents", "Common clothes"],
            starting_gold=10,
            feature_name="City Secrets",
            feature_description="You know the secret patterns of city streets.",
        ),
    }

    @property
    def id(self) -> str:
        return "dnd2014"

    @property
    def name(self) -> str:
        return "D&D 5e (2014)"

    @property
    def description(self) -> str:
        return "Dungeons & Dragons 5th Edition 2014 Player's Handbook"

    @property
    def creation_order(self) -> list[CharacterCreationStep]:
        return [
            CharacterCreationStep.RACE,
            CharacterCreationStep.CLASS,
            CharacterCreationStep.ABILITY_SCORES,
            CharacterCreationStep.ALIGNMENT,
            CharacterCreationStep.BACKGROUND,
            CharacterCreationStep.EQUIPMENT,
            CharacterCreationStep.SPELLS,
            CharacterCreationStep.PERSONALITY,
            CharacterCreationStep.FINISHING,
        ]

    @property
    def species_term(self) -> str:
        return "Race"

    @property
    def subspecies_term(self) -> str:
        return "Subrace"

    def get_ability_score_source(self) -> str:
        return "race"

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
        return self.RACES.get(species_name)

    def get_available_species(self) -> list[str]:
        return list(self.RACES.keys())

    def get_background_definition(self, background_name: str) -> Optional[BackgroundDefinition]:
        return self.BACKGROUNDS.get(background_name)

    def get_available_backgrounds(self) -> list[str]:
        return list(self.BACKGROUNDS.keys())

    def has_origin_feats(self) -> bool:
        return False

    def get_asi_levels(self) -> list[int]:
        return [4, 8, 12, 16, 19]
