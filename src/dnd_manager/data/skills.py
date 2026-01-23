"""Skill descriptions for supported rulesets."""

from __future__ import annotations

from typing import Optional

from dnd_manager.models.abilities import Skill


DEFAULT_SKILL_DESCRIPTIONS: dict[Skill, str] = {
    Skill.ACROBATICS: "Balance, flips, and nimble movement on tricky surfaces.",
    Skill.ANIMAL_HANDLING: "Calm, control, or intuit the behavior of animals.",
    Skill.ARCANA: "Recall lore about magic, spells, and magical traditions.",
    Skill.ATHLETICS: "Climb, jump, swim, and perform feats of raw strength.",
    Skill.DECEPTION: "Mislead or lie convincingly through words or behavior.",
    Skill.HISTORY: "Recall events, legends, and historical figures or cultures.",
    Skill.INSIGHT: "Read motives and body language to gauge intent or truthfulness.",
    Skill.INTIMIDATION: "Influence through threats, presence, or coercion.",
    Skill.INVESTIGATION: "Search for clues and draw logical conclusions.",
    Skill.MEDICINE: "Stabilize the dying, diagnose illness, and treat wounds.",
    Skill.NATURE: "Know terrain, plants, animals, and natural cycles.",
    Skill.PERCEPTION: "Notice details using sight, sound, or other senses.",
    Skill.PERFORMANCE: "Entertain through acting, music, or other performance.",
    Skill.PERSUASION: "Influence with tact, honest appeal, or negotiation.",
    Skill.RELIGION: "Know deities, rites, symbols, and religious traditions.",
    Skill.SLEIGHT_OF_HAND: "Use nimble fingers for tricks, palming, or concealment.",
    Skill.STEALTH: "Move quietly and stay hidden from notice.",
    Skill.SURVIVAL: "Track, forage, and navigate in the wilderness.",
}

RULESET_SKILL_DESCRIPTIONS: dict[str, dict[Skill, str]] = {
    "dnd2014": DEFAULT_SKILL_DESCRIPTIONS,
    "dnd2024": DEFAULT_SKILL_DESCRIPTIONS,
    "tov": DEFAULT_SKILL_DESCRIPTIONS,
}


def skill_name_to_enum(skill_name: str) -> Optional[Skill]:
    """Convert a display name like 'Sleight of Hand' to Skill enum."""
    normalized = (
        skill_name.strip()
        .lower()
        .replace("’", "")
        .replace("'", "")
        .replace("-", " ")
        .replace(" ", "_")
    )
    try:
        return Skill(normalized)
    except ValueError:
        return None


def get_skill_description(skill_name: str, ruleset: Optional[str] = None) -> str:
    """Return a ruleset-appropriate description for a skill name."""
    skill = skill_name_to_enum(skill_name)
    if not skill:
        return ""
    if ruleset and ruleset in RULESET_SKILL_DESCRIPTIONS:
        return RULESET_SKILL_DESCRIPTIONS[ruleset].get(skill, "")
    return DEFAULT_SKILL_DESCRIPTIONS.get(skill, "")
