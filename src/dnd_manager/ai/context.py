"""Character context building for AI conversations."""

import logging
from dataclasses import dataclass
from typing import Optional

from dnd_manager.models.character import Character
from dnd_manager.data.custom import CustomContent, get_custom_content_store
from dnd_manager.data.balance import get_balance_guidelines, get_homebrew_prompt

logger = logging.getLogger(__name__)


@dataclass
class CharacterContext:
    """Comprehensive context about a character for AI assistance.

    This provides the AI with COMPLETE knowledge of the character's state,
    including all proficiencies, equipment, combat status, resources, and more.
    """

    # Identity
    name: str
    player: Optional[str]
    class_info: str
    level: int
    species: Optional[str]
    subspecies: Optional[str]
    background: Optional[str]
    alignment: str
    ruleset: str

    # Ability scores with full breakdown
    abilities: dict[str, dict]  # {"strength": {"score": 16, "modifier": "+3", "base": 15, "bonus": 1}}

    # Proficiencies (complete)
    skill_proficiencies: dict[str, dict]  # {"athletics": {"modifier": "+5", "proficiency": "proficient"}}
    saving_throws: dict[str, dict]  # {"strength": {"modifier": "+5", "proficient": True}}
    weapon_proficiencies: list[str]
    armor_proficiencies: list[str]
    tool_proficiencies: list[str]
    languages: list[str]

    # Combat state (complete)
    armor_class: int
    ac_bonus: int
    hit_points_current: int
    hit_points_max: int
    temp_hp: int
    is_bloodied: bool
    is_unconscious: bool
    speed: int
    speed_bonus: int
    initiative: int
    passive_perception: int
    hit_dice: str  # "5/5d10 + 3/3d6" format
    death_saves: dict[str, int]  # {"successes": 0, "failures": 0}

    # Spellcasting (complete)
    spellcasting_ability: Optional[str]
    spell_save_dc: Optional[int]
    spell_attack_bonus: Optional[int]
    spell_slots: dict[int, dict]  # {1: {"remaining": 3, "total": 4}}
    cantrips: list[str]
    spells_known: list[str]
    spells_prepared: list[str]

    # Equipment (complete)
    equipped_items: list[dict]  # [{"name": "Longsword", "attuned": False}]
    attuned_items: list[str]  # Items requiring attunement
    attunement_slots: dict[str, int]  # {"used": 2, "max": 3}
    inventory_summary: list[str]  # Non-equipped notable items
    currency: dict[str, int]  # {"cp": 0, "sp": 0, "ep": 0, "gp": 100, "pp": 0}
    total_wealth_gp: float
    total_weight: float

    # Features and resources
    features: list[dict]  # [{"name": "Action Surge", "source": "Fighter", "uses": "1/1", "recharge": "short rest"}]

    # Custom tracking
    custom_stats: list[dict]  # [{"name": "Luck", "value": 3, "max": 20}]
    stat_bonuses: list[dict]  # [{"source": "Belt of Giant Strength", "ability": "strength", "effect": "set to 21"}]

    # Personality & story
    personality: dict[str, list[str]]  # {"traits": [...], "ideals": [...], "bonds": [...], "flaws": [...]}
    backstory_summary: Optional[str]

    # AI context
    playstyle: Optional[str]
    campaign_notes: Optional[str]
    relationships: list[str]
    custom_rules: list[str]

    @classmethod
    def from_character(cls, character: Character) -> "CharacterContext":
        """Build comprehensive context from a Character object."""
        c = character

        # --- Identity ---
        class_info = f"{c.primary_class.name}"
        if c.primary_class.subclass:
            class_info += f" ({c.primary_class.subclass})"
        for mc in c.multiclass:
            class_info += f" / {mc.name} {mc.level}"
            if mc.subclass:
                class_info += f" ({mc.subclass})"

        ruleset = c.get_ruleset()
        ruleset_name = ruleset.name if ruleset else c.meta.ruleset.value

        # --- Ability Scores (full breakdown) ---
        abilities = {}
        for name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = getattr(c.abilities, name)
            abilities[name] = {
                "score": score.total,
                "modifier": score.modifier_str,
                "base": score.base,
                "bonus": score.bonus,
                "override": score.override,
            }

        # --- Skills (all 18 with modifiers and proficiency) ---
        from dnd_manager.models.abilities import Skill, SKILL_ABILITY_MAP
        skill_proficiencies = {}
        for skill in Skill:
            prof = c.proficiencies.get_skill_proficiency(skill)
            modifier = c.get_skill_modifier(skill)
            skill_proficiencies[skill.value] = {
                "modifier": f"{modifier:+d}",
                "proficiency": prof.value,
                "ability": SKILL_ABILITY_MAP[skill].value,
            }

        # --- Saving Throws (all 6 with modifiers) ---
        from dnd_manager.models.abilities import Ability
        saving_throws = {}
        for ability in Ability:
            is_proficient = c.proficiencies.is_proficient_save(ability)
            modifier = c.get_save_modifier(ability)
            saving_throws[ability.value] = {
                "modifier": f"{modifier:+d}",
                "proficient": is_proficient,
            }

        # --- Combat State ---
        hp = c.combat.hit_points

        # Hit dice display
        hit_dice_display = c.combat.get_hit_dice_display()

        # Death saves
        death_saves = {
            "successes": c.combat.death_saves.successes,
            "failures": c.combat.death_saves.failures,
            "is_stable": c.combat.death_saves.is_stable,
            "is_dead": c.combat.death_saves.is_dead,
        }

        # --- Spellcasting ---
        spell_slots = {}
        for lvl, slot in c.spellcasting.slots.items():
            spell_slots[lvl] = {
                "remaining": slot.remaining,
                "total": slot.total,
                "used": slot.used,
            }

        # --- Equipment ---
        equipped_items = []
        attuned_items = []
        inventory_summary = []

        for item in c.equipment.items:
            item_info = {
                "name": item.name,
                "quantity": item.quantity,
                "equipped": item.equipped,
                "attuned": item.attuned,
            }
            if item.description:
                item_info["description"] = item.description[:100]  # Truncate long descriptions

            if item.equipped:
                equipped_items.append(item_info)
            if item.attuned:
                attuned_items.append(item.name)
            if not item.equipped and item.quantity > 0:
                inventory_summary.append(f"{item.name} x{item.quantity}" if item.quantity > 1 else item.name)

        currency = {
            "cp": c.equipment.currency.cp,
            "sp": c.equipment.currency.sp,
            "ep": c.equipment.currency.ep,
            "gp": c.equipment.currency.gp,
            "pp": c.equipment.currency.pp,
        }

        # --- Features with resource tracking ---
        features = []
        for f in c.features:
            feature_info = {
                "name": f.name,
                "source": f.source,
            }
            if f.uses is not None:
                remaining = f.uses - f.used
                feature_info["uses"] = f"{remaining}/{f.uses}"
                feature_info["recharge"] = f.recharge or "long rest"
            if f.description:
                feature_info["description"] = f.description[:150]  # Truncate
            features.append(feature_info)

        # --- Custom Stats ---
        custom_stats = []
        for stat in c.custom_stats:
            stat_info = {
                "name": stat.name,
                "value": stat.value,
            }
            if stat.max_value is not None:
                stat_info["max"] = stat.max_value
            if stat.min_value is not None:
                stat_info["min"] = stat.min_value
            if stat.description:
                stat_info["description"] = stat.description
            custom_stats.append(stat_info)

        # --- Stat Bonuses ---
        stat_bonuses = []
        for bonus in c.stat_bonuses:
            bonus_info = {
                "source": bonus.source,
                "ability": bonus.ability,
            }
            if bonus.is_override:
                bonus_info["effect"] = f"set to {bonus.override_value}"
            else:
                bonus_info["effect"] = f"+{bonus.bonus}" if bonus.bonus >= 0 else str(bonus.bonus)
            if bonus.temporary:
                bonus_info["temporary"] = True
                if bonus.duration:
                    bonus_info["duration"] = bonus.duration
            stat_bonuses.append(bonus_info)

        # --- Personality ---
        personality = {
            "traits": c.personality.traits,
            "ideals": c.personality.ideals,
            "bonds": c.personality.bonds,
            "flaws": c.personality.flaws,
        }

        # --- Backstory summary (first 200 chars) ---
        backstory_summary = None
        if c.backstory:
            backstory_summary = c.backstory[:200] + "..." if len(c.backstory) > 200 else c.backstory

        return cls(
            # Identity
            name=c.name,
            player=c.player,
            class_info=class_info,
            level=c.total_level,
            species=c.species,
            subspecies=c.subspecies,
            background=c.background,
            alignment=c.alignment.display_name,
            ruleset=ruleset_name,

            # Abilities
            abilities=abilities,

            # Proficiencies
            skill_proficiencies=skill_proficiencies,
            saving_throws=saving_throws,
            weapon_proficiencies=c.proficiencies.weapons,
            armor_proficiencies=c.proficiencies.armor,
            tool_proficiencies=c.proficiencies.tools,
            languages=c.proficiencies.languages,

            # Combat
            armor_class=c.combat.total_ac,
            ac_bonus=c.combat.armor_class_bonus,
            hit_points_current=hp.current,
            hit_points_max=hp.maximum,
            temp_hp=hp.temporary,
            is_bloodied=hp.is_bloodied,
            is_unconscious=hp.is_unconscious,
            speed=c.combat.total_speed,
            speed_bonus=c.combat.speed_bonus,
            initiative=c.get_initiative(),
            passive_perception=c.get_passive_perception(),
            hit_dice=hit_dice_display,
            death_saves=death_saves,

            # Spellcasting
            spellcasting_ability=c.spellcasting.ability.value if c.spellcasting.ability else None,
            spell_save_dc=c.get_spell_save_dc(),
            spell_attack_bonus=c.get_spell_attack_bonus(),
            spell_slots=spell_slots,
            cantrips=c.spellcasting.cantrips,
            spells_known=c.spellcasting.known,
            spells_prepared=c.spellcasting.prepared,

            # Equipment
            equipped_items=equipped_items,
            attuned_items=attuned_items,
            attunement_slots={"used": c.equipment.attuned_count, "max": 3},
            inventory_summary=inventory_summary,
            currency=currency,
            total_wealth_gp=c.equipment.currency.total_gp,
            total_weight=c.equipment.total_weight,

            # Features
            features=features,

            # Custom
            custom_stats=custom_stats,
            stat_bonuses=stat_bonuses,

            # Personality
            personality=personality,
            backstory_summary=backstory_summary,

            # AI context
            playstyle=c.ai_context.playstyle,
            campaign_notes=c.ai_context.campaign_notes,
            relationships=c.ai_context.relationships,
            custom_rules=c.ai_context.custom_rules,
        )

    def to_prompt(self) -> str:
        """Convert context to a comprehensive text summary for the AI."""
        lines = []

        # === IDENTITY ===
        lines.append("=== CHARACTER IDENTITY ===")
        lines.append(f"Name: {self.name}")
        if self.player:
            lines.append(f"Player: {self.player}")
        lines.append(f"Class: Level {self.level} {self.class_info}")
        if self.species:
            species_str = self.species
            if self.subspecies:
                species_str += f" ({self.subspecies})"
            lines.append(f"Species: {species_str}")
        if self.background:
            lines.append(f"Background: {self.background}")
        lines.append(f"Alignment: {self.alignment}")
        lines.append(f"Ruleset: {self.ruleset}")

        # === ABILITY SCORES ===
        lines.append("")
        lines.append("=== ABILITY SCORES ===")
        for name, data in self.abilities.items():
            line = f"{name.upper()[:3]}: {data['score']} ({data['modifier']})"
            if data.get('bonus'):
                line += f" [base {data['base']} + {data['bonus']} bonus]"
            if data.get('override'):
                line += f" [overridden]"
            lines.append(line)

        # === COMBAT STATUS ===
        lines.append("")
        lines.append("=== COMBAT STATUS ===")
        hp_status = f"HP: {self.hit_points_current}/{self.hit_points_max}"
        if self.temp_hp:
            hp_status += f" (+{self.temp_hp} temp)"
        if self.is_unconscious:
            hp_status += " [UNCONSCIOUS]"
        elif self.is_bloodied:
            hp_status += " [BLOODIED]"
        lines.append(hp_status)
        lines.append(f"AC: {self.armor_class}" + (f" (+{self.ac_bonus} bonus)" if self.ac_bonus else ""))
        lines.append(f"Speed: {self.speed} ft" + (f" (+{self.speed_bonus} bonus)" if self.speed_bonus else ""))
        lines.append(f"Initiative: {self.initiative:+d}")
        lines.append(f"Passive Perception: {self.passive_perception}")
        lines.append(f"Hit Dice: {self.hit_dice}")

        if self.death_saves["successes"] > 0 or self.death_saves["failures"] > 0:
            lines.append(f"Death Saves: {self.death_saves['successes']} successes, {self.death_saves['failures']} failures")

        # === SAVING THROWS ===
        lines.append("")
        lines.append("=== SAVING THROWS ===")
        save_parts = []
        for ability, data in self.saving_throws.items():
            prof_mark = "*" if data["proficient"] else ""
            save_parts.append(f"{ability[:3].upper()}{prof_mark}: {data['modifier']}")
        lines.append(", ".join(save_parts))
        lines.append("(* = proficient)")

        # === SKILLS ===
        lines.append("")
        lines.append("=== SKILLS ===")
        # Group by proficiency level for clarity
        proficient_skills = []
        expertise_skills = []

        for skill, data in self.skill_proficiencies.items():
            skill_display = skill.replace("_", " ").title()
            if data["proficiency"] == "expertise":
                expertise_skills.append(f"{skill_display}: {data['modifier']}")
            elif data["proficiency"] == "proficient":
                proficient_skills.append(f"{skill_display}: {data['modifier']}")

        if expertise_skills:
            lines.append(f"Expertise: {', '.join(expertise_skills)}")
        if proficient_skills:
            lines.append(f"Proficient: {', '.join(proficient_skills)}")

        # All skills with modifiers
        all_skills = [f"{s.replace('_', ' ').title()}: {d['modifier']}" for s, d in self.skill_proficiencies.items()]
        lines.append(f"All Skills: {', '.join(all_skills)}")

        # === PROFICIENCIES ===
        lines.append("")
        lines.append("=== PROFICIENCIES ===")
        if self.weapon_proficiencies:
            lines.append(f"Weapons: {', '.join(self.weapon_proficiencies)}")
        if self.armor_proficiencies:
            lines.append(f"Armor: {', '.join(self.armor_proficiencies)}")
        if self.tool_proficiencies:
            lines.append(f"Tools: {', '.join(self.tool_proficiencies)}")
        if self.languages:
            lines.append(f"Languages: {', '.join(self.languages)}")

        # === SPELLCASTING ===
        if self.spellcasting_ability:
            lines.append("")
            lines.append("=== SPELLCASTING ===")
            lines.append(f"Ability: {self.spellcasting_ability.title()}")
            lines.append(f"Spell Save DC: {self.spell_save_dc}")
            lines.append(f"Spell Attack: +{self.spell_attack_bonus}")

            if self.spell_slots:
                slots_str = ", ".join(f"L{lvl}: {d['remaining']}/{d['total']}" for lvl, d in sorted(self.spell_slots.items()))
                lines.append(f"Spell Slots: {slots_str}")

            if self.cantrips:
                lines.append(f"Cantrips: {', '.join(self.cantrips)}")
            if self.spells_known:
                lines.append(f"Known Spells: {', '.join(self.spells_known)}")
            if self.spells_prepared:
                lines.append(f"Prepared Spells: {', '.join(self.spells_prepared)}")

        # === EQUIPMENT ===
        lines.append("")
        lines.append("=== EQUIPMENT ===")
        lines.append(f"Wealth: {self.total_wealth_gp:.1f} gp total ({self.currency['gp']} gp, {self.currency['sp']} sp, {self.currency['cp']} cp, {self.currency['pp']} pp, {self.currency['ep']} ep)")
        lines.append(f"Attunement: {self.attunement_slots['used']}/{self.attunement_slots['max']} slots used")

        if self.equipped_items:
            equipped_str = ", ".join(
                f"{i['name']}{'[A]' if i['attuned'] else ''}" for i in self.equipped_items
            )
            lines.append(f"Equipped: {equipped_str}")

        if self.inventory_summary:
            lines.append(f"Inventory: {', '.join(self.inventory_summary[:20])}")  # Limit to 20 items
            if len(self.inventory_summary) > 20:
                lines.append(f"  (+{len(self.inventory_summary) - 20} more items)")

        lines.append(f"Total Weight: {self.total_weight:.1f} lbs")

        # === FEATURES ===
        if self.features:
            lines.append("")
            lines.append("=== FEATURES & ABILITIES ===")
            for f in self.features:
                feature_str = f"{f['name']} ({f['source']})"
                if "uses" in f:
                    feature_str += f" [{f['uses']} - recharges on {f['recharge']}]"
                lines.append(f"- {feature_str}")

        # === CUSTOM STATS ===
        if self.custom_stats:
            lines.append("")
            lines.append("=== CUSTOM STATS ===")
            for stat in self.custom_stats:
                stat_str = f"{stat['name']}: {stat['value']}"
                if "max" in stat:
                    stat_str += f"/{stat['max']}"
                lines.append(stat_str)

        # === ACTIVE BONUSES ===
        if self.stat_bonuses:
            lines.append("")
            lines.append("=== ACTIVE BONUSES ===")
            for bonus in self.stat_bonuses:
                bonus_str = f"{bonus['source']}: {bonus['ability']} {bonus['effect']}"
                if bonus.get("temporary"):
                    bonus_str += f" (temp: {bonus.get('duration', 'unknown')})"
                lines.append(f"- {bonus_str}")

        # === PERSONALITY ===
        has_personality = any([
            self.personality.get("traits"),
            self.personality.get("ideals"),
            self.personality.get("bonds"),
            self.personality.get("flaws"),
        ])
        if has_personality:
            lines.append("")
            lines.append("=== PERSONALITY ===")
            if self.personality.get("traits"):
                lines.append(f"Traits: {'; '.join(self.personality['traits'])}")
            if self.personality.get("ideals"):
                lines.append(f"Ideals: {'; '.join(self.personality['ideals'])}")
            if self.personality.get("bonds"):
                lines.append(f"Bonds: {'; '.join(self.personality['bonds'])}")
            if self.personality.get("flaws"):
                lines.append(f"Flaws: {'; '.join(self.personality['flaws'])}")

        if self.backstory_summary:
            lines.append(f"Backstory: {self.backstory_summary}")

        # === AI CONTEXT ===
        has_ai_context = any([self.playstyle, self.campaign_notes, self.relationships, self.custom_rules])
        if has_ai_context:
            lines.append("")
            lines.append("=== PLAYER NOTES ===")
            if self.playstyle:
                lines.append(f"Playstyle: {self.playstyle}")
            if self.campaign_notes:
                lines.append(f"Campaign: {self.campaign_notes}")
            if self.relationships:
                lines.append(f"Relationships: {', '.join(self.relationships)}")
            if self.custom_rules:
                lines.append(f"Custom Rules: {', '.join(self.custom_rules)}")

        return "\n".join(lines)


