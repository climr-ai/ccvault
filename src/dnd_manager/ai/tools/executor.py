"""Tool executor with validation and safety checks."""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from dnd_manager.models.character import Character
from dnd_manager.ai.tools.schema import ToolDefinition, ToolRiskLevel
from dnd_manager.ai.tools.registry import get_tool_registry

logger = logging.getLogger(__name__)


@dataclass
class ToolExecutionResult:
    """Result of tool execution.

    Attributes:
        success: Whether execution succeeded
        result: Result data from the handler
        error: Error message if failed
        changes_made: List of changes for logging/display
        requires_confirmation: If True, user must confirm before execution
        confirmation_prompt: Prompt to show user for confirmation
    """
    success: bool
    result: Any
    error: Optional[str] = None
    changes_made: list[str] = field(default_factory=list)
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None

    def to_json(self) -> str:
        """Convert to JSON string for AI response.

        Returns:
            JSON string representing the result
        """
        if self.success:
            return json.dumps({
                "success": True,
                "result": self.result,
                "changes": self.changes_made,
            }, default=str)
        return json.dumps({
            "success": False,
            "error": self.error,
        })

    @classmethod
    def error_result(cls, error: str) -> "ToolExecutionResult":
        """Create an error result.

        Args:
            error: Error message

        Returns:
            ToolExecutionResult with success=False
        """
        return cls(success=False, result=None, error=error)

    @classmethod
    def confirmation_required(cls, prompt: str) -> "ToolExecutionResult":
        """Create a confirmation-required result.

        Args:
            prompt: Confirmation prompt to show

        Returns:
            ToolExecutionResult requesting confirmation
        """
        return cls(
            success=False,
            result=None,
            requires_confirmation=True,
            confirmation_prompt=prompt,
        )


class ToolExecutor:
    """Executes tools with validation and safety checks.

    This class handles:
    - Input validation against tool schemas
    - Safety confirmation for destructive operations
    - Handler invocation with character context
    - Error handling and logging
    """

    def __init__(
        self,
        character: Optional[Character] = None,
        auto_confirm: bool = False,
        confirmation_callback: Optional[Callable[[str], bool]] = None,
    ) -> None:
        """Initialize the executor.

        Args:
            character: Character to operate on
            auto_confirm: Auto-confirm destructive operations (dangerous!)
            confirmation_callback: Sync callback for confirmation prompts
        """
        self.character = character
        self.auto_confirm = auto_confirm
        self.confirmation_callback = confirmation_callback
        self._registry = get_tool_registry()
        self._pending_confirmations: dict[str, dict] = {}

    async def execute(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_use_id: str,
    ) -> ToolExecutionResult:
        """Execute a tool with validation.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters from AI
            tool_use_id: Unique ID for this tool use

        Returns:
            ToolExecutionResult with outcome
        """
        # Get tool definition
        tool = self._registry.get_tool(tool_name)
        if not tool:
            return ToolExecutionResult.error_result(f"Unknown tool: {tool_name}")

        # Check if character is required
        if tool.requires_character and self.character is None:
            return ToolExecutionResult.error_result(
                f"Tool '{tool_name}' requires a character to be loaded"
            )

        # Validate input against schema
        validation_error = tool.validate_input(tool_input)
        if validation_error:
            return ToolExecutionResult.error_result(validation_error)

        # Check if confirmation needed
        if tool.risk_level == ToolRiskLevel.DESTRUCTIVE and not self.auto_confirm:
            return await self._handle_confirmation(tool, tool_input, tool_use_id)

        # Execute the tool
        return await self._execute_handler(tool, tool_input)

    async def _handle_confirmation(
        self,
        tool: ToolDefinition,
        tool_input: dict,
        tool_use_id: str,
    ) -> ToolExecutionResult:
        """Handle confirmation for destructive operations.

        Args:
            tool: Tool definition
            tool_input: Input parameters
            tool_use_id: Unique ID for this tool use

        Returns:
            Execution result or confirmation request
        """
        prompt = self._build_confirmation_prompt(tool, tool_input)

        if self.confirmation_callback:
            # Synchronous confirmation via callback
            confirmed = self.confirmation_callback(prompt)
            if confirmed:
                return await self._execute_handler(tool, tool_input)
            return ToolExecutionResult.error_result("Operation cancelled by user")

        # Store pending confirmation for later
        self._pending_confirmations[tool_use_id] = {
            "tool": tool,
            "input": tool_input,
        }

        return ToolExecutionResult.confirmation_required(prompt)

    def _build_confirmation_prompt(
        self, tool: ToolDefinition, tool_input: dict
    ) -> str:
        """Build a human-readable confirmation prompt.

        Args:
            tool: Tool definition
            tool_input: Input parameters

        Returns:
            Confirmation prompt string
        """
        prompts = {
            "level_up": lambda i: f"Level up character in {i.get('class_name', 'primary class')}?",
            "remove_feature": lambda i: f"Remove feature '{i.get('name', 'unknown')}'?",
            "remove_spell": lambda i: f"Remove spell '{i.get('spell_name', 'unknown')}'?",
            "remove_item": lambda i: f"Remove item '{i.get('name', 'unknown')}'?",
        }

        builder = prompts.get(tool.name)
        if builder:
            return builder(tool_input)
        return f"Execute {tool.name} with {tool_input}?"

    async def _execute_handler(
        self,
        tool: ToolDefinition,
        tool_input: dict,
    ) -> ToolExecutionResult:
        """Execute the tool handler.

        Args:
            tool: Tool definition
            tool_input: Input parameters

        Returns:
            Execution result
        """
        handler = self._registry.get_handler(tool.name)
        if not handler:
            return ToolExecutionResult.error_result(
                f"No handler registered for tool: {tool.name}"
            )

        try:
            # Execute handler with character context
            result = await handler(self.character, **tool_input)
            return ToolExecutionResult(
                success=True,
                result=result.get("data"),
                changes_made=result.get("changes", []),
            )
        except Exception as e:
            logger.exception(f"Tool execution failed: {tool.name}")
            return ToolExecutionResult.error_result(str(e))

    def has_pending_confirmation(self, tool_use_id: str) -> bool:
        """Check if a tool use has pending confirmation.

        Args:
            tool_use_id: Tool use ID to check

        Returns:
            True if confirmation is pending
        """
        return tool_use_id in self._pending_confirmations

    async def execute_confirmed(self, tool_use_id: str) -> ToolExecutionResult:
        """Execute a confirmed pending operation.

        Args:
            tool_use_id: Tool use ID to execute

        Returns:
            Execution result
        """
        pending = self._pending_confirmations.pop(tool_use_id, None)
        if not pending:
            return ToolExecutionResult.error_result("No pending confirmation found")

        return await self._execute_handler(pending["tool"], pending["input"])

    def cancel_pending(self, tool_use_id: str) -> bool:
        """Cancel a pending confirmation.

        Args:
            tool_use_id: Tool use ID to cancel

        Returns:
            True if cancelled, False if not found
        """
        if tool_use_id in self._pending_confirmations:
            del self._pending_confirmations[tool_use_id]
            return True
        return False

    def clear_pending(self) -> int:
        """Clear all pending confirmations.

        Returns:
            Number of confirmations cleared
        """
        count = len(self._pending_confirmations)
        self._pending_confirmations.clear()
        return count
