"""Custom content system for homebrew D&D content.

This module provides a system for users to add their own custom spells,
items, classes, backgrounds, and other content.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any
import yaml

from dnd_manager.data.spells import Spell
from dnd_manager.data.items import Weapon, Armor, Equipment
from dnd_manager.data.classes import ClassFeature
from dnd_manager.data.backgrounds import Background, BackgroundFeature


@dataclass
class ValidationWarning:
    """A validation warning for custom content."""
    content_type: str
    content_name: str
    message: str
    severity: str = "warning"  # "warning", "error"


@dataclass
class CustomSpell:
    """A custom spell definition."""
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    components: str
    duration: str
    description: str
    classes: list[str]
    ritual: bool = False
    concentration: bool = False
    higher_levels: Optional[str] = None
    source: str = "homebrew"
    author: Optional[str] = None
    notes: Optional[str] = None

    def to_spell(self) -> Spell:
        """Convert to a standard Spell object."""
        return Spell(
            name=self.name,
            level=self.level,
            school=self.school,
            casting_time=self.casting_time,
            range=self.range,
            components=self.components,
            duration=self.duration,
            description=self.description,
            classes=self.classes,
            ritual=self.ritual,
            concentration=self.concentration,
            higher_levels=self.higher_levels,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "name": self.name,
            "level": self.level,
            "school": self.school,
            "casting_time": self.casting_time,
            "range": self.range,
            "components": self.components,
            "duration": self.duration,
            "description": self.description,
            "classes": self.classes,
            "ritual": self.ritual,
            "concentration": self.concentration,
            "higher_levels": self.higher_levels,
            "source": self.source,
            "author": self.author,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CustomSpell":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            level=data.get("level", 1),
            school=data.get("school", "Evocation"),
            casting_time=data.get("casting_time", "1 action"),
            range=data.get("range", "Self"),
            components=data.get("components", "V, S"),
            duration=data.get("duration", "Instantaneous"),
            description=data.get("description", ""),
            classes=data.get("classes", []),
            ritual=data.get("ritual", False),
            concentration=data.get("concentration", False),
            higher_levels=data.get("higher_levels"),
            source=data.get("source", "homebrew"),
            author=data.get("author"),
            notes=data.get("notes"),
        )


@dataclass
class CustomItem:
    """A custom item definition."""
    name: str
    item_type: str  # "weapon", "armor", "equipment", "wondrous", "potion"
    rarity: str = "common"  # common, uncommon, rare, very rare, legendary, artifact
    description: str = ""
    properties: list[str] = field(default_factory=list)
    requires_attunement: bool = False
    attunement_requirements: Optional[str] = None
    # Weapon-specific
    damage: Optional[str] = None
    damage_type: Optional[str] = None
    weapon_properties: list[str] = field(default_factory=list)
    # Armor-specific
    base_ac: Optional[int] = None
    armor_type: Optional[str] = None
    # Common
    weight: float = 0
    cost: str = "0 gp"
    source: str = "homebrew"
    author: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        result = {
            "name": self.name,
            "item_type": self.item_type,
            "rarity": self.rarity,
            "description": self.description,
            "properties": self.properties,
            "requires_attunement": self.requires_attunement,
            "weight": self.weight,
            "cost": self.cost,
            "source": self.source,
        }
        if self.attunement_requirements:
            result["attunement_requirements"] = self.attunement_requirements
        if self.damage:
            result["damage"] = self.damage
        if self.damage_type:
            result["damage_type"] = self.damage_type
        if self.weapon_properties:
            result["weapon_properties"] = self.weapon_properties
        if self.base_ac is not None:
            result["base_ac"] = self.base_ac
        if self.armor_type:
            result["armor_type"] = self.armor_type
        if self.author:
            result["author"] = self.author
        if self.notes:
            result["notes"] = self.notes
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "CustomItem":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            item_type=data.get("item_type", "equipment"),
            rarity=data.get("rarity", "common"),
            description=data.get("description", ""),
            properties=data.get("properties", []),
            requires_attunement=data.get("requires_attunement", False),
            attunement_requirements=data.get("attunement_requirements"),
            damage=data.get("damage"),
            damage_type=data.get("damage_type"),
            weapon_properties=data.get("weapon_properties", []),
            base_ac=data.get("base_ac"),
            armor_type=data.get("armor_type"),
            weight=data.get("weight", 0),
            cost=data.get("cost", "0 gp"),
            source=data.get("source", "homebrew"),
            author=data.get("author"),
            notes=data.get("notes"),
        )


@dataclass
class CustomFeat:
    """A custom feat definition."""
    name: str
    description: str
    prerequisites: list[str] = field(default_factory=list)
    benefits: list[str] = field(default_factory=list)
    category: str = "general"  # origin, general, epic_boon
    source: str = "homebrew"
    author: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "benefits": self.benefits,
            "category": self.category,
            "source": self.source,
            "author": self.author,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CustomFeat":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            prerequisites=data.get("prerequisites", []),
            benefits=data.get("benefits", []),
            category=data.get("category", "general"),
            source=data.get("source", "homebrew"),
            author=data.get("author"),
            notes=data.get("notes"),
        )


@dataclass
class CustomContent:
    """Container for all custom content."""
    spells: list[CustomSpell] = field(default_factory=list)
    items: list[CustomItem] = field(default_factory=list)
    feats: list[CustomFeat] = field(default_factory=list)
    # Future: classes, subclasses, backgrounds, species

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "spells": [s.to_dict() for s in self.spells],
            "items": [i.to_dict() for i in self.items],
            "feats": [f.to_dict() for f in self.feats],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CustomContent":
        """Create from dictionary."""
        return cls(
            spells=[CustomSpell.from_dict(s) for s in data.get("spells", [])],
            items=[CustomItem.from_dict(i) for i in data.get("items", [])],
            feats=[CustomFeat.from_dict(f) for f in data.get("feats", [])],
        )


class ContentValidator:
    """Validates custom content for balance and correctness."""

    # Typical spell damage by level for comparison
    SPELL_DAMAGE_REFERENCE = {
        0: "1d10",  # Cantrip
        1: "3d10",  # e.g., Burning Hands
        2: "3d8",   # e.g., Scorching Ray
        3: "8d6",   # e.g., Fireball
        4: "7d8",   # e.g., Ice Storm
        5: "8d8",   # e.g., Cone of Cold
        6: "10d6",  # e.g., Chain Lightning
        7: "7d8",   # e.g., Finger of Death
        8: "12d6",  # e.g., Sunburst
        9: "40d6",  # e.g., Meteor Swarm
    }

    def validate_spell(self, spell: CustomSpell) -> list[ValidationWarning]:
        """Validate a custom spell."""
        warnings = []

        # Check level range
        if spell.level < 0 or spell.level > 9:
            warnings.append(ValidationWarning(
                "spell", spell.name,
                f"Spell level {spell.level} is outside valid range (0-9)",
                "error"
            ))

        # Check required fields
        if not spell.name:
            warnings.append(ValidationWarning(
                "spell", spell.name or "Unknown",
                "Spell name is required",
                "error"
            ))

        if not spell.description:
            warnings.append(ValidationWarning(
                "spell", spell.name,
                "Spell description is empty",
                "warning"
            ))

        if not spell.classes:
            warnings.append(ValidationWarning(
                "spell", spell.name,
                "No classes specified for this spell",
                "warning"
            ))

        # Check school
        valid_schools = ["Abjuration", "Conjuration", "Divination", "Enchantment",
                         "Evocation", "Illusion", "Necromancy", "Transmutation"]
        if spell.school not in valid_schools:
            warnings.append(ValidationWarning(
                "spell", spell.name,
                f"Unknown school '{spell.school}'. Valid schools: {', '.join(valid_schools)}",
                "warning"
            ))

        # Check for concentration + instantaneous (likely error)
        if spell.concentration and "Instantaneous" in spell.duration:
            warnings.append(ValidationWarning(
                "spell", spell.name,
                "Spell has concentration but duration is Instantaneous - this is unusual",
                "warning"
            ))

        return warnings

    def validate_item(self, item: CustomItem) -> list[ValidationWarning]:
        """Validate a custom item."""
        warnings = []

        if not item.name:
            warnings.append(ValidationWarning(
                "item", item.name or "Unknown",
                "Item name is required",
                "error"
            ))

        # Check rarity
        valid_rarities = ["common", "uncommon", "rare", "very rare", "legendary", "artifact"]
        if item.rarity.lower() not in valid_rarities:
            warnings.append(ValidationWarning(
                "item", item.name,
                f"Unknown rarity '{item.rarity}'. Valid rarities: {', '.join(valid_rarities)}",
                "warning"
            ))

        # Weapon-specific checks
        if item.item_type == "weapon":
            if not item.damage:
                warnings.append(ValidationWarning(
                    "item", item.name,
                    "Weapon has no damage specified",
                    "warning"
                ))
            if not item.damage_type:
                warnings.append(ValidationWarning(
                    "item", item.name,
                    "Weapon has no damage type specified",
                    "warning"
                ))

        # Armor-specific checks
        if item.item_type == "armor":
            if item.base_ac is None:
                warnings.append(ValidationWarning(
                    "item", item.name,
                    "Armor has no base AC specified",
                    "warning"
                ))

        # Attunement check
        if item.requires_attunement and item.rarity == "common":
            warnings.append(ValidationWarning(
                "item", item.name,
                "Common items typically don't require attunement",
                "warning"
            ))

        return warnings

    def validate_feat(self, feat: CustomFeat) -> list[ValidationWarning]:
        """Validate a custom feat."""
        warnings = []

        if not feat.name:
            warnings.append(ValidationWarning(
                "feat", feat.name or "Unknown",
                "Feat name is required",
                "error"
            ))

        if not feat.description and not feat.benefits:
            warnings.append(ValidationWarning(
                "feat", feat.name,
                "Feat has no description or benefits",
                "warning"
            ))

        # Check category
        valid_categories = ["origin", "general", "epic_boon", "fighting_style"]
        if feat.category not in valid_categories:
            warnings.append(ValidationWarning(
                "feat", feat.name,
                f"Unknown category '{feat.category}'. Valid categories: {', '.join(valid_categories)}",
                "warning"
            ))

        return warnings

    def validate_all(self, content: CustomContent) -> list[ValidationWarning]:
        """Validate all custom content."""
        warnings = []
        for spell in content.spells:
            warnings.extend(self.validate_spell(spell))
        for item in content.items:
            warnings.extend(self.validate_item(item))
        for feat in content.feats:
            warnings.extend(self.validate_feat(feat))
        return warnings


class CustomContentStore:
    """Manages loading, saving, and accessing custom content."""

    def __init__(self, content_dir: Path):
        self.content_dir = content_dir
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self._content: Optional[CustomContent] = None
        self._validator = ContentValidator()

    @property
    def content(self) -> CustomContent:
        """Get the loaded custom content, loading if necessary."""
        if self._content is None:
            self._content = self.load_all()
        return self._content

    def load_all(self) -> CustomContent:
        """Load all custom content from YAML files."""
        combined = CustomContent()

        for yaml_file in self.content_dir.glob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
                if data:
                    file_content = CustomContent.from_dict(data)
                    combined.spells.extend(file_content.spells)
                    combined.items.extend(file_content.items)
                    combined.feats.extend(file_content.feats)
            except Exception as e:
                print(f"Warning: Failed to load {yaml_file}: {e}")

        self._content = combined
        return combined

    def save(self, filename: str, content: CustomContent) -> Path:
        """Save custom content to a YAML file."""
        filepath = self.content_dir / filename
        with open(filepath, "w") as f:
            yaml.dump(content.to_dict(), f, default_flow_style=False, sort_keys=False)
        return filepath

    def validate(self) -> list[ValidationWarning]:
        """Validate all loaded custom content."""
        return self._validator.validate_all(self.content)

    def add_spell(self, spell: CustomSpell) -> list[ValidationWarning]:
        """Add a custom spell and validate it."""
        warnings = self._validator.validate_spell(spell)
        if not any(w.severity == "error" for w in warnings):
            self.content.spells.append(spell)
        return warnings

    def add_item(self, item: CustomItem) -> list[ValidationWarning]:
        """Add a custom item and validate it."""
        warnings = self._validator.validate_item(item)
        if not any(w.severity == "error" for w in warnings):
            self.content.items.append(item)
        return warnings

    def add_feat(self, feat: CustomFeat) -> list[ValidationWarning]:
        """Add a custom feat and validate it."""
        warnings = self._validator.validate_feat(feat)
        if not any(w.severity == "error" for w in warnings):
            self.content.feats.append(feat)
        return warnings

    def get_spell(self, name: str) -> Optional[CustomSpell]:
        """Get a custom spell by name."""
        for spell in self.content.spells:
            if spell.name.lower() == name.lower():
                return spell
        return None

    def get_item(self, name: str) -> Optional[CustomItem]:
        """Get a custom item by name."""
        for item in self.content.items:
            if item.name.lower() == name.lower():
                return item
        return None

    def get_feat(self, name: str) -> Optional[CustomFeat]:
        """Get a custom feat by name."""
        for feat in self.content.feats:
            if feat.name.lower() == name.lower():
                return feat
        return None

    def search_spells(self, query: str) -> list[CustomSpell]:
        """Search custom spells by name or description."""
        query_lower = query.lower()
        return [
            s for s in self.content.spells
            if query_lower in s.name.lower() or query_lower in s.description.lower()
        ]

    def search_items(self, query: str) -> list[CustomItem]:
        """Search custom items by name or description."""
        query_lower = query.lower()
        return [
            i for i in self.content.items
            if query_lower in i.name.lower() or query_lower in i.description.lower()
        ]

    def export_to_yaml(self, output_path: Path) -> Path:
        """Export all custom content to a single YAML file."""
        with open(output_path, "w") as f:
            yaml.dump(self.content.to_dict(), f, default_flow_style=False, sort_keys=False)
        return output_path

    def import_from_yaml(self, input_path: Path) -> tuple[CustomContent, list[ValidationWarning]]:
        """Import custom content from a YAML file."""
        with open(input_path) as f:
            data = yaml.safe_load(f)

        imported = CustomContent.from_dict(data)
        warnings = self._validator.validate_all(imported)

        # Only add content without errors
        for spell in imported.spells:
            spell_warnings = self._validator.validate_spell(spell)
            if not any(w.severity == "error" for w in spell_warnings):
                self.content.spells.append(spell)

        for item in imported.items:
            item_warnings = self._validator.validate_item(item)
            if not any(w.severity == "error" for w in item_warnings):
                self.content.items.append(item)

        for feat in imported.feats:
            feat_warnings = self._validator.validate_feat(feat)
            if not any(w.severity == "error" for w in feat_warnings):
                self.content.feats.append(feat)

        return imported, warnings


def get_custom_content_store() -> CustomContentStore:
    """Get the default custom content store."""
    from platformdirs import user_data_dir
    content_dir = Path(user_data_dir("dnd-manager", "dnd-manager")) / "custom"
    return CustomContentStore(content_dir)
