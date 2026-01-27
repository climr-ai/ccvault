"""Google Gemini AI provider using the new google-genai SDK."""

import os
from typing import Any, AsyncIterator, Optional

from dnd_manager.ai.base import (
    AIMessage,
    AIProvider,
    AIResponse,
    MessageRole,
    ToolChoice,
    ToolUseBlock,
    ToolResultBlock,
)


class GeminiProvider(AIProvider):
    """Google Gemini AI provider.

    Uses the google-genai SDK (the new unified SDK).
    Free tier: ~50 requests/day for gemini-2.5-flash
    """

    MODELS = [
        "gemini-2.5-flash",       # Best free tier option, 1M context
        "gemini-2.5-flash-lite",  # Cheapest, high throughput
        "gemini-2.5-pro",         # Most capable 2.5
        "gemini-3-flash-preview", # Newest flash
        "gemini-3-pro-preview",   # Newest pro (paid only)
    ]

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini provider.

        Args:
            api_key: API key (uses config/env if not provided)
        """
        # Get API key from config or environment
        if api_key is None:
            from dnd_manager.config import get_config_manager
            manager = get_config_manager()
            api_key = manager.get_api_key("gemini")

        # Fall back to environment variables if not in config
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

        self._api_key = api_key
        self._client = None

    def _get_client(self):
        """Lazy-load the Gemini client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
            except ImportError:
                raise ImportError("google-genai package not installed. Run: pip install google-genai")
        return self._client

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return "gemini-2.5-flash"

    @property
    def available_models(self) -> list[str]:
        return self.MODELS.copy()

    def is_configured(self) -> bool:
        return self._api_key is not None

    def _build_contents(self, messages: list[AIMessage]) -> tuple[Optional[str], list[dict]]:
        """Convert messages to Gemini format.

        Returns:
            Tuple of (system_instruction, contents)
        """
        system_instruction = None
        contents = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            elif msg.role == MessageRole.USER:
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == MessageRole.ASSISTANT:
                if isinstance(msg.content, str):
                    contents.append({"role": "model", "parts": [{"text": msg.content}]})
                else:
                    # Tool use blocks from AI - convert to function_call parts
                    parts = []
                    for block in msg.content:
                        if isinstance(block, ToolUseBlock):
                            parts.append({
                                "function_call": {
                                    "name": block.name,
                                    "args": block.input,
                                }
                            })
                    if parts:
                        contents.append({"role": "model", "parts": parts})
            elif msg.role == MessageRole.TOOL_RESULT:
                # Tool results go as function_response parts
                if isinstance(msg.content, list):
                    parts = []
                    for block in msg.content:
                        if isinstance(block, ToolResultBlock):
                            tool_name = self._get_tool_name_for_id(messages, block.tool_use_id)
                            parts.append({
                                "function_response": {
                                    "name": tool_name,
                                    "response": {"result": block.content},
                                }
                            })
                    if parts:
                        contents.append({"role": "user", "parts": parts})

        return system_instruction, contents

    def _get_tool_name_for_id(self, messages: list[AIMessage], tool_use_id: str) -> str:
        """Find the tool name associated with a tool_use_id."""
        for msg in messages:
            if msg.role == MessageRole.ASSISTANT and not isinstance(msg.content, str):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock) and block.id == tool_use_id:
                        return block.name
        return "unknown"

    async def chat(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        """Send a chat request to Gemini."""
        from google.genai import types

        client = self._get_client()
        model_name = model or self.default_model

        system_instruction, contents = self._build_contents(messages)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        response = await client.aio.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )

        # Extract usage info if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", None)
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", None)

        return AIResponse(
            content=response.text or "",
            model=model_name,
            provider=self.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            finish_reason=response.candidates[0].finish_reason.name if response.candidates else None,
        )

    async def chat_stream(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a chat response from Gemini."""
        from google.genai import types

        client = self._get_client()
        model_name = model or self.default_model

        system_instruction, contents = self._build_contents(messages)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        async for chunk in client.aio.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                yield chunk.text

    def _convert_tools_to_gemini(self, tools: list[dict]) -> list[dict]:
        """Convert Anthropic-format tool definitions to Gemini format.

        Anthropic format:
        {
            "name": "tool_name",
            "description": "...",
            "input_schema": {"type": "object", "properties": {...}, "required": [...]}
        }

        Gemini format uses FunctionDeclaration objects.
        """
        gemini_tools = []

        for tool in tools:
            func_decl = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
            }
            gemini_tools.append(func_decl)

        return gemini_tools

    async def chat_with_tools(
        self,
        messages: list[AIMessage],
        tools: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        tool_choice: ToolChoice = ToolChoice.AUTO,
    ) -> AIResponse:
        """Send a chat request with tools to Gemini.

        Args:
            messages: Conversation history (may include tool results)
            tools: List of tool definitions in Anthropic format (will be converted)
            model: Model to use (defaults to default_model)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            tool_choice: Controls tool usage (AUTO, ANY, NONE)

        Returns:
            AIResponse which may include tool_use requests
        """
        from google.genai import types

        client = self._get_client()
        model_name = model or self.default_model

        system_instruction, contents = self._build_contents(messages)

        # Convert tools to Gemini format
        gemini_func_decls = self._convert_tools_to_gemini(tools)

        # Build config with tools
        if tool_choice == ToolChoice.NONE or not tools:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
        else:
            # Set tool config based on tool_choice
            if tool_choice == ToolChoice.ANY:
                tool_config = types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(mode="ANY")
                )
            else:  # AUTO
                tool_config = types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(mode="AUTO")
                )

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=max_tokens,
                temperature=temperature,
                tools=[types.Tool(function_declarations=gemini_func_decls)],
                tool_config=tool_config,
            )

        response = await client.aio.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )

        # Parse response for function calls and text
        tool_use_blocks = []
        text_content = ""

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    text_content += part.text
                elif hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    # Generate a unique ID for the tool use (full UUID for collision safety)
                    import uuid
                    tool_use_blocks.append(ToolUseBlock(
                        id=f"toolu_{uuid.uuid4().hex}",
                        name=fc.name,
                        input=dict(fc.args) if fc.args else {},
                    ))

        # Extract usage info if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", None)
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", None)

        # Determine finish reason
        finish_reason = None
        if response.candidates:
            finish_reason = response.candidates[0].finish_reason.name

        return AIResponse(
            content=text_content,
            model=model_name,
            provider=self.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            finish_reason=finish_reason,
            tool_use=tool_use_blocks,
        )

    def supports_vision(self) -> bool:
        """Gemini supports vision/image input."""
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
        """Send a chat request with images to Gemini.

        Args:
            messages: Conversation history (can be empty for single-turn)
            images: List of image data (PNG or JPEG bytes)
            system_prompt: Optional system prompt for instructions
            model: Model to use (defaults to gemini-2.5-flash which supports vision)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            Response from Gemini after processing the images
        """
        import base64
        from google.genai import types

        client = self._get_client()
        model_name = model or self.default_model

        # Build contents with images
        parts = []

        # Add images as inline_data parts
        for img_data in images:
            # Detect image type from magic bytes
            mime_type = "image/png"
            if img_data[:2] == b"\xff\xd8":
                mime_type = "image/jpeg"
            elif img_data[:4] == b"\x89PNG":
                mime_type = "image/png"

            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.b64encode(img_data).decode("utf-8"),
                }
            })

        # Add text prompt requesting analysis
        parts.append({
            "text": "Please analyze these character sheet images and extract all character information."
        })

        # Build the contents list
        contents = [{"role": "user", "parts": parts}]

        # Add any prior messages
        if messages:
            system_instruction, prior_contents = self._build_contents(messages)
            # Prepend prior contents (but system_prompt param takes precedence)
            contents = prior_contents + contents
            if system_prompt is None and system_instruction:
                system_prompt = system_instruction

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        response = await client.aio.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )

        # Extract usage info if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", None)
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", None)

        return AIResponse(
            content=response.text or "",
            model=model_name,
            provider=self.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            finish_reason=response.candidates[0].finish_reason.name if response.candidates else None,
        )
