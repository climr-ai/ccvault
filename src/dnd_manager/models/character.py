"""Character model for D&D 5e character management."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field, computed_field

from dnd_manager.models.abilities import (
    Ability,
    AbilityScores,
    Skill,
    SkillProficiency,
    SKILL_ABILITY_MAP,
    calculate_skill_modifier,
    get_proficiency_bonus,
)

if TYPE_CHECKING:
    from dnd_manager.rulesets.base import Ruleset as RulesetBase


class RulesetId(str, Enum):
    """Supported ruleset identifiers."""

    DND_2014 = "dnd2014"
    DND_2024 = "dnd2024"
    TALES_OF_VALIANT = "tov"


class Alignment(str, Enum):
    """Character alignments."""

    LAWFUL_GOOD = "lawful_good"
    NEUTRAL_GOOD = "neutral_good"
    CHAOTIC_GOOD = "chaotic_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    TRUE_NEUTRAL = "true_neutral"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_EVIL = "chaotic_evil"
    UNALIGNED = "unaligned"

    @property
    def display_name(self) -> str:
        """Return human-readable name."""
        return self.value.replace("_", " ").title()


class CharacterMeta(BaseModel):
    """Metadata about the character file."""

    version: str = Field(default="1.0", description="Schema version")
    ruleset: RulesetId = Field(default=RulesetId.DND_2024, description="Active ruleset")
    created: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
    sync_id: Optional[str] = Field(default=None, description="Backend sync identifier")


class CharacterClass(BaseModel):
    """A character's class and level."""

    name: str = Field(description="Class name (e.g., 'Wizard', 'Fighter')")
    subclass: Optional[str] = Field(default=None, description="Subclass name")
    level: int = Field(default=1, ge=1, le=20)


class HitPoints(BaseModel):
    """Current hit point status."""

    maximum: int = Field(default=1, ge=1)
    current: int = Field(default=1)
    temporary: int = Field(default=0, ge=0)

    @property
    def effective(self) -> int:
        """Current + temporary HP."""
        return self.current + self.temporary

    @property
    def is_bloodied(self) -> bool:
        """Below half max HP."""
        return self.current <= self.maximum // 2

    @property
    def is_unconscious(self) -> bool:
        """At 0 HP."""
        return self.current <= 0


class HitDice(BaseModel):
    """Hit dice tracking for a single die type."""

    total: int = Field(default=1, ge=1)
    remaining: int = Field(default=1, ge=0)
    die: str = Field(default="d8", pattern=r"^d\d+$")

    @property
    def die_size(self) -> int:
        """Extract numeric die size."""
        return int(self.die[1:])


