"""Tool definitions for AI-driven character creation."""

from dnd_manager.ai.tools.schema import ToolDefinition, ToolCategory, ToolRiskLevel


# Character initialization
CREATE_CHARACTER = ToolDefinition(
    name="create_character",
    description="""Initialize a new character for creation. This must be called first before setting any other character properties.

Use this when the user wants to create a new character. After calling this, you can set the character's name, class, species, etc.""",
    input_schema={
        "type": "object",
        "properties": {
            "ruleset": {
                "type": "string",
                "description": "The ruleset to use for this character",
                "enum": ["dnd2024", "dnd2014", "tov"],
            },
        },
        "required": ["ruleset"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.MODERATE,
    requires_character=False,
)

SET_CHARACTER_NAME = ToolDefinition(
    name="set_character_name",
    description="Set the character's name. Call this after create_character.",
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The character's name",
            },
        },
        "required": ["name"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

SET_CHARACTER_CLASS = ToolDefinition(
    name="set_character_class",
    description="""Set the character's class. Use lookup_class first to verify the class exists and understand its features.

Common classes: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard.
Tales of the Valiant also has: Mechanist.""",
    input_schema={
        "type": "object",
        "properties": {
            "class_name": {
                "type": "string",
                "description": "The class name (e.g., 'Fighter', 'Wizard')",
            },
        },
        "required": ["class_name"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.MODERATE,
    requires_character=False,
)

SET_CHARACTER_SPECIES = ToolDefinition(
    name="set_character_species",
    description="""Set the character's species (race) and optionally subspecies. Use list_species and lookup_species first to see available options.

In 2024 rules, species don't provide ability bonuses (backgrounds do). In 2014 rules, races provide ability bonuses.""",
    input_schema={
        "type": "object",
        "properties": {
            "species": {
                "type": "string",
                "description": "The species/race name (e.g., 'Elf', 'Dwarf', 'Human')",
            },
            "subspecies": {
                "type": "string",
                "description": "The subspecies/subrace if applicable (e.g., 'High Elf', 'Hill Dwarf')",
            },
        },
        "required": ["species"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.MODERATE,
    requires_character=False,
)

SET_CHARACTER_BACKGROUND = ToolDefinition(
    name="set_character_background",
    description="""Set the character's background. In 2024 rules, backgrounds provide ability score bonuses (+2/+1 or +1/+1/+1) and an origin feat.

Common backgrounds: Acolyte, Charlatan, Criminal, Entertainer, Folk Hero, Guild Artisan, Hermit, Noble, Outlander, Sage, Sailor, Soldier, Urchin.""",
    input_schema={
        "type": "object",
        "properties": {
            "background": {
                "type": "string",
                "description": "The background name (e.g., 'Soldier', 'Sage')",
            },
        },
        "required": ["background"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.MODERATE,
    requires_character=False,
)

ASSIGN_ABILITY_SCORES = ToolDefinition(
    name="assign_ability_scores",
    description="""Assign all six ability scores for the character. You can use standard array, point buy values, or rolled scores.

Standard Array: 15, 14, 13, 12, 10, 8
Point Buy: Each score starts at 8, spend 27 points (costs: 8=0, 9=1, 10=2, 11=3, 12=4, 13=5, 14=7, 15=9)

For optimization:
- Fighters/Paladins: prioritize STR or DEX, then CON
- Wizards: prioritize INT, then CON/DEX
- Clerics: prioritize WIS, then STR or CON
- Rogues: prioritize DEX, then CON/INT/CHA""",
    input_schema={
        "type": "object",
        "properties": {
            "strength": {
                "type": "integer",
                "description": "Strength score (typically 8-15 before bonuses)",
                "minimum": 3,
                "maximum": 18,
            },
            "dexterity": {
                "type": "integer",
                "description": "Dexterity score",
                "minimum": 3,
                "maximum": 18,
            },
            "constitution": {
                "type": "integer",
                "description": "Constitution score",
                "minimum": 3,
                "maximum": 18,
            },
            "intelligence": {
                "type": "integer",
                "description": "Intelligence score",
                "minimum": 3,
                "maximum": 18,
            },
            "wisdom": {
                "type": "integer",
                "description": "Wisdom score",
                "minimum": 3,
                "maximum": 18,
            },
            "charisma": {
                "type": "integer",
                "description": "Charisma score",
                "minimum": 3,
                "maximum": 18,
            },
        },
        "required": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.MODERATE,
    requires_character=False,
)

SET_ABILITY_BONUSES = ToolDefinition(
    name="set_ability_bonuses",
    description="""Set ability score bonuses from race (2014) or background (2024).

In 2024 rules, backgrounds offer +2 to one ability and +1 to another, OR +1 to three abilities.
In 2014 rules, races provide fixed bonuses (e.g., Dwarf gets +2 CON).""",
    input_schema={
        "type": "object",
        "properties": {
            "bonuses": {
                "type": "object",
                "description": "Map of ability name to bonus value",
                "additionalProperties": {"type": "integer"},
            },
        },
        "required": ["bonuses"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.MODERATE,
    requires_character=False,
)

ADD_SKILL_PROFICIENCY = ToolDefinition(
    name="add_skill_proficiency",
    description="""Add a skill proficiency to the character. The number of skills depends on class (e.g., Rogue gets 4, Fighter gets 2).

Skills: Acrobatics, Animal Handling, Arcana, Athletics, Deception, History, Insight, Intimidation, Investigation, Medicine, Nature, Perception, Performance, Persuasion, Religion, Sleight of Hand, Stealth, Survival.""",
    input_schema={
        "type": "object",
        "properties": {
            "skill": {
                "type": "string",
                "description": "The skill name",
                "enum": [
                    "Acrobatics", "Animal Handling", "Arcana", "Athletics",
                    "Deception", "History", "Insight", "Intimidation",
                    "Investigation", "Medicine", "Nature", "Perception",
                    "Performance", "Persuasion", "Religion", "Sleight of Hand",
                    "Stealth", "Survival"
                ],
            },
        },
        "required": ["skill"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

SELECT_CANTRIPS = ToolDefinition(
    name="select_cantrips",
    description="""Select cantrips for a spellcasting character. Use get_class_spells with max_level=0 to see available cantrips.

Number of cantrips at level 1 varies by class:
- Bard: 2, Cleric: 3, Druid: 2, Sorcerer: 4, Warlock: 2, Wizard: 3""",
    input_schema={
        "type": "object",
        "properties": {
            "cantrips": {
                "type": "array",
                "description": "List of cantrip names to learn",
                "items": {"type": "string"},
            },
        },
        "required": ["cantrips"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

SELECT_SPELLS = ToolDefinition(
    name="select_spells",
    description="""Select 1st-level spells for a spellcasting character. Use get_class_spells with max_level=1 to see available spells.

Number of spells at level 1 varies:
- Bard: 4 known, Sorcerer: 2 known, Warlock: 2 known
- Cleric/Druid: Prepare WIS mod + 1 spells
- Wizard: 6 in spellbook, prepare INT mod + 1""",
    input_schema={
        "type": "object",
        "properties": {
            "spells": {
                "type": "array",
                "description": "List of 1st-level spell names",
                "items": {"type": "string"},
            },
        },
        "required": ["spells"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

SELECT_ORIGIN_FEAT = ToolDefinition(
    name="select_origin_feat",
    description="""Select an origin feat (2024 rules only). Origin feats come from backgrounds.

Common origin feats: Alert, Crafter, Healer, Lucky, Magic Initiate, Musician, Savage Attacker, Skilled, Tavern Brawler, Tough.""",
    input_schema={
        "type": "object",
        "properties": {
            "feat": {
                "type": "string",
                "description": "The origin feat name",
            },
        },
        "required": ["feat"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

GET_CHARACTER_PREVIEW = ToolDefinition(
    name="get_character_preview",
    description="Get a preview of the character being created, showing all selected options and calculated stats.",
    input_schema={
        "type": "object",
        "properties": {},
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

FINALIZE_CHARACTER = ToolDefinition(
    name="finalize_character",
    description="""Complete character creation and save the character. This calculates HP, sets up proficiencies, and grants starting equipment.

Only call this when all required fields are set: name, class, species, background (for 2024), and ability scores.""",
    input_schema={
        "type": "object",
        "properties": {
            "confirm": {
                "type": "boolean",
                "description": "Set to true to confirm character creation",
            },
        },
        "required": ["confirm"],
    },
    category=ToolCategory.CHARACTER,
    risk_level=ToolRiskLevel.DESTRUCTIVE,
    requires_character=False,
)

SUGGEST_BUILD = ToolDefinition(
    name="suggest_build",
    description="""Suggest an optimized build for a character concept. Analyzes the concept and recommends class, species, background, ability scores, and key choices.

Use this when a user describes what they want to play (e.g., "sneaky archer", "holy warrior", "fire mage").""",
    input_schema={
        "type": "object",
        "properties": {
            "concept": {
                "type": "string",
                "description": "The character concept or playstyle the user wants",
            },
            "optimization_focus": {
                "type": "string",
                "description": "What to optimize for",
                "enum": ["combat", "roleplay", "balanced"],
            },
            "ruleset": {
                "type": "string",
                "description": "The ruleset to use",
                "enum": ["dnd2024", "dnd2014", "tov"],
            },
        },
        "required": ["concept"],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)

CREATE_ADVANCEMENT_PLAN = ToolDefinition(
    name="create_advancement_plan",
    description="""Create a level 1-20 advancement plan for the character. Includes subclass selection, ASI/feat choices, spell progression, and multiclass options if desired.

Call this after the basic character is set up to help the player plan their progression.""",
    input_schema={
        "type": "object",
        "properties": {
            "target_level": {
                "type": "integer",
                "description": "Maximum level to plan to (default 20)",
                "minimum": 2,
                "maximum": 20,
            },
            "allow_multiclass": {
                "type": "boolean",
                "description": "Whether to consider multiclassing options",
            },
            "optimization_focus": {
                "type": "string",
                "description": "What to optimize the plan for",
                "enum": ["damage", "utility", "survivability", "roleplay", "balanced"],
            },
        },
        "required": [],
    },
    category=ToolCategory.QUERY,
    risk_level=ToolRiskLevel.SAFE,
    requires_character=False,
)


# All creation tools
CREATION_TOOLS = [
    CREATE_CHARACTER,
    SET_CHARACTER_NAME,
    SET_CHARACTER_CLASS,
    SET_CHARACTER_SPECIES,
    SET_CHARACTER_BACKGROUND,
    ASSIGN_ABILITY_SCORES,
    SET_ABILITY_BONUSES,
    ADD_SKILL_PROFICIENCY,
    SELECT_CANTRIPS,
    SELECT_SPELLS,
    SELECT_ORIGIN_FEAT,
    GET_CHARACTER_PREVIEW,
    FINALIZE_CHARACTER,
    SUGGEST_BUILD,
    CREATE_ADVANCEMENT_PLAN,
]
