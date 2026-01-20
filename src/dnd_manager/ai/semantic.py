"""Semantic layer for AI access to game data.

Provides structured access to D&D content (spells, items, monsters, classes, etc.)
that can be used to enhance AI responses with accurate game information.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class QueryResult:
    """Result from a semantic query."""
    query_type: str
    data: list[dict]
    total_count: int
    has_more: bool
    summary: str


class SemanticLayer:
    """Provides semantic access to D&D game data for AI assistance."""

    def __init__(self):
        # Lazy-load data modules to avoid circular imports
        self._spells = None
        self._items = None
        self._monsters = None
        self._classes = None
        self._species = None
        self._feats = None
        self._subclasses = None

    def _load_spells(self):
        if self._spells is None:
            from dnd_manager.data.spells import ALL_SPELLS
            self._spells = ALL_SPELLS

    def _load_items(self):
        if self._items is None:
            from dnd_manager.data.magic_items import ALL_MAGIC_ITEMS
            from dnd_manager.data.items import ALL_WEAPONS, ARMOR, ADVENTURING_GEAR
            self._items = {
                "magic": ALL_MAGIC_ITEMS,
                "weapons": ALL_WEAPONS,
                "armor": ARMOR,
                "gear": ADVENTURING_GEAR,
            }

    def _load_monsters(self):
        if self._monsters is None:
            from dnd_manager.data.monsters import ALL_MONSTERS
            self._monsters = ALL_MONSTERS

    def _load_classes(self):
        if self._classes is None:
            from dnd_manager.data.classes import ALL_CLASSES
            self._classes = ALL_CLASSES

    def _load_species(self):
        if self._species is None:
            from dnd_manager.data.species import ALL_SPECIES
            self._species = ALL_SPECIES

    def _load_feats(self):
        if self._feats is None:
            from dnd_manager.data.feats import ALL_FEATS
            self._feats = ALL_FEATS

    def _load_subclasses(self):
        if self._subclasses is None:
            from dnd_manager.data.subclasses import ALL_SUBCLASSES
            self._subclasses = ALL_SUBCLASSES

    # Spell queries
    def get_spell(self, name: str) -> Optional[dict]:
        """Get a spell by exact name (case-insensitive)."""
        self._load_spells()
        name_lower = name.lower()
        for spell in self._spells:
            if spell.name.lower() == name_lower:
                return self._spell_to_dict(spell)
        return None

    def search_spells(
        self,
        query: str = "",
        level: Optional[int] = None,
        school: Optional[str] = None,
        class_name: Optional[str] = None,
        concentration: Optional[bool] = None,
        ritual: Optional[bool] = None,
        limit: int = 10,
    ) -> QueryResult:
        """Search spells with various filters."""
        self._load_spells()
        results = []

        for spell in self._spells:
            # Apply filters
            if query and query.lower() not in spell.name.lower():
                continue
            if level is not None and spell.level != level:
                continue
            if school and school.lower() not in spell.school.lower():
                continue
            if class_name and class_name not in spell.classes:
                continue
            if concentration is not None and spell.concentration != concentration:
                continue
            if ritual is not None and spell.ritual != ritual:
                continue

            results.append(self._spell_to_dict(spell))

        total = len(results)
        limited = results[:limit]
        return QueryResult(
            query_type="spells",
            data=limited,
            total_count=total,
            has_more=total > limit,
            summary=f"Found {total} spells matching criteria",
        )

    def get_spells_for_class(self, class_name: str, max_level: int = 9) -> QueryResult:
        """Get all spells available to a class up to a certain level."""
        self._load_spells()
        results = []
        for spell in self._spells:
            if class_name in spell.classes and spell.level <= max_level:
                results.append(self._spell_to_dict(spell))

        results.sort(key=lambda s: (s["level"], s["name"]))
        return QueryResult(
            query_type="class_spells",
            data=results,
            total_count=len(results),
            has_more=False,
            summary=f"{class_name} has access to {len(results)} spells up to level {max_level}",
        )

    def _spell_to_dict(self, spell) -> dict:
        return {
            "name": spell.name,
            "level": spell.level,
            "school": spell.school,
            "casting_time": spell.casting_time,
            "range": spell.range,
            "components": spell.components,
            "duration": spell.duration,
            "description": spell.description[:200] + "..." if len(spell.description) > 200 else spell.description,
            "classes": spell.classes,
            "concentration": spell.concentration,
            "ritual": spell.ritual,
        }

    # Monster queries
    def get_monster(self, name: str) -> Optional[dict]:
        """Get a monster by name."""
        self._load_monsters()
        name_lower = name.lower()
        for monster in self._monsters:
            if monster.name.lower() == name_lower:
                return self._monster_to_dict(monster)
        return None

    def search_monsters(
        self,
        query: str = "",
        cr_min: Optional[float] = None,
        cr_max: Optional[float] = None,
        monster_type: Optional[str] = None,
        limit: int = 10,
    ) -> QueryResult:
        """Search monsters with filters."""
        self._load_monsters()
        results = []

        for monster in self._monsters:
            if query and query.lower() not in monster.name.lower():
                continue
            cr = monster.cr_numeric
            if cr_min is not None and cr < cr_min:
                continue
            if cr_max is not None and cr > cr_max:
                continue
            if monster_type and monster_type.lower() != monster.monster_type.value.lower():
                continue

            results.append(self._monster_to_dict(monster))

        total = len(results)
        limited = results[:limit]
        return QueryResult(
            query_type="monsters",
            data=limited,
            total_count=total,
            has_more=total > limit,
            summary=f"Found {total} monsters matching criteria",
        )

    def get_monsters_for_encounter(self, party_level: int, party_size: int = 4) -> QueryResult:
        """Get monsters suitable for an encounter based on party level."""
        self._load_monsters()

        # Simple CR recommendation: party level / 4 to party level for challenging fights
        min_cr = max(0, party_level / 4 - 1)
        max_cr = party_level + 2

        suitable = []
        for monster in self._monsters:
            cr = monster.cr_numeric
            if min_cr <= cr <= max_cr:
                suitable.append(self._monster_to_dict(monster))

        suitable.sort(key=lambda m: m["cr_numeric"])
        return QueryResult(
            query_type="encounter_monsters",
            data=suitable,
            total_count=len(suitable),
            has_more=False,
            summary=f"{len(suitable)} monsters suitable for a level {party_level} party (CR {min_cr:.1f}-{max_cr:.1f})",
        )

    def _monster_to_dict(self, monster) -> dict:
        return {
            "name": monster.name,
            "size": monster.size.value,
            "type": monster.monster_type.value,
            "alignment": monster.alignment,
            "cr": monster.challenge_rating,
            "cr_numeric": monster.cr_numeric,
            "xp": monster.xp,
            "ac": monster.armor_class,
            "hp": monster.hit_points,
            "speed": monster.speed,
            "str": monster.strength,
            "dex": monster.dexterity,
            "con": monster.constitution,
            "int": monster.intelligence,
            "wis": monster.wisdom,
            "cha": monster.charisma,
        }

    # Magic item queries
    def get_magic_item(self, name: str) -> Optional[dict]:
        """Get a magic item by name."""
        self._load_items()
        name_lower = name.lower()
        for item in self._items["magic"]:
            if item.name.lower() == name_lower:
                return self._magic_item_to_dict(item)
        return None

    def search_magic_items(
        self,
        query: str = "",
        rarity: Optional[str] = None,
        item_type: Optional[str] = None,
        requires_attunement: Optional[bool] = None,
        limit: int = 10,
    ) -> QueryResult:
        """Search magic items with filters."""
        self._load_items()
        results = []

        for item in self._items["magic"]:
            if query and query.lower() not in item.name.lower():
                continue
            if rarity and rarity.lower() != item.rarity.lower():
                continue
            if item_type and item_type.lower() not in item.item_type.lower():
                continue
            if requires_attunement is not None and item.requires_attunement != requires_attunement:
                continue

            results.append(self._magic_item_to_dict(item))

        total = len(results)
        limited = results[:limit]
        return QueryResult(
            query_type="magic_items",
            data=limited,
            total_count=total,
            has_more=total > limit,
            summary=f"Found {total} magic items matching criteria",
        )

    def _magic_item_to_dict(self, item) -> dict:
        return {
            "name": item.name,
            "type": item.item_type,
            "rarity": item.rarity,
            "description": item.description[:200] + "..." if len(item.description) > 200 else item.description,
            "requires_attunement": item.requires_attunement,
            "attunement_requirements": item.attunement_requirements,
            "magic_bonus": item.magic_bonus,
            "charges": item.charges,
        }

    # Class/Subclass queries
    def get_class_info(self, class_name: str) -> Optional[dict]:
        """Get information about a class."""
        self._load_classes()
        name_lower = class_name.lower()

        # Handle both dict and list formats
        if isinstance(self._classes, dict):
            # Find by key (case-insensitive)
            for key, cls in self._classes.items():
                if key.lower() == name_lower:
                    return self._class_to_dict(cls)
        else:
            # List format
            for cls in self._classes:
                if cls.name.lower() == name_lower:
                    return self._class_to_dict(cls)
        return None

    def _class_to_dict(self, cls) -> dict:
        """Convert a class object to a dict."""
        features_by_level = {}
        for f in cls.features:
            lvl = f.level
            if lvl not in features_by_level:
                features_by_level[lvl] = []
            features_by_level[lvl].append(f.name)

        return {
            "name": cls.name,
            "hit_die": cls.hit_die,
            "primary_ability": cls.primary_ability,
            "saving_throws": cls.saving_throws,
            "armor_proficiencies": cls.armor_proficiencies,
            "weapon_proficiencies": cls.weapon_proficiencies,
            "skill_choices": cls.skill_choices,
            "skill_options": cls.skill_options,
            "spellcasting_ability": cls.spellcasting_ability,
            "features_by_level": features_by_level,
            "total_features": len(cls.features),
        }

    def get_subclasses_for_class(self, class_name: str) -> QueryResult:
        """Get all subclasses for a class."""
        self._load_subclasses()
        results = []
        for sub in self._subclasses:
            if sub.parent_class.lower() == class_name.lower():
                results.append({
                    "name": sub.name,
                    "parent_class": sub.parent_class,
                    "description": sub.description[:150] + "..." if len(sub.description) > 150 else sub.description,
                    "level_gained": sub.level_gained,
                    "features_count": len(sub.features),
                })
        return QueryResult(
            query_type="subclasses",
            data=results,
            total_count=len(results),
            has_more=False,
            summary=f"Found {len(results)} subclasses for {class_name}",
        )

    # Feat queries
    def get_feat(self, name: str) -> Optional[dict]:
        """Get a feat by name."""
        self._load_feats()
        name_lower = name.lower()
        for feat in self._feats:
            if feat.name.lower() == name_lower:
                return self._feat_to_dict(feat)
        return None

    def search_feats(
        self,
        query: str = "",
        category: Optional[str] = None,
        has_prerequisites: Optional[bool] = None,
        limit: int = 10,
    ) -> QueryResult:
        """Search feats with filters."""
        self._load_feats()
        results = []

        for feat in self._feats:
            if query and query.lower() not in feat.name.lower():
                continue
            if category and feat.category.lower() != category.lower():
                continue
            if has_prerequisites is not None:
                has_prereq = bool(feat.prerequisites)
                if has_prereq != has_prerequisites:
                    continue

            results.append(self._feat_to_dict(feat))

        total = len(results)
        limited = results[:limit]
        return QueryResult(
            query_type="feats",
            data=limited,
            total_count=total,
            has_more=total > limit,
            summary=f"Found {total} feats matching criteria",
        )

    def _feat_to_dict(self, feat) -> dict:
        return {
            "name": feat.name,
            "category": feat.category,
            "description": feat.description[:200] + "..." if len(feat.description) > 200 else feat.description,
            "prerequisites": feat.prerequisites,
            "benefits": feat.benefits[:3] if hasattr(feat, 'benefits') else [],
            "repeatable": getattr(feat, 'repeatable', False),
        }

    # Species queries
    def get_species(self, name: str) -> Optional[dict]:
        """Get a species by name."""
        self._load_species()
        name_lower = name.lower()

        # Handle both dict and list formats
        species_list = self._species.values() if isinstance(self._species, dict) else self._species

        for species in species_list:
            if species.name.lower() == name_lower:
                return self._species_to_dict(species)
        return None

    def _species_to_dict(self, species) -> dict:
        """Convert a species object to a dict."""
        traits = []
        for t in species.traits:
            traits.append({
                "name": t.name,
                "description": t.description,
            })

        return {
            "name": species.name,
            "size": species.size,
            "speed": species.speed,
            "description": species.description[:300] + "..." if len(species.description) > 300 else species.description,
            "ability_bonuses": getattr(species, 'ability_bonuses', {}),
            "languages": getattr(species, 'languages', []),
            "darkvision": getattr(species, 'darkvision', 0),
            "traits": traits,
            "has_subraces": bool(species.subraces),
            "subraces": [s.name for s in species.subraces] if species.subraces else [],
        }

    def list_species(self) -> QueryResult:
        """List all available species."""
        self._load_species()
        results = []

        # Handle both dict and list formats
        species_list = self._species.values() if isinstance(self._species, dict) else self._species

        for species in species_list:
            results.append({
                "name": species.name,
                "size": species.size,
                "speed": species.speed,
                "has_subraces": bool(species.subraces),
            })
        return QueryResult(
            query_type="species",
            data=results,
            total_count=len(results),
            has_more=False,
            summary=f"{len(results)} playable species available",
        )

    # Data summary for AI context
    def get_data_summary(self) -> str:
        """Get a summary of available data for AI context."""
        self._load_spells()
        self._load_monsters()
        self._load_items()
        self._load_classes()
        self._load_species()
        self._load_feats()
        self._load_subclasses()

        spell_levels = {}
        for spell in self._spells:
            level = spell.level
            spell_levels[level] = spell_levels.get(level, 0) + 1

        monster_crs = {}
        for monster in self._monsters:
            cr = monster.challenge_rating
            monster_crs[cr] = monster_crs.get(cr, 0) + 1

        item_rarities = {}
        for item in self._items["magic"]:
            rarity = item.rarity
            item_rarities[rarity] = item_rarities.get(rarity, 0) + 1

        summary = f"""Game Data Available:
