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
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import AsyncIterator, Optional

from dnd_manager.ai.base import AIMessage, AIProvider, AIResponse, MessageRole


class QueryComplexity(str, Enum):
    """Query complexity levels."""
    SIMPLE = "simple"      # Basic questions, lookups
    MODERATE = "moderate"  # Rules clarifications, character advice
    COMPLEX = "complex"    # Multi-step reasoning, strategy, creativity


@dataclass
class QuotaTracker:
    """Track rate limit state for a model."""
    model: str
    requests_today: int = 0
    last_request: Optional[datetime] = None
    rate_limited_until: Optional[datetime] = None
    daily_limit: int = 50  # Conservative estimate

    def is_available(self) -> bool:
        """Check if model is available for use."""
        now = datetime.now()

        # Check if rate limited
        if self.rate_limited_until and now < self.rate_limited_until:
            return False

        # Check daily quota (reset at midnight)
        if self.last_request and self.last_request.date() < now.date():
            self.requests_today = 0

        return self.requests_today < self.daily_limit

    def record_request(self):
        """Record a successful request."""
        self.requests_today += 1
        self.last_request = datetime.now()

    def record_rate_limit(self, retry_after_seconds: int = 60):
        """Record a rate limit error."""
        self.rate_limited_until = datetime.now() + timedelta(seconds=retry_after_seconds)


@dataclass
class RouterState:
    """State for the intelligent router."""
    quotas: dict[str, QuotaTracker] = field(default_factory=dict)

    def get_quota(self, model: str) -> QuotaTracker:
        """Get or create quota tracker for a model."""
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
                import google.generativeai as genai
                genai.configure(api_key=self._api_key)
                self._client = genai
            except ImportError:
                raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
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
            genai = self._get_client()
            model = genai.GenerativeModel(self.CLASSIFIER_MODEL)
            prompt = CLASSIFICATION_PROMPT.format(query=query)

            response = await model.generate_content_async(prompt)
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
            quota = self._state.get_quota(model)
            if quota.is_available():
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
        genai = self._get_client()
        quota = self._state.get_quota(model)

        # Extract system prompt and history
        system_instruction = None
        history = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            elif msg.role == MessageRole.USER:
                history.append({"role": "user", "parts": [msg.content]})
            elif msg.role == MessageRole.ASSISTANT:
                history.append({"role": "model", "parts": [msg.content]})

        try:
            gen_model = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_instruction,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )

            chat_history = history[:-1] if history else []
            chat = gen_model.start_chat(history=chat_history)
            last_message = history[-1]["parts"][0] if history else ""

            response = await chat.send_message_async(last_message)
            quota.record_request()

            return AIResponse(
                content=response.text,
                model=model,
                provider=self.name,
                finish_reason="stop",
            )

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "quota" in error_str:
                quota.record_rate_limit()
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
            quota = self._state.get_quota(model)
            if not quota.is_available():
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

    async def chat_stream(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream chat response with intelligent routing."""
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

        genai = self._get_client()
        quota = self._state.get_quota(selected_model)

        # Extract messages
        system_instruction = None
        history = []
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            elif msg.role == MessageRole.USER:
                history.append({"role": "user", "parts": [msg.content]})
            elif msg.role == MessageRole.ASSISTANT:
                history.append({"role": "model", "parts": [msg.content]})

        gen_model = genai.GenerativeModel(
            model_name=selected_model,
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )

        chat_history = history[:-1] if history else []
        chat = gen_model.start_chat(history=chat_history)
        last_message = history[-1]["parts"][0] if history else ""

        try:
            response = await chat.send_message_async(last_message, stream=True)
            quota.record_request()

            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                quota.record_rate_limit()
            raise

    def get_quota_status(self) -> dict[str, dict]:
        """Get current quota status for all models."""
        status = {}
        for model in self.available_models:
            quota = self._state.get_quota(model)
            status[model] = {
                "requests_today": quota.requests_today,
                "daily_limit": quota.daily_limit,
                "available": quota.is_available(),
                "rate_limited_until": quota.rate_limited_until.isoformat() if quota.rate_limited_until else None,
            }
        return status


class RateLimitError(Exception):
    """Rate limit error with model info."""
    def __init__(self, model: str, message: str):
        self.model = model
        super().__init__(f"Rate limit on {model}: {message}")
