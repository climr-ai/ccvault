"""Handlers for ruleset data query tools."""

import json
from typing import Any, Optional

from dnd_manager.models.character import Character
from dnd_manager.ai.semantic import get_semantic_layer


def handle_lookup_spell(
    character: Optional[Character],
    name: str,
) -> dict[str, Any]:
    """Look up a spell by name."""
    layer = get_semantic_layer()
    result = layer.get_spell(name)

    if result:
        return {
            "found": True,
            "spell": result,
        }
    return {
        "found": False,
        "error": f"Spell '{name}' not found. Check the spelling or use search_spells to find similar spells.",
    }


def handle_search_spells(
    character: Optional[Character],
    query: str = "",
    level: Optional[int] = None,
    school: Optional[str] = None,
    class_name: Optional[str] = None,
    concentration: Optional[bool] = None,
    ritual: Optional[bool] = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for spells with filters."""
    layer = get_semantic_layer()
    result = layer.search_spells(
        query=query,
        level=level,
        school=school,
        class_name=class_name,
        concentration=concentration,
        ritual=ritual,
        limit=limit,
    )

    return {
        "spells": result.data,
        "total_count": result.total_count,
        "has_more": result.has_more,
        "summary": result.summary,
    }


def handle_get_class_spells(
    character: Optional[Character],
    class_name: str,
    max_level: int = 9,
) -> dict[str, Any]:
    """Get all spells available to a class."""
    layer = get_semantic_layer()
    result = layer.get_spells_for_class(class_name, max_level)

    # Group spells by level for better readability
    by_level = {}
    for spell in result.data:
        lvl = spell["level"]
        if lvl not in by_level:
            by_level[lvl] = []
        by_level[lvl].append(spell["name"])

    return {
        "class": class_name,
        "max_level": max_level,
        "total_spells": result.total_count,
        "spells_by_level": by_level,
        "summary": result.summary,
    }


def handle_lookup_class(
    character: Optional[Character],
    name: str,
) -> dict[str, Any]:
    """Look up a class by name."""
    layer = get_semantic_layer()
    result = layer.get_class_info(name)

    if result:
        return {
            "found": True,
            "class": result,
        }
    return {
        "found": False,
        "error": f"Class '{name}' not found. Available classes: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard",
    }


def handle_get_subclasses(
    character: Optional[Character],
    class_name: str,
) -> dict[str, Any]:
    """Get all subclasses for a class."""
    layer = get_semantic_layer()
    result = layer.get_subclasses_for_class(class_name)

    return {
        "class": class_name,
        "subclasses": result.data,
        "total_count": result.total_count,
        "summary": result.summary,
    }


def handle_lookup_species(
    character: Optional[Character],
    name: str,
) -> dict[str, Any]:
    """Look up a species by name."""
    layer = get_semantic_layer()
    result = layer.get_species(name)

    if result:
        return {
            "found": True,
            "species": result,
        }
    return {
        "found": False,
        "error": f"Species '{name}' not found. Use list_species to see available options.",
    }


def handle_list_species(
    character: Optional[Character],
) -> dict[str, Any]:
    """List all available species."""
    layer = get_semantic_layer()
    result = layer.list_species()

    return {
        "species": result.data,
        "total_count": result.total_count,
        "summary": result.summary,
    }


def handle_lookup_feat(
    character: Optional[Character],
    name: str,
) -> dict[str, Any]:
    """Look up a feat by name."""
    layer = get_semantic_layer()
    result = layer.get_feat(name)

    if result:
        return {
            "found": True,
            "feat": result,
        }
    return {
        "found": False,
        "error": f"Feat '{name}' not found. Use search_feats to find similar feats.",
    }


def handle_search_feats(
    character: Optional[Character],
    query: str = "",
    category: Optional[str] = None,
    has_prerequisites: Optional[bool] = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for feats with filters."""
    layer = get_semantic_layer()
    result = layer.search_feats(
        query=query,
        category=category,
        has_prerequisites=has_prerequisites,
        limit=limit,
    )

    return {
        "feats": result.data,
        "total_count": result.total_count,
        "has_more": result.has_more,
        "summary": result.summary,
    }


def handle_lookup_magic_item(
    character: Optional[Character],
    name: str,
) -> dict[str, Any]:
    """Look up a magic item by name."""
    layer = get_semantic_layer()
    result = layer.get_magic_item(name)

    if result:
        return {
            "found": True,
            "item": result,
        }
    return {
        "found": False,
        "error": f"Magic item '{name}' not found. Use search_magic_items to find similar items.",
    }


def handle_search_magic_items(
    character: Optional[Character],
    query: str = "",
    rarity: Optional[str] = None,
    item_type: Optional[str] = None,
    requires_attunement: Optional[bool] = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for magic items with filters."""
    layer = get_semantic_layer()
    result = layer.search_magic_items(
        query=query,
        rarity=rarity,
        item_type=item_type,
        requires_attunement=requires_attunement,
        limit=limit,
    )

    return {
        "items": result.data,
        "total_count": result.total_count,
        "has_more": result.has_more,
        "summary": result.summary,
    }


def handle_lookup_monster(
    character: Optional[Character],
    name: str,
) -> dict[str, Any]:
    """Look up a monster by name."""
    layer = get_semantic_layer()
    result = layer.get_monster(name)

    if result:
        return {
            "found": True,
            "monster": result,
        }
    return {
        "found": False,
        "error": f"Monster '{name}' not found. Use search_monsters to find similar monsters.",
    }


def handle_search_monsters(
    character: Optional[Character],
    query: str = "",
    cr_min: Optional[float] = None,
    cr_max: Optional[float] = None,
    monster_type: Optional[str] = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for monsters with filters."""
    layer = get_semantic_layer()
    result = layer.search_monsters(
        query=query,
        cr_min=cr_min,
        cr_max=cr_max,
        monster_type=monster_type,
        limit=limit,
    )

    return {
        "monsters": result.data,
        "total_count": result.total_count,
        "has_more": result.has_more,
        "summary": result.summary,
    }


def handle_get_encounter_monsters(
    character: Optional[Character],
    party_level: int,
    party_size: int = 4,
) -> dict[str, Any]:
    """Get monsters suitable for an encounter."""
    layer = get_semantic_layer()
    result = layer.get_monsters_for_encounter(party_level, party_size)

    # Group by CR for easier reading
    by_cr = {}
    for monster in result.data:
        cr = monster["cr"]
        if cr not in by_cr:
            by_cr[cr] = []
        by_cr[cr].append(monster["name"])

    return {
        "party_level": party_level,
        "party_size": party_size,
        "monsters_by_cr": by_cr,
        "total_suitable": result.total_count,
        "summary": result.summary,
    }


# Handler mapping
RULESET_HANDLERS = {
    "lookup_spell": handle_lookup_spell,
    "search_spells": handle_search_spells,
    "get_class_spells": handle_get_class_spells,
    "lookup_class": handle_lookup_class,
    "get_subclasses": handle_get_subclasses,
    "lookup_species": handle_lookup_species,
    "list_species": handle_list_species,
    "lookup_feat": handle_lookup_feat,
    "search_feats": handle_search_feats,
    "lookup_magic_item": handle_lookup_magic_item,
    "search_magic_items": handle_search_magic_items,
    "lookup_monster": handle_lookup_monster,
    "search_monsters": handle_search_monsters,
    "get_encounter_monsters": handle_get_encounter_monsters,
}
