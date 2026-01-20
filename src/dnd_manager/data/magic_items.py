"""Magic items data for D&D.

Contains SRD magic items with original flavor text and accurate mechanics
across all rarity tiers.
"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from dnd_manager.data.prerequisites import Prerequisite


# Recommended minimum character levels by rarity (based on DMG guidelines)
RARITY_MIN_LEVELS = {
    "common": 1,
    "uncommon": 1,
    "rare": 5,
    "very_rare": 11,
    "legendary": 17,
    "artifact": 17,
}


@dataclass
class MagicItem:
    """Represents a magic item.

    The ruleset field indicates which rules system the item was designed for:
    - None: Universal, works with any ruleset
    - "dnd2014", "dnd2024": D&D specific items
    - "tov": Tales of the Valiant specific items

    Prerequisites:
    - min_level: Minimum character level (None uses rarity default from RARITY_MIN_LEVELS)
    - attunement_requirements: Human-readable string for display
    - structured_prereq: Prerequisite object for validation (optional)
    """

    name: str
    item_type: str  # weapon, armor, wondrous, potion, ring, rod, staff, wand, scroll
    rarity: str  # common, uncommon, rare, very_rare, legendary, artifact
    description: str
    requires_attunement: bool = False
    attunement_requirements: Optional[str] = None
    magic_bonus: Optional[int] = None
    charges: Optional[int] = None
    properties: list[str] = field(default_factory=list)
    ruleset: Optional[str] = None  # None = universal, "dnd2014", "dnd2024", "tov"
    # New prerequisite fields
    min_level: Optional[int] = None  # Override rarity default, None = use RARITY_MIN_LEVELS
    structured_prereq: Optional["Prerequisite"] = None  # Structured attunement requirements

    def get_min_level(self) -> int:
        """Get the minimum character level for this item."""
        if self.min_level is not None:
            return self.min_level
        return RARITY_MIN_LEVELS.get(self.rarity.lower(), 1)


# =============================================================================
# COMMON ITEMS
# =============================================================================

POTION_OF_HEALING = MagicItem(
    name="Potion of Healing",
    item_type="potion",
    rarity="common",
    description=(
        "This vial contains a red liquid that shimmers when agitated. Drinking "
        "this potion restores 2d4 + 2 hit points. Drinking or administering a "
        "potion takes an action."
    ),
)

SPELL_SCROLL_CANTRIP = MagicItem(
    name="Spell Scroll (Cantrip)",
    item_type="scroll",
    rarity="common",
    description=(
        "A spell scroll bears the words of a single spell, written in a mystical "
        "cipher. If the spell is on your class's spell list, you can read the "
        "scroll and cast its spell without providing any material components. "
        "Otherwise, the scroll is unintelligible. This scroll contains a cantrip. "
        "The spell's save DC is 13 and attack bonus is +5."
    ),
)

SPELL_SCROLL_1ST = MagicItem(
    name="Spell Scroll (1st Level)",
    item_type="scroll",
    rarity="common",
    description=(
        "A spell scroll bears the words of a single spell, written in a mystical "
        "cipher. If the spell is on your class's spell list, you can read the "
        "scroll and cast its spell without providing any material components. "
        "This scroll contains a 1st-level spell. The spell's save DC is 13 and "
        "attack bonus is +5. Once the spell is cast, the scroll crumbles to dust."
    ),
)

POTION_OF_CLIMBING = MagicItem(
    name="Potion of Climbing",
    item_type="potion",
    rarity="common",
    description=(
        "When you drink this potion, you gain a climbing speed equal to your "
        "walking speed for 1 hour. During this time, you have advantage on "
        "Strength (Athletics) checks you make to climb. The potion is separated "
        "into brown, silver, and gray layers resembling bands of stone."
    ),
)

DRIFTGLOBE = MagicItem(
    name="Driftglobe",
    item_type="wondrous",
    rarity="common",
    description=(
        "This small sphere of thick glass weighs 1 pound. If you are within 60 "
        "feet of it, you can speak its command word and cause it to emanate the "
        "light or daylight spell. Once used, the daylight effect can't be used "
        "again until the next dawn. You can speak another command word as an "
        "action to make the illuminated globe rise into the air and float no "
        "more than 5 feet off the ground. The globe hovers in this way until you "
        "or another creature grasps it."
    ),
)

HAT_OF_WIZARDRY = MagicItem(
    name="Hat of Wizardry",
    item_type="wondrous",
    rarity="common",
    description=(
        "This antiquated, cone-shaped hat is adorned with gold crescent moons "
        "and stars. While you are wearing it, you gain the following benefits: "
        "You can use the hat as a spellcasting focus for your wizard spells. "
        "You can try to cast a cantrip that you don't know by making a DC 10 "
        "Intelligence (Arcana) check. On a success, you cast the spell. On a "
        "failure, the spell fails and the hat can't be used this way again until "
        "the next dawn."
    ),
    requires_attunement=True,
    attunement_requirements="wizard",
)

TANKARD_OF_SOBRIETY = MagicItem(
    name="Tankard of Sobriety",
    item_type="wondrous",
    rarity="common",
    description=(
        "This tankard has a stern face engraved on one side. You can drink ale, "
        "wine, or any other nonmagical alcoholic beverage poured into it without "
        "becoming inebriated. The tankard has no effect on magical liquids or "
        "harmful substances such as poison."
    ),
)

CLOCKWORK_AMULET = MagicItem(
    name="Clockwork Amulet",
    item_type="wondrous",
    rarity="common",
    description=(
        "This copper amulet contains tiny interlocking gears and is powered by "
        "magic from Mechanus, a plane of clockwork predictability. A creature "
        "that puts an ear to the amulet can hear faint ticking and whirring "
        "noises coming from within. When you make an attack roll while wearing "
        "the amulet, you can forgo rolling the d20 to get a 10 on the die. Once "
        "used, this property can't be used again until the next dawn."
    ),
)

MOON_TOUCHED_SWORD = MagicItem(
    name="Moon-Touched Sword",
    item_type="weapon",
    rarity="common",
    description=(
        "In darkness, the unsheathed blade of this sword sheds moonlight, "
        "creating bright light in a 15-foot radius and dim light for an "
        "additional 15 feet."
    ),
)

RUBY_OF_THE_WAR_MAGE = MagicItem(
    name="Ruby of the War Mage",
    item_type="wondrous",
    rarity="common",
    description=(
        "Etched with eldritch runes, this 1-inch-diameter ruby allows you to "
        "use a simple or martial weapon as a spellcasting focus for your spells. "
        "For this property to work, you must attach the ruby to the weapon by "
        "pressing the ruby against it for at least 10 minutes. Thereafter, the "
        "ruby can't be removed unless you detach it as an action or the weapon "
        "is destroyed."
    ),
    requires_attunement=True,
    attunement_requirements="spellcaster",
)

# =============================================================================
# UNCOMMON ITEMS
# =============================================================================

WEAPON_PLUS_1 = MagicItem(
    name="Weapon, +1",
    item_type="weapon",
    rarity="uncommon",
    description=(
        "You have a +1 bonus to attack and damage rolls made with this magic "
        "weapon. This bonus applies to any weapon type imbued with this enchantment."
    ),
    magic_bonus=1,
)

ARMOR_PLUS_1 = MagicItem(
    name="Armor, +1",
    item_type="armor",
    rarity="uncommon",
    description=(
        "You have a +1 bonus to AC while wearing this armor. This enchantment "
        "can be applied to any type of armor."
    ),
    magic_bonus=1,
)

SHIELD_PLUS_1 = MagicItem(
    name="Shield, +1",
    item_type="armor",
    rarity="uncommon",
    description=(
        "While holding this shield, you have a +1 bonus to AC. This bonus is in "
        "addition to the shield's normal bonus to AC."
    ),
    magic_bonus=1,
)

BAG_OF_HOLDING = MagicItem(
    name="Bag of Holding",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "This bag has an interior space considerably larger than its outside "
        "dimensions, roughly 2 feet in diameter at the mouth and 4 feet deep. "
        "The bag can hold up to 500 pounds, not exceeding a volume of 64 cubic "
        "feet. The bag weighs 15 pounds, regardless of its contents. Retrieving "
        "an item from the bag requires an action. If the bag is overloaded, "
        "pierced, or torn, it ruptures and is destroyed, and its contents are "
        "scattered in the Astral Plane."
    ),
)

BOOTS_OF_ELVENKIND = MagicItem(
    name="Boots of Elvenkind",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While you wear these boots, your steps make no sound, regardless of the "
        "surface you are moving across. You also have advantage on Dexterity "
        "(Stealth) checks that rely on moving silently."
    ),
)

CLOAK_OF_ELVENKIND = MagicItem(
    name="Cloak of Elvenkind",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While you wear this cloak with its hood up, Wisdom (Perception) checks "
        "made to see you have disadvantage, and you have advantage on Dexterity "
        "(Stealth) checks made to hide, as the cloak's color shifts to camouflage "
        "you. Pulling the hood up or down requires an action."
    ),
    requires_attunement=True,
)

CLOAK_OF_PROTECTION = MagicItem(
    name="Cloak of Protection",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "You gain a +1 bonus to AC and saving throws while you wear this cloak."
    ),
    requires_attunement=True,
    magic_bonus=1,
)

GAUNTLETS_OF_OGRE_POWER = MagicItem(
    name="Gauntlets of Ogre Power",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "Your Strength score is 19 while you wear these gauntlets. They have no "
        "effect on you if your Strength is already 19 or higher."
    ),
    requires_attunement=True,
)

GLOVES_OF_THIEVERY = MagicItem(
    name="Gloves of Thievery",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "These gloves are invisible while worn. While wearing them, you gain a "
        "+5 bonus to Dexterity (Sleight of Hand) checks and Dexterity checks "
        "made to pick locks."
    ),
)

GOGGLES_OF_NIGHT = MagicItem(
    name="Goggles of Night",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While wearing these dark lenses, you have darkvision out to a range of "
        "60 feet. If you already have darkvision, wearing the goggles increases "
        "its range by 60 feet."
    ),
)

HEADBAND_OF_INTELLECT = MagicItem(
    name="Headband of Intellect",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "Your Intelligence score is 19 while you wear this headband. It has no "
        "effect on you if your Intelligence is already 19 or higher."
    ),
    requires_attunement=True,
)

LANTERN_OF_REVEALING = MagicItem(
    name="Lantern of Revealing",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While lit, this hooded lantern burns for 6 hours on 1 pint of oil, "
        "shedding bright light in a 30-foot radius and dim light for an "
        "additional 30 feet. Invisible creatures and objects are visible as long "
        "as they are in the lantern's bright light. You can use an action to "
        "lower the hood, reducing the light to dim light in a 5-foot radius."
    ),
)

PEARL_OF_POWER = MagicItem(
    name="Pearl of Power",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While this pearl is on your person, you can use an action to speak its "
        "command word and regain one expended spell slot. If the expended slot "
        "was of 4th level or higher, the new slot is 3rd level. Once you use "
        "the pearl, it can't be used again until the next dawn."
    ),
    requires_attunement=True,
)

RING_OF_JUMPING = MagicItem(
    name="Ring of Jumping",
    item_type="ring",
    rarity="uncommon",
    description=(
        "While wearing this ring, you can cast the jump spell from it as a bonus "
        "action at will, but can target only yourself when you do so."
    ),
    requires_attunement=True,
)

RING_OF_WATER_WALKING = MagicItem(
    name="Ring of Water Walking",
    item_type="ring",
    rarity="uncommon",
    description=(
        "While wearing this ring, you can stand on and move across any liquid "
        "surface as if it were solid ground."
    ),
)

ROPE_OF_CLIMBING = MagicItem(
    name="Rope of Climbing",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "This 60-foot length of silk rope weighs 3 pounds and can hold up to "
        "3,000 pounds. If you hold one end of the rope and use an action to "
        "speak the command word, the rope animates. As a bonus action, you can "
        "command the other end to move toward a destination you choose. That end "
        "moves 10 feet on your turn when you first command it and 10 feet on each "
        "of your turns until reaching its destination, up to its maximum length "
        "away, or until you tell it to stop."
    ),
)

SLIPPERS_OF_SPIDER_CLIMBING = MagicItem(
    name="Slippers of Spider Climbing",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While you wear these light shoes, you can move up, down, and across "
        "vertical surfaces and upside down along ceilings, while leaving your "
        "hands free. You have a climbing speed equal to your walking speed. "
        "However, the slippers don't allow you to move this way on a slippery "
        "surface, such as one covered by ice or oil."
    ),
    requires_attunement=True,
)

WAND_OF_MAGIC_MISSILES = MagicItem(
    name="Wand of Magic Missiles",
    item_type="wand",
    rarity="uncommon",
    description=(
        "This wand has 7 charges. While holding it, you can use an action to "
        "expend 1 or more of its charges to cast the magic missile spell from it. "
        "For 1 charge, you cast the 1st-level version of the spell. You can "
        "increase the spell slot level by one for each additional charge you "
        "expend. The wand regains 1d6 + 1 expended charges daily at dawn. If you "
        "expend the wand's last charge, roll a d20. On a 1, the wand crumbles "
        "into ashes and is destroyed."
    ),
    charges=7,
)

WINGED_BOOTS = MagicItem(
    name="Winged Boots",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While you wear these boots, you have a flying speed equal to your "
        "walking speed. You can use the boots to fly for up to 4 hours, all at "
        "once or in several shorter flights, each one using a minimum of 1 minute "
        "from the duration. If you are flying when the duration expires, you "
        "descend at a rate of 30 feet per round until you land. The boots regain "
        "2 hours of flying capability for every 12 hours they aren't in use."
    ),
    requires_attunement=True,
)

IMMOVABLE_ROD = MagicItem(
    name="Immovable Rod",
    item_type="rod",
    rarity="uncommon",
    description=(
        "This flat iron rod has a button on one end. You can use an action to "
        "press the button, which causes the rod to become magically fixed in "
        "place. Until you or another creature uses an action to push the button "
        "again, the rod doesn't move, even if it is defying gravity. The rod can "
        "hold up to 8,000 pounds of weight. More weight causes the rod to "
        "deactivate and fall."
    ),
)

BOOTS_OF_STRIDING_AND_SPRINGING = MagicItem(
    name="Boots of Striding and Springing",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While you wear these boots, your walking speed becomes 30 feet, unless "
        "your walking speed is higher, and your speed isn't reduced if you are "
        "encumbered or wearing heavy armor. In addition, you can jump three "
        "times the normal distance, though you can't jump farther than your "
        "remaining movement would allow."
    ),
    requires_attunement=True,
)

BROOM_OF_FLYING = MagicItem(
    name="Broom of Flying",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "This wooden broom, which weighs 3 pounds, functions like a mundane "
        "broom until you stand astride it and speak its command word. It then "
        "hovers beneath you and can be ridden in the air. It has a flying speed "
        "of 50 feet. It can carry up to 400 pounds, but its flying speed becomes "
        "30 feet while carrying over 200 pounds. The broom stops hovering when "
        "you land. You can send the broom to travel alone to a destination "
        "within 1 mile of you if you speak the command word, name the location, "
        "and are familiar with that place."
    ),
)

CAP_OF_WATER_BREATHING = MagicItem(
    name="Cap of Water Breathing",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While wearing this cap underwater, you can speak its command word as "
        "an action to create a bubble of air around your head. It allows you to "
        "breathe normally underwater. This bubble stays with you until you speak "
        "the command word again, the cap is removed, or you are no longer "
        "underwater."
    ),
)

CIRCLET_OF_BLASTING = MagicItem(
    name="Circlet of Blasting",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While wearing this circlet, you can use an action to cast the scorching "
        "ray spell with it. When you make the spell's attacks, you do so with an "
        "attack bonus of +5. The circlet can't be used this way again until the "
        "next dawn."
    ),
)

DECANTER_OF_ENDLESS_WATER = MagicItem(
    name="Decanter of Endless Water",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "This stoppered flask sloshes when shaken, as if it contains water. The "
        "decanter weighs 2 pounds. You can use an action to remove the stopper "
        "and speak one of three command words, whereupon an amount of fresh "
        "water or salt water (your choice) pours out of the flask. The water "
        "stops pouring out at the start of your next turn. Choose from 'Stream' "
        "(1 gallon), 'Fountain' (5 gallons), or 'Geyser' (30 gallons in a 30-foot "
        "line that is 1 foot wide, knocking prone creatures that fail a DC 13 "
        "Strength saving throw)."
    ),
)

HELM_OF_TELEPATHY = MagicItem(
    name="Helm of Telepathy",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "While wearing this helm, you can use an action to cast the detect "
        "thoughts spell (save DC 13) from it. As long as you maintain "
        "concentration on the spell, you can use a bonus action to send a "
        "telepathic message to a creature you are focused on. It can reply—using "
        "a bonus action to do so—while your focus on it continues. While "
        "focusing on a creature with detect thoughts, you can use an action to "
        "cast the suggestion spell (save DC 13) from the helm on that creature. "
        "Once used, the suggestion property can't be used again until the next "
        "dawn."
    ),
    requires_attunement=True,
)

EYES_OF_MINUTE_SEEING = MagicItem(
    name="Eyes of Minute Seeing",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "These crystal lenses fit over the eyes. While wearing them, you can see "
        "much better than normal out to a range of 1 foot. You have advantage on "
        "Intelligence (Investigation) checks that rely on sight while searching "
        "an area or studying an object within that range."
    ),
)

# =============================================================================
# RARE ITEMS
# =============================================================================

WEAPON_PLUS_2 = MagicItem(
    name="Weapon, +2",
    item_type="weapon",
    rarity="rare",
    description=(
        "You have a +2 bonus to attack and damage rolls made with this magic "
        "weapon. This bonus applies to any weapon type imbued with this enchantment."
    ),
    magic_bonus=2,
)

ARMOR_PLUS_2 = MagicItem(
    name="Armor, +2",
    item_type="armor",
    rarity="rare",
    description=(
        "You have a +2 bonus to AC while wearing this armor. This enchantment "
        "can be applied to any type of armor."
    ),
    magic_bonus=2,
)

SHIELD_PLUS_2 = MagicItem(
    name="Shield, +2",
    item_type="armor",
    rarity="rare",
    description=(
        "While holding this shield, you have a +2 bonus to AC. This bonus is in "
        "addition to the shield's normal bonus to AC."
    ),
    magic_bonus=2,
)

AMULET_OF_HEALTH = MagicItem(
    name="Amulet of Health",
    item_type="wondrous",
    rarity="rare",
    description=(
        "Your Constitution score is 19 while you wear this amulet. It has no "
        "effect on you if your Constitution is already 19 or higher."
    ),
    requires_attunement=True,
)

BELT_OF_HILL_GIANT_STRENGTH = MagicItem(
    name="Belt of Hill Giant Strength",
    item_type="wondrous",
    rarity="rare",
    description=(
        "While wearing this belt, your Strength score changes to 21. The item "
        "has no effect on you if your Strength is equal to or greater than the "
        "belt's score."
    ),
    requires_attunement=True,
)

BOOTS_OF_SPEED = MagicItem(
    name="Boots of Speed",
    item_type="wondrous",
    rarity="rare",
    description=(
        "While you wear these boots, you can use a bonus action and click the "
        "boots' heels together. If you do, the boots double your walking speed, "
        "and any creature that makes an opportunity attack against you has "
        "disadvantage on the attack roll. If you click your heels together again, "
        "you end the effect. When the boots' property has been used for a total "
        "of 10 minutes, the magic ceases to function until you finish a long rest."
    ),
    requires_attunement=True,
)

BRACERS_OF_DEFENSE = MagicItem(
    name="Bracers of Defense",
    item_type="wondrous",
    rarity="rare",
    description=(
        "While wearing these bracers, you gain a +2 bonus to AC if you are "
        "wearing no armor and using no shield."
    ),
    requires_attunement=True,
    magic_bonus=2,
)

CAPE_OF_THE_MOUNTEBANK = MagicItem(
    name="Cape of the Mountebank",
    item_type="wondrous",
    rarity="rare",
    description=(
        "This cape smells faintly of brimstone. While wearing it, you can use it "
        "to cast the dimension door spell as an action. This property of the cape "
        "can't be used again until the next dawn. When you disappear, you leave "
        "behind a cloud of smoke, and you appear in a similar cloud of smoke at "
        "your destination."
    ),
)

CLOAK_OF_DISPLACEMENT = MagicItem(
    name="Cloak of Displacement",
    item_type="wondrous",
    rarity="rare",
    description=(
        "While you wear this cloak, it projects an illusion that makes you appear "
        "to be standing in a place near your actual location, causing any creature "
        "to have disadvantage on attack rolls against you. If you take damage, the "
        "property ceases to function until the start of your next turn. This "
        "property is suppressed while you are incapacitated, restrained, or "
        "otherwise unable to move."
    ),
    requires_attunement=True,
)

FLAME_TONGUE = MagicItem(
    name="Flame Tongue",
    item_type="weapon",
    rarity="rare",
    description=(
        "You can use a bonus action to speak this magic sword's command word, "
        "causing flames to erupt from the blade. These flames shed bright light "
        "in a 40-foot radius and dim light for an additional 40 feet. While the "
        "sword is ablaze, it deals an extra 2d6 fire damage to any target it hits. "
        "The flames last until you use a bonus action to speak the command word "
        "again or until you drop or sheathe the sword."
    ),
    requires_attunement=True,
)

NECKLACE_OF_FIREBALLS = MagicItem(
    name="Necklace of Fireballs",
    item_type="wondrous",
    rarity="rare",
    description=(
        "This necklace has 1d6 + 3 beads hanging from it. You can use an action "
        "to detach a bead and throw it up to 60 feet away. When it reaches the "
        "end of its trajectory, the bead detonates as a 3rd-level fireball spell "
        "(save DC 15). You can hurl multiple beads, or even the whole necklace, "
        "as one action. When you do so, increase the level of the fireball by 1 "
        "for each bead beyond the first."
    ),
)

RING_OF_PROTECTION = MagicItem(
    name="Ring of Protection",
    item_type="ring",
    rarity="rare",
    description=(
        "You gain a +1 bonus to AC and saving throws while wearing this ring."
    ),
    requires_attunement=True,
    magic_bonus=1,
)

RING_OF_RESISTANCE = MagicItem(
    name="Ring of Resistance",
    item_type="ring",
    rarity="rare",
    description=(
        "You have resistance to one damage type while wearing this ring. The gem "
        "in the ring indicates the type, which the DM chooses or determines "
        "randomly: Pearl (acid), Tourmaline (cold), Garnet (fire), Sapphire "
        "(lightning), Jet (necrotic), Amethyst (poison), Jade (psychic), Citrine "
        "(radiant), Jacinth (thunder)."
    ),
    requires_attunement=True,
)

RING_OF_SPELL_STORING = MagicItem(
    name="Ring of Spell Storing",
    item_type="ring",
    rarity="rare",
    description=(
        "This ring stores spells cast into it, holding them until the attuned "
        "wearer uses them. The ring can store up to 5 levels worth of spells at "
        "a time. When found, it contains 1d6 − 1 levels of stored spells chosen "
        "by the DM. Any creature can cast a spell of 1st through 5th level into "
        "the ring by touching the ring as the spell is cast. While wearing this "
        "ring, you can cast any spell stored in it."
    ),
    requires_attunement=True,
)

ROBE_OF_EYES = MagicItem(
    name="Robe of Eyes",
    item_type="wondrous",
    rarity="rare",
    description=(
        "This robe is adorned with eyelike patterns. While you wear the robe, "
        "you gain the following benefits: You can see in all directions, and you "
        "have advantage on Wisdom (Perception) checks that rely on sight. You "
        "have darkvision out to a range of 120 feet. You can see invisible "
        "creatures and objects, as well as see into the Ethereal Plane, out to "
        "a range of 120 feet. However, a light spell cast on the robe or a "
        "daylight spell cast within 5 feet of the robe causes you to be blinded "
        "for 1 minute."
    ),
    requires_attunement=True,
)

WAND_OF_FIREBALLS = MagicItem(
    name="Wand of Fireballs",
    item_type="wand",
    rarity="rare",
    description=(
        "This wand has 7 charges. While holding it, you can use an action to "
        "expend 1 or more of its charges to cast the fireball spell (save DC 15) "
        "from it. For 1 charge, you cast the 3rd-level version of the spell. You "
        "can increase the spell slot level by one for each additional charge you "
        "expend. The wand regains 1d6 + 1 expended charges daily at dawn. If you "
        "expend the wand's last charge, roll a d20. On a 1, the wand crumbles "
        "into ashes and is destroyed."
    ),
    requires_attunement=True,
    charges=7,
)

WAND_OF_LIGHTNING_BOLTS = MagicItem(
    name="Wand of Lightning Bolts",
    item_type="wand",
    rarity="rare",
    description=(
        "This wand has 7 charges. While holding it, you can use an action to "
        "expend 1 or more of its charges to cast the lightning bolt spell (save "
        "DC 15) from it. For 1 charge, you cast the 3rd-level version of the "
        "spell. You can increase the spell slot level by one for each additional "
        "charge you expend. The wand regains 1d6 + 1 expended charges daily at "
        "dawn. If you expend the wand's last charge, roll a d20. On a 1, the wand "
        "crumbles into ashes and is destroyed."
    ),
    requires_attunement=True,
    charges=7,
)

MANTLE_OF_SPELL_RESISTANCE = MagicItem(
    name="Mantle of Spell Resistance",
    item_type="wondrous",
    rarity="rare",
    description=(
        "You have advantage on saving throws against spells while you wear this "
        "cloak."
    ),
    requires_attunement=True,
)

# =============================================================================
# VERY RARE ITEMS
# =============================================================================

WEAPON_PLUS_3 = MagicItem(
    name="Weapon, +3",
    item_type="weapon",
    rarity="very_rare",
    description=(
        "You have a +3 bonus to attack and damage rolls made with this magic "
        "weapon. This bonus applies to any weapon type imbued with this enchantment."
    ),
    magic_bonus=3,
)

ARMOR_PLUS_3 = MagicItem(
    name="Armor, +3",
    item_type="armor",
    rarity="very_rare",
    description=(
        "You have a +3 bonus to AC while wearing this armor. This enchantment "
        "can be applied to any type of armor."
    ),
    magic_bonus=3,
)

SHIELD_PLUS_3 = MagicItem(
    name="Shield, +3",
    item_type="armor",
    rarity="very_rare",
    description=(
        "While holding this shield, you have a +3 bonus to AC. This bonus is in "
        "addition to the shield's normal bonus to AC."
    ),
    magic_bonus=3,
)

BELT_OF_FIRE_GIANT_STRENGTH = MagicItem(
    name="Belt of Fire Giant Strength",
    item_type="wondrous",
    rarity="very_rare",
    description=(
        "While wearing this belt, your Strength score changes to 25. The item "
        "has no effect on you if your Strength is equal to or greater than the "
        "belt's score."
    ),
    requires_attunement=True,
)

CLOAK_OF_INVISIBILITY = MagicItem(
    name="Cloak of Invisibility",
    item_type="wondrous",
    rarity="very_rare",
    description=(
        "While wearing this cloak, you can pull its hood over your head to cause "
        "yourself to become invisible. While you are invisible, anything you are "
        "carrying or wearing is invisible with you. You become visible when you "
        "cease wearing the hood. Pulling the hood up or down requires an action. "
        "Deduct the time you are invisible, in increments of 1 minute, from the "
        "cloak's maximum duration of 2 hours. After 2 hours of use, the cloak "
        "ceases to function. For every uninterrupted period of 12 hours the cloak "
        "goes unused, it regains 1 hour of duration."
    ),
    requires_attunement=True,
)

DANCING_SWORD = MagicItem(
    name="Dancing Sword",
    item_type="weapon",
    rarity="very_rare",
    description=(
        "You can use a bonus action to toss this magic sword into the air and "
        "speak the command word. When you do so, the sword begins to hover, "
        "flies up to 30 feet, and attacks one creature of your choice within 5 "
        "feet of it. The sword uses your attack roll and ability score modifier "
        "to damage rolls. While the sword hovers, you can use a bonus action to "
        "cause it to fly up to 30 feet to another spot within 30 feet of you. "
        "After the hovering sword attacks for the fourth time, it flies up to 30 "
        "feet and tries to return to your hand."
    ),
    requires_attunement=True,
)

MANUAL_OF_BODILY_HEALTH = MagicItem(
    name="Manual of Bodily Health",
    item_type="wondrous",
    rarity="very_rare",
    description=(
        "This book contains health and diet tips, and its words are charged with "
        "magic. If you spend 48 hours over a period of 6 days or fewer studying "
        "the book's contents and practicing its guidelines, your Constitution "
        "score increases by 2, as does your maximum for that score. The manual "
        "then loses its magic, but regains it in a century."
    ),
)

MANUAL_OF_GAINFUL_EXERCISE = MagicItem(
    name="Manual of Gainful Exercise",
    item_type="wondrous",
    rarity="very_rare",
    description=(
        "This book describes fitness exercises, and its words are charged with "
        "magic. If you spend 48 hours over a period of 6 days or fewer studying "
        "the book's contents and practicing its guidelines, your Strength score "
        "increases by 2, as does your maximum for that score. The manual then "
        "loses its magic, but regains it in a century."
    ),
)

ROD_OF_ABSORPTION = MagicItem(
    name="Rod of Absorption",
    item_type="rod",
    rarity="very_rare",
    description=(
        "While holding this rod, you can use your reaction to absorb a spell "
        "that is targeting only you and not with an area of effect. The absorbed "
        "spell's effect is canceled, and the spell's energy—not the spell "
        "itself—is stored in the rod. The energy has the same level as the spell "
        "when it was cast. The rod can absorb and store up to 50 levels of "
        "energy over the course of its existence. You can use the stored energy "
        "to fuel spells you cast as a bonus action."
    ),
    requires_attunement=True,
)

STAFF_OF_FIRE = MagicItem(
    name="Staff of Fire",
    item_type="staff",
    rarity="very_rare",
    description=(
        "You have resistance to fire damage while you hold this staff. The staff "
        "has 10 charges. While holding it, you can use an action to expend 1 or "
        "more of its charges to cast one of the following spells from it, using "
        "your spell save DC: burning hands (1 charge), fireball (3 charges), or "
        "wall of fire (4 charges). The staff regains 1d6 + 4 expended charges "
        "daily at dawn. If you expend the last charge, roll a d20. On a 1, the "
        "staff blackens, crumbles into cinders, and is destroyed."
    ),
    requires_attunement=True,
    attunement_requirements="druid, sorcerer, warlock, or wizard",
    charges=10,
)

STAFF_OF_FROST = MagicItem(
    name="Staff of Frost",
    item_type="staff",
    rarity="very_rare",
    description=(
        "You have resistance to cold damage while you hold this staff. The staff "
        "has 10 charges. While holding it, you can use an action to expend 1 or "
        "more of its charges to cast one of the following spells from it, using "
        "your spell save DC: cone of cold (5 charges), fog cloud (1 charge), ice "
        "storm (4 charges), or wall of ice (4 charges). The staff regains 1d6 + "
        "4 expended charges daily at dawn. If you expend the last charge, roll a "
        "d20. On a 1, the staff turns to water and is destroyed."
    ),
    requires_attunement=True,
    attunement_requirements="druid, sorcerer, warlock, or wizard",
    charges=10,
)

STAFF_OF_POWER = MagicItem(
    name="Staff of Power",
    item_type="staff",
    rarity="very_rare",
    description=(
        "This staff can be wielded as a magic quarterstaff that grants a +2 bonus "
        "to attack and damage rolls made with it. While holding it, you gain a +2 "
        "bonus to Armor Class, saving throws, and spell attack rolls. The staff "
        "has 20 charges for the following properties. It regains 2d8 + 4 expended "
        "charges daily at dawn. If you expend the last charge, roll a d20. On a "
        "20, the staff regains 1d8 + 2 charges. On a 1, the staff retains its +2 "
        "bonus to attack and damage rolls but loses all other properties."
    ),
    requires_attunement=True,
    attunement_requirements="sorcerer, warlock, or wizard",
    magic_bonus=2,
    charges=20,
)

RING_OF_REGENERATION = MagicItem(
    name="Ring of Regeneration",
    item_type="ring",
    rarity="very_rare",
    description=(
        "While wearing this ring, you regain 1d6 hit points every 10 minutes, "
        "provided that you have at least 1 hit point. If you lose a body part, "
        "the ring causes the missing part to regrow and return to full "
        "functionality after 1d6 + 1 days if you have at least 1 hit point the "
        "whole time."
    ),
    requires_attunement=True,
)

TOME_OF_CLEAR_THOUGHT = MagicItem(
    name="Tome of Clear Thought",
    item_type="wondrous",
    rarity="very_rare",
    description=(
        "This book contains memory and logic exercises, and its words are charged "
        "with magic. If you spend 48 hours over a period of 6 days or fewer "
        "studying the book's contents and practicing its guidelines, your "
        "Intelligence score increases by 2, as does your maximum for that score. "
        "The manual then loses its magic, but regains it in a century."
    ),
)

# =============================================================================
# LEGENDARY ITEMS
# =============================================================================

HOLY_AVENGER = MagicItem(
    name="Holy Avenger",
    item_type="weapon",
    rarity="legendary",
    description=(
        "You gain a +3 bonus to attack and damage rolls made with this magic "
        "weapon. When you hit a fiend or an undead with it, that creature takes "
        "an extra 2d10 radiant damage. While you hold the drawn sword, it creates "
        "an aura in a 10-foot radius around you. You and all creatures friendly "
        "to you in the aura have advantage on saving throws against spells and "
        "other magical effects. If you have 17 or more levels in the paladin "
        "class, the radius of the aura increases to 30 feet."
    ),
    requires_attunement=True,
    attunement_requirements="paladin",
    magic_bonus=3,
)

LUCK_BLADE = MagicItem(
    name="Luck Blade",
    item_type="weapon",
    rarity="legendary",
    description=(
        "You gain a +1 bonus to attack and damage rolls made with this magic "
        "weapon. While the sword is on your person, you also gain a +1 bonus to "
        "saving throws. Luck: If the sword is on your person, you can call on its "
        "luck (no action required) to reroll one attack roll, ability check, or "
        "saving throw you dislike. You must use the second roll. This property "
        "can't be used again until the next dawn. Wish: The sword has 1d4 − 1 "
        "charges. While holding it, you can use an action to expend 1 charge and "
        "cast the wish spell from it. This property can't be used again until "
        "the next dawn."
    ),
    requires_attunement=True,
    magic_bonus=1,
)

RING_OF_THREE_WISHES = MagicItem(
    name="Ring of Three Wishes",
    item_type="ring",
    rarity="legendary",
    description=(
        "While wearing this ring, you can use an action to expend 1 of its 3 "
        "charges to cast the wish spell from it. The ring becomes nonmagical "
        "when you use the last charge."
    ),
    charges=3,
)

ROD_OF_LORDLY_MIGHT = MagicItem(
    name="Rod of Lordly Might",
    item_type="rod",
    rarity="legendary",
    description=(
        "This rod has a flanged head, and it functions as a magic mace that "
        "grants a +3 bonus to attack and damage rolls made with it. The rod has "
        "properties associated with six different buttons that are set in a row "
        "along the haft. It has three other properties as well, including the "
        "ability to transform into various weapons, extend up to 50 feet, drain "
        "life from enemies, and terrify foes with a command word."
    ),
    requires_attunement=True,
    magic_bonus=3,
)

STAFF_OF_THE_MAGI = MagicItem(
    name="Staff of the Magi",
    item_type="staff",
    rarity="legendary",
    description=(
        "This staff can be wielded as a magic quarterstaff that grants a +2 bonus "
        "to attack and damage rolls made with it. While you hold it, you gain a "
        "+2 bonus to spell attack rolls. The staff has 50 charges for the "
        "following properties. It regains 4d6 + 2 expended charges daily at dawn. "
        "If you expend the last charge, roll a d20. On a 20, the staff regains "
        "1d12 + 1 charges. On a 1, the staff retains its +2 bonus to attack and "
        "damage rolls but loses all other properties."
    ),
    requires_attunement=True,
    attunement_requirements="sorcerer, warlock, or wizard",
    magic_bonus=2,
    charges=50,
)

VORPAL_SWORD = MagicItem(
    name="Vorpal Sword",
    item_type="weapon",
    rarity="legendary",
    description=(
        "You gain a +3 bonus to attack and damage rolls made with this magic "
        "weapon. In addition, the weapon ignores resistance to slashing damage. "
        "When you attack a creature that has at least one head with this weapon "
        "and roll a 20 on the attack roll, you cut off one of the creature's "
        "heads. The creature dies if it can't survive without the lost head. A "
        "creature is immune to this effect if it is immune to slashing damage, "
        "doesn't have or need a head, has legendary actions, or the DM decides "
        "that the creature is too big for its head to be cut off with this weapon."
    ),
    requires_attunement=True,
    magic_bonus=3,
)

ARMOR_OF_INVULNERABILITY = MagicItem(
    name="Armor of Invulnerability",
    item_type="armor",
    rarity="legendary",
    description=(
        "You have resistance to nonmagical damage while you wear this armor. "
        "Additionally, you can use an action to make yourself immune to "
        "nonmagical damage for 10 minutes or until you are no longer wearing the "
        "armor. Once this special action is used, it can't be used again until "
        "the next dawn."
    ),
    requires_attunement=True,
)

BELT_OF_STORM_GIANT_STRENGTH = MagicItem(
    name="Belt of Storm Giant Strength",
    item_type="wondrous",
    rarity="legendary",
    description=(
        "While wearing this belt, your Strength score changes to 29. The item "
        "has no effect on you if your Strength is equal to or greater than the "
        "belt's score."
    ),
    requires_attunement=True,
)

CLOAK_OF_ARACHNIDA = MagicItem(
    name="Cloak of Arachnida",
    item_type="wondrous",
    rarity="very_rare",
    description=(
        "This fine garment is made of black silk interwoven with faint silvery "
        "threads. While wearing it, you gain the following benefits: You have "
        "resistance to poison damage. You have a climbing speed equal to your "
        "walking speed. You can move up, down, and across vertical surfaces and "
        "upside down along ceilings, while leaving your hands free. You can't be "
        "caught in webs of any sort and can move through webs as if they were "
        "difficult terrain. You can use an action to cast the web spell (save DC "
        "13). The web created by the spell fills twice its normal area. Once "
        "used, this property of the cloak can't be used again until the next dawn."
    ),
    requires_attunement=True,
)

IOUN_STONE_MASTERY = MagicItem(
    name="Ioun Stone (Mastery)",
    item_type="wondrous",
    rarity="legendary",
    description=(
        "An Ioun stone is named after Ioun, a god of knowledge and prophecy "
        "revered on some worlds. This pale green prism Ioun stone orbits your "
        "head while attuned, granting you proficiency in all skills. If you "
        "already have proficiency in a skill, you gain expertise in that skill, "
        "doubling your proficiency bonus for ability checks using that skill."
    ),
    requires_attunement=True,
)


# =============================================================================
# TALES OF THE VALIANT MAGIC ITEMS
# =============================================================================

# ToV introduces some unique magic items with distinct flavor

TOV_AMULET_OF_LUCK = MagicItem(
    name="Amulet of Luck",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "This small silver charm is shaped like a four-leaf clover. While wearing "
        "this amulet, you can use your Luck feature one additional time before "
        "needing to take a long rest. If you don't have the Luck feature, you "
        "instead gain 1 luck point that you can use as described in the Lucky "
        "talent. Once you use this luck point, it is expended until you finish "
        "a long rest."
    ),
    requires_attunement=True,
    ruleset="tov",
)

TOV_BLADE_OF_THE_IRON_LEGION = MagicItem(
    name="Blade of the Iron Legion",
    item_type="weapon",
    rarity="rare",
    description=(
        "This longsword has a blade of dark iron etched with martial sigils. You "
        "gain a +1 bonus to attack and damage rolls made with this magic weapon. "
        "When you hit a creature with this weapon while you have no allies within "
        "30 feet of you, the attack deals an extra 1d6 damage. Additionally, while "
        "attuned to this weapon, you cannot be frightened."
    ),
    requires_attunement=True,
    magic_bonus=1,
    ruleset="tov",
)

TOV_CIRCLET_OF_MENTAL_FORTITUDE = MagicItem(
    name="Circlet of Mental Fortitude",
    item_type="wondrous",
    rarity="uncommon",
    description=(
        "This slender circlet of woven silver threads rests upon your brow. While "
        "wearing this circlet, you have advantage on saving throws against being "
        "charmed or having your thoughts read. Additionally, you can use an action "
        "to cast the calm emotions spell (save DC 13). Once used, this property "
        "can't be used again until the next dawn."
    ),
    requires_attunement=True,
    ruleset="tov",
)

TOV_CLOAK_OF_THE_WILDS = MagicItem(
    name="Cloak of the Wilds",
    item_type="wondrous",
    rarity="rare",
    description=(
        "This cloak appears to be woven from living vines and leaves that shift "
        "with the seasons. While wearing this cloak in natural environments, you "
        "have advantage on Dexterity (Stealth) checks. Additionally, you can use "
        "an action to cast pass without trace. Once you use this property, you "
        "can't use it again until you finish a short or long rest."
    ),
    requires_attunement=True,
    ruleset="tov",
)

TOV_DUELING_DAGGER = MagicItem(
    name="Dueling Dagger",
    item_type="weapon",
    rarity="uncommon",
    description=(
        "This elegant dagger has a blade that gleams with arcane runes. You gain "
        "a +1 bonus to attack and damage rolls made with this magic weapon. When "
        "you make an attack with this dagger against a creature that has attacked "
        "you since the start of your last turn, you deal an extra 1d4 damage on "
        "a hit."
    ),
    magic_bonus=1,
    ruleset="tov",
)

TOV_GAUNTLETS_OF_THE_BATTLE_MASTER = MagicItem(
    name="Gauntlets of the Battle Master",
    item_type="wondrous",
    rarity="rare",
    description=(
        "These steel gauntlets are etched with images of warriors locked in combat. "
        "While wearing these gauntlets, you learn two maneuvers of your choice from "
        "those available to the Battle Master archetype. You gain 2 superiority dice "
        "(d8s) for use with these maneuvers. You regain all expended superiority "
        "dice when you finish a short or long rest."
    ),
    requires_attunement=True,
    ruleset="tov",
)

TOV_STAFF_OF_THE_WILD_HEART = MagicItem(
    name="Staff of the Wild Heart",
    item_type="staff",
    rarity="rare",
    description=(
        "This gnarled staff is made from the heartwood of an ancient treant. While "
        "holding this staff, you can use an action to expend 1 of its 10 charges "
        "to cast one of the following spells (save DC 15): speak with animals (1 "
        "charge), animal messenger (2 charges), conjure animals (3 charges). The "
        "staff regains 1d6 + 4 expended charges daily at dawn."
    ),
    requires_attunement=True,
    attunement_requirements="druid or ranger",
    charges=10,
    ruleset="tov",
)

TOV_RING_OF_SPELL_STORING = MagicItem(
    name="Ring of Spell Storing (ToV)",
    item_type="ring",
    rarity="rare",
    description=(
        "This ring stores spells cast into it, holding them until the attuned "
        "wearer uses them. The ring can store up to 5 levels worth of spells at "
        "a time. When found, it contains 1d6 − 1 levels of stored spells chosen "
        "by the GM. Any creature can cast a spell into the ring by touching the "
        "ring as the spell is cast. The wearer can cast any stored spell using "
        "the original caster's spell save DC and spell attack bonus."
    ),
    requires_attunement=True,
    ruleset="tov",
)

TOV_VANGUARD_SHIELD = MagicItem(
    name="Vanguard Shield",
    item_type="armor",
    rarity="uncommon",
    description=(
        "This sturdy shield bears the emblem of a charging knight. While holding "
        "this shield, you have advantage on initiative rolls. Additionally, when "
        "a creature you can see attacks a target other than you that is within "
        "5 feet of you, you can use your reaction to become the target of the "
        "attack instead."
    ),
    requires_attunement=True,
    ruleset="tov",
)

TOV_WYRMSLAYER_AXE = MagicItem(
    name="Wyrmslayer Axe",
    item_type="weapon",
    rarity="rare",
    description=(
        "This battleaxe is forged from dragon bone and etched with draconic runes "
        "of binding. You gain a +1 bonus to attack and damage rolls made with "
        "this magic weapon. When you hit a dragon with this weapon, the dragon "
        "takes an extra 2d6 damage. For the purpose of this weapon, 'dragon' refers "
        "to any creature with the dragon type."
    ),
    requires_attunement=True,
    magic_bonus=1,
    ruleset="tov",
)

# ToV Collections
TOV_MAGIC_ITEMS: list[MagicItem] = [
    TOV_AMULET_OF_LUCK,
    TOV_BLADE_OF_THE_IRON_LEGION,
    TOV_CIRCLET_OF_MENTAL_FORTITUDE,
    TOV_CLOAK_OF_THE_WILDS,
    TOV_DUELING_DAGGER,
    TOV_GAUNTLETS_OF_THE_BATTLE_MASTER,
    TOV_STAFF_OF_THE_WILD_HEART,
    TOV_RING_OF_SPELL_STORING,
    TOV_VANGUARD_SHIELD,
    TOV_WYRMSLAYER_AXE,
]


# =============================================================================
# COLLECTIONS
# =============================================================================

COMMON_ITEMS: list[MagicItem] = [
    POTION_OF_HEALING,
    SPELL_SCROLL_CANTRIP,
    SPELL_SCROLL_1ST,
    POTION_OF_CLIMBING,
    DRIFTGLOBE,
    HAT_OF_WIZARDRY,
    TANKARD_OF_SOBRIETY,
    CLOCKWORK_AMULET,
    MOON_TOUCHED_SWORD,
    RUBY_OF_THE_WAR_MAGE,
]

UNCOMMON_ITEMS: list[MagicItem] = [
    WEAPON_PLUS_1,
    ARMOR_PLUS_1,
    SHIELD_PLUS_1,
    BAG_OF_HOLDING,
    BOOTS_OF_ELVENKIND,
    CLOAK_OF_ELVENKIND,
    CLOAK_OF_PROTECTION,
    GAUNTLETS_OF_OGRE_POWER,
    GLOVES_OF_THIEVERY,
    GOGGLES_OF_NIGHT,
    HEADBAND_OF_INTELLECT,
    LANTERN_OF_REVEALING,
    PEARL_OF_POWER,
    RING_OF_JUMPING,
    RING_OF_WATER_WALKING,
    ROPE_OF_CLIMBING,
    SLIPPERS_OF_SPIDER_CLIMBING,
    WAND_OF_MAGIC_MISSILES,
    WINGED_BOOTS,
    IMMOVABLE_ROD,
    BOOTS_OF_STRIDING_AND_SPRINGING,
    BROOM_OF_FLYING,
    CAP_OF_WATER_BREATHING,
    CIRCLET_OF_BLASTING,
    DECANTER_OF_ENDLESS_WATER,
    HELM_OF_TELEPATHY,
    EYES_OF_MINUTE_SEEING,
]

RARE_ITEMS: list[MagicItem] = [
    WEAPON_PLUS_2,
    ARMOR_PLUS_2,
    SHIELD_PLUS_2,
    AMULET_OF_HEALTH,
    BELT_OF_HILL_GIANT_STRENGTH,
    BOOTS_OF_SPEED,
    BRACERS_OF_DEFENSE,
    CAPE_OF_THE_MOUNTEBANK,
    CLOAK_OF_DISPLACEMENT,
    FLAME_TONGUE,
    NECKLACE_OF_FIREBALLS,
    RING_OF_PROTECTION,
    RING_OF_RESISTANCE,
    RING_OF_SPELL_STORING,
    ROBE_OF_EYES,
    WAND_OF_FIREBALLS,
    WAND_OF_LIGHTNING_BOLTS,
    MANTLE_OF_SPELL_RESISTANCE,
]

VERY_RARE_ITEMS: list[MagicItem] = [
    WEAPON_PLUS_3,
    ARMOR_PLUS_3,
    SHIELD_PLUS_3,
    BELT_OF_FIRE_GIANT_STRENGTH,
    CLOAK_OF_INVISIBILITY,
    DANCING_SWORD,
    MANUAL_OF_BODILY_HEALTH,
    MANUAL_OF_GAINFUL_EXERCISE,
    ROD_OF_ABSORPTION,
    STAFF_OF_FIRE,
    STAFF_OF_FROST,
    STAFF_OF_POWER,
    RING_OF_REGENERATION,
    TOME_OF_CLEAR_THOUGHT,
    CLOAK_OF_ARACHNIDA,
]

LEGENDARY_ITEMS: list[MagicItem] = [
    HOLY_AVENGER,
    LUCK_BLADE,
    RING_OF_THREE_WISHES,
    ROD_OF_LORDLY_MIGHT,
    STAFF_OF_THE_MAGI,
    VORPAL_SWORD,
    ARMOR_OF_INVULNERABILITY,
    BELT_OF_STORM_GIANT_STRENGTH,
    IOUN_STONE_MASTERY,
]

# D&D Magic Items (all rulesets except ToV-specific)
DND_MAGIC_ITEMS: list[MagicItem] = (
    COMMON_ITEMS + UNCOMMON_ITEMS + RARE_ITEMS + VERY_RARE_ITEMS + LEGENDARY_ITEMS
)

ALL_MAGIC_ITEMS: list[MagicItem] = DND_MAGIC_ITEMS + TOV_MAGIC_ITEMS

# Dictionary for quick lookup
_ITEMS_BY_NAME: dict[str, MagicItem] = {
    item.name.lower(): item for item in ALL_MAGIC_ITEMS
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_magic_item(name: str) -> Optional[MagicItem]:
    """Get a magic item by name (case-insensitive)."""
    return _ITEMS_BY_NAME.get(name.lower())


def get_magic_items_by_rarity(rarity: str) -> list[MagicItem]:
    """Get all magic items of a specific rarity.

    Args:
        rarity: Rarity name (e.g., "common", "very rare", "very_rare")
                Spaces and underscores are normalized.
    """
    # Normalize: lowercase and convert spaces to underscores
    rarity_normalized = rarity.lower().replace(" ", "_")
    return [item for item in ALL_MAGIC_ITEMS if item.rarity == rarity_normalized]


def get_magic_items_by_type(item_type: str) -> list[MagicItem]:
    """Get all magic items of a specific type."""
    type_lower = item_type.lower()
    return [item for item in ALL_MAGIC_ITEMS if item.item_type == type_lower]


def get_attunement_items() -> list[MagicItem]:
    """Get all magic items that require attunement."""
    return [item for item in ALL_MAGIC_ITEMS if item.requires_attunement]


def get_items_with_charges() -> list[MagicItem]:
    """Get all magic items that have charges."""
    return [item for item in ALL_MAGIC_ITEMS if item.charges]


def search_magic_items(query: str) -> list[MagicItem]:
    """Search magic items by name or description."""
    query_lower = query.lower()
    results = []
    for item in ALL_MAGIC_ITEMS:
        if query_lower in item.name.lower() or query_lower in item.description.lower():
            results.append(item)
    return results


def get_all_magic_item_names() -> list[str]:
    """Get a list of all magic item names."""
    return [item.name for item in ALL_MAGIC_ITEMS]


def get_magic_items_for_ruleset(ruleset: Optional[str] = None) -> list[MagicItem]:
    """Get magic items appropriate for a specific ruleset.

    Args:
        ruleset: The ruleset ID ('dnd2014', 'dnd2024', 'tov', or None for all)

    Returns:
        List of magic items available for the ruleset. ToV returns only ToV items,
        D&D rulesets return only D&D items, None returns all.
    """
    if ruleset is None:
        return ALL_MAGIC_ITEMS.copy()
    elif ruleset == "tov":
        return TOV_MAGIC_ITEMS.copy()
    else:
        # D&D 2014 or 2024 - return D&D items
        return DND_MAGIC_ITEMS.copy()


def get_tov_magic_items() -> list[MagicItem]:
    """Get all Tales of the Valiant magic items."""
    return TOV_MAGIC_ITEMS.copy()


# =============================================================================
# MAGIC ITEM PREREQUISITE VALIDATION
# =============================================================================

def _parse_attunement_requirements(requirements: str) -> Optional["Prerequisite"]:
    """Parse attunement requirements string into a structured Prerequisite.

    Handles common patterns like:
    - "wizard" -> ClassRequirement for Wizard
    - "spellcaster" -> SpellcastingRequirement
    - "druid, sorcerer, warlock, or wizard" -> ClassRequirement with multiple classes
    - "paladin" -> ClassRequirement for Paladin

    Returns None if the requirements can't be parsed.
    """
    from dnd_manager.data.prerequisites import (
        Prerequisite,
        ClassRequirement,
        SpellcastingRequirement,
    )

    if not requirements:
        return None

    req_lower = requirements.lower().strip()

    # Check for spellcaster
    if req_lower == "spellcaster":
        return Prerequisite(
            spellcasting=SpellcastingRequirement(requires_spellcasting=True),
            description=requirements
        )

    # Check for class list patterns
    # Common patterns: "druid, sorcerer, warlock, or wizard"
    #                  "sorcerer, warlock, or wizard"
    #                  "paladin"

    # List of all class names to check
    all_classes = [
        "barbarian", "bard", "cleric", "druid", "fighter", "monk",
        "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"
    ]

    # Find all mentioned classes
    found_classes = []
    for cls in all_classes:
        if cls in req_lower:
            found_classes.append(cls.title())

    if found_classes:
        return Prerequisite(
            class_req=ClassRequirement(found_classes),
            description=requirements
        )

    return None


def get_item_prerequisite(item: MagicItem) -> Optional["Prerequisite"]:
    """Get the structured prerequisite for a magic item.

    If the item has a structured_prereq set, return that.
    Otherwise, attempt to parse the attunement_requirements string.
    """
    if item.structured_prereq:
        return item.structured_prereq
    if item.attunement_requirements:
        return _parse_attunement_requirements(item.attunement_requirements)
    return None


def check_item_requirements(item: MagicItem, character) -> tuple[bool, list[str]]:
    """Check if a character meets a magic item's requirements.

    Checks both:
    - Minimum character level (based on rarity or explicit min_level)
    - Attunement requirements (if any)

    Args:
        item: The magic item to check
        character: The Character object to check against

    Returns:
        Tuple of (all_met, list_of_failure_reasons)
    """
    failures = []

    # Check minimum level
    min_level = item.get_min_level()
    if character.level < min_level:
        failures.append(
            f"Requires character level {min_level}+ (you are level {character.level})"
        )

    # Check attunement requirements
    if item.requires_attunement:
        prereq = get_item_prerequisite(item)
        if prereq:
            met, reasons = prereq.check(character)
            if not met:
                failures.extend(reasons)

    return len(failures) == 0, failures


def get_items_for_level(level: int, ruleset: Optional[str] = None) -> list[MagicItem]:
    """Get magic items appropriate for a character of the given level.

    Returns items where the minimum level requirement is met.
    """
    items = get_magic_items_for_ruleset(ruleset)
    return [item for item in items if item.get_min_level() <= level]