class HitDicePool(BaseModel):
    """Hit dice tracking for multiclass characters.

    Tracks hit dice by die type, allowing proper multiclass support.
    For example, a Fighter 5/Wizard 3 would have:
    - pools["d10"] = HitDice(total=5, remaining=5, die="d10")
    - pools["d6"] = HitDice(total=3, remaining=3, die="d6")
    """

    pools: dict[str, HitDice] = Field(default_factory=dict)

    @property
    def total(self) -> int:
        """Total number of hit dice across all pools."""
        return sum(hd.total for hd in self.pools.values())

    @property
    def remaining(self) -> int:
        """Total remaining hit dice across all pools."""
        return sum(hd.remaining for hd in self.pools.values())

    def add_dice(self, die: str, count: int = 1) -> None:
        """Add hit dice of a specific type.

        Args:
            die: Die type (e.g., "d10", "d8")
            count: Number of dice to add
        """
        if die not in self.pools:
            self.pools[die] = HitDice(total=count, remaining=count, die=die)
        else:
            self.pools[die].total += count
            self.pools[die].remaining += count

    def remove_dice(self, die: str, count: int = 1) -> bool:
        """Remove hit dice of a specific type.

        Args:
            die: Die type (e.g., "d10", "d8")
            count: Number of dice to remove

        Returns:
            True if dice were removed, False if die type not found.
        """
        if die not in self.pools:
            return False

        self.pools[die].total = max(0, self.pools[die].total - count)
        self.pools[die].remaining = min(self.pools[die].remaining, self.pools[die].total)
        if self.pools[die].total == 0:
            del self.pools[die]
        return True

    def spend(self, die: str) -> bool:
        """Spend one hit die of a specific type.

        Args:
            die: Die type to spend

        Returns:
            True if spent successfully, False if none remaining.
        """
        if die in self.pools and self.pools[die].remaining > 0:
            self.pools[die].remaining -= 1
            return True
        return False

    def spend_any(self) -> str | None:
        """Spend one hit die, preferring larger dice.

        Returns:
            The die type spent (e.g., "d10"), or None if none available.
        """
        # Sort by die size descending (d12, d10, d8, d6)
        for die in sorted(self.pools.keys(), key=lambda d: int(d[1:]), reverse=True):
            if self.pools[die].remaining > 0:
                self.pools[die].remaining -= 1
                return die
        return None

    def recover(self, count: int) -> int:
        """Recover hit dice (typically half total on long rest).

        Recovers larger dice first.

        Args:
            count: Number of dice to recover (must be positive)

        Returns:
            Actual number recovered.
        """
        if count <= 0:
            return 0

        recovered = 0
        # Recover larger dice first
        for die in sorted(self.pools.keys(), key=lambda d: int(d[1:]), reverse=True):
            pool = self.pools[die]
            can_recover = min(count - recovered, pool.total - pool.remaining)
            pool.remaining += can_recover
            recovered += can_recover
            if recovered >= count:
                break
        return recovered

    def recover_all(self) -> None:
        """Recover all hit dice."""
        for pool in self.pools.values():
            pool.remaining = pool.total

    def get_display_string(self) -> str:
        """Get a display string like '5d10 + 3d6'."""
        if not self.pools:
            return "None"
        parts = []
        for die in sorted(self.pools.keys(), key=lambda d: int(d[1:]), reverse=True):
            pool = self.pools[die]
            parts.append(f"{pool.remaining}/{pool.total}{die}")
        return " + ".join(parts)

    @classmethod
    def from_single(cls, hit_dice: HitDice) -> "HitDicePool":
        """Create a pool from a single HitDice (for migration)."""
        pool = cls()
        if hit_dice.total > 0:
            pool.pools[hit_dice.die] = HitDice(
                total=hit_dice.total,
                remaining=hit_dice.remaining,
                die=hit_dice.die
            )
        return pool

    def to_single(self) -> HitDice:
        """Convert to single HitDice (uses largest die type)."""
        if not self.pools:
            return HitDice()
        # Use the largest die type for display
        largest_die = max(self.pools.keys(), key=lambda d: int(d[1:]))
        return HitDice(
            total=self.total,
            remaining=self.remaining,
            die=largest_die
        )


class DeathSaves(BaseModel):
    """Death saving throw tracking."""

    successes: int = Field(default=0, ge=0, le=3)
    failures: int = Field(default=0, ge=0, le=3)

    @property
    def is_stable(self) -> bool:
        """Three successes = stable."""
        return self.successes >= 3

    @property
    def is_dead(self) -> bool:
        """Three failures = dead."""
        return self.failures >= 3

    def reset(self) -> None:
        """Reset death saves (when healed or stabilized)."""
        self.successes = 0
        self.failures = 0


class CustomStat(BaseModel):
    """A custom stat for campaign-specific tracking (Luck, Renown, Piety, etc.)."""

    name: str = Field(description="Name of the custom stat (e.g., 'Luck', 'Renown', 'Piety')")
    value: int = Field(default=0, description="Current value of the stat")
    min_value: Optional[int] = Field(default=None, description="Minimum allowed value (None = no limit)")
    max_value: Optional[int] = Field(default=None, description="Maximum allowed value (None = no limit)")
    description: Optional[str] = Field(default=None, description="Description of what this stat represents")

    def adjust(self, amount: int) -> int:
        """Adjust the stat value, respecting min/max limits. Returns new value."""
        new_value = self.value + amount
        if self.min_value is not None:
            new_value = max(self.min_value, new_value)
        if self.max_value is not None:
            new_value = min(self.max_value, new_value)
        self.value = new_value
        return self.value


# Common custom stat templates
CUSTOM_STAT_TEMPLATES = {
    "luck": CustomStat(name="Luck", value=0, min_value=0, max_value=20, description="Points of luck that can be spent for rerolls"),
    "renown": CustomStat(name="Renown", value=0, min_value=0, description="Standing with factions or organizations"),
    "piety": CustomStat(name="Piety", value=0, description="Favor with a deity or divine force"),
    "sanity": CustomStat(name="Sanity", value=100, min_value=0, max_value=100, description="Mental stability"),
    "honor": CustomStat(name="Honor", value=0, description="Personal honor and reputation"),
    "infamy": CustomStat(name="Infamy", value=0, min_value=0, description="Notoriety for villainous deeds"),
    "inspiration": CustomStat(name="Inspiration Points", value=0, min_value=0, max_value=5, description="Points that can be spent for advantage"),
}


