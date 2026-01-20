"""SRD equipment and item data for D&D 5e.

This module contains equipment from the System Reference Document (SRD)
which is available under the Open Gaming License.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ItemCategory(Enum):
    """Equipment categories."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ADVENTURING_GEAR = "adventuring_gear"
    TOOL = "tool"
    MOUNT = "mount"
    VEHICLE = "vehicle"


class WeaponProperty(Enum):
    """Weapon properties."""
    AMMUNITION = "Ammunition"
    FINESSE = "Finesse"
    HEAVY = "Heavy"
    LIGHT = "Light"
    LOADING = "Loading"
    RANGE = "Range"
    REACH = "Reach"
    SPECIAL = "Special"
    THROWN = "Thrown"
    TWO_HANDED = "Two-Handed"
    VERSATILE = "Versatile"


class ArmorType(Enum):
    """Armor types."""
    LIGHT = "Light"
    MEDIUM = "Medium"
    HEAVY = "Heavy"
    SHIELD = "Shield"


@dataclass
class Weapon:
    """A weapon definition."""
    name: str
    category: str  # Simple or Martial
    damage: str
    damage_type: str
    weight: float  # pounds
    cost: str
    properties: list[str]
    range_normal: Optional[int] = None
    range_long: Optional[int] = None


@dataclass
class Armor:
    """An armor definition."""
    name: str
    armor_type: ArmorType
    base_ac: int
    max_dex_bonus: Optional[int]  # None = no limit
    strength_required: Optional[int]
    stealth_disadvantage: bool
    weight: float
    cost: str


@dataclass
class Equipment:
    """Generic equipment/gear item."""
    name: str
    category: str
    cost: str
    weight: float
    description: str = ""


# SRD Simple Weapons
SIMPLE_MELEE_WEAPONS = [
    Weapon("Club", "Simple Melee", "1d4", "bludgeoning", 2, "1 sp", ["Light"]),
    Weapon("Dagger", "Simple Melee", "1d4", "piercing", 1, "2 gp",
           ["Finesse", "Light", "Thrown"], range_normal=20, range_long=60),
    Weapon("Greatclub", "Simple Melee", "1d8", "bludgeoning", 10, "2 sp", ["Two-Handed"]),
    Weapon("Handaxe", "Simple Melee", "1d6", "slashing", 2, "5 gp",
           ["Light", "Thrown"], range_normal=20, range_long=60),
    Weapon("Javelin", "Simple Melee", "1d6", "piercing", 2, "5 sp",
           ["Thrown"], range_normal=30, range_long=120),
    Weapon("Light Hammer", "Simple Melee", "1d4", "bludgeoning", 2, "2 gp",
           ["Light", "Thrown"], range_normal=20, range_long=60),
    Weapon("Mace", "Simple Melee", "1d6", "bludgeoning", 4, "5 gp", []),
    Weapon("Quarterstaff", "Simple Melee", "1d6", "bludgeoning", 4, "2 sp", ["Versatile"]),
    Weapon("Sickle", "Simple Melee", "1d4", "slashing", 2, "1 gp", ["Light"]),
    Weapon("Spear", "Simple Melee", "1d6", "piercing", 3, "1 gp",
           ["Thrown", "Versatile"], range_normal=20, range_long=60),
]

SIMPLE_RANGED_WEAPONS = [
    Weapon("Light Crossbow", "Simple Ranged", "1d8", "piercing", 5, "25 gp",
           ["Ammunition", "Loading", "Two-Handed"], range_normal=80, range_long=320),
    Weapon("Dart", "Simple Ranged", "1d4", "piercing", 0.25, "5 cp",
           ["Finesse", "Thrown"], range_normal=20, range_long=60),
    Weapon("Shortbow", "Simple Ranged", "1d6", "piercing", 2, "25 gp",
           ["Ammunition", "Two-Handed"], range_normal=80, range_long=320),
    Weapon("Sling", "Simple Ranged", "1d4", "bludgeoning", 0, "1 sp",
           ["Ammunition"], range_normal=30, range_long=120),
]

