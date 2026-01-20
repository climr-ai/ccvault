"""Google Gemini AI provider."""

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

    Uses the google-generativeai SDK with async support.
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
                import google.generativeai as genai
                genai.configure(api_key=self._api_key)
                self._client = genai
            except ImportError:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
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

    def _convert_messages(self, messages: list[AIMessage]) -> tuple[Optional[str], list[dict]]:
        """Convert messages to Gemini format.

        Gemini uses a different format:
        - System prompt is set separately
        - History is a list of {"role": "user"|"model", "parts": [text]}

        Returns:
            Tuple of (system_instruction, history)
        """
        system_instruction = None
        history = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            elif msg.role == MessageRole.USER:
                history.append({"role": "user", "parts": [msg.content]})
            elif msg.role == MessageRole.ASSISTANT:
                history.append({"role": "model", "parts": [msg.content]})

        return system_instruction, history

    async def chat(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        """Send a chat request to Gemini."""
        genai = self._get_client()
        model_name = model or self.default_model

        system_instruction, history = self._convert_messages(messages)

        # Create the model with system instruction
        gen_model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )

        # Start chat with history (excluding the last user message)
        chat_history = history[:-1] if history else []
        chat = gen_model.start_chat(history=chat_history)

        # Get the last user message
        last_message = history[-1]["parts"][0] if history else ""

        # Generate response
        response = await chat.send_message_async(last_message)

        # Extract usage info if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, "usage_metadata"):
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", None)
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", None)

        return AIResponse(
            content=response.text,
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
        genai = self._get_client()
        model_name = model or self.default_model

        system_instruction, history = self._convert_messages(messages)

        gen_model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )

        chat_history = history[:-1] if history else []
        chat = gen_model.start_chat(history=chat_history)
        last_message = history[-1]["parts"][0] if history else ""

        response = await chat.send_message_async(last_message, stream=True)

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    def _convert_json_schema_type(self, type_str: str) -> "protos.Type":
        """Convert JSON Schema type string to Gemini protos.Type enum."""
        genai = self._get_client()
        type_map = {
            "string": genai.protos.Type.STRING,
            "number": genai.protos.Type.NUMBER,
            "integer": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT,
        }
        return type_map.get(type_str, genai.protos.Type.STRING)

    def _convert_schema_to_gemini(self, schema: dict) -> dict:
        """Convert JSON Schema to Gemini Schema format.

        Gemini uses protos.Type enum values instead of string type names.
        """
        if not schema:
            return {}

        genai = self._get_client()
        result = {}

        # Convert type
        if "type" in schema:
            result["type"] = self._convert_json_schema_type(schema["type"])

        # Convert description
        if "description" in schema:
            result["description"] = schema["description"]

        # Convert enum
        if "enum" in schema:
            result["enum"] = schema["enum"]

        # Convert properties (for objects)
        if "properties" in schema:
            result["properties"] = {
                name: self._convert_schema_to_gemini(prop_schema)
                for name, prop_schema in schema["properties"].items()
            }

        # Convert required
        if "required" in schema:
            result["required"] = schema["required"]

        # Convert items (for arrays)
        if "items" in schema:
            result["items"] = self._convert_schema_to_gemini(schema["items"])

        return result

    def _convert_tools_to_gemini(self, tools: list[dict]) -> list:
        """Convert Anthropic-format tool definitions to Gemini format.

        Anthropic format:
        {
            "name": "tool_name",
            "description": "...",
            "input_schema": {"type": "object", "properties": {...}, "required": [...]}
        }

        Gemini requires protos.Type enum values for schema types.
        """
        genai = self._get_client()
        gemini_tools = []

        for tool in tools:
            input_schema = tool.get("input_schema", {"type": "object", "properties": {}})
            converted_schema = self._convert_schema_to_gemini(input_schema)

            func_decl = genai.protos.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=genai.protos.Schema(**converted_schema) if converted_schema else None,
            )
            gemini_tools.append(func_decl)

        return gemini_tools

    def _convert_messages_with_tools(
        self, messages: list[AIMessage]
    ) -> tuple[Optional[str], list[dict]]:
        """Convert messages including tool results to Gemini format.

        Handles:
        - System prompts (extracted separately)
        - User messages
        - Assistant messages (text or function calls)
        - Tool results (as function_response parts)
        """
        system_instruction = None
        history = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                if isinstance(msg.content, str):
                    system_instruction = msg.content

            elif msg.role == MessageRole.USER:
                if isinstance(msg.content, str):
                    history.append({"role": "user", "parts": [msg.content]})

            elif msg.role == MessageRole.ASSISTANT:
                if isinstance(msg.content, str):
                    history.append({"role": "model", "parts": [msg.content]})
                else:
                    # Tool use blocks from AI - convert to function_call parts
                    parts = []
                    for block in msg.content:
                        if isinstance(block, ToolUseBlock):
                            # Gemini uses function_call format
                            parts.append({
                                "function_call": {
                                    "name": block.name,
                                    "args": block.input,
                                }
                            })
                    if parts:
                        history.append({"role": "model", "parts": parts})

            elif msg.role == MessageRole.TOOL_RESULT:
                # Tool results go as function_response parts
                if isinstance(msg.content, list):
                    parts = []
                    for block in msg.content:
                        if isinstance(block, ToolResultBlock):
                            parts.append({
                                "function_response": {
                                    "name": self._get_tool_name_for_id(messages, block.tool_use_id),
                                    "response": {"result": block.content},
                                }
                            })
                    if parts:
                        history.append({"role": "user", "parts": parts})

        return system_instruction, history

    def _get_tool_name_for_id(self, messages: list[AIMessage], tool_use_id: str) -> str:
        """Find the tool name associated with a tool_use_id."""
        for msg in messages:
            if msg.role == MessageRole.ASSISTANT and not isinstance(msg.content, str):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock) and block.id == tool_use_id:
                        return block.name
        return "unknown"

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

        This enables function calling. The AI can request tool execution,
        and the caller is responsible for executing tools and feeding
        results back in subsequent messages.

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
        genai = self._get_client()
        model_name = model or self.default_model

        system_instruction, history = self._convert_messages_with_tools(messages)

        # Handle NONE case - no tools
        if tool_choice == ToolChoice.NONE:
            gen_model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
        else:
            gemini_func_decls = self._convert_tools_to_gemini(tools)
            gemini_tools = [genai.protos.Tool(function_declarations=gemini_func_decls)]

            # Set tool_config based on tool_choice
            # Gemini modes: AUTO, ANY, NONE
            if tool_choice == ToolChoice.ANY:
                tool_config = genai.protos.ToolConfig(
                    function_calling_config=genai.protos.FunctionCallingConfig(
                        mode=genai.protos.FunctionCallingConfig.Mode.ANY
                    )
                )
            else:  # AUTO
                tool_config = genai.protos.ToolConfig(
                    function_calling_config=genai.protos.FunctionCallingConfig(
                        mode=genai.protos.FunctionCallingConfig.Mode.AUTO
                    )
                )

            gen_model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
                tools=gemini_tools,
                tool_config=tool_config,
            )

        # Start chat with history (excluding the last message)
        chat_history = history[:-1] if history else []
        chat = gen_model.start_chat(history=chat_history)

        # Get the last message content
        last_message = history[-1]["parts"] if history else [""]

        # Generate response
        response = await chat.send_message_async(last_message)

        # Parse response for function calls and text
        tool_use_blocks = []
        text_content = ""

        for part in response.parts:
            if hasattr(part, "text") and part.text:
                text_content += part.text
            elif hasattr(part, "function_call"):
                fc = part.function_call
                # Generate a unique ID for the tool use
                import uuid
                tool_use_blocks.append(ToolUseBlock(
                    id=f"toolu_{uuid.uuid4().hex[:24]}",
                    name=fc.name,
                    input=dict(fc.args) if fc.args else {},
                ))

        # Extract usage info if available
        input_tokens = None
        output_tokens = None
        if hasattr(response, "usage_metadata"):
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