class StatBonus(BaseModel):
    """A bonus to an ability score from a specific source.

    Used to track bonuses from magic items, spells, blessings, and other effects.
    """

    source: str = Field(description="Source of the bonus (e.g., 'Gauntlets of Ogre Power', 'Enhance Ability')")
    ability: str = Field(description="The ability affected (strength, dexterity, etc.)")
    bonus: int = Field(default=0, description="The bonus amount (+2, +4, etc.)")
    is_override: bool = Field(default=False, description="If True, sets score to this value instead of adding")
    override_value: Optional[int] = Field(default=None, description="Value to set if is_override is True")
    temporary: bool = Field(default=False, description="If True, this is a temporary effect (spell, etc.)")
    duration: Optional[str] = Field(default=None, description="Duration description (e.g., '1 hour', 'until long rest')")
    notes: Optional[str] = Field(default=None, description="Additional notes about this bonus")


class Combat(BaseModel):
    """Combat-related stats."""

    armor_class: int = Field(default=10, ge=1)
    armor_class_bonus: int = Field(default=0)
    initiative_bonus: int = Field(default=0)
    speed: int = Field(default=30, ge=0)
    speed_bonus: int = Field(default=0)
    hit_points: HitPoints = Field(default_factory=HitPoints)
    hit_dice: HitDice = Field(default_factory=HitDice)
    # Multiclass hit dice pool - used when character is multiclassed
    hit_dice_pool: Optional[HitDicePool] = Field(default=None)
    death_saves: DeathSaves = Field(default_factory=DeathSaves)

    @property
    def total_ac(self) -> int:
        """Total armor class with bonuses."""
        return self.armor_class + self.armor_class_bonus

    @property
    def total_speed(self) -> int:
        """Total speed with bonuses."""
        return self.speed + self.speed_bonus

    def get_hit_dice_display(self) -> str:
        """Get display string for hit dice (uses pool if available)."""
        if self.hit_dice_pool and self.hit_dice_pool.pools:
            return self.hit_dice_pool.get_display_string()
        return f"{self.hit_dice.remaining}/{self.hit_dice.total}{self.hit_dice.die}"

    def ensure_hit_dice_pool(self) -> HitDicePool:
        """Ensure hit_dice_pool exists, creating from hit_dice if needed."""
        if self.hit_dice_pool is None:
            self.hit_dice_pool = HitDicePool.from_single(self.hit_dice)
        return self.hit_dice_pool


class Proficiencies(BaseModel):
    """Character proficiencies."""

    skills: dict[Skill, SkillProficiency] = Field(default_factory=dict)
    saving_throws: list[Ability] = Field(default_factory=list)
    weapons: list[str] = Field(default_factory=list)
    armor: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=lambda: ["Common"])

    def get_skill_proficiency(self, skill: Skill) -> SkillProficiency:
        """Get proficiency level for a skill."""
        return self.skills.get(skill, SkillProficiency.NONE)

    def is_proficient_save(self, ability: Ability) -> bool:
        """Check if proficient in a saving throw."""
        return ability in self.saving_throws


class SpellSlot(BaseModel):
    """Spell slot tracking for a single level."""

    total: int = Field(default=0, ge=0)
    used: int = Field(default=0, ge=0)

    @property
    def remaining(self) -> int:
        """Remaining spell slots."""
        return max(0, self.total - self.used)

    def use(self) -> bool:
        """Use a slot. Returns True if successful."""
        if self.remaining > 0:
            self.used += 1
            return True
        return False

    def restore(self, count: int = 1) -> None:
        """Restore spell slots."""
        self.used = max(0, self.used - count)

    def restore_all(self) -> None:
        """Restore all spell slots."""
        self.used = 0


class Spellcasting(BaseModel):
    """Spellcasting information."""

    ability: Optional[Ability] = Field(default=None, description="Spellcasting ability")
    slots: dict[int, SpellSlot] = Field(
        default_factory=dict, description="Spell slots by level (1-9)"
    )
    cantrips: list[str] = Field(default_factory=list)
    known: list[str] = Field(default_factory=list, description="Spells known")
    prepared: list[str] = Field(default_factory=list, description="Currently prepared spells")

    def get_spell_save_dc(self, ability_modifier: int, proficiency_bonus: int) -> int:
        """Calculate spell save DC."""
        return 8 + ability_modifier + proficiency_bonus

    def get_spell_attack_bonus(self, ability_modifier: int, proficiency_bonus: int) -> int:
        """Calculate spell attack bonus."""
        return ability_modifier + proficiency_bonus