# SRD Martial Weapons
MARTIAL_MELEE_WEAPONS = [
    Weapon("Battleaxe", "Martial Melee", "1d8", "slashing", 4, "10 gp", ["Versatile"]),
    Weapon("Flail", "Martial Melee", "1d8", "bludgeoning", 2, "10 gp", []),
    Weapon("Glaive", "Martial Melee", "1d10", "slashing", 6, "20 gp",
           ["Heavy", "Reach", "Two-Handed"]),
    Weapon("Greataxe", "Martial Melee", "1d12", "slashing", 7, "30 gp",
           ["Heavy", "Two-Handed"]),
    Weapon("Greatsword", "Martial Melee", "2d6", "slashing", 6, "50 gp",
           ["Heavy", "Two-Handed"]),
    Weapon("Halberd", "Martial Melee", "1d10", "slashing", 6, "20 gp",
           ["Heavy", "Reach", "Two-Handed"]),
    Weapon("Lance", "Martial Melee", "1d12", "piercing", 6, "10 gp",
           ["Reach", "Special"]),
    Weapon("Longsword", "Martial Melee", "1d8", "slashing", 3, "15 gp", ["Versatile"]),
    Weapon("Maul", "Martial Melee", "2d6", "bludgeoning", 10, "10 gp",
           ["Heavy", "Two-Handed"]),
    Weapon("Morningstar", "Martial Melee", "1d8", "piercing", 4, "15 gp", []),
    Weapon("Pike", "Martial Melee", "1d10", "piercing", 18, "5 gp",
           ["Heavy", "Reach", "Two-Handed"]),
    Weapon("Rapier", "Martial Melee", "1d8", "piercing", 2, "25 gp", ["Finesse"]),
    Weapon("Scimitar", "Martial Melee", "1d6", "slashing", 3, "25 gp",
           ["Finesse", "Light"]),
    Weapon("Shortsword", "Martial Melee", "1d6", "piercing", 2, "10 gp",
           ["Finesse", "Light"]),
    Weapon("Trident", "Martial Melee", "1d6", "piercing", 4, "5 gp",
           ["Thrown", "Versatile"], range_normal=20, range_long=60),
    Weapon("War Pick", "Martial Melee", "1d8", "piercing", 2, "5 gp", []),
    Weapon("Warhammer", "Martial Melee", "1d8", "bludgeoning", 2, "15 gp", ["Versatile"]),
    Weapon("Whip", "Martial Melee", "1d4", "slashing", 3, "2 gp",
           ["Finesse", "Reach"]),
]

MARTIAL_RANGED_WEAPONS = [
    Weapon("Blowgun", "Martial Ranged", "1", "piercing", 1, "10 gp",
           ["Ammunition", "Loading"], range_normal=25, range_long=100),
    Weapon("Hand Crossbow", "Martial Ranged", "1d6", "piercing", 3, "75 gp",
           ["Ammunition", "Light", "Loading"], range_normal=30, range_long=120),
    Weapon("Heavy Crossbow", "Martial Ranged", "1d10", "piercing", 18, "50 gp",
           ["Ammunition", "Heavy", "Loading", "Two-Handed"], range_normal=100, range_long=400),
    Weapon("Longbow", "Martial Ranged", "1d8", "piercing", 2, "50 gp",
           ["Ammunition", "Heavy", "Two-Handed"], range_normal=150, range_long=600),
    Weapon("Net", "Martial Ranged", "0", "none", 3, "1 gp",
           ["Special", "Thrown"], range_normal=5, range_long=15),
]

ALL_WEAPONS = (SIMPLE_MELEE_WEAPONS + SIMPLE_RANGED_WEAPONS +
               MARTIAL_MELEE_WEAPONS + MARTIAL_RANGED_WEAPONS)

