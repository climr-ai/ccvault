"""Balance guidelines system for homebrew content creation.

This module loads and manages configurable balance guidelines that help
AI assistants provide balanced homebrew creation advice.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any
import yaml

from platformdirs import user_data_dir


@dataclass
class BalanceGuidelines:
    """Container for balance guidelines data."""
    version: str = "1.0"
    spells: dict = field(default_factory=dict)
    magic_items: dict = field(default_factory=dict)
    races: dict = field(default_factory=dict)
    classes: dict = field(default_factory=dict)
    subclasses: dict = field(default_factory=dict)
    feats: dict = field(default_factory=dict)
    backgrounds: dict = field(default_factory=dict)
    general_principles: dict = field(default_factory=dict)
    ai_guidance: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "BalanceGuidelines":
        """Create guidelines from a dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            spells=data.get("spells", {}),
            magic_items=data.get("magic_items", {}),
            races=data.get("races", {}),
            classes=data.get("classes", {}),
            subclasses=data.get("subclasses", {}),
            feats=data.get("feats", {}),
            backgrounds=data.get("backgrounds", {}),
            general_principles=data.get("general_principles", {}),
            ai_guidance=data.get("ai_guidance", {}),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "spells": self.spells,
            "magic_items": self.magic_items,
            "races": self.races,
            "classes": self.classes,
            "subclasses": self.subclasses,
            "feats": self.feats,
            "backgrounds": self.backgrounds,
            "general_principles": self.general_principles,
            "ai_guidance": self.ai_guidance,
        }

    def get_section(self, section: str) -> dict:
        """Get a specific section of guidelines."""
        return getattr(self, section, {})

    def get_prompt_for_content_type(self, content_type: str) -> str:
        """Generate an AI prompt for creating a specific content type."""
        prompts = {
            "spell": self._build_spell_prompt(),
            "magic_item": self._build_magic_item_prompt(),
            "item": self._build_magic_item_prompt(),
            "race": self._build_race_prompt(),
            "species": self._build_race_prompt(),
            "class": self._build_class_prompt(),
            "subclass": self._build_subclass_prompt(),
            "feat": self._build_feat_prompt(),
            "background": self._build_background_prompt(),
        }
        return prompts.get(content_type.lower(), self._build_general_prompt())

    def _build_spell_prompt(self) -> str:
        """Build prompt for spell creation."""
        s = self.spells
        lines = [
            "## Spell Creation Guidelines",
            "",
            s.get("description", ""),
            "",
            "### Damage Benchmarks by Level",
        ]

        benchmarks = s.get("damage_benchmarks", {})
        for level, damage in benchmarks.items():
            if level != "description":
                lines.append(f"- {level}: {damage}")

        lines.extend([
            "",
            "### AoE Adjustment",
            s.get("aoe_adjustment", ""),
            "",
            "### Concentration Rules",
            s.get("concentration_rules", ""),
            "",
            "### Red Flags to Avoid",
        ])

        for flag in s.get("red_flags", []):
            lines.append(f"- {flag}")

        lines.extend([
            "",
            "### Design Tips",
        ])
        for tip in s.get("design_tips", []):
            lines.append(f"- {tip}")

        return "\n".join(lines)

    def _build_magic_item_prompt(self) -> str:
        """Build prompt for magic item creation."""
        m = self.magic_items
        lines = [
            "## Magic Item Creation Guidelines",
            "",
            m.get("description", ""),
            "",
            "### Rarity Guidelines",
        ]

        for rarity, info in m.get("rarity_guidelines", {}).items():
            if isinstance(info, dict):
                lines.append(f"\n**{rarity.title()}** (Character Level {info.get('character_level', '?')}+)")
                lines.append(f"- Attunement: {info.get('attunement', 'Varies')}")
                for effect in info.get("typical_effects", []):
                    lines.append(f"- {effect}")

        lines.extend([
            "",
            "### Attunement Rules",
            m.get("attunement_rules", ""),
            "",
            "### Red Flags to Avoid",
        ])
        for flag in m.get("red_flags", []):
            lines.append(f"- {flag}")

        lines.extend([
            "",
            "### Design Tips",
        ])
        for tip in m.get("design_tips", []):
            lines.append(f"- {tip}")

        return "\n".join(lines)

    def _build_race_prompt(self) -> str:
        """Build prompt for race/species creation."""
        r = self.races
        lines = [
            "## Race/Species Creation Guidelines",
            "",
            r.get("description", ""),
            "",
            "### Trait Budget",
            r.get("trait_budget", {}).get("description", ""),
            "",
            "### Common Traits",
        ]

        for trait in r.get("common_traits", []):
            lines.append(f"- {trait}")

        lines.extend([
            "",
            "### Ability Scores by Ruleset",
        ])
        for ruleset, rule in r.get("ability_scores", {}).items():
            lines.append(f"- {ruleset}: {rule}")

        lines.extend([
            "",
            "### Red Flags to Avoid",
        ])
        for flag in r.get("red_flags", []):
            lines.append(f"- {flag}")

        return "\n".join(lines)

    def _build_class_prompt(self) -> str:
        """Build prompt for class creation."""
        c = self.classes
        lines = [
            "## Class Creation Guidelines",
            "",
            c.get("description", ""),
            "",
            "### Hit Dice by Role",
        ]

        for die, classes in c.get("hit_dice", {}).items():
            lines.append(f"- {die}: {classes}")

        lines.extend([
            "",
            "### Feature Progression",
        ])
        for level, feature in c.get("feature_progression", {}).items():
            lines.append(f"- {level}: {feature}")

        lines.extend([
            "",
            "### Design Pillars",
        ])
        for pillar in c.get("design_pillars", []):
            lines.append(f"- {pillar}")

        lines.extend([
            "",
            "### Red Flags to Avoid",
        ])
        for flag in c.get("red_flags", []):
            lines.append(f"- {flag}")

        return "\n".join(lines)

    def _build_subclass_prompt(self) -> str:
        """Build prompt for subclass creation."""
        s = self.subclasses
        lines = [
            "## Subclass Creation Guidelines",
            "",
            s.get("description", ""),
            "",
            "### Power Budget by Level",
        ]

        for level, budget in s.get("power_budget", {}).items():
            lines.append(f"- {level}: {budget}")

        lines.extend([
            "",
            "### Red Flags to Avoid",
        ])
        for flag in s.get("red_flags", []):
            lines.append(f"- {flag}")

        lines.extend([
            "",
            "### Design Tips",
        ])
        for tip in s.get("design_tips", []):
            lines.append(f"- {tip}")

        return "\n".join(lines)

    def _build_feat_prompt(self) -> str:
        """Build prompt for feat creation."""
        f = self.feats
        lines = [
            "## Feat Creation Guidelines",
            "",
            f.get("description", ""),
            "",
            "### Value Equivalents (compared to +2 ASI)",
        ]

        for item, value in f.get("value_equivalents", {}).items():
            lines.append(f"- {item}: {value}")

        lines.extend([
            "",
            "### Common Structures",
        ])
        for struct, desc in f.get("common_structures", {}).items():
            lines.append(f"- {struct}: {desc}")

        lines.extend([
            "",
            "### Red Flags to Avoid",
        ])
        for flag in f.get("red_flags", []):
            lines.append(f"- {flag}")

        return "\n".join(lines)

    def _build_background_prompt(self) -> str:
        """Build prompt for background creation."""
        b = self.backgrounds
        lines = [
            "## Background Creation Guidelines",
            "",
            b.get("description", ""),
            "",
            "### 2014 Structure",
        ]

        for key, value in b.get("2014_structure", {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "### 2024 Structure",
        ])
        for key, value in b.get("2024_structure", {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "### Feature Guidelines",
            b.get("feature_guidelines", ""),
            "",
            "### Red Flags to Avoid",
        ])
        for flag in b.get("red_flags", []):
            lines.append(f"- {flag}")

        return "\n".join(lines)

    def _build_general_prompt(self) -> str:
        """Build general homebrew guidance prompt."""
        g = self.general_principles
        lines = [
            "## General Homebrew Design Principles",
            "",
            "### Bounded Accuracy",
            g.get("bounded_accuracy", ""),
            "",
            "### Action Economy",
            g.get("action_economy", ""),
            "",
            "### Resource Management",
            g.get("resource_management", ""),
            "",
            "### Party Dynamics",
            g.get("party_dynamics", ""),
            "",
            "### Tier Play",
        ]

        for tier, desc in g.get("tier_play", {}).items():
            lines.append(f"- {tier}: {desc}")

        return "\n".join(lines)

    def get_ai_approach(self) -> str:
        """Get the AI approach guidelines."""
        return self.ai_guidance.get("approach", "")

    def get_ai_tone(self) -> str:
        """Get the AI tone guidelines."""
        return self.ai_guidance.get("tone", "")

    def get_overpowered_response_guidance(self) -> str:
        """Get guidance for when users request overpowered content."""
        return self.ai_guidance.get("when_asked_for_overpowered", {}).get("response", "")


