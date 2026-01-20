#!/usr/bin/env python3
"""Test script for Gemini tool calling functionality.

Usage:
    GEMINI_API_KEY=your-key python scripts/test_gemini_tools.py

Or configure via:
    dnd config set ai.gemini.api_key your-key
    python scripts/test_gemini_tools.py
"""

import asyncio
import sys

from dnd_manager.ai.gemini import GeminiProvider
from dnd_manager.ai.base import AIMessage, MessageRole, ToolChoice
from dnd_manager.ai.tools import get_tool_registry


async def test_tool_calling():
    """Test that Gemini can call tools correctly."""
    provider = GeminiProvider()

    if not provider.is_configured():
        print("ERROR: Gemini API key not configured!")
        print()
        print("Set the key using one of these methods:")
        print("  1. Environment variable: export GEMINI_API_KEY=your-key")
        print("  2. Config file: dnd config set ai.gemini.api_key your-key")
        return False

    print("Gemini provider configured successfully!")
    print(f"Using model: {provider.default_model}")
    print()

    # Get tool definitions
    registry = get_tool_registry()
    tools = registry.get_anthropic_tool_definitions()
    print(f"Loaded {len(tools)} tool definitions")
    print()

    # Test simple chat first
    print("Test 1: Simple chat (no tools)...")
    messages = [
        AIMessage(role=MessageRole.USER, content="Say hello in 5 words or less."),
    ]

    try:
        response = await provider.chat(messages)
        print(f"  Response: {response.content}")
        print(f"  Tokens: {response.input_tokens} in, {response.output_tokens} out")
        print("  PASSED")
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    print()

    # Test tool calling with AUTO (AI decides)
    print("Test 2: Chat with tools (AUTO - AI decides)...")
    messages = [
        AIMessage(
            role=MessageRole.SYSTEM,
            content="You are a D&D assistant with tools. Use the deal_damage tool when asked to deal damage."
        ),
        AIMessage(
            role=MessageRole.USER,
            content="My character just took 10 slashing damage from a goblin. Please use the deal_damage tool to record this."
        ),
    ]

    try:
        response = await provider.chat_with_tools(messages, tools, tool_choice=ToolChoice.AUTO)
        print(f"  Text content: {response.content[:100] if response.content else '(none)'}...")
        print(f"  Has tool use: {response.has_tool_use}")
        if response.tool_use:
            for tu in response.tool_use:
                print(f"    Tool: {tu.name}")
                print(f"    Input: {tu.input}")
        print("  PASSED")
    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Test forced tool calling with ANY
    print("Test 3: Chat with tools (ANY - force tool use)...")
    messages = [
        AIMessage(
            role=MessageRole.SYSTEM,
            content="You are a D&D assistant. Use tools to help the player."
        ),
        AIMessage(
            role=MessageRole.USER,
            content="What's the weather like today?",  # Unrelated question - should still use a tool
        ),
    ]

    try:
        response = await provider.chat_with_tools(messages, tools, tool_choice=ToolChoice.ANY)
        print(f"  Text content: {response.content[:100] if response.content else '(none)'}...")
        print(f"  Has tool use: {response.has_tool_use}")
        if response.tool_use:
            for tu in response.tool_use:
                print(f"    Tool: {tu.name}")
                print(f"    Input: {tu.input}")
            print("  PASSED - AI was forced to use a tool")
        else:
            print("  FAILED - AI should have been forced to use a tool")
            return False
    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("All tests passed!")
    return True


def main():
    success = asyncio.run(test_tool_calling())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
