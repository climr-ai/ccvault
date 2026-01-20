"""Tool definitions for querying ruleset data (spells, features, species, etc.)."""

from dnd_manager.ai.tools.schema import ToolDefinition, ToolCategory, ToolRiskLevel

# Spell lookup tools
LOOKUP_SPELL = ToolDefinition(
    name="lookup_spell",
    description="Look up a spell's full details including level, school, casting time, range, components, duration, and description. Use this whenever discussing spell mechanics - NEVER guess about spell details.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The spell name to look up (case-insensitive)",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

SEARCH_SPELLS = ToolDefinition(
    name="search_spells",
    description="Search for spells by level, school, class availability, or other criteria. Use this to find spells that match specific requirements.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Text to search for in spell names",
            },
            "level": {
                "type": "integer",
                "description": "Spell level (0 for cantrips, 1-9 for leveled spells)",
            },
            "school": {
                "type": "string",
                "description": "School of magic (Abjuration, Conjuration, Divination, Enchantment, Evocation, Illusion, Necromancy, Transmutation)",
            },
            "class_name": {
                "type": "string",
                "description": "Class that can cast this spell (Wizard, Cleric, etc.)",
            },
            "concentration": {
                "type": "boolean",
                "description": "Whether the spell requires concentration",
            },
            "ritual": {
                "type": "boolean",
                "description": "Whether the spell can be cast as a ritual",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default 10)",
            },
        },
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

GET_CLASS_SPELLS = ToolDefinition(
    name="get_class_spells",
    description="Get all spells available to a specific class. Use this when helping a player choose spells for their character.",
    input_schema={
        "type": "object",
        "properties": {
            "class_name": {
                "type": "string",
                "description": "The class name (Wizard, Cleric, Bard, etc.)",
            },
            "max_level": {
                "type": "integer",
                "description": "Maximum spell level to include (default 9)",
            },
        },
        "required": ["class_name"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

# Class/Subclass lookup tools
LOOKUP_CLASS = ToolDefinition(
    name="lookup_class",
    description="Look up a class's details including hit die, primary ability, saving throw proficiencies, and armor/weapon proficiencies. Use this when discussing class mechanics.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The class name to look up",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

GET_SUBCLASSES = ToolDefinition(
    name="get_subclasses",
    description="Get all subclasses available for a class. Use this when helping a player choose a subclass.",
    input_schema={
        "type": "object",
        "properties": {
            "class_name": {
                "type": "string",
                "description": "The parent class name",
            },
        },
        "required": ["class_name"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

# Species/Race lookup tools
LOOKUP_SPECIES = ToolDefinition(
    name="lookup_species",
    description="Look up a species/race's traits, size, speed, and abilities. Use this when discussing racial features or character creation.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The species/race name to look up",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

LIST_SPECIES = ToolDefinition(
    name="list_species",
    description="List all available playable species/races. Use this when helping a player choose a race for their character.",
    input_schema={
        "type": "object",
        "properties": {},
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

# Feat lookup tools
LOOKUP_FEAT = ToolDefinition(
    name="lookup_feat",
    description="Look up a feat's details including prerequisites and benefits. Use this when discussing feat options or verifying prerequisites.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The feat name to look up",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

SEARCH_FEATS = ToolDefinition(
    name="search_feats",
    description="Search for feats by category or prerequisites. Use this to find feats that match specific requirements.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Text to search for in feat names",
            },
            "category": {
                "type": "string",
                "description": "Feat category (General, Origin, Fighting Style, Epic Boon, etc.)",
            },
            "has_prerequisites": {
                "type": "boolean",
                "description": "Whether the feat has prerequisites",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default 10)",
            },
        },
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

# Magic item lookup tools
LOOKUP_MAGIC_ITEM = ToolDefinition(
    name="lookup_magic_item",
    description="Look up a magic item's details including rarity, attunement requirements, and properties. Use this when discussing magic items.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The magic item name to look up",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

SEARCH_MAGIC_ITEMS = ToolDefinition(
    name="search_magic_items",
    description="Search for magic items by rarity, type, or attunement. Use this to find suitable magic items for a character.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Text to search for in item names",
            },
            "rarity": {
                "type": "string",
                "description": "Item rarity (Common, Uncommon, Rare, Very Rare, Legendary, Artifact)",
            },
            "item_type": {
                "type": "string",
                "description": "Type of item (Armor, Weapon, Wondrous Item, etc.)",
            },
            "requires_attunement": {
                "type": "boolean",
                "description": "Whether the item requires attunement",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default 10)",
            },
        },
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

# Monster lookup tools
LOOKUP_MONSTER = ToolDefinition(
    name="lookup_monster",
    description="Look up a monster's stats including CR, HP, AC, abilities, and attacks. Use this when running encounters or answering questions about monsters.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The monster name to look up",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

SEARCH_MONSTERS = ToolDefinition(
    name="search_monsters",
    description="Search for monsters by CR, type, or name. Use this to find monsters for encounters.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Text to search for in monster names",
            },
            "cr_min": {
                "type": "number",
                "description": "Minimum challenge rating",
            },
            "cr_max": {
                "type": "number",
                "description": "Maximum challenge rating",
            },
            "monster_type": {
                "type": "string",
                "description": "Monster type (Aberration, Beast, Dragon, Fiend, Humanoid, Undead, etc.)",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default 10)",
            },
        },
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

GET_ENCOUNTER_MONSTERS = ToolDefinition(
    name="get_encounter_monsters",
    description="Get monsters suitable for an encounter based on party level. Use this when helping the DM build encounters.",
    input_schema={
        "type": "object",
        "properties": {
            "party_level": {
                "type": "integer",
                "description": "Average level of the party",
            },
            "party_size": {
                "type": "integer",
                "description": "Number of party members (default 4)",
            },
        },
        "required": ["party_level"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

# All ruleset tools
RULESET_TOOLS = [
    # Spells
    LOOKUP_SPELL,
    SEARCH_SPELLS,
    GET_CLASS_SPELLS,
    # Classes
    LOOKUP_CLASS,
    GET_SUBCLASSES,
    # Species
    LOOKUP_SPECIES,
    LIST_SPECIES,
    # Feats
    LOOKUP_FEAT,
    SEARCH_FEATS,
    # Magic Items
    LOOKUP_MAGIC_ITEM,
    SEARCH_MAGIC_ITEMS,
    # Monsters
    LOOKUP_MONSTER,
    SEARCH_MONSTERS,
    GET_ENCOUNTER_MONSTERS,
]