def build_custom_content_context() -> Optional[str]:
    """Build context string for custom homebrew content.

    Returns:
        Context string describing available custom content, or None if no custom content exists.
    """
    try:
        store = get_custom_content_store()
        content = store.content

        if not content.spells and not content.items and not content.feats:
            return None

        lines = ["Available Homebrew Content:"]

        if content.spells:
            spell_summaries = []
            for spell in content.spells[:10]:  # Limit to 10 for context length
                level_str = "Cantrip" if spell.level == 0 else f"L{spell.level}"
                spell_summaries.append(f"{spell.name} ({level_str} {spell.school})")
            lines.append(f"- Custom Spells: {', '.join(spell_summaries)}")
            if len(content.spells) > 10:
                lines.append(f"  (+{len(content.spells) - 10} more)")

        if content.items:
            item_summaries = []
            for item in content.items[:10]:
                item_summaries.append(f"{item.name} ({item.rarity} {item.item_type})")
            lines.append(f"- Custom Items: {', '.join(item_summaries)}")
            if len(content.items) > 10:
                lines.append(f"  (+{len(content.items) - 10} more)")

        if content.feats:
            feat_names = [f.name for f in content.feats[:10]]
            lines.append(f"- Custom Feats: {', '.join(feat_names)}")
            if len(content.feats) > 10:
                lines.append(f"  (+{len(content.feats) - 10} more)")

        return "\n".join(lines)
    except (OSError, IOError) as e:
        # File system errors loading custom content
        logger.debug(f"Failed to load custom content: {e}")
        return None
    except (KeyError, TypeError, AttributeError) as e:
        # Data structure issues in custom content
        logger.warning(f"Invalid custom content data: {e}")
        return None


