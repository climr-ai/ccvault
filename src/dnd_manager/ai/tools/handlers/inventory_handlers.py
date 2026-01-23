"""Inventory management tool handlers."""

from typing import Any, Optional

from dnd_manager.models.character import Character, InventoryItem


async def add_item(
    character: Character,
    name: str,
    quantity: int = 1,
    weight: Optional[float] = None,
    description: Optional[str] = None,
    equipped: bool = False,
) -> dict[str, Any]:
    """Add an item to inventory."""
    # Ensure equipment.items exists
    if character.equipment.items is None:
        character.equipment.items = []

    # Check if item already exists
    existing = next(
        (i for i in character.equipment.items if i.name.lower() == name.lower()),
        None
    )

    if existing:
        existing.quantity += quantity
        changes = [f"Added {quantity}x {name} (now have {existing.quantity})"]
    else:
        item = InventoryItem(
            name=name,
            quantity=quantity,
            weight=weight,
            description=description or "",
            equipped=equipped,
        )
        character.equipment.items.append(item)
        changes = [f"Added {quantity}x {name} to inventory"]
        if equipped:
            changes.append(f"{name} is equipped")

    character.update_modified()

    return {
        "data": {
            "name": name,
            "quantity": quantity,
            "total_items": len(character.equipment.items),
            "total_weight": character.equipment.total_weight,
        },
        "changes": changes,
    }


async def remove_item(
    character: Character,
    name: str,
    quantity: Optional[int] = None,
) -> dict[str, Any]:
    """Remove an item from inventory."""
    items = character.equipment.items if character.equipment and character.equipment.items else []
    item = next(
        (i for i in items if i.name.lower() == name.lower()),
        None
    )

    if not item:
        raise ValueError(f"Item '{name}' not found in inventory")

    if quantity is None or quantity >= item.quantity:
        # Remove entirely
        character.equipment.items.remove(item)
        removed = item.quantity
        changes = [f"Removed all {removed}x {name}"]
    else:
        # Remove partial
        item.quantity -= quantity
        removed = quantity
        changes = [f"Removed {quantity}x {name} ({item.quantity} remaining)"]

    character.update_modified()

    return {
        "data": {
            "name": name,
            "removed": removed,
            "remaining": item.quantity if item in character.equipment.items else 0,
        },
        "changes": changes,
    }


async def equip_item(
    character: Character,
    name: str,
    equipped: bool = True,
) -> dict[str, Any]:
    """Equip or unequip an item."""
    items = character.equipment.items if character.equipment and character.equipment.items else []
    item = next(
        (i for i in items if i.name.lower() == name.lower()),
        None
    )

    if not item:
        raise ValueError(f"Item '{name}' not found in inventory")

    old_status = item.equipped
    item.equipped = equipped
    character.update_modified()

    action = "equipped" if equipped else "unequipped"

    return {
        "data": {
            "name": name,
            "equipped": equipped,
            "was_equipped": old_status,
        },
        "changes": [f"{name} {action}"] if old_status != equipped else [f"{name} was already {action}"],
    }


async def attune_item(
    character: Character,
    name: str,
    attuned: bool = True,
) -> dict[str, Any]:
    """Attune or end attunement to an item."""
    item = next(
        (i for i in character.equipment.items if i.name.lower() == name.lower()),
        None
    )

    if not item:
        raise ValueError(f"Item '{name}' not found in inventory")

    # Check attunement limit
    if attuned and not item.attuned:
        current_attuned = character.equipment.attuned_count
        if current_attuned >= 3:
            raise ValueError("Cannot attune to more than 3 items. End attunement to another item first.")

    old_status = item.attuned
    item.attuned = attuned
    character.update_modified()

    action = "attuned to" if attuned else "ended attunement to"

    return {
        "data": {
            "name": name,
            "attuned": attuned,
            "was_attuned": old_status,
            "total_attuned": character.equipment.attuned_count,
        },
        "changes": [f"{action.title()} {name}"] if old_status != attuned else [f"Already {action} {name}"],
    }


async def modify_currency(
    character: Character,
    cp: int = 0,
    sp: int = 0,
    ep: int = 0,
    gp: int = 0,
    pp: int = 0,
) -> dict[str, Any]:
    """Add or remove currency."""
    currency = character.equipment.currency
    changes = []

    def update_currency(attr: str, amount: int, name: str) -> None:
        old_val = getattr(currency, attr)
        new_val = max(0, old_val + amount)
        setattr(currency, attr, new_val)
        if amount > 0:
            changes.append(f"+{amount} {name}")
        elif amount < 0:
            actual_removed = old_val - new_val
            changes.append(f"-{actual_removed} {name}")

    if cp: update_currency("cp", cp, "cp")
    if sp: update_currency("sp", sp, "sp")
    if ep: update_currency("ep", ep, "ep")
    if gp: update_currency("gp", gp, "gp")
    if pp: update_currency("pp", pp, "pp")

    character.update_modified()

    return {
        "data": {
            "currency": {
                "cp": currency.cp,
                "sp": currency.sp,
                "ep": currency.ep,
                "gp": currency.gp,
                "pp": currency.pp,
            },
            "total_gp_value": currency.total_gp,
        },
        "changes": changes or ["No currency changed"],
    }