# SRD Armor
ARMOR = [
    # Light Armor
    Armor("Padded", ArmorType.LIGHT, 11, None, None, True, 8, "5 gp"),
    Armor("Leather", ArmorType.LIGHT, 11, None, None, False, 10, "10 gp"),
    Armor("Studded Leather", ArmorType.LIGHT, 12, None, None, False, 13, "45 gp"),

    # Medium Armor
    Armor("Hide", ArmorType.MEDIUM, 12, 2, None, False, 12, "10 gp"),
    Armor("Chain Shirt", ArmorType.MEDIUM, 13, 2, None, False, 20, "50 gp"),
    Armor("Scale Mail", ArmorType.MEDIUM, 14, 2, None, True, 45, "50 gp"),
    Armor("Breastplate", ArmorType.MEDIUM, 14, 2, None, False, 20, "400 gp"),
    Armor("Half Plate", ArmorType.MEDIUM, 15, 2, None, True, 40, "750 gp"),

    # Heavy Armor
    Armor("Ring Mail", ArmorType.HEAVY, 14, 0, None, True, 40, "30 gp"),
    Armor("Chain Mail", ArmorType.HEAVY, 16, 0, 13, True, 55, "75 gp"),
    Armor("Splint", ArmorType.HEAVY, 17, 0, 15, True, 60, "200 gp"),
    Armor("Plate", ArmorType.HEAVY, 18, 0, 15, True, 65, "1,500 gp"),

    # Shields
    Armor("Shield", ArmorType.SHIELD, 2, None, None, False, 6, "10 gp"),
]

# SRD Adventuring Gear
ADVENTURING_GEAR = [
    Equipment("Backpack", "Containers", "2 gp", 5),
    Equipment("Ball Bearings (bag of 1,000)", "Standard Gear", "1 gp", 2),
    Equipment("Bedroll", "Standard Gear", "1 gp", 7),
    Equipment("Bell", "Standard Gear", "1 gp", 0),
    Equipment("Blanket", "Standard Gear", "5 sp", 3),
    Equipment("Block and Tackle", "Standard Gear", "1 gp", 5),
    Equipment("Book", "Standard Gear", "25 gp", 5),
    Equipment("Candle", "Standard Gear", "1 cp", 0),
    Equipment("Chain (10 feet)", "Standard Gear", "5 gp", 10),
    Equipment("Chalk (1 piece)", "Standard Gear", "1 cp", 0),
    Equipment("Climber's Kit", "Kits", "25 gp", 12),
    Equipment("Clothes, Common", "Standard Gear", "5 sp", 3),
    Equipment("Clothes, Fine", "Standard Gear", "15 gp", 6),
    Equipment("Clothes, Traveler's", "Standard Gear", "2 gp", 4),
    Equipment("Component Pouch", "Spellcasting Focus", "25 gp", 2),
    Equipment("Crowbar", "Standard Gear", "2 gp", 5),
    Equipment("Flask or Tankard", "Containers", "2 cp", 1),
    Equipment("Grappling Hook", "Standard Gear", "2 gp", 4),
    Equipment("Hammer", "Standard Gear", "1 gp", 3),
    Equipment("Healer's Kit", "Kits", "5 gp", 3),
    Equipment("Holy Symbol", "Spellcasting Focus", "5 gp", 1),
    Equipment("Hourglass", "Standard Gear", "25 gp", 1),
    Equipment("Hunting Trap", "Standard Gear", "5 gp", 25),
    Equipment("Ink (1 ounce bottle)", "Standard Gear", "10 gp", 0),
    Equipment("Ink Pen", "Standard Gear", "2 cp", 0),
    Equipment("Lantern, Bullseye", "Standard Gear", "10 gp", 2),
    Equipment("Lantern, Hooded", "Standard Gear", "5 gp", 2),
    Equipment("Lock", "Standard Gear", "10 gp", 1),
    Equipment("Magnifying Glass", "Standard Gear", "100 gp", 0),
    Equipment("Manacles", "Standard Gear", "2 gp", 6),
    Equipment("Mirror, Steel", "Standard Gear", "5 gp", 0.5),
    Equipment("Oil (flask)", "Standard Gear", "1 sp", 1),
    Equipment("Paper (one sheet)", "Standard Gear", "2 sp", 0),
    Equipment("Parchment (one sheet)", "Standard Gear", "1 sp", 0),
    Equipment("Pick, Miner's", "Standard Gear", "2 gp", 10),
    Equipment("Piton", "Standard Gear", "5 cp", 0.25),
    Equipment("Pole (10-foot)", "Standard Gear", "5 cp", 7),
    Equipment("Pot, Iron", "Containers", "2 gp", 10),
    Equipment("Potion of Healing", "Potion", "50 gp", 0.5,
              "Regain 2d4+2 hit points when you drink this potion."),
    Equipment("Pouch", "Containers", "5 sp", 1),
    Equipment("Quiver", "Standard Gear", "1 gp", 1),
    Equipment("Ram, Portable", "Standard Gear", "4 gp", 35),
    Equipment("Rations (1 day)", "Standard Gear", "5 sp", 2),
    Equipment("Rope, Hempen (50 feet)", "Standard Gear", "1 gp", 10),
    Equipment("Rope, Silk (50 feet)", "Standard Gear", "10 gp", 5),
    Equipment("Sack", "Containers", "1 cp", 0.5),
    Equipment("Scale, Merchant's", "Standard Gear", "5 gp", 3),
    Equipment("Shovel", "Standard Gear", "2 gp", 5),
    Equipment("Signal Whistle", "Standard Gear", "5 cp", 0),
    Equipment("Spellbook", "Spellcasting Focus", "50 gp", 3),
    Equipment("Spikes, Iron (10)", "Standard Gear", "1 gp", 5),
    Equipment("Spyglass", "Standard Gear", "1,000 gp", 1),
    Equipment("Tent, Two-Person", "Standard Gear", "2 gp", 20),
    Equipment("Tinderbox", "Standard Gear", "5 sp", 1),
    Equipment("Torch", "Standard Gear", "1 cp", 1),
    Equipment("Vial", "Containers", "1 gp", 0),
    Equipment("Waterskin", "Containers", "2 sp", 5),
    Equipment("Whetstone", "Standard Gear", "1 cp", 1),
]

