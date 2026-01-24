"""AI provider registry and factory."""

import logging
from typing import Optional

from dnd_manager.ai.base import AIProvider, AIError, AIConfigurationError

logger = logging.getLogger(__name__)


# Registry of available providers
_PROVIDERS: dict[str, type[AIProvider]] = {}


def _register_providers():
    """Register all available providers."""
    global _PROVIDERS

    if _PROVIDERS:
        return  # Already registered

    # Import and register each provider
    try:
        from dnd_manager.ai.router import GeminiRouter
        _PROVIDERS["gemini"] = GeminiRouter  # Default: intelligent router
        _PROVIDERS["gemini-router"] = GeminiRouter
    except ImportError:
        pass

    try:
        from dnd_manager.ai.gemini import GeminiProvider
        _PROVIDERS["gemini-direct"] = GeminiProvider  # Direct access if needed
    except ImportError:
        pass

    try:
        from dnd_manager.ai.anthropic_provider import AnthropicProvider
        _PROVIDERS["anthropic"] = AnthropicProvider
    except ImportError:
        pass

    try:
        from dnd_manager.ai.openai_provider import OpenAIProvider
        _PROVIDERS["openai"] = OpenAIProvider
    except ImportError:
        pass

    try:
        from dnd_manager.ai.ollama_provider import OllamaProvider
        _PROVIDERS["ollama"] = OllamaProvider
    except ImportError:
        pass


def list_providers() -> list[str]:
    """List all available provider names."""
    _register_providers()
    return list(_PROVIDERS.keys())


def get_provider(name: str, **kwargs) -> Optional[AIProvider]:
    """Get a provider instance by name.

    Args:
        name: Provider name (gemini, anthropic, openai, ollama)
        **kwargs: Additional arguments passed to the provider constructor

    Returns:
        Provider instance or None if not found
    """
    _register_providers()
    provider_class = _PROVIDERS.get(name.lower())
    if provider_class:
        return provider_class(**kwargs)
    return None


def get_configured_providers() -> list[AIProvider]:
    """Get list of all configured (ready to use) providers."""
    _register_providers()
    configured = []
    for name, provider_class in _PROVIDERS.items():
        try:
            provider = provider_class()
            if provider.is_configured():
                configured.append(provider)
        except AIConfigurationError:
            # Provider not configured - expected, skip silently
            pass
        except AIError as e:
            logger.debug("Provider %s not available: %s", name, e)
        except (ImportError, ModuleNotFoundError) as e:
            logger.debug("Provider %s dependencies not installed: %s", name, e)
    return configured


def get_default_provider() -> Optional[AIProvider]:
    """Get the first configured provider.

    Priority order: gemini (free tier), ollama (local), anthropic, openai
    """
    priority = ["gemini", "ollama", "anthropic", "openai"]
    _register_providers()

    for name in priority:
        provider_class = _PROVIDERS.get(name)
        if provider_class:
            try:
                provider = provider_class()
                if provider.is_configured():
                    return provider
            except AIConfigurationError:
                # Provider not configured - expected, try next
                pass
            except AIError as e:
                logger.debug("Provider %s not available: %s", name, e)
            except (ImportError, ModuleNotFoundError) as e:
                logger.debug("Provider %s dependencies not installed: %s", name, e)

    return None
