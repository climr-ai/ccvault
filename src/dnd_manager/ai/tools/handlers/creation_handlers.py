"""Character creation tool handlers.

These handlers work with a CreationSession that holds the character being created.
They don't require an existing character - they create one from scratch.
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from dataclasses import dataclass, field

from dnd_manager.models.character import (
    Character,
    CharacterClass,
    CharacterMeta,
    RulesetId,
    Feature,
    HitPoints,
    HitDicePool,
    HitDice,
    AbilityScores,
    InventoryItem,
    Currency,
    SpellSlot,
    Personality,
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

    # Session metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)

    # Core choices
    ruleset: Optional[str] = None
    name: Optional[str] = None
    class_name: Optional[str] = None
    species_name: Optional[str] = None
    subspecies_name: Optional[str] = None
    background_name: Optional[str] = None

    # Class configuration (extended for multiclass)
    primary_level: int = 1
    primary_subclass: Optional[str] = None
    multiclass_entries: list[dict] = field(default_factory=list)

    # Ability scores (base values before bonuses)
    ability_scores: dict[str, int] = field(default_factory=dict)
    ability_bonuses: dict[str, int] = field(default_factory=dict)

    # Combat stats (direct overrides)
    max_hp: Optional[int] = None
    armor_class: Optional[int] = None
    speed: int = 30
    hit_dice_pools: dict[str, int] = field(default_factory=dict)

    # Extended proficiencies
    skill_proficiencies: list[str] = field(default_factory=list)
    saving_throws: list[str] = field(default_factory=list)
    armor_proficiencies: list[str] = field(default_factory=list)
    weapon_proficiencies: list[str] = field(default_factory=list)
    tool_proficiencies: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)

    # Features
    features: list[dict] = field(default_factory=list)

    # Spells (extended)
    cantrips: list[str] = field(default_factory=list)
    spells: list[str] = field(default_factory=list)
    prepared_spells: list[str] = field(default_factory=list)
    spellcasting_ability: Optional[str] = None
    spell_slots: dict[int, int] = field(default_factory=dict)

    # Equipment
    equipment_items: list[dict] = field(default_factory=list)
    currency: dict[str, int] = field(default_factory=dict)

    # Personality
    personality_data: dict[str, Any] = field(default_factory=dict)
    backstory: Optional[str] = None

    # Feats
    origin_feat: Optional[str] = None
    species_feat: Optional[str] = None

    # The finalized character (None until finalize is called)
    character: Optional[Character] = None

    def get_preview(self) -> dict[str, Any]:
        """Get a preview of the character being created."""
        # Calculate total level
        total_level = self.primary_level
        for mc in self.multiclass_entries:
            total_level += mc.get("level", 0)

        preview = {
            "ruleset": self.ruleset,
            "name": self.name or "(not set)",
            "class": self.class_name or "(not set)",
            "level": self.primary_level,
            "subclass": self.primary_subclass,
            "multiclass": self.multiclass_entries,
            "total_level": total_level,
            "species": self.species_name or "(not set)",
            "subspecies": self.subspecies_name,
            "background": self.background_name or "(not set)",
            "ability_scores": {},
            "skills": self.skill_proficiencies,
            "saving_throws": self.saving_throws,
            "armor_proficiencies": self.armor_proficiencies,
            "weapon_proficiencies": self.weapon_proficiencies,
            "tool_proficiencies": self.tool_proficiencies,
            "languages": self.languages,
            "features_count": len(self.features),
            "cantrips": self.cantrips,
            "spells_known": self.spells,
            "spells_prepared": self.prepared_spells,
            "spell_slots": self.spell_slots,
            "equipment_count": len(self.equipment_items),
            "currency": self.currency,
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

        # HP preview - use override if set, otherwise calculate
        if self.max_hp is not None:
            preview["hp"] = self.max_hp
        elif self.class_name:
            class_info = get_class_info(self.class_name)
            if class_info:
                hit_die = int(class_info.hit_die[1:])
                con_mod = preview["ability_scores"]["constitution"]["modifier"]
                hp = max(1, hit_die + con_mod)
                preview["hp"] = hp
                preview["hit_die"] = class_info.hit_die

        # AC preview
        if self.armor_class is not None:
            preview["ac"] = self.armor_class

        # Speed
        preview["speed"] = self.speed

        # Hit dice pools
        if self.hit_dice_pools:
            preview["hit_dice"] = self.hit_dice_pools

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


# Session management constants
SESSION_TTL_HOURS = 24  # Sessions expire after 24 hours of inactivity
MAX_SESSIONS = 100  # Maximum number of concurrent sessions

# Global creation session (per-conversation)
_creation_sessions: dict[str, CreationSession] = {}


def cleanup_expired_sessions() -> int:
    """Remove expired sessions based on TTL.

    Returns:
        Number of sessions removed
    """
    now = datetime.now()
    ttl = timedelta(hours=SESSION_TTL_HOURS)
    expired = [
        session_id
        for session_id, session in _creation_sessions.items()
        if now - session.last_accessed > ttl
    ]
    for session_id in expired:
        del _creation_sessions[session_id]
    return len(expired)


def cleanup_oldest_sessions(keep_count: int = MAX_SESSIONS) -> int:
    """Remove oldest sessions if we exceed the maximum.

    Args:
        keep_count: Maximum number of sessions to keep

    Returns:
        Number of sessions removed
    """
    if len(_creation_sessions) <= keep_count:
        return 0

    # Sort by last_accessed, oldest first
    sorted_sessions = sorted(
        _creation_sessions.items(),
        key=lambda x: x[1].last_accessed,
    )

    # Remove oldest sessions
    to_remove = len(_creation_sessions) - keep_count
    removed = 0
    for session_id, _ in sorted_sessions[:to_remove]:
        del _creation_sessions[session_id]
        removed += 1

    return removed


def get_creation_session(session_id: str = "default") -> CreationSession:
    """Get or create a creation session.

    Also performs cleanup of expired sessions periodically.
    """
    # Cleanup expired sessions (lightweight check)
    if len(_creation_sessions) > MAX_SESSIONS // 2:
        cleanup_expired_sessions()
        cleanup_oldest_sessions()

    if session_id not in _creation_sessions:
        _creation_sessions[session_id] = CreationSession()
    else:
        # Update last_accessed timestamp
        _creation_sessions[session_id].last_accessed = datetime.now()

    return _creation_sessions[session_id]


def clear_creation_session(session_id: str = "default") -> None:
    """Clear a creation session."""
    if session_id in _creation_sessions:
        del _creation_sessions[session_id]


def get_session_count() -> int:
    """Get the current number of active sessions."""
    return len(_creation_sessions)


def clear_all_sessions() -> int:
    """Clear all sessions. Returns count of sessions cleared."""
    count = len(_creation_sessions)
    _creation_sessions.clear()
    return count


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


# ============================================================================
# Extended creation tools for full character building (multiclass, equipment, etc.)
# ============================================================================


async def set_class_levels(
    primary_class: str,
    primary_level: int,
    primary_subclass: Optional[str] = None,
    multiclass: Optional[list[dict]] = None,
    session_id: str = "default",
) -> dict[str, Any]:
    """Set primary class with level/subclass and optional multiclass entries."""
    session = get_creation_session(session_id)

    # Validate primary class
    class_info = get_class_info(primary_class)
    if not class_info:
        raise ValueError(f"Unknown class: {primary_class}")

    if primary_level < 1 or primary_level > 20:
        raise ValueError(f"Level must be between 1 and 20, got {primary_level}")

    # Set primary class info
    session.class_name = primary_class
    session.primary_level = primary_level
    session.primary_subclass = primary_subclass

    # Validate and set multiclass
    total_level = primary_level
    session.multiclass_entries = []

    if multiclass:
        for mc in multiclass:
            mc_class = mc.get("class")
            mc_level = mc.get("level", 1)
            mc_subclass = mc.get("subclass")

            mc_info = get_class_info(mc_class)
            if not mc_info:
                raise ValueError(f"Unknown multiclass: {mc_class}")

            if mc_level < 1 or mc_level > 20:
                raise ValueError(f"Multiclass level must be between 1 and 20")

            total_level += mc_level
            session.multiclass_entries.append({
                "class": mc_class,
                "level": mc_level,
                "subclass": mc_subclass,
            })

    if total_level > 20:
        raise ValueError(f"Total level ({total_level}) exceeds maximum of 20")

    return {
        "data": {
            "primary_class": primary_class,
            "primary_level": primary_level,
            "primary_subclass": primary_subclass,
            "multiclass": session.multiclass_entries,
            "total_level": total_level,
        },
        "changes": [
            f"Set class to {primary_class} {primary_level}"
            + (f" ({primary_subclass})" if primary_subclass else "")
            + (f" with {len(session.multiclass_entries)} multiclass(es)" if session.multiclass_entries else "")
        ],
    }


async def set_combat_stats(
    max_hp: Optional[int] = None,
    current_hp: Optional[int] = None,
    armor_class: Optional[int] = None,
    speed: Optional[int] = None,
    session_id: str = "default",
) -> dict[str, Any]:
    """Set combat statistics directly (HP, AC, speed)."""
    session = get_creation_session(session_id)

    changes = []

    if max_hp is not None:
        if max_hp < 1:
            raise ValueError("Max HP must be at least 1")
        session.max_hp = max_hp
        changes.append(f"Set max HP to {max_hp}")

    if armor_class is not None:
        if armor_class < 1:
            raise ValueError("AC must be at least 1")
        session.armor_class = armor_class
        changes.append(f"Set AC to {armor_class}")

    if speed is not None:
        if speed < 0:
            raise ValueError("Speed cannot be negative")
        session.speed = speed
        changes.append(f"Set speed to {speed}")

    return {
        "data": {
            "max_hp": session.max_hp,
            "current_hp": current_hp or session.max_hp,
            "armor_class": session.armor_class,
            "speed": session.speed,
        },
        "changes": changes or ["No combat stats changed"],
    }


async def set_hit_dice_pool(
    pools: dict[str, int],
    session_id: str = "default",
) -> dict[str, Any]:
    """Set hit dice pools for multiclass characters."""
    session = get_creation_session(session_id)

    # Validate dice types
    valid_dice = ["d6", "d8", "d10", "d12"]
    for die, count in pools.items():
        if die not in valid_dice:
            raise ValueError(f"Invalid hit die: {die}. Must be one of {valid_dice}")
        if count < 0:
            raise ValueError(f"Hit dice count cannot be negative")

    session.hit_dice_pools = pools

    total = sum(pools.values())
    display = " + ".join(f"{count}{die}" for die, count in pools.items())

    return {
        "data": {
            "pools": pools,
            "total": total,
            "display": display,
        },
        "changes": [f"Set hit dice pool: {display}"],
    }


async def set_saving_throw_proficiencies(
    saves: list[str],
    session_id: str = "default",
) -> dict[str, Any]:
    """Set saving throw proficiencies."""
    session = get_creation_session(session_id)

    valid_saves = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    normalized = []
    for save in saves:
        save_lower = save.lower()
        if save_lower not in valid_saves:
            raise ValueError(f"Invalid saving throw: {save}. Must be one of {valid_saves}")
        normalized.append(save_lower)

    session.saving_throws = normalized

    return {
        "data": {
            "saving_throws": normalized,
            "count": len(normalized),
        },
        "changes": [f"Set saving throw proficiencies: {', '.join(s.upper()[:3] for s in normalized)}"],
    }


async def set_proficiencies(
    armor: Optional[list[str]] = None,
    weapons: Optional[list[str]] = None,
    tools: Optional[list[str]] = None,
    languages: Optional[list[str]] = None,
    session_id: str = "default",
) -> dict[str, Any]:
    """Set armor, weapon, tool, and language proficiencies."""
    session = get_creation_session(session_id)

    changes = []

    if armor is not None:
        session.armor_proficiencies = armor
        changes.append(f"Set armor proficiencies: {', '.join(armor)}")

    if weapons is not None:
        session.weapon_proficiencies = weapons
        changes.append(f"Set weapon proficiencies: {', '.join(weapons)}")

    if tools is not None:
        session.tool_proficiencies = tools
        changes.append(f"Set tool proficiencies: {', '.join(tools)}")

    if languages is not None:
        session.languages = languages
        changes.append(f"Set languages: {', '.join(languages)}")

    return {
        "data": {
            "armor": session.armor_proficiencies,
            "weapons": session.weapon_proficiencies,
            "tools": session.tool_proficiencies,
            "languages": session.languages,
        },
        "changes": changes or ["No proficiencies changed"],
    }


async def add_features(
    features: list[dict],
    session_id: str = "default",
) -> dict[str, Any]:
    """Add multiple features to the character."""
    session = get_creation_session(session_id)

    added = []
    for feat in features:
        name = feat.get("name")
        if not name:
            raise ValueError("Feature must have a name")

        feature_entry = {
            "name": name,
            "source": feat.get("source", "Unknown"),
            "description": feat.get("description", ""),
            "uses": feat.get("uses"),
            "used": feat.get("used", 0),
            "recharge": feat.get("recharge"),
        }
        session.features.append(feature_entry)
        added.append(name)

    return {
        "data": {
            "added": added,
            "count": len(added),
            "total_features": len(session.features),
        },
        "changes": [f"Added {len(added)} features: {', '.join(added[:5])}" + ("..." if len(added) > 5 else "")],
    }


async def set_spellcasting(
    ability: Optional[str] = None,
    cantrips: Optional[list[str]] = None,
    known: Optional[list[str]] = None,
    prepared: Optional[list[str]] = None,
    slots: Optional[dict[int, int]] = None,
    session_id: str = "default",
) -> dict[str, Any]:
    """Configure full spellcasting (ability, cantrips, known, prepared, slots)."""
    session = get_creation_session(session_id)

    changes = []

    if ability is not None:
        valid_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        ability_lower = ability.lower()
        if ability_lower not in valid_abilities:
            raise ValueError(f"Invalid spellcasting ability: {ability}")
        session.spellcasting_ability = ability_lower
        changes.append(f"Set spellcasting ability to {ability_lower.capitalize()}")

    if cantrips is not None:
        session.cantrips = cantrips
        changes.append(f"Set {len(cantrips)} cantrips")

    if known is not None:
        session.spells = known
        changes.append(f"Set {len(known)} spells known")

    if prepared is not None:
        session.prepared_spells = prepared
        changes.append(f"Set {len(prepared)} spells prepared")

    if slots is not None:
        # Convert string keys to int if needed
        session.spell_slots = {int(k): v for k, v in slots.items()}
        total_slots = sum(session.spell_slots.values())
        changes.append(f"Set spell slots ({total_slots} total across levels 1-9)")

    return {
        "data": {
            "ability": session.spellcasting_ability,
            "cantrips_count": len(session.cantrips),
            "known_count": len(session.spells),
            "prepared_count": len(session.prepared_spells),
            "slots": session.spell_slots,
        },
        "changes": changes or ["No spellcasting changes"],
    }


async def add_equipment(
    items: list[dict],
    session_id: str = "default",
) -> dict[str, Any]:
    """Add equipment items to the character."""
    session = get_creation_session(session_id)

    added = []
    attuned_count = sum(1 for i in session.equipment_items if i.get("attuned"))

    for item in items:
        name = item.get("name")
        if not name:
            raise ValueError("Item must have a name")

        is_attuned = item.get("attuned", False)
        if is_attuned:
            attuned_count += 1
            if attuned_count > 3:
                raise ValueError(f"Cannot attune more than 3 items. '{name}' would exceed limit.")

        item_entry = {
            "name": name,
            "quantity": item.get("quantity", 1),
            "weight": item.get("weight"),
            "description": item.get("description"),
            "equipped": item.get("equipped", False),
            "attuned": is_attuned,
        }
        session.equipment_items.append(item_entry)
        added.append(name)

    return {
        "data": {
            "added": added,
            "count": len(added),
            "total_items": len(session.equipment_items),
            "attuned_count": attuned_count,
        },
        "changes": [f"Added {len(added)} items: {', '.join(added[:5])}" + ("..." if len(added) > 5 else "")],
    }


async def set_currency(
    pp: int = 0,
    gp: int = 0,
    ep: int = 0,
    sp: int = 0,
    cp: int = 0,
    session_id: str = "default",
) -> dict[str, Any]:
    """Set currency amounts."""
    session = get_creation_session(session_id)

    if any(v < 0 for v in [pp, gp, ep, sp, cp]):
        raise ValueError("Currency values cannot be negative")

    session.currency = {
        "pp": pp,
        "gp": gp,
        "ep": ep,
        "sp": sp,
        "cp": cp,
    }

    # Calculate total in GP
    total_gp = pp * 10 + gp + ep * 0.5 + sp * 0.1 + cp * 0.01

    return {
        "data": {
            "currency": session.currency,
            "total_gp": total_gp,
        },
        "changes": [f"Set currency: {pp}pp, {gp}gp, {ep}ep, {sp}sp, {cp}cp (total: {total_gp:.2f}gp)"],
    }


async def set_personality(
    traits: Optional[list[str]] = None,
    ideals: Optional[list[str]] = None,
    bonds: Optional[list[str]] = None,
    flaws: Optional[list[str]] = None,
    backstory: Optional[str] = None,
    session_id: str = "default",
) -> dict[str, Any]:
    """Set personality traits, ideals, bonds, flaws, and backstory."""
    session = get_creation_session(session_id)

    changes = []

    if traits is not None:
        session.personality_data["traits"] = traits
        changes.append(f"Set {len(traits)} personality traits")

    if ideals is not None:
        session.personality_data["ideals"] = ideals
        changes.append(f"Set {len(ideals)} ideals")

    if bonds is not None:
        session.personality_data["bonds"] = bonds
        changes.append(f"Set {len(bonds)} bonds")

    if flaws is not None:
        session.personality_data["flaws"] = flaws
        changes.append(f"Set {len(flaws)} flaws")

    if backstory is not None:
        session.backstory = backstory
        changes.append(f"Set backstory ({len(backstory)} characters)")

    return {
        "data": {
            "traits": session.personality_data.get("traits", []),
            "ideals": session.personality_data.get("ideals", []),
            "bonds": session.personality_data.get("bonds", []),
            "flaws": session.personality_data.get("flaws", []),
            "has_backstory": session.backstory is not None,
        },
        "changes": changes or ["No personality changes"],
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

    # Create primary class with level and subclass
    char = Character(
        name=session.name,
        meta=CharacterMeta(ruleset=ruleset_map.get(session.ruleset, RulesetId.DND_2024)),
        primary_class=CharacterClass(
            name=session.class_name,
            level=session.primary_level,
            subclass=session.primary_subclass,
        ),
        species=session.species_name,
        subspecies=session.subspecies_name,
        background=session.background_name,
    )

    # Add multiclass entries
    for mc in session.multiclass_entries:
        char.multiclass.append(CharacterClass(
            name=mc["class"],
            level=mc["level"],
            subclass=mc.get("subclass"),
        ))

    # Set ability scores with bonuses
    abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    ability_scores = {}
    for ability in abilities:
        base = session.ability_scores.get(ability, 10)
        bonus = session.ability_bonuses.get(ability, 0)
        ability_scores[ability] = AbilityScore(base=base + bonus)

    char.abilities = AbilityScores(**ability_scores)

    # Add skill proficiencies
    for skill_name in session.skill_proficiencies:
        skill_key = skill_name.lower().replace(" ", "_")
        try:
            skill_enum = Skill(skill_key)
            char.proficiencies.skills[skill_enum] = SkillProficiency.PROFICIENT
        except ValueError:
            pass

    # Set saving throw proficiencies (use session if provided, else from class)
    if session.saving_throws:
        for save_name in session.saving_throws:
            try:
                ability_enum = Ability(save_name.lower())
                if ability_enum not in char.proficiencies.saving_throws:
                    char.proficiencies.saving_throws.append(ability_enum)
            except ValueError:
                pass
    else:
        # Fall back to class-based saving throws
        class_info = get_class_info(session.class_name)
        if class_info:
            for save_name in class_info.saving_throws:
                try:
                    ability_enum = Ability(save_name.lower())
                    if ability_enum not in char.proficiencies.saving_throws:
                        char.proficiencies.saving_throws.append(ability_enum)
                except ValueError:
                    pass

    # Set other proficiencies (use session if provided, else from class)
    if session.armor_proficiencies:
        char.proficiencies.armor = session.armor_proficiencies.copy()
    elif (class_info := get_class_info(session.class_name)):
        char.proficiencies.armor = class_info.armor_proficiencies.copy()

    if session.weapon_proficiencies:
        char.proficiencies.weapons = session.weapon_proficiencies.copy()
    elif (class_info := get_class_info(session.class_name)):
        char.proficiencies.weapons = class_info.weapon_proficiencies.copy()

    if session.tool_proficiencies:
        char.proficiencies.tools = session.tool_proficiencies.copy()

    if session.languages:
        char.proficiencies.languages = session.languages.copy()

    # Set HP (use override or calculate from class)
    if session.max_hp is not None:
        char.combat.hit_points = HitPoints(maximum=session.max_hp, current=session.max_hp)
    else:
        class_info = get_class_info(session.class_name)
        if class_info:
            hit_die = int(class_info.hit_die[1:])
            con_mod = char.abilities.constitution.modifier
            max_hp = max(1, hit_die + con_mod)
            char.combat.hit_points = HitPoints(maximum=max_hp, current=max_hp)

    # Set AC (use override or leave default)
    if session.armor_class is not None:
        char.combat.armor_class = session.armor_class

    # Set speed
    char.combat.speed = session.speed

    # Set hit dice pool (for multiclass)
    if session.hit_dice_pools:
        pools = {}
        for die, count in session.hit_dice_pools.items():
            pools[die] = HitDice(total=count, remaining=count, die=die)
        char.combat.hit_dice_pool = HitDicePool(pools=pools)

    # Add features
    for feat_data in session.features:
        char.features.append(Feature(
            name=feat_data["name"],
            source=feat_data.get("source", "Unknown"),
            description=feat_data.get("description", ""),
            uses=feat_data.get("uses"),
            used=feat_data.get("used", 0),
            recharge=feat_data.get("recharge"),
        ))

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

    # Set spellcasting
    if session.spellcasting_ability:
        try:
            char.spellcasting.ability = Ability(session.spellcasting_ability.lower())
        except ValueError:
            pass
    elif (class_info := get_class_info(session.class_name)) and class_info.spellcasting_ability:
        try:
            char.spellcasting.ability = Ability(class_info.spellcasting_ability.lower())
        except ValueError:
            pass

    char.spellcasting.cantrips = session.cantrips.copy()
    char.spellcasting.known = session.spells.copy()
    char.spellcasting.prepared = session.prepared_spells.copy()

    # Set spell slots
    if session.spell_slots:
        for level, total in session.spell_slots.items():
            char.spellcasting.slots[level] = SpellSlot(total=total, used=0)

    # Add equipment
    for item_data in session.equipment_items:
        char.equipment.items.append(InventoryItem(
            name=item_data["name"],
            quantity=item_data.get("quantity", 1),
            weight=item_data.get("weight"),
            description=item_data.get("description"),
            equipped=item_data.get("equipped", False),
            attuned=item_data.get("attuned", False),
        ))

    # Set currency
    if session.currency:
        char.equipment.currency = Currency(
            pp=session.currency.get("pp", 0),
            gp=session.currency.get("gp", 0),
            ep=session.currency.get("ep", 0),
            sp=session.currency.get("sp", 0),
            cp=session.currency.get("cp", 0),
        )

    # Set personality
    if session.personality_data:
        char.personality = Personality(
            traits=session.personality_data.get("traits", []),
            ideals=session.personality_data.get("ideals", []),
            bonds=session.personality_data.get("bonds", []),
            flaws=session.personality_data.get("flaws", []),
        )

    if session.backstory:
        char.backstory = session.backstory

    # Store the finalized character
    session.character = char

    # Build class display string
    class_display = f"{char.primary_class.name} {char.primary_class.level}"
    if char.multiclass:
        for mc in char.multiclass:
            class_display += f" / {mc.name} {mc.level}"

    return {
        "data": {
            "name": char.name,
            "class": class_display,
            "total_level": char.total_level,
            "species": char.species,
            "background": char.background,
            "hp": char.combat.hit_points.maximum,
            "ac": char.combat.armor_class,
            "features_count": len(char.features),
            "spells_count": len(char.spellcasting.known) + len(char.spellcasting.prepared),
            "items_count": len(char.equipment.items),
            "character_created": True,
        },
        "changes": [f"Created character: {char.name} the {class_display}!"],
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
