"""Monster data for D&D 5e.

Contains SRD monsters with stats for encounter building and combat tracking.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Size(str, Enum):
    """Creature sizes."""
    TINY = "Tiny"
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    HUGE = "Huge"
    GARGANTUAN = "Gargantuan"


class MonsterType(str, Enum):
    """Monster types."""
    ABERRATION = "Aberration"
    BEAST = "Beast"
    CELESTIAL = "Celestial"
    CONSTRUCT = "Construct"
    DRAGON = "Dragon"
    ELEMENTAL = "Elemental"
    FEY = "Fey"
    FIEND = "Fiend"
    GIANT = "Giant"
    HUMANOID = "Humanoid"
    MONSTROSITY = "Monstrosity"
    OOZE = "Ooze"
    PLANT = "Plant"
    UNDEAD = "Undead"


@dataclass
class Attack:
    """A monster's attack action."""
    name: str
    attack_bonus: int
    damage: str  # e.g., "2d6+4 slashing"
    reach: str = "5 ft."
    description: str = ""


@dataclass
class Trait:
    """A monster's special trait."""
    name: str
    description: str


@dataclass
class Action:
    """A monster's action (non-attack)."""
    name: str
    description: str
    recharge: Optional[str] = None  # e.g., "5-6", "short rest"


