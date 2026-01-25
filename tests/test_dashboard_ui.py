"""UI interaction tests for the main dashboard and detail overlay."""

import pytest

from dnd_manager.app import (
    AbilityBlock,
    ClickableListItem,
    DashboardPanel,
    DetailOverlay,
    DNDManagerApp,
    MainDashboard,
)
from dnd_manager.data import get_armor_by_name
from dnd_manager.models.abilities import AbilityScore
from dnd_manager.models.character import Character, CharacterClass, InventoryItem, RulesetId


def _make_character() -> Character:
    char = Character(primary_class=CharacterClass(name="Fighter", level=1), name="UI Tester")
    char.meta.ruleset = RulesetId.DND_2024
    char.proficiencies.weapons = ["Simple", "Martial"]
    char.abilities.dexterity = AbilityScore(base=14)
    char.equipment.items = [
        InventoryItem(name="Longsword", equipped=True),
        InventoryItem(name="Chain Mail", equipped=False),
        InventoryItem(name="Shield", equipped=False),
    ]
    char.apply_equipment_effects()
    return char


@pytest.mark.asyncio
async def test_dashboard_tab_cycles_focus():
    app = DNDManagerApp()
    char = _make_character()
    async with app.run_test() as pilot:
        app.current_character = char
        app.push_screen(MainDashboard(char))
        await pilot.pause()

        screen = app.screen
        panels = list(screen.query(DashboardPanel))
        assert panels
        assert app.focused == panels[0]

        await pilot.press("tab")
        assert app.focused != panels[0]


@pytest.mark.asyncio
async def test_dashboard_arrow_moves_selection_in_focused_pane():
    app = DNDManagerApp()
    char = _make_character()
    async with app.run_test() as pilot:
        app.current_character = char
        app.push_screen(MainDashboard(char))
        await pilot.pause()

        screen = app.screen
        # Use _pane_order to get the correct index for _focus_pane
        skills_pane = next(p for p in screen._pane_order if p.pane_id == "skills")
        screen._focus_pane(screen._pane_order.index(skills_pane))
        await pilot.pause()

        start_index = skills_pane.selected_index
        await pilot.press("down")
        assert skills_pane.selected_index == start_index + 1


@pytest.mark.asyncio
async def test_double_click_opens_detail_overlay():
    app = DNDManagerApp()
    char = _make_character()
    async with app.run_test() as pilot:
        app.current_character = char
        app.push_screen(MainDashboard(char))
        await pilot.pause()

        ability_panel = app.screen.query(AbilityBlock).first()
        item = ability_panel.query(ClickableListItem).first()
        await pilot.double_click(item)
        await pilot.pause()

        assert isinstance(app.screen, DetailOverlay)


@pytest.mark.asyncio
async def test_detail_overlay_toggles_equipped_and_updates_ac():
    app = DNDManagerApp()
    char = _make_character()
    armor_item = next(i for i in char.equipment.items if i.name == "Chain Mail")
    base_ac = char.combat.armor_class

    async with app.run_test() as pilot:
        app.current_character = char
        overlay = DetailOverlay(char, "inventory", armor_item)
        app.push_screen(overlay)
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause()

        assert armor_item.equipped is True
        armor = get_armor_by_name("Chain Mail")
        assert armor is not None
        assert char.combat.armor_class == armor.base_ac
        assert char.combat.armor_class != base_ac


@pytest.mark.asyncio
async def test_detail_overlay_hold_main_clears_other_items():
    app = DNDManagerApp()
    char = _make_character()
    sword = next(i for i in char.equipment.items if i.name == "Longsword")
    shield = next(i for i in char.equipment.items if i.name == "Shield")

    async with app.run_test() as pilot:
        app.current_character = char
        overlay = DetailOverlay(char, "inventory", sword)
        app.push_screen(overlay)
        await pilot.pause()

        await pilot.press("1")
        assert sword.held == "main"

        app.pop_screen()
        overlay = DetailOverlay(char, "inventory", shield)
        app.push_screen(overlay)
        await pilot.pause()

        await pilot.press("1")
        assert shield.held == "main"
        assert sword.held is None
