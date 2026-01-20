"""SRD class data and features for D&D 5e.

This module contains class information from the System Reference Document (SRD).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CasterType(Enum):
    """Spellcasting progression type for multiclass spell slot calculation."""
    FULL = "full"       # Bard, Cleric, Druid, Sorcerer, Wizard (full level contribution)
    HALF = "half"       # Paladin, Ranger (level / 2, rounded down)
    THIRD = "third"     # Eldritch Knight, Arcane Trickster (level / 3, rounded down)
    PACT = "pact"       # Warlock (separate pact magic, doesn't combine)
    NONE = "none"       # Non-casters (Barbarian, Fighter*, Monk, Rogue*)


@dataclass
class ClassFeature:
    """A class feature definition.

    The ruleset field indicates which rules system the feature applies to:
    - None: Universal, applies to all rulesets
    - "dnd2014": Only for D&D 2014 rules
    - "dnd2024": Only for D&D 2024 rules
    - "tov": Only for Tales of the Valiant
    """
    name: str
    level: int
    description: str
    source: str = "class"  # class, subclass
    uses: Optional[int] = None
    recharge: Optional[str] = None  # "short rest", "long rest", None
    ruleset: Optional[str] = None  # None = universal, "dnd2014", "dnd2024", "tov"


@dataclass
class ClassInfo:
    """Information about a character class.

    Features can have ruleset-specific variants. Use get_features_for_ruleset()
    to filter features for a specific ruleset.
    """
    name: str
    hit_die: str
    primary_ability: str
    saving_throws: list[str]
    armor_proficiencies: list[str]
    weapon_proficiencies: list[str]
    skill_choices: int
    skill_options: list[str]
    spellcasting_ability: Optional[str]
    features: list[ClassFeature] = field(default_factory=list)
    # 2024 additions
    weapon_masteries: int = 0  # Number of weapon masteries (2024 martial classes)


# SRD Class Definitions
BARBARIAN = ClassInfo(
    name="Barbarian",
    hit_die="d12",
    primary_ability="Strength",
    saving_throws=["Strength", "Constitution"],
    armor_proficiencies=["Light", "Medium", "Shields"],
    weapon_proficiencies=["Simple", "Martial"],
    skill_choices=2,
    skill_options=["Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"],
    spellcasting_ability=None,
    weapon_masteries=2,  # 2024: Start with 2 weapon masteries
    features=[
        ClassFeature("Rage", 1, "Enter a rage as a bonus action. While raging, gain advantage on STR checks and saves, bonus rage damage, and resistance to bludgeoning, piercing, and slashing damage.", uses=2, recharge="long rest"),
        ClassFeature("Unarmored Defense", 1, "While not wearing armor, AC equals 10 + DEX modifier + CON modifier."),
        ClassFeature("Weapon Mastery", 1, "You can use the mastery property of two kinds of Simple or Martial weapons. When you finish a long rest, you can change the weapons you have selected.", ruleset="dnd2024"),
        ClassFeature("Reckless Attack", 2, "When making your first attack, you can attack recklessly, gaining advantage on all melee attacks using STR but attacks against you have advantage."),
        ClassFeature("Danger Sense", 2, "You have advantage on DEX saving throws against effects you can see."),
        ClassFeature("Primal Path", 3, "Choose a Primal Path that shapes your rage."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Extra Attack", 5, "Attack twice when you take the Attack action."),
        ClassFeature("Fast Movement", 5, "Your speed increases by 10 feet while not wearing heavy armor."),
        ClassFeature("Feral Instinct", 7, "Advantage on initiative rolls. Can act normally on your first turn if surprised."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Brutal Critical", 9, "Roll one additional weapon damage die on a critical hit.", ruleset="dnd2014"),
        ClassFeature("Weapon Mastery (3 weapons)", 9, "You can use the mastery property of three kinds of weapons.", ruleset="dnd2024"),
        ClassFeature("Relentless Rage", 11, "If you drop to 0 HP while raging, make a DC 10 CON save to drop to 1 HP instead.", recharge="long rest"),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Brutal Critical (2 dice)", 13, "Roll two additional weapon damage dice on a critical hit.", ruleset="dnd2014"),
        ClassFeature("Persistent Rage", 15, "Your rage only ends early if you fall unconscious or choose to end it."),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Brutal Critical (3 dice)", 17, "Roll three additional weapon damage dice on a critical hit.", ruleset="dnd2014"),
        ClassFeature("Weapon Mastery (4 weapons)", 17, "You can use the mastery property of four kinds of weapons.", ruleset="dnd2024"),
        ClassFeature("Indomitable Might", 18, "If your STR check total is less than your STR score, use your STR score instead."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Primal Champion", 20, "STR and CON scores increase by 4, to a maximum of 24."),
    ]
)

BARD = ClassInfo(
    name="Bard",
    hit_die="d8",
    primary_ability="Charisma",
    saving_throws=["Dexterity", "Charisma"],
    armor_proficiencies=["Light"],
    weapon_proficiencies=["Simple", "Hand crossbows", "Longswords", "Rapiers", "Shortswords"],
    skill_choices=3,
    skill_options=["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History",
                   "Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception",
                   "Performance", "Persuasion", "Religion", "Sleight of Hand", "Stealth", "Survival"],
    spellcasting_ability="Charisma",
    features=[
        ClassFeature("Spellcasting", 1, "You can cast bard spells using Charisma as your spellcasting ability."),
        ClassFeature("Bardic Inspiration", 1, "Use a bonus action to give one creature a Bardic Inspiration die (d6) to add to one ability check, attack roll, or saving throw.", uses=None, recharge="long rest"),
        ClassFeature("Jack of All Trades", 2, "Add half your proficiency bonus to any ability check that doesn't already include your proficiency bonus."),
        ClassFeature("Song of Rest", 2, "During a short rest, you and allies regain an extra 1d6 hit points from Hit Dice."),
        ClassFeature("Bard College", 3, "Choose a Bard College that grants features at 3rd, 6th, and 14th level."),
        ClassFeature("Expertise", 3, "Choose two skill proficiencies to double your proficiency bonus."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Bardic Inspiration (d8)", 5, "Your Bardic Inspiration die becomes a d8."),
        ClassFeature("Font of Inspiration", 5, "Bardic Inspiration recharges on a short rest."),
        ClassFeature("Countercharm", 6, "As an action, start a performance that gives you and allies advantage on saves vs. being frightened or charmed."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Song of Rest (d8)", 9, "Your Song of Rest die becomes a d8."),
        ClassFeature("Bardic Inspiration (d10)", 10, "Your Bardic Inspiration die becomes a d10."),
        ClassFeature("Magical Secrets", 10, "Learn two spells from any class."),
        ClassFeature("Expertise", 10, "Choose two more skill proficiencies to double your proficiency bonus."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Song of Rest (d10)", 13, "Your Song of Rest die becomes a d10."),
        ClassFeature("Magical Secrets", 14, "Learn two additional spells from any class."),
        ClassFeature("Bardic Inspiration (d12)", 15, "Your Bardic Inspiration die becomes a d12."),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Song of Rest (d12)", 17, "Your Song of Rest die becomes a d12."),
        ClassFeature("Magical Secrets", 18, "Learn two additional spells from any class."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Superior Inspiration", 20, "If you have no Bardic Inspiration dice when you roll initiative, regain one."),
    ]
)

CLERIC = ClassInfo(
    name="Cleric",
    hit_die="d8",
    primary_ability="Wisdom",
    saving_throws=["Wisdom", "Charisma"],
    armor_proficiencies=["Light", "Medium", "Shields"],
    weapon_proficiencies=["Simple"],
    skill_choices=2,
    skill_options=["History", "Insight", "Medicine", "Persuasion", "Religion"],
    spellcasting_ability="Wisdom",
    features=[
        ClassFeature("Spellcasting", 1, "You can cast cleric spells using Wisdom as your spellcasting ability."),
        ClassFeature("Divine Domain", 1, "Choose a Divine Domain related to your deity."),
        ClassFeature("Channel Divinity", 2, "Gain the ability to channel divine energy. Turn Undead is always available.", uses=1, recharge="short rest"),
        ClassFeature("Turn Undead", 2, "As an action, present your holy symbol. Each undead within 30 feet must make a WIS save or be turned for 1 minute."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Destroy Undead (CR 1/2)", 5, "When an undead fails its save vs. Turn Undead and is CR 1/2 or lower, it is destroyed."),
        ClassFeature("Channel Divinity (2/rest)", 6, "You can use Channel Divinity twice between rests."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Destroy Undead (CR 1)", 8, "Destroy Undead now affects undead of CR 1 or lower."),
        ClassFeature("Divine Intervention", 10, "Call on your deity to intervene. Roll percentile dice; if you roll equal to or less than your cleric level, your deity intervenes.", uses=1, recharge="long rest"),
        ClassFeature("Destroy Undead (CR 2)", 11, "Destroy Undead now affects undead of CR 2 or lower."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Destroy Undead (CR 3)", 14, "Destroy Undead now affects undead of CR 3 or lower."),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Destroy Undead (CR 4)", 17, "Destroy Undead now affects undead of CR 4 or lower."),
        ClassFeature("Channel Divinity (3/rest)", 18, "You can use Channel Divinity three times between rests."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Divine Intervention Improvement", 20, "Your Divine Intervention feature succeeds automatically."),
    ]
)

DRUID = ClassInfo(
    name="Druid",
    hit_die="d8",
    primary_ability="Wisdom",
    saving_throws=["Intelligence", "Wisdom"],
    armor_proficiencies=["Light", "Medium", "Shields (non-metal)"],
    weapon_proficiencies=["Clubs", "Daggers", "Darts", "Javelins", "Maces", "Quarterstaffs", "Scimitars", "Sickles", "Slings", "Spears"],
    skill_choices=2,
    skill_options=["Arcana", "Animal Handling", "Insight", "Medicine", "Nature", "Perception", "Religion", "Survival"],
    spellcasting_ability="Wisdom",
    features=[
        ClassFeature("Druidic", 1, "You know Druidic, the secret language of druids."),
        ClassFeature("Spellcasting", 1, "You can cast druid spells using Wisdom as your spellcasting ability."),
        ClassFeature("Wild Shape", 2, "As an action, magically assume the shape of a beast you have seen before.", uses=2, recharge="short rest"),
        ClassFeature("Druid Circle", 2, "Choose a Druid Circle that grants features."),
        ClassFeature("Wild Shape Improvement", 4, "Can transform into beasts with CR 1/2 or lower (no flying speed)."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Wild Shape Improvement", 8, "Can transform into beasts with CR 1 or lower."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Timeless Body", 18, "You age more slowly. For every 10 years, your body ages only 1 year."),
        ClassFeature("Beast Spells", 18, "You can cast spells in beast form (no material components)."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Archdruid", 20, "You can use Wild Shape an unlimited number of times."),
    ]
)

FIGHTER = ClassInfo(
    name="Fighter",
    hit_die="d10",
    primary_ability="Strength or Dexterity",
    saving_throws=["Strength", "Constitution"],
    armor_proficiencies=["Light", "Medium", "Heavy", "Shields"],
    weapon_proficiencies=["Simple", "Martial"],
    skill_choices=2,
    skill_options=["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"],
    spellcasting_ability=None,
    weapon_masteries=3,  # 2024: Start with 3 weapon masteries
    features=[
        ClassFeature("Fighting Style", 1, "Choose a fighting style: Archery, Defense, Dueling, Great Weapon Fighting, Protection, or Two-Weapon Fighting."),
        ClassFeature("Second Wind", 1, "On your turn, use a bonus action to regain 1d10 + fighter level hit points.", uses=1, recharge="short rest"),
        ClassFeature("Weapon Mastery", 1, "You can use the mastery property of three kinds of Simple or Martial weapons. When you finish a long rest, you can change the weapons you have selected.", ruleset="dnd2024"),
        ClassFeature("Action Surge", 2, "On your turn, take one additional action.", uses=1, recharge="short rest"),
        ClassFeature("Martial Archetype", 3, "Choose a Martial Archetype that grants features."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Extra Attack", 5, "Attack twice when you take the Attack action."),
        ClassFeature("Ability Score Improvement", 6, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Weapon Mastery (4 weapons)", 7, "You can use the mastery property of four kinds of weapons.", ruleset="dnd2024"),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Indomitable", 9, "Reroll a failed saving throw.", uses=1, recharge="long rest"),
        ClassFeature("Extra Attack (2)", 11, "Attack three times when you take the Attack action."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Indomitable (2 uses)", 13, "You can use Indomitable twice between long rests.", uses=2, recharge="long rest"),
        ClassFeature("Ability Score Improvement", 14, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Weapon Mastery (5 weapons)", 15, "You can use the mastery property of five kinds of weapons.", ruleset="dnd2024"),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Action Surge (2 uses)", 17, "You can use Action Surge twice before a rest.", uses=2, recharge="short rest"),
        ClassFeature("Indomitable (3 uses)", 17, "You can use Indomitable three times between long rests.", uses=3, recharge="long rest"),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Extra Attack (3)", 20, "Attack four times when you take the Attack action."),
    ]
)

MONK = ClassInfo(
    name="Monk",
    hit_die="d8",
    primary_ability="Dexterity and Wisdom",
    saving_throws=["Strength", "Dexterity"],
    armor_proficiencies=[],
    weapon_proficiencies=["Simple", "Shortswords"],
    skill_choices=2,
    skill_options=["Acrobatics", "Athletics", "History", "Insight", "Religion", "Stealth"],
    spellcasting_ability=None,
    features=[
        ClassFeature("Unarmored Defense", 1, "While not wearing armor, AC equals 10 + DEX modifier + WIS modifier."),
        ClassFeature("Martial Arts", 1, "Use DEX instead of STR for unarmed strikes and monk weapons. Roll a d4 for unarmed damage."),
        ClassFeature("Ki", 2, "You have ki points equal to your monk level. Spend ki for Flurry of Blows, Patient Defense, or Step of the Wind.", recharge="short rest"),
        ClassFeature("Unarmored Movement", 2, "Your speed increases by 10 feet while not wearing armor."),
        ClassFeature("Monastic Tradition", 3, "Choose a Monastic Tradition that grants features."),
        ClassFeature("Deflect Missiles", 3, "Use your reaction to deflect or catch a ranged weapon attack."),
        ClassFeature("Slow Fall", 4, "Use your reaction to reduce falling damage by 5 times your monk level."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Extra Attack", 5, "Attack twice when you take the Attack action."),
        ClassFeature("Stunning Strike", 5, "When you hit with a melee weapon attack, spend 1 ki point to attempt to stun the target."),
        ClassFeature("Martial Arts (d6)", 5, "Your Martial Arts damage die becomes a d6."),
        ClassFeature("Ki-Empowered Strikes", 6, "Your unarmed strikes count as magical."),
        ClassFeature("Unarmored Movement (+15 ft)", 6, "Your speed increases by 15 feet while not wearing armor."),
        ClassFeature("Evasion", 7, "When you make a DEX save for half damage, take no damage on success, half on failure."),
        ClassFeature("Stillness of Mind", 7, "Use your action to end one effect causing you to be charmed or frightened."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Unarmored Movement (vertical surfaces)", 9, "You can move along vertical surfaces and across liquids without falling."),
        ClassFeature("Purity of Body", 10, "You are immune to disease and poison."),
        ClassFeature("Unarmored Movement (+20 ft)", 10, "Your speed increases by 20 feet while not wearing armor."),
        ClassFeature("Martial Arts (d8)", 11, "Your Martial Arts damage die becomes a d8."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Tongue of the Sun and Moon", 13, "You can understand and be understood by any creature with a language."),
        ClassFeature("Diamond Soul", 14, "You are proficient in all saving throws."),
        ClassFeature("Unarmored Movement (+25 ft)", 14, "Your speed increases by 25 feet while not wearing armor."),
        ClassFeature("Timeless Body", 15, "You suffer none of the frailty of old age and can't be aged magically."),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Martial Arts (d10)", 17, "Your Martial Arts damage die becomes a d10."),
        ClassFeature("Empty Body", 18, "Spend 4 ki points to become invisible for 1 minute."),
        ClassFeature("Unarmored Movement (+30 ft)", 18, "Your speed increases by 30 feet while not wearing armor."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Perfect Self", 20, "If you have no ki points when you roll initiative, regain 4 ki points."),
    ]
)

PALADIN = ClassInfo(
    name="Paladin",
    hit_die="d10",
    primary_ability="Strength and Charisma",
    saving_throws=["Wisdom", "Charisma"],
    armor_proficiencies=["Light", "Medium", "Heavy", "Shields"],
    weapon_proficiencies=["Simple", "Martial"],
    skill_choices=2,
    skill_options=["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"],
    spellcasting_ability="Charisma",
    weapon_masteries=2,  # 2024: Start with 2 weapon masteries
    features=[
        ClassFeature("Divine Sense", 1, "Detect celestials, fiends, and undead within 60 feet.", uses=None, recharge="long rest"),
        ClassFeature("Lay on Hands", 1, "You have a pool of healing power equal to paladin level x 5.", recharge="long rest"),
        ClassFeature("Weapon Mastery", 1, "You can use the mastery property of two kinds of Simple or Martial weapons. When you finish a long rest, you can change the weapons you have selected.", ruleset="dnd2024"),
        ClassFeature("Fighting Style", 2, "Choose a fighting style: Defense, Dueling, Great Weapon Fighting, or Protection."),
        ClassFeature("Spellcasting", 2, "You can cast paladin spells using Charisma as your spellcasting ability."),
        ClassFeature("Divine Smite", 2, "When you hit with a melee weapon attack, expend a spell slot to deal extra radiant damage."),
        ClassFeature("Divine Health", 3, "You are immune to disease."),
        ClassFeature("Sacred Oath", 3, "Choose a Sacred Oath that grants features."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Extra Attack", 5, "Attack twice when you take the Attack action."),
        ClassFeature("Aura of Protection", 6, "You and friendly creatures within 10 feet gain a bonus to saving throws equal to your CHA modifier."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Weapon Mastery (3 weapons)", 9, "You can use the mastery property of three kinds of weapons.", ruleset="dnd2024"),
        ClassFeature("Aura of Courage", 10, "You and friendly creatures within 10 feet can't be frightened while you're conscious."),
        ClassFeature("Improved Divine Smite", 11, "All melee weapon attacks deal an extra 1d8 radiant damage."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Cleansing Touch", 14, "Use your action to end one spell on yourself or a willing creature you touch.", uses=None, recharge="long rest"),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Aura Improvements", 18, "Your auras now extend to 30 feet."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
    ]
)

RANGER = ClassInfo(
    name="Ranger",
    hit_die="d10",
    primary_ability="Dexterity and Wisdom",
    saving_throws=["Strength", "Dexterity"],
    armor_proficiencies=["Light", "Medium", "Shields"],
    weapon_proficiencies=["Simple", "Martial"],
    skill_choices=3,
    skill_options=["Animal Handling", "Athletics", "Insight", "Investigation", "Nature", "Perception", "Stealth", "Survival"],
    spellcasting_ability="Wisdom",
    weapon_masteries=2,  # 2024: Start with 2 weapon masteries
    features=[
        ClassFeature("Favored Enemy", 1, "Choose a type of favored enemy. You have advantage on Survival checks to track them and Intelligence checks to recall info about them.", ruleset="dnd2014"),
        ClassFeature("Natural Explorer", 1, "Choose a type of favored terrain. You gain benefits when traveling through that terrain.", ruleset="dnd2014"),
        ClassFeature("Weapon Mastery", 1, "You can use the mastery property of two kinds of Simple or Martial weapons. When you finish a long rest, you can change the weapons you have selected.", ruleset="dnd2024"),
        ClassFeature("Fighting Style", 2, "Choose a fighting style: Archery, Defense, Dueling, or Two-Weapon Fighting."),
        ClassFeature("Spellcasting", 2, "You can cast ranger spells using Wisdom as your spellcasting ability."),
        ClassFeature("Ranger Archetype", 3, "Choose a Ranger Archetype that grants features."),
        ClassFeature("Primeval Awareness", 3, "Expend a spell slot to sense certain creature types within 1 mile."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Extra Attack", 5, "Attack twice when you take the Attack action."),
        ClassFeature("Favored Enemy Improvement", 6, "Choose another favored enemy type.", ruleset="dnd2014"),
        ClassFeature("Natural Explorer Improvement", 6, "Choose another favored terrain type.", ruleset="dnd2014"),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Land's Stride", 8, "Moving through nonmagical difficult terrain costs no extra movement."),
        ClassFeature("Weapon Mastery (3 weapons)", 9, "You can use the mastery property of three kinds of weapons.", ruleset="dnd2024"),
        ClassFeature("Natural Explorer Improvement", 10, "Choose another favored terrain type.", ruleset="dnd2014"),
        ClassFeature("Hide in Plain Sight", 10, "Spend 1 minute creating camouflage to gain +10 to Stealth checks while remaining still.", ruleset="dnd2014"),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Vanish", 14, "You can use Hide as a bonus action, and you can't be tracked by nonmagical means."),
        ClassFeature("Favored Enemy Improvement", 14, "Choose another favored enemy type.", ruleset="dnd2014"),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Weapon Mastery (4 weapons)", 17, "You can use the mastery property of four kinds of weapons.", ruleset="dnd2024"),
        ClassFeature("Feral Senses", 18, "You have a sense for invisible creatures within 30 feet."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Foe Slayer", 20, "Once per turn, add your WIS modifier to attack or damage against your favored enemy."),
    ]
)

ROGUE = ClassInfo(
    name="Rogue",
    hit_die="d8",
    primary_ability="Dexterity",
    saving_throws=["Dexterity", "Intelligence"],
    armor_proficiencies=["Light"],
    weapon_proficiencies=["Simple", "Hand crossbows", "Longswords", "Rapiers", "Shortswords"],
    skill_choices=4,
    skill_options=["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation",
                   "Perception", "Performance", "Persuasion", "Sleight of Hand", "Stealth"],
    spellcasting_ability=None,
    features=[
        ClassFeature("Expertise", 1, "Choose two skill proficiencies to double your proficiency bonus."),
        ClassFeature("Sneak Attack (1d6)", 1, "Deal extra 1d6 damage to one creature you hit with advantage or if an ally is within 5 feet of the target."),
        ClassFeature("Thieves' Cant", 1, "You know thieves' cant, a secret mix of dialect and coded messages."),
        ClassFeature("Cunning Action", 2, "On your turn, use a bonus action to Dash, Disengage, or Hide."),
        ClassFeature("Roguish Archetype", 3, "Choose a Roguish Archetype that grants features."),
        ClassFeature("Sneak Attack (2d6)", 3, "Sneak Attack damage increases to 2d6."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Sneak Attack (3d6)", 5, "Sneak Attack damage increases to 3d6."),
        ClassFeature("Uncanny Dodge", 5, "Use your reaction to halve an attack's damage against you."),
        ClassFeature("Expertise", 6, "Choose two more skill proficiencies to double your proficiency bonus."),
        ClassFeature("Sneak Attack (4d6)", 7, "Sneak Attack damage increases to 4d6."),
        ClassFeature("Evasion", 7, "When you make a DEX save for half damage, take no damage on success, half on failure."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Sneak Attack (5d6)", 9, "Sneak Attack damage increases to 5d6."),
        ClassFeature("Ability Score Improvement", 10, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Sneak Attack (6d6)", 11, "Sneak Attack damage increases to 6d6."),
        ClassFeature("Reliable Talent", 11, "When you make an ability check with a skill you're proficient in, treat any d20 roll of 9 or lower as a 10."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Sneak Attack (7d6)", 13, "Sneak Attack damage increases to 7d6."),
        ClassFeature("Blindsense", 14, "You can sense hidden or invisible creatures within 10 feet."),
        ClassFeature("Sneak Attack (8d6)", 15, "Sneak Attack damage increases to 8d6."),
        ClassFeature("Slippery Mind", 15, "You gain proficiency in Wisdom saving throws."),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Sneak Attack (9d6)", 17, "Sneak Attack damage increases to 9d6."),
        ClassFeature("Elusive", 18, "Attacks against you don't have advantage while you're conscious."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Sneak Attack (10d6)", 19, "Sneak Attack damage increases to 10d6."),
        ClassFeature("Stroke of Luck", 20, "If your attack misses, you can turn it into a hit. If you fail an ability check, treat the d20 roll as a 20.", uses=1, recharge="short rest"),
    ]
)

SORCERER = ClassInfo(
    name="Sorcerer",
    hit_die="d6",
    primary_ability="Charisma",
    saving_throws=["Constitution", "Charisma"],
    armor_proficiencies=[],
    weapon_proficiencies=["Daggers", "Darts", "Slings", "Quarterstaffs", "Light crossbows"],
    skill_choices=2,
    skill_options=["Arcana", "Deception", "Insight", "Intimidation", "Persuasion", "Religion"],
    spellcasting_ability="Charisma",
    features=[
        ClassFeature("Spellcasting", 1, "You can cast sorcerer spells using Charisma as your spellcasting ability."),
        ClassFeature("Sorcerous Origin", 1, "Choose a Sorcerous Origin that grants features."),
        ClassFeature("Font of Magic", 2, "You have sorcery points equal to your sorcerer level."),
        ClassFeature("Flexible Casting", 2, "Create spell slots by spending sorcery points, or gain sorcery points by expending spell slots."),
        ClassFeature("Metamagic", 3, "Choose two Metamagic options. You can use only one Metamagic option per spell."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Metamagic", 10, "Choose an additional Metamagic option."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Metamagic", 17, "Choose an additional Metamagic option."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Sorcerous Restoration", 20, "Regain 4 sorcery points on a short rest."),
    ]
)

WARLOCK = ClassInfo(
    name="Warlock",
    hit_die="d8",
    primary_ability="Charisma",
    saving_throws=["Wisdom", "Charisma"],
    armor_proficiencies=["Light"],
    weapon_proficiencies=["Simple"],
    skill_choices=2,
    skill_options=["Arcana", "Deception", "History", "Intimidation", "Investigation", "Nature", "Religion"],
    spellcasting_ability="Charisma",
    features=[
        ClassFeature("Otherworldly Patron", 1, "Choose a patron that grants features and expanded spell options."),
        ClassFeature("Pact Magic", 1, "You can cast warlock spells using Charisma. Your spell slots recharge on a short rest."),
        ClassFeature("Eldritch Invocations", 2, "Choose two Eldritch Invocations that grant special abilities."),
        ClassFeature("Pact Boon", 3, "Choose a Pact Boon: Pact of the Chain, Pact of the Blade, or Pact of the Tome."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Eldritch Invocations", 5, "Learn an additional Eldritch Invocation."),
        ClassFeature("Eldritch Invocations", 7, "Learn an additional Eldritch Invocation."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Eldritch Invocations", 9, "Learn an additional Eldritch Invocation."),
        ClassFeature("Mystic Arcanum (6th level)", 11, "Choose one 6th-level spell from the warlock spell list that you can cast once per long rest without a spell slot."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Mystic Arcanum (7th level)", 13, "Choose one 7th-level spell from the warlock spell list that you can cast once per long rest without a spell slot."),
        ClassFeature("Eldritch Invocations", 12, "Learn an additional Eldritch Invocation."),
        ClassFeature("Mystic Arcanum (8th level)", 15, "Choose one 8th-level spell from the warlock spell list that you can cast once per long rest without a spell slot."),
        ClassFeature("Eldritch Invocations", 15, "Learn an additional Eldritch Invocation."),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Mystic Arcanum (9th level)", 17, "Choose one 9th-level spell from the warlock spell list that you can cast once per long rest without a spell slot."),
        ClassFeature("Eldritch Invocations", 18, "Learn an additional Eldritch Invocation."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Eldritch Master", 20, "Spend 1 minute entreating your patron to regain all expended spell slots.", uses=1, recharge="long rest"),
    ]
)

WIZARD = ClassInfo(
    name="Wizard",
    hit_die="d6",
    primary_ability="Intelligence",
    saving_throws=["Intelligence", "Wisdom"],
    armor_proficiencies=[],
    weapon_proficiencies=["Daggers", "Darts", "Slings", "Quarterstaffs", "Light crossbows"],
    skill_choices=2,
    skill_options=["Arcana", "History", "Insight", "Investigation", "Medicine", "Religion"],
    spellcasting_ability="Intelligence",
    features=[
        ClassFeature("Spellcasting", 1, "You can cast wizard spells using Intelligence. You use a spellbook."),
        ClassFeature("Arcane Recovery", 1, "Once per day when you finish a short rest, recover expended spell slots with combined levels equal to half your wizard level (rounded up).", uses=1, recharge="long rest"),
        ClassFeature("Arcane Tradition", 2, "Choose an Arcane Tradition that grants features."),
        ClassFeature("Ability Score Improvement", 4, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Ability Score Improvement", 8, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Ability Score Improvement", 12, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Ability Score Improvement", 16, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Spell Mastery", 18, "Choose a 1st-level and a 2nd-level spell to cast at will without expending a spell slot."),
        ClassFeature("Ability Score Improvement", 19, "Increase one ability score by 2, or two ability scores by 1, or take a feat."),
        ClassFeature("Signature Spells", 20, "Choose two 3rd-level spells that are always prepared and can be cast once each without a spell slot.", uses=2, recharge="short rest"),
    ]
)

# All classes dictionary
ALL_CLASSES = {
    "Barbarian": BARBARIAN,
    "Bard": BARD,
    "Cleric": CLERIC,
    "Druid": DRUID,
    "Fighter": FIGHTER,
    "Monk": MONK,
    "Paladin": PALADIN,
    "Ranger": RANGER,
    "Rogue": ROGUE,
    "Sorcerer": SORCERER,
    "Warlock": WARLOCK,
    "Wizard": WIZARD,
}


# =============================================================================
# MULTICLASSING DATA
# =============================================================================

# Ability score requirements for multiclassing into a class
# Note: Fighter can use STR OR DEX (handled in validation logic)
MULTICLASS_REQUIREMENTS: dict[str, dict[str, int]] = {
    "Barbarian": {"strength": 13},
    "Bard": {"charisma": 13},
    "Cleric": {"wisdom": 13},
    "Druid": {"wisdom": 13},
    "Fighter": {"strength": 13},  # Also accepts dexterity >= 13
    "Monk": {"dexterity": 13, "wisdom": 13},
    "Paladin": {"strength": 13, "charisma": 13},
    "Ranger": {"dexterity": 13, "wisdom": 13},
    "Rogue": {"dexterity": 13},
    "Sorcerer": {"charisma": 13},
    "Warlock": {"charisma": 13},
    "Wizard": {"intelligence": 13},
}

# Classes that can use an alternate ability score for multiclass requirements
MULTICLASS_ALT_REQUIREMENTS: dict[str, dict[str, int]] = {
    "Fighter": {"dexterity": 13},  # Fighter can use DEX instead of STR
}

# Spellcasting progression type for each class
# Used to calculate multiclass spell slots
CLASS_CASTER_TYPES: dict[str, CasterType] = {
    "Barbarian": CasterType.NONE,
    "Bard": CasterType.FULL,
    "Cleric": CasterType.FULL,
    "Druid": CasterType.FULL,
    "Fighter": CasterType.NONE,  # Eldritch Knight subclass is THIRD
    "Monk": CasterType.NONE,
    "Paladin": CasterType.HALF,
    "Ranger": CasterType.HALF,
    "Rogue": CasterType.NONE,  # Arcane Trickster subclass is THIRD
    "Sorcerer": CasterType.FULL,
    "Warlock": CasterType.PACT,  # Separate pact magic
    "Wizard": CasterType.FULL,
}

# Subclasses that grant spellcasting (third casters)
THIRD_CASTER_SUBCLASSES: dict[str, list[str]] = {
    "Fighter": ["Eldritch Knight"],
    "Rogue": ["Arcane Trickster"],
}

# Multiclass spellcaster spell slots table (by combined caster level)
# Based on PHB multiclass spellcaster table
MULTICLASS_SPELL_SLOTS: dict[int, dict[int, int]] = {
    # caster_level: {spell_level: slots}
    1: {1: 2},
    2: {1: 3},
    3: {1: 4, 2: 2},
    4: {1: 4, 2: 3},
    5: {1: 4, 2: 3, 3: 2},
    6: {1: 4, 2: 3, 3: 3},
    7: {1: 4, 2: 3, 3: 3, 4: 1},
    8: {1: 4, 2: 3, 3: 3, 4: 2},
    9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
}


def get_class_info(class_name: str) -> Optional[ClassInfo]:
    """Get class information by name."""
    return ALL_CLASSES.get(class_name)


def get_features_at_level(class_name: str, level: int) -> list[ClassFeature]:
    """Get all class features gained at a specific level."""
    class_info = get_class_info(class_name)
    if not class_info:
        return []
    return [f for f in class_info.features if f.level == level]


def get_features_up_to_level(class_name: str, level: int) -> list[ClassFeature]:
    """Get all class features from level 1 up to the specified level."""
    class_info = get_class_info(class_name)
    if not class_info:
        return []
    return [f for f in class_info.features if f.level <= level]


def get_features_for_ruleset(
    class_name: str,
    level: int,
    ruleset: Optional[str] = None
) -> list[ClassFeature]:
    """Get class features up to a level filtered by ruleset.

    Args:
        class_name: The class name
        level: Maximum level to include features for
        ruleset: The ruleset ID ('dnd2014', 'dnd2024', 'tov', or None for all)

    Returns:
        List of features up to the specified level, filtered by ruleset.
        Returns features matching the ruleset or with ruleset=None (universal).
    """
    all_features = get_features_up_to_level(class_name, level)
    if ruleset is None:
        return all_features
    return [
        f for f in all_features
        if f.ruleset is None or f.ruleset == ruleset
    ]
