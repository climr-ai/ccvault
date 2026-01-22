"""Character creation tool handlers.

These handlers work with a CreationSession that holds the character being created.
They don't require an existing character - they create one from scratch.
"""

from typing import Any, Optional
from dataclasses import dataclass, field

from dnd_manager.models.character import (
    Character,
    CharacterClass,
    CharacterMeta,
    RulesetId,
    Feature,
    HitPoints,
    AbilityScores,
)
from dnd_manager.models.abilities import (
    AbilityScore,
    Skill,
    SkillProficiency,
    Ability,
)
from dnd_manager.data import get_class_info, get_species, get_background


@dataclass
class CreationSession:
    """Holds the state of a character being created via AI."""

    # Core choices
    ruleset: Optional[str] = None
    name: Optional[str] = None
    class_name: Optional[str] = None
    species_name: Optional[str] = None
    subspecies_name: Optional[str] = None
    background_name: Optional[str] = None

    # Ability scores (base values before bonuses)
    ability_scores: dict[str, int] = field(default_factory=dict)
    ability_bonuses: dict[str, int] = field(default_factory=dict)

    # Proficiencies
    skill_proficiencies: list[str] = field(default_factory=list)

    # Spells
    cantrips: list[str] = field(default_factory=list)
    spells: list[str] = field(default_factory=list)

    # Feats
    origin_feat: Optional[str] = None
    species_feat: Optional[str] = None

    # The finalized character (None until finalize is called)
    character: Optional[Character] = None

    def get_preview(self) -> dict[str, Any]:
        """Get a preview of the character being created."""
        preview = {
            "ruleset": self.ruleset,
            "name": self.name or "(not set)",
            "class": self.class_name or "(not set)",
            "species": self.species_name or "(not set)",
            "subspecies": self.subspecies_name,
            "background": self.background_name or "(not set)",
            "ability_scores": {},
            "skills": self.skill_proficiencies,
            "cantrips": self.cantrips,
            "spells": self.spells,
            "origin_feat": self.origin_feat,
            "species_feat": self.species_feat,
        }

        # Build ability score display
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in abilities:
            base = self.ability_scores.get(ability, 10)
            bonus = self.ability_bonuses.get(ability, 0)
            total = base + bonus
            modifier = (total - 10) // 2
            preview["ability_scores"][ability] = {
                "base": base,
                "bonus": bonus,
                "total": total,
                "modifier": modifier,
            }

        # Calculate HP preview if class is set
        if self.class_name:
            class_info = get_class_info(self.class_name)
            if class_info:
                hit_die = int(class_info.hit_die[1:])
                con_mod = preview["ability_scores"]["constitution"]["modifier"]
                hp = max(1, hit_die + con_mod)
                preview["hp"] = hp
                preview["hit_die"] = class_info.hit_die

        return preview

    def is_complete(self) -> tuple[bool, list[str]]:
        """Check if the character has all required fields."""
        missing = []
        if not self.name:
            missing.append("name")
        if not self.class_name:
            missing.append("class")
        if not self.species_name:
            missing.append("species")
        if not self.ability_scores:
            missing.append("ability scores")
        if self.ruleset == "dnd2024" and not self.background_name:
            missing.append("background (required for 2024 rules)")

        return len(missing) == 0, missing


# Global creation session (per-conversation)
_creation_sessions: dict[str, CreationSession] = {}


def get_creation_session(session_id: str = "default") -> CreationSession:
    """Get or create a creation session."""
    if session_id not in _creation_sessions:
        _creation_sessions[session_id] = CreationSession()
    return _creation_sessions[session_id]


def clear_creation_session(session_id: str = "default") -> None:
    """Clear a creation session."""
    if session_id in _creation_sessions:
        del _creation_sessions[session_id]


# Tool handlers

async def create_character(
    ruleset: str,
    session_id: str = "default",
) -> dict[str, Any]:
    """Initialize a new character creation session."""
    # Clear any existing session
    clear_creation_session(session_id)

    session = get_creation_session(session_id)
    session.ruleset = ruleset

    ruleset_names = {
        "dnd2024": "D&D 2024 (5.5e)",
        "dnd2014": "D&D 2014 (5e)",
        "tov": "Tales of the Valiant",
    }

    return {
        "data": {
            "ruleset": ruleset,
            "ruleset_name": ruleset_names.get(ruleset, ruleset),
            "session_started": True,
        },
        "changes": [f"Started character creation using {ruleset_names.get(ruleset, ruleset)} rules"],
    }


