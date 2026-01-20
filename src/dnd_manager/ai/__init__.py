"""AI integration for D&D character assistance."""

from dnd_manager.ai.base import AIProvider, AIResponse, AIMessage, MessageRole
from dnd_manager.ai.context import CharacterContext, build_system_prompt
from dnd_manager.ai.providers import get_provider, list_providers
from dnd_manager.ai.semantic import (
    SemanticLayer,
    QueryResult,
    get_semantic_layer,
    query_game_data,
)

__all__ = [
    "AIProvider",
    "AIResponse",
    "AIMessage",
    "MessageRole",
    "CharacterContext",
    "build_system_prompt",
    "get_provider",
    "list_providers",
    # Semantic layer
    "SemanticLayer",
    "QueryResult",
    "get_semantic_layer",
    "query_game_data",
]
