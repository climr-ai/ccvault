"""Intelligent AI router for Gemini models.

Uses Gemini 2.5 Flash-Lite to classify query complexity and routes to the
most appropriate model while respecting rate limits and falling back gracefully.

Routing strategy:
1. Flash-Lite classifies the query complexity (simple/moderate/complex)
2. Complex -> Gemini 3 Flash Preview (best reasoning)
3. Moderate -> Gemini 2.5 Flash (good balance)
4. Simple -> Gemini 2.5 Flash-Lite (fast, high quota)
5. On rate limit errors, fall back to next tier
"""

import asyncio
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import AsyncIterator, Optional

from dnd_manager.ai.base import (
    AIMessage,
    AIProvider,
    AIRateLimitError,
    AIResponse,
    MessageRole,
    ToolChoice,
    ToolUseBlock,
    ToolResultBlock,
)


class QueryComplexity(str, Enum):
    """Query complexity levels."""
    SIMPLE = "simple"      # Basic questions, lookups
    MODERATE = "moderate"  # Rules clarifications, character advice
    COMPLEX = "complex"    # Multi-step reasoning, strategy, creativity


@dataclass
class QuotaTracker:
    """Track rate limit state for a model.

    Note: This class is NOT thread-safe. All access should be through
    RouterState methods which provide proper synchronization.
    """
    model: str
    requests_today: int = 0
    last_request: Optional[datetime] = None
    rate_limited_until: Optional[datetime] = None
    daily_limit: int = 50  # Conservative estimate

    def _reset_if_new_day(self) -> None:
        """Reset daily counter if it's a new day. Must be called under lock."""
        now = datetime.now()
        if self.last_request and self.last_request.date() < now.date():
            self.requests_today = 0

    def is_available(self) -> bool:
        """Check if model is available for use. Must be called under lock."""
        now = datetime.now()

        # Check if rate limited
        if self.rate_limited_until and now < self.rate_limited_until:
            return False

        # Reset daily quota if new day
        self._reset_if_new_day()

        return self.requests_today < self.daily_limit

    def record_request(self) -> None:
        """Record a successful request. Must be called under lock."""
        # Reset if new day before incrementing
        self._reset_if_new_day()
        self.requests_today += 1
        self.last_request = datetime.now()

    def record_rate_limit(self, retry_after_seconds: int = 60) -> None:
        """Record a rate limit error. Must be called under lock."""
        self.rate_limited_until = datetime.now() + timedelta(seconds=retry_after_seconds)


@dataclass
class RouterState:
    """Thread-safe state for the intelligent router."""
    quotas: dict[str, QuotaTracker] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def _get_or_create_quota(self, model: str) -> QuotaTracker:
        """Get or create quota tracker for a model. Must be called with lock held."""
        if model not in self.quotas:
            # Set daily limits based on known free tier limits
            daily_limits = {
                "gemini-3-flash-preview": 25,      # Limited preview
                "gemini-2.5-flash": 50,            # Standard free tier
                "gemini-2.5-flash-lite": 1000,     # High throughput
                "gemini-2.5-pro": 25,              # Limited
            }
            self.quotas[model] = QuotaTracker(
                model=model,
                daily_limit=daily_limits.get(model, 50)
            )
        return self.quotas[model]

    def get_quota(self, model: str) -> QuotaTracker:
        """Get or create quota tracker for a model (thread-safe)."""
        with self._lock:
            return self._get_or_create_quota(model)

    def is_model_available(self, model: str) -> bool:
        """Check if a model is available for use (thread-safe)."""
        with self._lock:
            quota = self._get_or_create_quota(model)
            return quota.is_available()

    def record_request(self, model: str) -> None:
        """Record a successful request (thread-safe)."""
        with self._lock:
            quota = self._get_or_create_quota(model)
            quota.record_request()

    def record_rate_limit(self, model: str, retry_after_seconds: int = 60) -> None:
        """Record a rate limit error (thread-safe)."""
        with self._lock:
            quota = self._get_or_create_quota(model)
            quota.record_rate_limit(retry_after_seconds)


# Classification prompt for Flash-Lite
CLASSIFICATION_PROMPT = """Classify this D&D-related query by complexity. Respond with ONLY one word: simple, moderate, or complex.

Guidelines:
- SIMPLE: Basic lookups, yes/no questions, simple calculations, spell slot tracking
  Examples: "How much damage does fireball do?", "What's my AC?", "Roll initiative"

- MODERATE: Rules clarifications, character building advice, tactical suggestions
  Examples: "Should I multiclass?", "How does counterspell work?", "Best spell for this situation"

- COMPLEX: Multi-step strategy, creative roleplay, encounter design, complex rule interactions
  Examples: "Plan my level 1-20 wizard build", "Design an encounter for my party", "How would my character react to betrayal?"

Query: {query}

Classification:"""