async def set_character_name(
    name: str,
    session_id: str = "default",
) -> dict[str, Any]:
    """Set the character's name."""
    session = get_creation_session(session_id)
    old_name = session.name
    session.name = name

    return {
        "data": {
            "name": name,
            "previous_name": old_name,
        },
        "changes": [f"Set character name to '{name}'"],
    }


async def set_character_class(
    class_name: str,
    session_id: str = "default",
) -> dict[str, Any]:
    """Set the character's class."""
    session = get_creation_session(session_id)

    # Validate class exists
    class_info = get_class_info(class_name)
    if not class_info:
        raise ValueError(f"Unknown class: {class_name}")

    old_class = session.class_name
    session.class_name = class_name

    # Clear skills/spells if class changed (they may no longer be valid)
    if old_class and old_class != class_name:
        session.skill_proficiencies = []
        session.cantrips = []
        session.spells = []

    return {
        "data": {
            "class": class_name,
            "hit_die": class_info.hit_die,
            "primary_ability": class_info.primary_ability,
            "saving_throws": class_info.saving_throws,
            "skill_choices": class_info.skill_choices,
            "skill_options": class_info.skill_options,
            "is_caster": class_info.spellcasting_ability is not None,
            "spellcasting_ability": class_info.spellcasting_ability,
        },
        "changes": [f"Set class to {class_name}"],
    }


async def set_character_species(
    species: str,
    subspecies: Optional[str] = None,
    session_id: str = "default",
) -> dict[str, Any]:
    """Set the character's species and optional subspecies."""
    session = get_creation_session(session_id)

    # Validate species exists
    species_data = get_species(species)
    if not species_data:
        raise ValueError(f"Unknown species: {species}")

    # Validate subspecies if provided
    if subspecies:
        subspecies_found = any(s.name == subspecies for s in species_data.subspecies)
        if not subspecies_found:
            available = [s.name for s in species_data.subspecies]
            raise ValueError(f"Unknown subspecies '{subspecies}' for {species}. Available: {available}")

    session.species_name = species
    session.subspecies_name = subspecies

    # Get traits info
    traits = [t.name for t in species_data.traits]

    return {
        "data": {
            "species": species,
            "subspecies": subspecies,
            "size": species_data.size,
            "speed": species_data.speed,
            "traits": traits,
            "available_subspecies": [s.name for s in species_data.subspecies] if species_data.subspecies else [],
        },
        "changes": [
            f"Set species to {species}" + (f" ({subspecies})" if subspecies else "")
        ],
    }


async def set_character_background(
    background: str,
    session_id: str = "default",
) -> dict[str, Any]:
    """Set the character's background."""
    session = get_creation_session(session_id)

    # Validate background exists
    bg_data = get_background(background)
    if not bg_data:
        raise ValueError(f"Unknown background: {background}")

    session.background_name = background

    return {
        "data": {
            "background": background,
            "feature_name": bg_data.feature.name if bg_data.feature else None,
            "feature_description": bg_data.feature.description if bg_data.feature else None,
            "skill_proficiencies": bg_data.skill_proficiencies,
            "tool_proficiencies": bg_data.tool_proficiencies,
            "languages": bg_data.languages,
            "ability_score_options": bg_data.ability_score_options,
            "origin_feat": bg_data.origin_feat,
        },
        "changes": [f"Set background to {background}"],
    }


async def assign_ability_scores(
    strength: int,
    dexterity: int,
    constitution: int,
    intelligence: int,
    wisdom: int,
    charisma: int,
    session_id: str = "default",
) -> dict[str, Any]:
    """Assign all six ability scores."""
    session = get_creation_session(session_id)

    session.ability_scores = {
        "strength": strength,
        "dexterity": dexterity,
        "constitution": constitution,
        "intelligence": intelligence,
        "wisdom": wisdom,
        "charisma": charisma,
    }

    # Calculate modifiers
    modifiers = {}
    for ability, score in session.ability_scores.items():
        modifiers[ability] = (score - 10) // 2

    return {
        "data": {
            "scores": session.ability_scores,
            "modifiers": modifiers,
        },
        "changes": [
            f"Assigned ability scores: STR {strength}, DEX {dexterity}, CON {constitution}, INT {intelligence}, WIS {wisdom}, CHA {charisma}"
        ],
    }