class BalanceGuidelinesManager:
    """Manages loading and saving balance guidelines."""

    def __init__(self):
        self._guidelines: Optional[BalanceGuidelines] = None
        self._default_path = Path(__file__).parent / "balance_guidelines.yaml"
        self._user_path = Path(user_data_dir("dnd-manager", "dnd-manager")) / "balance_guidelines.yaml"

    @property
    def guidelines(self) -> BalanceGuidelines:
        """Get the current guidelines, loading if necessary."""
        if self._guidelines is None:
            self._guidelines = self.load()
        return self._guidelines

    def load(self) -> BalanceGuidelines:
        """Load guidelines from file, with user overrides."""
        # Start with defaults
        guidelines_data = {}

        # Load default guidelines
        if self._default_path.exists():
            with open(self._default_path, "r") as f:
                guidelines_data = yaml.safe_load(f) or {}

        # Load and merge user overrides
        if self._user_path.exists():
            with open(self._user_path, "r") as f:
                user_data = yaml.safe_load(f) or {}
            guidelines_data = self._deep_merge(guidelines_data, user_data)

        self._guidelines = BalanceGuidelines.from_dict(guidelines_data)
        return self._guidelines

    def save_user_overrides(self, overrides: dict) -> Path:
        """Save user overrides to the user config directory."""
        self._user_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing user overrides
        existing = {}
        if self._user_path.exists():
            with open(self._user_path, "r") as f:
                existing = yaml.safe_load(f) or {}

        # Merge new overrides
        merged = self._deep_merge(existing, overrides)

        with open(self._user_path, "w") as f:
            yaml.dump(merged, f, default_flow_style=False, sort_keys=False)

        # Reload guidelines
        self._guidelines = None

        return self._user_path

    def reset_to_defaults(self) -> None:
        """Remove user overrides and reset to defaults."""
        if self._user_path.exists():
            self._user_path.unlink()
        self._guidelines = None

    def get_user_overrides_path(self) -> Path:
        """Get the path to user overrides file."""
        return self._user_path

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries, with override taking precedence."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result


# Global manager instance
_manager: Optional[BalanceGuidelinesManager] = None


def get_balance_guidelines() -> BalanceGuidelines:
    """Get the current balance guidelines."""
    global _manager
    if _manager is None:
        _manager = BalanceGuidelinesManager()
    return _manager.guidelines


def get_guidelines_manager() -> BalanceGuidelinesManager:
    """Get the balance guidelines manager."""
    global _manager
    if _manager is None:
        _manager = BalanceGuidelinesManager()
    return _manager


def get_homebrew_prompt(content_type: str) -> str:
    """Get an AI prompt for creating a specific type of homebrew content.

    Args:
        content_type: Type of content (spell, magic_item, race, class, subclass, feat, background)

    Returns:
        Formatted prompt string with balance guidelines
    """
    guidelines = get_balance_guidelines()
    return guidelines.get_prompt_for_content_type(content_type)
