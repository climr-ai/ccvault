"""Subclass data for D&D character options.

Contains SRD subclasses (one per class) with original flavor text
and accurate mechanics.

Note: This file is large (~4,600 lines) to keep all subclass data with Python
dataclass definitions. This provides IDE type checking, fast imports without
runtime parsing, and dataclass methods on subclass instances.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SubclassFeature:
    """A feature granted by a subclass at a specific level."""

    name: str
    level: int
    description: str


@dataclass
class Subclass:
    """A subclass specialization for a character class.

    For ToV subclasses, features typically come at levels 3, 7, 11, and 15.
    """

    name: str
    parent_class: str
    description: str
    features: list[SubclassFeature] = field(default_factory=list)
    subclass_spells: list[tuple[int, list[str]]] = field(default_factory=list)
    source: str = "SRD"
    ruleset: Optional[str] = None  # None = all rulesets, "tov" = Tales of the Valiant only


# =============================================================================
# BARBARIAN - PATH OF THE BERSERKER
# =============================================================================

BERSERKER = Subclass(
    name="Path of the Berserker",
    parent_class="Barbarian",
    description=(
        "For some barbarians, rage is a means to an end—that end being violence. "
        "The Path of the Berserker is a path of untrammeled fury, slick with blood. "
        "As you enter the berserker's rage, you thrill in the chaos of battle, "
        "heedless of your own health or well-being."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Frenzy",
            level=3,
            description=(
                "Starting when you choose this path at 3rd level, you can go into a "
                "frenzy when you rage. If you do so, for the duration of your rage you "
                "can make a single melee weapon attack as a bonus action on each of "
                "your turns after this one. When your rage ends, you suffer one level "
                "of exhaustion."
            ),
        ),
        SubclassFeature(
            name="Mindless Rage",
            level=6,
            description=(
                "Beginning at 6th level, you can't be charmed or frightened while "
                "raging. If you are charmed or frightened when you enter your rage, "
                "the effect is suspended for the duration of the rage."
            ),
        ),
        SubclassFeature(
            name="Intimidating Presence",
            level=10,
            description=(
                "Beginning at 10th level, you can use your action to frighten someone "
                "with your menacing presence. When you do so, choose one creature that "
                "you can see within 30 feet of you. If the creature can see or hear "
                "you, it must succeed on a Wisdom saving throw (DC equal to 8 + your "
                "proficiency bonus + your Charisma modifier) or be frightened of you "
                "until the end of your next turn. On subsequent turns, you can use "
                "your action to extend the duration of this effect on the frightened "
                "creature until the end of your next turn. This effect ends if the "
                "creature ends its turn out of line of sight or more than 60 feet away "
                "from you. If the creature succeeds on its saving throw, you can't use "
                "this feature on that creature again for 24 hours."
            ),
        ),
        SubclassFeature(
            name="Retaliation",
            level=14,
            description=(
                "Starting at 14th level, when you take damage from a creature that is "
                "within 5 feet of you, you can use your reaction to make a melee "
                "weapon attack against that creature."
            ),
        ),
    ],
)

# =============================================================================
# BARD - COLLEGE OF LORE
# =============================================================================

COLLEGE_OF_LORE = Subclass(
    name="College of Lore",
    parent_class="Bard",
    description=(
        "Bards of the College of Lore know something about most things, collecting "
        "bits of knowledge from sources as diverse as scholarly tomes and peasant "
        "tales. Whether singing folk ballads in taverns or elaborate compositions in "
        "royal courts, these bards use their gifts to hold audiences spellbound. "
        "The loyalty of these bards lies in the pursuit of beauty and truth."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Bonus Proficiencies",
            level=3,
            description=(
                "When you join the College of Lore at 3rd level, you gain proficiency "
                "with three skills of your choice."
            ),
        ),
        SubclassFeature(
            name="Cutting Words",
            level=3,
            description=(
                "Also at 3rd level, you learn how to use your wit to distract, confuse, "
                "and otherwise sap the confidence and competence of others. When a "
                "creature that you can see within 60 feet of you makes an attack roll, "
                "an ability check, or a damage roll, you can use your reaction to "
                "expend one of your uses of Bardic Inspiration, rolling a Bardic "
                "Inspiration die and subtracting the number rolled from the creature's "
                "roll. You can choose to use this feature after the creature makes its "
                "roll, but before the DM determines whether the attack roll or ability "
                "check succeeds or fails, or before the creature deals its damage."
            ),
        ),
        SubclassFeature(
            name="Additional Magical Secrets",
            level=6,
            description=(
                "At 6th level, you learn two spells of your choice from any class. A "
                "spell you choose must be of a level you can cast, as shown on the "
                "Bard table, or a cantrip. The chosen spells count as bard spells for "
                "you but don't count against the number of bard spells you know."
            ),
        ),
        SubclassFeature(
            name="Peerless Skill",
            level=14,
            description=(
                "Starting at 14th level, when you make an ability check, you can "
                "expend one use of Bardic Inspiration. Roll a Bardic Inspiration die "
                "and add the number rolled to your ability check. You can choose to do "
                "so after you roll the die for the ability check, but before the DM "
                "tells you whether you succeed or fail."
            ),
        ),
    ],
)

# =============================================================================
# CLERIC - LIFE DOMAIN
# =============================================================================

LIFE_DOMAIN = Subclass(
    name="Life Domain",
    parent_class="Cleric",
    description=(
        "The Life domain focuses on the vibrant positive energy—one of the "
        "fundamental forces of the universe—that sustains all life. The gods of "
        "life promote vitality and health through healing the sick and wounded, "
        "caring for those in need, and driving away the forces of death and undeath."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Bonus Proficiency",
            level=1,
            description=(
                "When you choose this domain at 1st level, you gain proficiency with "
                "heavy armor."
            ),
        ),
        SubclassFeature(
            name="Disciple of Life",
            level=1,
            description=(
                "Also starting at 1st level, your healing spells are more effective. "
                "Whenever you use a spell of 1st level or higher to restore hit points "
                "to a creature, the creature regains additional hit points equal to "
                "2 + the spell's level."
            ),
        ),
        SubclassFeature(
            name="Channel Divinity: Preserve Life",
            level=2,
            description=(
                "Starting at 2nd level, you can use your Channel Divinity to heal the "
                "badly injured. As an action, you present your holy symbol and evoke "
                "healing energy that can restore a number of hit points equal to five "
                "times your cleric level. Choose any creatures within 30 feet of you, "
                "and divide those hit points among them. This feature can restore a "
                "creature to no more than half of its hit point maximum. You can't use "
                "this feature on an undead or a construct."
            ),
        ),
        SubclassFeature(
            name="Blessed Healer",
            level=6,
            description=(
                "Beginning at 6th level, the healing spells you cast on others heal "
                "you as well. When you cast a spell of 1st level or higher that "
                "restores hit points to a creature other than you, you regain hit "
                "points equal to 2 + the spell's level."
            ),
        ),
        SubclassFeature(
            name="Divine Strike",
            level=8,
            description=(
                "At 8th level, you gain the ability to infuse your weapon strikes with "
                "divine energy. Once on each of your turns when you hit a creature "
                "with a weapon attack, you can cause the attack to deal an extra 1d8 "
                "radiant damage to the target. When you reach 14th level, the extra "
                "damage increases to 2d8."
            ),
        ),
        SubclassFeature(
            name="Supreme Healing",
            level=17,
            description=(
                "Starting at 17th level, when you would normally roll one or more dice "
                "to restore hit points with a spell, you instead use the highest "
                "number possible for each die. For example, instead of restoring 2d6 "
                "hit points to a creature, you restore 12."
            ),
        ),
    ],
    subclass_spells=[
        (1, ["Bless", "Cure Wounds"]),
        (3, ["Lesser Restoration", "Spiritual Weapon"]),
        (5, ["Beacon of Hope", "Revivify"]),
        (7, ["Death Ward", "Guardian of Faith"]),
        (9, ["Mass Cure Wounds", "Raise Dead"]),
    ],
)

# =============================================================================
# DRUID - CIRCLE OF THE LAND
# =============================================================================

CIRCLE_OF_THE_LAND = Subclass(
    name="Circle of the Land",
    parent_class="Druid",
    description=(
        "The Circle of the Land is made up of mystics and sages who safeguard "
        "ancient knowledge and rites through a vast oral tradition. These druids "
        "meet within sacred circles of trees or standing stones to whisper primal "
        "secrets. The circle's wisest members preside as the chief priests of "
        "communities that hold to the Old Faith."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Bonus Cantrip",
            level=2,
            description=(
                "When you choose this circle at 2nd level, you learn one additional "
                "druid cantrip of your choice."
            ),
        ),
        SubclassFeature(
            name="Natural Recovery",
            level=2,
            description=(
                "Starting at 2nd level, you can regain some of your magical energy by "
                "sitting in meditation and communing with nature. During a short rest, "
                "you choose expended spell slots to recover. The spell slots can have "
                "a combined level that is equal to or less than half your druid level "
                "(rounded up), and none of the slots can be 6th level or higher. You "
                "can't use this feature again until you finish a long rest."
            ),
        ),
        SubclassFeature(
            name="Circle Spells",
            level=3,
            description=(
                "Your mystical connection to the land infuses you with the ability to "
                "cast certain spells. At 3rd, 5th, 7th, and 9th level you gain access "
                "to circle spells connected to the land where you became a druid. "
                "Choose that land—arctic, coast, desert, forest, grassland, mountain, "
                "swamp, or Underdark—and consult the associated list of spells. These "
                "spells are always prepared and don't count against the number of "
                "spells you can prepare each day."
            ),
        ),
        SubclassFeature(
            name="Land's Stride",
            level=6,
            description=(
                "Starting at 6th level, moving through nonmagical difficult terrain "
                "costs you no extra movement. You can also pass through nonmagical "
                "plants without being slowed by them and without taking damage from "
                "them if they have thorns, spines, or a similar hazard. In addition, "
                "you have advantage on saving throws against plants that are magically "
                "created or manipulated to impede movement."
            ),
        ),
        SubclassFeature(
            name="Nature's Ward",
            level=10,
            description=(
                "When you reach 10th level, you can't be charmed or frightened by "
                "elementals or fey, and you are immune to poison and disease."
            ),
        ),
        SubclassFeature(
            name="Nature's Sanctuary",
            level=14,
            description=(
                "When you reach 14th level, creatures of the natural world sense your "
                "connection to nature and become hesitant to attack you. When a beast "
                "or plant creature attacks you, that creature must make a Wisdom "
                "saving throw against your druid spell save DC. On a failed save, the "
                "creature must choose a different target, or the attack automatically "
                "misses. On a successful save, the creature is immune to this effect "
                "for 24 hours. The creature is aware of this effect before it makes "
                "its attack against you."
            ),
        ),
    ],
)

# =============================================================================
# FIGHTER - CHAMPION
# =============================================================================

CHAMPION = Subclass(
    name="Champion",
    parent_class="Fighter",
    description=(
        "The archetypal Champion focuses on the development of raw physical power "
        "honed to deadly perfection. Those who model themselves on this archetype "
        "combine rigorous training with physical excellence to deal devastating "
        "blows. The simplicity of the Champion's approach belies its effectiveness."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Improved Critical",
            level=3,
            description=(
                "Beginning when you choose this archetype at 3rd level, your weapon "
                "attacks score a critical hit on a roll of 19 or 20."
            ),
        ),
        SubclassFeature(
            name="Remarkable Athlete",
            level=7,
            description=(
                "Starting at 7th level, you can add half your proficiency bonus "
                "(round up) to any Strength, Dexterity, or Constitution check you "
                "make that doesn't already use your proficiency bonus. In addition, "
                "when you make a running long jump, the distance you can cover "
                "increases by a number of feet equal to your Strength modifier."
            ),
        ),
        SubclassFeature(
            name="Additional Fighting Style",
            level=10,
            description=(
                "At 10th level, you can choose a second option from the Fighting "
                "Style class feature."
            ),
        ),
        SubclassFeature(
            name="Superior Critical",
            level=15,
            description=(
                "Starting at 15th level, your weapon attacks score a critical hit on "
                "a roll of 18–20."
            ),
        ),
        SubclassFeature(
            name="Survivor",
            level=18,
            description=(
                "At 18th level, you attain the pinnacle of resilience in battle. At "
                "the start of each of your turns, you regain hit points equal to "
                "5 + your Constitution modifier if you have no more than half of your "
                "hit points left. You don't gain this benefit if you have 0 hit points."
            ),
        ),
    ],
)

# =============================================================================
# MONK - WAY OF THE OPEN HAND
# =============================================================================

WAY_OF_THE_OPEN_HAND = Subclass(
    name="Way of the Open Hand",
    parent_class="Monk",
    description=(
        "Monks of the Way of the Open Hand are the ultimate masters of martial arts "
        "combat, whether armed or unarmed. They learn techniques to push and trip "
        "their opponents, manipulate ki to heal damage to their bodies, and practice "
        "advanced meditation that can protect them from harm."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Open Hand Technique",
            level=3,
            description=(
                "Starting when you choose this tradition at 3rd level, you can "
                "manipulate your enemy's ki when you harness your own. Whenever you "
                "hit a creature with one of the attacks granted by your Flurry of "
                "Blows, you can impose one of the following effects on that target: "
                "It must succeed on a Dexterity saving throw or be knocked prone. "
                "It must make a Strength saving throw. If it fails, you can push it "
                "up to 15 feet away from you. It can't take reactions until the end "
                "of your next turn."
            ),
        ),
        SubclassFeature(
            name="Wholeness of Body",
            level=6,
            description=(
                "At 6th level, you gain the ability to heal yourself. As an action, "
                "you can regain hit points equal to three times your monk level. You "
                "must finish a long rest before you can use this feature again."
            ),
        ),
        SubclassFeature(
            name="Tranquility",
            level=11,
            description=(
                "Beginning at 11th level, you can enter a special meditation that "
                "surrounds you with an aura of peace. At the end of a long rest, you "
                "gain the effect of a sanctuary spell that lasts until the start of "
                "your next long rest (the spell can end early as normal). The saving "
                "throw DC for the spell equals 8 + your Wisdom modifier + your "
                "proficiency bonus."
            ),
        ),
        SubclassFeature(
            name="Quivering Palm",
            level=17,
            description=(
                "At 17th level, you gain the ability to set up lethal vibrations in "
                "someone's body. When you hit a creature with an unarmed strike, you "
                "can spend 3 ki points to start these imperceptible vibrations, which "
                "last for a number of days equal to your monk level. The vibrations "
                "are harmless unless you use your action to end them. To do so, you "
                "and the target must be on the same plane of existence. When you use "
                "this action, the creature must make a Constitution saving throw. If "
                "it fails, it is reduced to 0 hit points. If it succeeds, it takes "
                "10d10 necrotic damage. You can have only one creature under the "
                "effect of this feature at a time."
            ),
        ),
    ],
)

# =============================================================================
# PALADIN - OATH OF DEVOTION
# =============================================================================

OATH_OF_DEVOTION = Subclass(
    name="Oath of Devotion",
    parent_class="Paladin",
    description=(
        "The Oath of Devotion binds a paladin to the loftiest ideals of justice, "
        "virtue, and order. Sometimes called cavaliers, white knights, or holy "
        "warriors, these paladins meet the ideal of the knight in shining armor, "
        "acting with honor in pursuit of justice and the greater good."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Tenets of Devotion",
            level=3,
            description=(
                "The tenets of the Oath of Devotion drive a paladin to the highest "
                "standards of conduct: Honesty (Don't lie or cheat. Let your word be "
                "your promise.), Courage (Never fear to act, though caution is wise.), "
                "Compassion (Aid others, protect the weak, and punish those who "
                "threaten them.), Honor (Treat others with fairness, and let your "
                "honorable deeds be an example to them.), Duty (Be responsible for "
                "your actions and their consequences. Protect those entrusted to your "
                "care and obey those who have authority over you.)"
            ),
        ),
        SubclassFeature(
            name="Channel Divinity",
            level=3,
            description=(
                "When you take this oath at 3rd level, you gain the following two "
                "Channel Divinity options. Sacred Weapon: As an action, you can imbue "
                "one weapon that you are holding with positive energy. For 1 minute, "
                "you add your Charisma modifier to attack rolls made with that weapon "
                "(minimum +1). The weapon also emits bright light in a 20-foot radius "
                "and dim light 20 feet beyond that. Turn the Unholy: As an action, "
                "each fiend or undead that can see or hear you within 30 feet must "
                "make a Wisdom saving throw or be turned for 1 minute or until it "
                "takes damage."
            ),
        ),
        SubclassFeature(
            name="Aura of Devotion",
            level=7,
            description=(
                "Starting at 7th level, you and friendly creatures within 10 feet of "
                "you can't be charmed while you are conscious. At 18th level, the "
                "range of this aura increases to 30 feet."
            ),
        ),
        SubclassFeature(
            name="Purity of Spirit",
            level=15,
            description=(
                "Beginning at 15th level, you are always under the effects of a "
                "protection from evil and good spell."
            ),
        ),
        SubclassFeature(
            name="Holy Nimbus",
            level=20,
            description=(
                "At 20th level, as an action, you can emanate an aura of sunlight. "
                "For 1 minute, bright light shines from you in a 30-foot radius, and "
                "dim light shines 30 feet beyond that. Whenever an enemy creature "
                "starts its turn in the bright light, the creature takes 10 radiant "
                "damage. In addition, for the duration, you have advantage on saving "
                "throws against spells cast by fiends or undead. Once you use this "
                "feature, you can't use it again until you finish a long rest."
            ),
        ),
    ],
    subclass_spells=[
        (3, ["Protection from Evil and Good", "Sanctuary"]),
        (5, ["Lesser Restoration", "Zone of Truth"]),
        (9, ["Beacon of Hope", "Dispel Magic"]),
        (13, ["Freedom of Movement", "Guardian of Faith"]),
        (17, ["Commune", "Flame Strike"]),
    ],
)

# =============================================================================
# RANGER - HUNTER
# =============================================================================

HUNTER = Subclass(
    name="Hunter",
    parent_class="Ranger",
    description=(
        "Emulating the Hunter archetype means accepting your place as a bulwark "
        "between civilization and the terrors of the wilderness. As you walk the "
        "Hunter's path, you learn specialized techniques for fighting the threats "
        "you face, from rampaging ogres and hordes of orcs to towering giants and "
        "terrifying dragons."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Hunter's Prey",
            level=3,
            description=(
                "At 3rd level, you gain one of the following features of your choice: "
                "Colossus Slayer (Once per turn, deal an extra 1d8 damage to a creature "
                "you hit if it's below its hit point maximum.), Giant Killer (When a "
                "Large or larger creature within 5 feet of you hits or misses you with "
                "an attack, you can use your reaction to attack that creature.), or "
                "Horde Breaker (Once on each of your turns, you can make another weapon "
                "attack against a different creature within 5 feet of the original "
                "target and within range of your weapon.)"
            ),
        ),
        SubclassFeature(
            name="Defensive Tactics",
            level=7,
            description=(
                "At 7th level, you gain one of the following features of your choice: "
                "Escape the Horde (Opportunity attacks against you are made with "
                "disadvantage.), Multiattack Defense (When a creature hits you with "
                "an attack, you gain a +4 bonus to AC against all subsequent attacks "
                "made by that creature for the rest of the turn.), or Steel Will "
                "(You have advantage on saving throws against being frightened.)"
            ),
        ),
        SubclassFeature(
            name="Multiattack",
            level=11,
            description=(
                "At 11th level, you gain one of the following features of your choice: "
                "Volley (You can use your action to make a ranged attack against any "
                "number of creatures within 10 feet of a point you can see within your "
                "weapon's range. You must have ammunition for each target and make a "
                "separate attack roll for each target.), or Whirlwind Attack (You can "
                "use your action to make a melee attack against any number of creatures "
                "within 5 feet of you, with a separate attack roll for each target.)"
            ),
        ),
        SubclassFeature(
            name="Superior Hunter's Defense",
            level=15,
            description=(
                "At 15th level, you gain one of the following features of your choice: "
                "Evasion (When you are subjected to an effect that allows you to make "
                "a Dexterity saving throw to take only half damage, you instead take "
                "no damage if you succeed on the saving throw, and only half damage if "
                "you fail.), Stand Against the Tide (When a hostile creature misses "
                "you with a melee attack, you can use your reaction to force that "
                "creature to repeat the same attack against another creature of your "
                "choice.), or Uncanny Dodge (When an attacker that you can see hits "
                "you with an attack, you can use your reaction to halve the attack's "
                "damage against you.)"
            ),
        ),
    ],
)

# =============================================================================
# ROGUE - THIEF
# =============================================================================

THIEF = Subclass(
    name="Thief",
    parent_class="Rogue",
    description=(
        "You hone your skills in the larcenous arts. Burglars, bandits, "
        "cutpurses, and other criminals typically follow this archetype, but so "
        "do rogues who prefer to think of themselves as professional treasure "
        "seekers, explorers, delvers, and investigators. In addition to improving "
        "your agility and stealth, you learn skills useful for delving into "
        "ancient ruins, reading unfamiliar languages, and using magic items."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Fast Hands",
            level=3,
            description=(
                "Starting at 3rd level, you can use the bonus action granted by your "
                "Cunning Action to make a Dexterity (Sleight of Hand) check, use your "
                "thieves' tools to disarm a trap or open a lock, or take the Use an "
                "Object action."
            ),
        ),
        SubclassFeature(
            name="Second-Story Work",
            level=3,
            description=(
                "When you choose this archetype at 3rd level, you gain the ability to "
                "climb faster than normal; climbing no longer costs you extra movement. "
                "In addition, when you make a running jump, the distance you cover "
                "increases by a number of feet equal to your Dexterity modifier."
            ),
        ),
        SubclassFeature(
            name="Supreme Sneak",
            level=9,
            description=(
                "Starting at 9th level, you have advantage on a Dexterity (Stealth) "
                "check if you move no more than half your speed on the same turn."
            ),
        ),
        SubclassFeature(
            name="Use Magic Device",
            level=13,
            description=(
                "By 13th level, you have learned enough about the workings of magic "
                "that you can improvise the use of items even when they are not "
                "intended for you. You ignore all class, race, and level requirements "
                "on the use of magic items."
            ),
        ),
        SubclassFeature(
            name="Thief's Reflexes",
            level=17,
            description=(
                "When you reach 17th level, you have become adept at laying ambushes "
                "and quickly escaping danger. You can take two turns during the first "
                "round of any combat. You take your first turn at your normal "
                "initiative and your second turn at your initiative minus 10. You "
                "can't use this feature when you are surprised."
            ),
        ),
    ],
)

# =============================================================================
# SORCERER - DRACONIC BLOODLINE
# =============================================================================

DRACONIC_BLOODLINE = Subclass(
    name="Draconic Bloodline",
    parent_class="Sorcerer",
    description=(
        "Your innate magic comes from draconic magic that was mingled with your "
        "blood or that of your ancestors. Most often, sorcerers with this origin "
        "trace their descent back to a mighty sorcerer of ancient times who made "
        "a bargain with a dragon or who might even have claimed a dragon parent. "
        "Some of these bloodlines are well established in the world, but most are "
        "obscure. Any given sorcerer could be the first of a new bloodline."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Dragon Ancestor",
            level=1,
            description=(
                "At 1st level, you choose one type of dragon as your ancestor. The "
                "damage type associated with each dragon is used by features you gain "
                "later. Black (Acid), Blue (Lightning), Brass (Fire), Bronze "
                "(Lightning), Copper (Acid), Gold (Fire), Green (Poison), Red (Fire), "
                "Silver (Cold), White (Cold). You can speak, read, and write Draconic. "
                "Additionally, whenever you make a Charisma check when interacting "
                "with dragons, your proficiency bonus is doubled if it applies."
            ),
        ),
        SubclassFeature(
            name="Draconic Resilience",
            level=1,
            description=(
                "As magic flows through your body, it causes physical traits of your "
                "dragon ancestors to emerge. At 1st level, your hit point maximum "
                "increases by 1 and increases by 1 again whenever you gain a level in "
                "this class. Additionally, parts of your skin are covered by a thin "
                "sheen of dragon-like scales. When you aren't wearing armor, your AC "
                "equals 13 + your Dexterity modifier."
            ),
        ),
        SubclassFeature(
            name="Elemental Affinity",
            level=6,
            description=(
                "Starting at 6th level, when you cast a spell that deals damage of the "
                "type associated with your draconic ancestry, you can add your Charisma "
                "modifier to one damage roll of that spell. At the same time, you can "
                "spend 1 sorcery point to gain resistance to that damage type for 1 "
                "hour."
            ),
        ),
        SubclassFeature(
            name="Dragon Wings",
            level=14,
            description=(
                "At 14th level, you gain the ability to sprout a pair of dragon wings "
                "from your back, gaining a flying speed equal to your current speed. "
                "You can create these wings as a bonus action on your turn. They last "
                "until you dismiss them as a bonus action on your turn. You can't "
                "manifest your wings while wearing armor unless the armor is made to "
                "accommodate them, and clothing not made to accommodate your wings "
                "might be destroyed when you manifest them."
            ),
        ),
        SubclassFeature(
            name="Draconic Presence",
            level=18,
            description=(
                "Beginning at 18th level, you can channel the dread presence of your "
                "dragon ancestor, causing those around you to become awestruck or "
                "frightened. As an action, you can spend 5 sorcery points to draw on "
                "this power and exude an aura of awe or fear (your choice) to a "
                "distance of 60 feet. For 1 minute or until you lose your "
                "concentration, each hostile creature that starts its turn in this "
                "aura must succeed on a Wisdom saving throw or be charmed (if you "
                "chose awe) or frightened (if you chose fear) until the aura ends."
            ),
        ),
    ],
)

# =============================================================================
# WARLOCK - THE FIEND
# =============================================================================

THE_FIEND = Subclass(
    name="The Fiend",
    parent_class="Warlock",
    description=(
        "You have made a pact with a fiend from the lower planes of existence, a "
        "being whose aims are evil, even if you strive against those aims. Such "
        "beings desire the corruption or destruction of all things, ultimately "
        "including you. Fiends powerful enough to forge a pact include demon lords "
        "such as Demogorgon and Orcus; archdevils such as Asmodeus and Dispater; "
        "pit fiends and balors that are especially mighty; and ultroloths and "
        "other lords of the yugoloths."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Dark One's Blessing",
            level=1,
            description=(
                "Starting at 1st level, when you reduce a hostile creature to 0 hit "
                "points, you gain temporary hit points equal to your Charisma modifier "
                "+ your warlock level (minimum of 1)."
            ),
        ),
        SubclassFeature(
            name="Dark One's Own Luck",
            level=6,
            description=(
                "Starting at 6th level, you can call on your patron to alter fate in "
                "your favor. When you make an ability check or a saving throw, you can "
                "use this feature to add a d10 to your roll. You can do so after "
                "seeing the initial roll but before any of the roll's effects occur. "
                "Once you use this feature, you can't use it again until you finish a "
                "short or long rest."
            ),
        ),
        SubclassFeature(
            name="Fiendish Resilience",
            level=10,
            description=(
                "Starting at 10th level, you can choose one damage type when you "
                "finish a short or long rest. You gain resistance to that damage type "
                "until you choose a different one with this feature. Damage from "
                "magical weapons or silver weapons ignores this resistance."
            ),
        ),
        SubclassFeature(
            name="Hurl Through Hell",
            level=14,
            description=(
                "Starting at 14th level, when you hit a creature with an attack, you "
                "can use this feature to instantly transport the target through the "
                "lower planes. The creature disappears and hurtles through a nightmare "
                "landscape. At the end of your next turn, the target returns to the "
                "space it previously occupied, or the nearest unoccupied space. If "
                "the target is not a fiend, it takes 10d10 psychic damage as it reels "
                "from its horrific experience. Once you use this feature, you can't "
                "use it again until you finish a long rest."
            ),
        ),
    ],
    subclass_spells=[
        (1, ["Burning Hands", "Command"]),
        (3, ["Blindness/Deafness", "Scorching Ray"]),
        (5, ["Fireball", "Stinking Cloud"]),
        (7, ["Fire Shield", "Wall of Fire"]),
        (9, ["Flame Strike", "Hallow"]),
    ],
)

# =============================================================================
# WIZARD - SCHOOL OF EVOCATION
# =============================================================================

SCHOOL_OF_EVOCATION = Subclass(
    name="School of Evocation",
    parent_class="Wizard",
    description=(
        "You focus your study on magic that creates powerful elemental effects "
        "such as bitter cold, searing flame, rolling thunder, crackling lightning, "
        "and burning acid. Some evokers find employment in military forces, serving "
        "as artillery to blast enemy armies from afar. Others use their spectacular "
        "power to protect the weak, while some seek their own gain as bandits, "
        "adventurers, or aspiring tyrants."
    ),
    ruleset="dnd2014",
    features=[
        SubclassFeature(
            name="Evocation Savant",
            level=2,
            description=(
                "Beginning when you select this school at 2nd level, the gold and "
                "time you must spend to copy an evocation spell into your spellbook "
                "is halved."
            ),
        ),
        SubclassFeature(
            name="Sculpt Spells",
            level=2,
            description=(
                "Beginning at 2nd level, you can create pockets of relative safety "
                "within the effects of your evocation spells. When you cast an "
                "evocation spell that affects other creatures that you can see, you "
                "can choose a number of them equal to 1 + the spell's level. The "
                "chosen creatures automatically succeed on their saving throws against "
                "the spell, and they take no damage if they would normally take half "
                "damage on a successful save."
            ),
        ),
        SubclassFeature(
            name="Potent Cantrip",
            level=6,
            description=(
                "Starting at 6th level, your damaging cantrips affect even creatures "
                "that avoid the brunt of the effect. When a creature succeeds on a "
                "saving throw against your cantrip, the creature takes half the "
                "cantrip's damage (if any) but suffers no additional effect from the "
                "cantrip."
            ),
        ),
        SubclassFeature(
            name="Empowered Evocation",
            level=10,
            description=(
                "Beginning at 10th level, you can add your Intelligence modifier to "
                "one damage roll of any wizard evocation spell you cast."
            ),
        ),
        SubclassFeature(
            name="Overchannel",
            level=14,
            description=(
                "Starting at 14th level, you can increase the power of your simpler "
                "spells. When you cast a wizard spell of 1st through 5th level that "
                "deals damage, you can deal maximum damage with that spell. The first "
                "time you do so, you suffer no adverse effect. If you use this feature "
                "again before you finish a long rest, you take 2d12 necrotic damage "
                "for each level of the spell, immediately after you cast it. Each time "
                "you use this feature again before finishing a long rest, the necrotic "
                "damage per spell level increases by 1d12."
            ),
        ),
    ],
)


# =============================================================================
# BARBARIAN - PATH OF THE TOTEM WARRIOR
# =============================================================================

TOTEM_WARRIOR = Subclass(
    name="Path of the Totem Warrior",
    parent_class="Barbarian",
    description=(
        "The Path of the Totem Warrior is a spiritual journey, as the barbarian "
        "accepts a spirit animal as guide, protector, and inspiration. In battle, "
        "your totem spirit fills you with supernatural might, adding magical fuel "
        "to your barbarian rage."
    ),
    features=[
        SubclassFeature(
            name="Spirit Seeker",
            level=3,
            description=(
                "Yours is a path that seeks attunement with the natural world, "
                "giving you a kinship with beasts. At 3rd level, you gain the ability "
                "to cast Beast Sense and Speak with Animals as rituals."
            ),
        ),
        SubclassFeature(
            name="Totem Spirit",
            level=3,
            description=(
                "At 3rd level, when you adopt this path, you choose a totem spirit "
                "and gain its feature. Bear: While raging, you have resistance to all "
                "damage except psychic. Eagle: While raging, other creatures have "
                "disadvantage on opportunity attacks against you, and you can Dash as "
                "a bonus action. Wolf: While raging, your friends have advantage on "
                "melee attack rolls against any creature within 5 feet of you."
            ),
        ),
        SubclassFeature(
            name="Aspect of the Beast",
            level=6,
            description=(
                "At 6th level, you gain a magical benefit based on your totem animal. "
                "Bear: Your carrying capacity doubles and you have advantage on "
                "Strength checks to push, pull, lift, or break objects. Eagle: You "
                "can see up to 1 mile away with no difficulty and discern fine details "
                "as if looking at something no more than 100 feet away. Wolf: You can "
                "track creatures at a fast pace and move stealthily at a normal pace."
            ),
        ),
        SubclassFeature(
            name="Spirit Walker",
            level=10,
            description=(
                "At 10th level, you can cast Commune with Nature as a ritual. When you "
                "do so, a spiritual version of one of your totem animals appears to "
                "convey the information you seek."
            ),
        ),
        SubclassFeature(
            name="Totemic Attunement",
            level=14,
            description=(
                "At 14th level, you gain a magical benefit based on your totem animal. "
                "Bear: While raging, any creature within 5 feet that is hostile to you "
                "has disadvantage on attack rolls against targets other than you. "
                "Eagle: While raging, you have a flying speed equal to your walking "
                "speed. Wolf: While raging, when you hit a Large or smaller creature, "
                "you can use a bonus action to knock it prone."
            ),
        ),
    ],
)

# =============================================================================
# BARBARIAN - PATH OF WILD MAGIC
# =============================================================================

WILD_MAGIC_BARBARIAN = Subclass(
    name="Path of Wild Magic",
    parent_class="Barbarian",
    description=(
        "Many places in the multiverse abound with beauty, intense emotion, and "
        "rampant magic; the Feywild, the Upper Planes, and other realms of "
        "supernatural power radiate with such forces and can profoundly influence "
        "people. As folk of deep feeling, barbarians are especially susceptible "
        "to these wild influences."
    ),
    features=[
        SubclassFeature(
            name="Magic Awareness",
            level=3,
            description=(
                "As an action, you can open your awareness to the presence of "
                "concentrated magic. Until the end of your next turn, you know the "
                "location of any spell or magic item within 60 feet of you that isn't "
                "behind total cover. You can use this feature a number of times equal "
                "to your proficiency bonus, regaining all uses on a long rest."
            ),
        ),
        SubclassFeature(
            name="Wild Surge",
            level=3,
            description=(
                "Starting at 3rd level, when you enter your rage, roll on the Wild "
                "Magic table to determine the magical effect produced. If the effect "
                "requires a saving throw, the DC equals 8 + your proficiency bonus + "
                "your Constitution modifier."
            ),
        ),
        SubclassFeature(
            name="Bolstering Magic",
            level=6,
            description=(
                "At 6th level, you can harness wild magic to bolster yourself or a "
                "companion. As an action, touch a creature and roll a d3. The creature "
                "gains a bonus to attack rolls and ability checks equal to the number "
                "rolled for 10 minutes, OR the creature regains one expended spell "
                "slot of a level equal to the number rolled. You can use this feature "
                "a number of times equal to your proficiency bonus."
            ),
        ),
        SubclassFeature(
            name="Unstable Backlash",
            level=10,
            description=(
                "At 10th level, when you are imperiled during your rage, the magic "
                "within you can lash out. Immediately after you take damage or fail "
                "a saving throw while raging, you can use your reaction to roll on "
                "the Wild Magic table and immediately produce the effect rolled. This "
                "replaces your current Wild Magic effect."
            ),
        ),
        SubclassFeature(
            name="Controlled Surge",
            level=14,
            description=(
                "At 14th level, when you roll on the Wild Magic table, you can roll "
                "the die twice and choose which of the two effects to unleash. If you "
                "roll the same number on both dice, you can ignore the number and "
                "choose any effect on the table."
            ),
        ),
    ],
)

# =============================================================================
# BARD - COLLEGE OF VALOR
# =============================================================================

COLLEGE_OF_VALOR = Subclass(
    name="College of Valor",
    parent_class="Bard",
    description=(
        "Bards of the College of Valor are daring skalds whose tales keep alive "
        "the memory of the great heroes of the past, and thereby inspire a new "
        "generation of heroes. These bards gather in mead halls or around great "
        "bonfires to sing the deeds of the mighty, both past and present."
    ),
    features=[
        SubclassFeature(
            name="Bonus Proficiencies",
            level=3,
            description=(
                "When you join the College of Valor at 3rd level, you gain proficiency "
                "with medium armor, shields, and martial weapons."
            ),
        ),
        SubclassFeature(
            name="Combat Inspiration",
            level=3,
            description=(
                "Also at 3rd level, a creature that has a Bardic Inspiration die from "
                "you can roll that die and add the number rolled to a weapon damage "
                "roll it just made. Alternatively, when an attack roll is made against "
                "the creature, it can use its reaction to roll the Bardic Inspiration "
                "die and add the number rolled to its AC against that attack."
            ),
        ),
        SubclassFeature(
            name="Extra Attack",
            level=6,
            description=(
                "Starting at 6th level, you can attack twice, instead of once, "
                "whenever you take the Attack action on your turn."
            ),
        ),
        SubclassFeature(
            name="Battle Magic",
            level=14,
            description=(
                "At 14th level, when you use your action to cast a bard spell, you "
                "can make one weapon attack as a bonus action."
            ),
        ),
    ],
)

# =============================================================================
# BARD - COLLEGE OF SWORDS
# =============================================================================

COLLEGE_OF_SWORDS = Subclass(
    name="College of Swords",
    parent_class="Bard",
    description=(
        "Bards of the College of Swords are called blades, and they entertain "
        "through daring feats of weapon prowess. Blades perform stunts such as "
        "sword swallowing, knife throwing and juggling, and mock combats. Though "
        "they use their weapons to entertain, they are also highly trained and "
        "skilled warriors in their own right."
    ),
    features=[
        SubclassFeature(
            name="Bonus Proficiencies",
            level=3,
            description=(
                "When you join the College of Swords at 3rd level, you gain "
                "proficiency with medium armor and the scimitar. If you're proficient "
                "with a simple or martial melee weapon, you can use it as a "
                "spellcasting focus for your bard spells."
            ),
        ),
        SubclassFeature(
            name="Fighting Style",
            level=3,
            description=(
                "At 3rd level, you adopt a style of fighting as your specialty. "
                "Choose one: Dueling (When you are wielding a melee weapon in one "
                "hand and no other weapons, you gain a +2 bonus to damage rolls.) or "
                "Two-Weapon Fighting (When you engage in two-weapon fighting, you can "
                "add your ability modifier to the damage of the second attack.)"
            ),
        ),
        SubclassFeature(
            name="Blade Flourish",
            level=3,
            description=(
                "At 3rd level, whenever you take the Attack action on your turn, your "
                "walking speed increases by 10 feet until the end of the turn. If a "
                "weapon attack you make as part of this action hits, you can expend "
                "one Bardic Inspiration die and choose: Defensive Flourish (add the "
                "die to damage and AC until your next turn), Slashing Flourish (add "
                "the die to damage and deal the same damage to another creature "
                "within 5 feet), or Mobile Flourish (add the die to damage and push "
                "the target 5 + the die roll feet away)."
            ),
        ),
        SubclassFeature(
            name="Extra Attack",
            level=6,
            description=(
                "Starting at 6th level, you can attack twice, instead of once, "
                "whenever you take the Attack action on your turn."
            ),
        ),
        SubclassFeature(
            name="Master's Flourish",
            level=14,
            description=(
                "Starting at 14th level, whenever you use a Blade Flourish option, "
                "you can roll a d6 and use it instead of expending a Bardic "
                "Inspiration die."
            ),
        ),
    ],
)

# =============================================================================
# CLERIC - LIGHT DOMAIN
# =============================================================================

LIGHT_DOMAIN = Subclass(
    name="Light Domain",
    parent_class="Cleric",
    description=(
        "Gods of light promote the ideals of rebirth and renewal, truth, "
        "vigilance, and beauty, often using the symbol of the sun. Some of these "
        "gods are portrayed as the sun itself or as a charioteer who guides the "
        "sun across the sky. Others are tireless sentinels whose eyes pierce "
        "every shadow and see through every deception."
    ),
    features=[
        SubclassFeature(
            name="Bonus Cantrip",
            level=1,
            description=(
                "When you choose this domain at 1st level, you gain the Light "
                "cantrip if you don't already know it."
            ),
        ),
        SubclassFeature(
            name="Warding Flare",
            level=1,
            description=(
                "Also at 1st level, you can interpose divine light between yourself "
                "and an attacking enemy. When you are attacked by a creature within "
                "30 feet that you can see, you can use your reaction to impose "
                "disadvantage on the attack roll. You can use this feature a number "
                "of times equal to your Wisdom modifier (minimum once), and you "
                "regain all expended uses when you finish a long rest."
            ),
        ),
        SubclassFeature(
            name="Channel Divinity: Radiance of the Dawn",
            level=2,
            description=(
                "Starting at 2nd level, you can use your Channel Divinity to harness "
                "sunlight, banishing darkness and dealing radiant damage to your foes. "
                "As an action, any magical darkness within 30 feet is dispelled. Each "
                "hostile creature within 30 feet must make a Constitution saving throw, "
                "taking 2d10 + your cleric level radiant damage on a failed save, or "
                "half as much on a success."
            ),
        ),
        SubclassFeature(
            name="Improved Flare",
            level=6,
            description=(
                "Starting at 6th level, you can also use your Warding Flare feature "
                "when a creature that you can see within 30 feet of you attacks a "
                "creature other than you."
            ),
        ),
        SubclassFeature(
            name="Potent Spellcasting",
            level=8,
            description=(
                "Starting at 8th level, you add your Wisdom modifier to the damage "
                "you deal with any cleric cantrip."
            ),
        ),
        SubclassFeature(
            name="Corona of Light",
            level=17,
            description=(
                "Starting at 17th level, you can use your action to activate an aura "
                "of sunlight that lasts for 1 minute or until you dismiss it. You "
                "emit bright light in a 60-foot radius and dim light 30 feet beyond "
                "that. Your enemies in the bright light have disadvantage on saving "
                "throws against any spell that deals fire or radiant damage."
            ),
        ),
    ],
    subclass_spells=[
        (1, ["Burning Hands", "Faerie Fire"]),
        (3, ["Flaming Sphere", "Scorching Ray"]),
        (5, ["Daylight", "Fireball"]),
        (7, ["Guardian of Faith", "Wall of Fire"]),
        (9, ["Flame Strike", "Scrying"]),
    ],
)

# =============================================================================
# CLERIC - WAR DOMAIN
# =============================================================================

WAR_DOMAIN = Subclass(
    name="War Domain",
    parent_class="Cleric",
    description=(
        "War has many manifestations. It can make heroes of ordinary people. It "
        "can be desperate and horrific, with acts of cruelty and cowardice "
        "eclipsing instances of excellence and courage. Clerics who serve deities "
        "of war encourage such conflicts and are blessed with awesome power."
    ),
    features=[
        SubclassFeature(
            name="Bonus Proficiencies",
            level=1,
            description=(
                "At 1st level, you gain proficiency with martial weapons and heavy "
                "armor."
            ),
        ),
        SubclassFeature(
            name="War Priest",
            level=1,
            description=(
                "From 1st level, your god delivers bolts of inspiration in battle. "
                "When you use the Attack action, you can make one weapon attack as a "
                "bonus action. You can use this feature a number of times equal to "
                "your Wisdom modifier (minimum once), and you regain all expended "
                "uses when you finish a long rest."
            ),
        ),
        SubclassFeature(
            name="Channel Divinity: Guided Strike",
            level=2,
            description=(
                "Starting at 2nd level, you can use your Channel Divinity to strike "
                "with supernatural accuracy. When you make an attack roll, you can "
                "use your Channel Divinity to gain a +10 bonus to the roll. You make "
                "this choice after you see the roll, but before the DM says whether "
                "the attack hits or misses."
            ),
        ),
        SubclassFeature(
            name="Channel Divinity: War God's Blessing",
            level=6,
            description=(
                "At 6th level, when a creature within 30 feet of you makes an attack "
                "roll, you can use your reaction to grant that creature a +10 bonus "
                "to the roll, using your Channel Divinity. You make this choice after "
                "you see the roll, but before the DM says whether the attack hits."
            ),
        ),
        SubclassFeature(
            name="Divine Strike",
            level=8,
            description=(
                "At 8th level, you gain the ability to infuse your weapon strikes "
                "with divine energy. Once on each of your turns when you hit a "
                "creature with a weapon attack, you can cause the attack to deal an "
                "extra 1d8 damage of the same type dealt by the weapon. When you "
                "reach 14th level, the extra damage increases to 2d8."
            ),
        ),
        SubclassFeature(
            name="Avatar of Battle",
            level=17,
            description=(
                "At 17th level, you gain resistance to bludgeoning, piercing, and "
                "slashing damage from nonmagical attacks."
            ),
        ),
    ],
    subclass_spells=[
        (1, ["Divine Favor", "Shield of Faith"]),
        (3, ["Magic Weapon", "Spiritual Weapon"]),
        (5, ["Crusader's Mantle", "Spirit Guardians"]),
        (7, ["Freedom of Movement", "Stoneskin"]),
        (9, ["Flame Strike", "Hold Monster"]),
    ],
)

# =============================================================================
# DRUID - CIRCLE OF THE MOON
# =============================================================================

CIRCLE_OF_THE_MOON = Subclass(
    name="Circle of the Moon",
    parent_class="Druid",
    description=(
        "Druids of the Circle of the Moon are fierce guardians of the wilds. "
        "Their order gathers under the full moon to share news and trade warnings. "
        "They haunt the deepest parts of the wilderness, where they might go for "
        "weeks on end before crossing paths with another humanoid creature."
    ),
    features=[
        SubclassFeature(
            name="Combat Wild Shape",
            level=2,
            description=(
                "When you choose this circle at 2nd level, you gain the ability to "
                "use Wild Shape on your turn as a bonus action, rather than as an "
                "action. Additionally, while you are transformed by Wild Shape, you "
                "can use a bonus action to expend one spell slot to regain 1d8 hit "
                "points per level of the spell slot expended."
            ),
        ),
        SubclassFeature(
            name="Circle Forms",
            level=2,
            description=(
                "At 2nd level, you can use your Wild Shape to transform into a beast "
                "with a CR as high as 1 (you ignore the Max. CR column of the Beast "
                "Shapes table). Starting at 6th level, you can transform into a beast "
                "with a CR as high as your druid level divided by 3, rounded down."
            ),
        ),
        SubclassFeature(
            name="Primal Strike",
            level=6,
            description=(
                "Starting at 6th level, your attacks in beast form count as magical "
                "for the purpose of overcoming resistance and immunity to nonmagical "
                "attacks and damage."
            ),
        ),
        SubclassFeature(
            name="Elemental Wild Shape",
            level=10,
            description=(
                "At 10th level, you can expend two uses of Wild Shape at the same "
                "time to transform into an air elemental, an earth elemental, a fire "
                "elemental, or a water elemental."
            ),
        ),
        SubclassFeature(
            name="Thousand Forms",
            level=14,
            description=(
                "By 14th level, you have learned to use magic to alter your physical "
                "form in more subtle ways. You can cast Alter Self at will."
            ),
        ),
    ],
)

# =============================================================================
# DRUID - CIRCLE OF SPORES
# =============================================================================

CIRCLE_OF_SPORES = Subclass(
    name="Circle of Spores",
    parent_class="Druid",
    description=(
        "Druids of the Circle of Spores find beauty in decay. They see within "
        "mold and other fungi the ability to transform lifeless material into "
        "abundant, albeit somewhat strange, life. These druids believe that life "
        "and death are parts of a grand cycle, with one leading to the other and "
        "then back again."
    ),
    features=[
        SubclassFeature(
            name="Circle Spells",
            level=2,
            description=(
                "At 2nd level, you learn the Chill Touch cantrip. At 3rd, 5th, 7th, "
                "and 9th level, you gain access to the spells listed in the Circle "
                "of Spores Spells table. These spells are always prepared and don't "
                "count against your prepared spells."
            ),
        ),
        SubclassFeature(
            name="Halo of Spores",
            level=2,
            description=(
                "Starting at 2nd level, you are surrounded by invisible necrotic "
                "spores. When a creature you can see moves into a space within 10 "
                "feet of you or starts its turn there, you can use your reaction to "
                "deal 1d4 necrotic damage to that creature (Constitution save negates). "
                "The damage increases to 1d6 at 6th level, 1d8 at 10th, and 1d10 at 14th."
            ),
        ),
        SubclassFeature(
            name="Symbiotic Entity",
            level=2,
            description=(
                "At 2nd level, you can use Wild Shape to awaken your spores. As an "
                "action, you gain 4 temporary hit points per druid level, your Halo "
                "of Spores damage doubles, and your melee weapon attacks deal an "
                "extra 1d6 necrotic damage. These benefits last for 10 minutes, "
                "until you lose all temporary hit points, or until you use Wild Shape."
            ),
        ),
        SubclassFeature(
            name="Fungal Infestation",
            level=6,
            description=(
                "At 6th level, if a beast or humanoid that is Small or Medium dies "
                "within 10 feet of you, you can use your reaction to animate it. It "
                "rises as a zombie with 1 hit point. The zombie remains animate for "
                "1 hour, after which it collapses. You can use this feature a number "
                "of times equal to your Wisdom modifier."
            ),
        ),
        SubclassFeature(
            name="Spreading Spores",
            level=10,
            description=(
                "At 10th level, you gain the ability to seed an area with deadly "
                "spores. As a bonus action while your Symbiotic Entity feature is "
                "active, you can hurl spores up to 30 feet away to create a 10-foot "
                "cube. Any creature moving into or starting its turn in that cube "
                "must save against your Halo of Spores."
            ),
        ),
        SubclassFeature(
            name="Fungal Body",
            level=14,
            description=(
                "At 14th level, the fungal spores in your body alter you: you can't "
                "be blinded, deafened, frightened, or poisoned, and any critical hit "
                "against you counts as a normal hit instead, unless you're incapacitated."
            ),
        ),
    ],
    subclass_spells=[
        (3, ["Blindness/Deafness", "Gentle Repose"]),
        (5, ["Animate Dead", "Gaseous Form"]),
        (7, ["Blight", "Confusion"]),
        (9, ["Cloudkill", "Contagion"]),
    ],
)

# =============================================================================
# FIGHTER - BATTLE MASTER
# =============================================================================

BATTLE_MASTER = Subclass(
    name="Battle Master",
    parent_class="Fighter",
    description=(
        "Those who emulate the archetypal Battle Master employ martial techniques "
        "passed down through generations. To a Battle Master, combat is an "
        "academic field, sometimes including subjects beyond battle such as "
        "weaponsmithing and calligraphy. Not every fighter absorbs the lessons of "
        "history, theory, and artistry that are reflected in the Battle Master "
        "archetype, but those who do are well-rounded fighters of great skill."
    ),
    features=[
        SubclassFeature(
            name="Combat Superiority",
            level=3,
            description=(
                "At 3rd level, you learn three maneuvers of your choice. You have "
                "four superiority dice, which are d8s. A superiority die is expended "
                "when you use it. You regain all expended dice on a short or long "
                "rest. You gain another die at 7th and 15th level. Your dice become "
                "d10s at 10th level and d12s at 18th level."
            ),
        ),
        SubclassFeature(
            name="Student of War",
            level=3,
            description=(
                "At 3rd level, you gain proficiency with one type of artisan's tools "
                "of your choice."
            ),
        ),
        SubclassFeature(
            name="Know Your Enemy",
            level=7,
            description=(
                "Starting at 7th level, if you spend at least 1 minute observing or "
                "interacting with another creature outside combat, you can learn "
                "certain information about its capabilities compared to your own. "
                "The DM tells you if the creature is your equal, superior, or "
                "inferior in two of the following: Strength, Dexterity, Constitution, "
                "AC, Current HP, Total class levels, or Fighter levels."
            ),
        ),
        SubclassFeature(
            name="Improved Combat Superiority",
            level=10,
            description=(
                "At 10th level, your superiority dice turn into d10s. At 18th level, "
                "they turn into d12s."
            ),
        ),
        SubclassFeature(
            name="Relentless",
            level=15,
            description=(
                "Starting at 15th level, when you roll initiative and have no "
                "superiority dice remaining, you regain one superiority die."
            ),
        ),
    ],
)

# =============================================================================
# FIGHTER - ELDRITCH KNIGHT
# =============================================================================

ELDRITCH_KNIGHT = Subclass(
    name="Eldritch Knight",
    parent_class="Fighter",
    description=(
        "The archetypal Eldritch Knight combines the martial mastery common to all "
        "fighters with a careful study of magic. Eldritch Knights use magical "
        "techniques similar to those practiced by wizards. They focus their study "
        "on two of the eight schools of magic: abjuration and evocation."
    ),
    features=[
        SubclassFeature(
            name="Spellcasting",
            level=3,
            description=(
                "At 3rd level, you augment your martial prowess with the ability to "
                "cast spells. You know three cantrips of your choice from the wizard "
                "spell list. You know three 1st-level wizard spells, two of which "
                "must be from abjuration or evocation. Intelligence is your "
                "spellcasting ability."
            ),
        ),
        SubclassFeature(
            name="Weapon Bond",
            level=3,
            description=(
                "At 3rd level, you learn a ritual that creates a magical bond with "
                "one weapon. Once bonded, you can't be disarmed of that weapon "
                "unless you are incapacitated. If it is on the same plane of "
                "existence, you can summon that weapon as a bonus action. You can "
                "have up to two bonded weapons."
            ),
        ),
        SubclassFeature(
            name="War Magic",
            level=7,
            description=(
                "Beginning at 7th level, when you use your action to cast a cantrip, "
                "you can make one weapon attack as a bonus action."
            ),
        ),
        SubclassFeature(
            name="Eldritch Strike",
            level=10,
            description=(
                "At 10th level, when you hit a creature with a weapon attack, that "
                "creature has disadvantage on the next saving throw it makes against "
                "a spell you cast before the end of your next turn."
            ),
        ),
        SubclassFeature(
            name="Arcane Charge",
            level=15,
            description=(
                "At 15th level, when you use Action Surge, you can teleport up to "
                "30 feet to an unoccupied space you can see. You can teleport before "
                "or after the additional action."
            ),
        ),
        SubclassFeature(
            name="Improved War Magic",
            level=18,
            description=(
                "Starting at 18th level, when you use your action to cast a spell, "
                "you can make one weapon attack as a bonus action."
            ),
        ),
    ],
)

# =============================================================================
# MONK - WAY OF SHADOW
# =============================================================================

WAY_OF_SHADOW = Subclass(
    name="Way of Shadow",
    parent_class="Monk",
    description=(
        "Monks of the Way of Shadow follow a tradition that values stealth and "
        "subterfuge. These monks might be called ninjas or shadowdancers, and "
        "they serve as spies and assassins. Sometimes the members of a ninja "
        "monastery are family members, forming a clan sworn to secrecy about "
        "their arts and missions."
    ),
    features=[
        SubclassFeature(
            name="Shadow Arts",
            level=3,
            description=(
                "Starting when you choose this tradition at 3rd level, you can use "
                "your ki to duplicate the effects of certain spells. As an action, "
                "you can spend 2 ki points to cast Darkness, Darkvision, Pass without "
                "Trace, or Silence, without providing material components. You also "
                "gain the Minor Illusion cantrip if you don't already know it."
            ),
        ),
        SubclassFeature(
            name="Shadow Step",
            level=6,
            description=(
                "At 6th level, you gain the ability to step from one shadow into "
                "another. When you are in dim light or darkness, as a bonus action "
                "you can teleport up to 60 feet to an unoccupied space you can see "
                "that is also in dim light or darkness. You then have advantage on "
                "the first melee attack you make before the end of the turn."
            ),
        ),
        SubclassFeature(
            name="Cloak of Shadows",
            level=11,
            description=(
                "By 11th level, you have learned to become one with the shadows. "
                "When you are in an area of dim light or darkness, you can use your "
                "action to become invisible. You remain invisible until you make an "
                "attack, cast a spell, or are in an area of bright light."
            ),
        ),
        SubclassFeature(
            name="Opportunist",
            level=17,
            description=(
                "At 17th level, you can exploit a creature's momentary distraction "
                "when it is hit by an attack. Whenever a creature within 5 feet of "
                "you is hit by an attack made by a creature other than you, you can "
                "use your reaction to make a melee attack against that creature."
            ),
        ),
    ],
)

# =============================================================================
# MONK - WAY OF THE FOUR ELEMENTS
# =============================================================================

WAY_OF_FOUR_ELEMENTS = Subclass(
    name="Way of the Four Elements",
    parent_class="Monk",
    description=(
        "You follow a monastic tradition that teaches you to harness the elements. "
        "When you focus your ki, you can align yourself with the forces of "
        "creation and bend the four elements to your will, using them as an "
        "extension of your body. Some members of this tradition dedicate "
        "themselves to a single element, while others weave the elements together."
    ),
    features=[
        SubclassFeature(
            name="Disciple of the Elements",
            level=3,
            description=(
                "You learn magical disciplines that harness the power of the four "
                "elements. You learn the Elemental Attunement discipline and one "
                "other elemental discipline of your choice. You learn one additional "
                "discipline at 6th, 11th, and 17th level. Casting elemental spells "
                "costs ki points equal to the spell's level + 1."
            ),
        ),
        SubclassFeature(
            name="Elemental Attunement",
            level=3,
            description=(
                "You can use your action to briefly control elemental forces within "
                "30 feet of you, causing one of these effects: create a harmless "
                "sensory effect related to air, earth, fire, or water; instantaneously "
                "light or snuff out a candle, torch, or small campfire; chill or warm "
                "up to 1 pound of nonliving material for up to 1 hour; or cause earth, "
                "fire, water, or mist to shape itself into a crude form you design."
            ),
        ),
        SubclassFeature(
            name="Additional Elemental Discipline",
            level=6,
            description=(
                "At 6th level, you learn one additional elemental discipline of your "
                "choice. Available disciplines include: Fist of Four Thunders (Burning "
                "Hands, 2 ki), Water Whip (bonus action, 10 feet, 3d10 damage, 2 ki), "
                "Sweeping Cinder Strike (Burning Hands, 2 ki), and others."
            ),
        ),
        SubclassFeature(
            name="Master of Elements",
            level=11,
            description=(
                "At 11th level, you learn one additional elemental discipline. You "
                "also gain access to more powerful disciplines including: Flames of "
                "the Phoenix (Fireball, 4 ki), Mist Stance (Gaseous Form, 4 ki), "
                "Ride the Wind (Fly, 4 ki), and others."
            ),
        ),
        SubclassFeature(
            name="Elemental Mastery",
            level=17,
            description=(
                "At 17th level, you learn one additional elemental discipline. You "
                "now have access to the most powerful disciplines including: Breath "
                "of Winter (Cone of Cold, 6 ki), River of Hungry Flame (Wall of Fire, "
                "5 ki), Wave of Rolling Earth (Wall of Stone, 6 ki)."
            ),
        ),
    ],
)

# =============================================================================
# PALADIN - OATH OF THE ANCIENTS
# =============================================================================

OATH_OF_THE_ANCIENTS = Subclass(
    name="Oath of the Ancients",
    parent_class="Paladin",
    description=(
        "The Oath of the Ancients is as old as the race of elves and the rituals "
        "of the druids. Sometimes called fey knights, green knights, or horned "
        "knights, paladins who swear this oath cast their lot with the side of "
        "the light in the cosmic struggle against darkness because they love the "
        "beautiful and life-giving things of the world."
    ),
    features=[
        SubclassFeature(
            name="Tenets of the Ancients",
            level=3,
            description=(
                "The tenets of the Oath of the Ancients have been preserved for "
                "uncounted centuries: Kindle the Light (Through acts of mercy, "
                "kindness, and forgiveness, kindle the light of hope in the world.), "
                "Shelter the Light (Where there is good, beauty, love, and laughter, "
                "stand against the wickedness that would swallow it.), Preserve Your "
                "Own Light (Delight in song and laughter, in beauty and art.), Be the "
                "Light (Be a glorious beacon for all who live in despair.)"
            ),
        ),
        SubclassFeature(
            name="Channel Divinity",
            level=3,
            description=(
                "When you take this oath at 3rd level, you gain two Channel Divinity "
                "options. Nature's Wrath: As an action, spectral vines restrain a "
                "creature within 10 feet (Strength or Dexterity save to escape). "
                "Turn the Faithless: Each fey or fiend within 30 feet that can hear "
                "you must make a Wisdom save or be turned for 1 minute."
            ),
        ),
        SubclassFeature(
            name="Aura of Warding",
            level=7,
            description=(
                "Beginning at 7th level, you and friendly creatures within 10 feet "
                "of you have resistance to damage from spells. At 18th level, the "
                "range of this aura increases to 30 feet."
            ),
        ),
        SubclassFeature(
            name="Undying Sentinel",
            level=15,
            description=(
                "Starting at 15th level, when you are reduced to 0 hit points and "
                "are not killed outright, you can choose to drop to 1 hit point "
                "instead. Once you use this ability, you can't use it again until "
                "you finish a long rest. Additionally, you suffer none of the "
                "drawbacks of old age, and you can't be aged magically."
            ),
        ),
        SubclassFeature(
            name="Elder Champion",
            level=20,
            description=(
                "At 20th level, you can assume the form of an ancient force of "
                "nature for 1 minute. Your appearance takes on an otherworldly "
                "quality. Once per turn, you can heal yourself for 10 hit points. "
                "Paladin spells you cast cost no spell slot if 4th level or lower. "
                "Enemies within 10 feet have disadvantage on saves against your "
                "paladin spells and Channel Divinity."
            ),
        ),
    ],
    subclass_spells=[
        (3, ["Ensnaring Strike", "Speak with Animals"]),
        (5, ["Misty Step", "Moonbeam"]),
        (9, ["Plant Growth", "Protection from Energy"]),
        (13, ["Ice Storm", "Stoneskin"]),
        (17, ["Commune with Nature", "Tree Stride"]),
    ],
)

# =============================================================================
# PALADIN - OATH OF VENGEANCE
# =============================================================================

OATH_OF_VENGEANCE = Subclass(
    name="Oath of Vengeance",
    parent_class="Paladin",
    description=(
        "The Oath of Vengeance is a solemn commitment to punish those who have "
        "committed a grievous sin. When evil forces slaughter helpless villagers, "
        "when an entire people turns against the will of the gods, when a thieves' "
        "guild grows too violent and powerful, when a dragon rampages through the "
        "countryside—at times like these, paladins arise and swear an Oath of "
        "Vengeance to set right that which has gone wrong."
    ),
    features=[
        SubclassFeature(
            name="Tenets of Vengeance",
            level=3,
            description=(
                "The tenets of the Oath of Vengeance vary by paladin, but all the "
                "tenets revolve around punishing wrongdoers by any means necessary: "
                "Fight the Greater Evil (Faced with a choice, choose the greater evil "
                "to fight.), No Mercy for the Wicked (Ordinary foes might win your "
                "mercy, but your sworn enemies do not.), By Any Means Necessary (Your "
                "qualms can't get in the way of exterminating your foes.), Restitution "
                "(Help those harmed by your sworn enemies.)"
            ),
        ),
        SubclassFeature(
            name="Channel Divinity",
            level=3,
            description=(
                "When you take this oath at 3rd level, you gain two Channel Divinity "
                "options. Abjure Enemy: As an action, one creature within 60 feet "
                "must make a Wisdom save or be frightened for 1 minute and have its "
                "speed reduced to 0. Vow of Enmity: As a bonus action, you gain "
                "advantage on attack rolls against a creature within 10 feet for 1 "
                "minute."
            ),
        ),
        SubclassFeature(
            name="Relentless Avenger",
            level=7,
            description=(
                "By 7th level, your supernatural focus helps you close off a foe's "
                "retreat. When you hit a creature with an opportunity attack, you "
                "can move up to half your speed immediately after the attack and as "
                "part of the same reaction. This movement doesn't provoke opportunity "
                "attacks."
            ),
        ),
        SubclassFeature(
            name="Soul of Vengeance",
            level=15,
            description=(
                "Starting at 15th level, the authority with which you speak your Vow "
                "of Enmity gives you greater power over your foe. When a creature "
                "under the effect of your Vow of Enmity makes an attack, you can use "
                "your reaction to make a melee weapon attack against that creature "
                "if it is within range."
            ),
        ),
        SubclassFeature(
            name="Avenging Angel",
            level=20,
            description=(
                "At 20th level, you can assume the form of an angelic avenger for 1 "
                "hour. You sprout wings that give you a flying speed of 60 feet. You "
                "emanate a menacing aura in a 30-foot radius. The first time any "
                "enemy creature enters the aura or starts its turn there, it must "
                "succeed on a Wisdom save or be frightened of you for 1 minute."
            ),
        ),
    ],
    subclass_spells=[
        (3, ["Bane", "Hunter's Mark"]),
        (5, ["Hold Person", "Misty Step"]),
        (9, ["Haste", "Protection from Energy"]),
        (13, ["Banishment", "Dimension Door"]),
        (17, ["Hold Monster", "Scrying"]),
    ],
)

# =============================================================================
# RANGER - BEAST MASTER
# =============================================================================

BEAST_MASTER = Subclass(
    name="Beast Master",
    parent_class="Ranger",
    description=(
        "The Beast Master archetype embodies a friendship between the civilized "
        "races and the beasts of the world. United in focus, beast and ranger "
        "work as one to fight the monstrous foes that threaten civilization and "
        "the wilderness alike. Emulating the Beast Master archetype means "
        "committing yourself to this ideal."
    ),
    features=[
        SubclassFeature(
            name="Ranger's Companion",
            level=3,
            description=(
                "At 3rd level, you gain a beast companion that accompanies you on "
                "your adventures. Choose a beast that is no larger than Medium and "
                "that has a challenge rating of 1/4 or lower. The beast obeys your "
                "commands as best it can. It takes its turn on your initiative but "
                "doesn't take an action unless you command it to. On your turn, you "
                "can verbally command the beast where to move (no action required). "
                "You can use your action to command it to Attack, Dash, Disengage, "
                "Dodge, or Help."
            ),
        ),
        SubclassFeature(
            name="Exceptional Training",
            level=7,
            description=(
                "Beginning at 7th level, on any of your turns when your beast "
                "companion doesn't attack, you can use a bonus action to command the "
                "beast to take the Dash, Disengage, Dodge, or Help action on its "
                "turn. In addition, the beast's attacks now count as magical for the "
                "purpose of overcoming resistance and immunity to nonmagical attacks."
            ),
        ),
        SubclassFeature(
            name="Bestial Fury",
            level=11,
            description=(
                "Starting at 11th level, your beast companion can make two attacks "
                "when you command it to use the Attack action."
            ),
        ),
        SubclassFeature(
            name="Share Spells",
            level=15,
            description=(
                "Beginning at 15th level, when you cast a spell targeting yourself, "
                "you can also affect your beast companion with the spell if the "
                "beast is within 30 feet of you."
            ),
        ),
    ],
)

# =============================================================================
# RANGER - GLOOM STALKER
# =============================================================================

GLOOM_STALKER = Subclass(
    name="Gloom Stalker",
    parent_class="Ranger",
    description=(
        "Gloom Stalkers are at home in the darkest places: deep under the earth, "
        "in gloomy alleyways, in primeval forests, and wherever else the light "
        "dims. Most folk enter such places with trepidation, but a Gloom Stalker "
        "ventures boldly into the darkness, seeking to ambush threats before they "
        "can reach the broader world."
    ),
    features=[
        SubclassFeature(
            name="Gloom Stalker Magic",
            level=3,
            description=(
                "Starting at 3rd level, you learn an additional spell when you reach "
                "certain levels in this class: 3rd (Disguise Self), 5th (Rope Trick), "
                "9th (Fear), 13th (Greater Invisibility), 17th (Seeming). You gain "
                "these spells once you reach the level and they don't count against "
                "your prepared spells."
            ),
        ),
        SubclassFeature(
            name="Dread Ambusher",
            level=3,
            description=(
                "At 3rd level, you master the art of the ambush. You can add your "
                "Wisdom modifier to your initiative rolls. At the start of your "
                "first turn of each combat, your walking speed increases by 10 feet "
                "until the end of that turn. If you take the Attack action on that "
                "turn, you can make one additional weapon attack. If that attack "
                "hits, the target takes an extra 1d8 damage."
            ),
        ),
        SubclassFeature(
            name="Umbral Sight",
            level=3,
            description=(
                "At 3rd level, you gain darkvision out to a range of 60 feet. If you "
                "already have darkvision from your race, its range increases by 30 "
                "feet. You are also adept at evading creatures that rely on "
                "darkvision. While in darkness, you are invisible to any creature "
                "that relies on darkvision to see you in that darkness."
            ),
        ),
        SubclassFeature(
            name="Iron Mind",
            level=7,
            description=(
                "By 7th level, you have honed your ability to resist the mind-altering "
                "powers of your prey. You gain proficiency in Wisdom saving throws. "
                "If you already have this proficiency, you instead gain proficiency "
                "in Intelligence or Charisma saving throws (your choice)."
            ),
        ),
        SubclassFeature(
            name="Stalker's Flurry",
            level=11,
            description=(
                "At 11th level, you learn to attack with such unexpected speed that "
                "you can turn a miss into another strike. Once on each of your turns "
                "when you miss with a weapon attack, you can make another weapon "
                "attack as part of the same action."
            ),
        ),
        SubclassFeature(
            name="Shadowy Dodge",
            level=15,
            description=(
                "Starting at 15th level, you can dodge in unforeseen ways, with "
                "wisps of supernatural shadow around you. Whenever a creature makes "
                "an attack roll against you and doesn't have advantage on the roll, "
                "you can use your reaction to impose disadvantage on it. You must "
                "use this feature before you know the outcome of the attack roll."
            ),
        ),
    ],
)

# =============================================================================
# ROGUE - ASSASSIN
# =============================================================================

ASSASSIN = Subclass(
    name="Assassin",
    parent_class="Rogue",
    description=(
        "You focus your training on the grim art of death. Those who adhere to "
        "this archetype are diverse: hired killers, spies, bounty hunters, and "
        "even specially anointed priests trained to exterminate the enemies of "
        "their deity. Stealth, poison, and disguise help you eliminate your foes "
        "with deadly efficiency."
    ),
    features=[
        SubclassFeature(
            name="Bonus Proficiencies",
            level=3,
            description=(
                "When you choose this archetype at 3rd level, you gain proficiency "
                "with the disguise kit and the poisoner's kit."
            ),
        ),
        SubclassFeature(
            name="Assassinate",
            level=3,
            description=(
                "Starting at 3rd level, you are at your deadliest when you get the "
                "drop on your enemies. You have advantage on attack rolls against "
                "any creature that hasn't taken a turn in the combat yet. In "
                "addition, any hit you score against a creature that is surprised "
                "is a critical hit."
            ),
        ),
        SubclassFeature(
            name="Infiltration Expertise",
            level=9,
            description=(
                "Starting at 9th level, you can unfailingly create false identities "
                "for yourself. You must spend seven days and 25 gp to establish the "
                "history, profession, and affiliations for an identity. You can't "
                "establish an identity that belongs to someone else. Thereafter, if "
                "you adopt the new identity as a disguise, other creatures believe "
                "you to be that person until given an obvious reason not to."
            ),
        ),
        SubclassFeature(
            name="Impostor",
            level=13,
            description=(
                "At 13th level, you gain the ability to unerringly mimic another "
                "person's speech, writing, and behavior. You must spend at least "
                "three hours studying these three components: listening, examining "
                "handwriting, and observing mannerisms. Your ruse is indiscernible "
                "to the casual observer. If a wary creature suspects something is "
                "amiss, you have advantage on any Charisma (Deception) check you "
                "make to avoid detection."
            ),
        ),
        SubclassFeature(
            name="Death Strike",
            level=17,
            description=(
                "Starting at 17th level, you become a master of instant death. When "
                "you attack and hit a creature that is surprised, it must make a "
                "Constitution saving throw (DC 8 + your Dexterity modifier + your "
                "proficiency bonus). On a failed save, double the damage of your "
                "attack against the creature."
            ),
        ),
    ],
)

# =============================================================================
# ROGUE - ARCANE TRICKSTER
# =============================================================================

ARCANE_TRICKSTER = Subclass(
    name="Arcane Trickster",
    parent_class="Rogue",
    description=(
        "Some rogues enhance their fine-honed skills of stealth and agility with "
        "magic, learning tricks of enchantment and illusion. These rogues include "
        "pickpockets and burglars, but also pranksters, mischief-makers, and a "
        "significant number of adventurers."
    ),
    features=[
        SubclassFeature(
            name="Spellcasting",
            level=3,
            description=(
                "When you reach 3rd level, you augment your martial prowess with the "
                "ability to cast spells. You know three cantrips: Mage Hand and two "
                "others from the wizard spell list. You know three 1st-level wizard "
                "spells, two of which must be from enchantment or illusion. "
                "Intelligence is your spellcasting ability."
            ),
        ),
        SubclassFeature(
            name="Mage Hand Legerdemain",
            level=3,
            description=(
                "Starting at 3rd level, when you cast Mage Hand, you can make the "
                "spectral hand invisible, and you can perform the following additional "
                "tasks with it: stow or retrieve an object in a container worn or "
                "carried by another creature, use thieves' tools to pick locks and "
                "disarm traps at range. You can perform one of these tasks without "
                "being noticed with a Sleight of Hand check vs. the creature's "
                "Perception check."
            ),
        ),
        SubclassFeature(
            name="Magical Ambush",
            level=9,
            description=(
                "Starting at 9th level, if you are hidden from a creature when you "
                "cast a spell on it, the creature has disadvantage on any saving "
                "throw it makes against the spell this turn."
            ),
        ),
        SubclassFeature(
            name="Versatile Trickster",
            level=13,
            description=(
                "At 13th level, you gain the ability to distract targets with your "
                "Mage Hand. As a bonus action on your turn, you can designate a "
                "creature within 5 feet of the spectral hand. You have advantage on "
                "attack rolls against that creature until the end of the turn."
            ),
        ),
        SubclassFeature(
            name="Spell Thief",
            level=17,
            description=(
                "At 17th level, you gain the ability to magically steal the knowledge "
                "of how to cast a spell from another spellcaster. Immediately after "
                "a creature casts a spell that targets you or includes you in its "
                "area of effect, you can use your reaction to force the creature to "
                "make a saving throw with its spellcasting ability. The DC equals "
                "your spell save DC. On a failed save, you negate the spell's effect "
                "against you, and you steal the knowledge of the spell if it is at "
                "least 1st level and of a level you can cast (up to 4th level). For "
                "8 hours, you know the spell and can cast it using your spell slots."
            ),
        ),
    ],
)

# =============================================================================
# SORCERER - WILD MAGIC
# =============================================================================

WILD_MAGIC_SORCERER = Subclass(
    name="Wild Magic",
    parent_class="Sorcerer",
    description=(
        "Your innate magic comes from the wild forces of chaos that underlie the "
        "order of creation. You might have endured exposure to some form of raw "
        "magic, perhaps through a planar portal leading to Limbo, the Elemental "
        "Planes, or the mysterious Far Realm. Perhaps you were blessed by a "
        "powerful fey creature or marked by a demon."
    ),
    features=[
        SubclassFeature(
            name="Wild Magic Surge",
            level=1,
            description=(
                "Starting when you choose this origin at 1st level, your spellcasting "
                "can unleash surges of untamed magic. Once per turn, the DM can have "
                "you roll a d20 immediately after you cast a sorcerer spell of 1st "
                "level or higher. If you roll a 1, roll on the Wild Magic Surge "
                "table to create a magical effect."
            ),
        ),
        SubclassFeature(
            name="Tides of Chaos",
            level=1,
            description=(
                "Starting at 1st level, you can manipulate the forces of chance and "
                "chaos to gain advantage on one attack roll, ability check, or saving "
                "throw. Once you do so, you must finish a long rest before you can "
                "use this feature again. Any time before you regain the use of this "
                "feature, the DM can have you roll on the Wild Magic Surge table "
                "immediately after you cast a spell. You then regain the use of this "
                "feature."
            ),
        ),
        SubclassFeature(
            name="Bend Luck",
            level=6,
            description=(
                "Starting at 6th level, you have the ability to twist fate using "
                "your wild magic. When another creature you can see makes an attack "
                "roll, an ability check, or a saving throw, you can use your reaction "
                "and spend 2 sorcery points to roll 1d4 and apply the number rolled "
                "as a bonus or penalty (your choice) to the creature's roll."
            ),
        ),
        SubclassFeature(
            name="Controlled Chaos",
            level=14,
            description=(
                "At 14th level, you gain a modicum of control over the surges of your "
                "wild magic. Whenever you roll on the Wild Magic Surge table, you can "
                "roll twice and use either number."
            ),
        ),
        SubclassFeature(
            name="Spell Bombardment",
            level=18,
            description=(
                "Beginning at 18th level, the harmful energy of your spells "
                "intensifies. When you roll damage for a spell and roll the highest "
                "number possible on any of the dice, choose one of those dice, roll "
                "it again and add that roll to the damage. You can use the feature "
                "only once per turn."
            ),
        ),
    ],
)

# =============================================================================
# SORCERER - SHADOW MAGIC
# =============================================================================

SHADOW_MAGIC = Subclass(
    name="Shadow Magic",
    parent_class="Sorcerer",
    description=(
        "You are a creature of shadow, for your innate magic comes from the "
        "Shadowfell itself. You might trace your lineage to an entity from that "
        "place, or perhaps you were exposed to its fell energy and transformed by "
        "it. The power of shadow magic casts a strange pall over your physical "
        "presence. The spark of life that sustains you is muffled, as if it "
        "struggles to remain viable against the dark energy that imbues your soul."
    ),
    features=[
        SubclassFeature(
            name="Eyes of the Dark",
            level=1,
            description=(
                "From 1st level, you have darkvision with a range of 120 feet. When "
                "you reach 3rd level in this class, you learn the Darkness spell, "
                "which doesn't count against your spells known. You can cast it by "
                "spending 2 sorcery points or by using a spell slot. If you cast it "
                "with sorcery points, you can see through the darkness created."
            ),
        ),
        SubclassFeature(
            name="Strength of the Grave",
            level=1,
            description=(
                "Starting at 1st level, your existence in a twilight state between "
                "life and death makes you difficult to defeat. When damage reduces "
                "you to 0 hit points, you can make a Charisma saving throw (DC 5 + "
                "the damage taken). On a success, you instead drop to 1 hit point. "
                "You can't use this feature if you are reduced to 0 hit points by "
                "radiant damage or by a critical hit."
            ),
        ),
        SubclassFeature(
            name="Hound of Ill Omen",
            level=6,
            description=(
                "At 6th level, you can spend 3 sorcery points to summon a hound of "
                "ill omen to target one creature you can see within 120 feet. The "
                "hound uses the dire wolf stat block with some modifications. It "
                "appears in an unoccupied space of your choice within 30 feet of the "
                "target. The hound can move through creatures and objects as if they "
                "were difficult terrain. The target has disadvantage on saving throws "
                "against your spells while the hound is within 5 feet of it."
            ),
        ),
        SubclassFeature(
            name="Shadow Walk",
            level=14,
            description=(
                "At 14th level, you gain the ability to step from one shadow into "
                "another. When you are in dim light or darkness, as a bonus action, "
                "you can magically teleport up to 120 feet to an unoccupied space you "
                "can see that is also in dim light or darkness."
            ),
        ),
        SubclassFeature(
            name="Umbral Form",
            level=18,
            description=(
                "Starting at 18th level, you can spend 6 sorcery points as a bonus "
                "action to transform yourself into a shadowy form. In this form, you "
                "have resistance to all damage except force and radiant damage, and "
                "you can move through other creatures and objects as if they were "
                "difficult terrain. The transformation lasts for 1 minute."
            ),
        ),
    ],
)

# =============================================================================
# WARLOCK - THE GREAT OLD ONE
# =============================================================================

THE_GREAT_OLD_ONE = Subclass(
    name="The Great Old One",
    parent_class="Warlock",
    description=(
        "Your patron is a mysterious entity whose nature is utterly foreign to "
        "the fabric of reality. It might come from the Far Realm, the space beyond "
        "reality, or it could be one of the elder gods known only in legends. Its "
        "motives are incomprehensible to mortals, and its knowledge so immense and "
        "ancient that even the greatest libraries pale in comparison to the vast "
        "secrets it holds."
    ),
    features=[
        SubclassFeature(
            name="Awakened Mind",
            level=1,
            description=(
                "Starting at 1st level, your alien knowledge gives you the ability "
                "to touch the minds of other creatures. You can telepathically speak "
                "to any creature you can see within 30 feet of you. You don't need "
                "to share a language with the creature for it to understand your "
                "telepathic utterances, but the creature must be able to understand "
                "at least one language."
            ),
        ),
        SubclassFeature(
            name="Entropic Ward",
            level=6,
            description=(
                "At 6th level, you learn to magically ward yourself against attack "
                "and to turn an enemy's failed strike into good luck for yourself. "
                "When a creature makes an attack roll against you, you can use your "
                "reaction to impose disadvantage on that roll. If the attack misses "
                "you, your next attack roll against the creature has advantage if "
                "you make it before the end of your next turn. Once you use this "
                "feature, you can't use it again until you finish a short or long rest."
            ),
        ),
        SubclassFeature(
            name="Thought Shield",
            level=10,
            description=(
                "Starting at 10th level, your thoughts can't be read by telepathy "
                "or other means unless you allow it. You also have resistance to "
                "psychic damage, and whenever a creature deals psychic damage to "
                "you, that creature takes the same amount of damage that you do."
            ),
        ),
        SubclassFeature(
            name="Create Thrall",
            level=14,
            description=(
                "At 14th level, you gain the ability to infect a humanoid's mind "
                "with the alien magic of your patron. You can use your action to "
                "touch an incapacitated humanoid. That creature is then charmed by "
                "you until a Remove Curse spell is cast on it, the charmed condition "
                "is removed from it, or you use this feature again. You can "
                "communicate telepathically with the charmed creature as long as the "
                "two of you are on the same plane of existence."
            ),
        ),
    ],
    subclass_spells=[
        (1, ["Dissonant Whispers", "Tasha's Hideous Laughter"]),
        (3, ["Detect Thoughts", "Phantasmal Force"]),
        (5, ["Clairvoyance", "Sending"]),
        (7, ["Dominate Beast", "Black Tentacles"]),
        (9, ["Dominate Person", "Telekinesis"]),
    ],
)

# =============================================================================
# WARLOCK - THE CELESTIAL
# =============================================================================

THE_CELESTIAL = Subclass(
    name="The Celestial",
    parent_class="Warlock",
    description=(
        "Your patron is a powerful being of the Upper Planes. You have bound "
        "yourself to an ancient empyrean, solar, ki-rin, unicorn, or other entity "
        "that resides in the planes of everlasting bliss. Your pact with that "
        "being allows you to experience the barest touch of the holy light that "
        "illuminates the multiverse."
    ),
    features=[
        SubclassFeature(
            name="Bonus Cantrips",
            level=1,
            description=(
                "At 1st level, you learn the Light and Sacred Flame cantrips. They "
                "count as warlock cantrips for you, but they don't count against your "
                "number of cantrips known."
            ),
        ),
        SubclassFeature(
            name="Healing Light",
            level=1,
            description=(
                "At 1st level, you gain the ability to channel celestial energy to "
                "heal wounds. You have a pool of d6s that you spend to fuel this "
                "healing. The number of dice in the pool equals 1 + your warlock "
                "level. As a bonus action, you can heal one creature you can see "
                "within 60 feet of you, spending dice from the pool. The maximum "
                "number of dice you can spend at once equals your Charisma modifier "
                "(minimum of one die). Roll the dice you spend, add them together, "
                "and restore a number of hit points equal to the total."
            ),
        ),
        SubclassFeature(
            name="Radiant Soul",
            level=6,
            description=(
                "Starting at 6th level, your link to the Celestial allows you to "
                "serve as a conduit for radiant energy. You have resistance to "
                "radiant damage, and when you cast a spell that deals radiant or "
                "fire damage, you can add your Charisma modifier to one radiant or "
                "fire damage roll of that spell against one of its targets."
            ),
        ),
        SubclassFeature(
            name="Celestial Resilience",
            level=10,
            description=(
                "Starting at 10th level, you gain temporary hit points whenever you "
                "finish a short or long rest. These temporary hit points equal your "
                "warlock level + your Charisma modifier. Additionally, choose up to "
                "five creatures you can see at the end of the rest. Those creatures "
                "each gain temporary hit points equal to half your warlock level + "
                "your Charisma modifier."
            ),
        ),
        SubclassFeature(
            name="Searing Vengeance",
            level=14,
            description=(
                "Starting at 14th level, the radiant energy you channel allows you "
                "to resist death. When you have to make a death saving throw at the "
                "start of your turn, you can instead spring back to your feet with "
                "a burst of radiant energy. You regain hit points equal to half your "
                "hit point maximum, and then you stand up if you so choose. Each "
                "creature of your choice within 30 feet of you takes radiant damage "
                "equal to 2d8 + your Charisma modifier, and is blinded until the end "
                "of the current turn. Once you use this feature, you can't use it "
                "again until you finish a long rest."
            ),
        ),
    ],
    subclass_spells=[
        (1, ["Cure Wounds", "Guiding Bolt"]),
        (3, ["Flaming Sphere", "Lesser Restoration"]),
        (5, ["Daylight", "Revivify"]),
        (7, ["Guardian of Faith", "Wall of Fire"]),
        (9, ["Flame Strike", "Greater Restoration"]),
    ],
)

# =============================================================================
# WIZARD - SCHOOL OF ABJURATION
# =============================================================================

SCHOOL_OF_ABJURATION = Subclass(
    name="School of Abjuration",
    parent_class="Wizard",
    description=(
        "The School of Abjuration emphasizes magic that blocks, banishes, or "
        "protects. Detractors of this school say that its tradition is about "
        "denial, negation rather than positive assertion. You understand, however, "
        "that ending harmful effects, protecting the weak, and banishing evil "
        "influences is anything but a philosophical void."
    ),
    features=[
        SubclassFeature(
            name="Abjuration Savant",
            level=2,
            description=(
                "Beginning when you select this school at 2nd level, the gold and "
                "time you must spend to copy an abjuration spell into your spellbook "
                "is halved."
            ),
        ),
        SubclassFeature(
            name="Arcane Ward",
            level=2,
            description=(
                "Starting at 2nd level, you can weave magic around yourself for "
                "protection. When you cast an abjuration spell of 1st level or "
                "higher, you can simultaneously use a strand of the spell's magic "
                "to create a magical ward on yourself that lasts until you finish "
                "a long rest. The ward has hit points equal to twice your wizard "
                "level + your Intelligence modifier. Whenever you take damage, the "
                "ward takes the damage instead. If the damage reduces the ward to "
                "0 hit points, you take any remaining damage."
            ),
        ),
        SubclassFeature(
            name="Projected Ward",
            level=6,
            description=(
                "Starting at 6th level, when a creature that you can see within 30 "
                "feet of you takes damage, you can use your reaction to cause your "
                "Arcane Ward to absorb that damage. If this damage reduces the ward "
                "to 0 hit points, the warded creature takes any remaining damage."
            ),
        ),
        SubclassFeature(
            name="Improved Abjuration",
            level=10,
            description=(
                "Beginning at 10th level, when you cast an abjuration spell that "
                "requires you to make an ability check as a part of casting that "
                "spell (as in Counterspell and Dispel Magic), you add your "
                "proficiency bonus to that ability check."
            ),
        ),
        SubclassFeature(
            name="Spell Resistance",
            level=14,
            description=(
                "Starting at 14th level, you have advantage on saving throws against "
                "spells. Furthermore, you have resistance against the damage of spells."
            ),
        ),
    ],
)

# =============================================================================
# WIZARD - SCHOOL OF DIVINATION
# =============================================================================

SCHOOL_OF_DIVINATION = Subclass(
    name="School of Divination",
    parent_class="Wizard",
    description=(
        "The counsel of a diviner is sought by royalty and commoners alike, for "
        "all seek a clearer understanding of the past, present, and future. As a "
        "diviner, you strive to part the veils of space, time, and consciousness "
        "so that you can see clearly. You work to master spells of discernment, "
        "remote viewing, supernatural knowledge, and foresight."
    ),
    features=[
        SubclassFeature(
            name="Divination Savant",
            level=2,
            description=(
                "Beginning when you select this school at 2nd level, the gold and "
                "time you must spend to copy a divination spell into your spellbook "
                "is halved."
            ),
        ),
        SubclassFeature(
            name="Portent",
            level=2,
            description=(
                "Starting at 2nd level when you choose this school, glimpses of the "
                "future begin to press in on your awareness. When you finish a long "
                "rest, roll two d20s and record the numbers rolled. You can replace "
                "any attack roll, saving throw, or ability check made by you or a "
                "creature that you can see with one of these foretelling rolls. You "
                "must choose to do so before the roll. Each foretelling roll can be "
                "used only once. When you finish a long rest, you lose any unused "
                "foretelling rolls."
            ),
        ),
        SubclassFeature(
            name="Expert Divination",
            level=6,
            description=(
                "Beginning at 6th level, casting divination spells comes so easily "
                "to you that it expends only a fraction of your spellcasting efforts. "
                "When you cast a divination spell of 2nd level or higher using a "
                "spell slot, you regain one expended spell slot. The slot you regain "
                "must be of a level lower than the spell you cast and can't be higher "
                "than 5th level."
            ),
        ),
        SubclassFeature(
            name="The Third Eye",
            level=10,
            description=(
                "Starting at 10th level, you can use your action to increase your "
                "powers of perception. When you do so, choose one of the following "
                "benefits, which lasts until you are incapacitated or you take a "
                "short or long rest: Darkvision (60 feet), Ethereal Sight (see into "
                "the Ethereal Plane within 60 feet), Greater Comprehension (read any "
                "language), or See Invisibility (see invisible creatures and objects "
                "within 10 feet)."
            ),
        ),
        SubclassFeature(
            name="Greater Portent",
            level=14,
            description=(
                "Starting at 14th level, the visions in your dreams intensify and "
                "paint a more accurate picture in your mind of what is to come. You "
                "roll three d20s for your Portent feature, rather than two."
            ),
        ),
    ],
)


# =============================================================================
# 2024 REVISED SUBCLASSES
# =============================================================================

# The 2024 Player's Handbook revised several subclasses with updated mechanics.
# These versions are marked with ruleset="dnd2024" while the original 2014
# versions remain for backwards compatibility.

BERSERKER_2024 = Subclass(
    name="Path of the Berserker",
    parent_class="Barbarian",
    description=(
        "For some barbarians, rage is a means to an end—that end being violence. "
        "The Path of the Berserker is a path of untrammeled fury, slick with blood. "
        "As you enter the berserker's rage, you thrill in the chaos of battle, "
        "heedless of your own health or well-being."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Frenzy",
            level=3,
            description=(
                "You can go into a frenzy as part of your Rage. If you do so, "
                "for the duration of the Rage you can make one extra attack "
                "as part of each of your Attack actions. When your Rage ends, "
                "you have Exhaustion 1 unless you succeeded on a DC 15 "
                "Constitution saving throw made when the Rage ends. The DC "
                "increases by 5 each time you use Frenzy, resetting after a Long Rest."
            ),
        ),
        SubclassFeature(
            name="Mindless Rage",
            level=6,
            description=(
                "You have Immunity to the Charmed and Frightened conditions while "
                "Raging. If you were Charmed or Frightened when you entered your "
                "Rage, those conditions are suppressed for the Rage's duration."
            ),
        ),
        SubclassFeature(
            name="Retaliation",
            level=10,
            description=(
                "When you take damage from a creature that is within 5 feet of you, "
                "you can take a Reaction to make one melee attack against that creature "
                "using a weapon or an Unarmed Strike."
            ),
        ),
        SubclassFeature(
            name="Intimidating Presence",
            level=14,
            description=(
                "As a Bonus Action, you can strike terror into others with your "
                "menacing presence. When you do so, each creature of your choice "
                "within 30 feet of you must succeed on a Wisdom saving throw "
                "(DC 8 + your Proficiency Bonus + your Strength modifier) or have "
                "the Frightened condition until the end of your next turn. If a "
                "creature fails the save while you're Raging, the condition lasts "
                "until the Rage ends, but the creature can repeat the save at the "
                "end of each of its turns, ending the effect on itself on a success."
            ),
        ),
    ],
)

CHAMPION_2024 = Subclass(
    name="Champion",
    parent_class="Fighter",
    description=(
        "A Champion focuses on the development of martial prowess honed to deadly "
        "perfection. Champions combine rigorous training with physical excellence "
        "to deal devastating blows. Their straightforward approach to combat "
        "emphasizes raw power and athletic skill over tactical complexity."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Improved Critical",
            level=3,
            description=(
                "Your attack rolls with weapons and Unarmed Strikes can score a "
                "Critical Hit on a roll of 19 or 20 on the d20."
            ),
        ),
        SubclassFeature(
            name="Remarkable Athlete",
            level=7,
            description=(
                "You have Advantage on Initiative rolls and Strength (Athletics) checks. "
                "When you make a running Long Jump, the distance you can cover increases "
                "by a number of feet equal to your Strength modifier."
            ),
        ),
        SubclassFeature(
            name="Additional Fighting Style",
            level=10,
            description=(
                "You gain another Fighting Style feat of your choice."
            ),
        ),
        SubclassFeature(
            name="Superior Critical",
            level=15,
            description=(
                "Your attack rolls with weapons and Unarmed Strikes can score a "
                "Critical Hit on a roll of 18, 19, or 20 on the d20."
            ),
        ),
        SubclassFeature(
            name="Survivor",
            level=18,
            description=(
                "You attain the pinnacle of resilience in battle. At the start of "
                "each of your turns, you regain Hit Points equal to 5 plus your "
                "Constitution modifier if you have no more than half of your Hit "
                "Points left. You don't gain this benefit if you have 0 Hit Points."
            ),
        ),
    ],
)

THIEF_2024 = Subclass(
    name="Thief",
    parent_class="Rogue",
    description=(
        "You hone your skills in the larcenous arts. Burglars, bandits, cutpurses, "
        "and other criminals typically follow this archetype, but so do rogues who "
        "prefer to think of themselves as professional treasure seekers, explorers, "
        "delvers, and investigators. You improve your agility and stealth while "
        "learning skills useful for delving into ancient ruins and using magic items."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Fast Hands",
            level=3,
            description=(
                "You have Advantage on Dexterity (Sleight of Hand) checks, and as "
                "a Bonus Action, you can do one of the following: make a Dexterity "
                "(Sleight of Hand) check to pick a pocket, pick a lock or disarm "
                "a trap with Thieves' Tools, or take the Use an Object action."
            ),
        ),
        SubclassFeature(
            name="Second-Story Work",
            level=3,
            description=(
                "You have a Climb Speed equal to your Speed, and when you take the "
                "Dash action, the extra movement from that action isn't reduced by "
                "Difficult Terrain."
            ),
        ),
        SubclassFeature(
            name="Supreme Sneak",
            level=9,
            description=(
                "You gain the following benefits: You have Advantage on every "
                "Dexterity (Stealth) check you make, provided you aren't wearing "
                "Medium or Heavy armor. On your turn, you can move through any "
                "enemy's space if that enemy is Large or larger."
            ),
        ),
        SubclassFeature(
            name="Use Magic Device",
            level=13,
            description=(
                "You have learned enough about how magic works that you can use "
                "any magic item that has a class, species, or other requirement. "
                "You also ignore Attunement requirements for magic items. If the "
                "item requires Attunement, you must still attune to it, but you "
                "can ignore any of its other requirements."
            ),
        ),
        SubclassFeature(
            name="Thief's Reflexes",
            level=17,
            description=(
                "You can take two turns during the first round of any combat. You "
                "take your first turn at your normal Initiative and your second turn "
                "at your Initiative minus 10."
            ),
        ),
    ],
)

HUNTER_2024 = Subclass(
    name="Hunter",
    parent_class="Ranger",
    description=(
        "Emulating the Hunter archetype means accepting your place as a bulwark "
        "between civilization and the terrors of the wilderness. As you walk the "
        "Hunter's path, you learn specialized techniques for fighting the threats "
        "you face, from rampaging ogres and hordes of orcs to towering giants and "
        "terrifying dragons."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Hunter's Prey",
            level=3,
            description=(
                "You gain one of the following features of your choice. Whenever you "
                "finish a Short or Long Rest, you can replace the feature you chose "
                "with the other one. Colossus Slayer: Your tenacity can wear down the "
                "most potent foes. Once per turn when you hit a creature with a weapon, "
                "that attack deals an extra 1d8 damage to the target if it's below its "
                "Hit Point maximum. Horde Breaker: Once on each of your turns when you "
                "make an attack with a weapon, you can make another attack with the same "
                "weapon against a different creature that is within 5 feet of the "
                "original target, is within the weapon's normal range, and that you "
                "haven't attacked this turn."
            ),
        ),
        SubclassFeature(
            name="Hunter's Lore",
            level=3,
            description=(
                "You can call on the forces of nature to reveal certain strengths and "
                "weaknesses of your prey. As a Bonus Action while a creature is in your "
                "Hunter's Mark, you learn whether the creature has any Immunities, "
                "Resistances, or Vulnerabilities, and if so, what they are."
            ),
        ),
        SubclassFeature(
            name="Defensive Tactics",
            level=7,
            description=(
                "You gain one of the following features of your choice. Whenever you "
                "finish a Short or Long Rest, you can replace the feature you chose "
                "with the other one. Multiattack Defense: When a creature hits you with "
                "an attack roll, you gain a +4 bonus to AC against all subsequent attacks "
                "made by that creature for the rest of the turn. Escape the Horde: "
                "Opportunity Attacks have Disadvantage against you."
            ),
        ),
        SubclassFeature(
            name="Superior Hunter's Prey",
            level=11,
            description=(
                "You gain one of the following features of your choice. Whenever you "
                "finish a Short or Long Rest, you can replace the feature you chose "
                "with the other one. Multiattack: Make two attacks with your Extra "
                "Attack feature instead of one when you use the Attack action. Whirlwind "
                "Attack: You can use your action to make a melee attack against any "
                "number of creatures within 5 feet of you, making a separate attack roll "
                "for each target."
            ),
        ),
        SubclassFeature(
            name="Superior Hunter's Defense",
            level=15,
            description=(
                "You gain one of the following features of your choice. Whenever you "
                "finish a Short or Long Rest, you can replace the feature you chose "
                "with the other one. Evasion: When you take the Dodge action, you can "
                "make one weapon attack as part of that action. Uncanny Dodge: When an "
                "attacker that you can see hits you with an attack roll, you can use "
                "your Reaction to halve the attack's damage against you."
            ),
        ),
    ],
)

LIFE_DOMAIN_2024 = Subclass(
    name="Life Domain",
    parent_class="Cleric",
    description=(
        "The Life domain focuses on the vibrant positive energy that sustains all "
        "life. Clerics of this domain promote vitality and health through healing "
        "the sick and wounded, caring for those in need, and driving away the "
        "forces of death and undeath."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Disciple of Life",
            level=3,
            description=(
                "When a spell you cast with a spell slot restores Hit Points to a "
                "creature, that creature regains additional Hit Points on the turn "
                "you cast the spell. The additional Hit Points equal 2 plus the "
                "spell slot's level."
            ),
        ),
        SubclassFeature(
            name="Preserve Life",
            level=3,
            description=(
                "As a Magic action, you present your Holy Symbol and expend a use "
                "of your Channel Divinity to evoke healing energy. Choose creatures "
                "within 30 feet of yourself, and divide the following amount of Hit "
                "Points among them: 5 times your Cleric level. You can restore no "
                "more than half a creature's Hit Point maximum. You can't use this "
                "feature on a creature that has the Undead or Construct creature type."
            ),
        ),
        SubclassFeature(
            name="Blessed Healer",
            level=6,
            description=(
                "The healing spells you cast on others heal you as well. Immediately "
                "after you cast a spell with a spell slot that restores Hit Points "
                "to one or more creatures other than you, you regain Hit Points "
                "equal to 2 plus the spell slot's level."
            ),
        ),
        SubclassFeature(
            name="Divine Strike",
            level=8,
            description=(
                "Once on each of your turns when you hit a creature with an attack "
                "roll using a weapon or a cantrip, you can cause the target to take "
                "an extra 1d8 Radiant damage. When you reach level 14, this extra "
                "damage increases to 2d8."
            ),
        ),
        SubclassFeature(
            name="Supreme Healing",
            level=17,
            description=(
                "When you would normally roll one or more dice to restore Hit Points "
                "to a creature with a spell or Channel Divinity, don't roll those "
                "dice for the healing. Instead, use the highest number possible for "
                "each die."
            ),
        ),
    ],
    subclass_spells=[
        (3, ["Bless", "Cure Wounds"]),
        (5, ["Aid", "Lesser Restoration"]),
        (7, ["Mass Healing Word", "Revivify"]),
        (9, ["Aura of Life", "Death Ward"]),
    ],
)

COLLEGE_OF_LORE_2024 = Subclass(
    name="College of Lore",
    parent_class="Bard",
    description=(
        "Bards of the College of Lore know something about most things, collecting "
        "bits of knowledge from sources as diverse as scholarly tomes and peasant "
        "tales. Whether singing folk ballads in taverns or elaborate compositions in "
        "royal courts, these bards use their gifts to hold audiences spellbound."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Bonus Proficiencies",
            level=3,
            description=(
                "You gain proficiency with three skills of your choice."
            ),
        ),
        SubclassFeature(
            name="Cutting Words",
            level=3,
            description=(
                "You learn how to use your wit to supernaturally distract, confuse, "
                "and otherwise sap the confidence and competence of others. When a "
                "creature that you can see within 60 feet of yourself makes an "
                "Attack Roll, Ability Check, or Damage Roll, you can take a Reaction "
                "to expend one use of your Bardic Inspiration. Roll the Bardic "
                "Inspiration die, and subtract the number rolled from the creature's "
                "roll, potentially turning a success into a failure."
            ),
        ),
        SubclassFeature(
            name="Magical Discoveries",
            level=6,
            description=(
                "You learn two spells of your choice. These spells can come from any "
                "spell list, and they must be of a level for which you have spell "
                "slots. The spells count as Bard spells for you but don't count "
                "against the number of spells you know."
            ),
        ),
        SubclassFeature(
            name="Peerless Skill",
            level=14,
            description=(
                "When you make an Ability Check or Attack Roll and fail, you can "
                "expend one use of your Bardic Inspiration, roll the Bardic "
                "Inspiration die, and add the number rolled to the d20, potentially "
                "turning a failure into a success. If the check still fails, the "
                "Bardic Inspiration is not expended."
            ),
        ),
    ],
)

CIRCLE_OF_THE_LAND_2024 = Subclass(
    name="Circle of the Land",
    parent_class="Druid",
    description=(
        "The Circle of the Land is made up of mystics and sages who safeguard "
        "ancient knowledge and rites through a vast oral tradition. These druids "
        "meet within sacred circles of trees or standing stones to whisper primal "
        "secrets and guard the balance of nature."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Land's Aid",
            level=3,
            description=(
                "As a Magic action, you can expend a use of your Wild Shape and "
                "choose a point within 60 feet of yourself. Vitality-giving flowers "
                "and life energy appear for a moment in a 10-foot-radius Sphere "
                "centered on that point. Each creature of your choice in that area "
                "regains Hit Points equal to 2d6 plus your Wisdom modifier."
            ),
        ),
        SubclassFeature(
            name="Circle Spells",
            level=3,
            description=(
                "Your connection to a particular terrain infuses you with the ability "
                "to cast certain spells. You have the spells from the Circle Spells "
                "table always prepared and they don't count against the number of "
                "spells you can have prepared. Choose the type of land that most "
                "represents the terrain you are most connected to: Arid, Polar, "
                "Temperate, or Tropical."
            ),
        ),
        SubclassFeature(
            name="Natural Recovery",
            level=6,
            description=(
                "You can cast one of your Circle Spells without expending a spell slot, "
                "and you must finish a Long Rest before you can do so again. In addition, "
                "when you finish a Short Rest, you can recover spell slots with a combined "
                "level equal to no more than half your Druid level (round up), and none "
                "of the slots can be level 6 or higher."
            ),
        ),
        SubclassFeature(
            name="Nature's Ward",
            level=10,
            description=(
                "You have Immunity to the Poisoned condition, and you have Resistance "
                "to one of the following damage types of your choice: Cold, Fire, "
                "Lightning, or Poison."
            ),
        ),
        SubclassFeature(
            name="Nature's Sanctuary",
            level=14,
            description=(
                "Creatures of the natural world sense your connection to nature and "
                "become hesitant to attack you. When a Beast, Elemental, Fey, or Plant "
                "creature targets you or includes you in an area of effect, that creature "
                "must succeed on a Wisdom saving throw against your spell save DC or "
                "the creature must choose a different target, or the attack automatically "
                "misses. On a successful save, the creature is immune to this effect "
                "for 24 hours."
            ),
        ),
    ],
)

WAY_OF_THE_OPEN_HAND_2024 = Subclass(
    name="Way of the Open Hand",
    parent_class="Monk",
    description=(
        "Monks of the Way of the Open Hand are the ultimate masters of martial arts "
        "combat, whether armed or unarmed. They learn techniques to push and trip "
        "their opponents, manipulate their life energy to heal damage, and practice "
        "meditation to grant them protection."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Open Hand Technique",
            level=3,
            description=(
                "Whenever you hit a creature with an attack granted by your Flurry "
                "of Blows, you can impose one of the following effects on that target: "
                "The target must succeed on a Dexterity saving throw or have the "
                "Prone condition. The target must succeed on a Strength saving throw "
                "or be pushed up to 15 feet directly away from you. The target can't "
                "take Reactions until the start of its next turn."
            ),
        ),
        SubclassFeature(
            name="Wholeness of Body",
            level=6,
            description=(
                "You gain the ability to heal yourself. As a Bonus Action, you can "
                "spend 2 Focus Points and roll your Martial Arts die. You regain "
                "Hit Points equal to three times the number rolled."
            ),
        ),
        SubclassFeature(
            name="Fleet Step",
            level=11,
            description=(
                "When you take a Bonus Action other than Step of the Wind, you can "
                "also take that Bonus Action to move up to half your Speed without "
                "provoking Opportunity Attacks."
            ),
        ),
        SubclassFeature(
            name="Quivering Palm",
            level=17,
            description=(
                "You gain the ability to set up lethal vibrations in someone's body. "
                "When you hit a creature with an Unarmed Strike, you can spend 4 "
                "Focus Points to start these imperceptible vibrations, which last "
                "for a number of days equal to your Monk level. The vibrations end "
                "early if you use this feature again. At any point while the target "
                "is affected, you can take an action to end the vibrations, dealing "
                "10d12 Force damage. Or you can allow the creature to make a "
                "Constitution saving throw. On a failed save, it drops to 0 Hit Points. "
                "On a successful save, it takes 10d12 Force damage."
            ),
        ),
    ],
)

OATH_OF_DEVOTION_2024 = Subclass(
    name="Oath of Devotion",
    parent_class="Paladin",
    description=(
        "The Oath of Devotion binds a paladin to the loftiest ideals of justice and "
        "virtue. These paladins meet the ideal of the knight in shining armor, "
        "acting with honor in pursuit of justice and the greater good."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Oath Spells",
            level=3,
            description=(
                "You gain oath spells at the Paladin levels listed: 3rd - Protection "
                "from Evil and Good, Shield of Faith; 5th - Aid, Zone of Truth; "
                "9th - Beacon of Hope, Dispel Magic; 13th - Freedom of Movement, "
                "Guardian of Faith; 17th - Commune, Flame Strike."
            ),
        ),
        SubclassFeature(
            name="Sacred Weapon",
            level=3,
            description=(
                "As a Bonus Action, you can expend one use of your Channel Divinity "
                "to imbue one weapon that you are holding with positive energy. For "
                "1 minute, you add your Charisma modifier to attack rolls made with "
                "that weapon (minimum bonus of +1). The weapon also emits Bright Light "
                "in a 20-foot radius and Dim Light 20 feet beyond that. You can end "
                "this effect early as a Bonus Action. This effect also ends if you "
                "aren't carrying the weapon or if you have the Incapacitated condition."
            ),
        ),
        SubclassFeature(
            name="Aura of Devotion",
            level=7,
            description=(
                "You and your allies have Immunity to the Charmed condition while "
                "in your Aura of Protection."
            ),
        ),
        SubclassFeature(
            name="Smite of Protection",
            level=15,
            description=(
                "Your magical smites now protect your allies. When you use your Divine "
                "Smite, you can also choose one ally you can see within 30 feet of "
                "yourself. That ally gains Temporary Hit Points equal to 1d8 plus the "
                "level of the spell slot expended, plus your Charisma modifier."
            ),
        ),
        SubclassFeature(
            name="Holy Nimbus",
            level=20,
            description=(
                "As a Bonus Action, you can emanate an aura of sunlight that lasts for "
                "1 minute or until you end it (no action required). You emit Bright "
                "Light in a 30-foot radius and Dim Light 30 feet beyond that. Whenever "
                "an enemy creature starts its turn in that Bright Light, it takes "
                "Radiant damage equal to your Proficiency Bonus plus your Charisma "
                "modifier. You also have Advantage on saving throws against spells "
                "cast by Fiends or Undead. Once you use this feature, you can't use "
                "it again until you finish a Long Rest, unless you expend a level 5 "
                "spell slot to restore your use of it."
            ),
        ),
    ],
)

DRACONIC_BLOODLINE_2024 = Subclass(
    name="Draconic Bloodline",
    parent_class="Sorcerer",
    description=(
        "Your innate magic comes from draconic ancestry. Most often, sorcerers with "
        "this origin trace their descent back to a mighty sorcerer of ancient times "
        "who made a bargain with a dragon or who might even have claimed a dragon "
        "parent. Some bloodlines are well established, but most are obscure."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Draconic Resilience",
            level=1,
            description=(
                "As magic flows through your body, it causes physical traits of your "
                "dragon ancestors to emerge. Your Hit Point maximum increases by 1, "
                "and it increases by 1 again whenever you gain a level in this class. "
                "Parts of your skin are covered by a thin sheen of dragon-like scales. "
                "While you aren't wearing armor, your base Armor Class equals 10 plus "
                "your Dexterity modifier plus your Charisma modifier."
            ),
        ),
        SubclassFeature(
            name="Draconic Ancestry",
            level=1,
            description=(
                "Choose one type of dragon from the Draconic Ancestry table. The damage "
                "type associated with your ancestry is used by features you gain later. "
                "You can speak, read, and write Draconic. In addition, you learn the "
                "Thaumaturgy cantrip, which doesn't count against the number of "
                "Sorcerer cantrips you know."
            ),
        ),
        SubclassFeature(
            name="Elemental Affinity",
            level=6,
            description=(
                "When you cast a spell that deals damage of the type associated with "
                "your Draconic Ancestry, you can add your Charisma modifier to one "
                "damage roll of that spell. At the same time, you can spend 1 Sorcery "
                "Point to gain Resistance to that damage type for 1 hour."
            ),
        ),
        SubclassFeature(
            name="Dragon Wings",
            level=14,
            description=(
                "You gain the ability to sprout a pair of dragon wings from your back. "
                "As a Bonus Action, you gain a Fly Speed equal to your Speed for 1 hour "
                "or until you dismiss the wings (no action required). You can't manifest "
                "your wings while wearing armor unless the armor is made to accommodate "
                "them, and clothing not made to accommodate your wings might be destroyed "
                "when you manifest them."
            ),
        ),
        SubclassFeature(
            name="Draconic Presence",
            level=18,
            description=(
                "You can channel the dread presence of your dragon ancestor, causing "
                "those around you to become awestruck or frightened. As a Magic action, "
                "you can spend 5 Sorcery Points to draw on this power and exude an "
                "aura of awe or fear (your choice) to a distance of 60 feet. For 1 "
                "minute or until you have the Incapacitated condition or lose "
                "Concentration, each hostile creature that starts its turn in this "
                "aura must succeed on a Wisdom saving throw or have the Charmed "
                "(if you chose awe) or Frightened (if you chose fear) condition "
                "until the aura ends. A creature that succeeds on this saving throw "
                "is immune to your Draconic Presence for 24 hours."
            ),
        ),
    ],
)

THE_FIEND_2024 = Subclass(
    name="The Fiend",
    parent_class="Warlock",
    description=(
        "You have made a pact with a fiend from the lower planes of existence, a "
        "being whose aims are evil, even if you strive against those aims. Such "
        "beings desire the corruption or destruction of all things, ultimately "
        "including you."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Dark One's Blessing",
            level=1,
            description=(
                "When you reduce an enemy to 0 Hit Points, you gain Temporary Hit "
                "Points equal to your Charisma modifier plus your Warlock level "
                "(minimum of 1 Temporary Hit Point)."
            ),
        ),
        SubclassFeature(
            name="Dark One's Own Luck",
            level=6,
            description=(
                "You can call on your patron to alter fate in your favor. When you "
                "make an Ability Check or a saving throw, you can use this feature "
                "to add 1d10 to your roll. You can do so after seeing the roll but "
                "before any of the roll's effects occur. You can use this feature "
                "a number of times equal to your Charisma modifier (minimum once), "
                "and you regain all expended uses when you finish a Long Rest."
            ),
        ),
        SubclassFeature(
            name="Fiendish Resilience",
            level=10,
            description=(
                "Choose one damage type when you finish a Short or Long Rest. You "
                "gain Resistance to that damage type until you choose a different "
                "one with this feature. Damage from magical weapons or silver weapons "
                "ignores this Resistance."
            ),
        ),
        SubclassFeature(
            name="Hurl Through Hell",
            level=14,
            description=(
                "When you hit a creature with an attack roll, you can use this "
                "feature to instantly transport the target through the lower planes. "
                "The creature disappears and hurtles through a nightmare landscape. "
                "At the end of your next turn, the target returns to the space it "
                "previously occupied, or the nearest unoccupied space. If the target "
                "is not a Fiend, it takes 10d10 Psychic damage as it reels from its "
                "horrific experience. Once you use this feature, you can't use it "
                "again until you finish a Long Rest."
            ),
        ),
    ],
    subclass_spells=[
        (1, ["Burning Hands", "Command"]),
        (3, ["Scorching Ray", "Suggestion"]),
        (5, ["Fireball", "Stinking Cloud"]),
        (7, ["Fire Shield", "Wall of Fire"]),
        (9, ["Flame Strike", "Geas"]),
    ],
)

SCHOOL_OF_EVOCATION_2024 = Subclass(
    name="School of Evocation",
    parent_class="Wizard",
    description=(
        "You focus your study on magic that creates powerful elemental effects such "
        "as bitter cold, searing flame, rolling thunder, crackling lightning, and "
        "burning acid. Some evokers find employment in military forces, serving as "
        "artillery to blast enemy armies from afar."
    ),
    ruleset="dnd2024",
    features=[
        SubclassFeature(
            name="Evocation Savant",
            level=2,
            description=(
                "Choose two Evocation spells from the Wizard spell list, each of "
                "which must be no higher than 2nd level, and add them to your "
                "spellbook for free. Whenever you gain a Wizard level after this, "
                "you can add one Evocation spell from the Wizard spell list to your "
                "spellbook for free."
            ),
        ),
        SubclassFeature(
            name="Sculpt Spells",
            level=2,
            description=(
                "You can create pockets of relative safety within the effects of "
                "your evocation spells. When you cast an Evocation spell that "
                "affects other creatures that you can see, you can choose a number "
                "of them equal to 1 + the spell's level. The chosen creatures "
                "automatically succeed on their saving throws against the spell, "
                "and they take no damage if they would normally take half damage "
                "on a successful save."
            ),
        ),
        SubclassFeature(
            name="Potent Cantrip",
            level=6,
            description=(
                "Your damaging cantrips affect even creatures that avoid the brunt "
                "of the effect. When a creature succeeds on a saving throw against "
                "your cantrip, the creature takes half the cantrip's damage (if any) "
                "but suffers no additional effect from the cantrip."
            ),
        ),
        SubclassFeature(
            name="Empowered Evocation",
            level=10,
            description=(
                "You can add your Intelligence modifier to one damage roll of any "
                "Evocation spell that you cast."
            ),
        ),
        SubclassFeature(
            name="Overchannel",
            level=14,
            description=(
                "You can increase the power of your simpler spells. When you cast "
                "a spell of levels 1-5 that deals damage, you can deal maximum "
                "damage with that spell. The first time you do so, you suffer no "
                "adverse effect. If you use this feature again before you finish "
                "a Long Rest, you take 2d12 Necrotic damage for each level of the "
                "spell immediately after you cast it. Each time you use this feature "
                "again before finishing a Long Rest, the Necrotic damage per spell "
                "level increases by 1d12."
            ),
        ),
    ],
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - BARBARIAN
# =============================================================================

TOV_WILD_FURY = Subclass(
    name="Path of Wild Fury",
    parent_class="Barbarian",
    description=(
        "Some barbarians draw upon the primal spirits of nature itself. The Path "
        "of Wild Fury connects you to animal totems that grant supernatural "
        "abilities. In battle, your totem spirit fills you with might, making you "
        "a force of nature incarnate."
    ),
    features=[
        SubclassFeature(
            name="Totem Spirit",
            level=3,
            description=(
                "At 3rd level, when you adopt this path, you choose a totem spirit "
                "and gain its feature. Bear: While raging, you have resistance to "
                "all damage except psychic. Eagle: While raging, you can Dash as "
                "a bonus action and opportunity attacks against you have "
                "disadvantage. Wolf: While raging, your allies have advantage on "
                "melee attack rolls against creatures within 5 feet of you."
            ),
        ),
        SubclassFeature(
            name="Aspect of the Beast",
            level=7,
            description=(
                "At 7th level, you gain a magical benefit based on your totem. "
                "Bear: Your carrying capacity doubles and you have advantage on "
                "Strength checks. Eagle: You can see clearly up to 1 mile and "
                "discern fine details at 100 feet. Wolf: You can track at fast "
                "pace and move stealthily at normal pace."
            ),
        ),
        SubclassFeature(
            name="Spirit Walker",
            level=11,
            description=(
                "At 11th level, you can cast Commune with Nature as a ritual. When "
                "you do so, a spiritual version of your totem animal appears to "
                "convey the information you seek. Additionally, while raging, you "
                "gain 1 Luck at the start of each of your turns."
            ),
        ),
        SubclassFeature(
            name="Totemic Attunement",
            level=15,
            description=(
                "At 15th level, you gain a powerful magical benefit. Bear: While "
                "raging, hostile creatures within 5 feet have disadvantage on "
                "attacks against targets other than you. Eagle: While raging, you "
                "have a flying speed equal to your walking speed. Wolf: While "
                "raging, hitting a Large or smaller creature lets you knock it "
                "prone as a bonus action."
            ),
        ),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - BARD
# =============================================================================

TOV_COLLEGE_OF_VICTORY = Subclass(
    name="College of Victory",
    parent_class="Bard",
    description=(
        "Bards of the College of Victory are warriors at heart, using their "
        "performances to rally troops and celebrate martial prowess. They train "
        "in combat alongside their musical studies, becoming skilled fighters "
        "who inspire through deeds as much as words."
    ),
    features=[
        SubclassFeature(
            name="Bonus Proficiencies",
            level=3,
            description=(
                "When you join the College of Victory at 3rd level, you gain "
                "proficiency with medium armor, shields, and martial weapons."
            ),
        ),
        SubclassFeature(
            name="War Chant",
            level=3,
            description=(
                "Also at 3rd level, you can use a bonus action to begin a war "
                "chant. For 1 minute, you and allies within 30 feet who can hear "
                "you gain a bonus to weapon damage rolls equal to your Charisma "
                "modifier. The chant ends early if you are incapacitated or "
                "silenced. You can use this feature once per short or long rest."
            ),
        ),
        SubclassFeature(
            name="Extra Attack",
            level=7,
            description=(
                "Beginning at 7th level, you can attack twice, instead of once, "
                "whenever you take the Attack action on your turn."
            ),
        ),
        SubclassFeature(
            name="Triumphant Surge",
            level=11,
            description=(
                "Starting at 11th level, when you reduce a creature to 0 hit "
                "points, you can use your reaction to grant an ally within 30 "
                "feet who can see you temporary hit points equal to your bard "
                "level + your Charisma modifier, and they gain 1 Luck."
            ),
        ),
        SubclassFeature(
            name="Legendary Presence",
            level=15,
            description=(
                "At 15th level, your presence on the battlefield is the stuff of "
                "legend. When you use your War Chant, allies also gain advantage "
                "on saving throws against being frightened or charmed for the "
                "duration. Additionally, when an ally uses a Bardic Inspiration "
                "die you gave them, they gain 1 Luck."
            ),
        ),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - DRUID
# =============================================================================

TOV_RING_OF_THE_LEAF = Subclass(
    name="Ring of the Leaf",
    parent_class="Druid",
    description=(
        "Druids of the Ring of the Leaf are devoted to the green growing things "
        "of the world. They draw power from forests, fields, and gardens, "
        "channeling the vitality of plant life into their magic. These druids "
        "often serve as guardians of ancient groves and cultivators of rare "
        "botanical specimens."
    ),
    features=[
        SubclassFeature(
            name="Bonus Cantrip",
            level=3,
            description=(
                "When you choose this circle at 3rd level, you learn the "
                "Thorn Whip cantrip. This counts as a druid cantrip for you "
                "but doesn't count against your number of cantrips known."
            ),
        ),
        SubclassFeature(
            name="Verdant Growth",
            level=3,
            description=(
                "Also at 3rd level, as an action, you can expend a use of Wild "
                "Shape to cause plants to grow rapidly in a 20-foot radius around "
                "you. The area becomes difficult terrain for creatures of your "
                "choice. Additionally, you and allies in the area regain hit "
                "points equal to your druid level. The plants remain for 10 "
                "minutes or until you dismiss them."
            ),
        ),
        SubclassFeature(
            name="Rooted Defense",
            level=7,
            description=(
                "At 7th level, while you are standing on natural ground, you "
                "can use a bonus action to root yourself. Until you move, you "
                "have advantage on Strength and Constitution saving throws, and "
                "you can't be knocked prone or moved against your will. You also "
                "gain 1 Luck when you first use this feature each combat."
            ),
        ),
        SubclassFeature(
            name="Chlorophyll Surge",
            level=11,
            description=(
                "Starting at 11th level, when you cast a spell that restores hit "
                "points while in bright light or standing on natural ground, you "
                "can add your Wisdom modifier to the healing done to each target."
            ),
        ),
        SubclassFeature(
            name="Avatar of the Green",
            level=15,
            description=(
                "At 15th level, you can use Wild Shape to become a plant-like "
                "form, gaining resistance to bludgeoning, piercing, and slashing "
                "damage, immunity to poison and the poisoned condition, and the "
                "ability to move through difficult terrain made of plants without "
                "spending extra movement. This transformation lasts for 1 hour."
            ),
        ),
    ],
    ruleset="tov",
)

TOV_RING_OF_THE_SHIFTER = Subclass(
    name="Ring of the Shifter",
    parent_class="Druid",
    description=(
        "Druids of the Ring of the Shifter embrace the animal aspects of nature "
        "most fully. They spend extended periods in animal form, blurring the "
        "line between humanoid and beast. These druids often prefer the company "
        "of animals to people and view Wild Shape as their truest expression."
    ),
    features=[
        SubclassFeature(
            name="Enhanced Wild Shape",
            level=3,
            description=(
                "When you choose this circle at 3rd level, you can use Wild Shape "
                "as a bonus action. Additionally, while transformed, you can use "
                "a bonus action to expend one spell slot to regain 1d8 hit points "
                "per level of the spell slot expended."
            ),
        ),
        SubclassFeature(
            name="Beast Forms",
            level=3,
            description=(
                "At 3rd level, you can transform into beasts with a CR as high "
                "as 1 (ignoring the normal CR limitations). Starting at 6th level, "
                "you can transform into beasts with a CR as high as your druid "
                "level divided by 3, rounded down."
            ),
        ),
        SubclassFeature(
            name="Primal Strike",
            level=7,
            description=(
                "Starting at 7th level, your attacks in beast form count as "
                "magical for the purpose of overcoming resistance and immunity. "
                "Additionally, once per turn when you hit with a natural weapon "
                "attack in beast form, you can spend 1 Luck to deal extra damage "
                "equal to your Wisdom modifier."
            ),
        ),
        SubclassFeature(
            name="Elemental Forms",
            level=11,
            description=(
                "At 11th level, you can expend two uses of Wild Shape at the "
                "same time to transform into an air, earth, fire, or water "
                "elemental."
            ),
        ),
        SubclassFeature(
            name="Master Shifter",
            level=15,
            description=(
                "At 15th level, when you use Wild Shape, you can choose to gain "
                "temporary hit points equal to twice your druid level. While "
                "transformed, you can cast druid spells that don't require "
                "material components, using your beast form to perform verbal "
                "and somatic components."
            ),
        ),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - FIGHTER
# =============================================================================

TOV_SPELL_BLADE = Subclass(
    name="Spell Blade",
    parent_class="Fighter",
    description=(
        "The Spell Blade combines martial prowess with arcane study, weaving "
        "spells into their weapon techniques. Unlike traditional wizards, Spell "
        "Blades focus on magic that enhances their combat abilities, creating "
        "a seamless fusion of steel and sorcery."
    ),
    features=[
        SubclassFeature(
            name="Spellcasting",
            level=3,
            description=(
                "At 3rd level, you augment your martial prowess with arcane magic. "
                "You learn two cantrips from the wizard spell list and three "
                "1st-level wizard spells. Intelligence is your spellcasting "
                "ability. You learn additional spells as you gain fighter levels."
            ),
        ),
        SubclassFeature(
            name="Arcane Weapon",
            level=3,
            description=(
                "At 3rd level, you can bond with a weapon through a special "
                "ritual taking 1 hour. The bonded weapon counts as magical and "
                "can be used as a spellcasting focus. You can summon the weapon "
                "to your hand as a bonus action if it's on the same plane."
            ),
        ),
        SubclassFeature(
            name="War Magic",
            level=7,
            description=(
                "Beginning at 7th level, when you use your action to cast a "
                "cantrip, you can make one weapon attack as a bonus action. "
                "Additionally, you gain 1 Luck when you successfully cast a "
                "spell while wielding your bonded weapon."
            ),
        ),
        SubclassFeature(
            name="Eldritch Strike",
            level=11,
            description=(
                "At 11th level, when you hit a creature with a weapon attack, "
                "that creature has disadvantage on the next saving throw it makes "
                "against a spell you cast before the end of your next turn."
            ),
        ),
        SubclassFeature(
            name="Arcane Charge",
            level=15,
            description=(
                "At 15th level, when you use Action Surge, you can teleport up "
                "to 30 feet to an unoccupied space you can see before or after "
                "the additional action. Additionally, when you cast a spell of "
                "1st level or higher, you can make one weapon attack as part of "
                "the same action."
            ),
        ),
    ],
    ruleset="tov",
)

TOV_WEAPON_MASTER = Subclass(
    name="Weapon Master",
    parent_class="Fighter",
    description=(
        "Those who become Weapon Masters treat combat as both an art and a "
        "science. Through rigorous study and practice, they develop a repertoire "
        "of special maneuvers that give them an edge in any battle. Their "
        "techniques are passed down through martial academies and fighting guilds."
    ),
    features=[
        SubclassFeature(
            name="Combat Superiority",
            level=3,
            description=(
                "At 3rd level, you learn three maneuvers of your choice from the "
                "list of Weapon Master maneuvers. You gain four superiority dice, "
                "which are d8s. A die is expended when you use it. You regain all "
                "expended dice on a short or long rest. You learn two additional "
                "maneuvers at 7th, 11th, and 15th level."
            ),
        ),
        SubclassFeature(
            name="Student of War",
            level=3,
            description=(
                "At 3rd level, you gain proficiency with one type of artisan's "
                "tools of your choice, reflecting your study of warfare."
            ),
        ),
        SubclassFeature(
            name="Know Your Enemy",
            level=7,
            description=(
                "Starting at 7th level, if you spend at least 1 minute observing "
                "a creature outside combat, you learn if it is superior, equal, "
                "or inferior in two characteristics of your choice: Strength, "
                "Dexterity, Constitution, AC, HP, total levels, or fighter levels."
            ),
        ),
        SubclassFeature(
            name="Improved Superiority",
            level=11,
            description=(
                "At 11th level, your superiority dice become d10s. Additionally, "
                "when you roll initiative and have no superiority dice remaining, "
                "you regain one die. You also gain 1 Luck at the start of combat."
            ),
        ),
        SubclassFeature(
            name="Master's Precision",
            level=15,
            description=(
                "Starting at 15th level, your superiority dice become d12s. When "
                "you use a maneuver, you can spend 2 Luck to use a second maneuver "
                "on the same attack without expending another superiority die."
            ),
        ),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - MONK
# =============================================================================

TOV_WAY_OF_THE_IRON_FIST = Subclass(
    name="Way of the Iron Fist",
    parent_class="Monk",
    description=(
        "Monks of the Way of the Iron Fist believe that true martial perfection "
        "comes through pushing the body beyond its limits. They train to deliver "
        "devastating strikes that can shatter stone and break through any defense. "
        "Their philosophy holds that an unbreakable will creates an unbreakable body."
    ),
    features=[
        SubclassFeature(
            name="Iron Body",
            level=3,
            description=(
                "When you choose this tradition at 3rd level, your unarmed strikes "
                "can deal bludgeoning, piercing, or slashing damage (your choice "
                "each time you hit). Additionally, when you use Flurry of Blows, "
                "you can spend 1 additional ki point to make three unarmed strikes "
                "instead of two."
            ),
        ),
        SubclassFeature(
            name="Hardened Resolve",
            level=7,
            description=(
                "At 7th level, you can use your reaction when you take damage to "
                "reduce it by an amount equal to your monk level + your Wisdom "
                "modifier. You can use this feature once per short or long rest. "
                "When you do, you gain 1 Luck."
            ),
        ),
        SubclassFeature(
            name="Shattering Strike",
            level=11,
            description=(
                "Starting at 11th level, once per turn when you hit with an "
                "unarmed strike, you can spend 2 ki points to deal extra damage "
                "equal to your Martial Arts die + your Wisdom modifier. If the "
                "target is an object or construct, this damage is doubled."
            ),
        ),
        SubclassFeature(
            name="Unbreakable",
            level=15,
            description=(
                "At 15th level, you gain resistance to bludgeoning, piercing, and "
                "slashing damage from nonmagical attacks. Additionally, when you "
                "are reduced to 0 hit points but not killed outright, you can spend "
                "4 ki points to drop to 1 hit point instead."
            ),
        ),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - PALADIN
# =============================================================================

TOV_OATH_OF_JUSTICE = Subclass(
    name="Oath of Justice",
    parent_class="Paladin",
    description=(
        "The Oath of Justice binds paladins to the pursuit of fairness and the "
        "protection of the innocent. These paladins serve as judges, arbiters, "
        "and champions of the oppressed. They believe that law without mercy is "
        "tyranny, and mercy without law is weakness."
    ),
    features=[
        SubclassFeature(
            name="Oath Spells",
            level=3,
            description=(
                "You gain oath spells at the paladin levels listed: 3rd (Command, "
                "Sanctuary), 5th (Zone of Truth, Hold Person), 9th (Remove Curse, "
                "Speak with Dead), 13th (Banishment, Death Ward), 17th (Dispel "
                "Evil and Good, Geas)."
            ),
        ),
        SubclassFeature(
            name="Channel Divinity",
            level=3,
            description=(
                "At 3rd level, you gain two Channel Divinity options. Scales of "
                "Justice: As an action, choose a creature within 30 feet. It must "
                "succeed on a Wisdom save or be compelled to speak the truth for "
                "1 minute. Champion of the Weak: As a bonus action, choose an ally "
                "within 30 feet with fewer HP than you. For 1 minute, when that "
                "ally takes damage, you can use your reaction to take the damage."
            ),
        ),
        SubclassFeature(
            name="Aura of Equity",
            level=7,
            description=(
                "Starting at 7th level, you and friendly creatures within 10 feet "
                "gain a bonus to saving throws against being charmed, frightened, "
                "or having their thoughts read equal to your Charisma modifier. "
                "At 18th level, this aura extends to 30 feet."
            ),
        ),
        SubclassFeature(
            name="Righteous Judgment",
            level=11,
            description=(
                "Beginning at 11th level, when you deal radiant damage with Divine "
                "Smite to a creature that has attacked an ally since your last "
                "turn, you deal an extra 1d8 radiant damage. You also gain 1 Luck "
                "when you use Divine Smite to protect an ally."
            ),
        ),
        SubclassFeature(
            name="Avatar of Justice",
            level=15,
            description=(
                "At 15th level, as a bonus action, you can become an avatar of "
                "justice for 1 minute. You gain resistance to all damage from "
                "creatures that have dealt damage to your allies in the last "
                "minute, and your weapon attacks deal an extra 1d8 radiant damage. "
                "Once you use this feature, you can't do so again until you "
                "finish a long rest."
            ),
        ),
    ],
    subclass_spells=[
        (3, ["Command", "Sanctuary"]),
        (5, ["Zone of Truth", "Hold Person"]),
        (9, ["Remove Curse", "Speak with Dead"]),
        (13, ["Banishment", "Death Ward"]),
        (17, ["Dispel Evil and Good", "Geas"]),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - RANGER
# =============================================================================

TOV_PACK_MASTER = Subclass(
    name="Pack Master",
    parent_class="Ranger",
    description=(
        "Pack Masters form deep bonds with animal companions, leading them as "
        "the alpha of a small pack. Unlike other beast-focused traditions, Pack "
        "Masters emphasize tactical coordination, using their animal allies as "
        "extensions of their own combat prowess."
    ),
    features=[
        SubclassFeature(
            name="Animal Companion",
            level=3,
            description=(
                "At 3rd level, you gain a beast companion that fights alongside "
                "you. Choose a beast of CR 1/4 or lower. It gains proficiency in "
                "two skills, adds your proficiency bonus to its AC, attack rolls, "
                "damage rolls, and saving throws. It acts on your initiative and "
                "can take the Dash, Disengage, Dodge, or Help action, or you can "
                "use your bonus action to command it to Attack."
            ),
        ),
        SubclassFeature(
            name="Pack Tactics",
            level=7,
            description=(
                "Beginning at 7th level, you and your companion have advantage "
                "on attack rolls against a creature if the other is within 5 feet "
                "of it and isn't incapacitated. Additionally, your companion's "
                "attacks count as magical. When your companion hits, you gain 1 "
                "Luck (once per turn)."
            ),
        ),
        SubclassFeature(
            name="Bestial Fury",
            level=11,
            description=(
                "Starting at 11th level, your companion can make two attacks when "
                "you command it to take the Attack action. You can also use a "
                "bonus action to command multiple companions if you have them."
            ),
        ),
        SubclassFeature(
            name="Share Spells",
            level=15,
            description=(
                "Beginning at 15th level, when you cast a spell targeting yourself, "
                "you can also affect your companion if it's within 30 feet. "
                "Additionally, when your companion is reduced to 0 hit points, "
                "you can spend 3 Luck to have it drop to 1 hit point instead."
            ),
        ),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - ROGUE
# =============================================================================

TOV_SHADOW_DANCER = Subclass(
    name="Shadow Dancer",
    parent_class="Rogue",
    description=(
        "Shadow Dancers merge with darkness itself, learning to step between "
        "shadows and strike from impossible angles. Their training combines "
        "stealth techniques with a touch of shadow magic, making them the "
        "ultimate infiltrators and assassins."
    ),
    features=[
        SubclassFeature(
            name="Shadow Arts",
            level=3,
            description=(
                "When you choose this archetype at 3rd level, you learn the Minor "
                "Illusion cantrip if you don't already know it. You can also cast "
                "Darkness once without using a spell slot. You regain this ability "
                "after a short or long rest. Charisma is your spellcasting ability."
            ),
        ),
        SubclassFeature(
            name="Shadow Step",
            level=7,
            description=(
                "At 7th level, when you are in dim light or darkness, you can use "
                "a bonus action to teleport up to 60 feet to an unoccupied space "
                "you can see that is also in dim light or darkness. You then have "
                "advantage on the first melee attack you make before the end of "
                "the turn, and you gain 1 Luck."
            ),
        ),
        SubclassFeature(
            name="Cloak of Shadows",
            level=11,
            description=(
                "By 11th level, you can use your action to become invisible in dim "
                "light or darkness. You remain invisible until you attack, cast a "
                "spell, or enter bright light. While invisible this way, you can "
                "spend 2 Luck to extend the invisibility for 1 round after attacking."
            ),
        ),
        SubclassFeature(
            name="Shadow Strike",
            level=15,
            description=(
                "Starting at 15th level, when you hit a creature with an attack "
                "while hidden or invisible, you deal extra damage equal to half "
                "your rogue level (rounded down). If you score a critical hit "
                "while in dim light or darkness, you can teleport to an unoccupied "
                "space within 30 feet as part of the same action."
            ),
        ),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - SORCERER
# =============================================================================

TOV_STORM_SOUL = Subclass(
    name="Storm Soul",
    parent_class="Sorcerer",
    description=(
        "Your innate magic derives from the raw power of storms. Perhaps you "
        "were born during a hurricane, struck by lightning, or descended from "
        "creatures of elemental air. The tempest lives within you, and you can "
        "call upon its fury at will."
    ),
    features=[
        SubclassFeature(
            name="Wind Speaker",
            level=1,
            description=(
                "Starting at 1st level, you can speak, read, and write Primordial. "
                "You also learn the Shocking Grasp cantrip, which doesn't count "
                "against your number of cantrips known."
            ),
        ),
        SubclassFeature(
            name="Tempestuous Magic",
            level=1,
            description=(
                "Starting at 1st level, immediately before or after you cast a "
                "spell of 1st level or higher, you can use a bonus action to fly "
                "up to 10 feet without provoking opportunity attacks."
            ),
        ),
        SubclassFeature(
            name="Heart of the Storm",
            level=7,
            description=(
                "At 7th level, you gain resistance to lightning and thunder "
                "damage. Whenever you cast a spell of 1st level or higher that "
                "deals lightning or thunder damage, you deal lightning or thunder "
                "damage equal to half your sorcerer level to all creatures of your "
                "choice within 10 feet. You also gain 1 Luck when you do so."
            ),
        ),
        SubclassFeature(
            name="Storm Guide",
            level=11,
            description=(
                "At 11th level, you can subtly control the weather within 1 mile "
                "of you. You can end rain in a 20-foot radius centered on you, or "
                "cause it to rain. You can change the direction of wind in a "
                "100-foot radius. These effects last until the end of your next "
                "turn."
            ),
        ),
        SubclassFeature(
            name="Wind Soul",
            level=15,
            description=(
                "At 15th level, you gain immunity to lightning and thunder damage. "
                "You also gain a magical flying speed of 60 feet. As an action, "
                "you can grant this flying speed to up to 3 + your Charisma "
                "modifier allies within 30 feet for 1 hour. Once you grant this "
                "speed, you can't do so again until you finish a short or long rest."
            ),
        ),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - WARLOCK
# =============================================================================

TOV_THE_COSMIC_MACHINE = Subclass(
    name="The Cosmic Machine",
    parent_class="Warlock",
    description=(
        "Your patron is a vast cosmic intelligence, perhaps an ancient construct "
        "of the gods, a sentient planar mechanism, or an entity from beyond the "
        "known multiverse. It grants you power in exchange for serving as its "
        "agent in the material world, furthering purposes you may never fully "
        "comprehend."
    ),
    features=[
        SubclassFeature(
            name="Bonus Cantrips",
            level=1,
            description=(
                "At 1st level, you learn the Mending and Light cantrips. They "
                "count as warlock cantrips for you, but don't count against your "
                "number of cantrips known."
            ),
        ),
        SubclassFeature(
            name="Calculated Precision",
            level=1,
            description=(
                "Also at 1st level, when you make an attack roll or ability check, "
                "you can spend 2 Luck to treat the d20 roll as a 10. You must "
                "choose to do this before the roll."
            ),
        ),
        SubclassFeature(
            name="Clockwork Shield",
            level=7,
            description=(
                "Starting at 7th level, when you or a creature you can see within "
                "30 feet takes damage, you can use your reaction to reduce the "
                "damage by an amount equal to your warlock level + your Charisma "
                "modifier. You can use this feature once per short or long rest."
            ),
        ),
        SubclassFeature(
            name="Probability Matrix",
            level=11,
            description=(
                "At 11th level, when a creature you can see within 60 feet makes "
                "an attack roll, ability check, or saving throw, you can use your "
                "reaction to add or subtract 1d8 from the roll. You can use this "
                "feature a number of times equal to your Charisma modifier, "
                "regaining all uses on a long rest."
            ),
        ),
        SubclassFeature(
            name="Perfect Calculation",
            level=15,
            description=(
                "At 15th level, when you roll initiative, you can choose to take "
                "a result of 20 instead of rolling. Additionally, once per long "
                "rest, when you or an ally within 30 feet fails a saving throw, "
                "you can change that failure into a success."
            ),
        ),
    ],
    subclass_spells=[
        (1, ["Alarm", "Identify"]),
        (3, ["Arcane Lock", "Heat Metal"]),
        (5, ["Lightning Bolt", "Protection from Energy"]),
        (7, ["Fabricate", "Resilient Sphere"]),
        (9, ["Animate Objects", "Wall of Force"]),
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT SUBCLASSES - WIZARD
# =============================================================================

TOV_SCHOOL_OF_WAR_MAGIC = Subclass(
    name="School of War Magic",
    parent_class="Wizard",
    description=(
        "Wizards of the School of War Magic focus on spells that aid in battle, "
        "combining defensive techniques with offensive power. Many serve as "
        "military advisors, battle mages, or personal protectors to rulers and "
        "generals. They understand that magic is the ultimate force multiplier."
    ),
    features=[
        SubclassFeature(
            name="Arcane Deflection",
            level=3,
            description=(
                "At 3rd level, when you are hit by an attack or fail a saving "
                "throw, you can use your reaction to gain a +2 bonus to AC against "
                "that attack or a +4 bonus to the saving throw. When you use this "
                "feature, you can't cast spells other than cantrips until the end "
                "of your next turn. You gain 1 Luck when you use this feature."
            ),
        ),
        SubclassFeature(
            name="Tactical Wit",
            level=3,
            description=(
                "Starting at 3rd level, you can add your Intelligence modifier to "
                "your initiative rolls."
            ),
        ),
        SubclassFeature(
            name="Power Surge",
            level=7,
            description=(
                "Starting at 7th level, you can store magical energy within "
                "yourself. You have a number of power surges equal to your "
                "Intelligence modifier. When you deal damage with a wizard spell, "
                "you can spend one power surge to deal extra force damage equal "
                "to half your wizard level. You regain one power surge when you "
                "successfully counter a spell or dispel a magical effect."
            ),
        ),
        SubclassFeature(
            name="Durable Magic",
            level=11,
            description=(
                "Beginning at 11th level, while you maintain concentration on a "
                "spell, you have a +2 bonus to AC and all saving throws."
            ),
        ),
        SubclassFeature(
            name="Deflecting Shroud",
            level=15,
            description=(
                "At 15th level, when you use your Arcane Deflection feature, you "
                "can cause magical energy to arc from you. Up to three creatures "
                "of your choice within 60 feet of you each take force damage "
                "equal to half your wizard level."
            ),
        ),
    ],
    ruleset="tov",
)


# =============================================================================
# COLLECTIONS
# =============================================================================

# Tales of the Valiant Subclasses
TOV_SUBCLASSES: list[Subclass] = [
    TOV_WILD_FURY,
    TOV_COLLEGE_OF_VICTORY,
    TOV_RING_OF_THE_LEAF,
    TOV_RING_OF_THE_SHIFTER,
    TOV_SPELL_BLADE,
    TOV_WEAPON_MASTER,
    TOV_WAY_OF_THE_IRON_FIST,
    TOV_OATH_OF_JUSTICE,
    TOV_PACK_MASTER,
    TOV_SHADOW_DANCER,
    TOV_STORM_SOUL,
    TOV_THE_COSMIC_MACHINE,
    TOV_SCHOOL_OF_WAR_MAGIC,
]

# D&D 2014 Subclasses
DND_2014_SUBCLASSES: list[Subclass] = [
    # Original 2014 subclasses (marked with ruleset="dnd2014")
    BERSERKER,
    COLLEGE_OF_LORE,
    LIFE_DOMAIN,
    CIRCLE_OF_THE_LAND,
    CHAMPION,
    WAY_OF_THE_OPEN_HAND,
    OATH_OF_DEVOTION,
    HUNTER,
    THIEF,
    DRACONIC_BLOODLINE,
    THE_FIEND,
    SCHOOL_OF_EVOCATION,
    # Additional subclasses (ruleset=None, works for all)
    TOTEM_WARRIOR,
    WILD_MAGIC_BARBARIAN,
    COLLEGE_OF_VALOR,
    COLLEGE_OF_SWORDS,
    LIGHT_DOMAIN,
    WAR_DOMAIN,
    CIRCLE_OF_THE_MOON,
    CIRCLE_OF_SPORES,
    BATTLE_MASTER,
    ELDRITCH_KNIGHT,
    WAY_OF_SHADOW,
    WAY_OF_FOUR_ELEMENTS,
    OATH_OF_THE_ANCIENTS,
    OATH_OF_VENGEANCE,
    BEAST_MASTER,
    GLOOM_STALKER,
    ASSASSIN,
    ARCANE_TRICKSTER,
    WILD_MAGIC_SORCERER,
    SHADOW_MAGIC,
    THE_GREAT_OLD_ONE,
    THE_CELESTIAL,
    SCHOOL_OF_ABJURATION,
    SCHOOL_OF_DIVINATION,
]

# D&D 2024 Revised Subclasses
DND_2024_SUBCLASSES: list[Subclass] = [
    BERSERKER_2024,
    COLLEGE_OF_LORE_2024,
    LIFE_DOMAIN_2024,
    CIRCLE_OF_THE_LAND_2024,
    CHAMPION_2024,
    WAY_OF_THE_OPEN_HAND_2024,
    OATH_OF_DEVOTION_2024,
    HUNTER_2024,
    THIEF_2024,
    DRACONIC_BLOODLINE_2024,
    THE_FIEND_2024,
    SCHOOL_OF_EVOCATION_2024,
]

# All D&D Subclasses (both 2014 and 2024)
DND_SUBCLASSES: list[Subclass] = DND_2014_SUBCLASSES + DND_2024_SUBCLASSES

ALL_SUBCLASSES: list[Subclass] = DND_SUBCLASSES + TOV_SUBCLASSES

# Dictionary for quick lookup
_SUBCLASSES_BY_NAME: dict[str, Subclass] = {
    subclass.name.lower(): subclass for subclass in ALL_SUBCLASSES
}

_SUBCLASSES_BY_CLASS: dict[str, list[Subclass]] = {}
for subclass in ALL_SUBCLASSES:
    parent = subclass.parent_class.lower()
    if parent not in _SUBCLASSES_BY_CLASS:
        _SUBCLASSES_BY_CLASS[parent] = []
    _SUBCLASSES_BY_CLASS[parent].append(subclass)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_subclass(name: str) -> Optional[Subclass]:
    """Get a subclass by name (case-insensitive)."""
    return _SUBCLASSES_BY_NAME.get(name.lower())


def get_subclasses_for_class(class_name: str) -> list[Subclass]:
    """Get all subclasses for a given parent class."""
    return _SUBCLASSES_BY_CLASS.get(class_name.lower(), [])


def get_all_subclass_names() -> list[str]:
    """Get a list of all subclass names."""
    return [subclass.name for subclass in ALL_SUBCLASSES]


def get_subclass_features_at_level(subclass: Subclass, level: int) -> list[SubclassFeature]:
    """Get all features a subclass grants at a specific level."""
    return [f for f in subclass.features if f.level == level]


def get_subclass_features_up_to_level(
    subclass: Subclass, level: int
) -> list[SubclassFeature]:
    """Get all features a subclass grants up to and including a specific level."""
    return [f for f in subclass.features if f.level <= level]


def search_subclasses(query: str) -> list[Subclass]:
    """Search subclasses by name or description."""
    query_lower = query.lower()
    results = []
    for subclass in ALL_SUBCLASSES:
        if (
            query_lower in subclass.name.lower()
            or query_lower in subclass.description.lower()
        ):
            results.append(subclass)
    return results


# =============================================================================
# TOV SUBCLASS HELPER FUNCTIONS
# =============================================================================


def get_tov_subclasses() -> list[Subclass]:
    """Get all Tales of the Valiant subclasses."""
    return TOV_SUBCLASSES.copy()


def get_tov_subclasses_for_class(class_name: str) -> list[Subclass]:
    """Get all ToV subclasses for a given parent class."""
    return [
        s for s in TOV_SUBCLASSES
        if s.parent_class.lower() == class_name.lower()
    ]


def get_subclasses_for_ruleset(ruleset: Optional[str] = None) -> list[Subclass]:
    """Get subclasses appropriate for a specific ruleset.

    Args:
        ruleset: The ruleset ID ('dnd2014', 'dnd2024', 'tov', or None for all)

    Returns:
        List of subclasses available for the ruleset. ToV returns only ToV
        subclasses. For D&D rulesets, returns subclasses matching that ruleset
        or with ruleset=None (universal). None returns all subclasses.
    """
    if ruleset is None:
        return ALL_SUBCLASSES.copy()
    elif ruleset == "tov":
        return TOV_SUBCLASSES.copy()
    elif ruleset == "dnd2024":
        # Return 2024 versions + subclasses without version-specific differences
        return [s for s in DND_SUBCLASSES if s.ruleset in ("dnd2024", None)]
    else:
        # dnd2014 - Return 2014 versions + subclasses without version-specific differences
        return [s for s in DND_SUBCLASSES if s.ruleset in ("dnd2014", None)]


def get_subclasses_for_class_and_ruleset(
    class_name: str,
    ruleset: Optional[str] = None
) -> list[Subclass]:
    """Get subclasses for a class filtered by ruleset.

    Args:
        class_name: The parent class name
        ruleset: The ruleset ID ('dnd2014', 'dnd2024', 'tov', or None for all)

    Returns:
        List of subclasses for the class and ruleset.
    """
    all_for_class = get_subclasses_for_class(class_name)
    if ruleset is None:
        return all_for_class
    elif ruleset == "tov":
        return [s for s in all_for_class if s.ruleset == "tov"]
    elif ruleset == "dnd2024":
        return [s for s in all_for_class if s.ruleset in ("dnd2024", None)]
    else:
        # dnd2014
        return [s for s in all_for_class if s.ruleset in ("dnd2014", None)]


# =============================================================================
# SPELL VALIDATION FUNCTIONS
# =============================================================================


def validate_subclass_spells(subclass: Subclass) -> list[tuple[int, str]]:
    """Validate that all spells in a subclass exist in the spell database.

    Args:
        subclass: The subclass to validate

    Returns:
        List of (level, spell_name) tuples for spells that don't exist.
    """
    if not subclass.subclass_spells:
        return []

    # Import here to avoid circular imports
    from dnd_manager.data.spells import get_spell_by_name

    missing = []
    for level, spells in subclass.subclass_spells:
        for spell_name in spells:
            spell = get_spell_by_name(spell_name)
            if spell is None:
                missing.append((level, spell_name))
    return missing


def validate_all_subclass_spells() -> dict[str, list[tuple[int, str]]]:
    """Validate spells for all subclasses.

    Returns:
        Dictionary mapping subclass name to list of missing spells.
        Only subclasses with missing spells are included.
    """
    errors = {}
    for subclass in ALL_SUBCLASSES:
        missing = validate_subclass_spells(subclass)
        if missing:
            errors[subclass.name] = missing
    return errors


def get_subclass_spells_at_level(subclass: Subclass, level: int) -> list[str]:
    """Get spells granted by a subclass at a specific level.

    Args:
        subclass: The subclass to check
        level: The level to check for

    Returns:
        List of spell names granted at that level.
    """
    for spell_level, spells in subclass.subclass_spells:
        if spell_level == level:
            return spells.copy()
    return []


def get_subclass_spells_up_to_level(subclass: Subclass, level: int) -> list[str]:
    """Get all spells granted by a subclass up to and including a level.

    Args:
        subclass: The subclass to check
        level: The maximum level to include

    Returns:
        List of all spell names granted up to that level.
    """
    spells = []
    for spell_level, spell_list in subclass.subclass_spells:
        if spell_level <= level:
            spells.extend(spell_list)
    return spells