def build_system_prompt(
    character: Optional[Character] = None,
    mode: str = "assistant",
    include_custom_content: bool = True,
    include_data_summary: bool = False,
) -> str:
    """Build a system prompt for D&D AI assistance.

    Args:
        character: Optional character for context
        mode: Type of assistance
            - "assistant": General D&D assistant
            - "dm": Dungeon Master mode
            - "roleplay": Character roleplay mode
            - "rules": Rules lookup mode
        include_custom_content: Whether to include homebrew content context
        include_data_summary: Whether to include summary of available game data

    Returns:
        System prompt string
    """
    # Tool usage guidance included in all prompts
    tool_guidance = """

--- IMPORTANT: Using Your Tools ---
You have access to tools that let you query game data and modify characters. ALWAYS use these tools instead of guessing:

LOOKUP TOOLS (use these BEFORE answering questions about game mechanics):
- lookup_spell: Get exact spell details (casting time, range, components, description)
- lookup_class: Get class mechanics (hit die, proficiencies, primary ability)
- lookup_species: Get species traits, size, speed, and abilities
- lookup_feat: Get feat prerequisites and benefits
- lookup_magic_item: Get item properties and attunement requirements
- lookup_monster: Get monster stats for encounters

SEARCH TOOLS (find content matching criteria):
- search_spells: Find spells by level, school, class, or name
- get_class_spells: Get all spells available to a class
- search_feats: Find feats by category
- search_magic_items: Find items by rarity or type
- search_monsters: Find monsters by CR or type
- get_encounter_monsters: Get suitable monsters for a party level

CHARACTER TOOLS (modify the character):
- get_character_summary: Get full character state before making changes
- deal_damage, heal_character: Track HP changes
- level_up: Add a level (handles HP, spell slots automatically)
- add_spell, remove_spell: Manage spell lists
- add_item, remove_item: Manage inventory

RULES:
1. NEVER guess about spell effects, class features, or racial traits - look them up
2. Use get_character_summary before suggesting changes based on current state
3. When asked about spells a class can use, call get_class_spells
4. When asked about a specific spell/feat/item, call the lookup tool
5. If a lookup fails, tell the user it wasn't found rather than making something up
"""

    base_prompts = {
        "assistant": """You are a helpful D&D 5e assistant. You help players with:
- Rules questions and clarifications
- Character building advice
- Spell and ability mechanics
- Tactical suggestions
- Roleplaying ideas

Be concise but thorough. Reference specific rules when relevant.""" + tool_guidance,

        "dm": """You are an experienced Dungeon Master assistant. You help with:
- Encounter design and balance
- NPC creation and dialogue
- World-building ideas
- Improvisation suggestions
- Session planning

Be creative but practical. Offer multiple options when appropriate.""" + tool_guidance,

        "roleplay": """You are helping a player roleplay their D&D character. Based on their character's
personality, background, and situation, suggest:
- Dialogue options
- Actions their character might take
- Reactions to events
- Character development moments

Stay true to the character's established traits and motivations.""" + tool_guidance,

        "rules": """You are a D&D 5e rules expert. Answer questions about:
- Combat mechanics
- Spellcasting rules
- Class features
- Conditions and effects
- Edge cases and interactions

Be precise about mechanics. Note any differences between 2014 and 2024 rules if relevant.""" + tool_guidance,

        "homebrew": """You are a D&D 5e homebrew design expert. You help create balanced custom content:
- Spells and magic items
- Races/species and backgrounds
- Classes and subclasses
- Feats and abilities

Your approach:
1. First understand the player's fantasy and concept
2. Suggest appropriate power level and rarity
3. Compare to similar official content
4. Point out balance concerns while being supportive
5. Offer alternatives when something seems too strong
6. Encourage playtesting and iteration

Be collaborative, not restrictive. Explain your reasoning.""" + tool_guidance,
    }

    prompt = base_prompts.get(mode, base_prompts["assistant"])

    if character:
        context = CharacterContext.from_character(character)
        prompt += f"\n\n--- Current Character ---\n{context.to_prompt()}"

    if include_custom_content:
        custom_context = build_custom_content_context()
        if custom_context:
            prompt += f"\n\n--- Homebrew Content ---\n{custom_context}"
            prompt += "\n\nNote: The player has custom homebrew content. You can reference and suggest using this content when appropriate."

    if include_data_summary:
        try:
            from dnd_manager.ai.semantic import get_semantic_layer
            layer = get_semantic_layer()
            data_summary = layer.get_data_summary()
            prompt += f"\n\n--- Available Game Data ---\n{data_summary}"
            prompt += "\n\nYou have access to detailed information about all the content listed above. Reference specific spells, items, monsters, classes, etc. when relevant to provide accurate information."
        except ImportError:
            logger.debug("Semantic layer not available")
        except (RuntimeError, AttributeError) as e:
            logger.debug(f"Semantic layer failed: {e}")

    return prompt


