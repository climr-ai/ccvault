"""Base interface for AI providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Optional, Union


class MessageRole(str, Enum):
    """Role of a message in the conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL_RESULT = "tool_result"  # For tool execution results


class ToolChoice(str, Enum):
    """Controls how the AI uses tools.

    AUTO: AI decides whether to use tools (default)
    ANY: AI must use at least one tool
    NONE: AI cannot use tools (text response only)
    """
    AUTO = "auto"
    ANY = "any"
    NONE = "none"


@dataclass
class ToolUseBlock:
    """Represents a tool use request from the AI."""
    id: str  # Unique ID for this tool use
    name: str  # Tool name
    input: dict[str, Any]  # Tool input parameters


@dataclass
class ToolResultBlock:
    """Represents the result of a tool execution."""
    tool_use_id: str  # Matches the ToolUseBlock id
    content: str  # Result content (typically JSON)
    is_error: bool = False  # Whether execution failed


# Type alias for message content that can include tool blocks
MessageContent = Union[str, list[Union[ToolUseBlock, ToolResultBlock]]]


@dataclass
class AIMessage:
    """A single message in the conversation."""
    role: MessageRole
    content: MessageContent
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dict for API calls."""
        if isinstance(self.content, str):
            return {"role": self.role.value, "content": self.content}
        # Handle tool blocks - serialize to list of dicts
        return {"role": self.role.value, "content": self._serialize_content()}

    def _serialize_content(self) -> list[dict]:
        """Serialize content blocks for API calls."""
        if isinstance(self.content, str):
            return [{"type": "text", "text": self.content}]
        result = []
        for block in self.content:
            if isinstance(block, ToolUseBlock):
                result.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
            elif isinstance(block, ToolResultBlock):
                result.append({
                    "type": "tool_result",
                    "tool_use_id": block.tool_use_id,
                    "content": block.content,
                    "is_error": block.is_error,
                })
        return result


@dataclass
class AIResponse:
    """Response from an AI provider."""
    content: str
    model: str
    provider: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    finish_reason: Optional[str] = None  # "end_turn", "tool_use", "max_tokens"
    timestamp: datetime = field(default_factory=datetime.now)
    tool_use: list[ToolUseBlock] = field(default_factory=list)  # Tool calls from AI

    @property
    def total_tokens(self) -> Optional[int]:
        """Total tokens used."""
        if self.input_tokens is not None and self.output_tokens is not None:
            return self.input_tokens + self.output_tokens
        return None

    @property
    def has_tool_use(self) -> bool:
        """Check if response contains tool use requests."""
        return len(self.tool_use) > 0


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'gemini', 'anthropic', 'openai')."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model to use."""
        pass

    @property
    @abstractmethod
    def available_models(self) -> list[str]:
        """List of available models."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider is properly configured (API key, etc.)."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        """Send a chat request and get a complete response.

        Args:
            messages: Conversation history
            model: Model to use (defaults to provider's default)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            Complete response from the AI
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Send a chat request and stream the response.

        Args:
            messages: Conversation history
            model: Model to use (defaults to provider's default)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Yields:
            Chunks of the response as they arrive
        """
        pass

    async def chat_with_tools(
        self,
        messages: list[AIMessage],
        tools: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        tool_choice: ToolChoice = ToolChoice.AUTO,
    ) -> AIResponse:
        """Send a chat request with tool definitions.

        This method enables function calling / tool use. The AI can request
        tool execution, and the caller is responsible for executing tools
        and feeding results back.

        Args:
            messages: Conversation history (may include tool results)
            tools: List of tool definitions in Anthropic format
            model: Model to use (defaults to provider's default)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            tool_choice: Controls tool usage:
                - AUTO: AI decides whether to use tools (default)
                - ANY: AI must use at least one tool
                - NONE: AI cannot use tools

        Returns:
            Response which may include tool_use requests in the tool_use field

        Note:
            Default implementation falls back to regular chat without tools.
            Providers that support tools should override this method.
        """
        # Default: fall back to regular chat without tools
        return await self.chat(messages, model, max_tokens, temperature)

    async def simple_chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """Simple one-shot chat for convenience.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model to use

        Returns:
            Response content as string
        """
        messages = []
        if system_prompt:
            messages.append(AIMessage(role=MessageRole.SYSTEM, content=system_prompt))
        messages.append(AIMessage(role=MessageRole.USER, content=prompt))

        response = await self.chat(messages, model=model)
        return response.content
