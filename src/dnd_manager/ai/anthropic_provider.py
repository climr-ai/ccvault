"""Anthropic Claude AI provider."""

import os
from typing import AsyncIterator, Optional

from dnd_manager.ai.base import (
    AIMessage,
    AIProvider,
    AIResponse,
    MessageRole,
    ToolChoice,
    ToolUseBlock,
    ToolResultBlock,
)


class AnthropicProvider(AIProvider):
    """Anthropic Claude AI provider."""

    MODELS = [
        "claude-opus-4-5-20251101",   # Most capable
        "claude-sonnet-4-20250514",   # Balanced
        "claude-3-5-sonnet-20241022", # Previous gen
        "claude-3-5-haiku-20241022",  # Fast and cheap
    ]

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Anthropic provider.

        Args:
            api_key: API key (uses config/env if not provided)
        """
        # Get API key from config or environment
        if api_key is None:
            from dnd_manager.config import get_config_manager
            manager = get_config_manager()
            api_key = manager.get_api_key("anthropic")

        self._api_key = api_key
        self._client = None

    def _get_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self._api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
        return self._client

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return "claude-3-5-haiku-20241022"  # Fast and affordable

    @property
    def available_models(self) -> list[str]:
        return self.MODELS.copy()

    def is_configured(self) -> bool:
        return self._api_key is not None

    def _convert_messages(self, messages: list[AIMessage]) -> tuple[Optional[str], list[dict]]:
        """Convert messages to Anthropic format.

        Returns:
            Tuple of (system_prompt, messages)
        """
        system_prompt = None
        converted = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_prompt = msg.content
            else:
                converted.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })

        return system_prompt, converted

    async def chat(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        """Send a chat request to Claude."""
        client = self._get_client()
        model_name = model or self.default_model

        system_prompt, converted_messages = self._convert_messages(messages)

        kwargs = {
            "model": model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": converted_messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await client.messages.create(**kwargs)

        return AIResponse(
            content=response.content[0].text,
            model=model_name,
            provider=self.name,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=response.stop_reason,
        )

    async def chat_stream(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a chat response from Claude."""
        client = self._get_client()
        model_name = model or self.default_model

        system_prompt, converted_messages = self._convert_messages(messages)

        kwargs = {
            "model": model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": converted_messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        async with client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    async def chat_with_tools(
        self,
        messages: list[AIMessage],
        tools: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        tool_choice: ToolChoice = ToolChoice.AUTO,
    ) -> AIResponse:
        """Send a chat request with tools to Claude.

        This enables function calling. The AI can request tool execution,
        and the caller is responsible for executing tools and feeding
        results back in subsequent messages.

        Args:
            messages: Conversation history (may include tool results)
            tools: List of tool definitions in Anthropic format
            model: Model to use (defaults to default_model)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            tool_choice: Controls tool usage (AUTO, ANY, NONE)

        Returns:
            AIResponse which may include tool_use requests
        """
        client = self._get_client()
        model_name = model or self.default_model

        system_prompt, converted_messages = self._convert_messages_with_tools(messages)

        kwargs = {
            "model": model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": converted_messages,
            "tools": tools,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        # Set tool_choice based on enum
        if tool_choice == ToolChoice.ANY:
            kwargs["tool_choice"] = {"type": "any"}
        elif tool_choice == ToolChoice.NONE:
            # Don't pass tools if NONE is specified
            del kwargs["tools"]
        # AUTO is the default, no need to specify

        response = await client.messages.create(**kwargs)

        # Parse response for tool use blocks
        tool_use_blocks = []
        text_content = ""

        for block in response.content:
            if block.type == "text":
                text_content += block.text
            elif block.type == "tool_use":
                tool_use_blocks.append(ToolUseBlock(
                    id=block.id,
                    name=block.name,
                    input=block.input,
                ))

        return AIResponse(
            content=text_content,
            model=model_name,
            provider=self.name,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=response.stop_reason,
            tool_use=tool_use_blocks,
        )

    def _convert_messages_with_tools(
        self, messages: list[AIMessage]
    ) -> tuple[Optional[str], list[dict]]:
        """Convert messages including tool results to Anthropic format.

        This method handles the full message format including:
        - System prompts (extracted separately)
        - User messages (text content)
        - Assistant messages (text or tool_use blocks)
        - Tool results (sent as user messages with tool_result content)

        Args:
            messages: List of AIMessage objects

        Returns:
            Tuple of (system_prompt, converted_messages)
        """
        system_prompt = None
        converted = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                # System prompt is separate in Anthropic API
                if isinstance(msg.content, str):
                    system_prompt = msg.content

            elif msg.role == MessageRole.USER:
                # Regular user message
                if isinstance(msg.content, str):
                    converted.append({"role": "user", "content": msg.content})

            elif msg.role == MessageRole.ASSISTANT:
                # Assistant message - may be text or tool_use blocks
                if isinstance(msg.content, str):
                    converted.append({"role": "assistant", "content": msg.content})
                else:
                    # Tool use blocks from AI
                    content = []
                    for block in msg.content:
                        if isinstance(block, ToolUseBlock):
                            content.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input,
                            })
                    if content:
                        converted.append({"role": "assistant", "content": content})

            elif msg.role == MessageRole.TOOL_RESULT:
                # Tool results go as user messages with tool_result content
                if isinstance(msg.content, list):
                    content = []
                    for block in msg.content:
                        if isinstance(block, ToolResultBlock):
                            content.append({
                                "type": "tool_result",
                                "tool_use_id": block.tool_use_id,
                                "content": block.content,
                                "is_error": block.is_error,
                            })
                    if content:
                        converted.append({"role": "user", "content": content})

        return system_prompt, converted

    def supports_vision(self) -> bool:
        """Claude supports vision/image input."""
        return True

    async def chat_with_images(
        self,
        messages: list[AIMessage],
        images: list[bytes],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AIResponse:
        """Send a chat request with images to Claude.

        Args:
            messages: Conversation history (can be empty for single-turn)
            images: List of image data (PNG or JPEG bytes)
            system_prompt: Optional system prompt for instructions
            model: Model to use (defaults to claude-3-5-haiku which supports vision)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            Response from Claude after processing the images
        """
        import base64

        client = self._get_client()
        model_name = model or self.default_model

        # Build content array with images
        content = []

        # Add images as base64-encoded data
        for img_data in images:
            # Detect image type from magic bytes
            media_type = "image/png"
            if img_data[:2] == b"\xff\xd8":
                media_type = "image/jpeg"
            elif img_data[:4] == b"\x89PNG":
                media_type = "image/png"

            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64.b64encode(img_data).decode("utf-8"),
                },
            })

        # Add text prompt
        content.append({
            "type": "text",
            "text": "Please analyze these character sheet images and extract all character information.",
        })

        # Build messages list
        converted_messages = []

        # Add prior messages if any (extract system prompt from them)
        if messages:
            extracted_system, prior_msgs = self._convert_messages(messages)
            converted_messages.extend(prior_msgs)
            if system_prompt is None and extracted_system:
                system_prompt = extracted_system

        # Add the image message
        converted_messages.append({"role": "user", "content": content})

        kwargs = {
            "model": model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": converted_messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await client.messages.create(**kwargs)

        # Extract text content
        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content += block.text

        return AIResponse(
            content=text_content,
            model=model_name,
            provider=self.name,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=response.stop_reason,
        )