class Currency(BaseModel):
    """Currency tracking."""

    cp: int = Field(default=0, ge=0, description="Copper pieces")
    sp: int = Field(default=0, ge=0, description="Silver pieces")
    ep: int = Field(default=0, ge=0, description="Electrum pieces")
    gp: int = Field(default=0, ge=0, description="Gold pieces")
    pp: int = Field(default=0, ge=0, description="Platinum pieces")

    @property
    def total_gp(self) -> float:
        """Total value in gold pieces."""
        return (self.cp / 100) + (self.sp / 10) + (self.ep / 2) + self.gp + (self.pp * 10)


class InventoryItem(BaseModel):
    """An item in the character's inventory."""

    name: str
    quantity: int = Field(default=1, ge=1)
    weight: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None)
    equipped: bool = Field(default=False)
    attuned: bool = Field(default=False)
    custom_id: Optional[str] = Field(default=None, description="Reference to custom item")


class Equipment(BaseModel):
    """Character equipment and inventory."""

    currency: Currency = Field(default_factory=Currency)
    items: list[InventoryItem] = Field(default_factory=list)

    @property
    def attuned_count(self) -> int:
        """Count of attuned items (max 3 typically)."""
        return sum(1 for item in self.items if item.attuned)

    @property
    def total_weight(self) -> float:
        """Total inventory weight."""
        return sum((item.weight or 0) * item.quantity for item in self.items)


class Feature(BaseModel):
    """A character feature, trait, or ability."""

    name: str
    source: str = Field(description="Where this feature comes from (class, race, feat, etc.)")
    description: str = Field(default="")
    uses: Optional[int] = Field(default=None, description="Number of uses if limited")
    used: int = Field(default=0, ge=0)
    recharge: Optional[str] = Field(default=None, description="When it recharges (short rest, etc.)")


class Personality(BaseModel):
    """Character personality traits."""

    traits: list[str] = Field(default_factory=list)
    ideals: list[str] = Field(default_factory=list)
    bonds: list[str] = Field(default_factory=list)
    flaws: list[str] = Field(default_factory=list)


class Note(BaseModel):
    """A character note."""

    title: str
    content: str
    created: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)


class AIContext(BaseModel):
    """Context hints for AI assistance."""

    playstyle: Optional[str] = Field(default=None, description="How the character is played")
    campaign_notes: Optional[str] = Field(default=None, description="Campaign context")
    relationships: list[str] = Field(default_factory=list, description="Important NPCs/PCs")
    custom_rules: list[str] = Field(default_factory=list, description="Homebrew rules in effect")


