"""Ollama local AI provider."""

import logging
import os
from typing import AsyncIterator, Optional

from dnd_manager.ai.base import AIMessage, AIProvider, AIResponse, MessageRole

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    """Ollama local AI provider.

    Runs models locally via Ollama server.
    Default host: http://localhost:11434
    """

    # Popular models for D&D assistance
    SUGGESTED_MODELS = [
        "llama3.2",        # Good general purpose
        "mistral",         # Fast and capable
        "gemma2",          # Google's open model
        "qwen2.5",         # Good for roleplay
        "deepseek-r1",     # Reasoning focused
    ]

    def __init__(self, host: Optional[str] = None):
        """Initialize the Ollama provider.

        Args:
            host: Ollama server URL (uses config/env if not provided)
        """
        # Get host from config or environment
        if host is None:
            from dnd_manager.config import get_config_manager
            manager = get_config_manager()
            host = manager.get("ai.ollama.base_url")
            if not host:
                host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

        self._host = host
        self._client = None
        self._available_models: Optional[list[str]] = None

    def _get_client(self):
        """Lazy-load the Ollama client."""
        if self._client is None:
            try:
                from ollama import AsyncClient
                self._client = AsyncClient(host=self._host)
            except ImportError:
                raise ImportError("ollama package not installed. Run: pip install ollama")
        return self._client

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        return "llama3.2"

    @property
    def available_models(self) -> list[str]:
        """Return cached or suggested models."""
        if self._available_models is not None:
            return self._available_models
        return self.SUGGESTED_MODELS.copy()

    async def refresh_models(self) -> list[str]:
        """Fetch actually installed models from Ollama server."""
        try:
            client = self._get_client()
            response = await client.list()
            self._available_models = [m["name"] for m in response.get("models", [])]
            return self._available_models
        except (OSError, TimeoutError, ConnectionError) as e:
            logger.debug("Failed to fetch Ollama models: %s, using suggestions", e)
            return self.SUGGESTED_MODELS.copy()

    def is_configured(self) -> bool:
        """Check if Ollama server is accessible."""
        # For Ollama, we just check if the host is set
        # Actual connectivity is checked at runtime
        return True

    def _convert_messages(self, messages: list[AIMessage]) -> list[dict]:
        """Convert messages to Ollama format."""
        converted = []
        for msg in messages:
            converted.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        return converted

    async def chat(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        """Send a chat request to Ollama."""
        client = self._get_client()
        model_name = model or self.default_model

        response = await client.chat(
            model=model_name,
            messages=self._convert_messages(messages),
            options={
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        )

        return AIResponse(
            content=response["message"]["content"],
            model=model_name,
            provider=self.name,
            input_tokens=response.get("prompt_eval_count"),
            output_tokens=response.get("eval_count"),
            finish_reason="stop",
        )

    async def chat_stream(
        self,
        messages: list[AIMessage],
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a chat response from Ollama."""
        client = self._get_client()
        model_name = model or self.default_model

        stream = await client.chat(
            model=model_name,
            messages=self._convert_messages(messages),
            options={
                "num_predict": max_tokens,
                "temperature": temperature,
            },
            stream=True,
        )

        async for chunk in stream:
            if chunk.get("message", {}).get("content"):
                yield chunk["message"]["content"]