async def set_ability_bonuses(
    bonuses: dict[str, int],
    session_id: str = "default",
) -> dict[str, Any]:
    """Set ability score bonuses from race/background."""
    session = get_creation_session(session_id)

    session.ability_bonuses = bonuses

    # Calculate new totals
    totals = {}
    for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        base = session.ability_scores.get(ability, 10)
        bonus = bonuses.get(ability, 0)
        totals[ability] = base + bonus

    return {
        "data": {
            "bonuses": bonuses,
            "new_totals": totals,
        },
        "changes": [
            f"Applied ability bonuses: " + ", ".join(f"{k.upper()[:3]} +{v}" for k, v in bonuses.items() if v > 0)
        ],
    }


async def add_skill_proficiency(
    skill: str,
    session_id: str = "default",
) -> dict[str, Any]:
    """Add a skill proficiency."""
    session = get_creation_session(session_id)

    if skill in session.skill_proficiencies:
        raise ValueError(f"Already proficient in {skill}")

    # Validate skill name
    valid_skills = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics",
        "Deception", "History", "Insight", "Intimidation",
        "Investigation", "Medicine", "Nature", "Perception",
        "Performance", "Persuasion", "Religion", "Sleight of Hand",
        "Stealth", "Survival"
    ]
    if skill not in valid_skills:
        raise ValueError(f"Unknown skill: {skill}")

    session.skill_proficiencies.append(skill)

    # Check how many skills the class allows
    max_skills = 2
    if session.class_name:
        class_info = get_class_info(session.class_name)
        if class_info:
            max_skills = class_info.skill_choices

    return {
        "data": {
            "skill": skill,
            "total_skills": len(session.skill_proficiencies),
            "max_skills": max_skills,
            "remaining": max_skills - len(session.skill_proficiencies),
        },
        "changes": [f"Added skill proficiency: {skill}"],
    }


async def select_cantrips(
    cantrips: list[str],
    session_id: str = "default",
) -> dict[str, Any]:
    """Select cantrips for the character."""
    session = get_creation_session(session_id)

    session.cantrips = cantrips

    return {
        "data": {
            "cantrips": cantrips,
            "count": len(cantrips),
        },
        "changes": [f"Selected {len(cantrips)} cantrips: {', '.join(cantrips)}"],
    }


async def select_spells(
    spells: list[str],
    session_id: str = "default",
) -> dict[str, Any]:
    """Select 1st-level spells for the character."""
    session = get_creation_session(session_id)

    session.spells = spells

    return {
        "data": {
            "spells": spells,
            "count": len(spells),
        },
        "changes": [f"Selected {len(spells)} spells: {', '.join(spells)}"],
    }


async def select_origin_feat(
    feat: str,
    session_id: str = "default",
) -> dict[str, Any]:
    """Select an origin feat."""
    session = get_creation_session(session_id)

    session.origin_feat = feat

    return {
        "data": {
            "feat": feat,
        },
        "changes": [f"Selected origin feat: {feat}"],
    }


async def get_character_preview(
    session_id: str = "default",
) -> dict[str, Any]:
    """Get a preview of the character being created."""
    session = get_creation_session(session_id)

    preview = session.get_preview()
    is_complete, missing = session.is_complete()

    return {
        "data": {
            "preview": preview,
            "is_complete": is_complete,
            "missing_fields": missing,
        },
        "changes": [],
    }