- Spells: {len(self._spells)} total ({', '.join(f'L{k}: {v}' for k, v in sorted(spell_levels.items()))})
- Monsters: {len(self._monsters)} total (CR range: {', '.join(f'{k}: {v}' for k, v in sorted(monster_crs.items(), key=lambda x: float(x[0].replace('/', '.')) if '/' in x[0] else float(x[0])))})
- Magic Items: {len(self._items['magic'])} total ({', '.join(f'{k}: {v}' for k, v in item_rarities.items())})
- Classes: {len(self._classes)} ({', '.join(c.name for c in self._classes)})
- Subclasses: {len(self._subclasses)} total
- Species: {len(self._species)} ({', '.join(s.name for s in self._species)})
- Feats: {len(self._feats)} total"""

        return summary


# Singleton instance
_semantic_layer: Optional[SemanticLayer] = None


def get_semantic_layer() -> SemanticLayer:
    """Get the semantic layer singleton."""
    global _semantic_layer
    if _semantic_layer is None:
        _semantic_layer = SemanticLayer()
    return _semantic_layer


def query_game_data(query_type: str, **kwargs) -> QueryResult:
    """High-level query interface for game data.

    Args:
        query_type: Type of query - spell, monster, item, class, subclass, feat, species
        **kwargs: Query-specific parameters

    Returns:
        QueryResult with matching data
    """
    layer = get_semantic_layer()

    if query_type == "spell":
        if "name" in kwargs:
            result = layer.get_spell(kwargs["name"])
            if result:
                return QueryResult("spell", [result], 1, False, f"Found spell: {result['name']}")
            return QueryResult("spell", [], 0, False, f"Spell not found: {kwargs['name']}")
        return layer.search_spells(**kwargs)

    elif query_type == "monster":
        if "name" in kwargs:
            result = layer.get_monster(kwargs["name"])
            if result:
                return QueryResult("monster", [result], 1, False, f"Found monster: {result['name']}")
            return QueryResult("monster", [], 0, False, f"Monster not found: {kwargs['name']}")
        return layer.search_monsters(**kwargs)

    elif query_type == "item" or query_type == "magic_item":
        if "name" in kwargs:
            result = layer.get_magic_item(kwargs["name"])
            if result:
                return QueryResult("magic_item", [result], 1, False, f"Found item: {result['name']}")
            return QueryResult("magic_item", [], 0, False, f"Item not found: {kwargs['name']}")
        return layer.search_magic_items(**kwargs)

    elif query_type == "class":
        if "name" in kwargs:
            result = layer.get_class_info(kwargs["name"])
            if result:
                return QueryResult("class", [result], 1, False, f"Found class: {result['name']}")
            return QueryResult("class", [], 0, False, f"Class not found: {kwargs['name']}")
        return QueryResult("class", [], 0, False, "Specify class name")

    elif query_type == "subclass":
        if "class_name" in kwargs:
            return layer.get_subclasses_for_class(kwargs["class_name"])
        return QueryResult("subclass", [], 0, False, "Specify parent class name")

    elif query_type == "feat":
        if "name" in kwargs:
            result = layer.get_feat(kwargs["name"])
            if result:
                return QueryResult("feat", [result], 1, False, f"Found feat: {result['name']}")
            return QueryResult("feat", [], 0, False, f"Feat not found: {kwargs['name']}")
        return layer.search_feats(**kwargs)

    elif query_type == "species":
        if "name" in kwargs:
            result = layer.get_species(kwargs["name"])
            if result:
                return QueryResult("species", [result], 1, False, f"Found species: {result['name']}")
            return QueryResult("species", [], 0, False, f"Species not found: {kwargs['name']}")
        return layer.list_species()

    elif query_type == "encounter":
        party_level = kwargs.get("party_level", 5)
        party_size = kwargs.get("party_size", 4)
        return layer.get_monsters_for_encounter(party_level, party_size)

    else:
        return QueryResult(query_type, [], 0, False, f"Unknown query type: {query_type}")
