"""Tool session manager for AI conversations with function calling."""

from dataclasses import dataclass, field
from typing import Callable, Optional

from dnd_manager.models.character import Character
from dnd_manager.storage import CharacterStore
from dnd_manager.ai.base import (
    AIProvider,
    AIMessage,
    AIResponse,
    MessageRole,
    ToolChoice,
    ToolUseBlock,
    ToolResultBlock,
)
from dnd_manager.ai.context import build_system_prompt
from dnd_manager.ai.tools.registry import get_tool_registry
from dnd_manager.ai.tools.executor import ToolExecutor


@dataclass
class ToolSession:
    """Manages an AI conversation with tool calling capabilities.

    This class handles the full tool-use loop:
    1. Send user message to AI with tool definitions
    2. If AI requests tool use, execute tools
    3. Feed tool results back to AI
    4. Repeat until AI responds with text only
    5. Optionally save character changes

    Attributes:
        provider: AI provider to use for chat
        character: Optional character to operate on
        character_name: Character name for reloading
        store: Character store for persistence
        mode: AI mode (assistant, dm, roleplay, etc.)
        auto_save: Whether to save after tool modifications
        max_tool_iterations: Maximum tool call loops (safety limit)
    """

    provider: AIProvider
    character: Optional[Character] = None
    character_name: Optional[str] = None
    store: Optional[CharacterStore] = None
    mode: str = "assistant"
    auto_save: bool = True
    max_tool_iterations: int = 10

    # Internal state (initialized in __post_init__)
    messages: list[AIMessage] = field(default_factory=list, init=False)
    _executor: ToolExecutor = field(init=False)
    _registry: "ToolRegistry" = field(init=False)
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Initialize session state."""
        self._registry = get_tool_registry()
        self._executor = ToolExecutor(
            character=self.character,
            auto_confirm=False,
        )

    def _ensure_initialized(self) -> None:
        """Ensure system prompt is set up."""
        if self._initialized:
            return
        self._initialized = True

        # Build initial system prompt
        system_prompt = self._build_system_prompt()
        self.messages.append(AIMessage(
            role=MessageRole.SYSTEM,
            content=system_prompt,
        ))

    def _build_system_prompt(self) -> str:
        """Build system prompt with tool instructions."""
        # Base prompt already includes comprehensive tool guidance
        base_prompt = build_system_prompt(self.character, mode=self.mode)

        # Add character-specific tool reminder
        tool_reminder = """

## Character Management

You are managing this character's state. When the user asks to:
- Track damage/healing: Use deal_damage or heal_character
- Rest: Use take_short_rest or take_long_rest
- Level up: Use level_up (it handles HP and spell slots automatically)
- Manage spells: Use add_spell, remove_spell, use_spell_slot
- Manage inventory: Use add_item, remove_item, equip_item

IMPORTANT:
- Use get_character_summary if you need to see current state
- Explain changes before and after making them
- Confirm significant changes (like leveling up) before executing
"""
        return base_prompt + tool_reminder

    async def chat(
        self,
        user_message: str,
        stream_callback: Optional[Callable[[str], None]] = None,
        require_tools: bool = False,
    ) -> str:
        """Process a user message, potentially with tool use.

        Args:
            user_message: The user's input
            stream_callback: Optional callback for streaming text chunks
            require_tools: If True, force the AI to use at least one tool

        Returns:
            The final assistant response text
        """
        self._ensure_initialized()

        # Add user message
        self.messages.append(AIMessage(
            role=MessageRole.USER,
            content=user_message,
        ))

        # Get tool definitions
        tools = self._registry.get_anthropic_tool_definitions()

        # Determine tool choice - force tools on first iteration if required
        tool_choice = ToolChoice.ANY if require_tools else ToolChoice.AUTO

        # Iterate until no more tool use or max iterations
        iterations = 0
        final_response = ""

        while iterations < self.max_tool_iterations:
            iterations += 1

            # Call AI with tools
            response = await self.provider.chat_with_tools(
                messages=self.messages,
                tools=tools,
                tool_choice=tool_choice,
            )

            # After first iteration, switch back to AUTO
            tool_choice = ToolChoice.AUTO

            # Stream any text content
            if response.content and stream_callback:
                stream_callback(response.content)

            # If no tool use, we're done
            if not response.has_tool_use:
                final_response = response.content
                self.messages.append(AIMessage(
                    role=MessageRole.ASSISTANT,
                    content=response.content,
                ))
                break

            # Accumulate text content
            final_response = response.content

            # Add assistant message with tool use blocks
            self.messages.append(AIMessage(
                role=MessageRole.ASSISTANT,
                content=response.tool_use,  # List of ToolUseBlocks
            ))

            # Execute tools and collect results
            tool_results = []
            character_modified = False

            for tool_use in response.tool_use:
                result = await self._executor.execute(
                    tool_name=tool_use.name,
                    tool_input=tool_use.input,
                    tool_use_id=tool_use.id,
                )

                tool_results.append(ToolResultBlock(
                    tool_use_id=tool_use.id,
                    content=result.to_json(),
                    is_error=not result.success,
                ))

                if result.success and result.changes_made:
                    character_modified = True

            # Add tool results message
            self.messages.append(AIMessage(
                role=MessageRole.TOOL_RESULT,
                content=tool_results,
            ))

            # Save character if modified
            if character_modified and self.auto_save:
                self._save_character()

        return final_response

    def _save_character(self) -> None:
        """Save character state to storage."""
        if self.store and self.character:
            self.store.save(self.character)

    def refresh_character(self) -> None:
        """Reload character from storage."""
        if self.store and self.character_name:
            self.character = self.store.load(self.character_name)
            self._executor.character = self.character

    def clear_history(self) -> None:
        """Clear conversation history, keeping system prompt."""
        if self.messages:
            system_msg = self.messages[0]  # Keep system prompt
            self.messages = [system_msg]

    def get_message_count(self) -> int:
        """Get number of messages in conversation."""
        return len(self.messages)

    def set_confirmation_callback(
        self,
        callback: Callable[[str], bool],
    ) -> None:
        """Set callback for confirmation prompts.

        Args:
            callback: Function that takes a prompt string and returns True/False
        """
        self._executor.confirmation_callback = callback
