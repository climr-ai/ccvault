"""Tool registry for AI-callable tools."""

from typing import Callable, Optional

from dnd_manager.ai.tools.schema import ToolCategory, ToolDefinition


class ToolRegistry:
    """Registry for AI-callable tools.

    This is a singleton that holds all registered tools and their handlers.
    Tools are registered at module load time and can be discovered by category.
    """

    _instance: Optional["ToolRegistry"] = None

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._tools: dict[str, ToolDefinition] = {}
        self._handlers: dict[str, Callable] = {}
        self._initialized = False

    @classmethod
    def get_instance(cls) -> "ToolRegistry":
        """Get the singleton instance, creating if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing)."""
        cls._instance = None

    def _ensure_initialized(self) -> None:
        """Ensure built-in tools are registered."""
        if self._initialized:
            return
        self._initialized = True
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        """Register all built-in tools."""
        # Import definitions and handlers
        from dnd_manager.ai.tools.definitions import (
            query_tools,
            combat_tools,
            character_tools,
            spell_tools,
            inventory_tools,
            custom_tools,
            ruleset_tools,
        )
        from dnd_manager.ai.tools.handlers import (
            query_handlers,
            combat_handlers,
            character_handlers,
            spell_handlers,
            inventory_handlers,
            custom_handlers,
            ruleset_handlers,
        )

        # Register query tools
        self.register(query_tools.GET_CHARACTER_SUMMARY, query_handlers.get_character_summary)
        self.register(query_tools.GET_ABILITY_SCORES, query_handlers.get_ability_scores)
        self.register(query_tools.GET_SPELL_SLOTS, query_handlers.get_spell_slots)
        self.register(query_tools.GET_INVENTORY, query_handlers.get_inventory)
        self.register(query_tools.CHECK_MULTICLASS_REQUIREMENTS, query_handlers.check_multiclass_requirements)

        # Register combat tools
        self.register(combat_tools.DEAL_DAMAGE, combat_handlers.deal_damage)
        self.register(combat_tools.HEAL_CHARACTER, combat_handlers.heal_character)
        self.register(combat_tools.TAKE_SHORT_REST, combat_handlers.take_short_rest)
        self.register(combat_tools.TAKE_LONG_REST, combat_handlers.take_long_rest)
        self.register(combat_tools.SPEND_HIT_DIE, combat_handlers.spend_hit_die)
        self.register(combat_tools.MODIFY_DEATH_SAVES, combat_handlers.modify_death_saves)

        # Register character tools
        self.register(character_tools.SET_ABILITY_SCORE, character_handlers.set_ability_score)
        self.register(character_tools.ADD_ABILITY_BONUS, character_handlers.add_ability_bonus)
        self.register(character_tools.LEVEL_UP, character_handlers.level_up)
        self.register(character_tools.ADD_FEATURE, character_handlers.add_feature)
        self.register(character_tools.REMOVE_FEATURE, character_handlers.remove_feature)

        # Register spell tools
        self.register(spell_tools.ADD_SPELL, spell_handlers.add_spell)
        self.register(spell_tools.REMOVE_SPELL, spell_handlers.remove_spell)
        self.register(spell_tools.USE_SPELL_SLOT, spell_handlers.use_spell_slot)
        self.register(spell_tools.RESTORE_SPELL_SLOT, spell_handlers.restore_spell_slot)

        # Register inventory tools
        self.register(inventory_tools.ADD_ITEM, inventory_handlers.add_item)
        self.register(inventory_tools.REMOVE_ITEM, inventory_handlers.remove_item)
        self.register(inventory_tools.EQUIP_ITEM, inventory_handlers.equip_item)
        self.register(inventory_tools.ATTUNE_ITEM, inventory_handlers.attune_item)
        self.register(inventory_tools.MODIFY_CURRENCY, inventory_handlers.modify_currency)

        # Register custom tools
        self.register(custom_tools.MODIFY_CUSTOM_STAT, custom_handlers.modify_custom_stat)
        self.register(custom_tools.ADD_NOTE, custom_handlers.add_note)
        self.register(custom_tools.SET_PERSONALITY_TRAIT, custom_handlers.set_personality_trait)

        # Register ruleset data query tools
        self.register(ruleset_tools.LOOKUP_SPELL, ruleset_handlers.handle_lookup_spell)
        self.register(ruleset_tools.SEARCH_SPELLS, ruleset_handlers.handle_search_spells)
        self.register(ruleset_tools.GET_CLASS_SPELLS, ruleset_handlers.handle_get_class_spells)
        self.register(ruleset_tools.LOOKUP_CLASS, ruleset_handlers.handle_lookup_class)
        self.register(ruleset_tools.GET_SUBCLASSES, ruleset_handlers.handle_get_subclasses)
        self.register(ruleset_tools.LOOKUP_SPECIES, ruleset_handlers.handle_lookup_species)
        self.register(ruleset_tools.LIST_SPECIES, ruleset_handlers.handle_list_species)
        self.register(ruleset_tools.LOOKUP_FEAT, ruleset_handlers.handle_lookup_feat)
        self.register(ruleset_tools.SEARCH_FEATS, ruleset_handlers.handle_search_feats)
        self.register(ruleset_tools.LOOKUP_MAGIC_ITEM, ruleset_handlers.handle_lookup_magic_item)
        self.register(ruleset_tools.SEARCH_MAGIC_ITEMS, ruleset_handlers.handle_search_magic_items)
        self.register(ruleset_tools.LOOKUP_MONSTER, ruleset_handlers.handle_lookup_monster)
        self.register(ruleset_tools.SEARCH_MONSTERS, ruleset_handlers.handle_search_monsters)
        self.register(ruleset_tools.GET_ENCOUNTER_MONSTERS, ruleset_handlers.handle_get_encounter_monsters)

    def register(self, tool: ToolDefinition, handler: Callable) -> None:
        """Register a tool with its handler.

        Args:
            tool: Tool definition
            handler: Async function that executes the tool
        """
        self._tools[tool.name] = tool
        self._handlers[tool.name] = handler
        tool.handler = handler

    def unregister(self, tool_name: str) -> bool:
        """Unregister a tool.

        Args:
            tool_name: Name of tool to remove

        Returns:
            True if tool was removed, False if not found
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            del self._handlers[tool_name]
            return True
        return False

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool definition by name.

        Args:
            name: Tool name

        Returns:
            Tool definition or None if not found
        """
        self._ensure_initialized()
        return self._tools.get(name)

    def get_handler(self, name: str) -> Optional[Callable]:
        """Get a tool handler by name.

        Args:
            name: Tool name

        Returns:
            Handler function or None if not found
        """
        self._ensure_initialized()
        return self._handlers.get(name)

    def get_all_tools(self) -> list[ToolDefinition]:
        """Get all registered tools.

        Returns:
            List of all tool definitions
        """
        self._ensure_initialized()
        return list(self._tools.values())

    def get_tools_by_category(self, category: ToolCategory) -> list[ToolDefinition]:
        """Get tools filtered by category.

        Args:
            category: Category to filter by

        Returns:
            List of tools in that category
        """
        self._ensure_initialized()
        return [t for t in self._tools.values() if t.category == category]

    def get_anthropic_tool_definitions(
        self,
        categories: Optional[list[ToolCategory]] = None,
    ) -> list[dict]:
        """Get tool definitions in Anthropic format.

        Args:
            categories: Optional list of categories to include

        Returns:
            List of tool dicts compatible with Anthropic API
        """
        self._ensure_initialized()
        tools = self._tools.values()
        if categories:
            tools = [t for t in tools if t.category in categories]
        return [t.to_anthropic_format() for t in tools]

    def list_tool_names(self) -> list[str]:
        """Get names of all registered tools.

        Returns:
            List of tool names
        """
        self._ensure_initialized()
        return list(self._tools.keys())


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance.

    Returns:
        The singleton ToolRegistry
    """
    return ToolRegistry.get_instance()
