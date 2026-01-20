#!/usr/bin/env python3
"""Test AI integration with ruleset query tools.

This script tests that the AI correctly uses lookup tools instead of guessing.
"""

import asyncio
import sys

from dnd_manager.ai.gemini import GeminiProvider
from dnd_manager.ai.base import AIMessage, MessageRole, ToolChoice
from dnd_manager.ai.tools import get_tool_registry


async def test_ai_uses_lookup_tools():
    """Test that AI uses lookup tools for game data questions."""
    provider = GeminiProvider()

    if not provider.is_configured():
        print("ERROR: Gemini API key not configured!")
        return False

    print("Testing AI integration with ruleset query tools")
    print("=" * 60)
    print()

    registry = get_tool_registry()
    tools = registry.get_anthropic_tool_definitions()
    print(f"Loaded {len(tools)} tools")
    print()

    # Test 1: Spell lookup
    print("Test 1: Ask about a specific spell")
    print("-" * 40)
    messages = [
        AIMessage(
            role=MessageRole.SYSTEM,
            content="""You are a D&D rules expert. You have access to lookup tools.
IMPORTANT: When asked about spells, ALWAYS use the lookup_spell tool to get accurate information.
NEVER guess about spell details - look them up."""
        ),
        AIMessage(
            role=MessageRole.USER,
            content="What does the spell Counterspell do? What level is it?"
        ),
    ]

    try:
        response = await provider.chat_with_tools(messages, tools, tool_choice=ToolChoice.ANY)
        if response.has_tool_use:
            tool = response.tool_use[0]
            print(f"  AI called: {tool.name}")
            print(f"  Input: {tool.input}")
            if tool.name == "lookup_spell":
                print("  PASSED - AI used lookup_spell")
            else:
                print(f"  WARNING - AI used {tool.name} instead of lookup_spell")
        else:
            print("  FAILED - AI did not use any tool")
            return False
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    print()

    # Test 2: Class lookup
    print("Test 2: Ask about class features")
    print("-" * 40)
    messages = [
        AIMessage(
            role=MessageRole.SYSTEM,
            content="""You are a D&D rules expert. You have access to lookup tools.
IMPORTANT: When asked about class mechanics, ALWAYS use the lookup_class tool.
NEVER guess about class features - look them up."""
        ),
        AIMessage(
            role=MessageRole.USER,
            content="What hit die does a Barbarian use? What are their saving throw proficiencies?"
        ),
    ]

    try:
        response = await provider.chat_with_tools(messages, tools, tool_choice=ToolChoice.ANY)
        if response.has_tool_use:
            tool = response.tool_use[0]
            print(f"  AI called: {tool.name}")
            print(f"  Input: {tool.input}")
            if tool.name == "lookup_class":
                print("  PASSED - AI used lookup_class")
            else:
                print(f"  WARNING - AI used {tool.name} instead of lookup_class")
        else:
            print("  FAILED - AI did not use any tool")
            return False
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    print()

    # Test 3: Species lookup
    print("Test 3: Ask about species traits")
    print("-" * 40)
    messages = [
        AIMessage(
            role=MessageRole.SYSTEM,
            content="""You are a D&D rules expert. You have access to lookup tools.
IMPORTANT: When asked about species/race traits, ALWAYS use the lookup_species tool.
NEVER guess about racial abilities - look them up."""
        ),
        AIMessage(
            role=MessageRole.USER,
            content="What traits does a Dwarf have? What's their base speed?"
        ),
    ]

    try:
        response = await provider.chat_with_tools(messages, tools, tool_choice=ToolChoice.ANY)
        if response.has_tool_use:
            tool = response.tool_use[0]
            print(f"  AI called: {tool.name}")
            print(f"  Input: {tool.input}")
            if tool.name == "lookup_species":
                print("  PASSED - AI used lookup_species")
            else:
                print(f"  WARNING - AI used {tool.name} instead of lookup_species")
        else:
            print("  FAILED - AI did not use any tool")
            return False
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    print()

    # Test 4: Search for spells by class
    print("Test 4: Ask for class spell list")
    print("-" * 40)
    messages = [
        AIMessage(
            role=MessageRole.SYSTEM,
            content="""You are a D&D rules expert. You have access to lookup tools.
IMPORTANT: When asked about what spells a class can cast, use get_class_spells or search_spells.
NEVER guess about spell availability - look it up."""
        ),
        AIMessage(
            role=MessageRole.USER,
            content="What 2nd level spells can a Cleric prepare?"
        ),
    ]

    try:
        response = await provider.chat_with_tools(messages, tools, tool_choice=ToolChoice.ANY)
        if response.has_tool_use:
            tool = response.tool_use[0]
            print(f"  AI called: {tool.name}")
            print(f"  Input: {tool.input}")
            if tool.name in ["get_class_spells", "search_spells"]:
                print(f"  PASSED - AI used appropriate spell search tool")
            else:
                print(f"  WARNING - AI used {tool.name}")
        else:
            print("  FAILED - AI did not use any tool")
            return False
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    print()
    print("=" * 60)
    print("All tests passed! AI correctly uses lookup tools.")
    return True


def main():
    success = asyncio.run(test_ai_uses_lookup_tools())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