class GeminiRouter(AIProvider):
    """Intelligent router for Gemini models with automatic fallback.

    Uses Flash-Lite to classify queries and routes to appropriate model:
    - Complex queries -> Gemini 3 Flash (best reasoning)
    - Moderate queries -> Gemini 2.5 Flash (balanced)
    - Simple queries -> Gemini 2.5 Flash-Lite (fast)

    Falls back gracefully when rate limits are hit.
    """

    # Model tiers in order of capability
    MODEL_TIERS = {
        QueryComplexity.COMPLEX: [
            "gemini-3-flash-preview",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
        ],
        QueryComplexity.MODERATE: [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
        ],
        QueryComplexity.SIMPLE: [
            "gemini-2.5-flash-lite",
        ],
    }

    CLASSIFIER_MODEL = "gemini-2.5-flash-lite"

    def __init__(self, api_key: Optional[str] = None, auto_classify: Optional[bool] = None):
        """Initialize the router.

        Args:
            api_key: Gemini API key (uses config/env if not provided)
            auto_classify: Whether to auto-classify queries (uses config if not provided)
        """
        # Get API key from config or environment
        if api_key is None:
            from dnd_manager.config import get_config_manager
            manager = get_config_manager()
            api_key = manager.get_api_key("gemini")

        self._api_key = api_key
        self._client = None
        self._state = RouterState()

        # Get auto_classify from config if not specified
        if auto_classify is None:
            from dnd_manager.config import get_config_manager
            manager = get_config_manager()
            auto_classify = manager.get("ai.gemini.auto_classify")
            if auto_classify is None:
                auto_classify = True

        self._auto_classify = auto_classify

    def _get_client(self):
        """Lazy-load the Gemini client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
            except ImportError:
                raise ImportError("google-genai not installed. Run: pip install google-genai")
        return self._client

    @property
    def name(self) -> str:
        return "gemini-router"

    @property
    def default_model(self) -> str:
        return "gemini-2.5-flash"

    @property
    def available_models(self) -> list[str]:
        return [
            "gemini-3-flash-preview",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
        ]

    def is_configured(self) -> bool:
        return self._api_key is not None

    async def classify_query(self, query: str) -> QueryComplexity:
        """Classify query complexity using Flash-Lite.

        This is cheap (high quota) so we can afford to call it for every query.
        """
        try:
            client = self._get_client()
            prompt = CLASSIFICATION_PROMPT.format(query=query)

            response = await client.aio.models.generate_content(
                model=self.CLASSIFIER_MODEL,
                contents=prompt,
            )
            result = response.text.strip().lower()

            # Parse response
            if "complex" in result:
                return QueryComplexity.COMPLEX
            elif "moderate" in result:
                return QueryComplexity.MODERATE
            else:
                return QueryComplexity.SIMPLE

        except Exception:
            # On any error, default to moderate
            return QueryComplexity.MODERATE

    def _select_model(self, complexity: QueryComplexity) -> str:
        """Select best available model for the complexity level."""
        candidates = self.MODEL_TIERS[complexity]

        for model in candidates:
            if self._state.is_model_available(model):
                return model

        # All exhausted, return last resort
        return self.CLASSIFIER_MODEL

    async def _call_model(
        self,
        model: str,
        messages: list[AIMessage],
        max_tokens: int,
        temperature: float,
    ) -> AIResponse:
        """Call a specific model with rate limit handling."""
        from google.genai import types

        client = self._get_client()
        quota = self._state.get_quota(model)

        # Extract system prompt and contents
        system_instruction = None
        contents = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            elif msg.role == MessageRole.USER:
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == MessageRole.ASSISTANT:
                contents.append({"role": "model", "parts": [{"text": msg.content}]})

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=max_tokens,
                temperature=temperature,
            )

            response = await client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            self._state.record_request(model)

            return AIResponse(
                content=response.text or "",
                model=model,
                provider=self.name,
                finish_reason="stop",
            )

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "quota" in error_str:
                self._state.record_rate_limit(model)
                raise RateLimitError(model, str(e))
            raise

    async def chat(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        """Route chat to appropriate model based on query complexity."""
        # If model explicitly specified, use it directly
        if model:
            return await self._call_model(model, messages, max_tokens, temperature)

        # Get the user's query for classification
        user_messages = [m for m in messages if m.role == MessageRole.USER]
        query = user_messages[-1].content if user_messages else ""

        # Classify complexity
        if self._auto_classify and query:
            complexity = await self.classify_query(query)
        else:
            complexity = QueryComplexity.MODERATE

        # Try models in order of preference for this complexity
        candidates = self.MODEL_TIERS[complexity].copy()
        last_error = None

        for model in candidates:
            if not self._state.is_model_available(model):
                continue

            try:
                response = await self._call_model(model, messages, max_tokens, temperature)
                return response
            except RateLimitError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue

        # All models failed, raise the last error
        if last_error:
            raise last_error
        raise RuntimeError("All models exhausted")

    async def chat_with_tools(
        self,
        messages: list[AIMessage],
        tools: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        tool_choice: ToolChoice = ToolChoice.AUTO,
    ) -> AIResponse:
        """Route chat with tools to appropriate model based on query complexity.

        Args:
            messages: Conversation history (may include tool results)
            tools: List of tool definitions in Anthropic format (will be converted)
            model: Model to use (overrides auto-routing if specified)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            tool_choice: Controls tool usage (AUTO, ANY, NONE)

        Returns:
            AIResponse which may include tool_use requests
        """
        # If model explicitly specified, use it directly
        if model:
            return await self._call_model_with_tools(
                model, messages, tools, max_tokens, temperature, tool_choice
            )

        # Get the user's query for classification
        user_messages = [m for m in messages if m.role == MessageRole.USER]
        query = user_messages[-1].content if user_messages else ""

        # Classify complexity
        if self._auto_classify and query:
            complexity = await self.classify_query(query)
        else:
            complexity = QueryComplexity.MODERATE

        # Try models in order of preference for this complexity
        candidates = self.MODEL_TIERS[complexity].copy()
        last_error = None

        for candidate_model in candidates:
            if not self._state.is_model_available(candidate_model):
                continue

            try:
                response = await self._call_model_with_tools(
                    candidate_model, messages, tools, max_tokens, temperature, tool_choice
                )
                return response
            except RateLimitError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue

        # All models failed, raise the last error
        if last_error:
            raise last_error
        raise RuntimeError("All models exhausted")

    async def _call_model_with_tools(
        self,
        model: str,
        messages: list[AIMessage],
        tools: list[dict],
        max_tokens: int,
        temperature: float,
        tool_choice: ToolChoice,
    ) -> AIResponse:
        """Call a specific model with tools and rate limit handling."""
        from google.genai import types
        import uuid

        client = self._get_client()
        quota = self._state.get_quota(model)

        # Extract system prompt and build contents
        system_instruction, contents = self._build_contents_with_tools(messages)

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

        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            self._state.record_request(model)

            # Parse response for function calls and text
            tool_use_blocks = []
            text_content = ""

            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        text_content += part.text
                    elif hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
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
                model=model,
                provider=self.name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                finish_reason=finish_reason,
                tool_use=tool_use_blocks,
            )

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "quota" in error_str:
                self._state.record_rate_limit(model)
                raise RateLimitError(model, str(e))
            raise

    def _build_contents_with_tools(
        self, messages: list[AIMessage]
    ) -> tuple[Optional[str], list[dict]]:
        """Convert messages to Gemini format, handling tool use and results.

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

    def _convert_tools_to_gemini(self, tools: list[dict]) -> list[dict]:
        """Convert Anthropic-format tool definitions to Gemini format."""
        gemini_tools = []

        for tool in tools:
            func_decl = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
            }
            gemini_tools.append(func_decl)

        return gemini_tools

    async def chat_stream(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream chat response with intelligent routing."""
        from google.genai import types

        # Get the user's query for classification
        user_messages = [m for m in messages if m.role == MessageRole.USER]
        query = user_messages[-1].content if user_messages else ""

        # Classify and select model
        if model:
            selected_model = model
        elif self._auto_classify and query:
            complexity = await self.classify_query(query)
            selected_model = self._select_model(complexity)
        else:
            selected_model = self._select_model(QueryComplexity.MODERATE)

        client = self._get_client()
        quota = self._state.get_quota(selected_model)

        # Extract messages
        system_instruction = None
        contents = []
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            elif msg.role == MessageRole.USER:
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == MessageRole.ASSISTANT:
                contents.append({"role": "model", "parts": [{"text": msg.content}]})

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        try:
            chunk_count = 0
            async for chunk in client.aio.models.generate_content_stream(
                model=selected_model,
                contents=contents,
                config=config,
            ):
                chunk_count += 1
                if chunk.text:
                    yield chunk.text
            # Record request only once after streaming completes
            if chunk_count > 0:
                self._state.record_request(selected_model)
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                self._state.record_rate_limit(selected_model)
            raise

    def get_quota_status(self) -> dict[str, dict]:
        """Get current quota status for all models (thread-safe snapshot)."""
        status = {}
        for model in self.available_models:
            # Get thread-safe snapshot of quota state
            with self._state._lock:
                quota = self._state._get_or_create_quota(model)
                status[model] = {
                    "requests_today": quota.requests_today,
                    "daily_limit": quota.daily_limit,
                    "available": quota.is_available(),
                    "rate_limited_until": quota.rate_limited_until.isoformat() if quota.rate_limited_until else None,
                }
        return status


# Backwards-compatible alias for RateLimitError
class RateLimitError(AIRateLimitError):
    """Rate limit error with model info.

    Deprecated: Use AIRateLimitError from dnd_manager.ai.base instead.
    """
    def __init__(self, model: str, message: str):
        self.model = model
        super().__init__(message, provider="gemini-router")
