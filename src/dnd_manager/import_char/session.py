"""Import session state management for character import workflow."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json
import logging

from dnd_manager.models.character import Character, RulesetId

logger = logging.getLogger(__name__)


@dataclass
class ParsedCharacterData:
    """Structured data extracted from a character sheet.

    All fields are Optional since AI parsing may not successfully extract everything.
    The confidence dict tracks how confident the AI was in each extraction.
    """

    # Identity
    name: Optional[str] = None
    player_name: Optional[str] = None
    class_name: Optional[str] = None
    subclass: Optional[str] = None
    level: Optional[int] = None
    species: Optional[str] = None
    subspecies: Optional[str] = None
    background: Optional[str] = None
    alignment: Optional[str] = None

    # Ability Scores
    strength: Optional[int] = None
    dexterity: Optional[int] = None
    constitution: Optional[int] = None
    intelligence: Optional[int] = None
    wisdom: Optional[int] = None
    charisma: Optional[int] = None

    # Combat Stats
    armor_class: Optional[int] = None
    hit_points_max: Optional[int] = None
    hit_points_current: Optional[int] = None
    speed: Optional[int] = None
    initiative_bonus: Optional[int] = None

    # Proficiencies
    skill_proficiencies: list[str] = field(default_factory=list)
    skill_expertise: list[str] = field(default_factory=list)
    saving_throw_proficiencies: list[str] = field(default_factory=list)
    armor_proficiencies: list[str] = field(default_factory=list)
    weapon_proficiencies: list[str] = field(default_factory=list)
    tool_proficiencies: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)

    # Spellcasting
    spellcasting_ability: Optional[str] = None
    spell_save_dc: Optional[int] = None
    spell_attack_bonus: Optional[int] = None
    cantrips: list[str] = field(default_factory=list)
    spells_known: list[str] = field(default_factory=list)
    spells_prepared: list[str] = field(default_factory=list)
    spell_slots: dict[int, int] = field(default_factory=dict)  # level -> total slots

    # Features
    features: list[dict[str, Any]] = field(default_factory=list)
    # Each feature: {"name": str, "source": str, "description": str}

    # Equipment
    equipment: list[dict[str, Any]] = field(default_factory=list)
    # Each item: {"name": str, "quantity": int, "equipped": bool, "attuned": bool}
    currency: dict[str, int] = field(default_factory=dict)
    # {"pp": 0, "gp": 0, "ep": 0, "sp": 0, "cp": 0}

    # Personality
    personality_traits: Optional[str] = None
    ideals: Optional[str] = None
    bonds: Optional[str] = None
    flaws: Optional[str] = None
    backstory: Optional[str] = None

    # Multiclass (if applicable)
    multiclass: list[dict[str, Any]] = field(default_factory=list)
    # Each entry: {"class_name": str, "subclass": str, "level": int}

    # Confidence scores for each major section (0.0 to 1.0)
    confidence: dict[str, float] = field(default_factory=dict)

    # Raw AI response for debugging
    raw_response: Optional[str] = None

    def get_confidence(self, section: str) -> float:
        """Get confidence score for a section, defaulting to 0.5 if unknown."""
        return self.confidence.get(section, 0.5)

    def get_low_confidence_fields(self, threshold: float = 0.7) -> list[str]:
        """Get list of fields with confidence below threshold."""
        return [k for k, v in self.confidence.items() if v < threshold]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "player_name": self.player_name,
            "class_name": self.class_name,
            "subclass": self.subclass,
            "level": self.level,
            "species": self.species,
            "subspecies": self.subspecies,
            "background": self.background,
            "alignment": self.alignment,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
            "armor_class": self.armor_class,
            "hit_points_max": self.hit_points_max,
            "hit_points_current": self.hit_points_current,
            "speed": self.speed,
            "initiative_bonus": self.initiative_bonus,
            "skill_proficiencies": self.skill_proficiencies,
            "skill_expertise": self.skill_expertise,
            "saving_throw_proficiencies": self.saving_throw_proficiencies,
            "armor_proficiencies": self.armor_proficiencies,
            "weapon_proficiencies": self.weapon_proficiencies,
            "tool_proficiencies": self.tool_proficiencies,
            "languages": self.languages,
            "spellcasting_ability": self.spellcasting_ability,
            "spell_save_dc": self.spell_save_dc,
            "spell_attack_bonus": self.spell_attack_bonus,
            "cantrips": self.cantrips,
            "spells_known": self.spells_known,
            "spells_prepared": self.spells_prepared,
            "spell_slots": self.spell_slots,
            "features": self.features,
            "equipment": self.equipment,
            "currency": self.currency,
            "personality_traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws,
            "backstory": self.backstory,
            "multiclass": self.multiclass,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParsedCharacterData":
        """Create from dictionary."""
        return cls(
            name=data.get("name"),
            player_name=data.get("player_name"),
            class_name=data.get("class_name"),
            subclass=data.get("subclass"),
            level=data.get("level"),
            species=data.get("species"),
            subspecies=data.get("subspecies"),
            background=data.get("background"),
            alignment=data.get("alignment"),
            strength=data.get("strength"),
            dexterity=data.get("dexterity"),
            constitution=data.get("constitution"),
            intelligence=data.get("intelligence"),
            wisdom=data.get("wisdom"),
            charisma=data.get("charisma"),
            armor_class=data.get("armor_class"),
            hit_points_max=data.get("hit_points_max"),
            hit_points_current=data.get("hit_points_current"),
            speed=data.get("speed"),
            initiative_bonus=data.get("initiative_bonus"),
            skill_proficiencies=data.get("skill_proficiencies", []),
            skill_expertise=data.get("skill_expertise", []),
            saving_throw_proficiencies=data.get("saving_throw_proficiencies", []),
            armor_proficiencies=data.get("armor_proficiencies", []),
            weapon_proficiencies=data.get("weapon_proficiencies", []),
            tool_proficiencies=data.get("tool_proficiencies", []),
            languages=data.get("languages", []),
            spellcasting_ability=data.get("spellcasting_ability"),
            spell_save_dc=data.get("spell_save_dc"),
            spell_attack_bonus=data.get("spell_attack_bonus"),
            cantrips=data.get("cantrips", []),
            spells_known=data.get("spells_known", []),
            spells_prepared=data.get("spells_prepared", []),
            spell_slots=data.get("spell_slots", {}),
            features=data.get("features", []),
            equipment=data.get("equipment", []),
            currency=data.get("currency", {}),
            personality_traits=data.get("personality_traits"),
            ideals=data.get("ideals"),
            bonds=data.get("bonds"),
            flaws=data.get("flaws"),
            backstory=data.get("backstory"),
            multiclass=data.get("multiclass", []),
            confidence=data.get("confidence", {}),
        )


@dataclass
class ImportSession:
    """Holds state for a character import in progress.

    Manages the parsed data, user overrides, and conversion to Character.
    """

    # Source information
    source_file: Path
    source_type: str  # "dndbeyond", "roll20", "generic", "auto"
    ruleset: str = "dnd2024"  # Target ruleset for import

    # Parsed data from AI
    parsed_data: ParsedCharacterData = field(default_factory=ParsedCharacterData)

    # Manual overrides from user review
    manual_overrides: dict[str, Any] = field(default_factory=dict)

    # Session metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    session_id: str = ""

    def __post_init__(self) -> None:
        if not self.session_id:
            import uuid

            self.session_id = str(uuid.uuid4())[:8]

    def get_field(self, field_name: str) -> Any:
        """Get a field value, preferring manual override over parsed data."""
        if field_name in self.manual_overrides:
            return self.manual_overrides[field_name]
        return getattr(self.parsed_data, field_name, None)

    def set_override(self, field_name: str, value: Any) -> None:
        """Set a manual override for a field."""
        self.manual_overrides[field_name] = value
        self.last_modified = datetime.now()

    def clear_override(self, field_name: str) -> None:
        """Remove a manual override, reverting to parsed data."""
        self.manual_overrides.pop(field_name, None)
        self.last_modified = datetime.now()

    def get_review_data(self) -> dict[str, Any]:
        """Get combined data for review wizard display.

        Returns dict with all fields, indicating which are overridden.
        """
        result = self.parsed_data.to_dict()

        # Apply overrides
        for key, value in self.manual_overrides.items():
            result[key] = value

        # Mark which fields are overridden
        result["_overridden"] = list(self.manual_overrides.keys())
        result["_low_confidence"] = self.parsed_data.get_low_confidence_fields()

        return result

    def is_complete(self) -> tuple[bool, list[str]]:
        """Check if import has all required fields.

        Returns:
            Tuple of (is_complete, list_of_missing_fields)
        """
        missing = []

        # Required fields
        if not self.get_field("name"):
            missing.append("name")
        if not self.get_field("class_name"):
            missing.append("class_name")
        if not self.get_field("level"):
            missing.append("level")

        # Ability scores - all 6 required
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            if self.get_field(ability) is None:
                missing.append(ability)

        return (len(missing) == 0, missing)

    def to_character(self) -> Character:
        """Convert import session to a Character model.

        Returns:
            A new Character instance populated with imported data.
        """
        from dnd_manager.models.character import (
            Character,
            CharacterClass,
            CharacterMeta,
            AbilityScores,
            AbilityScore,
            Combat,
            HitPoints,
            Proficiencies,
            Equipment,
            Currency,
            Spellcasting,
            Personality,
            Alignment,
        )
        from dnd_manager.models.abilities import Ability, Skill, SkillProficiency

        # Get values with overrides applied
        name = self.get_field("name") or "Imported Character"
        class_name = self.get_field("class_name") or "Fighter"
        level = self.get_field("level") or 1
        subclass = self.get_field("subclass")

        # Determine ruleset
        ruleset_id = RulesetId.DND_2024
        if self.ruleset == "dnd2014":
            ruleset_id = RulesetId.DND_2014
        elif self.ruleset == "tov":
            ruleset_id = RulesetId.TOV

        # Create primary class
        primary_class = CharacterClass(
            name=class_name,
            level=level,
            subclass=subclass,
        )

        # Create multiclass entries if present
        multiclass = []
        for mc in self.get_field("multiclass") or []:
            multiclass.append(
                CharacterClass(
                    name=mc.get("class_name", ""),
                    level=mc.get("level", 1),
                    subclass=mc.get("subclass"),
                )
            )

        # Create ability scores
        abilities = AbilityScores(
            strength=AbilityScore(base=self.get_field("strength") or 10),
            dexterity=AbilityScore(base=self.get_field("dexterity") or 10),
            constitution=AbilityScore(base=self.get_field("constitution") or 10),
            intelligence=AbilityScore(base=self.get_field("intelligence") or 10),
            wisdom=AbilityScore(base=self.get_field("wisdom") or 10),
            charisma=AbilityScore(base=self.get_field("charisma") or 10),
        )

        # Create combat stats
        hp_max = self.get_field("hit_points_max") or 10
        hp_current = self.get_field("hit_points_current") or hp_max
        combat = Combat(
            armor_class=self.get_field("armor_class") or 10,
            initiative_bonus=self.get_field("initiative_bonus") or 0,
            speed=self.get_field("speed") or 30,
            hit_points=HitPoints(
                maximum=hp_max,
                current=hp_current,
                temporary=0,
            ),
        )

        # Create proficiencies
        skill_profs = {}
        for skill_name in self.get_field("skill_proficiencies") or []:
            try:
                skill = Skill(skill_name.lower().replace(" ", "_"))
                skill_profs[skill] = SkillProficiency.PROFICIENT
            except ValueError:
                logger.warning(f"Unknown skill: {skill_name}")

        for skill_name in self.get_field("skill_expertise") or []:
            try:
                skill = Skill(skill_name.lower().replace(" ", "_"))
                skill_profs[skill] = SkillProficiency.EXPERTISE
            except ValueError:
                logger.warning(f"Unknown skill for expertise: {skill_name}")

        save_profs = []
        for save_name in self.get_field("saving_throw_proficiencies") or []:
            try:
                ability = Ability(save_name.lower())
                save_profs.append(ability)
            except ValueError:
                logger.warning(f"Unknown saving throw: {save_name}")

        proficiencies = Proficiencies(
            skills=skill_profs,
            saving_throws=save_profs,
            armor=self.get_field("armor_proficiencies") or [],
            weapons=self.get_field("weapon_proficiencies") or [],
            tools=self.get_field("tool_proficiencies") or [],
            languages=self.get_field("languages") or ["Common"],
        )

        # Create equipment
        from dnd_manager.models.character import EquipmentItem

        items = []
        for item_data in self.get_field("equipment") or []:
            items.append(
                EquipmentItem(
                    name=item_data.get("name", "Unknown Item"),
                    quantity=item_data.get("quantity", 1),
                    equipped=item_data.get("equipped", False),
                    attuned=item_data.get("attuned", False),
                )
            )

        currency_data = self.get_field("currency") or {}
        equipment = Equipment(
            items=items,
            currency=Currency(
                pp=currency_data.get("pp", 0),
                gp=currency_data.get("gp", 0),
                ep=currency_data.get("ep", 0),
                sp=currency_data.get("sp", 0),
                cp=currency_data.get("cp", 0),
            ),
        )

        # Create spellcasting
        spellcasting_ability = None
        if self.get_field("spellcasting_ability"):
            try:
                spellcasting_ability = Ability(self.get_field("spellcasting_ability").lower())
            except ValueError:
                pass

        from dnd_manager.models.character import SpellSlot

        spell_slots = {}
        for level_str, total in (self.get_field("spell_slots") or {}).items():
            level = int(level_str) if isinstance(level_str, str) else level_str
            spell_slots[level] = SpellSlot(total=total, used=0)

        spellcasting = Spellcasting(
            ability=spellcasting_ability,
            cantrips=self.get_field("cantrips") or [],
            known=self.get_field("spells_known") or [],
            prepared=self.get_field("spells_prepared") or [],
            slots=spell_slots,
        )

        # Create features
        from dnd_manager.models.character import Feature

        features = []
        for feat_data in self.get_field("features") or []:
            features.append(
                Feature(
                    name=feat_data.get("name", "Unknown Feature"),
                    source=feat_data.get("source", "import"),
                    description=feat_data.get("description", ""),
                )
            )

        # Create personality
        personality = Personality(
            traits=self.get_field("personality_traits") or "",
            ideals=self.get_field("ideals") or "",
            bonds=self.get_field("bonds") or "",
            flaws=self.get_field("flaws") or "",
        )

        # Parse alignment
        alignment = Alignment.TRUE_NEUTRAL
        alignment_str = self.get_field("alignment")
        if alignment_str:
            alignment_map = {
                "lawful good": Alignment.LAWFUL_GOOD,
                "neutral good": Alignment.NEUTRAL_GOOD,
                "chaotic good": Alignment.CHAOTIC_GOOD,
                "lawful neutral": Alignment.LAWFUL_NEUTRAL,
                "true neutral": Alignment.TRUE_NEUTRAL,
                "neutral": Alignment.TRUE_NEUTRAL,
                "chaotic neutral": Alignment.CHAOTIC_NEUTRAL,
                "lawful evil": Alignment.LAWFUL_EVIL,
                "neutral evil": Alignment.NEUTRAL_EVIL,
                "chaotic evil": Alignment.CHAOTIC_EVIL,
            }
            alignment = alignment_map.get(alignment_str.lower(), Alignment.TRUE_NEUTRAL)

        # Create character
        character = Character(
            name=name,
            player=self.get_field("player_name"),
            primary_class=primary_class,
            multiclass=multiclass,
            species=self.get_field("species"),
            subspecies=self.get_field("subspecies"),
            background=self.get_field("background"),
            alignment=alignment,
            abilities=abilities,
            combat=combat,
            proficiencies=proficiencies,
            equipment=equipment,
            spellcasting=spellcasting,
            features=features,
            personality=personality,
            backstory=self.get_field("backstory") or "",
            meta=CharacterMeta(
                ruleset=ruleset_id,
                created=datetime.now(),
                modified=datetime.now(),
            ),
        )

        return character

    def save_partial(self, path: Path) -> None:
        """Save partial import for later resumption."""
        import yaml

        data = {
            "session_id": self.session_id,
            "source_file": str(self.source_file),
            "source_type": self.source_type,
            "ruleset": self.ruleset,
            "parsed_data": self.parsed_data.to_dict(),
            "manual_overrides": self.manual_overrides,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
        }

        with open(path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False)

    @classmethod
    def load_partial(cls, path: Path) -> "ImportSession":
        """Load a partial import session."""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        session = cls(
            source_file=Path(data["source_file"]),
            source_type=data["source_type"],
            ruleset=data.get("ruleset", "dnd2024"),
            parsed_data=ParsedCharacterData.from_dict(data["parsed_data"]),
            manual_overrides=data.get("manual_overrides", {}),
            session_id=data["session_id"],
        )
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.last_modified = datetime.fromisoformat(data["last_modified"])

        return session