class Character(BaseModel):
    """Complete D&D character model."""

    # Metadata
    meta: CharacterMeta = Field(default_factory=CharacterMeta)

    # Identity
    name: str = Field(default="New Character")
    player: Optional[str] = Field(default=None)

    # Class information
    primary_class: CharacterClass = Field(default_factory=lambda: CharacterClass(name="Fighter"))
    multiclass: list[CharacterClass] = Field(default_factory=list)

    # Species/Race/Lineage (terminology varies by ruleset)
    species: Optional[str] = Field(default=None)
    subspecies: Optional[str] = Field(default=None)  # Subspecies, heritage, etc.
    background: Optional[str] = Field(default=None)
    alignment: Alignment = Field(default=Alignment.TRUE_NEUTRAL)

    # Core stats
    abilities: AbilityScores = Field(default_factory=AbilityScores)
    combat: Combat = Field(default_factory=Combat)
    proficiencies: Proficiencies = Field(default_factory=Proficiencies)

    # Features
    features: list[Feature] = Field(default_factory=list)

    # Spellcasting
    spellcasting: Spellcasting = Field(default_factory=Spellcasting)

    # Equipment
    equipment: Equipment = Field(default_factory=Equipment)

    # Personality & Story
    personality: Personality = Field(default_factory=Personality)
    backstory: str = Field(default="")
    notes: list[Note] = Field(default_factory=list)

    # AI assistance context
    ai_context: AIContext = Field(default_factory=AIContext)

    # Custom content references
    custom_items: list[str] = Field(default_factory=list)
    custom_spells: list[str] = Field(default_factory=list)
    custom_features: list[str] = Field(default_factory=list)

    # Custom stats (Luck, Renown, Piety, etc.)
    custom_stats: list[CustomStat] = Field(default_factory=list)

    # Stat bonuses from various sources (magic items, spells, etc.)
    stat_bonuses: list[StatBonus] = Field(default_factory=list)

    @computed_field
    @property
    def total_level(self) -> int:
        """Total character level across all classes."""
        return self.primary_class.level + sum(c.level for c in self.multiclass)

    @computed_field
    @property
    def proficiency_bonus(self) -> int:
        """Proficiency bonus based on total level."""
        return get_proficiency_bonus(self.total_level)

    def get_skill_modifier(self, skill: Skill) -> int:
        """Calculate modifier for a skill check."""
        ability = SKILL_ABILITY_MAP[skill]
        ability_mod = self.abilities.get_modifier(ability)
        proficiency = self.proficiencies.get_skill_proficiency(skill)
        return calculate_skill_modifier(ability_mod, self.proficiency_bonus, proficiency)

    def get_save_modifier(self, ability: Ability) -> int:
        """Calculate modifier for a saving throw."""
        ability_mod = self.abilities.get_modifier(ability)
        if self.proficiencies.is_proficient_save(ability):
            return ability_mod + self.proficiency_bonus
        return ability_mod

    def get_initiative(self) -> int:
        """Calculate initiative modifier."""
        dex_mod = self.abilities.get_modifier(Ability.DEXTERITY)
        return dex_mod + self.combat.initiative_bonus

    def get_passive_perception(self) -> int:
        """Calculate passive perception."""
        return 10 + self.get_skill_modifier(Skill.PERCEPTION)

    def get_spell_save_dc(self) -> Optional[int]:
        """Calculate spell save DC if character can cast spells."""
        if self.spellcasting.ability is None:
            return None
        ability_mod = self.abilities.get_modifier(self.spellcasting.ability)
        return self.spellcasting.get_spell_save_dc(ability_mod, self.proficiency_bonus)

    def get_spell_attack_bonus(self) -> Optional[int]:
        """Calculate spell attack bonus if character can cast spells."""
        if self.spellcasting.ability is None:
            return None
        ability_mod = self.abilities.get_modifier(self.spellcasting.ability)
        return self.spellcasting.get_spell_attack_bonus(ability_mod, self.proficiency_bonus)

    def update_modified(self) -> None:
        """Update the modified timestamp."""
        self.meta.modified = datetime.now()

    def take_damage(self, amount: int) -> None:
        """Apply damage to the character."""
        hp = self.combat.hit_points
        # Damage temp HP first
        if hp.temporary > 0:
            absorbed = min(hp.temporary, amount)
            hp.temporary -= absorbed
            amount -= absorbed
        # Then real HP
        hp.current = max(0, hp.current - amount)
        self.update_modified()

    def heal(self, amount: int) -> None:
        """Heal the character."""
        hp = self.combat.hit_points
        hp.current = min(hp.maximum, hp.current + amount)
        # Reset death saves when healed from 0
        if hp.current > 0:
            self.combat.death_saves.reset()
        self.update_modified()

    def short_rest(self) -> None:
        """Apply short rest effects.

        Note: Per D&D rules, short rests do NOT restore hit dice.
        Hit dice are spent during short rest to heal (handled in UI).
        Hit dice are only recovered during long rests.
        """
        # Restore short-rest features
        for feature in self.features:
            if feature.uses and feature.recharge in ("short rest", "short_rest"):
                feature.used = 0

        self.update_modified()

    def long_rest(self) -> None:
        """Apply long rest effects."""
        hp = self.combat.hit_points
        hd = self.combat.hit_dice
        pool = self.combat.hit_dice_pool

        # Restore all HP
        hp.current = hp.maximum
        hp.temporary = 0

        # Restore hit dice (up to half max, minimum 1)
        if pool and pool.pools:
            # Use pool for multiclass
            restore = max(1, pool.total // 2)
            pool.recover(restore)
            # Sync simple hit_dice for backward compat
            self.combat.hit_dice = pool.to_single()
        else:
            # Simple single-class tracking
            restore = max(1, hd.total // 2)
            hd.remaining = min(hd.total, hd.remaining + restore)

        # Restore all spell slots
        for slot in self.spellcasting.slots.values():
            slot.restore_all()

        # Reset death saves
        self.combat.death_saves.reset()

        self.update_modified()

    def get_ruleset(self) -> Optional["RulesetBase"]:
        """Get the ruleset implementation for this character."""
        from dnd_manager.rulesets.base import RulesetRegistry

        return RulesetRegistry.get(self.meta.ruleset.value)

    def get_species_term(self) -> str:
        """Get the terminology for species/race/lineage based on ruleset."""
        ruleset = self.get_ruleset()
        if ruleset:
            return ruleset.species_term
        return "Species"

    def get_subspecies_term(self) -> str:
        """Get the terminology for subspecies/heritage based on ruleset."""
        ruleset = self.get_ruleset()
        if ruleset:
            return ruleset.subspecies_term
        return "Subspecies"

    def get_subclass_level(self, class_name: Optional[str] = None) -> int:
        """Get the level at which subclass is selected for a class."""
        ruleset = self.get_ruleset()
        if not ruleset:
            return 3  # Default
        target_class = class_name or self.primary_class.name
        prog = ruleset.get_subclass_progression(target_class)
        return prog.selection_level

    def has_subclass_available(self, class_name: Optional[str] = None) -> bool:
        """Check if subclass selection is available for a class."""
        target_class = class_name or self.primary_class.name
        # Find the level for this class
        if target_class == self.primary_class.name:
            level = self.primary_class.level
        else:
            mc = next((c for c in self.multiclass if c.name == target_class), None)
            level = mc.level if mc else 1

        return level >= self.get_subclass_level(target_class)

    def calculate_max_hp(self, method: str = "average") -> int:
        """Calculate maximum HP based on class and CON modifier.

        Args:
            method: "average" for fixed HP per level, "max" for max roll each level
        """
        ruleset = self.get_ruleset()
        if not ruleset:
            return 1

        con_mod = self.abilities.get_modifier(Ability.CONSTITUTION)

        # Calculate HP for primary class
        total_hp = ruleset.calculate_hit_points(
            self.primary_class.name,
            self.primary_class.level,
            con_mod,
            method=method,
        )

        # Add HP from multiclass levels (not max at level 1)
        for mc in self.multiclass:
            class_def = ruleset.get_class_definition(mc.name)
            if class_def:
                hit_die = class_def.hit_die
                if method == "average":
                    avg_roll = (hit_die // 2) + 1
                else:
                    avg_roll = hit_die
                total_hp += mc.level * (avg_roll + con_mod)

        return max(1, total_hp)

    def get_expected_spell_slots(self) -> dict[int, int]:
        """Get expected spell slots based on class and level.

        For multiclass characters, uses the combined caster level to look up
        spell slots from the multiclass spellcaster table.
        """
        from dnd_manager.data.classes import MULTICLASS_SPELL_SLOTS

        ruleset = self.get_ruleset()
        if not ruleset:
            return {}

        # If not multiclassed, use single-class table
        if not self.is_multiclass():
            return ruleset.get_spell_slots(self.primary_class.name, self.primary_class.level)

        # For multiclass, calculate combined caster level
        caster_level = self.get_multiclass_caster_level()

        # If no caster levels (e.g., Fighter/Barbarian multiclass), no spell slots
        if caster_level <= 0:
            return {}

        # Look up spell slots from multiclass table
        return MULTICLASS_SPELL_SLOTS.get(caster_level, {})

    def sync_spell_slots(self) -> None:
        """Synchronize spell slot totals with ruleset expectations."""
        expected = self.get_expected_spell_slots()
        for level, total in expected.items():
            if level in self.spellcasting.slots:
                self.spellcasting.slots[level].total = total
            else:
                self.spellcasting.slots[level] = SpellSlot(total=total, used=0)

        # Remove slots for levels we shouldn't have
        to_remove = [lvl for lvl in self.spellcasting.slots if lvl not in expected]
        for lvl in to_remove:
            del self.spellcasting.slots[lvl]

    def sync_hit_dice(self) -> None:
        """Synchronize hit dice with class information.

        For single-class characters, uses simple hit_dice tracking.
        For multiclass characters, uses hit_dice_pool to track by die type.
        """
        ruleset = self.get_ruleset()
        if not ruleset:
            return

        if self.is_multiclass():
            # Multiclass: build hit dice pool from all classes
            old_remaining = (
                self.combat.hit_dice_pool.remaining
                if self.combat.hit_dice_pool
                else self.combat.hit_dice.remaining
            )

            pool = HitDicePool()

            # Add primary class hit dice
            primary_def = ruleset.get_class_definition(self.primary_class.name)
            if primary_def:
                die = f"d{primary_def.hit_die}"
                pool.add_dice(die, self.primary_class.level)

            # Add multiclass hit dice
            for mc in self.multiclass:
                mc_def = ruleset.get_class_definition(mc.name)
                if mc_def:
                    die = f"d{mc_def.hit_die}"
                    pool.add_dice(die, mc.level)

            # Preserve remaining dice (proportionally if total changed)
            new_total = pool.total
            if new_total > 0:
                # Distribute remaining across pools proportionally
                if old_remaining >= new_total:
                    pool.recover_all()
                else:
                    # Set remaining to match old total, then cap at new totals
                    remaining_to_set = old_remaining
                    for die in sorted(pool.pools.keys(), key=lambda d: int(d[1:]), reverse=True):
                        p = pool.pools[die]
                        can_set = min(remaining_to_set, p.total)
                        p.remaining = can_set
                        remaining_to_set -= can_set

            self.combat.hit_dice_pool = pool

            # Also update simple hit_dice for backward compatibility display
            self.combat.hit_dice = pool.to_single()
        else:
            # Single class: use simple tracking
            class_def = ruleset.get_class_definition(self.primary_class.name)
            if class_def:
                self.combat.hit_dice.total = self.total_level
                self.combat.hit_dice.die = f"d{class_def.hit_die}"
                self.combat.hit_dice.remaining = min(
                    self.combat.hit_dice.remaining,
                    self.combat.hit_dice.total,
                )
                # Clear pool for single-class characters
                self.combat.hit_dice_pool = None

    def sync_with_ruleset(self, recalc_hp: bool = True) -> None:
        """Synchronize character with ruleset rules.

        Args:
            recalc_hp: Whether to recalculate max HP (use False if you want to preserve custom HP)
        """
        self.sync_spell_slots()
        self.sync_hit_dice()

        if recalc_hp:
            new_max = self.calculate_max_hp()
            # Adjust current HP proportionally if max changed
            old_max = self.combat.hit_points.maximum
            if old_max > 0 and new_max != old_max:
                ratio = self.combat.hit_points.current / old_max
                self.combat.hit_points.current = max(1, int(new_max * ratio))
            self.combat.hit_points.maximum = new_max

        self.update_modified()

    def get_available_classes(self) -> list[str]:
        """Get list of available classes for this ruleset."""
        ruleset = self.get_ruleset()
        if ruleset:
            return ruleset.get_available_classes()
        return []

    def get_available_species(self) -> list[str]:
        """Get list of available species/races/lineages for this ruleset."""
        ruleset = self.get_ruleset()
        if ruleset:
            return ruleset.get_available_species()
        return []

    def get_available_backgrounds(self) -> list[str]:
        """Get list of available backgrounds for this ruleset."""
        ruleset = self.get_ruleset()
        if ruleset:
            return ruleset.get_available_backgrounds()
        return []

    def get_asi_levels(self) -> list[int]:
        """Get levels where ASI/feat choices are available."""
        ruleset = self.get_ruleset()
        if ruleset:
            return ruleset.get_asi_levels()
        return [4, 8, 12, 16, 19]

    def can_multiclass_into(self, class_name: str, enforce: bool = True) -> tuple[bool, str]:
        """Check if character meets multiclass requirements for a class.

        Multiclassing requires meeting the ability score prerequisites for BOTH:
        1. Your current class(es) - to multiclass OUT
        2. The target class - to multiclass INTO

        Args:
            class_name: The class to potentially multiclass into
            enforce: If False, returns success but with informational message

        Returns:
            Tuple of (can_multiclass, reason)
        """
        from dnd_manager.data.classes import (
            MULTICLASS_REQUIREMENTS,
            MULTICLASS_ALT_REQUIREMENTS,
        )

        if not enforce:
            return True, "Multiclass requirements not enforced"

        # Check total level limit
        if self.total_level >= 20:
            return False, "Character is already at maximum level (20)"

        # Check if already have levels in this class (not an error, just informational)
        current_classes = [self.primary_class.name] + [mc.name for mc in self.multiclass]
        if class_name in current_classes:
            return True, f"Already has levels in {class_name} (will continue leveling)"

        # Helper to check if a set of requirements is met
        def check_requirements(reqs: dict[str, int], alt_reqs: Optional[dict[str, int]] = None) -> tuple[bool, str]:
            # Check primary requirements
            for ability, minimum in reqs.items():
                score = getattr(self.abilities, ability, 0)
                if score < minimum:
                    # Check if alt requirements exist and are met
                    if alt_reqs:
                        alt_met = all(
                            getattr(self.abilities, alt_ab, 0) >= alt_min
                            for alt_ab, alt_min in alt_reqs.items()
                        )
                        if alt_met:
                            continue
                    return False, f"Requires {ability.title()} {minimum} (have {score})"
            return True, ""

        # Check requirements to multiclass OUT of current class(es)
        # (current_classes already defined above for duplicate check)
        for current_class in current_classes:
            if current_class not in MULTICLASS_REQUIREMENTS:
                continue  # Unknown class, skip validation

            reqs = MULTICLASS_REQUIREMENTS[current_class]
            alt_reqs = MULTICLASS_ALT_REQUIREMENTS.get(current_class)
            can_leave, reason = check_requirements(reqs, alt_reqs)
            if not can_leave:
                return False, f"Cannot multiclass out of {current_class}: {reason}"

        # Check requirements to multiclass INTO the target class
        if class_name not in MULTICLASS_REQUIREMENTS:
            return True, f"No requirements defined for {class_name}"

        target_reqs = MULTICLASS_REQUIREMENTS[class_name]
        target_alt_reqs = MULTICLASS_ALT_REQUIREMENTS.get(class_name)
        can_enter, reason = check_requirements(target_reqs, target_alt_reqs)
        if not can_enter:
            return False, f"Cannot multiclass into {class_name}: {reason}"

        return True, "Meets all multiclass requirements"

    def get_multiclass_caster_level(self) -> int:
        """Calculate combined caster level for multiclass spell slots.

        Uses the PHB multiclass spellcasting rules:
        - Full casters (Bard, Cleric, Druid, Sorcerer, Wizard): full level
        - Half casters (Paladin, Ranger): level / 2 (rounded down)
        - Third casters (Eldritch Knight, Arcane Trickster): level / 3 (rounded down)
        - Warlock: separate pact magic (doesn't contribute)

        Returns:
            Combined caster level for spell slot calculation
        """
        from dnd_manager.data.classes import (
            CLASS_CASTER_TYPES,
            THIRD_CASTER_SUBCLASSES,
            CasterType,
        )

        total_caster_level = 0

        # Helper to get caster contribution for a class
        def get_caster_contribution(class_name: str, subclass: Optional[str], level: int) -> int:
            base_type = CLASS_CASTER_TYPES.get(class_name, CasterType.NONE)

            # Check if subclass grants spellcasting (third caster)
            if base_type == CasterType.NONE and subclass:
                third_caster_subs = THIRD_CASTER_SUBCLASSES.get(class_name, [])
                if subclass in third_caster_subs:
                    return level // 3

            # Apply caster type calculation
            if base_type == CasterType.FULL:
                return level
            elif base_type == CasterType.HALF:
                return level // 2
            elif base_type == CasterType.THIRD:
                return level // 3
            # PACT and NONE don't contribute to multiclass spell slots
            return 0

        # Add primary class contribution
        total_caster_level += get_caster_contribution(
            self.primary_class.name,
            self.primary_class.subclass,
            self.primary_class.level,
        )

        # Add multiclass contributions
        for mc in self.multiclass:
            total_caster_level += get_caster_contribution(mc.name, mc.subclass, mc.level)

        return total_caster_level

    def is_multiclass(self) -> bool:
        """Check if character is multiclassed."""
        return len(self.multiclass) > 0

    def get_class_levels(self) -> dict[str, int]:
        """Get a dictionary of class name to level for all classes."""
        levels = {self.primary_class.name: self.primary_class.level}
        for mc in self.multiclass:
            levels[mc.name] = levels.get(mc.name, 0) + mc.level
        return levels

    @classmethod
    def create_new(
        cls,
        name: str,
        ruleset_id: Optional[RulesetId] = None,
        class_name: Optional[str] = None,
        player: Optional[str] = None,
    ) -> "Character":
        """Factory method to create a new character with ruleset defaults.

        Args:
            name: Character name
            ruleset_id: Which ruleset to use (defaults to config)
            class_name: Starting class (defaults to config)
            player: Player name (optional)
        """
        from dnd_manager.config import get_config_manager
        from dnd_manager.rulesets.base import RulesetRegistry

        # Use config defaults if not specified
        config = get_config_manager().config
        if ruleset_id is None:
            ruleset_id = RulesetId(config.character_defaults.ruleset)
        if class_name is None:
            class_name = config.character_defaults.class_name

        ruleset = RulesetRegistry.get(ruleset_id.value)
        if not ruleset:
            raise ValueError(f"Unknown ruleset: {ruleset_id}")

        # Get class definition for defaults
        class_def = ruleset.get_class_definition(class_name)
        if not class_def:
            # Fall back to Fighter if unknown class
            class_def = ruleset.get_class_definition("Fighter")
            class_name = "Fighter"

        # Create character with ruleset-appropriate defaults
        char = cls(
            name=name,
            player=player,
            meta=CharacterMeta(ruleset=ruleset_id),
            primary_class=CharacterClass(name=class_name, level=1),
        )

        # Set up class-based proficiencies
        if class_def:
            char.proficiencies.saving_throws = [
                Ability(st.lower()) for st in class_def.saving_throws
            ]
            char.proficiencies.weapons = class_def.weapon_proficiencies.copy()
            char.proficiencies.armor = class_def.armor_proficiencies.copy()
            char.proficiencies.tools = class_def.tool_proficiencies.copy()

            # Set up spellcasting if applicable
            if class_def.spellcasting_ability:
                char.spellcasting.ability = Ability(class_def.spellcasting_ability.lower())

            # Set hit die
            char.combat.hit_dice.die = f"d{class_def.hit_die}"

        # Sync with ruleset to set up spell slots, HP, etc.
        char.sync_with_ruleset()

        return char