# SRD Tools
TOOLS = [
    Equipment("Alchemist's Supplies", "Artisan's Tools", "50 gp", 8),
    Equipment("Brewer's Supplies", "Artisan's Tools", "20 gp", 9),
    Equipment("Calligrapher's Supplies", "Artisan's Tools", "10 gp", 5),
    Equipment("Carpenter's Tools", "Artisan's Tools", "8 gp", 6),
    Equipment("Cartographer's Tools", "Artisan's Tools", "15 gp", 6),
    Equipment("Cobbler's Tools", "Artisan's Tools", "5 gp", 5),
    Equipment("Cook's Utensils", "Artisan's Tools", "1 gp", 8),
    Equipment("Glassblower's Tools", "Artisan's Tools", "30 gp", 5),
    Equipment("Jeweler's Tools", "Artisan's Tools", "25 gp", 2),
    Equipment("Leatherworker's Tools", "Artisan's Tools", "5 gp", 5),
    Equipment("Mason's Tools", "Artisan's Tools", "10 gp", 8),
    Equipment("Painter's Supplies", "Artisan's Tools", "10 gp", 5),
    Equipment("Potter's Tools", "Artisan's Tools", "10 gp", 3),
    Equipment("Smith's Tools", "Artisan's Tools", "20 gp", 8),
    Equipment("Tinker's Tools", "Artisan's Tools", "50 gp", 10),
    Equipment("Weaver's Tools", "Artisan's Tools", "1 gp", 5),
    Equipment("Woodcarver's Tools", "Artisan's Tools", "1 gp", 5),
    Equipment("Dice Set", "Gaming Set", "1 sp", 0),
    Equipment("Playing Card Set", "Gaming Set", "5 sp", 0),
    Equipment("Disguise Kit", "Kit", "25 gp", 3),
    Equipment("Forgery Kit", "Kit", "15 gp", 5),
    Equipment("Herbalism Kit", "Kit", "5 gp", 3),
    Equipment("Navigator's Tools", "Kit", "25 gp", 2),
    Equipment("Poisoner's Kit", "Kit", "50 gp", 2),
    Equipment("Thieves' Tools", "Kit", "25 gp", 1),
    Equipment("Bagpipes", "Musical Instrument", "30 gp", 6),
    Equipment("Drum", "Musical Instrument", "6 gp", 3),
    Equipment("Dulcimer", "Musical Instrument", "25 gp", 10),
    Equipment("Flute", "Musical Instrument", "2 gp", 1),
    Equipment("Lute", "Musical Instrument", "35 gp", 2),
    Equipment("Lyre", "Musical Instrument", "30 gp", 2),
    Equipment("Horn", "Musical Instrument", "3 gp", 2),
    Equipment("Pan Flute", "Musical Instrument", "12 gp", 2),
    Equipment("Shawm", "Musical Instrument", "2 gp", 1),
    Equipment("Viol", "Musical Instrument", "30 gp", 1),
]