async def finalize_character(
    confirm: bool,
    session_id: str = "default",
) -> dict[str, Any]:
    """Finalize and create the character."""
    if not confirm:
        return {
            "data": {"confirmed": False},
            "changes": ["Character creation not confirmed"],
        }

    session = get_creation_session(session_id)

    # Check completeness
    is_complete, missing = session.is_complete()
    if not is_complete:
        raise ValueError(f"Cannot finalize: missing {', '.join(missing)}")

    # Map ruleset string to enum
    ruleset_map = {
        "dnd2024": RulesetId.DND_2024,
        "dnd2014": RulesetId.DND_2014,
        "tov": RulesetId.TALES_OF_VALIANT,
    }

    # Create the character
    char = Character(
        name=session.name,
        meta=CharacterMeta(ruleset=ruleset_map.get(session.ruleset, RulesetId.DND_2024)),
        primary_class=CharacterClass(name=session.class_name, level=1),
        species=session.species_name,
        subspecies=session.subspecies_name,
        background=session.background_name,
    )

    # Set ability scores with bonuses
    abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    ability_scores = {}
    for ability in abilities:
        base = session.ability_scores.get(ability, 10)
        bonus = session.ability_bonuses.get(ability, 0)
        ability_scores[ability] = AbilityScore(base=base, bonus=bonus)

    char.abilities = AbilityScores(**ability_scores)

    # Add skill proficiencies
    for skill_name in session.skill_proficiencies:
        skill_key = skill_name.lower().replace(" ", "_")
        try:
            skill_enum = Skill(skill_key)
            char.proficiencies.skills[skill_enum] = SkillProficiency.PROFICIENT
        except ValueError:
            pass

    # Add class proficiencies
    class_info = get_class_info(session.class_name)
    if class_info:
        # Saving throws
        for save_name in class_info.saving_throws:
            try:
                ability_enum = Ability(save_name.lower())
                if ability_enum not in char.proficiencies.saving_throws:
                    char.proficiencies.saving_throws.append(ability_enum)
            except ValueError:
                pass

        # Weapons and armor
        char.proficiencies.weapons = class_info.weapon_proficiencies.copy()
        char.proficiencies.armor = class_info.armor_proficiencies.copy()

        # Calculate HP
        hit_die = int(class_info.hit_die[1:])
        con_mod = char.abilities.constitution.modifier
        max_hp = max(1, hit_die + con_mod)
        char.combat.hit_points = HitPoints(maximum=max_hp, current=max_hp)

        # Set spellcasting if applicable
        if class_info.spellcasting_ability:
            try:
                char.spellcasting.ability = Ability(class_info.spellcasting_ability.lower())
            except ValueError:
                pass
            char.spellcasting.cantrips = session.cantrips.copy()
            char.spellcasting.known = session.spells.copy()

    # Add origin feat if selected
    if session.origin_feat:
        from dnd_manager.data import get_feat
        feat_data = get_feat(session.origin_feat)
        if feat_data:
            char.features.append(Feature(
                name=session.origin_feat,
                source="feat",
                description=feat_data.description,
            ))

    # Store the finalized character
    session.character = char

    return {
        "data": {
            "name": char.name,
            "class": f"{char.primary_class.name} {char.primary_class.level}",
            "species": char.species,
            "background": char.background,
            "hp": char.combat.hit_points.maximum,
            "character_created": True,
        },
        "changes": [f"Created character: {char.name} the {char.primary_class.name}!"],
        "character": char,  # Special key to return the created character
    }


async def suggest_build(
    concept: str,
    optimization_focus: str = "balanced",
    ruleset: str = "dnd2024",
) -> dict[str, Any]:
    """Suggest a build based on a character concept.

    This is a query tool - it doesn't modify state, just provides recommendations.
    The AI will use its knowledge to interpret the concept and suggest options.
    """
    # This tool primarily relies on the AI's knowledge - we just structure the response
    return {
        "data": {
            "concept": concept,
            "optimization_focus": optimization_focus,
            "ruleset": ruleset,
            "note": "Use your D&D knowledge to suggest class, species, background, and ability score distribution based on this concept.",
        },
        "changes": [],
    }


async def create_advancement_plan(
    target_level: int = 20,
    allow_multiclass: bool = False,
    optimization_focus: str = "balanced",
    session_id: str = "default",
) -> dict[str, Any]:
    """Create an advancement plan for the character.

    This is a query tool - the AI generates the plan based on the current character state.
    """
    session = get_creation_session(session_id)

    return {
        "data": {
            "current_class": session.class_name,
            "target_level": target_level,
            "allow_multiclass": allow_multiclass,
            "optimization_focus": optimization_focus,
            "note": "Generate a level-by-level advancement plan including subclass selection, ASI/feat choices, and key spell selections.",
        },
        "changes": [],
    }