def build_homebrew_system_prompt(
    content_type: str,
    character: Optional[Character] = None,
) -> str:
    """Build a system prompt specifically for homebrew content creation.

    Args:
        content_type: Type of content to create (spell, magic_item, race, class, subclass, feat, background)
        character: Optional character for context

    Returns:
        System prompt with balance guidelines
    """
    # Start with homebrew base prompt
    prompt = build_system_prompt(character, mode="homebrew", include_custom_content=True)

    # Add content-specific guidelines
    try:
        guidelines = get_balance_guidelines()

        # Add general principles
        prompt += f"\n\n--- Balance Guidelines ---\n"
        prompt += guidelines._build_general_prompt()

        # Add content-specific guidelines
        if content_type:
            specific_prompt = guidelines.get_prompt_for_content_type(content_type)
            prompt += f"\n\n--- {content_type.title()} Creation Guidelines ---\n"
            prompt += specific_prompt

        # Add AI behavior guidance
        approach = guidelines.get_ai_approach()
        if approach:
            prompt += f"\n\n--- Your Approach ---\n{approach}"

    except (OSError, IOError) as e:
        # File system errors loading guidelines
        logger.debug(f"Failed to load balance guidelines: {e}")
    except (KeyError, TypeError, AttributeError) as e:
        # Data structure issues in guidelines
        logger.warning(f"Invalid balance guidelines data: {e}")

    return prompt


def get_available_modes() -> dict[str, str]:
    """Get all available AI assistant modes with descriptions."""
    return {
        "assistant": "General D&D assistant for rules, advice, and ideas",
        "dm": "Dungeon Master assistant for encounters, NPCs, and worldbuilding",
        "roleplay": "Character roleplay helper for dialogue and actions",
        "rules": "Rules expert for mechanics and edge cases",
        "homebrew": "Homebrew design expert for balanced custom content",
    }


def get_homebrew_content_types() -> list[str]:
    """Get list of supported homebrew content types."""
    return [
        "spell",
        "magic_item",
        "race",
        "species",
        "class",
        "subclass",
        "feat",
        "background",
    ]