# Equipment packs
EQUIPMENT_PACKS = {
    "Burglar's Pack": [
        "Backpack", "Ball Bearings (bag of 1,000)", "String (10 feet)",
        "Bell", "Candle (x5)", "Crowbar", "Hammer", "Piton (x10)",
        "Lantern, Hooded", "Oil (flask) (x2)", "Rations (1 day) (x5)",
        "Tinderbox", "Waterskin", "Rope, Hempen (50 feet)"
    ],
    "Diplomat's Pack": [
        "Chest", "Case, Map or Scroll (x2)", "Clothes, Fine", "Ink (1 ounce bottle)",
        "Ink Pen", "Lamp", "Oil (flask) (x2)", "Paper (one sheet) (x5)",
        "Perfume (vial)", "Sealing Wax", "Soap"
    ],
    "Dungeoneer's Pack": [
        "Backpack", "Crowbar", "Hammer", "Piton (x10)", "Torch (x10)",
        "Tinderbox", "Rations (1 day) (x10)", "Waterskin", "Rope, Hempen (50 feet)"
    ],
    "Entertainer's Pack": [
        "Backpack", "Bedroll", "Clothes, Costume (x2)", "Candle (x5)",
        "Rations (1 day) (x5)", "Waterskin", "Disguise Kit"
    ],
    "Explorer's Pack": [
        "Backpack", "Bedroll", "Mess Kit", "Tinderbox", "Torch (x10)",
        "Rations (1 day) (x10)", "Waterskin", "Rope, Hempen (50 feet)"
    ],
    "Priest's Pack": [
        "Backpack", "Blanket", "Candle (x10)", "Tinderbox", "Alms Box",
        "Block of Incense (x2)", "Censer", "Vestments", "Rations (1 day) (x2)", "Waterskin"
    ],
    "Scholar's Pack": [
        "Backpack", "Book", "Ink (1 ounce bottle)", "Ink Pen",
        "Parchment (one sheet) (x10)", "Little Bag of Sand", "Small Knife"
    ],
}


def get_weapon_by_name(name: str) -> Optional[Weapon]:
    """Get a weapon by name (case-insensitive)."""
    name_lower = name.lower()
    for weapon in ALL_WEAPONS:
        if weapon.name.lower() == name_lower:
            return weapon
    return None


def get_armor_by_name(name: str) -> Optional[Armor]:
    """Get armor by name (case-insensitive)."""
    name_lower = name.lower()
    for armor in ARMOR:
        if armor.name.lower() == name_lower:
            return armor
    return None


def get_equipment_by_name(name: str) -> Optional[Equipment]:
    """Get equipment by name (case-insensitive)."""
    name_lower = name.lower()
    all_equipment = ADVENTURING_GEAR + TOOLS
    for item in all_equipment:
        if item.name.lower() == name_lower:
            return item
    return None


def search_items(query: str) -> list:
    """Search all items by name."""
    query_lower = query.lower()
    results = []

    for weapon in ALL_WEAPONS:
        if query_lower in weapon.name.lower():
            results.append(("weapon", weapon))

    for armor in ARMOR:
        if query_lower in armor.name.lower():
            results.append(("armor", armor))

    for item in ADVENTURING_GEAR + TOOLS:
        if query_lower in item.name.lower():
            results.append(("equipment", item))

    return results
