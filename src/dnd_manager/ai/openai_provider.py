"""OpenAI GPT AI provider."""

import os
from typing import AsyncIterator, Optional

from dnd_manager.ai.base import AIMessage, AIProvider, AIResponse, MessageRole


class OpenAIProvider(AIProvider):
    """OpenAI GPT AI provider."""

    MODELS = [
        "gpt-4o",            # Most capable
        "gpt-4o-mini",       # Fast and cheap
        "gpt-4-turbo",       # Previous flagship
        "o1",                # Reasoning model
        "o1-mini",           # Fast reasoning
    ]

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI provider.

        Args:
            api_key: API key (uses config/env if not provided)
        """
        # Get API key from config or environment
        if api_key is None:
            from dnd_manager.config import get_config_manager
            manager = get_config_manager()
            api_key = manager.get_api_key("openai")

        self._api_key = api_key
        self._client = None

    def _get_client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self._api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        return self._client

    @property
    def name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return "gpt-4o-mini"  # Fast and affordable

    @property
    def available_models(self) -> list[str]:
        return self.MODELS.copy()

    def is_configured(self) -> bool:
        return self._api_key is not None

    def _convert_messages(self, messages: list[AIMessage]) -> list[dict]:
        """Convert messages to OpenAI format."""
        return [msg.to_dict() for msg in messages]

    async def chat(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        """Send a chat request to OpenAI."""
        client = self._get_client()
        model_name = model or self.default_model

        response = await client.chat.completions.create(
            model=model_name,
            messages=self._convert_messages(messages),
            max_tokens=max_tokens,
            temperature=temperature,
        )

        choice = response.choices[0]
        usage = response.usage

        return AIResponse(
            content=choice.message.content or "",
            model=model_name,
            provider=self.name,
            input_tokens=usage.prompt_tokens if usage else None,
            output_tokens=usage.completion_tokens if usage else None,
            finish_reason=choice.finish_reason,
        )

    async def chat_stream(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a chat response from OpenAI."""
        client = self._get_client()
        model_name = model or self.default_model

        stream = await client.chat.completions.create(
            model=model_name,
            messages=self._convert_messages(messages),
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
