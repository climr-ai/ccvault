"""Feats data for D&D character options.

Contains origin feats (background-granted) and general feats with original
flavor text and accurate SRD mechanics.
"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from dnd_manager.data.prerequisites import Prerequisite

# Import prerequisites for runtime use (lazy import to avoid circular imports)
def _get_prereqs():
    """Lazy import prerequisites to avoid circular imports."""
    from dnd_manager.data.prerequisites import (
        Prerequisite,
        AbilityRequirement,
        ProficiencyRequirement,
        ProficiencyType,
        SpellcastingRequirement,
        LevelRequirement,
        combine_prereqs,
        ability_prereq,
        proficiency_prereq,
        spellcasting_prereq,
        level_prereq,
    )
    return {
        'Prerequisite': Prerequisite,
        'AbilityRequirement': AbilityRequirement,
        'ProficiencyRequirement': ProficiencyRequirement,
        'ProficiencyType': ProficiencyType,
        'SpellcastingRequirement': SpellcastingRequirement,
        'LevelRequirement': LevelRequirement,
        'combine_prereqs': combine_prereqs,
        'ability_prereq': ability_prereq,
        'proficiency_prereq': proficiency_prereq,
        'spellcasting_prereq': spellcasting_prereq,
        'level_prereq': level_prereq,
    }


@dataclass
class Feat:
    """Represents a feat that grants special abilities or bonuses.

    For ToV Talents, category should be one of:
    - "tov_martial": Combat-focused talents
    - "tov_magic": Spellcasting and mind-focused talents
    - "tov_technical": Utility, social, and exploration talents

    Prerequisites can be specified in two ways:
    - prerequisites: List of human-readable strings (for display)
    - structured_prereq: Prerequisite object (for validation)

    If structured_prereq is provided, it will be used for validation.
    Otherwise, the system falls back to parsing the prerequisites strings.
    """

    name: str
    description: str
    category: str  # "origin", "general", "fighting_style", "epic_boon", "tov_martial", "tov_magic", "tov_technical"
    prerequisites: list[str] = field(default_factory=list)
    benefits: list[str] = field(default_factory=list)
    ability_increase: Optional[dict[str, int]] = None
    repeatable: bool = False
    ruleset: Optional[str] = None  # None = all rulesets, "tov" = Tales of the Valiant only
    structured_prereq: Optional["Prerequisite"] = None  # Structured prerequisite for validation


# =============================================================================
# ORIGIN FEATS (Granted by backgrounds at 1st level)
# =============================================================================

ALERT = Feat(
    name="Alert",
    description=(
        "Your keen senses and battle-honed instincts keep you constantly aware "
        "of threats. You've trained yourself to react to danger before others "
        "even realize it exists, making you nearly impossible to catch off guard."
    ),
    category="origin",
    benefits=[
        "You gain a +5 bonus to initiative.",
        "You can't be surprised while you are conscious.",
        "Other creatures don't gain advantage on attack rolls against you as "
        "a result of being unseen by you.",
    ],
)

CRAFTER = Feat(
    name="Crafter",
    description=(
        "You possess a knack for creating things with your hands. Whether "
        "forging weapons, brewing potions, or crafting mundane goods, your "
        "skill allows you to work faster and more efficiently than most."
    ),
    category="origin",
    benefits=[
        "You gain proficiency with three artisan's tools of your choice.",
        "When you craft an item using artisan's tools, the required crafting "
        "time is reduced by 20%.",
        "When you buy a nonmagical item, you pay 75% of the normal price.",
    ],
)

HEALER = Feat(
    name="Healer",
    description=(
        "You have studied the arts of medicine and first aid, learning to "
        "treat wounds and ailments with practiced efficiency. Your ministrations "
        "can restore allies to fighting shape when conventional magic isn't available."
    ),
    category="origin",
    benefits=[
        "You gain proficiency in the Medicine skill. If already proficient, "
        "you gain expertise (double proficiency bonus).",
        "Using a healer's kit, you can spend one action to tend to a creature "
        "and restore 1d6 + 4 hit points, plus additional hit points equal to "
        "the creature's maximum number of Hit Dice. A creature can only benefit "
        "from this once per short or long rest.",
        "Using a healer's kit, you can stabilize a dying creature as a bonus action.",
    ],
)

LUCKY = Feat(
    name="Lucky",
    description=(
        "Fortune seems to smile upon you at the most opportune moments. Whether "
        "through divine favor, cosmic chance, or sheer pluck, you can twist fate "
        "in your favor when it matters most."
    ),
    category="origin",
    benefits=[
        "You have 3 luck points. Whenever you make an attack roll, ability check, "
        "or saving throw, you can spend one luck point to roll an additional d20.",
        "You can choose to spend one of your luck points after you roll the die, "
        "but before the outcome is determined. You choose which of the d20s is "
        "used for the attack roll, ability check, or saving throw.",
        "You can also spend one luck point when an attack roll is made against you. "
        "Roll a d20, and then choose whether the attack uses the attacker's roll "
        "or yours.",
        "If more than one creature spends a luck point on the same roll, they "
        "cancel out, resulting in no additional dice.",
        "You regain your expended luck points when you finish a long rest.",
    ],
)

MAGIC_INITIATE = Feat(
    name="Magic Initiate",
    description=(
        "You have begun to unlock magical potential, learning the fundamentals "
        "of spellcasting through study, natural talent, or supernatural blessing. "
        "This initial mastery opens the door to greater magical achievements."
    ),
    category="origin",
    benefits=[
        "Choose a class: bard, cleric, druid, sorcerer, warlock, or wizard.",
        "You learn two cantrips of your choice from that class's spell list.",
        "You learn one 1st-level spell of your choice from that class's spell list. "
        "You can cast this spell once without expending a spell slot, and you regain "
        "the ability to do so when you finish a long rest.",
        "Your spellcasting ability for these spells depends on the class you chose: "
        "Charisma for bard, sorcerer, or warlock; Wisdom for cleric or druid; "
        "Intelligence for wizard.",
    ],
    repeatable=True,
)

# Magic Initiate class-specific variants (for backgrounds that grant a specific version)
MAGIC_INITIATE_BARD = Feat(
    name="Magic Initiate (Bard)",
    description=(
        "You have begun to unlock magical potential through the bardic tradition. "
        "Your study of music and lore has granted you access to arcane secrets."
    ),
    category="origin",
    benefits=[
        "You learn two cantrips of your choice from the bard spell list.",
        "You learn one 1st-level spell of your choice from the bard spell list. "
        "You can cast this spell once without expending a spell slot, and you regain "
        "the ability to do so when you finish a long rest.",
        "Charisma is your spellcasting ability for these spells.",
    ],
)

MAGIC_INITIATE_CLERIC = Feat(
    name="Magic Initiate (Cleric)",
    description=(
        "You have begun to unlock divine magical potential through faith and devotion. "
        "Your connection to the divine grants you access to sacred magic."
    ),
    category="origin",
    benefits=[
        "You learn two cantrips of your choice from the cleric spell list.",
        "You learn one 1st-level spell of your choice from the cleric spell list. "
        "You can cast this spell once without expending a spell slot, and you regain "
        "the ability to do so when you finish a long rest.",
        "Wisdom is your spellcasting ability for these spells.",
    ],
)

MAGIC_INITIATE_DRUID = Feat(
    name="Magic Initiate (Druid)",
    description=(
        "You have begun to unlock primal magical potential through your connection "
        "to nature. The natural world shares its secrets with you."
    ),
    category="origin",
    benefits=[
        "You learn two cantrips of your choice from the druid spell list.",
        "You learn one 1st-level spell of your choice from the druid spell list. "
        "You can cast this spell once without expending a spell slot, and you regain "
        "the ability to do so when you finish a long rest.",
        "Wisdom is your spellcasting ability for these spells.",
    ],
)

MAGIC_INITIATE_SORCERER = Feat(
    name="Magic Initiate (Sorcerer)",
    description=(
        "You have begun to unlock innate magical potential that flows through your "
        "bloodline. Raw arcane power responds to your will."
    ),
    category="origin",
    benefits=[
        "You learn two cantrips of your choice from the sorcerer spell list.",
        "You learn one 1st-level spell of your choice from the sorcerer spell list. "
        "You can cast this spell once without expending a spell slot, and you regain "
        "the ability to do so when you finish a long rest.",
        "Charisma is your spellcasting ability for these spells.",
    ],
)

MAGIC_INITIATE_WARLOCK = Feat(
    name="Magic Initiate (Warlock)",
    description=(
        "You have begun to unlock eldritch magical potential through a pact with "
        "an otherworldly entity. Dark secrets have been whispered to you."
    ),
    category="origin",
    benefits=[
        "You learn two cantrips of your choice from the warlock spell list.",
        "You learn one 1st-level spell of your choice from the warlock spell list. "
        "You can cast this spell once without expending a spell slot, and you regain "
        "the ability to do so when you finish a long rest.",
        "Charisma is your spellcasting ability for these spells.",
    ],
)

MAGIC_INITIATE_WIZARD = Feat(
    name="Magic Initiate (Wizard)",
    description=(
        "You have begun to unlock arcane magical potential through scholarly study. "
        "Ancient tomes and careful research have revealed magical formulas to you."
    ),
    category="origin",
    benefits=[
        "You learn two cantrips of your choice from the wizard spell list.",
        "You learn one 1st-level spell of your choice from the wizard spell list. "
        "You can cast this spell once without expending a spell slot, and you regain "
        "the ability to do so when you finish a long rest.",
        "Intelligence is your spellcasting ability for these spells.",
    ],
)

MUSICIAN = Feat(
    name="Musician",
    description=(
        "Your musical talents extend beyond mere entertainment. Through practice "
        "and passion, you've learned to use music to inspire allies and lift "
        "spirits even in the darkest circumstances."
    ),
    category="origin",
    benefits=[
        "You gain proficiency with three musical instruments of your choice.",
        "After you finish a short or long rest, you can play a song of restoration. "
        "Choose up to a number of allies equal to your proficiency bonus who can "
        "hear you. Each chosen creature regains an extra Hit Die, which can be "
        "spent immediately or saved.",
    ],
)

SAVAGE_ATTACKER = Feat(
    name="Savage Attacker",
    description=(
        "Your strikes carry devastating force. You've trained to deliver "
        "crushing blows that maximize the damage of every hit, turning "
        "glancing wounds into grievous injuries."
    ),
    category="origin",
    benefits=[
        "Once per turn when you hit a creature with a weapon attack, you can "
        "roll the weapon's damage dice twice and use either total.",
    ],
)

SKILLED = Feat(
    name="Skilled",
    description=(
        "You have a natural aptitude for picking up new abilities. Your diverse "
        "experiences and quick learning allow you to gain competence in areas "
        "that others spend years mastering."
    ),
    category="origin",
    benefits=[
        "You gain proficiency in any combination of three skills or tools of "
        "your choice.",
    ],
    repeatable=True,
)

TAVERN_BRAWLER = Feat(
    name="Tavern Brawler",
    description=(
        "Countless bar fights and street scuffles have taught you to fight with "
        "whatever's at hand. You've become adept at improvised combat, turning "
        "chairs, bottles, and even your bare fists into deadly weapons."
    ),
    category="origin",
    benefits=[
        "You are proficient with improvised weapons.",
        "Your unarmed strike uses a d4 for damage.",
        "When you hit a creature with an unarmed strike or an improvised weapon "
        "on your turn, you can use a bonus action to attempt to grapple the target.",
    ],
)

TOUGH = Feat(
    name="Tough",
    description=(
        "Your body has been hardened through rigorous training, harsh conditions, "
        "or sheer stubborn resilience. You can withstand punishment that would "
        "fell lesser individuals."
    ),
    category="origin",
    benefits=[
        "Your hit point maximum increases by an amount equal to twice your level "
        "when you gain this feat. Whenever you gain a level thereafter, your hit "
        "point maximum increases by an additional 2 hit points.",
    ],
)

# =============================================================================
# GENERAL FEATS (Available at ASI levels)
# =============================================================================

ACTOR = Feat(
    name="Actor",
    description=(
        "You have mastered the art of deception and performance. Your ability "
        "to mimic others and adopt personas makes you a skilled infiltrator "
        "and convincing liar."
    ),
    category="general",
    benefits=[
        "Increase your Charisma score by 1, to a maximum of 20.",
        "You have advantage on Charisma (Deception) and Charisma (Performance) "
        "checks when trying to pass yourself off as a different person.",
        "You can mimic the speech of another person or the sounds made by other "
        "creatures. You must have heard the person speaking, or heard the creature "
        "make the sound, for at least 1 minute. A successful Wisdom (Insight) check "
        "contested by your Charisma (Deception) check allows a listener to determine "
        "that the effect is faked.",
    ],
    ability_increase={"Charisma": 1},
)

ATHLETE = Feat(
    name="Athlete",
    description=(
        "Intensive physical training has made your body a finely tuned instrument. "
        "You move with the grace of an acrobat and the power of a warrior, "
        "excelling at physical feats that challenge ordinary individuals."
    ),
    category="general",
    benefits=[
        "Increase your Strength or Dexterity score by 1, to a maximum of 20.",
        "When you are prone, standing up uses only 5 feet of your movement.",
        "Climbing doesn't cost you extra movement.",
        "You can make a running long jump or a running high jump after moving "
        "only 5 feet on foot, rather than 10 feet.",
    ],
    ability_increase={"Strength or Dexterity": 1},
)

CHARGER = Feat(
    name="Charger",
    description=(
        "You have learned to build momentum into devastating attacks. When you "
        "rush headlong into battle, your strikes carry the full force of your "
        "charge behind them."
    ),
    category="general",
    ruleset="dnd2014",
    benefits=[
        "When you use your action to Dash, you can use a bonus action to make "
        "one melee weapon attack or to shove a creature.",
        "If you move at least 10 feet in a straight line immediately before "
        "taking this bonus action, you either gain a +5 bonus to the attack's "
        "damage roll (if you chose to make a melee attack) or push the target "
        "up to 10 feet away from you (if you chose to shove).",
    ],
)

CROSSBOW_EXPERT = Feat(
    name="Crossbow Expert",
    description=(
        "Through extensive practice with crossbows, you've mastered techniques "
        "that allow for rapid reloading and close-quarters accuracy. Your "
        "proficiency with these weapons rivals that of any archer."
    ),
    category="general",
    ruleset="dnd2014",
    benefits=[
        "You ignore the loading quality of crossbows with which you are proficient.",
        "Being within 5 feet of a hostile creature doesn't impose disadvantage "
        "on your ranged attack rolls.",
        "When you use the Attack action and attack with a one-handed weapon, you "
        "can use a bonus action to attack with a hand crossbow you are holding.",
    ],
)

DEFENSIVE_DUELIST = Feat(
    name="Defensive Duelist",
    description=(
        "Your training in finesse weapons has taught you to use them not just "
        "for attack, but for defense as well. You can deflect incoming blows "
        "with quick, precise movements."
    ),
    category="general",
    prerequisites=["Dexterity 13 or higher"],
    benefits=[
        "When you are wielding a finesse weapon with which you are proficient "
        "and another creature hits you with a melee attack, you can use your "
        "reaction to add your proficiency bonus to your AC for that attack, "
        "potentially causing the attack to miss you.",
    ],
)

DUAL_WIELDER = Feat(
    name="Dual Wielder",
    description=(
        "Fighting with a weapon in each hand has become second nature to you. "
        "You've mastered the coordination required to wield two weapons "
        "simultaneously, even larger ones than most can manage."
    ),
    category="general",
    ruleset="dnd2014",
    benefits=[
        "You gain a +1 bonus to AC while you are wielding a separate melee "
        "weapon in each hand.",
        "You can use two-weapon fighting even when the one-handed melee weapons "
        "you are wielding aren't light.",
        "You can draw or stow two one-handed weapons when you would normally "
        "be able to draw or stow only one.",
    ],
)

DUNGEON_DELVER = Feat(
    name="Dungeon Delver",
    description=(
        "Years of exploring dark corridors and ancient ruins have honed your "
        "senses for danger. You've learned to spot traps, find hidden passages, "
        "and avoid the countless perils that lurk in underground places."
    ),
    category="general",
    benefits=[
        "You have advantage on Wisdom (Perception) and Intelligence (Investigation) "
        "checks made to detect the presence of secret doors.",
        "You have advantage on saving throws made to avoid or resist traps.",
        "You have resistance to the damage dealt by traps.",
        "Traveling at a fast pace doesn't impose the normal -5 penalty on your "
        "passive Wisdom (Perception) score.",
    ],
)

DURABLE = Feat(
    name="Durable",
    description=(
        "Your constitution is remarkably resilient. You recover from injuries "
        "faster than most and can push through exhaustion that would debilitate "
        "others."
    ),
    category="general",
    benefits=[
        "Increase your Constitution score by 1, to a maximum of 20.",
        "When you roll a Hit Die to regain hit points, the minimum number of "
        "hit points you regain equals twice your Constitution modifier "
        "(minimum of 2).",
    ],
    ability_increase={"Constitution": 1},
)

ELEMENTAL_ADEPT = Feat(
    name="Elemental Adept",
    description=(
        "Your mastery of a particular element allows you to overcome the natural "
        "resistances of creatures and maximize the destructive potential of "
        "your elemental magic."
    ),
    category="general",
    prerequisites=["The ability to cast at least one spell"],
    benefits=[
        "Choose one of the following damage types: acid, cold, fire, lightning, "
        "or thunder.",
        "Spells you cast ignore resistance to damage of the chosen type.",
        "When you roll damage for a spell you cast that deals damage of that type, "
        "you can treat any 1 on a damage die as a 2.",
    ],
    repeatable=True,
)

GRAPPLER = Feat(
    name="Grappler",
    description=(
        "You've developed powerful techniques for wrestling and restraining "
        "opponents. Once you have hold of a foe, they find it nearly impossible "
        "to escape your iron grip."
    ),
    category="general",
    prerequisites=["Strength 13 or higher"],
    benefits=[
        "You have advantage on attack rolls against a creature you are grappling.",
        "You can use your action to try to pin a creature grappled by you. To do so, "
        "make another grapple check. If you succeed, you and the creature are both "
        "restrained until the grapple ends.",
    ],
)

GREAT_WEAPON_MASTER = Feat(
    name="Great Weapon Master",
    description=(
        "You've learned to put the full weight of your massive weapons into "
        "devastating swings. Your attacks with heavy weapons can cleave through "
        "enemies or deliver punishing blows at the cost of precision."
    ),
    category="general",
    ruleset="dnd2014",
    benefits=[
        "On your turn, when you score a critical hit with a melee weapon or "
        "reduce a creature to 0 hit points with one, you can make one melee "
        "weapon attack as a bonus action.",
        "Before you make a melee attack with a heavy weapon that you are "
        "proficient with, you can choose to take a -5 penalty to the attack roll. "
        "If the attack hits, you add +10 to the attack's damage.",
    ],
)

HEAVY_ARMOR_MASTER = Feat(
    name="Heavy Armor Master",
    description=(
        "Your training in heavy armor has taught you to use its weight and "
        "coverage to deflect blows that would otherwise wound you. Lesser "
        "attacks simply glance off your armored form."
    ),
    category="general",
    prerequisites=["Proficiency with heavy armor"],
    benefits=[
        "Increase your Strength score by 1, to a maximum of 20.",
        "While you are wearing heavy armor, bludgeoning, piercing, and slashing "
        "damage that you take from nonmagical weapons is reduced by 3.",
    ],
    ability_increase={"Strength": 1},
)

INSPIRING_LEADER = Feat(
    name="Inspiring Leader",
    description=(
        "Your words carry the power to steel hearts and bolster resolve. With "
        "a rousing speech, you can prepare your allies to face overwhelming "
        "odds with renewed courage."
    ),
    category="general",
    prerequisites=["Charisma 13 or higher"],
    benefits=[
        "You can spend 10 minutes inspiring your companions, shoring up their "
        "resolve to fight. When you do so, choose up to six friendly creatures "
        "(which can include yourself) within 30 feet of you who can see or hear "
        "you and who can understand you.",
        "Each creature gains temporary hit points equal to your level + your "
        "Charisma modifier. A creature can't gain temporary hit points from "
        "this feat again until it has finished a short or long rest.",
    ],
)

KEEN_MIND = Feat(
    name="Keen Mind",
    description=(
        "Your mind is a steel trap that captures and retains information with "
        "remarkable clarity. Details that others forget remain fresh in your "
        "memory, making you an invaluable source of knowledge."
    ),
    category="general",
    benefits=[
        "Increase your Intelligence score by 1, to a maximum of 20.",
        "You always know which way is north.",
        "You always know the number of hours left before the next sunrise or sunset.",
        "You can accurately recall anything you have seen or heard within the "
        "past month.",
    ],
    ability_increase={"Intelligence": 1},
)

LINGUIST = Feat(
    name="Linguist",
    description=(
        "You have a gift for languages, able to pick up new tongues with ease "
        "and create codes that baffle those who try to decipher them. Your "
        "linguistic expertise extends to both spoken and written communication."
    ),
    category="general",
    benefits=[
        "Increase your Intelligence score by 1, to a maximum of 20.",
        "You learn three languages of your choice.",
        "You can create written ciphers. Others can't decipher a code you create "
        "unless you teach them, they succeed on an Intelligence check (DC equal "
        "to your Intelligence score + your proficiency bonus), or they use magic "
        "to decipher it.",
    ],
    ability_increase={"Intelligence": 1},
)

MAGE_SLAYER = Feat(
    name="Mage Slayer",
    description=(
        "You have practiced techniques for fighting spellcasters. When magic "
        "users threaten you or your allies, you know exactly how to disrupt "
        "their concentration and punish them for their arcane audacity."
    ),
    category="general",
    benefits=[
        "When a creature within 5 feet of you casts a spell, you can use your "
        "reaction to make a melee weapon attack against that creature.",
        "When you damage a creature that is concentrating on a spell, that "
        "creature has disadvantage on the saving throw it makes to maintain "
        "its concentration.",
        "You have advantage on saving throws against spells cast by creatures "
        "within 5 feet of you.",
    ],
)

MEDIUM_ARMOR_MASTER = Feat(
    name="Medium Armor Master",
    description=(
        "You have perfected your use of medium armor, learning to move silently "
        "and make the most of its protective qualities without sacrificing "
        "agility."
    ),
    category="general",
    prerequisites=["Proficiency with medium armor"],
    benefits=[
        "Wearing medium armor doesn't impose disadvantage on your Dexterity "
        "(Stealth) checks.",
        "When you wear medium armor, you can add 3, rather than 2, to your AC "
        "if you have a Dexterity of 16 or higher.",
    ],
)

MOBILE = Feat(
    name="Mobile",
    description=(
        "Your speed and agility are exceptional. You dart across battlefields "
        "with ease, slipping past enemies and difficult terrain that would "
        "slow others down."
    ),
    category="general",
    benefits=[
        "Your speed increases by 10 feet.",
        "When you use the Dash action, difficult terrain doesn't cost you "
        "extra movement on that turn.",
        "When you make a melee attack against a creature, you don't provoke "
        "opportunity attacks from that creature for the rest of the turn, "
        "whether you hit or not.",
    ],
)

MOUNTED_COMBATANT = Feat(
    name="Mounted Combatant",
    description=(
        "You are a dangerous foe while mounted. Your bond with your steed "
        "allows you to fight as one, protecting your mount while delivering "
        "devastating attacks from above."
    ),
    category="general",
    benefits=[
        "You have advantage on melee attack rolls against any unmounted creature "
        "that is smaller than your mount.",
        "You can force an attack targeted at your mount to target you instead.",
        "If your mount is subjected to an effect that allows it to make a Dexterity "
        "saving throw to take only half damage, it instead takes no damage if it "
        "succeeds on the saving throw, and only half damage if it fails.",
    ],
)

OBSERVANT = Feat(
    name="Observant",
    description=(
        "Sharp eyes and quick wits let you notice things that others miss. "
        "You're adept at reading lips, spotting hidden details, and picking "
        "up on subtle environmental cues."
    ),
    category="general",
    benefits=[
        "Increase your Intelligence or Wisdom score by 1, to a maximum of 20.",
        "If you can see a creature's mouth while it is speaking a language you "
        "understand, you can interpret what it's saying by reading its lips.",
        "You have a +5 bonus to your passive Wisdom (Perception) and passive "
        "Intelligence (Investigation) scores.",
    ],
    ability_increase={"Intelligence or Wisdom": 1},
)

POLEARM_MASTER = Feat(
    name="Polearm Master",
    description=(
        "You have mastered the art of fighting with polearms, using their "
        "reach and versatility to control the battlefield and punish enemies "
        "who dare approach you."
    ),
    category="general",
    ruleset="dnd2014",
    benefits=[
        "When you take the Attack action and attack with only a glaive, halberd, "
        "quarterstaff, or spear, you can use a bonus action to make a melee attack "
        "with the opposite end of the weapon. This attack uses the same ability "
        "modifier as the primary attack. The weapon's damage die for this attack "
        "is a d4, and it deals bludgeoning damage.",
        "While you are wielding a glaive, halberd, pike, quarterstaff, or spear, "
        "other creatures provoke an opportunity attack from you when they enter "
        "the reach you have with that weapon.",
    ],
)

RESILIENT = Feat(
    name="Resilient",
    description=(
        "You have trained to strengthen a particular aspect of your being. "
        "Whether through mental discipline or physical conditioning, you've "
        "become more resistant to effects that target your weaknesses."
    ),
    category="general",
    benefits=[
        "Increase one ability score of your choice by 1, to a maximum of 20.",
        "You gain proficiency in saving throws using the chosen ability.",
    ],
    ability_increase={"Any": 1},
    repeatable=True,
)

RITUAL_CASTER = Feat(
    name="Ritual Caster",
    description=(
        "You have learned to perform certain spells as rituals. Your ritual "
        "book contains the secrets to casting powerful magic without expending "
        "precious spell slots."
    ),
    category="general",
    prerequisites=["Intelligence or Wisdom 13 or higher"],
    benefits=[
        "Choose one class: bard, cleric, druid, sorcerer, warlock, or wizard. "
        "You must have an Intelligence or Wisdom score of 13 or higher to take "
        "this feat (depending on class).",
        "You acquire a ritual book holding two 1st-level spells of your choice "
        "from the chosen class's spell list. The spells must have the ritual tag.",
        "You can cast the spells in your ritual book as rituals. You can't cast "
        "the spells except as rituals, unless you've learned them by some other means.",
        "When you find a spell with the ritual tag on your adventures, you can "
        "add it to your ritual book if the spell is on the spell list of the class "
        "you chose and if the spell's level is no higher than half your level "
        "(rounded up). The process takes 2 hours per level of the spell and costs "
        "50 gp per level.",
    ],
)

SENTINEL = Feat(
    name="Sentinel",
    description=(
        "You have mastered techniques to take advantage of every opportunity "
        "in combat. Your vigilance and quick reactions make it dangerous for "
        "enemies to ignore you or flee from your reach."
    ),
    category="general",
    ruleset="dnd2014",
    benefits=[
        "When you hit a creature with an opportunity attack, the creature's speed "
        "becomes 0 for the rest of the turn.",
        "Creatures provoke opportunity attacks from you even if they take the "
        "Disengage action before leaving your reach.",
        "When a creature within 5 feet of you makes an attack against a target "
        "other than you (and that target doesn't have this feat), you can use "
        "your reaction to make a melee weapon attack against the attacking creature.",
    ],
)

SHARPSHOOTER = Feat(
    name="Sharpshooter",
    description=(
        "Your aim with ranged weapons is legendary. You can make shots that "
        "seem impossible, striking distant targets and ignoring cover that "
        "would protect them from lesser archers."
    ),
    category="general",
    ruleset="dnd2014",
    benefits=[
        "Attacking at long range doesn't impose disadvantage on your ranged "
        "weapon attack rolls.",
        "Your ranged weapon attacks ignore half cover and three-quarters cover.",
        "Before you make an attack with a ranged weapon that you are proficient "
        "with, you can choose to take a -5 penalty to the attack roll. If the "
        "attack hits, you add +10 to the attack's damage.",
    ],
)

SHIELD_MASTER = Feat(
    name="Shield Master",
    description=(
        "You use shields not just for defense, but as weapons and tools for "
        "battlefield control. Your mastery allows you to deflect spells and "
        "knock enemies off balance."
    ),
    category="general",
    benefits=[
        "If you take the Attack action on your turn, you can use a bonus action "
        "to try to shove a creature within 5 feet of you with your shield.",
        "If you aren't incapacitated, you can add your shield's AC bonus to any "
        "Dexterity saving throw you make against a spell or other harmful effect "
        "that targets only you.",
        "If you are subjected to an effect that allows you to make a Dexterity "
        "saving throw to take only half damage, you can use your reaction to take "
        "no damage if you succeed on the saving throw, interposing your shield "
        "between yourself and the source of the effect.",
    ],
)

SKULKER = Feat(
    name="Skulker",
    description=(
        "You are expert at slinking through shadows and hiding from enemies. "
        "Even when your attacks miss, you can remain concealed, and dim light "
        "provides no obstacle to your keen eyes."
    ),
    category="general",
    prerequisites=["Dexterity 13 or higher"],
    benefits=[
        "You can try to hide when you are lightly obscured from the creature "
        "from which you are hiding.",
        "When you are hidden from a creature and miss it with a ranged weapon "
        "attack, making the attack doesn't reveal your position.",
        "Dim light doesn't impose disadvantage on your Wisdom (Perception) "
        "checks relying on sight.",
    ],
)

SPELL_SNIPER = Feat(
    name="Spell Sniper",
    description=(
        "Your practice with ranged spells has made you especially deadly at "
        "distance. Your attack spells reach farther and pierce defenses that "
        "would block other casters."
    ),
    category="general",
    prerequisites=["The ability to cast at least one spell"],
    benefits=[
        "When you cast a spell that requires you to make an attack roll, the "
        "spell's range is doubled.",
        "Your ranged spell attacks ignore half cover and three-quarters cover.",
        "You learn one cantrip that requires an attack roll. Choose the cantrip "
        "from the bard, cleric, druid, sorcerer, warlock, or wizard spell list. "
        "Your spellcasting ability for this cantrip depends on the spell list "
        "you chose from.",
    ],
)

WAR_CASTER = Feat(
    name="War Caster",
    description=(
        "You have practiced casting spells in the midst of combat, learning "
        "techniques that grant you concentration even amid chaos and the ability "
        "to respond to threats with magic rather than steel."
    ),
    category="general",
    prerequisites=["The ability to cast at least one spell"],
    benefits=[
        "You have advantage on Constitution saving throws that you make to "
        "maintain your concentration on a spell when you take damage.",
        "You can perform the somatic components of spells even when you have "
        "weapons or a shield in one or both hands.",
        "When a hostile creature's movement provokes an opportunity attack from "
        "you, you can use your reaction to cast a spell at the creature, rather "
        "than making an opportunity attack. The spell must have a casting time "
        "of 1 action and must target only that creature.",
    ],
)

WEAPON_MASTER = Feat(
    name="Weapon Master",
    description=(
        "Extensive training has granted you familiarity with a variety of "
        "weapons. You've practiced with arms both common and exotic until "
        "you can wield them with confidence."
    ),
    category="general",
    benefits=[
        "Increase your Strength or Dexterity score by 1, to a maximum of 20.",
        "You gain proficiency with four weapons of your choice. Each one must "
        "be a simple or a martial weapon.",
    ],
    ability_increase={"Strength or Dexterity": 1},
)


# =============================================================================
# TASHA'S CAULDRON FEATS (Original Descriptions)
# =============================================================================

FEY_TOUCHED = Feat(
    name="Fey Touched",
    description=(
        "Contact with the fey realm has left its mark on you, granting minor "
        "magical abilities tied to that mysterious plane."
    ),
    category="general",
    benefits=[
        "Increase Intelligence, Wisdom, or Charisma by 1 (max 20).",
        "Learn Misty Step and one 1st-level Divination or Enchantment spell.",
        "Cast each once per long rest without a slot, or use available slots.",
    ],
    ability_increase={"Intelligence, Wisdom, or Charisma": 1},
)

SHADOW_TOUCHED = Feat(
    name="Shadow Touched",
    description=(
        "Exposure to shadow magic has granted you abilities tied to darkness "
        "and the realm of shadows."
    ),
    category="general",
    benefits=[
        "Increase Intelligence, Wisdom, or Charisma by 1 (max 20).",
        "Learn Invisibility and one 1st-level Illusion or Necromancy spell.",
        "Cast each once per long rest without a slot, or use available slots.",
    ],
    ability_increase={"Intelligence, Wisdom, or Charisma": 1},
)

SKILL_EXPERT = Feat(
    name="Skill Expert",
    description=(
        "Dedicated practice has made you exceptionally skilled in a particular area."
    ),
    category="general",
    benefits=[
        "Increase one ability score by 1 (max 20).",
        "Gain proficiency in one skill.",
        "Gain expertise in one skill you're proficient with (double proficiency bonus).",
    ],
    ability_increase={"Any": 1},
)

TELEKINETIC = Feat(
    name="Telekinetic",
    description=(
        "You have developed minor telekinetic abilities through training or innate talent."
    ),
    category="general",
    benefits=[
        "Increase Intelligence, Wisdom, or Charisma by 1 (max 20).",
        "Learn Mage Hand (can be invisible, no components needed).",
        "Bonus action: shove creature within 30 ft 5 feet (Strength save negates).",
    ],
    ability_increase={"Intelligence, Wisdom, or Charisma": 1},
)

TELEPATHIC = Feat(
    name="Telepathic",
    description=(
        "You have awakened latent mental abilities allowing communication without speech."
    ),
    category="general",
    benefits=[
        "Increase Intelligence, Wisdom, or Charisma by 1 (max 20).",
        "Telepathically speak to creatures within 60 ft that share a language.",
        "Cast Detect Thoughts once per long rest without components or slots.",
    ],
    ability_increase={"Intelligence, Wisdom, or Charisma": 1},
)

CRUSHER = Feat(
    name="Crusher",
    description=(
        "Training with bludgeoning weapons lets you knock foes off balance."
    ),
    category="general",
    benefits=[
        "Increase Strength or Constitution by 1 (max 20).",
        "Once per turn, move a hit target 5 ft (if no more than one size larger).",
        "Critical hits grant advantage on attacks against target until your next turn.",
    ],
    ability_increase={"Strength or Constitution": 1},
)

SLASHER = Feat(
    name="Slasher",
    description=(
        "Expertise with slashing weapons allows you to hinder your enemies."
    ),
    category="general",
    benefits=[
        "Increase Strength or Dexterity by 1 (max 20).",
        "Once per turn, reduce hit target's speed by 10 ft until your next turn.",
        "Critical hits impose disadvantage on target's attacks until your next turn.",
    ],
    ability_increase={"Strength or Dexterity": 1},
)

PIERCER = Feat(
    name="Piercer",
    description=(
        "Precision with piercing weapons lets you strike vital points."
    ),
    category="general",
    benefits=[
        "Increase Strength or Dexterity by 1 (max 20).",
        "Once per turn, reroll one piercing damage die (must use new roll).",
        "Critical hits add one extra damage die.",
    ],
    ability_increase={"Strength or Dexterity": 1},
)

METAMAGIC_ADEPT = Feat(
    name="Metamagic Adept",
    description=(
        "Study of arcane theory has taught you to modify your spells."
    ),
    category="general",
    prerequisites=["Spellcasting or Pact Magic feature"],
    benefits=[
        "Learn two Metamagic options from the sorcerer class.",
        "Gain 2 sorcery points for Metamagic only (regain on long rest).",
    ],
)

ELDRITCH_ADEPT = Feat(
    name="Eldritch Adept",
    description=(
        "Occult study has unlocked eldritch secrets within you."
    ),
    category="general",
    prerequisites=["Spellcasting or Pact Magic feature"],
    benefits=[
        "Learn one Eldritch Invocation from the warlock class.",
        "Can swap invocation when you gain a level.",
        "Prerequisites apply only if you are a warlock.",
    ],
)

FIGHTING_INITIATE = Feat(
    name="Fighting Initiate",
    description=(
        "Martial training has taught you a specific combat technique."
    ),
    category="general",
    prerequisites=["Proficiency with a martial weapon"],
    benefits=[
        "Learn one Fighting Style from the fighter class.",
        "Can swap style at ASI levels.",
    ],
)

CHEF = Feat(
    name="Chef",
    description=(
        "Culinary expertise allows you to prepare restorative meals."
    ),
    category="general",
    benefits=[
        "Increase Constitution or Wisdom by 1 (max 20).",
        "Gain proficiency with cook's utensils.",
        "Short rest: creatures eating your food regain extra 1d8 HP when spending Hit Dice.",
        "Long rest: create treats (prof bonus) granting temp HP equal to prof bonus.",
    ],
    ability_increase={"Constitution or Wisdom": 1},
)

GUNNER = Feat(
    name="Gunner",
    description=(
        "Training with firearms has made you quick and accurate."
    ),
    category="general",
    benefits=[
        "Increase Dexterity by 1 (max 20).",
        "Gain proficiency with firearms.",
        "Ignore loading property of firearms.",
        "No disadvantage on ranged attacks with hostile creatures within 5 ft.",
    ],
    ability_increase={"Dexterity": 1},
)

POISONER = Feat(
    name="Poisoner",
    description=(
        "You have mastered the creation and application of toxins."
    ),
    category="general",
    benefits=[
        "Poison damage you deal ignores resistance.",
        "Apply poison as bonus action instead of action.",
        "Gain poisoner's kit proficiency; can craft potent poison (2d8 damage, DC 14).",
    ],
)

GIFT_OF_THE_CHROMATIC_DRAGON = Feat(
    name="Gift of the Chromatic Dragon",
    description=(
        "Draconic power of the chromatic variety flows through you."
    ),
    category="general",
    benefits=[
        "Bonus action: infuse weapon with acid/cold/fire/lightning/poison for +1d4 damage (1 min, 1/long rest).",
        "Reaction: gain resistance to one instance of those damage types (prof bonus/long rest).",
    ],
)

GIFT_OF_THE_METALLIC_DRAGON = Feat(
    name="Gift of the Metallic Dragon",
    description=(
        "Draconic power of the metallic variety flows through you."
    ),
    category="general",
    benefits=[
        "Learn Cure Wounds; cast once per long rest without slot or use available slots.",
        "Reaction: manifest wings to add d4 to AC against one attack (prof bonus/long rest).",
    ],
)

GIFT_OF_THE_GEM_DRAGON = Feat(
    name="Gift of the Gem Dragon",
    description=(
        "Draconic power of the gem variety flows through you."
    ),
    category="general",
    benefits=[
        "Increase Intelligence, Wisdom, or Charisma by 1 (max 20).",
        "Reaction when damaged: 2d8 force damage and push attacker 10 ft (Str save, prof bonus/long rest).",
    ],
    ability_increase={"Intelligence, Wisdom, or Charisma": 1},
)


# =============================================================================
# 2024 REVISED FEATS
# =============================================================================

# The 2024 Player's Handbook revised several feats with updated mechanics.
# These versions are marked with ruleset="dnd2024" while the original 2014
# versions remain for backwards compatibility.

GREAT_WEAPON_MASTER_2024 = Feat(
    name="Great Weapon Master",
    description=(
        "You've learned to leverage the weight and heft of heavy weapons for "
        "maximum impact. Your mastery allows you to deliver devastating blows "
        "that cleave through enemies with terrifying efficiency."
    ),
    category="general",
    prerequisites=["Strength 13 or higher", "Proficiency with any martial weapon"],
    ruleset="dnd2024",
    benefits=[
        "Increase your Strength score by 1, to a maximum of 20.",
        "On your turn, when you score a critical hit with a melee weapon or "
        "reduce a creature to 0 hit points with one, you can make one melee "
        "weapon attack as a Bonus Action.",
        "When you hit a creature with a weapon that has the Heavy property, you "
        "can deal extra damage to the target equal to your Proficiency Bonus.",
    ],
    ability_increase={"Strength": 1},
)

SHARPSHOOTER_2024 = Feat(
    name="Sharpshooter",
    description=(
        "Your aim with ranged weapons is precise and deadly. You've trained to "
        "make shots that seem impossible, striking distant targets and ignoring "
        "obstacles that would shield them from lesser marksmen."
    ),
    category="general",
    prerequisites=["Dexterity 13 or higher", "Proficiency with any martial weapon"],
    ruleset="dnd2024",
    benefits=[
        "Increase your Dexterity score by 1, to a maximum of 20.",
        "Attacking at long range doesn't impose disadvantage on your ranged "
        "weapon attack rolls.",
        "Your ranged weapon attacks ignore half cover and three-quarters cover.",
        "When you hit a creature with a ranged attack roll using a weapon, you "
        "can deal extra damage to the target equal to your Proficiency Bonus.",
    ],
    ability_increase={"Dexterity": 1},
)

POLEARM_MASTER_2024 = Feat(
    name="Polearm Master",
    description=(
        "You have mastered fighting with weapons that have extended reach. Your "
        "expertise allows you to control space on the battlefield and punish any "
        "who dare to approach you."
    ),
    category="general",
    prerequisites=["Strength or Dexterity 13 or higher", "Proficiency with any martial weapon"],
    ruleset="dnd2024",
    benefits=[
        "Increase your Strength or Dexterity score by 1, to a maximum of 20.",
        "When you take the Attack action and attack with a Glaive, Halberd, "
        "Quarterstaff, or Spear, you can use a Bonus Action to make a melee "
        "attack with the opposite end of the weapon. This attack uses the same "
        "ability modifier as the primary attack. The weapon's damage die for this "
        "attack is a d4, and it deals Bludgeoning damage.",
        "While you are wielding a Glaive, Halberd, Pike, Quarterstaff, or Spear, "
        "other creatures provoke an Opportunity Attack from you when they enter "
        "the reach you have with that weapon.",
    ],
    ability_increase={"Strength or Dexterity": 1},
)

SENTINEL_2024 = Feat(
    name="Sentinel",
    description=(
        "Your combat awareness allows you to capitalize on every opening. Your "
        "vigilance and quick reactions make it dangerous for enemies to focus on "
        "your allies or attempt to flee from combat."
    ),
    category="general",
    prerequisites=["Strength or Dexterity 13 or higher", "Proficiency with any martial weapon"],
    ruleset="dnd2024",
    benefits=[
        "Increase your Strength or Dexterity score by 1, to a maximum of 20.",
        "When you hit a creature with an Opportunity Attack, the creature's speed "
        "becomes 0 for the rest of the turn. This stops any movement they may "
        "have been taking.",
        "Creatures within 5 feet of you provoke Opportunity Attacks from you even "
        "if they take the Disengage action.",
        "When a creature within 5 feet of you makes an attack roll against a target "
        "other than you, you can take a Reaction to make a melee attack roll against "
        "the attacking creature.",
    ],
    ability_increase={"Strength or Dexterity": 1},
)

CROSSBOW_EXPERT_2024 = Feat(
    name="Crossbow Expert",
    description=(
        "You've mastered the use of crossbows, learning techniques that allow "
        "you to fire with impressive speed and accuracy even at point-blank range."
    ),
    category="general",
    prerequisites=["Dexterity 13 or higher", "Proficiency with any martial weapon"],
    ruleset="dnd2024",
    benefits=[
        "Increase your Dexterity score by 1, to a maximum of 20.",
        "You ignore the Loading property of crossbows with which you have proficiency.",
        "Being within 5 feet of an enemy doesn't impose disadvantage on your attack "
        "rolls with ranged weapons.",
        "When you make the extra attack of the Light weapon property, you can add "
        "your ability modifier to the damage of that attack if you're using a "
        "hand crossbow.",
    ],
    ability_increase={"Dexterity": 1},
)

DUAL_WIELDER_2024 = Feat(
    name="Dual Wielder",
    description=(
        "You have mastered fighting with two weapons, allowing you to wield "
        "larger weapons in both hands and gain defensive benefits from your "
        "dual-weapon fighting style."
    ),
    category="general",
    prerequisites=["Strength or Dexterity 13 or higher", "Proficiency with any martial weapon"],
    ruleset="dnd2024",
    benefits=[
        "Increase your Strength or Dexterity score by 1, to a maximum of 20.",
        "When you take the Attack action and attack with a weapon that has the "
        "Light property, you can make one extra attack as a Bonus Action later "
        "on the same turn with a different weapon that also has the Light property. "
        "You don't add your ability modifier to the extra attack's damage unless "
        "that modifier is negative.",
        "You can use Two-Weapon Fighting even when the weapons you are wielding "
        "aren't Light.",
    ],
    ability_increase={"Strength or Dexterity": 1},
)

CHARGER_2024 = Feat(
    name="Charger",
    description=(
        "You've learned to use your momentum in combat, turning a running charge "
        "into devastating attacks that knock foes off balance."
    ),
    category="general",
    prerequisites=["Strength or Dexterity 13 or higher", "Proficiency with any martial weapon"],
    ruleset="dnd2024",
    benefits=[
        "Increase your Strength or Dexterity score by 1, to a maximum of 20.",
        "When you take the Dash action on your turn and move at least 10 feet "
        "in a straight line immediately before hitting with a melee attack, you "
        "gain one of the following effects of your choice: deal 1d8 extra damage "
        "with the attack, or push the target up to 10 feet in a straight line "
        "if it's no more than one size larger than you.",
    ],
    ability_increase={"Strength or Dexterity": 1},
)


# =============================================================================
# TALES OF THE VALIANT TALENTS - MARTIAL
# =============================================================================

CRITICAL_TRAINING = Feat(
    name="Critical Training",
    description=(
        "Your combat training has honed your ability to strike vital points "
        "with devastating precision. When you land a critical blow, your "
        "strikes carry significantly more force than others."
    ),
    category="tov_martial",
    benefits=[
        "You score a critical hit on a d20 roll of 19 or 20 when attacking with a weapon.",
        "When you score a critical hit with a weapon attack, you add your ability "
        "modifier to the damage an additional time.",
    ],
    ruleset="tov",
)

PHYSICAL_FORTITUDE = Feat(
    name="Physical Fortitude",
    description=(
        "Your body has been hardened against physical ailments and effects "
        "that would debilitate lesser warriors. You can push through pain "
        "and adversity with sheer determination."
    ),
    category="tov_martial",
    benefits=[
        "When you fail a Strength or Constitution saving throw, you can expend one "
        "Hit Die to reroll. You must use the new roll. You can use this ability "
        "once per turn.",
        "When you start your turn while blinded, deafened, restrained, or poisoned, "
        "you gain 1 Luck.",
        "You have advantage on ability checks and saving throws to avoid being "
        "knocked prone, pulled, or pushed.",
    ],
    ruleset="tov",
)

HEAVY_WEAPONS_MASTERY = Feat(
    name="Heavy Weapons Mastery",
    description=(
        "You have mastered the art of wielding massive weapons, turning their "
        "weight and momentum into devastating attacks. Your strikes with heavy "
        "weapons can cleave through defenses and resistances."
    ),
    category="tov_martial",
    prerequisites=["Character 4th Level or Higher"],
    benefits=[
        "When you score a critical hit while wielding a melee weapon with the "
        "Heavy property in two hands, you can make one additional melee weapon "
        "attack as part of the same action.",
        "While wielding a melee weapon with the Heavy property in two hands, "
        "you can use a bonus action to choose one of the following: ignore "
        "damage resistance for your weapon attacks this turn, OR take a -5 "
        "penalty to your attack roll to add half your Strength modifier (rounded "
        "down) to the damage if the attack hits.",
    ],
    ruleset="tov",
)

RETURN_FIRE = Feat(
    name="Return Fire",
    description=(
        "You have trained to respond instantly to ranged attacks, turning "
        "defense into offense. When missiles fly your way, you can retaliate "
        "with your own projectile in the same breath."
    ),
    category="tov_martial",
    benefits=[
        "When you are hit or missed by a ranged attack from a creature you can "
        "see, you can use your reaction to make a single weapon attack with a "
        "ranged or thrown weapon against that creature.",
    ],
    ruleset="tov",
)

COMBAT_CONDITIONING = Feat(
    name="Combat Conditioning",
    description=(
        "Rigorous physical training has increased your endurance and resilience "
        "in battle. Your conditioning allows you to withstand punishment that "
        "would fell less dedicated warriors."
    ),
    category="tov_martial",
    benefits=[
        "Your hit point maximum increases by an amount equal to your level when "
        "you gain this talent. Whenever you gain a level thereafter, your hit "
        "point maximum increases by 1 additional hit point.",
        "You gain proficiency in Constitution saving throws. If you already have "
        "this proficiency, you gain proficiency in Strength saving throws instead.",
    ],
    ruleset="tov",
)

HARD_TARGET = Feat(
    name="Hard Target",
    description=(
        "You have trained to avoid attacks through constant movement and "
        "awareness. Your defensive instincts make you difficult to hit, "
        "especially when you can see your attackers coming."
    ),
    category="tov_martial",
    benefits=[
        "You gain proficiency in Constitution saving throws. If you already have "
        "this proficiency, you gain proficiency in Dexterity saving throws instead.",
        "When you can see your attacker, you can use your reaction when hit by "
        "an attack to add your proficiency bonus to your AC against that attack, "
        "potentially causing it to miss.",
    ],
    ruleset="tov",
)

DUAL_STRIKER = Feat(
    name="Dual Striker",
    description=(
        "Fighting with a weapon in each hand has become second nature to you. "
        "Your coordinated strikes flow together seamlessly, allowing you to "
        "attack with both weapons more effectively."
    ),
    category="tov_martial",
    benefits=[
        "You gain a +1 bonus to AC while wielding a separate melee weapon in "
        "each hand.",
        "You can use two-weapon fighting even when the one-handed melee weapons "
        "you are wielding aren't light.",
        "When you take the Attack action while wielding two weapons, you can make "
        "an additional attack with your off-hand weapon as part of that action "
        "instead of as a bonus action.",
    ],
    ruleset="tov",
)

SHIELD_EXPERTISE = Feat(
    name="Shield Expertise",
    description=(
        "Your shield is not merely a defensive tool but an extension of your "
        "fighting style. You can use it to deflect magical effects and create "
        "openings in your opponents' defenses."
    ),
    category="tov_martial",
    benefits=[
        "When you take the Attack action, you can use a bonus action to shove "
        "a creature within 5 feet with your shield.",
        "You can add your shield's AC bonus to Dexterity saving throws against "
        "effects that target only you.",
        "If you succeed on a Dexterity saving throw against an effect that deals "
        "half damage on a success, you can use your reaction to take no damage, "
        "interposing your shield between yourself and the effect.",
    ],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT TALENTS - MAGIC
# =============================================================================

ELEMENTAL_SAVANT = Feat(
    name="Elemental Savant",
    description=(
        "Your study of elemental magic has granted you mastery over a specific "
        "type of energy. You can channel other spells through this elemental "
        "lens, converting their damage type to match your specialty."
    ),
    category="tov_magic",
    benefits=[
        "Choose one damage type: acid, cold, fire, lightning, or thunder. When "
        "you cast a spell that deals damage, you can convert the damage type to "
        "your chosen elemental damage type.",
        "When you roll damage for a spell that deals your chosen damage type, "
        "you can reroll any 1s on the damage dice. You must use the new roll.",
    ],
    repeatable=True,
    ruleset="tov",
)

FOCUS_FEY = Feat(
    name="Focus (Fey)",
    description=(
        "You have attuned your magic to the otherworldly realm of the fey, "
        "gaining insights into enchantment and illusion magic. The capricious "
        "nature of fey magic sometimes preserves your magical reserves."
    ),
    category="tov_magic",
    benefits=[
        "When you expend a spell slot to cast an enchantment or illusion spell "
        "of 1st circle or higher, roll a d6. On a roll of 6, the spell slot "
        "isn't expended.",
        "You learn one enchantment or illusion spell of a level you can cast. "
        "You can cast this spell by expending Hit Dice equal to the spell's "
        "level instead of a spell slot, once per long rest.",
        "You can have only one Focus talent at a time.",
    ],
    prerequisites=["The ability to cast at least one spell"],
    ruleset="tov",
)

FOCUS_ARCANE = Feat(
    name="Focus (Arcane)",
    description=(
        "You have dedicated yourself to the study of pure arcane energy, "
        "specializing in abjuration and transmutation magic. Your understanding "
        "of magical fundamentals occasionally preserves your spell slots."
    ),
    category="tov_magic",
    benefits=[
        "When you expend a spell slot to cast an abjuration or transmutation "
        "spell of 1st circle or higher, roll a d6. On a roll of 6, the spell "
        "slot isn't expended.",
        "You learn one abjuration or transmutation spell of a level you can cast. "
        "You can cast this spell by expending Hit Dice equal to the spell's "
        "level instead of a spell slot, once per long rest.",
        "You can have only one Focus talent at a time.",
    ],
    prerequisites=["The ability to cast at least one spell"],
    ruleset="tov",
)

FOCUS_DIVINE = Feat(
    name="Focus (Divine)",
    description=(
        "Your connection to divine power enhances your ability to channel "
        "restorative and protective magic. Your faith occasionally preserves "
        "your magical reserves when casting certain spells."
    ),
    category="tov_magic",
    benefits=[
        "When you expend a spell slot to cast a spell that restores hit points "
        "or grants temporary hit points, roll a d6. On a roll of 6, the spell "
        "slot isn't expended.",
        "You learn one spell from the cleric or paladin spell list of a level "
        "you can cast. You can cast this spell by expending Hit Dice equal to "
        "the spell's level instead of a spell slot, once per long rest.",
        "You can have only one Focus talent at a time.",
    ],
    prerequisites=["The ability to cast at least one spell"],
    ruleset="tov",
)

FOCUS_PRIMAL = Feat(
    name="Focus (Primal)",
    description=(
        "You have attuned yourself to the raw power of nature, enhancing your "
        "ability to cast conjuration and evocation magic. Nature's bounty "
        "occasionally preserves your magical reserves."
    ),
    category="tov_magic",
    benefits=[
        "When you expend a spell slot to cast a conjuration or evocation spell "
        "of 1st circle or higher, roll a d6. On a roll of 6, the spell slot "
        "isn't expended.",
        "You learn one conjuration or evocation spell of a level you can cast. "
        "You can cast this spell by expending Hit Dice equal to the spell's "
        "level instead of a spell slot, once per long rest.",
        "You can have only one Focus talent at a time.",
    ],
    prerequisites=["The ability to cast at least one spell"],
    ruleset="tov",
)

FOCUS_SHADOW = Feat(
    name="Focus (Shadow)",
    description=(
        "You have embraced the magic of darkness and death, specializing in "
        "necromancy and shadow magic. The darkness occasionally preserves "
        "your magical reserves when casting sinister spells."
    ),
    category="tov_magic",
    benefits=[
        "When you expend a spell slot to cast a necromancy spell of 1st circle "
        "or higher, roll a d6. On a roll of 6, the spell slot isn't expended.",
        "You learn one necromancy spell of a level you can cast. You can cast "
        "this spell by expending Hit Dice equal to the spell's level instead "
        "of a spell slot, once per long rest.",
        "You have darkvision out to 60 feet. If you already have darkvision, "
        "its range increases by 30 feet.",
        "You can have only one Focus talent at a time.",
    ],
    prerequisites=["The ability to cast at least one spell"],
    ruleset="tov",
)

SPELL_DUELIST = Feat(
    name="Spell Duelist",
    description=(
        "You have trained to use magic in direct confrontation with other "
        "spellcasters. Your reflexes allow you to respond to magical attacks "
        "with your own spells, and your attack spells strike with precision."
    ),
    category="tov_magic",
    benefits=[
        "When you take damage from a spell cast by an enemy, you can use your "
        "reaction to cast a cantrip that targets the creature who damaged you.",
        "When you cast a spell that requires an attack roll, double the spell's "
        "range. Touch spells gain a range of 15 feet.",
        "Your ranged spell attacks ignore AC bonuses granted by cover.",
    ],
    prerequisites=["The ability to cast at least one spell"],
    ruleset="tov",
)

TOUCH_OF_LUCK = Feat(
    name="Touch of Luck",
    description=(
        "Fortune seems to favor you even in your failures. Your misfortunes "
        "fuel your luck, building reserves of good fortune that can be "
        "called upon when you need them most."
    ),
    category="tov_magic",
    benefits=[
        "When you fail an attack roll or saving throw, you gain 2 Luck.",
        "When you already have 5 Luck and would gain more, roll 1d4+1. If the "
        "result is higher than 5, your Luck becomes that value instead of "
        "being wasted.",
        "You can spend 2 Luck to reroll a failed ability check.",
    ],
    ruleset="tov",
)

BOTTOMLESS_LUCK = Feat(
    name="Bottomless Luck",
    description=(
        "Your incredible fortune spills over to benefit those around you. "
        "When fate truly smiles upon you, your allies share in your good "
        "fortune."
    ),
    category="tov_magic",
    benefits=[
        "When you roll a natural 20 on a d20 roll, one ally you can see within "
        "30 feet gains 1 Luck.",
        "Your maximum Luck increases by 2.",
        "When you finish a long rest, you gain Luck equal to half your "
        "proficiency bonus (rounded down).",
    ],
    ruleset="tov",
)

MENTAL_FORTRESS = Feat(
    name="Mental Fortress",
    description=(
        "Your mind has been fortified against magical intrusion and psychic "
        "assault. You can maintain concentration even under tremendous "
        "pressure and resist effects that target your intellect."
    ),
    category="tov_magic",
    benefits=[
        "You have advantage on Intelligence, Wisdom, and Charisma saving throws "
        "against spells and other magical effects.",
        "You have advantage on Constitution saving throws to maintain concentration "
        "on spells when you take damage.",
    ],
    prerequisites=["The ability to cast at least one spell"],
    ruleset="tov",
)


# =============================================================================
# TALES OF THE VALIANT TALENTS - TECHNICAL
# =============================================================================

COMRADE = Feat(
    name="Comrade",
    description=(
        "You excel at supporting your allies and working as part of a team. "
        "Your presence bolsters your companions, and witnessing their struggles "
        "fuels your determination to help them succeed."
    ),
    category="tov_technical",
    benefits=[
        "You can use the Help action as a bonus action on each of your turns.",
        "When an ally you can see or hear within 30 feet of you spends one or "
        "more Luck, you can also spend Luck to increase their roll.",
        "When an ally within 30 feet of you is reduced to 0 HP or fails a death "
        "saving throw, you gain 2 Luck.",
    ],
    ruleset="tov",
)

COVERT = Feat(
    name="Covert",
    description=(
        "You have mastered the art of stealth and concealment. You can hide "
        "in conditions others would find impossible and remain undetected even "
        "by those with supernatural senses."
    ),
    category="tov_technical",
    benefits=[
        "You can attempt to hide while in three-quarters cover or when lightly "
        "obscured.",
        "While you remain motionless in dim light or darkness, you are invisible "
        "to creatures relying on darkvision to see you.",
        "You don't have disadvantage on attack rolls or Wisdom (Perception) checks "
        "against targets in dim light.",
        "When a creature spots you while you are hidden, you can use your reaction "
        "to make a Dexterity (Stealth) check with disadvantage. If you succeed, "
        "you remain hidden. You can do this once per creature per 24 hours.",
    ],
    ruleset="tov",
)

FIELD_MEDIC = Feat(
    name="Field Medic",
    description=(
        "You have extensive training in emergency medical care. Your knowledge "
        "of anatomy and treatment allows you to stabilize the wounded and tend "
        "to injuries with remarkable efficiency."
    ),
    category="tov_technical",
    benefits=[
        "When you make a Wisdom (Medicine) check, treat any d20 roll of 9 or "
        "lower as a 10.",
        "As an action, you can tend to a creature within 5 feet and restore "
        "hit points equal to your proficiency bonus + your Constitution modifier. "
        "A creature can benefit from this only once per short or long rest.",
        "When you spend Hit Dice during a short rest, you can reroll a number "
        "of those dice equal to your proficiency bonus.",
    ],
    ruleset="tov",
)

AWARE = Feat(
    name="Aware",
    description=(
        "Your senses are finely tuned to detect danger before others even "
        "realize it exists. You react to threats with lightning speed and "
        "are nearly impossible to catch off guard."
    ),
    category="tov_technical",
    benefits=[
        "You gain a +5 bonus to initiative rolls.",
        "You can't be surprised while you are conscious.",
        "Other creatures don't gain advantage on attack rolls against you as "
        "a result of being unseen by you.",
    ],
    ruleset="tov",
)

POLYGLOT = Feat(
    name="Polyglot",
    description=(
        "You have an extraordinary gift for languages, picking up new tongues "
        "with remarkable ease. Your linguistic talents extend to understanding "
        "even unfamiliar languages through context and patterns."
    ),
    category="tov_technical",
    benefits=[
        "You learn three languages of your choice.",
        "You can communicate basic ideas with any creature that has a language, "
        "even if you don't share a language, by spending 10 minutes observing "
        "and interacting with it.",
        "You have advantage on Intelligence checks to decipher codes, ciphers, "
        "and ancient languages.",
    ],
    ruleset="tov",
)

SKILLED_TALENT = Feat(
    name="Skilled",
    description=(
        "You have a natural aptitude for learning new abilities. Your diverse "
        "experiences and quick study allow you to gain competence in areas "
        "that others take much longer to master."
    ),
    category="tov_technical",
    benefits=[
        "You gain proficiency in any combination of three skills or tools of "
        "your choice.",
    ],
    repeatable=True,
    ruleset="tov",
)

JACK_OF_ALL_TRADES_TALENT = Feat(
    name="Jack of All Trades",
    description=(
        "You have dabbled in countless disciplines, gaining a breadth of "
        "knowledge that helps in almost any situation. Your varied experience "
        "provides a baseline competence in nearly everything."
    ),
    category="tov_technical",
    benefits=[
        "You can add half your proficiency bonus (rounded down) to any ability "
        "check you make that doesn't already include your proficiency bonus.",
        "You gain proficiency with one skill and one tool of your choice.",
    ],
    ruleset="tov",
)

SOCIAL_EXPERTISE = Feat(
    name="Social Expertise",
    description=(
        "You have honed your interpersonal skills to a fine edge. Whether "
        "through charm, intimidation, or keen insight, you excel at reading "
        "people and influencing their behavior."
    ),
    category="tov_technical",
    benefits=[
        "You gain proficiency in one of the following skills: Deception, Insight, "
        "Intimidation, Performance, or Persuasion. If you are already proficient, "
        "you gain expertise in that skill.",
        "When you make a Charisma check against a creature, you can spend 1 Luck "
        "to gain advantage on the check.",
        "You can use your action to analyze a creature you can see within 30 feet. "
        "Make a Wisdom (Insight) check contested by the creature's Charisma "
        "(Deception). On a success, you learn its emotional state and whether "
        "it is being truthful.",
    ],
    ruleset="tov",
)

DUNGEON_EXPERT = Feat(
    name="Dungeon Expert",
    description=(
        "Years of delving into dangerous places have sharpened your instincts "
        "for avoiding traps and finding hidden passages. You've learned to "
        "navigate perilous environments with practiced ease."
    ),
    category="tov_technical",
    benefits=[
        "You have advantage on Wisdom (Perception) and Intelligence (Investigation) "
        "checks to detect traps and secret doors.",
        "You have advantage on saving throws against traps and resistance to "
        "damage dealt by traps.",
        "You can search for traps while moving at a normal pace instead of a "
        "slow pace.",
    ],
    ruleset="tov",
)

SWIFT_TALENT = Feat(
    name="Swift",
    description=(
        "Your speed and agility are exceptional. You dart through battlefields "
        "and difficult terrain with ease, slipping past obstacles and enemies "
        "that would slow others down."
    ),
    category="tov_technical",
    benefits=[
        "Your walking speed increases by 10 feet.",
        "When you use the Dash action, difficult terrain doesn't cost extra "
        "movement for the rest of the turn.",
        "When you make a melee attack against a creature, you don't provoke "
        "opportunity attacks from that creature for the rest of your turn.",
    ],
    ruleset="tov",
)


# =============================================================================
# COLLECTIONS
# =============================================================================

ORIGIN_FEATS: list[Feat] = [
    ALERT,
    CRAFTER,
    HEALER,
    LUCKY,
    MAGIC_INITIATE,
    MAGIC_INITIATE_BARD,
    MAGIC_INITIATE_CLERIC,
    MAGIC_INITIATE_DRUID,
    MAGIC_INITIATE_SORCERER,
    MAGIC_INITIATE_WARLOCK,
    MAGIC_INITIATE_WIZARD,
    MUSICIAN,
    SAVAGE_ATTACKER,
    SKILLED,
    TAVERN_BRAWLER,
    TOUGH,
]

# 2014 General Feats (includes feats that changed in 2024 marked with ruleset="dnd2014")
GENERAL_FEATS_2014: list[Feat] = [
    ACTOR,
    ATHLETE,
    CHARGER,
    CROSSBOW_EXPERT,
    DEFENSIVE_DUELIST,
    DUAL_WIELDER,
    DUNGEON_DELVER,
    DURABLE,
    ELEMENTAL_ADEPT,
    GRAPPLER,
    GREAT_WEAPON_MASTER,
    HEAVY_ARMOR_MASTER,
    INSPIRING_LEADER,
    KEEN_MIND,
    LINGUIST,
    MAGE_SLAYER,
    MEDIUM_ARMOR_MASTER,
    MOBILE,
    MOUNTED_COMBATANT,
    OBSERVANT,
    POLEARM_MASTER,
    RESILIENT,
    RITUAL_CASTER,
    SENTINEL,
    SHARPSHOOTER,
    SHIELD_MASTER,
    SKULKER,
    SPELL_SNIPER,
    WAR_CASTER,
    WEAPON_MASTER,
    # TCE Feats
    FEY_TOUCHED,
    SHADOW_TOUCHED,
    SKILL_EXPERT,
    TELEKINETIC,
    TELEPATHIC,
    CRUSHER,
    SLASHER,
    PIERCER,
    METAMAGIC_ADEPT,
    ELDRITCH_ADEPT,
    FIGHTING_INITIATE,
    CHEF,
    GUNNER,
    POISONER,
    # Fizban's Feats
    GIFT_OF_THE_CHROMATIC_DRAGON,
    GIFT_OF_THE_METALLIC_DRAGON,
    GIFT_OF_THE_GEM_DRAGON,
]

# 2024 Revised Feats
GENERAL_FEATS_2024: list[Feat] = [
    GREAT_WEAPON_MASTER_2024,
    SHARPSHOOTER_2024,
    POLEARM_MASTER_2024,
    SENTINEL_2024,
    CROSSBOW_EXPERT_2024,
    DUAL_WIELDER_2024,
    CHARGER_2024,
]

# Combined list of all general feats
GENERAL_FEATS: list[Feat] = GENERAL_FEATS_2014 + GENERAL_FEATS_2024

# Tales of the Valiant Talents
TOV_MARTIAL_TALENTS: list[Feat] = [
    CRITICAL_TRAINING,
    PHYSICAL_FORTITUDE,
    HEAVY_WEAPONS_MASTERY,
    RETURN_FIRE,
    COMBAT_CONDITIONING,
    HARD_TARGET,
    DUAL_STRIKER,
    SHIELD_EXPERTISE,
]

TOV_MAGIC_TALENTS: list[Feat] = [
    ELEMENTAL_SAVANT,
    FOCUS_FEY,
    FOCUS_ARCANE,
    FOCUS_DIVINE,
    FOCUS_PRIMAL,
    FOCUS_SHADOW,
    SPELL_DUELIST,
    TOUCH_OF_LUCK,
    BOTTOMLESS_LUCK,
    MENTAL_FORTRESS,
]

TOV_TECHNICAL_TALENTS: list[Feat] = [
    COMRADE,
    COVERT,
    FIELD_MEDIC,
    AWARE,
    POLYGLOT,
    SKILLED_TALENT,
    JACK_OF_ALL_TRADES_TALENT,
    SOCIAL_EXPERTISE,
    DUNGEON_EXPERT,
    SWIFT_TALENT,
]

TOV_TALENTS: list[Feat] = TOV_MARTIAL_TALENTS + TOV_MAGIC_TALENTS + TOV_TECHNICAL_TALENTS

# D&D Feats (all rulesets except ToV-specific)
DND_FEATS: list[Feat] = ORIGIN_FEATS + GENERAL_FEATS

ALL_FEATS: list[Feat] = DND_FEATS + TOV_TALENTS

# Dictionary for quick lookup
_FEATS_BY_NAME: dict[str, Feat] = {feat.name.lower(): feat for feat in ALL_FEATS}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_feat(name: str) -> Optional[Feat]:
    """Get a feat by name (case-insensitive)."""
    return _FEATS_BY_NAME.get(name.lower())


def get_feats_by_category(category: str) -> list[Feat]:
    """Get all feats in a specific category."""
    return [feat for feat in ALL_FEATS if feat.category == category]


def get_origin_feats() -> list[Feat]:
    """Get all origin feats."""
    return ORIGIN_FEATS.copy()


def get_general_feats() -> list[Feat]:
    """Get all general feats."""
    return GENERAL_FEATS.copy()


def get_feats_with_prerequisites() -> list[Feat]:
    """Get all feats that have prerequisites."""
    return [feat for feat in ALL_FEATS if feat.prerequisites]


def get_feats_with_ability_increase() -> list[Feat]:
    """Get all feats that grant ability score increases."""
    return [feat for feat in ALL_FEATS if feat.ability_increase]


def get_repeatable_feats() -> list[Feat]:
    """Get all feats that can be taken multiple times."""
    return [feat for feat in ALL_FEATS if feat.repeatable]


def search_feats(query: str) -> list[Feat]:
    """Search feats by name or description."""
    query_lower = query.lower()
    results = []
    for feat in ALL_FEATS:
        if query_lower in feat.name.lower() or query_lower in feat.description.lower():
            results.append(feat)
    return results


def get_all_feat_names() -> list[str]:
    """Get a list of all feat names."""
    return [feat.name for feat in ALL_FEATS]


# =============================================================================
# TOV TALENT HELPER FUNCTIONS
# =============================================================================


def get_tov_talents() -> list[Feat]:
    """Get all Tales of the Valiant talents."""
    return TOV_TALENTS.copy()


def get_tov_martial_talents() -> list[Feat]:
    """Get all ToV martial talents."""
    return TOV_MARTIAL_TALENTS.copy()


def get_tov_magic_talents() -> list[Feat]:
    """Get all ToV magic talents."""
    return TOV_MAGIC_TALENTS.copy()


def get_tov_technical_talents() -> list[Feat]:
    """Get all ToV technical talents."""
    return TOV_TECHNICAL_TALENTS.copy()


def get_feats_for_ruleset(ruleset: Optional[str] = None) -> list[Feat]:
    """Get feats/talents appropriate for a specific ruleset.

    Args:
        ruleset: The ruleset ID ('dnd2014', 'dnd2024', 'tov', or None for all)

    Returns:
        List of feats available for the ruleset. ToV returns only ToV talents.
        For D&D rulesets, returns feats matching that ruleset or with ruleset=None
        (universal). None returns all feats.
    """
    if ruleset is None:
        return ALL_FEATS.copy()
    elif ruleset == "tov":
        return TOV_TALENTS.copy()
    elif ruleset == "dnd2024":
        # Return 2024 versions + feats without version-specific differences
        return [f for f in DND_FEATS if f.ruleset in ("dnd2024", None)]
    else:
        # dnd2014 - Return 2014 versions + feats without version-specific differences
        return [f for f in DND_FEATS if f.ruleset in ("dnd2014", None)]


def get_focus_talents() -> list[Feat]:
    """Get all Focus talents (ToV magic talents that are mutually exclusive)."""
    return [
        feat for feat in TOV_MAGIC_TALENTS
        if feat.name.startswith("Focus (")
    ]


def search_talents(query: str) -> list[Feat]:
    """Search ToV talents by name or description."""
    query_lower = query.lower()
    results = []
    for feat in TOV_TALENTS:
        if query_lower in feat.name.lower() or query_lower in feat.description.lower():
            results.append(feat)
    return results


# =============================================================================
# STRUCTURED PREREQUISITE SUPPORT
# =============================================================================

def _build_structured_prereq(feat: Feat) -> Optional["Prerequisite"]:
    """Build a structured prerequisite from a feat's string prerequisites.

    This function parses common prerequisite patterns and creates
    a Prerequisite object for validation.

    Supported patterns:
    - Ability scores: "Strength 13 or higher", "Dexterity or Strength 13+"
    - Proficiencies: "Proficiency with heavy armor", "Proficiency with any martial weapon"
    - Spellcasting: "The ability to cast at least one spell", "Spellcasting or Pact Magic"
    - Level: "Character 4th level or higher", "8th level"
    - Class: "Fighter", "Paladin or Ranger level 5+"
    - Feat chains: "Alert feat", "Requires Grappler"
    - Size: "Small or Medium size"
    """
    if not feat.prerequisites:
        return None

    prereqs = _get_prereqs()
    Prerequisite = prereqs['Prerequisite']
    AbilityRequirement = prereqs['AbilityRequirement']
    ProficiencyRequirement = prereqs['ProficiencyRequirement']
    ProficiencyType = prereqs['ProficiencyType']
    SpellcastingRequirement = prereqs['SpellcastingRequirement']
    LevelRequirement = prereqs['LevelRequirement']

    # Import additional requirement types
    from dnd_manager.data.prerequisites import FeatRequirement, ClassRequirement

    abilities = []
    alt_abilities = []
    proficiencies = []
    spellcasting = None
    level = None
    feat_reqs = []
    class_req = None

    # All class names for detection
    all_classes = [
        "barbarian", "bard", "cleric", "druid", "fighter", "monk",
        "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"
    ]

    # All feat names for detection (we'll check against known feats)
    known_feat_names = [f.name.lower() for f in ALL_FEATS]

    import re

    for prereq_str in feat.prerequisites:
        prereq_lower = prereq_str.lower()

        # Check for feat prerequisites
        # Patterns: "X feat", "Requires X", "X feat or Y feat"
        feat_pattern = r'(\w+(?:\s+\w+)*)\s+feat'
        feat_matches = re.findall(feat_pattern, prereq_lower)
        for feat_name in feat_matches:
            # Verify it's a known feat
            if feat_name.lower() in known_feat_names:
                feat_reqs.append(FeatRequirement(feat_name.title()))

        # Also check "requires X" pattern
        requires_pattern = r'requires\s+(\w+(?:\s+\w+)*)'
        requires_matches = re.findall(requires_pattern, prereq_lower)
        for req_name in requires_matches:
            if req_name.lower() in known_feat_names:
                feat_reqs.append(FeatRequirement(req_name.title()))

        # Check for class requirements (without level)
        # Pattern: "Paladin", "Fighter or Ranger"
        found_classes = []
        for cls in all_classes:
            if cls in prereq_lower:
                found_classes.append(cls.title())

        if found_classes and not class_req:
            # Check if there's a level requirement with the class
            # Patterns: "5th level", "level 5", "level 5+"
            class_level_match = re.search(r'(\d+)(?:st|nd|rd|th)?\s*level', prereq_lower)
            if not class_level_match:
                # Try "level X" pattern
                class_level_match = re.search(r'level\s*(\d+)', prereq_lower)
            if class_level_match:
                class_req = ClassRequirement(found_classes, int(class_level_match.group(1)))
            elif "level" not in prereq_lower:
                # Only set class requirement if there's no general level requirement
                # (to avoid treating "Character 4th level" as class requirement)
                class_req = ClassRequirement(found_classes)

        # Check for "X or Y 13 or higher" pattern (alternative abilities)
        if " or " in prereq_lower and ("13" in prereq_lower or "higher" in prereq_lower):
            ability_pattern = r'(strength|dexterity|constitution|intelligence|wisdom|charisma)'
            matches = re.findall(ability_pattern, prereq_lower)
            if len(matches) >= 2:
                for ability in matches:
                    alt_abilities.append(AbilityRequirement(ability.title(), 13))
                continue

        # Check for single ability requirement
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            if ability in prereq_lower:
                match = re.search(r'(\d+)', prereq_str)
                if match:
                    min_score = int(match.group(1))
                    abilities.append(AbilityRequirement(ability.title(), min_score))
                break

        # Check for proficiency requirements
        if "proficiency" in prereq_lower:
            if "martial weapon" in prereq_lower:
                proficiencies.append(ProficiencyRequirement(ProficiencyType.MARTIAL_WEAPONS))
            elif "heavy armor" in prereq_lower:
                proficiencies.append(ProficiencyRequirement(ProficiencyType.HEAVY_ARMOR))
            elif "medium armor" in prereq_lower:
                proficiencies.append(ProficiencyRequirement(ProficiencyType.MEDIUM_ARMOR))
            elif "light armor" in prereq_lower:
                proficiencies.append(ProficiencyRequirement(ProficiencyType.LIGHT_ARMOR))
            elif "shield" in prereq_lower:
                proficiencies.append(ProficiencyRequirement(ProficiencyType.SHIELDS))
            elif "simple weapon" in prereq_lower:
                proficiencies.append(ProficiencyRequirement(ProficiencyType.SIMPLE_WEAPONS))

        # Check for spellcasting requirements
        if "spellcasting" in prereq_lower or ("cast" in prereq_lower and "spell" in prereq_lower):
            pact_ok = "pact magic" in prereq_lower or "pact" not in prereq_lower
            spellcasting = SpellcastingRequirement(
                requires_spellcasting=True,
                requires_pact_magic=pact_ok
            )

        # Check for level requirements (character level, not class level)
        if "level" in prereq_lower and not found_classes:
            match = re.search(r'(\d+)(?:st|nd|rd|th)?\s*level', prereq_lower)
            if match:
                level = LevelRequirement(int(match.group(1)))

    # Build the prerequisite if we found anything
    if abilities or alt_abilities or proficiencies or spellcasting or level or feat_reqs or class_req:
        return Prerequisite(
            abilities=abilities,
            alternative_abilities=alt_abilities,
            proficiencies=proficiencies,
            spellcasting=spellcasting,
            level=level,
            feats=feat_reqs,
            class_req=class_req,
            description="; ".join(feat.prerequisites)
        )

    return None


def get_feat_prerequisite(feat: Feat) -> Optional["Prerequisite"]:
    """Get the structured prerequisite for a feat.

    If the feat has a structured_prereq set, return that.
    Otherwise, attempt to parse the string prerequisites.
    """
    if feat.structured_prereq:
        return feat.structured_prereq
    return _build_structured_prereq(feat)


def check_feat_prerequisites(feat: Feat, character) -> tuple[bool, list[str]]:
    """Check if a character meets a feat's prerequisites.

    Args:
        feat: The feat to check
        character: The Character object to check against

    Returns:
        Tuple of (all_met, list_of_failure_reasons)
    """
    prereq = get_feat_prerequisite(feat)
    if prereq is None:
        return True, []
    return prereq.check(character)