@dataclass
class Monster:
    """A monster stat block."""
    name: str
    size: Size
    monster_type: MonsterType
    alignment: str
    armor_class: int
    hit_points: int
    hit_dice: str  # e.g., "4d8+8"
    speed: str  # e.g., "30 ft., fly 60 ft."

    # Ability scores
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    challenge_rating: str  # e.g., "1/4", "1", "5"
    xp: int

    # Optional features
    saving_throws: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    damage_vulnerabilities: list[str] = field(default_factory=list)
    damage_resistances: list[str] = field(default_factory=list)
    damage_immunities: list[str] = field(default_factory=list)
    condition_immunities: list[str] = field(default_factory=list)
    senses: str = ""
    languages: str = ""

    traits: list[Trait] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    attacks: list[Attack] = field(default_factory=list)
    legendary_actions: list[Action] = field(default_factory=list)

    description: str = ""

    @property
    def cr_numeric(self) -> float:
        """Get CR as a numeric value."""
        if "/" in self.challenge_rating:
            num, denom = self.challenge_rating.split("/")
            return int(num) / int(denom)
        return float(self.challenge_rating)

    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus from CR."""
        cr = self.cr_numeric
        if cr < 5:
            return 2
        elif cr < 9:
            return 3
        elif cr < 13:
            return 4
        elif cr < 17:
            return 5
        elif cr < 21:
            return 6
        elif cr < 25:
            return 7
        elif cr < 29:
            return 8
        return 9


# =============================================================================
# CR 0 MONSTERS
# =============================================================================

BAT = Monster(
    name="Bat",
    size=Size.TINY,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=12,
    hit_points=1,
    hit_dice="1d4-1",
    speed="5 ft., fly 30 ft.",
    strength=2, dexterity=15, constitution=8,
    intelligence=2, wisdom=12, charisma=4,
    challenge_rating="0",
    xp=10,
    senses="blindsight 60 ft., passive Perception 11",
    traits=[
        Trait("Echolocation", "The bat can't use its blindsight while deafened."),
        Trait("Keen Hearing", "The bat has advantage on Wisdom (Perception) checks that rely on hearing."),
    ],
    attacks=[
        Attack("Bite", 0, "1 piercing", "5 ft."),
    ],
)

RAT = Monster(
    name="Rat",
    size=Size.TINY,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=10,
    hit_points=1,
    hit_dice="1d4-1",
    speed="20 ft.",
    strength=2, dexterity=11, constitution=9,
    intelligence=2, wisdom=10, charisma=4,
    challenge_rating="0",
    xp=10,
    senses="darkvision 30 ft., passive Perception 10",
    traits=[
        Trait("Keen Smell", "The rat has advantage on Wisdom (Perception) checks that rely on smell."),
    ],
    attacks=[
        Attack("Bite", 0, "1 piercing", "5 ft."),
    ],
)

# =============================================================================
# CR 1/8 MONSTERS
# =============================================================================

BANDIT = Monster(
    name="Bandit",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="any non-lawful",
    armor_class=12,
    hit_points=11,
    hit_dice="2d8+2",
    speed="30 ft.",
    strength=11, dexterity=12, constitution=12,
    intelligence=10, wisdom=10, charisma=10,
    challenge_rating="1/8",
    xp=25,
    languages="any one language (usually Common)",
    senses="passive Perception 10",
    attacks=[
        Attack("Scimitar", 3, "1d6+1 slashing", "5 ft."),
        Attack("Light Crossbow", 3, "1d8+1 piercing", "80/320 ft."),
    ],
)

CULTIST = Monster(
    name="Cultist",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="any non-good",
    armor_class=12,
    hit_points=9,
    hit_dice="2d8",
    speed="30 ft.",
    strength=11, dexterity=12, constitution=10,
    intelligence=10, wisdom=11, charisma=10,
    challenge_rating="1/8",
    xp=25,
    skills=["Deception +2", "Religion +2"],
    languages="any one language (usually Common)",
    senses="passive Perception 10",
    traits=[
        Trait("Dark Devotion", "The cultist has advantage on saving throws against being charmed or frightened."),
    ],
    attacks=[
        Attack("Scimitar", 3, "1d6+1 slashing", "5 ft."),
    ],
)

GUARD = Monster(
    name="Guard",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="any alignment",
    armor_class=16,
    hit_points=11,
    hit_dice="2d8+2",
    speed="30 ft.",
    strength=13, dexterity=12, constitution=12,
    intelligence=10, wisdom=11, charisma=10,
    challenge_rating="1/8",
    xp=25,
    skills=["Perception +2"],
    languages="any one language (usually Common)",
    senses="passive Perception 12",
    attacks=[
        Attack("Spear", 3, "1d6+1 piercing", "5 ft."),
        Attack("Spear (Thrown)", 3, "1d6+1 piercing", "20/60 ft."),
    ],
)

# =============================================================================
# CR 1/4 MONSTERS
# =============================================================================

GOBLIN = Monster(
    name="Goblin",
    size=Size.SMALL,
    monster_type=MonsterType.HUMANOID,
    alignment="neutral evil",
    armor_class=15,
    hit_points=7,
    hit_dice="2d6",
    speed="30 ft.",
    strength=8, dexterity=14, constitution=10,
    intelligence=10, wisdom=8, charisma=8,
    challenge_rating="1/4",
    xp=50,
    skills=["Stealth +6"],
    languages="Common, Goblin",
    senses="darkvision 60 ft., passive Perception 9",
    traits=[
        Trait("Nimble Escape", "The goblin can take the Disengage or Hide action as a bonus action on each of its turns."),
    ],
    attacks=[
        Attack("Scimitar", 4, "1d6+2 slashing", "5 ft."),
        Attack("Shortbow", 4, "1d6+2 piercing", "80/320 ft."),
    ],
)

SKELETON = Monster(
    name="Skeleton",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="lawful evil",
    armor_class=13,
    hit_points=13,
    hit_dice="2d8+4",
    speed="30 ft.",
    strength=10, dexterity=14, constitution=15,
    intelligence=6, wisdom=8, charisma=5,
    challenge_rating="1/4",
    xp=50,
    damage_vulnerabilities=["bludgeoning"],
    damage_immunities=["poison"],
    condition_immunities=["exhaustion", "poisoned"],
    languages="understands languages it knew in life but can't speak",
    senses="darkvision 60 ft., passive Perception 9",
    attacks=[
        Attack("Shortsword", 4, "1d6+2 piercing", "5 ft."),
        Attack("Shortbow", 4, "1d6+2 piercing", "80/320 ft."),
    ],
)

ZOMBIE = Monster(
    name="Zombie",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="neutral evil",
    armor_class=8,
    hit_points=22,
    hit_dice="3d8+9",
    speed="20 ft.",
    strength=13, dexterity=6, constitution=16,
    intelligence=3, wisdom=6, charisma=5,
    challenge_rating="1/4",
    xp=50,
    saving_throws=["Wis +0"],
    damage_immunities=["poison"],
    condition_immunities=["poisoned"],
    languages="understands languages it knew in life but can't speak",
    senses="darkvision 60 ft., passive Perception 8",
    traits=[
        Trait("Undead Fortitude", "If damage reduces the zombie to 0 hit points, it must make a Constitution saving throw with a DC of 5 + the damage taken, unless the damage is radiant or from a critical hit. On a success, the zombie drops to 1 hit point instead."),
    ],
    attacks=[
        Attack("Slam", 3, "1d6+1 bludgeoning", "5 ft."),
    ],
)

WOLF = Monster(
    name="Wolf",
    size=Size.MEDIUM,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=13,
    hit_points=11,
    hit_dice="2d8+2",
    speed="40 ft.",
    strength=12, dexterity=15, constitution=12,
    intelligence=3, wisdom=12, charisma=6,
    challenge_rating="1/4",
    xp=50,
    skills=["Perception +3", "Stealth +4"],
    senses="passive Perception 13",
    traits=[
        Trait("Keen Hearing and Smell", "The wolf has advantage on Wisdom (Perception) checks that rely on hearing or smell."),
        Trait("Pack Tactics", "The wolf has advantage on attack rolls against a creature if at least one of the wolf's allies is within 5 feet of the creature and the ally isn't incapacitated."),
    ],
    attacks=[
        Attack("Bite", 4, "2d4+2 piercing", "5 ft.", "If the target is a creature, it must succeed on a DC 11 Strength saving throw or be knocked prone."),
    ],
)

# =============================================================================
# CR 1/2 MONSTERS
# =============================================================================

ORC = Monster(
    name="Orc",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="chaotic evil",
    armor_class=13,
    hit_points=15,
    hit_dice="2d8+6",
    speed="30 ft.",
    strength=16, dexterity=12, constitution=16,
    intelligence=7, wisdom=11, charisma=10,
    challenge_rating="1/2",
    xp=100,
    skills=["Intimidation +2"],
    languages="Common, Orc",
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Aggressive", "As a bonus action, the orc can move up to its speed toward a hostile creature that it can see."),
    ],
    attacks=[
        Attack("Greataxe", 5, "1d12+3 slashing", "5 ft."),
        Attack("Javelin", 5, "1d6+3 piercing", "30/120 ft."),
    ],
)

HOBGOBLIN = Monster(
    name="Hobgoblin",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="lawful evil",
    armor_class=18,
    hit_points=11,
    hit_dice="2d8+2",
    speed="30 ft.",
    strength=13, dexterity=12, constitution=12,
    intelligence=10, wisdom=10, charisma=9,
    challenge_rating="1/2",
    xp=100,
    languages="Common, Goblin",
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Martial Advantage", "Once per turn, the hobgoblin can deal an extra 7 (2d6) damage to a creature it hits with a weapon attack if that creature is within 5 feet of an ally of the hobgoblin that isn't incapacitated."),
    ],
    attacks=[
        Attack("Longsword", 3, "1d8+1 slashing", "5 ft."),
        Attack("Longbow", 3, "1d8+1 piercing", "150/600 ft."),
    ],
)

SHADOW = Monster(
    name="Shadow",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="chaotic evil",
    armor_class=12,
    hit_points=16,
    hit_dice="3d8+3",
    speed="40 ft.",
    strength=6, dexterity=14, constitution=13,
    intelligence=6, wisdom=10, charisma=8,
    challenge_rating="1/2",
    xp=100,
    skills=["Stealth +4 (+6 in dim light or darkness)"],
    damage_vulnerabilities=["radiant"],
    damage_resistances=["acid", "cold", "fire", "lightning", "thunder", "bludgeoning, piercing, and slashing from nonmagical attacks"],
    damage_immunities=["necrotic", "poison"],
    condition_immunities=["exhaustion", "frightened", "grappled", "paralyzed", "petrified", "poisoned", "prone", "restrained"],
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Amorphous", "The shadow can move through a space as narrow as 1 inch wide without squeezing."),
        Trait("Shadow Stealth", "While in dim light or darkness, the shadow can take the Hide action as a bonus action."),
        Trait("Sunlight Weakness", "While in sunlight, the shadow has disadvantage on attack rolls, ability checks, and saving throws."),
    ],
    attacks=[
        Attack("Strength Drain", 4, "2d6+2 necrotic", "5 ft.", "The target's Strength score is reduced by 1d4. The target dies if this reduces its Strength to 0. Otherwise, the reduction lasts until the target finishes a short or long rest. If a non-evil humanoid dies from this attack, a new shadow rises from the corpse 1d4 hours later."),
    ],
)

# =============================================================================
# CR 1 MONSTERS
# =============================================================================

BUGBEAR = Monster(
    name="Bugbear",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="chaotic evil",
    armor_class=16,
    hit_points=27,
    hit_dice="5d8+5",
    speed="30 ft.",
    strength=15, dexterity=14, constitution=13,
    intelligence=8, wisdom=11, charisma=9,
    challenge_rating="1",
    xp=200,
    skills=["Stealth +6", "Survival +2"],
    languages="Common, Goblin",
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Brute", "A melee weapon deals one extra die of its damage when the bugbear hits with it (included in the attack)."),
        Trait("Surprise Attack", "If the bugbear surprises a creature and hits it with an attack during the first round of combat, the target takes an extra 7 (2d6) damage from the attack."),
    ],
    attacks=[
        Attack("Morningstar", 4, "2d8+2 piercing", "5 ft."),
        Attack("Javelin", 4, "2d6+2 piercing", "30/120 ft."),
    ],
)

GHOUL = Monster(
    name="Ghoul",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="chaotic evil",
    armor_class=12,
    hit_points=22,
    hit_dice="5d8",
    speed="30 ft.",
    strength=13, dexterity=15, constitution=10,
    intelligence=7, wisdom=10, charisma=6,
    challenge_rating="1",
    xp=200,
    damage_immunities=["poison"],
    condition_immunities=["charmed", "exhaustion", "poisoned"],
    languages="Common",
    senses="darkvision 60 ft., passive Perception 10",
    attacks=[
        Attack("Bite", 2, "2d6+2 piercing", "5 ft."),
        Attack("Claws", 4, "2d4+2 slashing", "5 ft.", "If the target is a creature other than an elf or undead, it must succeed on a DC 10 Constitution saving throw or be paralyzed for 1 minute. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."),
    ],
)

DIRE_WOLF = Monster(
    name="Dire Wolf",
    size=Size.LARGE,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=14,
    hit_points=37,
    hit_dice="5d10+10",
    speed="50 ft.",
    strength=17, dexterity=15, constitution=15,
    intelligence=3, wisdom=12, charisma=7,
    challenge_rating="1",
    xp=200,
    skills=["Perception +3", "Stealth +4"],
    senses="passive Perception 13",
    traits=[
        Trait("Keen Hearing and Smell", "The wolf has advantage on Wisdom (Perception) checks that rely on hearing or smell."),
        Trait("Pack Tactics", "The wolf has advantage on attack rolls against a creature if at least one of the wolf's allies is within 5 feet of the creature and the ally isn't incapacitated."),
    ],
    attacks=[
        Attack("Bite", 5, "2d6+3 piercing", "5 ft.", "If the target is a creature, it must succeed on a DC 13 Strength saving throw or be knocked prone."),
    ],
)

# =============================================================================
# CR 2 MONSTERS
# =============================================================================

OGRE = Monster(
    name="Ogre",
    size=Size.LARGE,
    monster_type=MonsterType.GIANT,
    alignment="chaotic evil",
    armor_class=11,
    hit_points=59,
    hit_dice="7d10+21",
    speed="40 ft.",
    strength=19, dexterity=8, constitution=16,
    intelligence=5, wisdom=7, charisma=7,
    challenge_rating="2",
    xp=450,
    languages="Common, Giant",
    senses="darkvision 60 ft., passive Perception 8",
    attacks=[
        Attack("Greatclub", 6, "2d8+4 bludgeoning", "5 ft."),
        Attack("Javelin", 6, "2d6+4 piercing", "30/120 ft."),
    ],
)

GHAST = Monster(
    name="Ghast",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="chaotic evil",
    armor_class=13,
    hit_points=36,
    hit_dice="8d8",
    speed="30 ft.",
    strength=16, dexterity=17, constitution=10,
    intelligence=11, wisdom=10, charisma=8,
    challenge_rating="2",
    xp=450,
    damage_resistances=["necrotic"],
    damage_immunities=["poison"],
    condition_immunities=["charmed", "exhaustion", "poisoned"],
    languages="Common",
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Stench", "Any creature that starts its turn within 5 feet of the ghast must succeed on a DC 10 Constitution saving throw or be poisoned until the start of its next turn. On a successful saving throw, the creature is immune to the ghast's Stench for 24 hours."),
        Trait("Turning Defiance", "The ghast and any ghouls within 30 feet of it have advantage on saving throws against effects that turn undead."),
    ],
    attacks=[
        Attack("Bite", 3, "2d8+3 piercing", "5 ft."),
        Attack("Claws", 5, "2d6+3 slashing", "5 ft.", "If the target is a creature other than an undead, it must succeed on a DC 10 Constitution saving throw or be paralyzed for 1 minute."),
    ],
)

MIMIC = Monster(
    name="Mimic",
    size=Size.MEDIUM,
    monster_type=MonsterType.MONSTROSITY,
    alignment="neutral",
    armor_class=12,
    hit_points=58,
    hit_dice="9d8+18",
    speed="15 ft.",
    strength=17, dexterity=12, constitution=15,
    intelligence=5, wisdom=13, charisma=8,
    challenge_rating="2",
    xp=450,
    skills=["Stealth +5"],
    damage_immunities=["acid"],
    condition_immunities=["prone"],
    senses="darkvision 60 ft., passive Perception 11",
    traits=[
        Trait("Shapechanger", "The mimic can use its action to polymorph into an object or back into its true, amorphous form. Its statistics are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies."),
        Trait("Adhesive (Object Form Only)", "The mimic adheres to anything that touches it. A Huge or smaller creature adhered to the mimic is also grappled by it (escape DC 13). Ability checks made to escape this grapple have disadvantage."),
        Trait("False Appearance (Object Form Only)", "While the mimic remains motionless, it is indistinguishable from an ordinary object."),
        Trait("Grappler", "The mimic has advantage on attack rolls against any creature grappled by it."),
    ],
    attacks=[
        Attack("Pseudopod", 5, "1d8+3 bludgeoning", "5 ft.", "If the mimic is in object form, the target is subjected to its Adhesive trait."),
        Attack("Bite", 5, "1d8+3 piercing + 1d8 acid", "5 ft."),
    ],
)

# =============================================================================
# CR 3 MONSTERS
# =============================================================================

OWLBEAR = Monster(
    name="Owlbear",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="unaligned",
    armor_class=13,
    hit_points=59,
    hit_dice="7d10+21",
    speed="40 ft.",
    strength=20, dexterity=12, constitution=17,
    intelligence=3, wisdom=12, charisma=7,
    challenge_rating="3",
    xp=700,
    skills=["Perception +3"],
    senses="darkvision 60 ft., passive Perception 13",
    traits=[
        Trait("Keen Sight and Smell", "The owlbear has advantage on Wisdom (Perception) checks that rely on sight or smell."),
    ],
    attacks=[
        Attack("Beak", 7, "1d10+5 piercing", "5 ft."),
        Attack("Claws", 7, "2d8+5 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The owlbear makes two attacks: one with its beak and one with its claws."),
    ],
)

WEREWOLF = Monster(
    name="Werewolf",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="chaotic evil",
    armor_class=11,
    hit_points=58,
    hit_dice="9d8+18",
    speed="30 ft. (40 ft. in wolf form)",
    strength=15, dexterity=13, constitution=14,
    intelligence=10, wisdom=11, charisma=10,
    challenge_rating="3",
    xp=700,
    skills=["Perception +4", "Stealth +3"],
    damage_immunities=["bludgeoning, piercing, and slashing from nonmagical attacks not made with silvered weapons"],
    languages="Common (can't speak in wolf form)",
    senses="passive Perception 14",
    traits=[
        Trait("Shapechanger", "The werewolf can use its action to polymorph into a wolf-humanoid hybrid or into a wolf, or back into its true form, which is humanoid. Its statistics, other than its AC, are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies."),
        Trait("Keen Hearing and Smell", "The werewolf has advantage on Wisdom (Perception) checks that rely on hearing or smell."),
    ],
    attacks=[
        Attack("Bite (Wolf or Hybrid Form Only)", 4, "1d8+2 piercing", "5 ft.", "If the target is a humanoid, it must succeed on a DC 12 Constitution saving throw or be cursed with werewolf lycanthropy."),
        Attack("Claws (Hybrid Form Only)", 4, "2d4+2 slashing", "5 ft."),
        Attack("Spear (Humanoid Form Only)", 4, "1d6+2 piercing", "5 ft."),
    ],
    actions=[
        Action("Multiattack (Hybrid Form Only)", "The werewolf makes two attacks: one with its bite and one with its claws."),
    ],
)

MUMMY = Monster(
    name="Mummy",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="lawful evil",
    armor_class=11,
    hit_points=58,
    hit_dice="9d8+18",
    speed="20 ft.",
    strength=16, dexterity=8, constitution=15,
    intelligence=6, wisdom=10, charisma=12,
    challenge_rating="3",
    xp=700,
    saving_throws=["Wis +2"],
    damage_vulnerabilities=["fire"],
    damage_resistances=["bludgeoning, piercing, and slashing from nonmagical attacks"],
    damage_immunities=["necrotic", "poison"],
    condition_immunities=["charmed", "exhaustion", "frightened", "paralyzed", "poisoned"],
    languages="the languages it knew in life",
    senses="darkvision 60 ft., passive Perception 10",
    attacks=[
        Attack("Rotting Fist", 5, "2d6+3 bludgeoning + 3d6 necrotic", "5 ft.", "If the target is a creature, it must succeed on a DC 12 Constitution saving throw or be cursed with mummy rot. The cursed target can't regain hit points, and its hit point maximum decreases by 10 (3d6) for every 24 hours that elapse. If the curse reduces the target's hit point maximum to 0, the target dies, and its body turns to dust."),
    ],
    actions=[
        Action("Multiattack", "The mummy can use its Dreadful Glare and makes one attack with its rotting fist."),
        Action("Dreadful Glare", "The mummy targets one creature it can see within 60 feet of it. If the target can see the mummy, it must succeed on a DC 11 Wisdom saving throw against this magic or become frightened until the end of the mummy's next turn. If the target fails the saving throw by 5 or more, it is also paralyzed for the same duration. A target that succeeds on the saving throw is immune to the Dreadful Glare of all mummies (but not mummy lords) for the next 24 hours."),
    ],
)

# =============================================================================
# CR 5 MONSTERS
# =============================================================================

TROLL = Monster(
    name="Troll",
    size=Size.LARGE,
    monster_type=MonsterType.GIANT,
    alignment="chaotic evil",
    armor_class=15,
    hit_points=84,
    hit_dice="8d10+40",
    speed="30 ft.",
    strength=18, dexterity=13, constitution=20,
    intelligence=7, wisdom=9, charisma=7,
    challenge_rating="5",
    xp=1800,
    skills=["Perception +2"],
    senses="darkvision 60 ft., passive Perception 12",
    languages="Giant",
    traits=[
        Trait("Keen Smell", "The troll has advantage on Wisdom (Perception) checks that rely on smell."),
        Trait("Regeneration", "The troll regains 10 hit points at the start of its turn. If the troll takes acid or fire damage, this trait doesn't function at the start of the troll's next turn. The troll dies only if it starts its turn with 0 hit points and doesn't regenerate."),
    ],
    attacks=[
        Attack("Bite", 7, "1d6+4 piercing", "5 ft."),
        Attack("Claw", 7, "2d6+4 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The troll makes three attacks: one with its bite and two with its claws."),
    ],
)

SALAMANDER = Monster(
    name="Salamander",
    size=Size.LARGE,
    monster_type=MonsterType.ELEMENTAL,
    alignment="neutral evil",
    armor_class=15,
    hit_points=90,
    hit_dice="12d10+24",
    speed="30 ft.",
    strength=18, dexterity=14, constitution=15,
    intelligence=11, wisdom=10, charisma=12,
    challenge_rating="5",
    xp=1800,
    damage_vulnerabilities=["cold"],
    damage_resistances=["bludgeoning, piercing, and slashing from nonmagical attacks"],
    damage_immunities=["fire"],
    senses="darkvision 60 ft., passive Perception 10",
    languages="Ignan",
    traits=[
        Trait("Heated Body", "A creature that touches the salamander or hits it with a melee attack while within 5 feet of it takes 7 (2d6) fire damage."),
        Trait("Heated Weapons", "Any metal melee weapon the salamander wields deals an extra 3 (1d6) fire damage on a hit (included in the attack)."),
    ],
    attacks=[
        Attack("Spear", 7, "2d6+4 piercing + 1d6 fire", "5 ft."),
        Attack("Tail", 7, "2d6+4 bludgeoning + 2d6 fire", "10 ft.", "The target is grappled (escape DC 14). Until this grapple ends, the target is restrained, the salamander can automatically hit the target with its tail, and the salamander can't make tail attacks against other targets."),
    ],
    actions=[
        Action("Multiattack", "The salamander makes two attacks: one with its spear and one with its tail."),
    ],
)

# =============================================================================
# CR 8+ MONSTERS
# =============================================================================

YOUNG_RED_DRAGON = Monster(
    name="Young Red Dragon",
    size=Size.LARGE,
    monster_type=MonsterType.DRAGON,
    alignment="chaotic evil",
    armor_class=18,
    hit_points=178,
    hit_dice="17d10+85",
    speed="40 ft., climb 40 ft., fly 80 ft.",
    strength=23, dexterity=10, constitution=21,
    intelligence=14, wisdom=11, charisma=19,
    challenge_rating="10",
    xp=5900,
    saving_throws=["Dex +4", "Con +9", "Wis +4", "Cha +8"],
    skills=["Perception +8", "Stealth +4"],
    damage_immunities=["fire"],
    senses="blindsight 30 ft., darkvision 120 ft., passive Perception 18",
    languages="Common, Draconic",
    attacks=[
        Attack("Bite", 10, "2d10+6 piercing + 1d6 fire", "10 ft."),
        Attack("Claw", 10, "2d6+6 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The dragon makes three attacks: one with its bite and two with its claws."),
        Action("Fire Breath", "The dragon exhales fire in a 30-foot cone. Each creature in that area must make a DC 17 Dexterity saving throw, taking 56 (16d6) fire damage on a failed save, or half as much damage on a successful one.", "5-6"),
    ],
)

ADULT_RED_DRAGON = Monster(
    name="Adult Red Dragon",
    size=Size.HUGE,
    monster_type=MonsterType.DRAGON,
    alignment="chaotic evil",
    armor_class=19,
    hit_points=256,
    hit_dice="19d12+133",
    speed="40 ft., climb 40 ft., fly 80 ft.",
    strength=27, dexterity=10, constitution=25,
    intelligence=16, wisdom=13, charisma=21,
    challenge_rating="17",
    xp=18000,
    saving_throws=["Dex +6", "Con +13", "Wis +7", "Cha +11"],
    skills=["Perception +13", "Stealth +6"],
    damage_immunities=["fire"],
    senses="blindsight 60 ft., darkvision 120 ft., passive Perception 23",
    languages="Common, Draconic",
    traits=[
        Trait("Legendary Resistance (3/Day)", "If the dragon fails a saving throw, it can choose to succeed instead."),
    ],
    attacks=[
        Attack("Bite", 14, "2d10+8 piercing + 2d6 fire", "10 ft."),
        Attack("Claw", 14, "2d6+8 slashing", "5 ft."),
        Attack("Tail", 14, "2d8+8 bludgeoning", "15 ft."),
    ],
    actions=[
        Action("Multiattack", "The dragon can use its Frightful Presence. It then makes three attacks: one with its bite and two with its claws."),
        Action("Frightful Presence", "Each creature of the dragon's choice that is within 120 feet of the dragon and aware of it must succeed on a DC 19 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."),
        Action("Fire Breath", "The dragon exhales fire in a 60-foot cone. Each creature in that area must make a DC 21 Dexterity saving throw, taking 63 (18d6) fire damage on a failed save, or half as much damage on a successful one.", "5-6"),
    ],
    legendary_actions=[
        Action("Detect", "The dragon makes a Wisdom (Perception) check."),
        Action("Tail Attack", "The dragon makes a tail attack."),
        Action("Wing Attack (Costs 2 Actions)", "The dragon beats its wings. Each creature within 10 feet of the dragon must succeed on a DC 22 Dexterity saving throw or take 15 (2d6+8) bludgeoning damage and be knocked prone. The dragon can then fly up to half its flying speed."),
    ],
)


# =============================================================================
# CR 1/4 MONSTERS (Additional)
# =============================================================================

KOBOLD = Monster(
    name="Kobold",
    size=Size.SMALL,
    monster_type=MonsterType.HUMANOID,
    alignment="lawful evil",
    armor_class=12,
    hit_points=5,
    hit_dice="2d6-2",
    speed="30 ft.",
    strength=7, dexterity=15, constitution=9,
    intelligence=8, wisdom=7, charisma=8,
    challenge_rating="1/8",
    xp=25,
    languages="Common, Draconic",
    senses="darkvision 60 ft., passive Perception 8",
    traits=[
        Trait("Sunlight Sensitivity", "While in sunlight, the kobold has disadvantage on attack rolls and Perception checks that rely on sight."),
        Trait("Pack Tactics", "The kobold has advantage on attack rolls against a creature if at least one of the kobold's allies is within 5 feet of the creature and the ally isn't incapacitated."),
    ],
    attacks=[
        Attack("Dagger", 4, "1d4+2 piercing", "5 ft."),
        Attack("Sling", 4, "1d4+2 bludgeoning", "30/120 ft."),
    ],
)

GIANT_RAT = Monster(
    name="Giant Rat",
    size=Size.SMALL,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=12,
    hit_points=7,
    hit_dice="2d6",
    speed="30 ft.",
    strength=7, dexterity=15, constitution=11,
    intelligence=2, wisdom=10, charisma=4,
    challenge_rating="1/8",
    xp=25,
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Keen Smell", "The rat has advantage on Wisdom (Perception) checks that rely on smell."),
        Trait("Pack Tactics", "The rat has advantage on attack rolls against a creature if at least one of the rat's allies is within 5 feet of the creature and the ally isn't incapacitated."),
    ],
    attacks=[
        Attack("Bite", 4, "1d4+2 piercing", "5 ft."),
    ],
)

STIRGE = Monster(
    name="Stirge",
    size=Size.TINY,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=14,
    hit_points=2,
    hit_dice="1d4",
    speed="10 ft., fly 40 ft.",
    strength=4, dexterity=16, constitution=11,
    intelligence=2, wisdom=8, charisma=6,
    challenge_rating="1/8",
    xp=25,
    senses="darkvision 60 ft., passive Perception 9",
    attacks=[
        Attack("Blood Drain", 5, "1d4+3 piercing", "5 ft.", "The stirge attaches to the target. While attached, the stirge doesn't attack. Instead, at the start of each of the stirge's turns, the target loses 5 (1d4+3) hit points due to blood loss. The stirge can detach itself by spending 5 feet of its movement. It does so after it drains 10 hit points of blood from the target or the target dies."),
    ],
)

SPIDER = Monster(
    name="Giant Spider",
    size=Size.LARGE,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=14,
    hit_points=26,
    hit_dice="4d10+4",
    speed="30 ft., climb 30 ft.",
    strength=14, dexterity=16, constitution=12,
    intelligence=2, wisdom=11, charisma=4,
    challenge_rating="1",
    xp=200,
    skills=["Stealth +7"],
    senses="blindsight 10 ft., darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Spider Climb", "The spider can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check."),
        Trait("Web Sense", "While in contact with a web, the spider knows the exact location of any other creature in contact with the same web."),
        Trait("Web Walker", "The spider ignores movement restrictions caused by webbing."),
    ],
    attacks=[
        Attack("Bite", 5, "1d8+3 piercing + 2d8 poison", "5 ft.", "The target must make a DC 11 Constitution saving throw, taking the poison damage on a failed save, or half as much damage on a successful one. If the poison damage reduces the target to 0 hit points, the target is stable but poisoned for 1 hour, even after regaining hit points, and is paralyzed while poisoned in this way."),
    ],
    actions=[
        Action("Web", "The spider shoots a mass of sticky webbing at a point within 30 feet. Each creature within 5 feet of that point must succeed on a DC 12 Dexterity saving throw or be restrained. A restrained creature can use its action to make a DC 12 Strength check, freeing itself on a success.", "5-6"),
    ],
)

# =============================================================================
# CR 1/2 MONSTERS (Additional)
# =============================================================================

GNOLL = Monster(
    name="Gnoll",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="chaotic evil",
    armor_class=15,
    hit_points=22,
    hit_dice="5d8",
    speed="30 ft.",
    strength=14, dexterity=12, constitution=11,
    intelligence=6, wisdom=10, charisma=7,
    challenge_rating="1/2",
    xp=100,
    languages="Gnoll",
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Rampage", "When the gnoll reduces a creature to 0 hit points with a melee attack on its turn, the gnoll can take a bonus action to move up to half its speed and make a bite attack."),
    ],
    attacks=[
        Attack("Bite", 4, "1d4+2 piercing", "5 ft."),
        Attack("Spear", 4, "1d6+2 piercing", "5 ft."),
        Attack("Longbow", 3, "1d8+1 piercing", "150/600 ft."),
    ],
)

RUST_MONSTER = Monster(
    name="Rust Monster",
    size=Size.MEDIUM,
    monster_type=MonsterType.MONSTROSITY,
    alignment="unaligned",
    armor_class=14,
    hit_points=27,
    hit_dice="5d8+5",
    speed="40 ft.",
    strength=13, dexterity=12, constitution=13,
    intelligence=2, wisdom=13, charisma=6,
    challenge_rating="1/2",
    xp=100,
    senses="darkvision 60 ft., passive Perception 11",
    traits=[
        Trait("Iron Scent", "The rust monster can pinpoint, by scent, the location of ferrous metal within 30 feet of it."),
        Trait("Rust Metal", "Any nonmagical weapon made of metal that hits the rust monster corrodes. After dealing damage, the weapon takes a permanent and cumulative -1 penalty to damage rolls. If its penalty drops to -5, the weapon is destroyed."),
    ],
    attacks=[
        Attack("Bite", 3, "1d8+1 piercing", "5 ft."),
        Attack("Antennae", 3, "rusts metal", "5 ft.", "The rust monster can touch a nonmagical ferrous metal object. If the object is either metal armor or a metal shield being worn or carried, it takes a permanent and cumulative -1 penalty to the AC it offers. If its penalty drops to -5, the armor is destroyed. If the object is a held metal weapon, it rusts as described in the Rust Metal trait."),
    ],
)

WORG = Monster(
    name="Worg",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="neutral evil",
    armor_class=13,
    hit_points=26,
    hit_dice="4d10+4",
    speed="50 ft.",
    strength=16, dexterity=13, constitution=13,
    intelligence=7, wisdom=11, charisma=8,
    challenge_rating="1/2",
    xp=100,
    skills=["Perception +4"],
    languages="Goblin, Worg",
    senses="darkvision 60 ft., passive Perception 14",
    traits=[
        Trait("Keen Hearing and Smell", "The worg has advantage on Wisdom (Perception) checks that rely on hearing or smell."),
    ],
    attacks=[
        Attack("Bite", 5, "2d6+3 piercing", "5 ft.", "If the target is a creature, it must succeed on a DC 13 Strength saving throw or be knocked prone."),
    ],
)

# =============================================================================
# CR 1 MONSTERS (Additional)
# =============================================================================

SPECTER = Monster(
    name="Specter",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="chaotic evil",
    armor_class=12,
    hit_points=22,
    hit_dice="5d8",
    speed="0 ft., fly 50 ft. (hover)",
    strength=1, dexterity=14, constitution=11,
    intelligence=10, wisdom=10, charisma=11,
    challenge_rating="1",
    xp=200,
    damage_resistances=["acid", "cold", "fire", "lightning", "thunder", "bludgeoning, piercing, and slashing from nonmagical attacks"],
    damage_immunities=["necrotic", "poison"],
    condition_immunities=["charmed", "exhaustion", "grappled", "paralyzed", "petrified", "poisoned", "prone", "restrained", "unconscious"],
    senses="darkvision 60 ft., passive Perception 10",
    languages="understands languages it knew in life but can't speak",
    traits=[
        Trait("Incorporeal Movement", "The specter can move through other creatures and objects as if they were difficult terrain. It takes 5 (1d10) force damage if it ends its turn inside an object."),
        Trait("Sunlight Sensitivity", "While in sunlight, the specter has disadvantage on attack rolls, as well as on Wisdom (Perception) checks that rely on sight."),
    ],
    attacks=[
        Attack("Life Drain", 4, "3d6 necrotic", "5 ft.", "The target must succeed on a DC 10 Constitution saving throw or its hit point maximum is reduced by an amount equal to the damage taken. This reduction lasts until the creature finishes a long rest. The target dies if this effect reduces its hit point maximum to 0."),
    ],
)

DRYAD = Monster(
    name="Dryad",
    size=Size.MEDIUM,
    monster_type=MonsterType.FEY,
    alignment="neutral",
    armor_class=11,
    hit_points=22,
    hit_dice="5d8",
    speed="30 ft.",
    strength=10, dexterity=12, constitution=11,
    intelligence=14, wisdom=15, charisma=18,
    challenge_rating="1",
    xp=200,
    skills=["Perception +4", "Stealth +5"],
    languages="Elvish, Sylvan",
    senses="darkvision 60 ft., passive Perception 14",
    traits=[
        Trait("Magic Resistance", "The dryad has advantage on saving throws against spells and other magical effects."),
        Trait("Speak with Beasts and Plants", "The dryad can communicate with beasts and plants as if they shared a language."),
        Trait("Tree Stride", "Once on her turn, the dryad can use 10 feet of her movement to step magically into one living tree within her reach and emerge from a second living tree within 60 feet of the first tree, appearing in an unoccupied space within 5 feet of the second tree."),
    ],
    attacks=[
        Attack("Club", 2, "1d4 bludgeoning", "5 ft."),
    ],
    actions=[
        Action("Fey Charm", "The dryad targets one humanoid or beast that she can see within 30 feet. If the target can see the dryad, it must succeed on a DC 14 Wisdom saving throw or be magically charmed. The charmed creature regards the dryad as a trusted friend. The charm lasts for 24 hours or until the dryad or her allies harm the target."),
    ],
)

HARPY = Monster(
    name="Harpy",
    size=Size.MEDIUM,
    monster_type=MonsterType.MONSTROSITY,
    alignment="chaotic evil",
    armor_class=11,
    hit_points=38,
    hit_dice="7d8+7",
    speed="20 ft., fly 40 ft.",
    strength=12, dexterity=13, constitution=12,
    intelligence=7, wisdom=10, charisma=13,
    challenge_rating="1",
    xp=200,
    languages="Common",
    senses="passive Perception 10",
    attacks=[
        Attack("Claws", 3, "2d4+1 slashing", "5 ft."),
        Attack("Club", 3, "1d4+1 bludgeoning", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The harpy makes two attacks: one with its claws and one with its club."),
        Action("Luring Song", "The harpy sings a magical melody. Every humanoid and giant within 300 feet that can hear the song must succeed on a DC 11 Wisdom saving throw or be charmed until the song ends. While charmed, a target is incapacitated and ignores all other songs. If the charmed target is more than 5 feet away from the harpy, the target must move on its turn toward the harpy by the most direct route. It doesn't avoid opportunity attacks, but before moving into damaging terrain, such as lava or a pit, and whenever it takes damage from a source other than the harpy, a target can repeat the saving throw."),
    ],
)

# =============================================================================
# CR 2 MONSTERS (Additional)
# =============================================================================

GELATINOUS_CUBE = Monster(
    name="Gelatinous Cube",
    size=Size.LARGE,
    monster_type=MonsterType.OOZE,
    alignment="unaligned",
    armor_class=6,
    hit_points=84,
    hit_dice="8d10+40",
    speed="15 ft.",
    strength=14, dexterity=3, constitution=20,
    intelligence=1, wisdom=6, charisma=1,
    challenge_rating="2",
    xp=450,
    condition_immunities=["blinded", "charmed", "deafened", "exhaustion", "frightened", "prone"],
    senses="blindsight 60 ft. (blind beyond this radius), passive Perception 8",
    traits=[
        Trait("Ooze Cube", "The cube takes up its entire space. Other creatures can enter the space, but a creature that does so is subjected to the cube's Engulf and has disadvantage on the saving throw. Creatures inside the cube can be seen but have total cover."),
        Trait("Transparent", "Even when the cube is in plain sight, it takes a successful DC 15 Wisdom (Perception) check to spot a cube that has neither moved nor attacked. A creature that tries to enter the cube's space while unaware of the cube is surprised by the cube."),
    ],
    attacks=[
        Attack("Pseudopod", 4, "3d6 acid", "5 ft."),
    ],
    actions=[
        Action("Engulf", "The cube moves up to its speed. While doing so, it can enter Large or smaller creatures' spaces. Whenever the cube enters a creature's space, the creature must make a DC 12 Dexterity saving throw. On a successful save, the creature can choose to be pushed 5 feet back or to the side of the cube. A creature that chooses not to be pushed suffers the consequences of a failed saving throw. On a failed save, the cube enters the creature's space, and the creature takes 10 (3d6) acid damage and is engulfed. The engulfed creature can't breathe, is restrained, and takes 21 (6d6) acid damage at the start of each of the cube's turns. When the cube moves, the engulfed creature moves with it. An engulfed creature can try to escape by taking an action to make a DC 12 Strength check. On a success, the creature escapes and enters a space of its choice within 5 feet of the cube."),
    ],
)

GARGOYLE = Monster(
    name="Gargoyle",
    size=Size.MEDIUM,
    monster_type=MonsterType.ELEMENTAL,
    alignment="chaotic evil",
    armor_class=15,
    hit_points=52,
    hit_dice="7d8+21",
    speed="30 ft., fly 60 ft.",
    strength=15, dexterity=11, constitution=16,
    intelligence=6, wisdom=11, charisma=7,
    challenge_rating="2",
    xp=450,
    damage_resistances=["bludgeoning, piercing, and slashing from nonmagical attacks not made with adamantine weapons"],
    damage_immunities=["poison"],
    condition_immunities=["exhaustion", "petrified", "poisoned"],
    languages="Terran",
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("False Appearance", "While the gargoyle remains motionless, it is indistinguishable from an inanimate statue."),
    ],
    attacks=[
        Attack("Bite", 4, "1d6+2 piercing", "5 ft."),
        Attack("Claws", 4, "1d6+2 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The gargoyle makes two attacks: one with its bite and one with its claws."),
    ],
)

BASILISK = Monster(
    name="Basilisk",
    size=Size.MEDIUM,
    monster_type=MonsterType.MONSTROSITY,
    alignment="unaligned",
    armor_class=15,
    hit_points=52,
    hit_dice="8d8+16",
    speed="20 ft.",
    strength=16, dexterity=8, constitution=15,
    intelligence=2, wisdom=8, charisma=7,
    challenge_rating="3",
    xp=700,
    senses="darkvision 60 ft., passive Perception 9",
    traits=[
        Trait("Petrifying Gaze", "If a creature starts its turn within 30 feet of the basilisk and the two of them can see each other, the basilisk can force the creature to make a DC 12 Constitution saving throw if the basilisk isn't incapacitated. On a failed save, the creature magically begins to turn to stone and is restrained. It must repeat the saving throw at the end of its next turn. On a success, the effect ends. On a failure, the creature is petrified until freed by the greater restoration spell or other magic."),
    ],
    attacks=[
        Attack("Bite", 5, "2d6+3 piercing + 2d6 poison", "5 ft."),
    ],
)

# =============================================================================
# CR 3 MONSTERS (Additional)
# =============================================================================

HELL_HOUND = Monster(
    name="Hell Hound",
    size=Size.MEDIUM,
    monster_type=MonsterType.FIEND,
    alignment="lawful evil",
    armor_class=15,
    hit_points=45,
    hit_dice="7d8+14",
    speed="50 ft.",
    strength=17, dexterity=12, constitution=14,
    intelligence=6, wisdom=13, charisma=6,
    challenge_rating="3",
    xp=700,
    skills=["Perception +5"],
    damage_immunities=["fire"],
    languages="understands Infernal but can't speak",
    senses="darkvision 60 ft., passive Perception 15",
    traits=[
        Trait("Keen Hearing and Smell", "The hound has advantage on Wisdom (Perception) checks that rely on hearing or smell."),
        Trait("Pack Tactics", "The hound has advantage on attack rolls against a creature if at least one of the hound's allies is within 5 feet of the creature and the ally isn't incapacitated."),
    ],
    attacks=[
        Attack("Bite", 5, "1d8+3 piercing + 2d6 fire", "5 ft."),
    ],
    actions=[
        Action("Fire Breath", "The hound exhales fire in a 15-foot cone. Each creature in that area must make a DC 12 Dexterity saving throw, taking 21 (6d6) fire damage on a failed save, or half as much damage on a successful one.", "5-6"),
    ],
)

PHASE_SPIDER = Monster(
    name="Phase Spider",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="unaligned",
    armor_class=13,
    hit_points=32,
    hit_dice="5d10+5",
    speed="30 ft., climb 30 ft.",
    strength=15, dexterity=15, constitution=12,
    intelligence=6, wisdom=10, charisma=6,
    challenge_rating="3",
    xp=700,
    skills=["Stealth +6"],
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Ethereal Jaunt", "As a bonus action, the spider can magically shift from the Material Plane to the Ethereal Plane, or vice versa."),
        Trait("Spider Climb", "The spider can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check."),
        Trait("Web Walker", "The spider ignores movement restrictions caused by webbing."),
    ],
    attacks=[
        Attack("Bite", 4, "1d10+2 piercing + 4d8 poison", "5 ft.", "The target must make a DC 11 Constitution saving throw, taking the poison damage on a failed save, or half as much damage on a successful one. If the poison damage reduces the target to 0 hit points, the target is stable but poisoned for 1 hour and paralyzed while poisoned."),
    ],
)

MANTICORE = Monster(
    name="Manticore",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="lawful evil",
    armor_class=14,
    hit_points=68,
    hit_dice="8d10+24",
    speed="30 ft., fly 50 ft.",
    strength=17, dexterity=16, constitution=17,
    intelligence=7, wisdom=12, charisma=8,
    challenge_rating="3",
    xp=700,
    senses="darkvision 60 ft., passive Perception 11",
    languages="Common",
    traits=[
        Trait("Tail Spike Regrowth", "The manticore has twenty-four tail spikes. Used spikes regrow when the manticore finishes a long rest."),
    ],
    attacks=[
        Attack("Bite", 5, "1d8+3 piercing", "5 ft."),
        Attack("Claw", 5, "1d6+3 slashing", "5 ft."),
        Attack("Tail Spike", 5, "1d8+3 piercing", "100/200 ft."),
    ],
    actions=[
        Action("Multiattack", "The manticore makes three attacks: one with its bite and two with its claws or three with its tail spikes."),
    ],
)

# =============================================================================
# CR 4 MONSTERS
# =============================================================================

ETTIN = Monster(
    name="Ettin",
    size=Size.LARGE,
    monster_type=MonsterType.GIANT,
    alignment="chaotic evil",
    armor_class=12,
    hit_points=85,
    hit_dice="10d10+30",
    speed="40 ft.",
    strength=21, dexterity=8, constitution=17,
    intelligence=6, wisdom=10, charisma=8,
    challenge_rating="4",
    xp=1100,
    skills=["Perception +4"],
    languages="Giant, Orc",
    senses="darkvision 60 ft., passive Perception 14",
    traits=[
        Trait("Two Heads", "The ettin has advantage on Wisdom (Perception) checks and on saving throws against being blinded, charmed, deafened, frightened, stunned, and knocked unconscious."),
        Trait("Wakeful", "When one of the ettin's heads is asleep, its other head is awake."),
    ],
    attacks=[
        Attack("Battleaxe", 7, "2d8+5 slashing", "5 ft."),
        Attack("Morningstar", 7, "2d8+5 piercing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The ettin makes two attacks: one with its battleaxe and one with its morningstar."),
    ],
)

GHOST = Monster(
    name="Ghost",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="any alignment",
    armor_class=11,
    hit_points=45,
    hit_dice="10d8",
    speed="0 ft., fly 40 ft. (hover)",
    strength=7, dexterity=13, constitution=10,
    intelligence=10, wisdom=12, charisma=17,
    challenge_rating="4",
    xp=1100,
    damage_resistances=["acid", "fire", "lightning", "thunder", "bludgeoning, piercing, and slashing from nonmagical attacks"],
    damage_immunities=["cold", "necrotic", "poison"],
    condition_immunities=["charmed", "exhaustion", "frightened", "grappled", "paralyzed", "petrified", "poisoned", "prone", "restrained"],
    languages="any languages it knew in life",
    senses="darkvision 60 ft., passive Perception 11",
    traits=[
        Trait("Ethereal Sight", "The ghost can see 60 feet into the Ethereal Plane when it is on the Material Plane, and vice versa."),
        Trait("Incorporeal Movement", "The ghost can move through other creatures and objects as if they were difficult terrain. It takes 5 (1d10) force damage if it ends its turn inside an object."),
    ],
    attacks=[
        Attack("Withering Touch", 5, "4d6+3 necrotic", "5 ft."),
    ],
    actions=[
        Action("Etherealness", "The ghost enters the Ethereal Plane from the Material Plane, or vice versa. It is visible on the Material Plane while it is in the Border Ethereal, and vice versa, yet it can't affect or be affected by anything on the other plane."),
        Action("Horrifying Visage", "Each non-undead creature within 60 feet of the ghost that can see it must succeed on a DC 13 Wisdom saving throw or be frightened for 1 minute. If the save fails by 5 or more, the target also ages 1d4 x 10 years. A frightened target can repeat the saving throw at the end of each of its turns, ending the frightened condition on itself on a success."),
        Action("Possession", "One humanoid that the ghost can see within 5 feet of it must succeed on a DC 13 Charisma saving throw or be possessed by the ghost; the ghost then disappears, and the target is incapacitated and loses control of its body. The ghost now controls the body but doesn't deprive the target of awareness. The possession lasts until the body drops to 0 hit points, the ghost ends it as a bonus action, or the ghost is turned or forced out by an effect like the dispel evil and good spell.", "short rest"),
    ],
)

# =============================================================================
# CR 5 MONSTERS (Additional)
# =============================================================================

WRAITH = Monster(
    name="Wraith",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="neutral evil",
    armor_class=13,
    hit_points=67,
    hit_dice="9d8+27",
    speed="0 ft., fly 60 ft. (hover)",
    strength=6, dexterity=16, constitution=16,
    intelligence=12, wisdom=14, charisma=15,
    challenge_rating="5",
    xp=1800,
    damage_resistances=["acid", "cold", "fire", "lightning", "thunder", "bludgeoning, piercing, and slashing from nonmagical attacks not made with silvered weapons"],
    damage_immunities=["necrotic", "poison"],
    condition_immunities=["charmed", "exhaustion", "grappled", "paralyzed", "petrified", "poisoned", "prone", "restrained"],
    languages="the languages it knew in life",
    senses="darkvision 60 ft., passive Perception 12",
    traits=[
        Trait("Incorporeal Movement", "The wraith can move through other creatures and objects as if they were difficult terrain. It takes 5 (1d10) force damage if it ends its turn inside an object."),
        Trait("Sunlight Sensitivity", "While in sunlight, the wraith has disadvantage on attack rolls, as well as on Wisdom (Perception) checks that rely on sight."),
    ],
    attacks=[
        Attack("Life Drain", 6, "4d8+3 necrotic", "5 ft.", "The target must succeed on a DC 14 Constitution saving throw or its hit point maximum is reduced by an amount equal to the damage taken. This reduction lasts until the target finishes a long rest. The target dies if this effect reduces its hit point maximum to 0."),
    ],
    actions=[
        Action("Create Specter", "The wraith targets a humanoid within 10 feet of it that has been dead for no longer than 1 minute and died violently. The target's spirit rises as a specter in the space of its corpse or in the nearest unoccupied space. The specter is under the wraith's control. The wraith can have no more than seven specters under its control at one time."),
    ],
)

HILL_GIANT = Monster(
    name="Hill Giant",
    size=Size.HUGE,
    monster_type=MonsterType.GIANT,
    alignment="chaotic evil",
    armor_class=13,
    hit_points=105,
    hit_dice="10d12+40",
    speed="40 ft.",
    strength=21, dexterity=8, constitution=19,
    intelligence=5, wisdom=9, charisma=6,
    challenge_rating="5",
    xp=1800,
    skills=["Perception +2"],
    languages="Giant",
    senses="passive Perception 12",
    attacks=[
        Attack("Greatclub", 8, "3d8+5 bludgeoning", "10 ft."),
        Attack("Rock", 8, "3d10+5 bludgeoning", "60/240 ft."),
    ],
    actions=[
        Action("Multiattack", "The giant makes two greatclub attacks."),
    ],
)

# =============================================================================
# CR 6+ MONSTERS
# =============================================================================

MEDUSA = Monster(
    name="Medusa",
    size=Size.MEDIUM,
    monster_type=MonsterType.MONSTROSITY,
    alignment="lawful evil",
    armor_class=15,
    hit_points=127,
    hit_dice="17d8+51",
    speed="30 ft.",
    strength=10, dexterity=15, constitution=16,
    intelligence=12, wisdom=13, charisma=15,
    challenge_rating="6",
    xp=2300,
    skills=["Deception +5", "Insight +4", "Perception +4", "Stealth +5"],
    senses="darkvision 60 ft., passive Perception 14",
    languages="Common",
    traits=[
        Trait("Petrifying Gaze", "When a creature that can see the medusa's eyes starts its turn within 30 feet of the medusa, the medusa can force it to make a DC 14 Constitution saving throw if the medusa isn't incapacitated and can see the creature. If the saving throw fails by 5 or more, the creature is instantly petrified. Otherwise, a creature that fails the save begins to turn to stone and is restrained. The restrained creature must repeat the saving throw at the end of its next turn, becoming petrified on a failure or ending the effect on a success."),
    ],
    attacks=[
        Attack("Snake Hair", 5, "1d4+2 piercing + 4d6 poison", "5 ft."),
        Attack("Shortsword", 5, "1d6+2 piercing", "5 ft."),
        Attack("Longbow", 5, "1d8+2 piercing + 2d6 poison", "150/600 ft."),
    ],
    actions=[
        Action("Multiattack", "The medusa makes either three melee attacks (one with its snake hair and two with its shortsword) or two ranged attacks with its longbow."),
    ],
)

CHIMERA = Monster(
    name="Chimera",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="chaotic evil",
    armor_class=14,
    hit_points=114,
    hit_dice="12d10+48",
    speed="30 ft., fly 60 ft.",
    strength=19, dexterity=11, constitution=19,
    intelligence=3, wisdom=14, charisma=10,
    challenge_rating="6",
    xp=2300,
    skills=["Perception +8"],
    senses="darkvision 60 ft., passive Perception 18",
    languages="understands Draconic but can't speak",
    attacks=[
        Attack("Bite", 7, "2d6+4 piercing", "5 ft."),
        Attack("Horns", 7, "1d12+4 bludgeoning", "5 ft."),
        Attack("Claws", 7, "2d6+4 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The chimera makes three attacks: one with its bite, one with its horns, and one with its claws. When its fire breath is available, it can use the breath in place of its bite or horns."),
        Action("Fire Breath", "The dragon head exhales fire in a 15-foot cone. Each creature in that area must make a DC 15 Dexterity saving throw, taking 31 (7d8) fire damage on a failed save, or half as much damage on a successful one.", "5-6"),
    ],
)

YOUNG_BLACK_DRAGON = Monster(
    name="Young Black Dragon",
    size=Size.LARGE,
    monster_type=MonsterType.DRAGON,
    alignment="chaotic evil",
    armor_class=18,
    hit_points=127,
    hit_dice="15d10+45",
    speed="40 ft., fly 80 ft., swim 40 ft.",
    strength=19, dexterity=14, constitution=17,
    intelligence=12, wisdom=11, charisma=15,
    challenge_rating="7",
    xp=2900,
    saving_throws=["Dex +5", "Con +6", "Wis +3", "Cha +5"],
    skills=["Perception +6", "Stealth +5"],
    damage_immunities=["acid"],
    senses="blindsight 30 ft., darkvision 120 ft., passive Perception 16",
    languages="Common, Draconic",
    traits=[
        Trait("Amphibious", "The dragon can breathe air and water."),
    ],
    attacks=[
        Attack("Bite", 7, "2d10+4 piercing + 1d8 acid", "10 ft."),
        Attack("Claw", 7, "2d6+4 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The dragon makes three attacks: one with its bite and two with its claws."),
        Action("Acid Breath", "The dragon exhales acid in a 30-foot line that is 5 feet wide. Each creature in that line must make a DC 14 Dexterity saving throw, taking 49 (11d8) acid damage on a failed save, or half as much damage on a successful one.", "5-6"),
    ],
)

# =============================================================================
# CR 0 MONSTERS (Additional)
# =============================================================================

COMMONER = Monster(
    name="Commoner",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="any alignment",
    armor_class=10,
    hit_points=4,
    hit_dice="1d8",
    speed="30 ft.",
    strength=10, dexterity=10, constitution=10,
    intelligence=10, wisdom=10, charisma=10,
    challenge_rating="0",
    xp=10,
    languages="any one language (usually Common)",
    senses="passive Perception 10",
    attacks=[
        Attack("Club", 2, "1d4 bludgeoning", "5 ft."),
    ],
    description="Commoners include peasants, serfs, slaves, servants, pilgrims, merchants, artisans, and hermits.",
)

FROG = Monster(
    name="Frog",
    size=Size.TINY,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=11,
    hit_points=1,
    hit_dice="1d4-1",
    speed="20 ft., swim 20 ft.",
    strength=1, dexterity=13, constitution=8,
    intelligence=1, wisdom=8, charisma=3,
    challenge_rating="0",
    xp=0,
    skills=["Perception +1", "Stealth +3"],
    senses="darkvision 30 ft., passive Perception 11",
    traits=[
        Trait("Amphibious", "The frog can breathe air and water."),
        Trait("Standing Leap", "The frog's long jump is up to 10 feet and its high jump is up to 5 feet, with or without a running start."),
    ],
)

CAT = Monster(
    name="Cat",
    size=Size.TINY,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=12,
    hit_points=2,
    hit_dice="1d4",
    speed="40 ft., climb 30 ft.",
    strength=3, dexterity=15, constitution=10,
    intelligence=3, wisdom=12, charisma=7,
    challenge_rating="0",
    xp=10,
    skills=["Perception +3", "Stealth +4"],
    senses="passive Perception 13",
    traits=[
        Trait("Keen Smell", "The cat has advantage on Wisdom (Perception) checks that rely on smell."),
    ],
    attacks=[
        Attack("Claws", 0, "1 slashing", "5 ft."),
    ],
)

# =============================================================================
# CR 1/8 MONSTERS (Additional)
# =============================================================================

MASTIFF = Monster(
    name="Mastiff",
    size=Size.MEDIUM,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=12,
    hit_points=5,
    hit_dice="1d8+1",
    speed="40 ft.",
    strength=13, dexterity=14, constitution=12,
    intelligence=3, wisdom=12, charisma=7,
    challenge_rating="1/8",
    xp=25,
    skills=["Perception +3"],
    senses="passive Perception 13",
    traits=[
        Trait("Keen Hearing and Smell", "The mastiff has advantage on Wisdom (Perception) checks that rely on hearing or smell."),
    ],
    attacks=[
        Attack("Bite", 3, "1d6+1 piercing", "5 ft.", "If the target is a creature, it must succeed on a DC 11 Strength saving throw or be knocked prone."),
    ],
)

TRIBAL_WARRIOR = Monster(
    name="Tribal Warrior",
    size=Size.MEDIUM,
    monster_type=MonsterType.HUMANOID,
    alignment="any alignment",
    armor_class=12,
    hit_points=11,
    hit_dice="2d8+2",
    speed="30 ft.",
    strength=13, dexterity=11, constitution=12,
    intelligence=8, wisdom=11, charisma=8,
    challenge_rating="1/8",
    xp=25,
    languages="any one language",
    senses="passive Perception 10",
    traits=[
        Trait("Pack Tactics", "The warrior has advantage on attack rolls against a creature if at least one of the warrior's allies is within 5 feet of the creature and the ally isn't incapacitated."),
    ],
    attacks=[
        Attack("Spear", 3, "1d6+1 piercing", "5 ft."),
        Attack("Spear (Thrown)", 3, "1d6+1 piercing", "20/60 ft."),
    ],
)

# =============================================================================
# CR 1/4 MONSTERS (Additional)
# =============================================================================

GIANT_WOLF_SPIDER = Monster(
    name="Giant Wolf Spider",
    size=Size.MEDIUM,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=13,
    hit_points=11,
    hit_dice="2d8+2",
    speed="40 ft., climb 40 ft.",
    strength=12, dexterity=16, constitution=13,
    intelligence=3, wisdom=12, charisma=4,
    challenge_rating="1/4",
    xp=50,
    skills=["Perception +3", "Stealth +7"],
    senses="blindsight 10 ft., darkvision 60 ft., passive Perception 13",
    traits=[
        Trait("Spider Climb", "The spider can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check."),
        Trait("Web Sense", "While in contact with a web, the spider knows the exact location of any other creature in contact with the same web."),
        Trait("Web Walker", "The spider ignores movement restrictions caused by webbing."),
    ],
    attacks=[
        Attack("Bite", 3, "1d6+1 piercing + 2d6 poison", "5 ft.", "The target must make a DC 11 Constitution saving throw, taking the poison damage on a failed save, or half as much damage on a successful one. If the poison damage reduces the target to 0 hit points, the target is stable but poisoned for 1 hour, and paralyzed while poisoned."),
    ],
)

FLYING_SWORD = Monster(
    name="Flying Sword",
    size=Size.SMALL,
    monster_type=MonsterType.CONSTRUCT,
    alignment="unaligned",
    armor_class=17,
    hit_points=17,
    hit_dice="5d6",
    speed="0 ft., fly 50 ft. (hover)",
    strength=12, dexterity=15, constitution=11,
    intelligence=1, wisdom=5, charisma=1,
    challenge_rating="1/4",
    xp=50,
    saving_throws=["Dex +4"],
    damage_immunities=["poison", "psychic"],
    condition_immunities=["blinded", "charmed", "deafened", "frightened", "paralyzed", "petrified", "poisoned"],
    senses="blindsight 60 ft. (blind beyond this radius), passive Perception 7",
    traits=[
        Trait("Antimagic Susceptibility", "The sword is incapacitated while in the area of an antimagic field. If targeted by dispel magic, the sword must succeed on a Constitution saving throw against the caster's spell save DC or fall unconscious for 1 minute."),
        Trait("False Appearance", "While the sword remains motionless and isn't flying, it is indistinguishable from a normal sword."),
    ],
    attacks=[
        Attack("Longsword", 3, "1d8+1 slashing", "5 ft."),
    ],
)

PIXIE = Monster(
    name="Pixie",
    size=Size.TINY,
    monster_type=MonsterType.FEY,
    alignment="neutral good",
    armor_class=15,
    hit_points=1,
    hit_dice="1d4-1",
    speed="10 ft., fly 30 ft.",
    strength=2, dexterity=20, constitution=8,
    intelligence=10, wisdom=14, charisma=15,
    challenge_rating="1/4",
    xp=50,
    skills=["Perception +4", "Stealth +7"],
    languages="Sylvan",
    senses="passive Perception 14",
    traits=[
        Trait("Magic Resistance", "The pixie has advantage on saving throws against spells and other magical effects."),
    ],
    actions=[
        Action("Superior Invisibility", "The pixie magically turns invisible until its concentration ends (as if concentrating on a spell). Any equipment the pixie wears or carries is invisible with it."),
    ],
    description="A pixie is a tiny fey creature known for mischief and magic.",
)

SPRITE = Monster(
    name="Sprite",
    size=Size.TINY,
    monster_type=MonsterType.FEY,
    alignment="neutral good",
    armor_class=15,
    hit_points=2,
    hit_dice="1d4",
    speed="10 ft., fly 40 ft.",
    strength=3, dexterity=18, constitution=10,
    intelligence=14, wisdom=13, charisma=11,
    challenge_rating="1/4",
    xp=50,
    skills=["Perception +3", "Stealth +8"],
    languages="Common, Elvish, Sylvan",
    senses="passive Perception 13",
    attacks=[
        Attack("Longsword", 2, "1 slashing", "5 ft."),
        Attack("Shortbow", 6, "1 piercing + poison", "40/160 ft.", "The target must succeed on a DC 10 Constitution saving throw or become poisoned for 1 minute. If its saving throw result is 5 or lower, the poisoned target falls unconscious for the same duration, or until it takes damage or another creature takes an action to shake it awake."),
    ],
    actions=[
        Action("Heart Sight", "The sprite touches a creature and magically knows the creature's current emotional state. If the target fails a DC 10 Charisma saving throw, the sprite also knows the creature's alignment."),
        Action("Invisibility", "The sprite magically turns invisible until it attacks or casts a spell, or until its concentration ends."),
    ],
)

# =============================================================================
# CR 1/2 MONSTERS (Additional)
# =============================================================================

COCKATRICE = Monster(
    name="Cockatrice",
    size=Size.SMALL,
    monster_type=MonsterType.MONSTROSITY,
    alignment="unaligned",
    armor_class=11,
    hit_points=27,
    hit_dice="6d6+6",
    speed="20 ft., fly 40 ft.",
    strength=6, dexterity=12, constitution=12,
    intelligence=2, wisdom=13, charisma=5,
    challenge_rating="1/2",
    xp=100,
    senses="darkvision 60 ft., passive Perception 11",
    attacks=[
        Attack("Bite", 3, "1d4+1 piercing", "5 ft.", "The target must succeed on a DC 11 Constitution saving throw against being magically petrified. On a failed save, the creature begins to turn to stone and is restrained. It must repeat the saving throw at the end of its next turn. On a success, the effect ends. On a failure, the creature is petrified for 24 hours."),
    ],
)

DARKMANTLE = Monster(
    name="Darkmantle",
    size=Size.SMALL,
    monster_type=MonsterType.MONSTROSITY,
    alignment="unaligned",
    armor_class=11,
    hit_points=22,
    hit_dice="5d6+5",
    speed="10 ft., fly 30 ft.",
    strength=16, dexterity=12, constitution=13,
    intelligence=2, wisdom=10, charisma=5,
    challenge_rating="1/2",
    xp=100,
    skills=["Stealth +3"],
    senses="blindsight 60 ft., passive Perception 10",
    traits=[
        Trait("Echolocation", "The darkmantle can't use its blindsight while deafened."),
        Trait("False Appearance", "While the darkmantle remains motionless, it is indistinguishable from a cave formation such as a stalactite or stalagmite."),
    ],
    attacks=[
        Attack("Crush", 5, "1d6+3 bludgeoning", "5 ft.", "The darkmantle attaches to the target. If the target is Medium or smaller and the darkmantle has advantage on the attack roll, it attaches by engulfing the target's head, and the target is also blinded and unable to breathe while the darkmantle is attached."),
    ],
    actions=[
        Action("Darkness Aura", "A 15-foot radius of magical darkness extends out from the darkmantle, moves with it, and spreads around corners. The darkness lasts as long as the darkmantle maintains concentration, up to 10 minutes. Darkvision can't penetrate this darkness, and no natural light can illuminate it.", "short rest"),
    ],
)

GRAY_OOZE = Monster(
    name="Gray Ooze",
    size=Size.MEDIUM,
    monster_type=MonsterType.OOZE,
    alignment="unaligned",
    armor_class=8,
    hit_points=22,
    hit_dice="3d8+9",
    speed="10 ft., climb 10 ft.",
    strength=12, dexterity=6, constitution=16,
    intelligence=1, wisdom=6, charisma=2,
    challenge_rating="1/2",
    xp=100,
    skills=["Stealth +2"],
    damage_resistances=["acid", "cold", "fire"],
    condition_immunities=["blinded", "charmed", "deafened", "exhaustion", "frightened", "prone"],
    senses="blindsight 60 ft. (blind beyond this radius), passive Perception 8",
    traits=[
        Trait("Amorphous", "The ooze can move through a space as narrow as 1 inch wide without squeezing."),
        Trait("Corrode Metal", "Any nonmagical weapon made of metal that hits the ooze corrodes. After dealing damage, the weapon takes a permanent and cumulative -1 penalty to damage rolls. If its penalty drops to -5, the weapon is destroyed."),
        Trait("False Appearance", "While the ooze remains motionless, it is indistinguishable from an oily pool or wet rock."),
    ],
    attacks=[
        Attack("Pseudopod", 3, "1d6+1 bludgeoning + 2d6 acid", "5 ft.", "If the target is wearing nonmagical metal armor, its armor is partly corroded and takes a permanent and cumulative -1 penalty to the AC it offers. The armor is destroyed if the penalty reduces its AC to 10."),
    ],
)

MAGMIN = Monster(
    name="Magmin",
    size=Size.SMALL,
    monster_type=MonsterType.ELEMENTAL,
    alignment="chaotic neutral",
    armor_class=14,
    hit_points=9,
    hit_dice="2d6+2",
    speed="30 ft.",
    strength=7, dexterity=15, constitution=12,
    intelligence=8, wisdom=11, charisma=10,
    challenge_rating="1/2",
    xp=100,
    damage_resistances=["bludgeoning, piercing, and slashing from nonmagical attacks"],
    damage_immunities=["fire"],
    languages="Ignan",
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Death Burst", "When the magmin dies, it explodes in a burst of fire and magma. Each creature within 10 feet of it must make a DC 11 Dexterity saving throw, taking 7 (2d6) fire damage on a failed save, or half as much damage on a successful one. Flammable objects that aren't being worn or carried in that area are ignited."),
        Trait("Ignited Illumination", "As a bonus action, the magmin can set itself ablaze or extinguish its flames. While ablaze, the magmin sheds bright light in a 10-foot radius and dim light for an additional 10 feet."),
    ],
    attacks=[
        Attack("Touch", 4, "2d6 fire", "5 ft.", "If the target is a creature or a flammable object, it ignites. Until a creature takes an action to douse the fire, the target takes 3 (1d6) fire damage at the end of each of its turns."),
    ],
)

# =============================================================================
# CR 1 MONSTERS (Additional)
# =============================================================================

ANIMATED_ARMOR = Monster(
    name="Animated Armor",
    size=Size.MEDIUM,
    monster_type=MonsterType.CONSTRUCT,
    alignment="unaligned",
    armor_class=18,
    hit_points=33,
    hit_dice="6d8+6",
    speed="25 ft.",
    strength=14, dexterity=11, constitution=13,
    intelligence=1, wisdom=3, charisma=1,
    challenge_rating="1",
    xp=200,
    damage_immunities=["poison", "psychic"],
    condition_immunities=["blinded", "charmed", "deafened", "exhaustion", "frightened", "paralyzed", "petrified", "poisoned"],
    senses="blindsight 60 ft. (blind beyond this radius), passive Perception 6",
    traits=[
        Trait("Antimagic Susceptibility", "The armor is incapacitated while in the area of an antimagic field. If targeted by dispel magic, the armor must succeed on a Constitution saving throw against the caster's spell save DC or fall unconscious for 1 minute."),
        Trait("False Appearance", "While the armor remains motionless, it is indistinguishable from a normal suit of armor."),
    ],
    attacks=[
        Attack("Slam", 4, "1d6+2 bludgeoning", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The armor makes two melee attacks."),
    ],
)

DEATH_DOG = Monster(
    name="Death Dog",
    size=Size.MEDIUM,
    monster_type=MonsterType.MONSTROSITY,
    alignment="neutral evil",
    armor_class=12,
    hit_points=39,
    hit_dice="6d8+12",
    speed="40 ft.",
    strength=15, dexterity=14, constitution=14,
    intelligence=3, wisdom=13, charisma=6,
    challenge_rating="1",
    xp=200,
    skills=["Perception +5", "Stealth +4"],
    senses="darkvision 120 ft., passive Perception 15",
    traits=[
        Trait("Two-Headed", "The dog has advantage on Wisdom (Perception) checks and on saving throws against being blinded, charmed, deafened, frightened, stunned, or knocked unconscious."),
    ],
    attacks=[
        Attack("Bite", 4, "1d6+2 piercing", "5 ft.", "If the target is a creature, it must succeed on a DC 12 Constitution saving throw against disease or become poisoned until the disease is cured. Every 24 hours that elapse, the creature must repeat the saving throw, reducing its hit point maximum by 5 (1d10) on a failure."),
    ],
    actions=[
        Action("Multiattack", "The dog makes two bite attacks."),
    ],
)

GIANT_HYENA = Monster(
    name="Giant Hyena",
    size=Size.LARGE,
    monster_type=MonsterType.BEAST,
    alignment="unaligned",
    armor_class=12,
    hit_points=45,
    hit_dice="6d10+12",
    speed="50 ft.",
    strength=16, dexterity=14, constitution=14,
    intelligence=2, wisdom=12, charisma=7,
    challenge_rating="1",
    xp=200,
    skills=["Perception +3"],
    senses="passive Perception 13",
    traits=[
        Trait("Rampage", "When the hyena reduces a creature to 0 hit points with a melee attack on its turn, the hyena can take a bonus action to move up to half its speed and make a bite attack."),
    ],
    attacks=[
        Attack("Bite", 5, "2d6+3 piercing", "5 ft."),
    ],
)

HIPPOGRIFF = Monster(
    name="Hippogriff",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="unaligned",
    armor_class=11,
    hit_points=19,
    hit_dice="3d10+3",
    speed="40 ft., fly 60 ft.",
    strength=17, dexterity=13, constitution=13,
    intelligence=2, wisdom=12, charisma=8,
    challenge_rating="1",
    xp=200,
    skills=["Perception +5"],
    senses="passive Perception 15",
    traits=[
        Trait("Keen Sight", "The hippogriff has advantage on Wisdom (Perception) checks that rely on sight."),
    ],
    attacks=[
        Attack("Beak", 5, "1d10+3 piercing", "5 ft."),
        Attack("Claws", 5, "2d6+3 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The hippogriff makes two attacks: one with its beak and one with its claws."),
    ],
)

IMP = Monster(
    name="Imp",
    size=Size.TINY,
    monster_type=MonsterType.FIEND,
    alignment="lawful evil",
    armor_class=13,
    hit_points=10,
    hit_dice="3d4+3",
    speed="20 ft., fly 40 ft.",
    strength=6, dexterity=17, constitution=13,
    intelligence=11, wisdom=12, charisma=14,
    challenge_rating="1",
    xp=200,
    skills=["Deception +4", "Insight +3", "Persuasion +4", "Stealth +5"],
    damage_resistances=["cold", "bludgeoning, piercing, and slashing from nonmagical attacks not made with silvered weapons"],
    damage_immunities=["fire", "poison"],
    condition_immunities=["poisoned"],
    languages="Infernal, Common",
    senses="darkvision 120 ft., passive Perception 11",
    traits=[
        Trait("Shapechanger", "The imp can use its action to polymorph into a beast form that resembles a rat (speed 20 ft.), a raven (20 ft., fly 60 ft.), or a spider (20 ft., climb 20 ft.), or back into its true form."),
        Trait("Devil's Sight", "Magical darkness doesn't impede the imp's darkvision."),
        Trait("Magic Resistance", "The imp has advantage on saving throws against spells and other magical effects."),
    ],
    attacks=[
        Attack("Sting (Bite in Beast Form)", 5, "1d4+3 piercing + 3d6 poison", "5 ft.", "The target must make a DC 11 Constitution saving throw, taking the poison damage on a failed save, or half as much damage on a successful one."),
    ],
    actions=[
        Action("Invisibility", "The imp magically turns invisible until it attacks or until its concentration ends."),
    ],
)

QUASIT = Monster(
    name="Quasit",
    size=Size.TINY,
    monster_type=MonsterType.FIEND,
    alignment="chaotic evil",
    armor_class=13,
    hit_points=7,
    hit_dice="3d4",
    speed="40 ft.",
    strength=5, dexterity=17, constitution=10,
    intelligence=7, wisdom=10, charisma=10,
    challenge_rating="1",
    xp=200,
    skills=["Stealth +5"],
    damage_resistances=["cold", "fire", "lightning", "bludgeoning, piercing, and slashing from nonmagical attacks"],
    damage_immunities=["poison"],
    condition_immunities=["poisoned"],
    languages="Abyssal, Common",
    senses="darkvision 120 ft., passive Perception 10",
    traits=[
        Trait("Shapechanger", "The quasit can use its action to polymorph into a beast form that resembles a bat (speed 10 ft., fly 40 ft.), a centipede (40 ft., climb 40 ft.), or a toad (40 ft., swim 40 ft.), or back into its true form."),
        Trait("Magic Resistance", "The quasit has advantage on saving throws against spells and other magical effects."),
    ],
    attacks=[
        Attack("Claws (Bite in Beast Form)", 4, "1d4+3 piercing", "5 ft.", "The target must succeed on a DC 10 Constitution saving throw or take 5 (2d4) poison damage and become poisoned for 1 minute. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."),
    ],
    actions=[
        Action("Scare", "One creature of the quasit's choice within 20 feet of it must succeed on a DC 10 Wisdom saving throw or be frightened for 1 minute. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.", "short rest"),
        Action("Invisibility", "The quasit magically turns invisible until it attacks or uses Scare, or until its concentration ends."),
    ],
)

# =============================================================================
# CR 2 MONSTERS (Additional)
# =============================================================================

ANKHEG = Monster(
    name="Ankheg",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="unaligned",
    armor_class=14,
    hit_points=39,
    hit_dice="6d10+6",
    speed="30 ft., burrow 10 ft.",
    strength=17, dexterity=11, constitution=13,
    intelligence=1, wisdom=13, charisma=6,
    challenge_rating="2",
    xp=450,
    senses="darkvision 60 ft., tremorsense 60 ft., passive Perception 11",
    attacks=[
        Attack("Bite", 5, "2d6+3 slashing + 1d6 acid", "5 ft.", "If the target is a Large or smaller creature, it is grappled (escape DC 13). Until this grapple ends, the ankheg can bite only the grappled creature and has advantage on attack rolls to do so."),
    ],
    actions=[
        Action("Acid Spray", "The ankheg spits acid in a line that is 30 feet long and 5 feet wide, provided that it has no creature grappled. Each creature in that line must make a DC 13 Dexterity saving throw, taking 10 (3d6) acid damage on a failed save, or half as much damage on a successful one.", "5-6"),
    ],
)

ETTERCAP = Monster(
    name="Ettercap",
    size=Size.MEDIUM,
    monster_type=MonsterType.MONSTROSITY,
    alignment="neutral evil",
    armor_class=13,
    hit_points=44,
    hit_dice="8d8+8",
    speed="30 ft., climb 30 ft.",
    strength=14, dexterity=15, constitution=13,
    intelligence=7, wisdom=12, charisma=8,
    challenge_rating="2",
    xp=450,
    skills=["Perception +3", "Stealth +4", "Survival +3"],
    senses="darkvision 60 ft., passive Perception 13",
    traits=[
        Trait("Spider Climb", "The ettercap can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check."),
        Trait("Web Sense", "While in contact with a web, the ettercap knows the exact location of any other creature in contact with the same web."),
        Trait("Web Walker", "The ettercap ignores movement restrictions caused by webbing."),
    ],
    attacks=[
        Attack("Bite", 4, "1d8+2 piercing + 1d8 poison", "5 ft.", "The target must succeed on a DC 11 Constitution saving throw or be poisoned for 1 minute. The creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."),
        Attack("Claws", 4, "2d4+2 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The ettercap makes two attacks: one with its bite and one with its claws."),
        Action("Web", "The ettercap shoots a mass of webbing at one creature within 30 feet. The creature must succeed on a DC 11 Dexterity saving throw or be restrained. A restrained creature can use its action to make a DC 11 Strength check, freeing itself on a success.", "5-6"),
    ],
)

GRIFFON = Monster(
    name="Griffon",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="unaligned",
    armor_class=12,
    hit_points=59,
    hit_dice="7d10+21",
    speed="30 ft., fly 80 ft.",
    strength=18, dexterity=15, constitution=16,
    intelligence=2, wisdom=13, charisma=8,
    challenge_rating="2",
    xp=450,
    skills=["Perception +5"],
    senses="darkvision 60 ft., passive Perception 15",
    traits=[
        Trait("Keen Sight", "The griffon has advantage on Wisdom (Perception) checks that rely on sight."),
    ],
    attacks=[
        Attack("Beak", 6, "1d8+4 piercing", "5 ft."),
        Attack("Claws", 6, "2d6+4 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The griffon makes two attacks: one with its beak and one with its claws."),
    ],
)

MERROW = Monster(
    name="Merrow",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="chaotic evil",
    armor_class=13,
    hit_points=45,
    hit_dice="6d10+12",
    speed="10 ft., swim 40 ft.",
    strength=18, dexterity=10, constitution=15,
    intelligence=8, wisdom=10, charisma=9,
    challenge_rating="2",
    xp=450,
    senses="darkvision 60 ft., passive Perception 10",
    languages="Abyssal, Aquan",
    traits=[
        Trait("Amphibious", "The merrow can breathe air and water."),
    ],
    attacks=[
        Attack("Bite", 6, "1d8+4 piercing", "5 ft."),
        Attack("Claws", 6, "2d4+4 slashing", "5 ft."),
        Attack("Harpoon", 6, "2d6+4 piercing", "20/60 ft.", "If the target is a Huge or smaller creature, it must succeed on a Strength contest against the merrow or be pulled up to 20 feet toward the merrow."),
    ],
    actions=[
        Action("Multiattack", "The merrow makes two attacks: one with its bite and one with its claws or harpoon."),
    ],
)

OCHRE_JELLY = Monster(
    name="Ochre Jelly",
    size=Size.LARGE,
    monster_type=MonsterType.OOZE,
    alignment="unaligned",
    armor_class=8,
    hit_points=45,
    hit_dice="6d10+12",
    speed="10 ft., climb 10 ft.",
    strength=15, dexterity=6, constitution=14,
    intelligence=2, wisdom=6, charisma=1,
    challenge_rating="2",
    xp=450,
    damage_resistances=["acid"],
    damage_immunities=["lightning", "slashing"],
    condition_immunities=["blinded", "charmed", "deafened", "exhaustion", "frightened", "prone"],
    senses="blindsight 60 ft. (blind beyond this radius), passive Perception 8",
    traits=[
        Trait("Amorphous", "The jelly can move through a space as narrow as 1 inch wide without squeezing."),
        Trait("Spider Climb", "The jelly can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check."),
        Trait("Split", "When a jelly that is Medium or larger is subjected to lightning or slashing damage, it splits into two new jellies if it has at least 10 hit points. Each new jelly has hit points equal to half the original jelly's, rounded down. New jellies are one size smaller than the original jelly."),
    ],
    attacks=[
        Attack("Pseudopod", 4, "2d6+2 bludgeoning + 1d6 acid", "5 ft."),
    ],
)

PEGASUS = Monster(
    name="Pegasus",
    size=Size.LARGE,
    monster_type=MonsterType.CELESTIAL,
    alignment="chaotic good",
    armor_class=12,
    hit_points=59,
    hit_dice="7d10+21",
    speed="60 ft., fly 90 ft.",
    strength=18, dexterity=15, constitution=16,
    intelligence=10, wisdom=15, charisma=13,
    challenge_rating="2",
    xp=450,
    saving_throws=["Dex +4", "Wis +4", "Cha +3"],
    skills=["Perception +6"],
    languages="understands Celestial, Common, Elvish, and Sylvan but can't speak",
    senses="passive Perception 16",
    attacks=[
        Attack("Hooves", 6, "2d6+4 bludgeoning", "5 ft."),
    ],
)

# =============================================================================
# CR 3 MONSTERS (Additional)
# =============================================================================

DISPLACER_BEAST = Monster(
    name="Displacer Beast",
    size=Size.LARGE,
    monster_type=MonsterType.MONSTROSITY,
    alignment="lawful evil",
    armor_class=13,
    hit_points=85,
    hit_dice="10d10+30",
    speed="40 ft.",
    strength=18, dexterity=15, constitution=16,
    intelligence=6, wisdom=12, charisma=8,
    challenge_rating="3",
    xp=700,
    senses="darkvision 60 ft., passive Perception 11",
    traits=[
        Trait("Avoidance", "If the displacer beast is subjected to an effect that allows it to make a saving throw to take only half damage, it instead takes no damage if it succeeds on the saving throw, and only half damage if it fails."),
        Trait("Displacement", "The displacer beast projects a magical illusion that makes it appear to be standing near its actual location, causing attack rolls against it to have disadvantage. If it is hit by an attack, this trait is disrupted until the end of its next turn. This trait is also disrupted while the displacer beast is incapacitated or has a speed of 0."),
    ],
    attacks=[
        Attack("Tentacle", 6, "1d6+4 bludgeoning + 1d6 piercing", "10 ft."),
    ],
    actions=[
        Action("Multiattack", "The displacer beast makes two attacks with its tentacles."),
    ],
)

DOPPELGANGER = Monster(
    name="Doppelganger",
    size=Size.MEDIUM,
    monster_type=MonsterType.MONSTROSITY,
    alignment="neutral",
    armor_class=14,
    hit_points=52,
    hit_dice="8d8+16",
    speed="30 ft.",
    strength=11, dexterity=18, constitution=14,
    intelligence=11, wisdom=12, charisma=14,
    challenge_rating="3",
    xp=700,
    skills=["Deception +6", "Insight +3"],
    condition_immunities=["charmed"],
    languages="Common",
    senses="darkvision 60 ft., passive Perception 11",
    traits=[
        Trait("Shapechanger", "The doppelganger can use its action to polymorph into a Small or Medium humanoid it has seen, or back into its true form. Its statistics, other than its size, are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies."),
        Trait("Ambusher", "In the first round of combat, the doppelganger has advantage on attack rolls against any creature it has surprised."),
        Trait("Surprise Attack", "If the doppelganger surprises a creature and hits it with an attack during the first round of combat, the target takes an extra 10 (3d6) damage from the attack."),
    ],
    attacks=[
        Attack("Slam", 6, "1d6+4 bludgeoning", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The doppelganger makes two melee attacks."),
        Action("Read Thoughts", "The doppelganger magically reads the surface thoughts of one creature within 60 feet of it. The effect can penetrate barriers, but 3 feet of wood or dirt, 2 feet of stone, 2 inches of metal, or a thin sheet of lead blocks it."),
    ],
)

GREEN_HAG = Monster(
    name="Green Hag",
    size=Size.MEDIUM,
    monster_type=MonsterType.FEY,
    alignment="neutral evil",
    armor_class=17,
    hit_points=82,
    hit_dice="11d8+33",
    speed="30 ft.",
    strength=18, dexterity=12, constitution=16,
    intelligence=13, wisdom=14, charisma=14,
    challenge_rating="3",
    xp=700,
    skills=["Arcana +3", "Deception +4", "Perception +4", "Stealth +3"],
    languages="Common, Draconic, Sylvan",
    senses="darkvision 60 ft., passive Perception 14",
    traits=[
        Trait("Amphibious", "The hag can breathe air and water."),
        Trait("Mimicry", "The hag can mimic animal sounds and humanoid voices. A creature that hears the sounds can tell they are imitations with a successful DC 14 Wisdom (Insight) check."),
    ],
    attacks=[
        Attack("Claws", 6, "2d8+4 slashing", "5 ft."),
    ],
    actions=[
        Action("Illusory Appearance", "The hag covers herself and anything she is wearing or carrying with a magical illusion that makes her look like another creature of her general size and humanoid shape. The illusion ends if the hag takes a bonus action to end it or if she dies."),
        Action("Invisible Passage", "The hag magically turns invisible until she attacks or casts a spell, or until her concentration ends."),
    ],
)

NIGHTMARE = Monster(
    name="Nightmare",
    size=Size.LARGE,
    monster_type=MonsterType.FIEND,
    alignment="neutral evil",
    armor_class=13,
    hit_points=68,
    hit_dice="8d10+24",
    speed="60 ft., fly 90 ft.",
    strength=18, dexterity=15, constitution=16,
    intelligence=10, wisdom=13, charisma=15,
    challenge_rating="3",
    xp=700,
    damage_immunities=["fire"],
    languages="understands Abyssal, Common, and Infernal but can't speak",
    senses="passive Perception 11",
    traits=[
        Trait("Confer Fire Resistance", "The nightmare can grant resistance to fire damage to anyone riding it."),
        Trait("Illumination", "The nightmare sheds bright light in a 10-foot radius and dim light for an additional 10 feet."),
    ],
    attacks=[
        Attack("Hooves", 6, "2d8+4 bludgeoning + 2d6 fire", "5 ft."),
    ],
    actions=[
        Action("Ethereal Stride", "The nightmare and up to three willing creatures within 5 feet of it magically enter the Ethereal Plane from the Material Plane, or vice versa."),
    ],
)

SPECTATOR = Monster(
    name="Spectator",
    size=Size.MEDIUM,
    monster_type=MonsterType.ABERRATION,
    alignment="lawful neutral",
    armor_class=14,
    hit_points=39,
    hit_dice="6d8+12",
    speed="0 ft., fly 30 ft. (hover)",
    strength=8, dexterity=14, constitution=14,
    intelligence=13, wisdom=14, charisma=11,
    challenge_rating="3",
    xp=700,
    skills=["Perception +6"],
    condition_immunities=["prone"],
    languages="Deep Speech, Undercommon, telepathy 120 ft.",
    senses="darkvision 120 ft., passive Perception 16",
    attacks=[
        Attack("Bite", 1, "1d6-1 piercing", "5 ft."),
    ],
    actions=[
        Action("Eye Rays", "The spectator shoots up to two eye rays at one or two creatures it can see within 90 feet. Each ray is a different effect: Confusion Ray, Paralyzing Ray, Fear Ray, or Wounding Ray."),
        Action("Create Food and Water", "The spectator magically creates enough food and water to sustain itself for 24 hours."),
    ],
)

WATER_WEIRD = Monster(
    name="Water Weird",
    size=Size.LARGE,
    monster_type=MonsterType.ELEMENTAL,
    alignment="neutral",
    armor_class=13,
    hit_points=58,
    hit_dice="9d10+9",
    speed="0 ft., swim 60 ft.",
    strength=17, dexterity=16, constitution=13,
    intelligence=11, wisdom=10, charisma=10,
    challenge_rating="3",
    xp=700,
    damage_resistances=["fire", "bludgeoning, piercing, and slashing from nonmagical attacks"],
    damage_immunities=["poison"],
    condition_immunities=["exhaustion", "grappled", "paralyzed", "poisoned", "restrained", "prone", "unconscious"],
    languages="understands Aquan but doesn't speak",
    senses="blindsight 30 ft., passive Perception 10",
    traits=[
        Trait("Invisible in Water", "The water weird is invisible while fully immersed in water."),
        Trait("Water Bound", "The water weird dies if it leaves the water to which it is bound or if that water is destroyed."),
    ],
    attacks=[
        Attack("Constrict", 5, "3d6+3 bludgeoning", "10 ft.", "If the target is Medium or smaller, it is grappled (escape DC 13) and pulled 5 feet toward the water weird. Until this grapple ends, the target is restrained, the water weird tries to drown it, and the water weird can't constrict another target."),
    ],
)

WIGHT = Monster(
    name="Wight",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="neutral evil",
    armor_class=14,
    hit_points=45,
    hit_dice="6d8+18",
    speed="30 ft.",
    strength=15, dexterity=14, constitution=16,
    intelligence=10, wisdom=13, charisma=15,
    challenge_rating="3",
    xp=700,
    skills=["Perception +3", "Stealth +4"],
    damage_resistances=["necrotic", "bludgeoning, piercing, and slashing from nonmagical attacks not made with silvered weapons"],
    damage_immunities=["poison"],
    condition_immunities=["exhaustion", "poisoned"],
    languages="the languages it knew in life",
    senses="darkvision 60 ft., passive Perception 13",
    traits=[
        Trait("Sunlight Sensitivity", "While in sunlight, the wight has disadvantage on attack rolls, as well as on Wisdom (Perception) checks that rely on sight."),
    ],
    attacks=[
        Attack("Life Drain", 4, "1d6+2 necrotic", "5 ft.", "The target must succeed on a DC 13 Constitution saving throw or its hit point maximum is reduced by an amount equal to the damage taken. This reduction lasts until the target finishes a long rest. The target dies if this effect reduces its hit point maximum to 0. A humanoid slain by this attack rises 24 hours later as a zombie under the wight's control."),
        Attack("Longsword", 4, "1d8+2 slashing", "5 ft."),
        Attack("Longbow", 4, "1d8+2 piercing", "150/600 ft."),
    ],
    actions=[
        Action("Multiattack", "The wight makes two longsword attacks or two longbow attacks. It can use its Life Drain in place of one longsword attack."),
    ],
)

# =============================================================================
# CR 4 MONSTERS (Additional)
# =============================================================================

BANSHEE = Monster(
    name="Banshee",
    size=Size.MEDIUM,
    monster_type=MonsterType.UNDEAD,
    alignment="chaotic evil",
    armor_class=12,
    hit_points=58,
    hit_dice="13d8",
    speed="0 ft., fly 40 ft. (hover)",
    strength=1, dexterity=14, constitution=10,
    intelligence=12, wisdom=11, charisma=17,
    challenge_rating="4",
    xp=1100,
    saving_throws=["Wis +2", "Cha +5"],
    damage_resistances=["acid", "fire", "lightning", "thunder", "bludgeoning, piercing, and slashing from nonmagical attacks"],
    damage_immunities=["cold", "necrotic", "poison"],
    condition_immunities=["charmed", "exhaustion", "frightened", "grappled", "paralyzed", "petrified", "poisoned", "prone", "restrained"],
    languages="Common, Elvish",
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Detect Life", "The banshee can magically sense the presence of living creatures up to 5 miles away that aren't undead or constructs. She knows the general direction they're in but not their exact locations."),
        Trait("Incorporeal Movement", "The banshee can move through other creatures and objects as if they were difficult terrain. She takes 5 (1d10) force damage if she ends her turn inside an object."),
    ],
    attacks=[
        Attack("Corrupting Touch", 4, "3d6+2 necrotic", "5 ft."),
    ],
    actions=[
        Action("Horrifying Visage", "Each non-undead creature within 60 feet of the banshee that can see her must succeed on a DC 13 Wisdom saving throw or be frightened for 1 minute. A frightened target can repeat the saving throw at the end of each of its turns."),
        Action("Wail", "The banshee releases a mournful wail, provided that she isn't in sunlight. This wail has no effect on constructs and undead. All other creatures within 30 feet of her that can hear her must make a DC 13 Constitution saving throw. On a failure, a creature drops to 0 hit points. On a success, a creature takes 10 (3d6) psychic damage.", "long rest"),
    ],
)

COUATL = Monster(
    name="Couatl",
    size=Size.MEDIUM,
    monster_type=MonsterType.CELESTIAL,
    alignment="lawful good",
    armor_class=19,
    hit_points=97,
    hit_dice="13d8+39",
    speed="30 ft., fly 90 ft.",
    strength=16, dexterity=20, constitution=17,
    intelligence=18, wisdom=20, charisma=18,
    challenge_rating="4",
    xp=1100,
    saving_throws=["Con +5", "Wis +7", "Cha +6"],
    damage_resistances=["radiant"],
    damage_immunities=["psychic", "bludgeoning, piercing, and slashing from nonmagical attacks"],
    languages="all, telepathy 120 ft.",
    senses="truesight 120 ft., passive Perception 15",
    traits=[
        Trait("Magic Weapons", "The couatl's weapon attacks are magical."),
        Trait("Shielded Mind", "The couatl is immune to scrying and to any effect that would sense its emotions, read its thoughts, or detect its location."),
    ],
    attacks=[
        Attack("Bite", 8, "1d6+5 piercing", "5 ft.", "The target must succeed on a DC 13 Constitution saving throw or be poisoned for 24 hours. Until this poison ends, the target is unconscious. Another creature can use an action to shake the target awake."),
        Attack("Constrict", 6, "2d6+3 bludgeoning", "10 ft.", "The target is grappled (escape DC 15). Until this grapple ends, the target is restrained, and the couatl can't constrict another target."),
    ],
    actions=[
        Action("Change Shape", "The couatl magically polymorphs into a humanoid or beast that has a challenge rating equal to or less than its own, or back into its true form."),
    ],
)

FLAMESKULL = Monster(
    name="Flameskull",
    size=Size.TINY,
    monster_type=MonsterType.UNDEAD,
    alignment="neutral evil",
    armor_class=13,
    hit_points=40,
    hit_dice="9d4+18",
    speed="0 ft., fly 40 ft. (hover)",
    strength=1, dexterity=17, constitution=14,
    intelligence=16, wisdom=10, charisma=11,
    challenge_rating="4",
    xp=1100,
    skills=["Arcana +5", "Perception +2"],
    damage_resistances=["lightning", "necrotic", "piercing"],
    damage_immunities=["cold", "fire", "poison"],
    condition_immunities=["charmed", "frightened", "paralyzed", "poisoned", "prone"],
    languages="Common",
    senses="darkvision 60 ft., passive Perception 12",
    traits=[
        Trait("Illumination", "The flameskull sheds either dim light in a 15-foot radius, or bright light in a 15-foot radius and dim light for an additional 15 feet. It can switch between the options as an action."),
        Trait("Magic Resistance", "The flameskull has advantage on saving throws against spells and other magical effects."),
        Trait("Rejuvenation", "If the flameskull is destroyed, it regains all its hit points in 1 hour unless holy water is sprinkled on its remains or a dispel magic or remove curse spell is cast on them."),
    ],
    actions=[
        Action("Multiattack", "The flameskull uses Fire Ray twice."),
        Action("Fire Ray", "Ranged Spell Attack: +5 to hit, range 30 ft., one target. Hit: 10 (3d6) fire damage."),
        Action("Spellcasting", "The flameskull casts blur, fireball (3rd level), flaming sphere, magic missile, or shield."),
    ],
)

# =============================================================================
# CR 5+ MONSTERS (Additional)
# =============================================================================

FLESH_GOLEM = Monster(
    name="Flesh Golem",
    size=Size.MEDIUM,
    monster_type=MonsterType.CONSTRUCT,
    alignment="neutral",
    armor_class=9,
    hit_points=93,
    hit_dice="11d8+44",
    speed="30 ft.",
    strength=19, dexterity=9, constitution=18,
    intelligence=6, wisdom=10, charisma=5,
    challenge_rating="5",
    xp=1800,
    damage_immunities=["lightning", "poison", "bludgeoning, piercing, and slashing from nonmagical attacks not made with adamantine weapons"],
    condition_immunities=["charmed", "exhaustion", "frightened", "paralyzed", "petrified", "poisoned"],
    languages="understands the languages of its creator but can't speak",
    senses="darkvision 60 ft., passive Perception 10",
    traits=[
        Trait("Berserk", "Whenever the golem starts its turn with 40 hit points or fewer, roll a d6. On a 6, the golem goes berserk. On each of its turns while berserk, the golem attacks the nearest creature it can see."),
        Trait("Aversion of Fire", "If the golem takes fire damage, it has disadvantage on attack rolls and ability checks until the end of its next turn."),
        Trait("Immutable Form", "The golem is immune to any spell or effect that would alter its form."),
        Trait("Lightning Absorption", "Whenever the golem is subjected to lightning damage, it takes no damage and instead regains a number of hit points equal to the lightning damage dealt."),
        Trait("Magic Resistance", "The golem has advantage on saving throws against spells and other magical effects."),
        Trait("Magic Weapons", "The golem's weapon attacks are magical."),
    ],
    attacks=[
        Attack("Slam", 7, "2d8+4 bludgeoning", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The golem makes two slam attacks."),
    ],
)

NIGHT_HAG = Monster(
    name="Night Hag",
    size=Size.MEDIUM,
    monster_type=MonsterType.FIEND,
    alignment="neutral evil",
    armor_class=17,
    hit_points=112,
    hit_dice="15d8+45",
    speed="30 ft.",
    strength=18, dexterity=15, constitution=16,
    intelligence=16, wisdom=14, charisma=16,
    challenge_rating="5",
    xp=1800,
    skills=["Deception +7", "Insight +6", "Perception +6", "Stealth +6"],
    damage_resistances=["cold", "fire", "bludgeoning, piercing, and slashing from nonmagical attacks not made with silvered weapons"],
    condition_immunities=["charmed"],
    languages="Abyssal, Common, Infernal, Primordial",
    senses="darkvision 120 ft., passive Perception 16",
    traits=[
        Trait("Magic Resistance", "The hag has advantage on saving throws against spells and other magical effects."),
    ],
    attacks=[
        Attack("Claws (Hag Form Only)", 7, "2d8+4 slashing", "5 ft."),
    ],
    actions=[
        Action("Change Shape", "The hag magically polymorphs into a Small or Medium female humanoid, or back into her true form. Her statistics are the same in each form. Any equipment she is wearing or carrying isn't transformed. She reverts to her true form if she dies."),
        Action("Etherealness", "The hag magically enters the Ethereal Plane from the Material Plane, or vice versa. To do so, the hag must have a heartstone in her possession."),
        Action("Nightmare Haunting", "While on the Ethereal Plane, the hag magically touches a sleeping humanoid on the Material Plane. A protection from evil and good spell cast on the target prevents this contact. As long as the contact persists, the target has dreadful visions. If these visions last for at least 1 hour, the target gains no benefit from its rest, and its hit point maximum is reduced by 5 (1d10)."),
    ],
)

UNICORN = Monster(
    name="Unicorn",
    size=Size.LARGE,
    monster_type=MonsterType.CELESTIAL,
    alignment="lawful good",
    armor_class=12,
    hit_points=67,
    hit_dice="9d10+18",
    speed="50 ft.",
    strength=18, dexterity=14, constitution=15,
    intelligence=11, wisdom=17, charisma=16,
    challenge_rating="5",
    xp=1800,
    damage_immunities=["poison"],
    condition_immunities=["charmed", "paralyzed", "poisoned"],
    languages="Celestial, Elvish, Sylvan, telepathy 60 ft.",
    senses="darkvision 60 ft., passive Perception 13",
    traits=[
        Trait("Charge", "If the unicorn moves at least 20 feet straight toward a target and then hits it with a horn attack on the same turn, the target takes an extra 9 (2d8) piercing damage. If the target is a creature, it must succeed on a DC 15 Strength saving throw or be knocked prone."),
        Trait("Magic Resistance", "The unicorn has advantage on saving throws against spells and other magical effects."),
        Trait("Magic Weapons", "The unicorn's weapon attacks are magical."),
    ],
    attacks=[
        Attack("Hooves", 7, "2d6+4 bludgeoning", "5 ft."),
        Attack("Horn", 7, "1d8+4 piercing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The unicorn makes two attacks: one with its hooves and one with its horn."),
        Action("Healing Touch", "The unicorn touches another creature with its horn. The target magically regains 11 (2d8+2) hit points. In addition, the touch removes all diseases and neutralizes all poisons afflicting the target.", "long rest"),
        Action("Teleport", "The unicorn magically teleports itself and up to three willing creatures it can see within 5 feet of it, along with any equipment they are wearing or carrying, to a location the unicorn is familiar with, up to 1 mile away.", "long rest"),
    ],
    legendary_actions=[
        Action("Hooves", "The unicorn makes one attack with its hooves."),
        Action("Shimmering Shield (Costs 2 Actions)", "The unicorn creates a shimmering, magical field around itself or another creature it can see within 60 feet of it. The target gains a +2 bonus to AC until the end of the unicorn's next turn."),
        Action("Heal Self (Costs 3 Actions)", "The unicorn magically regains 11 (2d8+2) hit points."),
    ],
)

YOUNG_GREEN_DRAGON = Monster(
    name="Young Green Dragon",
    size=Size.LARGE,
    monster_type=MonsterType.DRAGON,
    alignment="lawful evil",
    armor_class=18,
    hit_points=136,
    hit_dice="16d10+48",
    speed="40 ft., fly 80 ft., swim 40 ft.",
    strength=19, dexterity=12, constitution=17,
    intelligence=16, wisdom=13, charisma=15,
    challenge_rating="8",
    xp=3900,
    saving_throws=["Dex +4", "Con +6", "Wis +4", "Cha +5"],
    skills=["Deception +5", "Perception +7", "Stealth +4"],
    damage_immunities=["poison"],
    condition_immunities=["poisoned"],
    senses="blindsight 30 ft., darkvision 120 ft., passive Perception 17",
    languages="Common, Draconic",
    traits=[
        Trait("Amphibious", "The dragon can breathe air and water."),
    ],
    attacks=[
        Attack("Bite", 7, "2d10+4 piercing + 2d6 poison", "10 ft."),
        Attack("Claw", 7, "2d6+4 slashing", "5 ft."),
    ],
    actions=[
        Action("Multiattack", "The dragon makes three attacks: one with its bite and two with its claws."),
        Action("Poison Breath", "The dragon exhales poisonous gas in a 30-foot cone. Each creature in that area must make a DC 14 Constitution saving throw, taking 42 (12d6) poison damage on a failed save, or half as much damage on a successful one.", "5-6"),
    ],
)

# =============================================================================
# COLLECTIONS
# =============================================================================

CR_0: list[Monster] = [BAT, RAT, COMMONER, FROG, CAT]
CR_1_8: list[Monster] = [BANDIT, CULTIST, GUARD, KOBOLD, GIANT_RAT, STIRGE, MASTIFF, TRIBAL_WARRIOR]
CR_1_4: list[Monster] = [GOBLIN, SKELETON, ZOMBIE, WOLF, GIANT_WOLF_SPIDER, FLYING_SWORD, PIXIE, SPRITE]
CR_1_2: list[Monster] = [ORC, HOBGOBLIN, SHADOW, GNOLL, RUST_MONSTER, WORG, COCKATRICE, DARKMANTLE, GRAY_OOZE, MAGMIN]
CR_1: list[Monster] = [BUGBEAR, GHOUL, DIRE_WOLF, SPIDER, SPECTER, DRYAD, HARPY, ANIMATED_ARMOR, DEATH_DOG, GIANT_HYENA, HIPPOGRIFF, IMP, QUASIT]
CR_2: list[Monster] = [OGRE, GHAST, MIMIC, GELATINOUS_CUBE, GARGOYLE, ANKHEG, ETTERCAP, GRIFFON, MERROW, OCHRE_JELLY, PEGASUS]
CR_3: list[Monster] = [OWLBEAR, WEREWOLF, MUMMY, BASILISK, HELL_HOUND, PHASE_SPIDER, MANTICORE, DISPLACER_BEAST, DOPPELGANGER, GREEN_HAG, NIGHTMARE, SPECTATOR, WATER_WEIRD, WIGHT]
CR_4: list[Monster] = [ETTIN, GHOST, BANSHEE, COUATL, FLAMESKULL]
CR_5: list[Monster] = [TROLL, SALAMANDER, WRAITH, HILL_GIANT, FLESH_GOLEM, NIGHT_HAG, UNICORN]
CR_6_PLUS: list[Monster] = [MEDUSA, CHIMERA, YOUNG_BLACK_DRAGON, YOUNG_GREEN_DRAGON]
CR_10_PLUS: list[Monster] = [YOUNG_RED_DRAGON, ADULT_RED_DRAGON]

ALL_MONSTERS: list[Monster] = (
    CR_0 + CR_1_8 + CR_1_4 + CR_1_2 + CR_1 + CR_2 + CR_3 + CR_4 + CR_5 + CR_6_PLUS + CR_10_PLUS
)

# Dictionary for quick lookup
_MONSTERS_BY_NAME: dict[str, Monster] = {
    monster.name.lower(): monster for monster in ALL_MONSTERS
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_monster(name: str) -> Optional[Monster]:
    """Get a monster by name (case-insensitive)."""
    return _MONSTERS_BY_NAME.get(name.lower())


def get_monsters_by_cr(cr: str) -> list[Monster]:
    """Get all monsters of a specific challenge rating."""
    return [m for m in ALL_MONSTERS if m.challenge_rating == cr]


def get_monsters_by_type(monster_type: MonsterType) -> list[Monster]:
    """Get all monsters of a specific type."""
    return [m for m in ALL_MONSTERS if m.monster_type == monster_type]


def get_monsters_by_cr_range(min_cr: float, max_cr: float) -> list[Monster]:
    """Get all monsters within a CR range."""
    return [m for m in ALL_MONSTERS if min_cr <= m.cr_numeric <= max_cr]


def search_monsters(query: str) -> list[Monster]:
    """Search monsters by name or description."""
    query_lower = query.lower()
    results = []
    for monster in ALL_MONSTERS:
        if (query_lower in monster.name.lower() or
            query_lower in monster.description.lower() or
            query_lower in monster.monster_type.value.lower()):
            results.append(monster)
    return results


def get_all_monster_names() -> list[str]:
    """Get a list of all monster names."""
    return [monster.name for monster in ALL_MONSTERS]


def calculate_encounter_xp(monsters: list[Monster], num_players: int = 4) -> dict:
    """Calculate encounter difficulty and XP.

    Returns dict with:
    - total_xp: Total XP of all monsters
    - adjusted_xp: XP adjusted for number of monsters
    - difficulty: easy, medium, hard, or deadly
    """
    if not monsters:
        return {"total_xp": 0, "adjusted_xp": 0, "difficulty": "trivial"}

    total_xp = sum(m.xp for m in monsters)

    # Encounter multipliers based on number of monsters
    num_monsters = len(monsters)
    if num_monsters == 1:
        multiplier = 1.0
    elif num_monsters == 2:
        multiplier = 1.5
    elif num_monsters <= 6:
        multiplier = 2.0
    elif num_monsters <= 10:
        multiplier = 2.5
    elif num_monsters <= 14:
        multiplier = 3.0
    else:
        multiplier = 4.0

    adjusted_xp = int(total_xp * multiplier)

    # Difficulty thresholds (assuming level 5 party)
    # These should ideally be calculated based on party level
    easy_threshold = 250 * num_players
    medium_threshold = 500 * num_players
    hard_threshold = 750 * num_players
    deadly_threshold = 1100 * num_players

    if adjusted_xp < easy_threshold:
        difficulty = "easy"
    elif adjusted_xp < medium_threshold:
        difficulty = "medium"
    elif adjusted_xp < hard_threshold:
        difficulty = "hard"
    else:
        difficulty = "deadly"

    return {
        "total_xp": total_xp,
        "adjusted_xp": adjusted_xp,
        "difficulty": difficulty,
    }
