"""Species/Race definitions for D&D 5e and Tales of the Valiant.

This module contains species (races) from D&D 2014, D&D 2024, and ToV
with original AI-generated flavor text and accurate mechanical details.

Ruleset differences:
- D&D 2014: Fixed ability score bonuses per species
- D&D 2024: Flexible ability scores (+2/+1 or +1/+1/+1 to any)
- ToV: Lineage + Heritage system (lineage gives traits, heritage gives skills/languages)
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RacialTrait:
    """A racial trait or feature.

    The min_level field indicates when a trait becomes available:
    - 1 (default): Available at character creation
    - 3, 5, etc.: Available when character reaches that level
    """
    name: str
    description: str
    min_level: int = 1  # Character level required (1 = always available)


@dataclass
class Subrace:
    """A subrace/subspecies variant."""
    name: str
    description: str
    ability_bonuses: dict[str, int] = field(default_factory=dict)
    traits: list[RacialTrait] = field(default_factory=list)


@dataclass
class Heritage:
    """A ToV Heritage (cultural background)."""
    name: str
    description: str
    skill_proficiencies: list[str] = field(default_factory=list)
    languages: int = 0  # Number of additional languages
    traits: list[RacialTrait] = field(default_factory=list)


@dataclass
class Species:
    """A playable species (race/lineage) definition."""
    name: str
    description: str
    size: str  # Small, Medium, Large
    speed: int
    ability_bonuses: dict[str, int]  # Base bonuses (2014 rules)
    languages: list[str]
    traits: list[RacialTrait] = field(default_factory=list)
    darkvision: int = 0  # Range in feet, 0 if none
    subraces: list[Subrace] = field(default_factory=list)
    age_info: str = ""
    alignment_tendency: str = ""
    # Ruleset support
    ruleset: Optional[str] = None  # None = universal, "dnd2014", "dnd2024", "tov"
    flexible_asi: bool = False  # True for 2024 rules (choose +2/+1 or +1/+1/+1)


# =============================================================================
# DWARF
# =============================================================================

DWARF = Species(
    name="Dwarf",
    description=(
        "Stout and resilient, dwarves are master craftspeople who carve their homes "
        "from the living rock of mountains. Their long memories and longer grudges "
        "are matched only by their legendary endurance and skill with stone and metal."
    ),
    size="Medium",
    speed=25,
    ability_bonuses={"Constitution": 2},
    languages=["Common", "Dwarvish"],
    darkvision=60,
    age_info="Dwarves mature at the same rate as humans but are considered young until age 50. They live to around 350 years.",
    alignment_tendency="Most dwarves tend toward lawful alignments, valuing order and tradition.",
    traits=[
        RacialTrait(
            name="Dwarven Resilience",
            description="You have advantage on saving throws against poison, and you have resistance to poison damage.",
        ),
        RacialTrait(
            name="Dwarven Combat Training",
            description="You have proficiency with the battleaxe, handaxe, light hammer, and warhammer.",
        ),
        RacialTrait(
            name="Tool Proficiency",
            description="You gain proficiency with the artisan's tools of your choice: smith's tools, brewer's supplies, or mason's tools.",
        ),
        RacialTrait(
            name="Stonecunning",
            description="Whenever you make an Intelligence (History) check related to the origin of stonework, you are considered proficient in the History skill and add double your proficiency bonus to the check.",
        ),
    ],
    subraces=[
        Subrace(
            name="Hill Dwarf",
            description="Hill dwarves possess keen senses and remarkable resilience, honed by generations living in the hills and valleys.",
            ability_bonuses={"Wisdom": 1},
            traits=[
                RacialTrait(
                    name="Dwarven Toughness",
                    description="Your hit point maximum increases by 1, and it increases by 1 every time you gain a level.",
                ),
            ],
        ),
        Subrace(
            name="Mountain Dwarf",
            description="Mountain dwarves are strong and hardy, accustomed to difficult terrain and the weight of heavy armor.",
            ability_bonuses={"Strength": 2},
            traits=[
                RacialTrait(
                    name="Dwarven Armor Training",
                    description="You have proficiency with light and medium armor.",
                ),
            ],
        ),
    ],
)

# =============================================================================
# ELF
# =============================================================================

ELF = Species(
    name="Elf",
    description=(
        "Graceful and long-lived, elves possess an otherworldly beauty and connection "
        "to the natural world. Their keen senses and innate magical affinity make them "
        "formidable allies and dangerous foes."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Dexterity": 2},
    languages=["Common", "Elvish"],
    darkvision=60,
    age_info="Elves reach physical maturity around age 20 but aren't considered adults until about 100. They can live to 750 years or more.",
    alignment_tendency="Elves love freedom and variety, often leaning toward chaotic alignments.",
    traits=[
        RacialTrait(
            name="Keen Senses",
            description="You have proficiency in the Perception skill.",
        ),
        RacialTrait(
            name="Fey Ancestry",
            description="You have advantage on saving throws against being charmed, and magic can't put you to sleep.",
        ),
        RacialTrait(
            name="Trance",
            description="Elves don't need to sleep. Instead, they meditate deeply for 4 hours a day, gaining the same benefit that a human does from 8 hours of sleep.",
        ),
    ],
    subraces=[
        Subrace(
            name="High Elf",
            description="High elves have a keen mind and mastery of basic magic, reflecting their heritage of arcane study.",
            ability_bonuses={"Intelligence": 1},
            traits=[
                RacialTrait(
                    name="Elf Weapon Training",
                    description="You have proficiency with the longsword, shortsword, shortbow, and longbow.",
                ),
                RacialTrait(
                    name="Cantrip",
                    description="You know one cantrip of your choice from the wizard spell list. Intelligence is your spellcasting ability for it.",
                ),
                RacialTrait(
                    name="Extra Language",
                    description="You can speak, read, and write one extra language of your choice.",
                ),
            ],
        ),
        Subrace(
            name="Wood Elf",
            description="Wood elves are swift and stealthy, at home in the deep forests where they have lived for millennia.",
            ability_bonuses={"Wisdom": 1},
            traits=[
                RacialTrait(
                    name="Elf Weapon Training",
                    description="You have proficiency with the longsword, shortsword, shortbow, and longbow.",
                ),
                RacialTrait(
                    name="Fleet of Foot",
                    description="Your base walking speed increases to 35 feet.",
                ),
                RacialTrait(
                    name="Mask of the Wild",
                    description="You can attempt to hide even when you are only lightly obscured by foliage, heavy rain, falling snow, mist, and other natural phenomena.",
                ),
            ],
        ),
        Subrace(
            name="Drow",
            description="Descended from elves who retreated to the Underdark, drow have adapted to life in eternal darkness.",
            ability_bonuses={"Charisma": 1},
            traits=[
                RacialTrait(
                    name="Superior Darkvision",
                    description="Your darkvision has a radius of 120 feet.",
                ),
                RacialTrait(
                    name="Sunlight Sensitivity",
                    description="You have disadvantage on attack rolls and Wisdom (Perception) checks that rely on sight when you, the target, or what you're trying to perceive is in direct sunlight.",
                ),
                RacialTrait(
                    name="Drow Magic",
                    description="You know the dancing lights cantrip. At 3rd level, you can cast faerie fire once per long rest. At 5th level, you can cast darkness once per long rest. Charisma is your spellcasting ability for these spells.",
                ),
                RacialTrait(
                    name="Drow Weapon Training",
                    description="You have proficiency with rapiers, shortswords, and hand crossbows.",
                ),
            ],
        ),
    ],
)

# =============================================================================
# HALFLING
# =============================================================================

HALFLING = Species(
    name="Halfling",
    description=(
        "Small but courageous, halflings are a practical folk who value comfort and community. "
        "Their natural luck and nimbleness allow them to slip out of danger with remarkable ease, "
        "and their cheerful demeanor makes them welcome guests wherever they wander."
    ),
    size="Small",
    speed=25,
    ability_bonuses={"Dexterity": 2},
    languages=["Common", "Halfling"],
    darkvision=0,
    age_info="Halflings reach adulthood at age 20 and generally live into the middle of their second century.",
    alignment_tendency="Most halflings are lawful good, valuing peace and order.",
    traits=[
        RacialTrait(
            name="Lucky",
            description="When you roll a 1 on the d20 for an attack roll, ability check, or saving throw, you can reroll the die and must use the new roll.",
        ),
        RacialTrait(
            name="Brave",
            description="You have advantage on saving throws against being frightened.",
        ),
        RacialTrait(
            name="Halfling Nimbleness",
            description="You can move through the space of any creature that is of a size larger than yours.",
        ),
    ],
    subraces=[
        Subrace(
            name="Lightfoot",
            description="Lightfoot halflings are naturally stealthy and sociable, blending into crowds with ease.",
            ability_bonuses={"Charisma": 1},
            traits=[
                RacialTrait(
                    name="Naturally Stealthy",
                    description="You can attempt to hide even when you are obscured only by a creature that is at least one size larger than you.",
                ),
            ],
        ),
        Subrace(
            name="Stout",
            description="Stout halflings are hardier than their cousins, rumored to have dwarven blood in their ancestry.",
            ability_bonuses={"Constitution": 1},
            traits=[
                RacialTrait(
                    name="Stout Resilience",
                    description="You have advantage on saving throws against poison, and you have resistance to poison damage.",
                ),
            ],
        ),
    ],
)

# =============================================================================
# HUMAN
# =============================================================================

HUMAN = Species(
    name="Human",
    description=(
        "Humans are the most adaptable and ambitious of the common races. Their short lives "
        "drive them to achieve as much as possible in the years they have, and their diversity "
        "of cultures and capabilities has allowed them to spread across every corner of the world."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={
        "Strength": 1,
        "Dexterity": 1,
        "Constitution": 1,
        "Intelligence": 1,
        "Wisdom": 1,
        "Charisma": 1,
    },
    languages=["Common"],
    darkvision=0,
    age_info="Humans reach adulthood in their late teens and live less than a century.",
    alignment_tendency="Humans tend toward no particular alignment, showing the full spectrum of ethical and moral diversity.",
    traits=[
        RacialTrait(
            name="Extra Language",
            description="You can speak, read, and write one extra language of your choice.",
        ),
    ],
    subraces=[
        Subrace(
            name="Variant Human",
            description="Some humans display exceptional talent in specific areas, trading broad ability for focused expertise.",
            ability_bonuses={},  # +1 to two different abilities of choice
            traits=[
                RacialTrait(
                    name="Ability Score Increase",
                    description="Two different ability scores of your choice increase by 1 (instead of +1 to all).",
                ),
                RacialTrait(
                    name="Skills",
                    description="You gain proficiency in one skill of your choice.",
                ),
                RacialTrait(
                    name="Feat",
                    description="You gain one feat of your choice.",
                ),
            ],
        ),
    ],
)

# =============================================================================
# DRAGONBORN
# =============================================================================

DRAGONBORN = Species(
    name="Dragonborn",
    description=(
        "Born of dragons, dragonborn walk proudly through a world that greets them with "
        "fearful incomprehension. Shaped by draconic gods or the dragons themselves, they "
        "originally hatched from dragon eggs as a unique race, combining the best attributes "
        "of dragons and humanoids."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Strength": 2, "Charisma": 1},
    languages=["Common", "Draconic"],
    darkvision=0,
    age_info="Dragonborn develop quickly, walking within hours of hatching and reaching adulthood by 15. They live to around 80.",
    alignment_tendency="Dragonborn tend toward extremes, making conscious choices for good or evil.",
    traits=[
        RacialTrait(
            name="Draconic Ancestry",
            description=(
                "Choose one type of dragon from the Draconic Ancestry table. Your breath weapon "
                "and damage resistance are determined by the dragon type."
            ),
        ),
        RacialTrait(
            name="Breath Weapon",
            description=(
                "You can use your action to exhale destructive energy. Your draconic ancestry "
                "determines the size, shape, and damage type of the exhalation. When you use "
                "your breath weapon, each creature in the area must make a saving throw (DC = 8 + "
                "Constitution modifier + proficiency bonus). On a failed save, a creature takes "
                "2d6 damage (increasing to 3d6 at 6th, 4d6 at 11th, and 5d6 at 16th level), or "
                "half as much on a successful save. You can use this once per short or long rest."
            ),
        ),
        RacialTrait(
            name="Damage Resistance",
            description="You have resistance to the damage type associated with your draconic ancestry.",
        ),
    ],
    subraces=[],  # Ancestry is chosen but doesn't constitute a subrace mechanically
)

# =============================================================================
# GNOME
# =============================================================================

GNOME = Species(
    name="Gnome",
    description=(
        "A gnome's energy and enthusiasm for living shines through every inch of their tiny body. "
        "Curious and impulsive, gnomes take delight in life's simple pleasures: good food, fine "
        "craftsmanship, and above all, the pursuit of knowledge and invention."
    ),
    size="Small",
    speed=25,
    ability_bonuses={"Intelligence": 2},
    languages=["Common", "Gnomish"],
    darkvision=60,
    age_info="Gnomes mature at the same rate as humans but are expected to settle into adult life around age 40. They can live 350 to almost 500 years.",
    alignment_tendency="Gnomes are most often good, with those tending toward law being sages and engineers, while those toward chaos are tricksters and wanderers.",
    traits=[
        RacialTrait(
            name="Gnome Cunning",
            description="You have advantage on all Intelligence, Wisdom, and Charisma saving throws against magic.",
        ),
    ],
    subraces=[
        Subrace(
            name="Forest Gnome",
            description="Forest gnomes have a natural knack for illusion and communication with small animals.",
            ability_bonuses={"Dexterity": 1},
            traits=[
                RacialTrait(
                    name="Natural Illusionist",
                    description="You know the minor illusion cantrip. Intelligence is your spellcasting ability for it.",
                ),
                RacialTrait(
                    name="Speak with Small Beasts",
                    description="Through sounds and gestures, you can communicate simple ideas with Small or smaller beasts.",
                ),
            ],
        ),
        Subrace(
            name="Rock Gnome",
            description="Rock gnomes are natural tinkerers with an affinity for mechanical devices.",
            ability_bonuses={"Constitution": 1},
            traits=[
                RacialTrait(
                    name="Artificer's Lore",
                    description="Whenever you make an Intelligence (History) check related to magic items, alchemical objects, or technological devices, you can add twice your proficiency bonus.",
                ),
                RacialTrait(
                    name="Tinker",
                    description="Using tinker's tools, you can spend 1 hour and 10 gp to construct a Tiny clockwork device (AC 5, 1 hp). The device ceases to function after 24 hours or when you dismantle it. You can have up to three devices active at a time.",
                ),
            ],
        ),
    ],
)

# =============================================================================
# HALF-ELF
# =============================================================================

HALF_ELF = Species(
    name="Half-Elf",
    description=(
        "Walking in two worlds but truly belonging to neither, half-elves combine what some "
        "say are the best qualities of their elf and human parents: human curiosity and "
        "ambition tempered by elven refinement and love of nature."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Charisma": 2},  # Plus +1 to two others of choice
    languages=["Common", "Elvish"],
    darkvision=60,
    age_info="Half-elves mature at the same rate as humans and reach adulthood around age 20. They live much longer than humans, often exceeding 180 years.",
    alignment_tendency="Half-elves share the chaotic bent of their elven heritage and value personal freedom and creative expression.",
    traits=[
        RacialTrait(
            name="Ability Score Increase",
            description="Two different ability scores of your choice increase by 1 (in addition to Charisma +2).",
        ),
        RacialTrait(
            name="Fey Ancestry",
            description="You have advantage on saving throws against being charmed, and magic can't put you to sleep.",
        ),
        RacialTrait(
            name="Skill Versatility",
            description="You gain proficiency in two skills of your choice.",
        ),
        RacialTrait(
            name="Extra Language",
            description="You can speak, read, and write one extra language of your choice.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# HALF-ORC
# =============================================================================

HALF_ORC = Species(
    name="Half-Orc",
    description=(
        "Half-orcs' grayish skin, sloping foreheads, jutting jaws, and prominent teeth mark "
        "their orcish heritage. Whether raised among orcs or in human lands, half-orcs must "
        "prove themselves constantly, channeling their inner fury into strength of will and deed."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Strength": 2, "Constitution": 1},
    languages=["Common", "Orc"],
    darkvision=60,
    age_info="Half-orcs mature a little faster than humans, reaching adulthood around age 14. They age noticeably faster and rarely live longer than 75 years.",
    alignment_tendency="Half-orcs inherit a tendency toward chaos from their orc parents but are not inherently evil.",
    traits=[
        RacialTrait(
            name="Menacing",
            description="You gain proficiency in the Intimidation skill.",
        ),
        RacialTrait(
            name="Relentless Endurance",
            description="When you are reduced to 0 hit points but not killed outright, you can drop to 1 hit point instead. You can't use this feature again until you finish a long rest.",
        ),
        RacialTrait(
            name="Savage Attacks",
            description="When you score a critical hit with a melee weapon attack, you can roll one of the weapon's damage dice one additional time and add it to the extra damage of the critical hit.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# TIEFLING
# =============================================================================

TIEFLING = Species(
    name="Tiefling",
    description=(
        "Tieflings are derived from human bloodlines, bearing the indelible mark of an "
        "infernal heritage. Their appearance and nature vary widely, but all tieflings share "
        "certain traits: horns, non-prehensile tails, and an innate connection to fire and darkness."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Intelligence": 1, "Charisma": 2},
    languages=["Common", "Infernal"],
    darkvision=60,
    age_info="Tieflings mature at the same rate as humans but live a few years longer.",
    alignment_tendency="Tieflings might not have an innate tendency toward evil, but many end up there due to the prejudice they face.",
    traits=[
        RacialTrait(
            name="Hellish Resistance",
            description="You have resistance to fire damage.",
        ),
        RacialTrait(
            name="Infernal Legacy",
            description=(
                "You know the thaumaturgy cantrip. At 3rd level, you can cast hellish rebuke "
                "as a 2nd-level spell once per long rest. At 5th level, you can cast darkness "
                "once per long rest. Charisma is your spellcasting ability for these spells."
            ),
        ),
    ],
    subraces=[],
)


# =============================================================================
# AASIMAR
# =============================================================================

AASIMAR = Species(
    name="Aasimar",
    description=(
        "Aasimar bear within their souls the light of the heavens. They are descended from "
        "humans with a touch of celestial power, manifesting as an otherworldly presence "
        "and divine abilities that set them apart from ordinary mortals."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Charisma": 2},
    languages=["Common", "Celestial"],
    darkvision=60,
    age_info="Aasimar mature at the same rate as humans but can live up to 160 years.",
    alignment_tendency="Due to their celestial heritage, aasimar often feel called to fight evil and protect the innocent.",
    traits=[
        RacialTrait(
            name="Celestial Resistance",
            description="You have resistance to necrotic damage and radiant damage.",
        ),
        RacialTrait(
            name="Healing Hands",
            description="As an action, you can touch a creature and heal hit points equal to your level. You can use this once per long rest.",
        ),
        RacialTrait(
            name="Light Bearer",
            description="You know the light cantrip. Charisma is your spellcasting ability for it.",
        ),
    ],
    subraces=[
        Subrace(
            name="Protector Aasimar",
            description="Protector aasimar are charged by celestial powers to guard the weak and strike against evil.",
            ability_bonuses={"Wisdom": 1},
            traits=[
                RacialTrait(
                    name="Radiant Soul",
                    description="Starting at 3rd level, you can use your action to unleash divine energy. For 1 minute, you sprout spectral wings (30 ft. flying speed) and deal extra radiant damage equal to your level once per turn. Usable once per long rest.",
                ),
            ],
        ),
        Subrace(
            name="Scourge Aasimar",
            description="Scourge aasimar are imbued with a divine energy that blazes intensely within them.",
            ability_bonuses={"Constitution": 1},
            traits=[
                RacialTrait(
                    name="Radiant Consumption",
                    description="Starting at 3rd level, you can use your action to unleash divine energy. For 1 minute, you shed bright light and deal radiant damage to creatures within 10 feet (including yourself) equal to half your level. You also deal extra radiant damage equal to your level once per turn. Usable once per long rest.",
                ),
            ],
        ),
        Subrace(
            name="Fallen Aasimar",
            description="Fallen aasimar are touched by dark powers in their youth or have turned to evil of their own accord.",
            ability_bonuses={"Strength": 1},
            traits=[
                RacialTrait(
                    name="Necrotic Shroud",
                    description="Starting at 3rd level, you can use your action to unleash divine energy. For 1 minute, your eyes become pools of darkness and skeletal wings sprout from your back. Creatures within 10 feet must succeed on a Charisma save or be frightened. You deal extra necrotic damage equal to your level once per turn. Usable once per long rest.",
                ),
            ],
        ),
    ],
)

# =============================================================================
# GOLIATH
# =============================================================================

GOLIATH = Species(
    name="Goliath",
    description=(
        "Goliaths are massive humanoids who dwell in the highest mountain peaks. Their stone-gray "
        "skin is marked with darker patches that they believe are signs of destiny. Competition "
        "drives every aspect of goliath society, as they constantly measure themselves against others."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Strength": 2, "Constitution": 1},
    languages=["Common", "Giant"],
    darkvision=0,
    age_info="Goliaths have lifespans comparable to humans, reaching adulthood in their late teens and living less than a century.",
    alignment_tendency="Goliath society, with its clear roles and tasks, has a strong lawful bent.",
    traits=[
        RacialTrait(
            name="Natural Athlete",
            description="You have proficiency in the Athletics skill.",
        ),
        RacialTrait(
            name="Stone's Endurance",
            description="When you take damage, you can use your reaction to roll a d12 and reduce the damage by the number rolled plus your Constitution modifier. You can use this once per short or long rest.",
        ),
        RacialTrait(
            name="Powerful Build",
            description="You count as one size larger when determining carrying capacity and the weight you can push, drag, or lift.",
        ),
        RacialTrait(
            name="Mountain Born",
            description="You have resistance to cold damage and are acclimated to high altitude, including elevations above 20,000 feet.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# TABAXI
# =============================================================================

TABAXI = Species(
    name="Tabaxi",
    description=(
        "Tabaxi are feline humanoids driven by curiosity to collect stories, artifacts, and lore. "
        "Hailing from distant lands, they are known for their agility, their wanderlust, and their "
        "tendency to appear wherever something interesting is happening."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Dexterity": 2, "Charisma": 1},
    languages=["Common"],
    darkvision=60,
    age_info="Tabaxi have lifespans equivalent to humans.",
    alignment_tendency="Tabaxi tend toward chaotic alignments, as they let impulse and fancy guide their decisions.",
    traits=[
        RacialTrait(
            name="Feline Agility",
            description="When you move on your turn, you can double your speed until the end of the turn. You can't use this again until you move 0 feet on one of your turns.",
        ),
        RacialTrait(
            name="Cat's Claws",
            description="You have a climbing speed of 20 feet. Your claws are natural weapons, which you can use to make unarmed strikes dealing 1d4 + Strength modifier slashing damage.",
        ),
        RacialTrait(
            name="Cat's Talent",
            description="You have proficiency in the Perception and Stealth skills.",
        ),
        RacialTrait(
            name="Extra Language",
            description="You can speak, read, and write one language of your choice.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# FIRBOLG
# =============================================================================

FIRBOLG = Species(
    name="Firbolg",
    description=(
        "Firbolgs are gentle giants who prefer to avoid contact with other sentient races. "
        "They live in remote forest strongholds, devoted to protecting nature and living in "
        "harmony with the woodland creatures around them."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Wisdom": 2, "Strength": 1},
    languages=["Common", "Elvish", "Giant"],
    darkvision=0,
    age_info="Firbolgs reach adulthood around 30 and can live for 500 years.",
    alignment_tendency="Firbolgs are strongly tied to neutral good, protecting nature and helping others.",
    traits=[
        RacialTrait(
            name="Firbolg Magic",
            description="You can cast detect magic and disguise self once each per short or long rest. When using disguise self, you can appear up to 3 feet shorter. Wisdom is your spellcasting ability.",
        ),
        RacialTrait(
            name="Hidden Step",
            description="As a bonus action, you can turn invisible until the start of your next turn, or until you attack, make a damage roll, or force someone to make a saving throw. You can use this once per short or long rest.",
        ),
        RacialTrait(
            name="Powerful Build",
            description="You count as one size larger when determining carrying capacity and the weight you can push, drag, or lift.",
        ),
        RacialTrait(
            name="Speech of Beast and Leaf",
            description="You can communicate simple ideas to beasts and plants. You have advantage on Charisma checks to influence them.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# KENKU
# =============================================================================

KENKU = Species(
    name="Kenku",
    description=(
        "Kenku are flightless avian humanoids cursed to mimic sounds and unable to speak "
        "original words. Haunted by an ancient crime, they lurk in the shadows of cities, "
        "working as spies, thieves, and messengers while longing for the skies they cannot reach."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Dexterity": 2, "Wisdom": 1},
    languages=["Common", "Auran"],
    darkvision=0,
    age_info="Kenku have shorter lifespans than humans, reaching adulthood at about 12 and living to 60.",
    alignment_tendency="Kenku are typically chaotic neutral, driven by self-interest.",
    traits=[
        RacialTrait(
            name="Expert Forgery",
            description="You can duplicate other creatures' handwriting and craftwork with advantage on checks to produce forgeries or duplicates.",
        ),
        RacialTrait(
            name="Kenku Training",
            description="You are proficient in two of the following skills: Acrobatics, Deception, Stealth, or Sleight of Hand.",
        ),
        RacialTrait(
            name="Mimicry",
            description="You can mimic sounds you have heard, including voices. A creature that hears the sounds can tell they are imitations with a successful Wisdom (Insight) check opposed by your Charisma (Deception) check.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# LIZARDFOLK
# =============================================================================

LIZARDFOLK = Species(
    name="Lizardfolk",
    description=(
        "Lizardfolk are cold-blooded reptilian humanoids who see the world through a lens of "
        "survival and practicality. Emotions are foreign concepts to them, replaced by simple "
        "assessments of threat, food, and utility. Their alien mindset makes them seem unsettling to others."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Constitution": 2, "Wisdom": 1},
    languages=["Common", "Draconic"],
    darkvision=0,
    age_info="Lizardfolk reach maturity around age 14 and rarely live longer than 60 years.",
    alignment_tendency="Most lizardfolk are neutral, viewing the world without moral bias.",
    traits=[
        RacialTrait(
            name="Bite",
            description="Your fanged maw is a natural weapon, dealing 1d6 + Strength modifier piercing damage.",
        ),
        RacialTrait(
            name="Cunning Artisan",
            description="During a short rest, you can harvest bone and hide from a slain creature to create a shield, club, javelin, or 1d4 darts or blowgun needles.",
        ),
        RacialTrait(
            name="Hold Breath",
            description="You can hold your breath for up to 15 minutes at a time.",
        ),
        RacialTrait(
            name="Hunter's Lore",
            description="You gain proficiency in two of the following skills: Animal Handling, Nature, Perception, Stealth, or Survival.",
        ),
        RacialTrait(
            name="Natural Armor",
            description="When unarmored, your AC equals 13 + Dexterity modifier. You can use a shield and still gain this benefit.",
        ),
        RacialTrait(
            name="Hungry Jaws",
            description="As a bonus action, you can make a bite attack. If it hits, you gain temporary hit points equal to your Constitution modifier (minimum 1). You can use this once per short or long rest.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# GOBLIN
# =============================================================================

GOBLIN = Species(
    name="Goblin",
    description=(
        "Goblins are small, cunning creatures with a reputation for mischief and mayhem. "
        "Though often underestimated, their quick wits and nimble bodies make them surprisingly "
        "effective at both causing trouble and escaping the consequences."
    ),
    size="Small",
    speed=30,
    ability_bonuses={"Dexterity": 2, "Constitution": 1},
    languages=["Common", "Goblin"],
    darkvision=60,
    age_info="Goblins reach adulthood at age 8 and live up to 60 years.",
    alignment_tendency="Goblins tend toward neutral evil but can be any alignment.",
    traits=[
        RacialTrait(
            name="Fury of the Small",
            description="When you damage a creature larger than you with an attack or spell, you can deal extra damage equal to your level. You can use this once per short or long rest.",
        ),
        RacialTrait(
            name="Nimble Escape",
            description="You can take the Disengage or Hide action as a bonus action on each of your turns.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# HOBGOBLIN
# =============================================================================

HOBGOBLIN = Species(
    name="Hobgoblin",
    description=(
        "Hobgoblins are disciplined and militaristic humanoids who value strength, honor, and "
        "hierarchy. Their society is built around warfare and conquest, with every hobgoblin "
        "trained from birth to serve the legion with unwavering loyalty."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Constitution": 2, "Intelligence": 1},
    languages=["Common", "Goblin"],
    darkvision=60,
    age_info="Hobgoblins mature at the same rate as humans and have similar lifespans.",
    alignment_tendency="Hobgoblin society is built on fidelity to a rigid code of honor, making them strongly lawful.",
    traits=[
        RacialTrait(
            name="Martial Training",
            description="You are proficient with two martial weapons of your choice and with light armor.",
        ),
        RacialTrait(
            name="Saving Face",
            description="If you miss with an attack roll or fail an ability check or saving throw, you can gain a bonus equal to the number of allies you can see within 30 feet (maximum +5). You can use this once per short or long rest.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# BUGBEAR
# =============================================================================

BUGBEAR = Species(
    name="Bugbear",
    description=(
        "Bugbears are massive goblinoids covered in coarse fur, with long limbs and surprising "
        "stealth for their size. They are ambush predators by nature, patient hunters who strike "
        "with devastating force when the moment is right."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Strength": 2, "Dexterity": 1},
    languages=["Common", "Goblin"],
    darkvision=60,
    age_info="Bugbears reach adulthood at age 16 and live up to 80 years.",
    alignment_tendency="Bugbears endure a violent existence, making them typically chaotic evil.",
    traits=[
        RacialTrait(
            name="Long-Limbed",
            description="Your reach for melee attacks increases by 5 feet.",
        ),
        RacialTrait(
            name="Powerful Build",
            description="You count as one size larger when determining carrying capacity and the weight you can push, drag, or lift.",
        ),
        RacialTrait(
            name="Sneaky",
            description="You are proficient in the Stealth skill.",
        ),
        RacialTrait(
            name="Surprise Attack",
            description="If you hit a creature that is surprised, you deal an extra 2d6 damage. You can use this once per combat.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# KOBOLD
# =============================================================================

KOBOLD = Species(
    name="Kobold",
    description=(
        "Kobolds are small reptilian humanoids who claim kinship with dragons. Though individually "
        "weak, they excel at teamwork and trap-making, using cunning and numbers to overcome foes "
        "far stronger than themselves."
    ),
    size="Small",
    speed=30,
    ability_bonuses={"Dexterity": 2},
    languages=["Common", "Draconic"],
    darkvision=60,
    age_info="Kobolds reach adulthood at age 6 and can live up to 120 years but rarely do so.",
    alignment_tendency="Kobolds are typically lawful evil, focused on survival and service to dragons.",
    traits=[
        RacialTrait(
            name="Draconic Cry",
            description="As a bonus action, you let out a cry that gives you and allies within 10 feet advantage on attack rolls against enemies within 10 feet of you until the start of your next turn. You can use this a number of times equal to your proficiency bonus per long rest.",
        ),
        RacialTrait(
            name="Kobold Legacy",
            description="Choose one: proficiency in a skill (Arcana, Investigation, Medicine, Sleight of Hand, or Survival), a sorcerer cantrip, or the ability to make advantage-giving Help actions as a bonus action.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# ORC
# =============================================================================

ORC = Species(
    name="Orc",
    description=(
        "Orcs are powerful humanoids with gray-green skin, prominent tusks, and a culture "
        "built around strength and martial prowess. Their fierce determination and physical "
        "might make them formidable warriors and steadfast allies."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Strength": 2, "Constitution": 1},
    languages=["Common", "Orc"],
    darkvision=60,
    age_info="Orcs reach adulthood at age 12 and live up to 50 years.",
    alignment_tendency="Orcs vary widely in alignment, though many follow the path of strength.",
    traits=[
        RacialTrait(
            name="Adrenaline Rush",
            description="As a bonus action, you can move up to your speed toward an enemy you can see. You can use this a number of times equal to your proficiency bonus per long rest.",
        ),
        RacialTrait(
            name="Powerful Build",
            description="You count as one size larger when determining carrying capacity and the weight you can push, drag, or lift.",
        ),
        RacialTrait(
            name="Relentless Endurance",
            description="When you are reduced to 0 hit points but not killed outright, you can drop to 1 hit point instead. You can't use this feature again until you finish a long rest.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# TORTLE
# =============================================================================

TORTLE = Species(
    name="Tortle",
    description=(
        "Tortles are turtle-like humanoids with heavy shells and a calm, philosophical demeanor. "
        "They live simple lives in harmony with nature, and many undertake wandering journeys "
        "to experience the world before settling down in their later years."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Strength": 2, "Wisdom": 1},
    languages=["Common", "Aquan"],
    darkvision=0,
    age_info="Tortles reach adulthood by age 15 and live an average of 50 years.",
    alignment_tendency="Tortles tend to lead orderly, ritualistic lives, leaning toward lawful good.",
    traits=[
        RacialTrait(
            name="Claws",
            description="Your claws are natural weapons, dealing 1d4 + Strength modifier slashing damage on unarmed strikes.",
        ),
        RacialTrait(
            name="Hold Breath",
            description="You can hold your breath for up to 1 hour at a time.",
        ),
        RacialTrait(
            name="Natural Armor",
            description="Your shell provides a base AC of 17 (Dexterity doesn't apply). You can't wear armor, but can use shields.",
        ),
        RacialTrait(
            name="Shell Defense",
            description="You can withdraw into your shell as an action. Until you emerge as a bonus action, you gain +4 AC, have advantage on Strength and Constitution saves, but are prone, have speed 0, and have disadvantage on Dexterity saves.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# TRITON
# =============================================================================

TRITON = Species(
    name="Triton",
    description=(
        "Tritons are aquatic humanoids who guard the ocean depths from threats that would rise "
        "to menace the surface world. Noble and somewhat aloof, they consider themselves "
        "protectors of the seas and all who dwell near them."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Strength": 1, "Constitution": 1, "Charisma": 1},
    languages=["Common", "Primordial"],
    darkvision=60,
    age_info="Tritons reach maturity around age 15 and can live to be 200.",
    alignment_tendency="Tritons tend toward lawful good, driven by a sense of duty to protect others.",
    traits=[
        RacialTrait(
            name="Amphibious",
            description="You can breathe air and water.",
        ),
        RacialTrait(
            name="Control Air and Water",
            description="You can cast fog cloud at 1st level. At 3rd level, you can cast gust of wind. At 5th level, you can cast wall of water. You can cast each once per long rest. Charisma is your spellcasting ability.",
        ),
        RacialTrait(
            name="Emissary of the Sea",
            description="You can communicate simple ideas to beasts that can breathe water.",
        ),
        RacialTrait(
            name="Guardians of the Depths",
            description="You have resistance to cold damage and ignore any drawbacks from a deep underwater environment.",
        ),
        RacialTrait(
            name="Swim Speed",
            description="You have a swimming speed of 30 feet.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# AARAKOCRA
# =============================================================================

AARAKOCRA = Species(
    name="Aarakocra",
    description=(
        "Aarakocra are avian humanoids with wings and talons, hailing from the Elemental Plane "
        "of Air. Sequestered in high mountains, they are fierce warriors who protect their nests "
        "and watch the skies for threats from the lower planes."
    ),
    size="Medium",
    speed=25,
    ability_bonuses={"Dexterity": 2, "Wisdom": 1},
    languages=["Common", "Aarakocra", "Auran"],
    darkvision=0,
    age_info="Aarakocra reach maturity by age 3 and rarely live longer than 30 years.",
    alignment_tendency="Most aarakocra are good and rarely choose to stay in one place for long.",
    traits=[
        RacialTrait(
            name="Flight",
            description="You have a flying speed of 50 feet. To use this speed, you can't be wearing medium or heavy armor.",
        ),
        RacialTrait(
            name="Talons",
            description="Your talons are natural weapons, dealing 1d4 + Strength modifier slashing damage on unarmed strikes.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# GENASI
# =============================================================================

GENASI = Species(
    name="Genasi",
    description=(
        "Genasi carry the power of elemental planes in their blood. Whether descended from genies "
        "or exposed to elemental energy, they manifest traits of air, earth, fire, or water that "
        "set them apart from ordinary mortals."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Constitution": 2},
    languages=["Common", "Primordial"],
    darkvision=0,
    age_info="Genasi mature at about the same rate as humans and reach adulthood in their late teens. They live somewhat longer than humans do, up to 120 years.",
    alignment_tendency="Independent and self-reliant, genasi tend toward a neutral alignment.",
    traits=[],
    subraces=[
        Subrace(
            name="Air Genasi",
            description="Air genasi carry the essence of elemental air, giving them pale blue skin, light hair, and a breeze that follows them.",
            ability_bonuses={"Dexterity": 1},
            traits=[
                RacialTrait(
                    name="Unending Breath",
                    description="You can hold your breath indefinitely while not incapacitated.",
                ),
                RacialTrait(
                    name="Mingle with the Wind",
                    description="You can cast levitate on yourself once per long rest. Constitution is your spellcasting ability.",
                ),
            ],
        ),
        Subrace(
            name="Earth Genasi",
            description="Earth genasi are drawn from the elemental earth, with skin like stone and eyes that glimmer like gems.",
            ability_bonuses={"Strength": 1},
            traits=[
                RacialTrait(
                    name="Earth Walk",
                    description="You can move across difficult terrain made of earth or stone without expending extra movement.",
                ),
                RacialTrait(
                    name="Merge with Stone",
                    description="You can cast pass without trace once per long rest. Constitution is your spellcasting ability.",
                ),
            ],
        ),
        Subrace(
            name="Fire Genasi",
            description="Fire genasi carry the heat of flames, with skin tones of deep reds and eyes like molten gold.",
            ability_bonuses={"Intelligence": 1},
            traits=[
                RacialTrait(
                    name="Fire Resistance",
                    description="You have resistance to fire damage.",
                ),
                RacialTrait(
                    name="Reach to the Blaze",
                    description="You know the produce flame cantrip. At 3rd level, you can cast burning hands once per long rest. Constitution is your spellcasting ability.",
                ),
            ],
        ),
        Subrace(
            name="Water Genasi",
            description="Water genasi descend from the elemental water, with skin that glistens and hair that flows like waves.",
            ability_bonuses={"Wisdom": 1},
            traits=[
                RacialTrait(
                    name="Acid Resistance",
                    description="You have resistance to acid damage.",
                ),
                RacialTrait(
                    name="Amphibious",
                    description="You can breathe air and water.",
                ),
                RacialTrait(
                    name="Swim",
                    description="You have a swimming speed of 30 feet.",
                ),
                RacialTrait(
                    name="Call to the Wave",
                    description="You know the shape water cantrip. At 3rd level, you can cast create or destroy water once per long rest. Constitution is your spellcasting ability.",
                ),
            ],
        ),
    ],
)

# =============================================================================
# CHANGELING
# =============================================================================

CHANGELING = Species(
    name="Changeling",
    description=(
        "Changelings possess a supernatural ability to alter their physical appearance. "
        "Whether due to fey ancestry or magical experimentation, they can shift their features "
        "at will, making them natural infiltrators and masters of disguise."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Charisma": 2},
    languages=["Common"],
    darkvision=0,
    age_info="Changelings mature slightly faster than humans but share a similar lifespan, typically about a century.",
    alignment_tendency="Changelings tend toward pragmatic neutrality, adopting whatever identity serves them best.",
    traits=[
        RacialTrait(
            name="Shapechanger",
            description="As an action, you can change your appearance to that of any humanoid you have seen, including height, weight, facial features, voice, hair, and clothing. You revert on death. A creature can tell you are disguised with a contested Insight vs. your Deception check.",
        ),
        RacialTrait(
            name="Changeling Instincts",
            description="You have proficiency with two of the following skills: Deception, Insight, Intimidation, or Persuasion.",
        ),
        RacialTrait(
            name="Extra Languages",
            description="You can speak, read, and write two languages of your choice.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# WARFORGED
# =============================================================================

WARFORGED = Species(
    name="Warforged",
    description=(
        "Warforged are constructs built for war, now free to find their own purpose. Made of "
        "metal, stone, and wood, they possess souls and seek meaning beyond the battlefields "
        "for which they were created."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Constitution": 2},
    languages=["Common"],
    darkvision=0,
    age_info="Warforged are created as adults and don't age. A warforged doesn't know how long it might live.",
    alignment_tendency="Warforged take comfort in order and discipline, tending toward law.",
    traits=[
        RacialTrait(
            name="Constructed Resilience",
            description="You have advantage on saving throws against being poisoned, and resistance to poison damage. You don't need to eat, drink, or breathe. You are immune to disease and don't need to sleep.",
        ),
        RacialTrait(
            name="Sentry's Rest",
            description="Instead of sleeping, you enter an inactive state for 6 hours. You appear inert but remain conscious and can perceive your surroundings.",
        ),
        RacialTrait(
            name="Integrated Protection",
            description="Your body provides a base AC of 11 + proficiency bonus. You can use a shield and still benefit from this. You can only don armor you're proficient with by incorporating it into your body over 1 hour, and similarly doff it over 1 hour.",
        ),
        RacialTrait(
            name="Specialized Design",
            description="You gain one skill proficiency and one tool proficiency of your choice.",
        ),
        RacialTrait(
            name="Extra Language",
            description="You can speak, read, and write one language of your choice.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# SHIFTER
# =============================================================================

SHIFTER = Species(
    name="Shifter",
    description=(
        "Shifters are descended from humans and lycanthropes. Though they can't fully transform, "
        "they can temporarily shift to tap into their bestial nature, gaining enhanced abilities "
        "that reflect their animal heritage."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={},  # Varies by subrace
    languages=["Common"],
    darkvision=60,
    age_info="Shifters are quick to mature, reaching adulthood at 10 and rarely living past 70.",
    alignment_tendency="Shifters tend toward neutrality, concerned with their own survival above all else.",
    traits=[
        RacialTrait(
            name="Shifting",
            description="As a bonus action, you can shift for 1 minute or until you end it as a bonus action. While shifted, you gain temporary hit points equal to your level + Constitution modifier. You can shift a number of times equal to your proficiency bonus per long rest. Additional benefits depend on your subrace.",
        ),
    ],
    subraces=[
        Subrace(
            name="Beasthide",
            description="Beasthide shifters are especially tough, channeling the resilience of a bear or boar.",
            ability_bonuses={"Constitution": 2, "Strength": 1},
            traits=[
                RacialTrait(
                    name="Natural Athlete",
                    description="You have proficiency in the Athletics skill.",
                ),
                RacialTrait(
                    name="Shifting Feature",
                    description="While shifted, you gain +1 AC.",
                ),
            ],
        ),
        Subrace(
            name="Longtooth",
            description="Longtooth shifters channel predatory ferocity, growing fearsome fangs.",
            ability_bonuses={"Strength": 2, "Dexterity": 1},
            traits=[
                RacialTrait(
                    name="Fierce",
                    description="You have proficiency in the Intimidation skill.",
                ),
                RacialTrait(
                    name="Shifting Feature",
                    description="While shifted, you can make a bite attack as a bonus action, dealing 1d6 + Strength modifier piercing damage.",
                ),
            ],
        ),
        Subrace(
            name="Swiftstride",
            description="Swiftstride shifters embody feline grace and speed.",
            ability_bonuses={"Dexterity": 2, "Charisma": 1},
            traits=[
                RacialTrait(
                    name="Graceful",
                    description="You have proficiency in the Acrobatics skill.",
                ),
                RacialTrait(
                    name="Shifting Feature",
                    description="While shifted, your speed increases by 10 feet. Additionally, you can move up to 10 feet as a reaction when an enemy ends its turn within 5 feet of you without provoking opportunity attacks.",
                ),
            ],
        ),
        Subrace(
            name="Wildhunt",
            description="Wildhunt shifters channel the keen senses of wolves and other trackers.",
            ability_bonuses={"Wisdom": 2, "Dexterity": 1},
            traits=[
                RacialTrait(
                    name="Natural Tracker",
                    description="You have proficiency in the Survival skill.",
                ),
                RacialTrait(
                    name="Shifting Feature",
                    description="While shifted, you have advantage on Wisdom checks, and no creature within 30 feet can make an attack roll with advantage against you unless you are incapacitated.",
                ),
            ],
        ),
    ],
)

# =============================================================================
# YUAN-TI PUREBLOOD
# =============================================================================

YUAN_TI = Species(
    name="Yuan-ti Pureblood",
    description=(
        "Yuan-ti purebloods are the most human-looking of the serpent folk, able to pass as "
        "human with only minor tells like slit pupils or patches of scales. They are cold, "
        "calculating, and devoted to advancing their mysterious agendas."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Charisma": 2, "Intelligence": 1},
    languages=["Common", "Abyssal", "Draconic"],
    darkvision=60,
    age_info="Yuan-ti purebloods mature at the same rate as humans and have similar lifespans.",
    alignment_tendency="Yuan-ti are typically neutral evil, viewing other creatures as tools or food.",
    traits=[
        RacialTrait(
            name="Innate Spellcasting",
            description="You know the poison spray cantrip. At 3rd level, you can cast animal friendship (snakes only) at will. At 3rd level, you can cast suggestion once per long rest. Charisma is your spellcasting ability.",
        ),
        RacialTrait(
            name="Magic Resistance",
            description="You have advantage on saving throws against spells and other magical effects.",
        ),
        RacialTrait(
            name="Poison Immunity",
            description="You are immune to poison damage and the poisoned condition.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# CENTAUR
# =============================================================================

CENTAUR = Species(
    name="Centaur",
    description=(
        "Centaurs are majestic beings with the upper body of a humanoid and the lower body "
        "of a horse. They roam wide grasslands and forests, valuing freedom, nature, and the "
        "bonds of their close-knit communities."
    ),
    size="Medium",
    speed=40,
    ability_bonuses={"Strength": 2, "Wisdom": 1},
    languages=["Common", "Sylvan"],
    darkvision=0,
    age_info="Centaurs mature and age at about the same rate as humans.",
    alignment_tendency="Centaurs lean toward neutrality, valuing personal freedom and natural balance.",
    traits=[
        RacialTrait(
            name="Fey",
            description="Your creature type is fey, rather than humanoid.",
        ),
        RacialTrait(
            name="Charge",
            description="If you move at least 30 feet straight toward a target and then hit it with a melee weapon attack on the same turn, you can immediately follow that attack with a bonus action, making one attack against the target with your hooves.",
        ),
        RacialTrait(
            name="Hooves",
            description="Your hooves are natural melee weapons, which you can use to make unarmed strikes. If you hit with them, you deal bludgeoning damage equal to 1d4 + your Strength modifier.",
        ),
        RacialTrait(
            name="Equine Build",
            description="You count as one size larger when determining your carrying capacity and the weight you can push or drag. In addition, any climb that requires hands and feet is especially difficult for you. When you make such a climb, each foot of movement costs you 4 extra feet instead of the normal 1 extra foot.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# MINOTAUR
# =============================================================================

MINOTAUR = Species(
    name="Minotaur",
    description=(
        "Minotaurs are barrel-chested humanoids with heads resembling those of bulls. They "
        "embrace their fearsome reputation, channeling their natural strength and aggression "
        "into purpose, whether as warriors, laborers, or champions."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Strength": 2, "Constitution": 1},
    languages=["Common", "Minotaur"],
    darkvision=0,
    age_info="Minotaurs enter adulthood at around 17 and can live up to 150 years.",
    alignment_tendency="Minotaurs believe in a well-ordered society, tending toward lawful alignments.",
    traits=[
        RacialTrait(
            name="Horns",
            description="Your horns are natural melee weapons, which you can use to make unarmed strikes. If you hit with them, you deal piercing damage equal to 1d6 + your Strength modifier.",
        ),
        RacialTrait(
            name="Goring Rush",
            description="Immediately after you use the Dash action on your turn and move at least 20 feet, you can make one melee attack with your horns as a bonus action.",
        ),
        RacialTrait(
            name="Hammering Horns",
            description="Immediately after you hit a creature with a melee attack as part of the Attack action on your turn, you can use a bonus action to attempt to shove that target with your horns. The target must be within 5 feet of you and no more than one size larger than you.",
        ),
        RacialTrait(
            name="Labyrinthine Recall",
            description="You can perfectly recall any path you have traveled.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# SATYR
# =============================================================================

SATYR = Species(
    name="Satyr",
    description=(
        "Satyrs are fey creatures who revel in music, dance, and revelry. With the upper body "
        "of a humanoid and the lower body of a goat, they embody the wild spirit of nature and "
        "the pursuit of pleasure and freedom."
    ),
    size="Medium",
    speed=35,
    ability_bonuses={"Charisma": 2, "Dexterity": 1},
    languages=["Common", "Sylvan"],
    darkvision=0,
    age_info="Satyrs mature and age at about the same rate as humans.",
    alignment_tendency="Satyrs delight in living a life free of restrictions, favoring chaotic alignments.",
    traits=[
        RacialTrait(
            name="Fey",
            description="Your creature type is fey, rather than humanoid.",
        ),
        RacialTrait(
            name="Ram",
            description="You can use your head and horns to make unarmed strikes. If you hit with them, you deal bludgeoning damage equal to 1d4 + your Strength modifier.",
        ),
        RacialTrait(
            name="Magic Resistance",
            description="You have advantage on saving throws against spells and other magical effects.",
        ),
        RacialTrait(
            name="Mirthful Leaps",
            description="Whenever you make a long or high jump, you can roll a d8 and add the number rolled to the number of feet you cover, even when making a standing jump. This extra distance costs movement as normal.",
        ),
        RacialTrait(
            name="Reveler",
            description="You have proficiency in the Performance and Persuasion skills.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# LEONIN
# =============================================================================

LEONIN = Species(
    name="Leonin",
    description=(
        "Leonin are proud lion-like humanoids who live in tight-knit prides on vast savannas. "
        "Fiercely protective of their families and territories, they value strength, honor, and "
        "the bonds of kinship above all else."
    ),
    size="Medium",
    speed=35,
    ability_bonuses={"Constitution": 2, "Strength": 1},
    languages=["Common", "Leonin"],
    darkvision=60,
    age_info="Leonin mature and age at about the same rate as humans.",
    alignment_tendency="Leonin tend toward good alignments, with a strong sense of honor and family loyalty.",
    traits=[
        RacialTrait(
            name="Claws",
            description="Your claws are natural weapons, which you can use to make unarmed strikes. If you hit with them, you deal slashing damage equal to 1d4 + your Strength modifier.",
        ),
        RacialTrait(
            name="Hunter's Instincts",
            description="You have proficiency in one of the following skills of your choice: Athletics, Intimidation, Perception, or Survival.",
        ),
        RacialTrait(
            name="Daunting Roar",
            description="As a bonus action, you can let out an especially menacing roar. Creatures of your choice within 10 feet of you that can hear you must succeed on a Wisdom saving throw (DC 8 + proficiency bonus + Constitution modifier) or become frightened of you until the end of your next turn. Once you use this trait, you can't use it again until you finish a short or long rest.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# LOXODON
# =============================================================================

LOXODON = Species(
    name="Loxodon",
    description=(
        "Loxodons are elephant-like humanoids known for their calm demeanor, excellent memory, "
        "and deep sense of loyalty. They move through life with patience and deliberation, "
        "forming lasting bonds with those they trust."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Constitution": 2, "Wisdom": 1},
    languages=["Common", "Loxodon"],
    darkvision=0,
    age_info="Loxodons mature at about the same rate as humans but live about 450 years.",
    alignment_tendency="Most loxodons are lawful, believing in the value of a peaceful, ordered life.",
    traits=[
        RacialTrait(
            name="Powerful Build",
            description="You count as one size larger when determining your carrying capacity and the weight you can push, drag, or lift.",
        ),
        RacialTrait(
            name="Loxodon Serenity",
            description="You have advantage on saving throws against being charmed or frightened.",
        ),
        RacialTrait(
            name="Natural Armor",
            description="You have thick, leathery skin. When you aren't wearing armor, your AC is 12 + your Constitution modifier. You can use your natural armor to determine your AC if the armor you wear would leave you with a lower AC. A shield's benefits apply as normal while you use your natural armor.",
        ),
        RacialTrait(
            name="Trunk",
            description="You can grasp things with your trunk, and you can use it as a snorkel. It has a reach of 5 feet, and it can lift a number of pounds equal to five times your Strength score. You can use it to do the following simple tasks: lift, drop, hold, push, or pull an object or a creature; open or close a door or a container; grapple someone; or make an unarmed strike. Your DM might allow other simple tasks to be added to that list of options. It can't wield weapons or shields or do anything that requires manual precision.",
        ),
        RacialTrait(
            name="Keen Smell",
            description="Thanks to your sensitive trunk, you have advantage on Wisdom (Perception), Wisdom (Survival), and Intelligence (Investigation) checks that involve smell.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# FAIRY
# =============================================================================

FAIRY = Species(
    name="Fairy",
    description=(
        "Fairies are diminutive fey creatures with gossamer wings and an innate connection to "
        "magic. Curious and playful, they flutter through the world bringing wonder and mischief "
        "wherever they go."
    ),
    size="Small",
    speed=30,
    ability_bonuses={},  # Flexible ability scores in newer rules
    languages=["Common", "Sylvan"],
    darkvision=0,
    age_info="Fairies have a fey nature, and their lifespans are tied to the magic that sustains them.",
    alignment_tendency="Fairies tend toward chaotic alignments, delighting in spontaneity and freedom.",
    traits=[
        RacialTrait(
            name="Creature Type",
            description="You are a Fey.",
        ),
        RacialTrait(
            name="Fairy Magic",
            description="You know the druidcraft cantrip. Starting at 3rd level, you can cast faerie fire once per long rest. Starting at 5th level, you can cast enlarge/reduce once per long rest. You can also cast these spells using spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this race).",
        ),
        RacialTrait(
            name="Flight",
            description="You have a flying speed equal to your walking speed. You can't use this flying speed if you're wearing medium or heavy armor.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# HARENGON
# =============================================================================

HARENGON = Species(
    name="Harengon",
    description=(
        "Harengons are rabbit-folk who originated in the Feywild. Quick-witted and nimble, they "
        "hop through life with an infectious energy, always ready for adventure and never content "
        "to stay in one place for long."
    ),
    size="Medium",  # Can be Small
    speed=30,
    ability_bonuses={},  # Flexible ability scores
    languages=["Common"],
    darkvision=0,
    age_info="Harengons have lifespans comparable to humans.",
    alignment_tendency="Harengons tend toward good alignments but value personal freedom.",
    traits=[
        RacialTrait(
            name="Hare-Trigger",
            description="You can add your proficiency bonus to your initiative rolls.",
        ),
        RacialTrait(
            name="Leporine Senses",
            description="You have proficiency in the Perception skill.",
        ),
        RacialTrait(
            name="Lucky Footwork",
            description="When you fail a Dexterity saving throw, you can use your reaction to roll a d4 and add it to the save, potentially turning the failure into a success. You can't use this reaction if you're prone or your speed is 0.",
        ),
        RacialTrait(
            name="Rabbit Hop",
            description="As a bonus action, you can jump a number of feet equal to five times your proficiency bonus, without provoking opportunity attacks. You can use this trait a number of times equal to your proficiency bonus, regaining all uses when you finish a long rest.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# OWLIN
# =============================================================================

OWLIN = Species(
    name="Owlin",
    description=(
        "Owlins are owl-like humanoids with large eyes and feathered wings. Wise and observant, "
        "they glide silently through the night, their keen senses missing nothing in the darkness "
        "around them."
    ),
    size="Medium",  # Can be Small
    speed=30,
    ability_bonuses={},  # Flexible ability scores
    languages=["Common"],
    darkvision=120,
    age_info="Owlins have lifespans comparable to humans.",
    alignment_tendency="Owlins value knowledge and tend toward neutral alignments.",
    traits=[
        RacialTrait(
            name="Flight",
            description="You have a flying speed equal to your walking speed. You can't use this flying speed if you're wearing medium or heavy armor.",
        ),
        RacialTrait(
            name="Silent Feathers",
            description="You have proficiency in the Stealth skill.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# KALASHTAR
# =============================================================================

KALASHTAR = Species(
    name="Kalashtar",
    description=(
        "Kalashtar are humans bound to spirits from the plane of dreams. This connection grants "
        "them psychic abilities and a serene demeanor, though they carry the weight of their "
        "spirits' ancient conflicts within their souls."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Wisdom": 2, "Charisma": 1},
    languages=["Common", "Quori"],
    darkvision=0,
    age_info="Kalashtar mature and age at the same rate as humans.",
    alignment_tendency="Kalashtar are typically lawful good, guided by the light of their bound spirits.",
    traits=[
        RacialTrait(
            name="Dual Mind",
            description="You have advantage on all Wisdom saving throws.",
        ),
        RacialTrait(
            name="Mental Discipline",
            description="You have resistance to psychic damage.",
        ),
        RacialTrait(
            name="Mind Link",
            description="You can speak telepathically to any creature you can see, provided the creature is within a number of feet of you equal to 10 times your level. You don't need to share a language with the creature for it to understand your telepathic utterances, but the creature must be able to understand at least one language. When you're using this trait to speak telepathically to a creature, you can use your action to give that creature the ability to speak telepathically with you for 1 hour or until you end this effect as an action.",
        ),
        RacialTrait(
            name="Severed from Dreams",
            description="Kalashtar sleep, but they don't connect to the plane of dreams as other creatures do. Instead, their minds draw from the memories of their otherworldly spirit while they sleep. As such, you are immune to spells and other magical effects that require you to dream, like dream, but not to spells and other magical effects that put you to sleep, like sleep.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# GITH (GITHYANKI)
# =============================================================================

GITHYANKI = Species(
    name="Githyanki",
    description=(
        "Githyanki are gaunt humanoids who escaped from mind flayer enslavement eons ago. Now "
        "they dwell in the Astral Plane, raiding other realms as fierce warriors and sorcerers, "
        "united under their immortal lich-queen."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Strength": 2, "Intelligence": 1},
    languages=["Common", "Gith"],
    darkvision=0,
    age_info="Gith reach adulthood in their late teens and live for about a century.",
    alignment_tendency="Githyanki tend toward lawful evil, with a culture built on conquest and martial discipline.",
    traits=[
        RacialTrait(
            name="Decadent Mastery",
            description="You learn one language of your choice, and you are proficient with one skill or tool of your choice.",
        ),
        RacialTrait(
            name="Martial Prodigy",
            description="You are proficient with light and medium armor and with shortswords, longswords, and greatswords.",
        ),
        RacialTrait(
            name="Githyanki Psionics",
            description="You know the mage hand cantrip, and the hand is invisible. Starting at 3rd level, you can cast jump on yourself once per long rest. Starting at 5th level, you can cast misty step once per long rest. Intelligence is your spellcasting ability for these spells.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# GITH (GITHZERAI)
# =============================================================================

GITHZERAI = Species(
    name="Githzerai",
    description=(
        "Githzerai are contemplative humanoids who rejected the violent ways of their githyanki "
        "cousins. Living in monasteries on the plane of Limbo, they have mastered psionic "
        "disciplines that allow them to impose order on chaos itself."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Wisdom": 2, "Intelligence": 1},
    languages=["Common", "Gith"],
    darkvision=0,
    age_info="Gith reach adulthood in their late teens and live for about a century.",
    alignment_tendency="Githzerai tend toward lawful neutral, valuing inner discipline and self-mastery.",
    traits=[
        RacialTrait(
            name="Mental Discipline",
            description="You have advantage on saving throws against the charmed and frightened conditions.",
        ),
        RacialTrait(
            name="Githzerai Psionics",
            description="You know the mage hand cantrip, and the hand is invisible. Starting at 3rd level, you can cast shield once per long rest. Starting at 5th level, you can cast detect thoughts once per long rest. Wisdom is your spellcasting ability for these spells.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# DEEP GNOME (SVIRFNEBLIN)
# =============================================================================

DEEP_GNOME = Species(
    name="Deep Gnome",
    description=(
        "Deep gnomes, or svirfneblin, are gnomes who dwell in the Underdark. Wary and suspicious "
        "of outsiders, they have adapted to the dangers of their subterranean home, becoming "
        "expert miners and masters of stealth and camouflage."
    ),
    size="Small",
    speed=25,
    ability_bonuses={"Intelligence": 2, "Dexterity": 1},
    languages=["Common", "Gnomish", "Undercommon"],
    darkvision=120,
    age_info="Deep gnomes are short-lived for gnomes, reaching adulthood at 25 and living 200 to 250 years.",
    alignment_tendency="Svirfneblin believe that survival depends on avoiding entanglements, tending toward neutrality.",
    traits=[
        RacialTrait(
            name="Gnome Cunning",
            description="You have advantage on Intelligence, Wisdom, and Charisma saving throws against magic.",
        ),
        RacialTrait(
            name="Stone Camouflage",
            description="You have advantage on Dexterity (Stealth) checks to hide in rocky terrain.",
        ),
        RacialTrait(
            name="Svirfneblin Magic",
            description="Starting at 3rd level, you can cast disguise self once per long rest. Starting at 5th level, you can cast nondetection on yourself once per long rest without a material component. Intelligence is your spellcasting ability.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# DUERGAR (GRAY DWARF)
# =============================================================================

DUERGAR = Species(
    name="Duergar",
    description=(
        "Duergar, or gray dwarves, are dour dwellers of the Underdark. Their ancestors were "
        "enslaved by mind flayers, and though they eventually broke free, the experience left "
        "them grim, suspicious, and possessing strange psionic abilities."
    ),
    size="Medium",
    speed=25,
    ability_bonuses={"Constitution": 2, "Strength": 1},
    languages=["Common", "Dwarvish", "Undercommon"],
    darkvision=120,
    age_info="Duergar mature at the same rate as humans but can live over 350 years.",
    alignment_tendency="Most duergar are lawful evil, raised in a harsh society that values obedience and cruelty.",
    traits=[
        RacialTrait(
            name="Dwarven Resilience",
            description="You have advantage on saving throws against poison, and you have resistance to poison damage.",
        ),
        RacialTrait(
            name="Duergar Magic",
            description="Starting at 3rd level, you can cast enlarge/reduce on yourself (enlarge only) once per long rest. Starting at 5th level, you can cast invisibility on yourself once per long rest without a material component. Intelligence is your spellcasting ability.",
        ),
        RacialTrait(
            name="Sunlight Sensitivity",
            description="You have disadvantage on attack rolls and Wisdom (Perception) checks that rely on sight when you, the target of your attack, or whatever you are trying to perceive is in direct sunlight.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# SEA ELF
# =============================================================================

SEA_ELF = Species(
    name="Sea Elf",
    description=(
        "Sea elves fell in love with the wild beauty of the ocean in the earliest days of the "
        "world. They established kingdoms beneath the waves, developing the ability to breathe "
        "water and swim with fish-like grace."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Dexterity": 2, "Constitution": 1},
    languages=["Common", "Elvish", "Aquan"],
    darkvision=60,
    age_info="Sea elves mature and age at the same rate as other elves.",
    alignment_tendency="Sea elves lean toward chaotic alignments, valuing freedom like the ocean itself.",
    traits=[
        RacialTrait(
            name="Fey Ancestry",
            description="You have advantage on saving throws against being charmed, and magic can't put you to sleep.",
        ),
        RacialTrait(
            name="Trance",
            description="Elves don't need to sleep. Instead, they meditate deeply for 4 hours a day.",
        ),
        RacialTrait(
            name="Sea Elf Training",
            description="You have proficiency with the spear, trident, light crossbow, and net.",
        ),
        RacialTrait(
            name="Child of the Sea",
            description="You have a swimming speed of 30 feet, and you can breathe air and water.",
        ),
        RacialTrait(
            name="Friend of the Sea",
            description="Using gestures and sounds, you can communicate simple ideas with any beast that has an innate swimming speed.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# ELADRIN
# =============================================================================

ELADRIN = Species(
    name="Eladrin",
    description=(
        "Eladrin are elves native to the Feywild, a realm of wonder and magic. Their forms shift "
        "with their emotions, taking on aspects of the seasons—spring's joy, summer's passion, "
        "autumn's peace, or winter's sorrow."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Dexterity": 2, "Charisma": 1},
    languages=["Common", "Elvish"],
    darkvision=60,
    age_info="Eladrin mature and age at the same rate as other elves.",
    alignment_tendency="Eladrin are strongly chaotic, their moods and alignments shifting like seasons.",
    traits=[
        RacialTrait(
            name="Fey Ancestry",
            description="You have advantage on saving throws against being charmed, and magic can't put you to sleep.",
        ),
        RacialTrait(
            name="Trance",
            description="Elves don't need to sleep. Instead, they meditate deeply for 4 hours a day.",
        ),
        RacialTrait(
            name="Fey Step",
            description="As a bonus action, you can magically teleport up to 30 feet to an unoccupied space you can see. You can use this trait a number of times equal to your proficiency bonus, regaining all uses when you finish a long rest. When you reach 3rd level, your Fey Step gains an additional effect based on your season, which you can change when you finish a long rest.",
        ),
        RacialTrait(
            name="Shifting Seasons",
            description="At the end of each long rest, you can align yourself with one of the four seasons: Autumn (charming effect), Winter (frightening effect), Spring (teleport an ally), or Summer (deal fire damage).",
        ),
    ],
    subraces=[],
)

# =============================================================================
# SHADAR-KAI
# =============================================================================

SHADAR_KAI = Species(
    name="Shadar-kai",
    description=(
        "Shadar-kai are elves who serve the Raven Queen in the Shadowfell. Their existence in "
        "that bleak realm has drained the color from their skin and hair, and they combat the "
        "plane's soul-numbing effects through extreme emotion and sensation."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={"Dexterity": 2, "Constitution": 1},
    languages=["Common", "Elvish"],
    darkvision=60,
    age_info="Shadar-kai mature and age at the same rate as other elves.",
    alignment_tendency="Most shadar-kai are neutral, shaped by the bleak indifference of the Shadowfell.",
    traits=[
        RacialTrait(
            name="Fey Ancestry",
            description="You have advantage on saving throws against being charmed, and magic can't put you to sleep.",
        ),
        RacialTrait(
            name="Trance",
            description="Elves don't need to sleep. Instead, they meditate deeply for 4 hours a day.",
        ),
        RacialTrait(
            name="Necrotic Resistance",
            description="You have resistance to necrotic damage.",
        ),
        RacialTrait(
            name="Blessing of the Raven Queen",
            description="As a bonus action, you can magically teleport up to 30 feet to an unoccupied space you can see. Once you use this trait, you can't do so again until you finish a long rest. Starting at 3rd level, you also become resistant to all damage when you teleport using this trait. The resistance lasts until the start of your next turn.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# GRUNG
# =============================================================================

GRUNG = Species(
    name="Grung",
    description=(
        "Grungs are small, frog-like humanoids with brightly colored skin that secretes poison. "
        "They live in tribal communities in tropical rainforests, their strict caste system "
        "determined by skin color."
    ),
    size="Small",
    speed=25,
    ability_bonuses={"Dexterity": 2, "Constitution": 1},
    languages=["Common", "Grung"],
    darkvision=0,
    age_info="Grungs reach adulthood at about 1 year old and live to be around 50.",
    alignment_tendency="Most grungs are lawful, living in strictly hierarchical tribal societies.",
    traits=[
        RacialTrait(
            name="Arboreal Alertness",
            description="You have proficiency in the Perception skill.",
        ),
        RacialTrait(
            name="Amphibious",
            description="You can breathe air and water.",
        ),
        RacialTrait(
            name="Poison Immunity",
            description="You are immune to poison damage and the poisoned condition.",
        ),
        RacialTrait(
            name="Poisonous Skin",
            description="Any creature that grapples you or otherwise comes into direct contact with your skin must succeed on a DC 12 Constitution saving throw or become poisoned for 1 minute. A poisoned creature no longer in direct contact with you can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.",
        ),
        RacialTrait(
            name="Standing Leap",
            description="Your long jump is up to 25 feet and your high jump is up to 15 feet, with or without a running start.",
        ),
        RacialTrait(
            name="Water Dependency",
            description="If you fail to immerse yourself in water for at least 1 hour during a day, you suffer 1 level of exhaustion at the end of that day.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# VERDAN
# =============================================================================

VERDAN = Species(
    name="Verdan",
    description=(
        "Verdans are goblinoids who were transformed by exposure to wild magic. They continue "
        "to change and grow throughout their lives, driven by an innate desire to understand "
        "themselves and their place in the world."
    ),
    size="Small",  # Can grow to Medium
    speed=30,
    ability_bonuses={"Constitution": 1, "Charisma": 2},
    languages=["Common", "Goblin"],
    darkvision=0,
    age_info="Verdans reach adulthood at around 24 and can live almost 200 years.",
    alignment_tendency="Verdans tend toward good alignments, driven by their curiosity and empathy.",
    traits=[
        RacialTrait(
            name="Black Blood Healing",
            description="When you roll a 1 or 2 on any Hit Die you spend at the end of a short rest, you can reroll the die and must use the new roll.",
        ),
        RacialTrait(
            name="Limited Telepathy",
            description="You can telepathically speak to any creature you can see within 30 feet. You don't need to share a language, but the creature must understand at least one language to comprehend your speech.",
        ),
        RacialTrait(
            name="Persuasive",
            description="You have proficiency in the Persuasion skill.",
        ),
        RacialTrait(
            name="Telepathic Insight",
            description="You have advantage on all Wisdom and Charisma saving throws.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# AUTOGNOME
# =============================================================================

AUTOGNOME = Species(
    name="Autognome",
    description=(
        "Autognomes are mechanical beings created by rock gnomes. Though constructed rather than "
        "born, they possess souls and free will. Each autognome is unique, built for specific "
        "purposes but free to forge their own destinies."
    ),
    size="Small",
    speed=30,
    ability_bonuses={},  # Flexible ability scores
    languages=["Common", "Gnomish"],
    darkvision=0,
    age_info="Autognomes don't age and could theoretically live forever if properly maintained.",
    alignment_tendency="Autognomes vary widely in alignment based on their programming and experiences.",
    traits=[
        RacialTrait(
            name="Creature Type",
            description="You are a Construct.",
        ),
        RacialTrait(
            name="Armored Casing",
            description="You are encased in thin metal or some other durable material. While you aren't wearing armor, your base AC is 13 + your Dexterity modifier.",
        ),
        RacialTrait(
            name="Built for Success",
            description="You can add a d4 to one attack roll, ability check, or saving throw you make, and you can do so after seeing the d20 roll but before the effects of the roll are resolved. You can use this trait a number of times equal to your proficiency bonus, regaining all uses when you finish a long rest.",
        ),
        RacialTrait(
            name="Healing Machine",
            description="If the mending spell is cast on you, you can spend a Hit Die, roll it, and regain a number of hit points equal to the roll plus your Constitution modifier (minimum 1). In addition, your creator designed you to benefit from several spells that preserve life but that normally don't affect Constructs: cure wounds, healing word, mass cure wounds, mass healing word, and spare the dying.",
        ),
        RacialTrait(
            name="Mechanical Nature",
            description="You have resistance to poison damage and immunity to disease, and you have advantage on saving throws against being paralyzed or poisoned. You don't need to eat, drink, or breathe.",
        ),
        RacialTrait(
            name="Sentry's Rest",
            description="When you take a long rest, you spend at least 6 hours in an inactive, motionless state, instead of sleeping. In this state, you appear inert, but you remain conscious.",
        ),
        RacialTrait(
            name="Specialized Design",
            description="You gain two tool proficiencies of your choice.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# GIFF
# =============================================================================

GIFF = Species(
    name="Giff",
    description=(
        "Giff are hippo-headed humanoids known for their love of firearms, military discipline, "
        "and mercenary work. They travel the Astral Sea in spelljamming vessels, hiring out "
        "their services to the highest bidder."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={},  # Flexible ability scores
    languages=["Common"],
    darkvision=0,
    age_info="Giff mature at the same rate as humans and have similar lifespans.",
    alignment_tendency="Giff respect military hierarchy and tend toward lawful alignments.",
    traits=[
        RacialTrait(
            name="Astral Spark",
            description="Your connection to the Astral Plane grants you a small spark of divine potential. You can add a d4 to one attack roll, ability check, or saving throw you make, and you can do so after seeing the d20 roll but before the effects are resolved. You can use this trait a number of times equal to your proficiency bonus, regaining all uses when you finish a long rest.",
        ),
        RacialTrait(
            name="Firearms Mastery",
            description="You have proficiency with all firearms and ignore the loading property of any firearm.",
        ),
        RacialTrait(
            name="Hippo Build",
            description="You have advantage on Strength-based ability checks and Strength saving throws. In addition, you count as one size larger when determining your carrying capacity and the weight you can push, drag, or lift.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# HADOZEE
# =============================================================================

HADOZEE = Species(
    name="Hadozee",
    description=(
        "Hadozees are simian humanoids with wing-like membranes that stretch from their arms to "
        "their legs. Originally from a world of towering trees, they've become expert climbers "
        "and gliders who thrive among spelljamming crews."
    ),
    size="Medium",  # Can be Small
    speed=30,
    ability_bonuses={},  # Flexible ability scores
    languages=["Common"],
    darkvision=0,
    age_info="Hadozees mature at the same rate as humans and live about as long.",
    alignment_tendency="Hadozees tend toward chaos, preferring flexibility over rigid structure.",
    traits=[
        RacialTrait(
            name="Dexterous Feet",
            description="As a bonus action, you can use your feet to manipulate an object, open or close a door or container, or pick up or set down a Tiny object.",
        ),
        RacialTrait(
            name="Glide",
            description="If you are not incapacitated or wearing heavy armor, you can extend your skin membranes and glide. When you do so, you can perform the following aerial maneuvers: Fall at a rate of 60 feet per round, taking no falling damage. Move up to 5 feet horizontally for every 1 foot you descend.",
        ),
        RacialTrait(
            name="Hadozee Resilience",
            description="When you take damage, you can use your reaction to roll a d6. Add your proficiency bonus to the number rolled, and reduce the damage you take by an amount equal to that total (minimum 0). You can use this trait a number of times equal to your proficiency bonus, regaining all uses when you finish a long rest.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# PLASMOID
# =============================================================================

PLASMOID = Species(
    name="Plasmoid",
    description=(
        "Plasmoids are amorphous beings composed of living ooze. They can reshape their bodies "
        "at will, squeezing through tight spaces and extending pseudopods to manipulate objects. "
        "Despite their alien nature, they possess intelligence and personality."
    ),
    size="Medium",  # Can be Small
    speed=30,
    ability_bonuses={},  # Flexible ability scores
    languages=["Common"],
    darkvision=60,
    age_info="Plasmoids reach maturity at about 20 years and live about 100 years.",
    alignment_tendency="Plasmoids have no strong tendencies toward any particular alignment.",
    traits=[
        RacialTrait(
            name="Creature Type",
            description="You are an Ooze.",
        ),
        RacialTrait(
            name="Amorphous",
            description="You can squeeze through a space as narrow as 1 inch wide, provided you are wearing and carrying nothing. You have advantage on ability checks you make to initiate or escape a grapple.",
        ),
        RacialTrait(
            name="Hold Breath",
            description="You can hold your breath for 1 hour.",
        ),
        RacialTrait(
            name="Natural Resilience",
            description="You have resistance to acid and poison damage, and you have advantage on saving throws against being poisoned.",
        ),
        RacialTrait(
            name="Shape Self",
            description="As an action, you can reshape your body to give yourself a head, one or two arms, one or two legs, and makeshift hands and feet, or you can revert to a limbless blob. While you have a humanlike shape, you can wear clothing and armor made for a Humanoid of your size. As a bonus action, you can extrude a pseudopod that is up to 6 inches wide and 10 feet long or reabsorb it into your body. As part of the same bonus action, you can use this pseudopod to manipulate an object, open or close a door or container, or pick up or set down a Tiny object. The pseudopod can't attack, activate magic items, or carry more than 10 pounds.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# THRI-KREEN
# =============================================================================

THRI_KREEN = Species(
    name="Thri-kreen",
    description=(
        "Thri-kreen are insectoid humanoids with four arms, mantis-like features, and a "
        "chitinous exoskeleton. Originally from desert worlds, they are skilled hunters who "
        "communicate through a combination of clicks, whistles, and telepathy."
    ),
    size="Medium",  # Can be Small
    speed=30,
    ability_bonuses={},  # Flexible ability scores
    languages=["Common", "Thri-kreen"],
    darkvision=60,
    age_info="Thri-kreen have a short lifespan, living only about 30 years.",
    alignment_tendency="Thri-kreen tend toward chaos, as they have little concept of personal property or social hierarchy.",
    traits=[
        RacialTrait(
            name="Chameleon Carapace",
            description="While you aren't wearing armor, your carapace gives you a base AC of 13 + your Dexterity modifier. As an action, you can change the color of your carapace. You have advantage on Dexterity (Stealth) checks made to hide in wilderness.",
        ),
        RacialTrait(
            name="Secondary Arms",
            description="You have two slightly smaller secondary arms below your primary pair of arms. The secondary arms can manipulate an object, open or close a door or container, pick up or set down a Tiny object, or wield a weapon that has the light property.",
        ),
        RacialTrait(
            name="Sleepless",
            description="You don't require sleep and can remain conscious during a long rest, though you must still refrain from strenuous activity to gain the benefit of the rest.",
        ),
        RacialTrait(
            name="Thri-kreen Telepathy",
            description="Without the need for a shared language, you can telepathically speak to any creature you can see within 120 feet of you. When you communicate telepathically with a creature, you can allow that creature to telepathically respond to you.",
        ),
    ],
    subraces=[],
)

# =============================================================================
# TALES OF THE VALIANT LINEAGES
# =============================================================================
# ToV uses Lineage + Heritage system. Lineages are listed here as Species
# with ruleset="tov". Heritages are separate and provide skills/languages.

TOV_BEASTKIN = Species(
    name="Beastkin",
    description=(
        "Beastkin are humanoids who bear the features of animals, whether through ancient "
        "magical transformation, divine blessing, or natural evolution. Each beastkin carries "
        "traits of their animal heritage, from keen senses to natural weapons."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={},  # ToV uses flexible ASI via heritage
    languages=["Common"],
    darkvision=0,
    age_info="Beastkin mature and age at rates similar to humans.",
    alignment_tendency="Beastkin vary widely based on their animal nature and upbringing.",
    ruleset="tov",
    flexible_asi=True,
    traits=[
        RacialTrait(
            name="Animal Instincts",
            description="You have proficiency in one of the following skills of your choice: Acrobatics, Athletics, Perception, Stealth, or Survival.",
        ),
        RacialTrait(
            name="Bestial Trait",
            description="Choose one bestial trait: Claws (1d4 slashing natural weapons), Bite (1d6 piercing natural weapon), Keen Senses (advantage on Perception checks using one sense), or Swift (base speed increases by 5 feet).",
        ),
    ],
    subraces=[],
)

TOV_DWARF = Species(
    name="Dwarf (ToV)",
    description=(
        "Dwarves are stout folk renowned for their craftsmanship, resilience, and long memories. "
        "Whether they dwell in mountain halls or surface cities, dwarves bring dedication and "
        "skill to everything they undertake."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={},
    languages=["Common", "Dwarvish"],
    darkvision=60,
    age_info="Dwarves mature at the same rate as humans but live for centuries.",
    alignment_tendency="Dwarves tend toward lawful alignments, valuing tradition and order.",
    ruleset="tov",
    flexible_asi=True,
    traits=[
        RacialTrait(
            name="Dwarven Resilience",
            description="You have advantage on saving throws against poison, and you have resistance to poison damage.",
        ),
        RacialTrait(
            name="Dwarven Toughness",
            description="Your hit point maximum increases by 1, and it increases by 1 every time you gain a level.",
        ),
        RacialTrait(
            name="Stonecunning",
            description="Whenever you make an Intelligence (History) check related to stonework, you are considered proficient and add double your proficiency bonus.",
        ),
    ],
    subraces=[],
)

TOV_ELF = Species(
    name="Elf (ToV)",
    description=(
        "Elves are graceful beings with an innate connection to magic and nature. Their long "
        "lives grant them patience and perspective that shorter-lived peoples often lack, and "
        "their keen senses make them formidable scouts and archers."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={},
    languages=["Common", "Elvish"],
    darkvision=60,
    age_info="Elves reach physical maturity around age 20 but aren't considered adults until about 100.",
    alignment_tendency="Elves love freedom and variety, tending toward chaotic alignments.",
    ruleset="tov",
    flexible_asi=True,
    traits=[
        RacialTrait(
            name="Fey Ancestry",
            description="You have advantage on saving throws against being charmed, and magic can't put you to sleep.",
        ),
        RacialTrait(
            name="Keen Senses",
            description="You have proficiency in the Perception skill.",
        ),
        RacialTrait(
            name="Trance",
            description="You don't need to sleep and can't be forced to sleep by any means. To gain the benefits of a long rest, you can spend 4 hours in a trancelike meditation, during which you retain consciousness.",
        ),
    ],
    subraces=[],
)

TOV_HUMAN = Species(
    name="Human (ToV)",
    description=(
        "Humans are the most adaptable and diverse of peoples. Their relatively short lives "
        "drive them to achieve great things quickly, and their ambition has led them to spread "
        "across every land and master every trade."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={},
    languages=["Common"],
    darkvision=0,
    age_info="Humans reach adulthood in their late teens and live less than a century.",
    alignment_tendency="Humans tend toward no particular alignment, displaying the full range of morality.",
    ruleset="tov",
    flexible_asi=True,
    traits=[
        RacialTrait(
            name="Ambitious",
            description="You gain proficiency in one skill of your choice and one tool of your choice.",
        ),
        RacialTrait(
            name="Resourceful",
            description="When you make an ability check and roll a 9 or lower on the d20, you can change the roll to a 10. Once you use this trait, you can't use it again until you finish a long rest.",
        ),
        RacialTrait(
            name="Versatile",
            description="You gain one feat of your choice for which you qualify.",
        ),
    ],
    subraces=[],
)

TOV_ORC = Species(
    name="Orc (ToV)",
    description=(
        "Orcs are powerful humanoids known for their strength, endurance, and fierce determination. "
        "Once feared as raiders, many orcs now channel their formidable abilities toward building "
        "communities and forging alliances with other peoples."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={},
    languages=["Common", "Orc"],
    darkvision=60,
    age_info="Orcs reach adulthood at age 12 and rarely live beyond 50 years.",
    alignment_tendency="Orcs tend toward chaotic alignments, valuing personal strength and freedom.",
    ruleset="tov",
    flexible_asi=True,
    traits=[
        RacialTrait(
            name="Adrenaline Rush",
            description="You can take the Dash action as a bonus action. You can use this trait a number of times equal to your proficiency bonus, regaining all uses when you finish a long rest.",
        ),
        RacialTrait(
            name="Powerful Build",
            description="You count as one size larger when determining your carrying capacity and the weight you can push, drag, or lift.",
        ),
        RacialTrait(
            name="Relentless Endurance",
            description="When you are reduced to 0 hit points but not killed outright, you can drop to 1 hit point instead. You can't use this feature again until you finish a long rest.",
        ),
    ],
    subraces=[],
)

TOV_SMALLFOLK = Species(
    name="Smallfolk",
    description=(
        "Smallfolk are diminutive humanoids who make up for their small stature with quick wits, "
        "nimble fingers, and surprising bravery. Whether living in cozy hillside homes or bustling "
        "cities, they bring cheer and resourcefulness wherever they go."
    ),
    size="Small",
    speed=30,
    ability_bonuses={},
    languages=["Common"],
    darkvision=0,
    age_info="Smallfolk reach adulthood around age 20 and generally live into their second century.",
    alignment_tendency="Smallfolk tend toward lawful good, valuing home and community.",
    ruleset="tov",
    flexible_asi=True,
    traits=[
        RacialTrait(
            name="Brave",
            description="You have advantage on saving throws against being frightened.",
        ),
        RacialTrait(
            name="Lucky",
            description="When you roll a 1 on the d20 for an attack roll, ability check, or saving throw, you can reroll the die and must use the new roll.",
        ),
        RacialTrait(
            name="Nimble",
            description="You can move through the space of any creature that is of a size larger than yours.",
        ),
    ],
    subraces=[],
)

TOV_SYDEREAN = Species(
    name="Syderean",
    description=(
        "Sydereans are beings touched by celestial or infernal powers, bearing visible marks of "
        "their otherworldly heritage. Some manifest angelic features while others show fiendish "
        "traits, but all possess innate magical abilities tied to their ancestry."
    ),
    size="Medium",
    speed=30,
    ability_bonuses={},
    languages=["Common", "Celestial"],
    darkvision=60,
    age_info="Sydereans mature at the same rate as humans but can live up to 150 years.",
    alignment_tendency="Sydereans feel pulled toward the alignment of their planar heritage.",
    ruleset="tov",
    flexible_asi=True,
    traits=[
        RacialTrait(
            name="Celestial Resistance",
            description="You have resistance to radiant damage.",
        ),
        RacialTrait(
            name="Otherworldly Legacy",
            description="You know one cantrip of your choice from the cleric spell list. Starting at 3rd level, you can cast a 1st-level spell once per long rest. Charisma is your spellcasting ability for these spells.",
        ),
        RacialTrait(
            name="Healing Hands",
            description="As an action, you can touch a creature and heal hit points equal to your level. Once you use this trait, you can't use it again until you finish a long rest.",
        ),
    ],
    subraces=[],
)

TOV_KOBOLD = Species(
    name="Kobold (ToV)",
    description=(
        "Kobolds are small reptilian humanoids who claim kinship with dragons. Clever and cunning, "
        "they excel at working together, using traps and tactics to overcome foes far larger "
        "than themselves."
    ),
    size="Small",
    speed=30,
    ability_bonuses={},
    languages=["Common", "Draconic"],
    darkvision=60,
    age_info="Kobolds reach adulthood at age 6 and can live up to 120 years.",
    alignment_tendency="Kobolds are typically lawful, focused on the good of their community.",
    ruleset="tov",
    flexible_asi=True,
    traits=[
        RacialTrait(
            name="Draconic Cry",
            description="As a bonus action, you let out a cry that gives you and allies within 10 feet advantage on attack rolls against enemies within 10 feet of you until the start of your next turn. You can use this a number of times equal to your proficiency bonus per long rest.",
        ),
        RacialTrait(
            name="Pack Tactics",
            description="You have advantage on attack rolls against a creature if at least one of your allies is within 5 feet of the creature and the ally isn't incapacitated.",
        ),
    ],
    subraces=[],
)

# ToV Heritages (cultural backgrounds that combine with lineages)
TOV_HERITAGES: dict[str, Heritage] = {
    "Cottage": Heritage(
        name="Cottage",
        description="You grew up in a small rural community where everyone knew each other and worked together.",
        skill_proficiencies=["Animal Handling"],
        languages=1,
        traits=[
            RacialTrait(
                name="Country Wisdom",
                description="You have proficiency with herbalism kits and cook's utensils.",
            ),
        ],
    ),
    "Cosmopolitan": Heritage(
        name="Cosmopolitan",
        description="You were raised in a bustling city where many cultures and peoples mingled.",
        skill_proficiencies=["Insight"],
        languages=2,
        traits=[
            RacialTrait(
                name="Urbane",
                description="You have proficiency in one of the following skills: Deception, Performance, or Persuasion.",
            ),
        ],
    ),
    "Diaspora": Heritage(
        name="Diaspora",
        description="Your people were scattered from their homeland, and you carry their traditions wherever you go.",
        skill_proficiencies=["History"],
        languages=1,
        traits=[
            RacialTrait(
                name="Keeper of Traditions",
                description="You have proficiency with one artisan's tool of your choice and know one additional language.",
            ),
        ],
    ),
    "Nomadic": Heritage(
        name="Nomadic",
        description="You grew up constantly on the move, following herds, trade routes, or the seasons.",
        skill_proficiencies=["Survival"],
        languages=1,
        traits=[
            RacialTrait(
                name="Wanderer",
                description="You have an excellent memory for maps and geography, and you can always find food and fresh water for yourself and up to five others each day.",
            ),
        ],
    ),
    "Slum": Heritage(
        name="Slum",
        description="You grew up in the poorest quarters of a settlement, learning to survive by your wits.",
        skill_proficiencies=["Stealth"],
        languages=1,
        traits=[
            RacialTrait(
                name="Street Smart",
                description="You have proficiency with thieves' tools. You know the layout of any settlement well enough to find hidden routes and safe houses.",
            ),
        ],
    ),
    "Wildlands": Heritage(
        name="Wildlands",
        description="You were raised far from civilization, in forests, mountains, or other untamed regions.",
        skill_proficiencies=["Nature"],
        languages=1,
        traits=[
            RacialTrait(
                name="Child of the Wild",
                description="You have proficiency with one of the following: herbalism kit, navigator's tools, or one type of musical instrument. You can move through nonmagical difficult terrain without expending extra movement.",
            ),
        ],
    ),
}

# Collections for ToV
TOV_LINEAGES: list[Species] = [
    TOV_BEASTKIN,
    TOV_DWARF,
    TOV_ELF,
    TOV_HUMAN,
    TOV_KOBOLD,
    TOV_ORC,
    TOV_SMALLFOLK,
    TOV_SYDEREAN,
]

# =============================================================================
# LOOKUP TABLES AND HELPER FUNCTIONS
# =============================================================================

ALL_SPECIES: dict[str, Species] = {
    # D&D Species (universal/2014/2024)
    "Aarakocra": AARAKOCRA,
    "Aasimar": AASIMAR,
    "Autognome": AUTOGNOME,
    "Bugbear": BUGBEAR,
    "Centaur": CENTAUR,
    "Changeling": CHANGELING,
    "Deep Gnome": DEEP_GNOME,
    "Dragonborn": DRAGONBORN,
    "Duergar": DUERGAR,
    "Dwarf": DWARF,
    "Eladrin": ELADRIN,
    "Elf": ELF,
    "Fairy": FAIRY,
    "Firbolg": FIRBOLG,
    "Genasi": GENASI,
    "Giff": GIFF,
    "Githyanki": GITHYANKI,
    "Githzerai": GITHZERAI,
    "Gnome": GNOME,
    "Goblin": GOBLIN,
    "Goliath": GOLIATH,
    "Grung": GRUNG,
    "Hadozee": HADOZEE,
    "Half-Elf": HALF_ELF,
    "Half-Orc": HALF_ORC,
    "Halfling": HALFLING,
    "Harengon": HARENGON,
    "Hobgoblin": HOBGOBLIN,
    "Human": HUMAN,
    "Kalashtar": KALASHTAR,
    "Kenku": KENKU,
    "Kobold": KOBOLD,
    "Leonin": LEONIN,
    "Lizardfolk": LIZARDFOLK,
    "Loxodon": LOXODON,
    "Minotaur": MINOTAUR,
    "Orc": ORC,
    "Owlin": OWLIN,
    "Plasmoid": PLASMOID,
    "Satyr": SATYR,
    "Sea Elf": SEA_ELF,
    "Shadar-kai": SHADAR_KAI,
    "Shifter": SHIFTER,
    "Tabaxi": TABAXI,
    "Thri-kreen": THRI_KREEN,
    "Tiefling": TIEFLING,
    "Tortle": TORTLE,
    "Triton": TRITON,
    "Verdan": VERDAN,
    "Warforged": WARFORGED,
    "Yuan-ti Pureblood": YUAN_TI,
    # ToV Lineages
    "Beastkin (ToV)": TOV_BEASTKIN,
    "Dwarf (ToV)": TOV_DWARF,
    "Elf (ToV)": TOV_ELF,
    "Human (ToV)": TOV_HUMAN,
    "Kobold (ToV)": TOV_KOBOLD,
    "Orc (ToV)": TOV_ORC,
    "Smallfolk (ToV)": TOV_SMALLFOLK,
    "Syderean (ToV)": TOV_SYDEREAN,
}

# D&D-only species (excludes ToV)
DND_SPECIES: dict[str, Species] = {
    k: v for k, v in ALL_SPECIES.items() if v.ruleset != "tov"
}

# Draconic Ancestry table for Dragonborn
DRACONIC_ANCESTRY: dict[str, dict[str, str]] = {
    "Black": {"damage_type": "Acid", "breath_weapon": "5 by 30 ft. line (Dex. save)"},
    "Blue": {"damage_type": "Lightning", "breath_weapon": "5 by 30 ft. line (Dex. save)"},
    "Brass": {"damage_type": "Fire", "breath_weapon": "5 by 30 ft. line (Dex. save)"},
    "Bronze": {"damage_type": "Lightning", "breath_weapon": "5 by 30 ft. line (Dex. save)"},
    "Copper": {"damage_type": "Acid", "breath_weapon": "5 by 30 ft. line (Dex. save)"},
    "Gold": {"damage_type": "Fire", "breath_weapon": "15 ft. cone (Dex. save)"},
    "Green": {"damage_type": "Poison", "breath_weapon": "15 ft. cone (Con. save)"},
    "Red": {"damage_type": "Fire", "breath_weapon": "15 ft. cone (Dex. save)"},
    "Silver": {"damage_type": "Cold", "breath_weapon": "15 ft. cone (Con. save)"},
    "White": {"damage_type": "Cold", "breath_weapon": "15 ft. cone (Con. save)"},
}


def get_species(name: str) -> Optional[Species]:
    """Get a species by name (case-insensitive)."""
    for species_name, species in ALL_SPECIES.items():
        if species_name.lower() == name.lower():
            return species
    return None


def get_all_species_names() -> list[str]:
    """Get a list of all species names."""
    return list(ALL_SPECIES.keys())


def get_subraces(species_name: str) -> list[Subrace]:
    """Get all subraces for a species."""
    species = get_species(species_name)
    if species:
        return species.subraces
    return []


def get_subrace(species_name: str, subrace_name: str) -> Optional[Subrace]:
    """Get a specific subrace by species and subrace name."""
    species = get_species(species_name)
    if species:
        for subrace in species.subraces:
            if subrace.name.lower() == subrace_name.lower():
                return subrace
    return None


def search_species(query: str) -> list[Species]:
    """Search species by name or description."""
    query = query.lower()
    results = []
    for species in ALL_SPECIES.values():
        if query in species.name.lower() or query in species.description.lower():
            results.append(species)
    return results


def get_species_by_size(size: str) -> list[Species]:
    """Get all species of a particular size."""
    size = size.capitalize()
    return [s for s in ALL_SPECIES.values() if s.size == size]


def get_species_with_darkvision() -> list[Species]:
    """Get all species that have darkvision."""
    return [s for s in ALL_SPECIES.values() if s.darkvision > 0]


def get_species_for_ruleset(ruleset: str) -> list[Species]:
    """Get species appropriate for a specific ruleset.

    Args:
        ruleset: One of "dnd2014", "dnd2024", or "tov"

    Returns:
        List of species available for that ruleset.
    """
    if ruleset == "tov":
        return [s for s in ALL_SPECIES.values() if s.ruleset == "tov" or s.ruleset is None]
    else:
        # D&D 2014/2024 - exclude ToV-only species
        return [s for s in ALL_SPECIES.values() if s.ruleset != "tov"]


def get_tov_lineages() -> list[Species]:
    """Get all Tales of the Valiant lineages."""
    return TOV_LINEAGES


def get_tov_heritages() -> dict[str, Heritage]:
    """Get all Tales of the Valiant heritages."""
    return TOV_HERITAGES


# =============================================================================
# LEVEL-GATED TRAIT SUPPORT
# =============================================================================

def _extract_level_requirements(description: str) -> list[tuple[int, str]]:
    """Extract level requirements from a trait description.

    Parses patterns like:
    - "At 3rd level, you can cast..."
    - "Starting at 3rd level, you can..."
    - "When you reach 3rd level..."

    Returns list of (level, partial_description) tuples.
    """
    import re

    results = []
    # Pattern to match level mentions
    level_pattern = r'(?:at|starting at|when you reach)\s+(\d+)(?:st|nd|rd|th)\s+level'

    # Find all level mentions
    matches = list(re.finditer(level_pattern, description.lower()))

    if not matches:
        # No level requirements found, trait is available at level 1
        return [(1, description)]

    # Split description by level requirements
    last_end = 0
    for match in matches:
        level = int(match.group(1))
        # Get the text from this level requirement to the next (or end)
        start = match.start()
        results.append((level, description[start:]))

    # If there's text before the first level requirement, it's level 1
    first_match = matches[0]
    if first_match.start() > 0:
        results.insert(0, (1, description[:first_match.start()].strip()))

    return results


def get_trait_min_level(trait: RacialTrait) -> int:
    """Get the minimum level for a trait.

    If trait.min_level is explicitly set (not 1), use that.
    Otherwise, parse the description for level requirements.
    """
    # If explicitly set to something other than default, use it
    if trait.min_level != 1:
        return trait.min_level

    # Parse description for level requirements
    requirements = _extract_level_requirements(trait.description)
    if requirements:
        return requirements[0][0]
    return 1


def get_species_traits_at_level(species: Species, level: int) -> list[RacialTrait]:
    """Get all species traits available at a given character level.

    This checks both the explicit min_level field and parses
    descriptions for level requirements.
    """
    available = []
    for trait in species.traits:
        if get_trait_min_level(trait) <= level:
            available.append(trait)
    return available


def get_subrace_traits_at_level(subrace: Subrace, level: int) -> list[RacialTrait]:
    """Get all subrace traits available at a given character level."""
    available = []
    for trait in subrace.traits:
        if get_trait_min_level(trait) <= level:
            available.append(trait)
    return available


def get_all_traits_at_level(
    species: Species,
    level: int,
    subrace: Optional[Subrace] = None
) -> list[RacialTrait]:
    """Get all traits (species + subrace) available at a given level."""
    traits = get_species_traits_at_level(species, level)
    if subrace:
        traits.extend(get_subrace_traits_at_level(subrace, level))
    return traits
