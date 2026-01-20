"""Ruleset implementations for different D&D variants."""

from dnd_manager.rulesets.base import (
    Ruleset,
    RulesetRegistry,
    CharacterCreationStep,
    SubclassProgression,
    SpellSlotProgression,
    CasterType,
)
from dnd_manager.rulesets.dnd2024 import DnD2024Ruleset
from dnd_manager.rulesets.dnd2014 import DnD2014Ruleset
from dnd_manager.rulesets.tov import TalesOfTheValiantRuleset

__all__ = [
    "Ruleset",
    "RulesetRegistry",
    "CharacterCreationStep",
    "SubclassProgression",
    "SpellSlotProgression",
    "CasterType",
    "DnD2024Ruleset",
    "DnD2014Ruleset",
    "TalesOfTheValiantRuleset",
]

# Register all rulesets
RulesetRegistry.register(DnD2024Ruleset())
RulesetRegistry.register(DnD2014Ruleset())
RulesetRegistry.register(TalesOfTheValiantRuleset())
