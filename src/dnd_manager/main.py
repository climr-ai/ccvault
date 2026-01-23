"""Main entry point for D&D Character Manager CLI."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from dnd_manager.app import run_app
from dnd_manager.storage import CharacterStore
from dnd_manager.models.character import Character
from dnd_manager.config import get_config_manager, Config


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ccvault",
        description="CLIMR Character Vault - D&D 5e Character Manager",
    )

    # Get version from config (used as fallback if package metadata unavailable)
    config = get_config_manager().config
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {config.versions.app_version}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command (default - launches TUI)
    run_parser = subparsers.add_parser("run", help="Launch the character manager TUI")
    run_parser.add_argument(
        "character",
        nargs="?",
        type=Path,
        help="Path to character YAML file to open",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List all characters")

    # New command
    new_parser = subparsers.add_parser("new", help="Create a new character")
    new_parser.add_argument("name", help="Character name")
    new_parser.add_argument(
        "--class",
        dest="char_class",
        default=None,
        help=f"Starting class (default: {config.character_defaults.class_name})",
    )
    new_parser.add_argument(
        "--level",
        type=int,
        default=1,
        help="Starting level (default: 1)",
    )

    # Show command
    show_parser = subparsers.add_parser("show", help="Show character summary")
    show_parser.add_argument("name", help="Character name")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a character")
    delete_parser.add_argument("name", help="Character name")
    delete_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Delete without confirmation",
    )

    # Export command
    export_parser = subparsers.add_parser("export", help="Export character to Markdown or PDF")
    export_parser.add_argument("name", help="Character name")
    export_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (default: <name>.md or <name>.pdf)",
    )
    export_parser.add_argument(
        "-f", "--format",
        choices=["md", "markdown", "pdf", "html"],
        default="md",
        help="Export format (default: md)",
    )

    # Roll command
    roll_parser = subparsers.add_parser("roll", help="Roll dice")
    roll_parser.add_argument("dice", help="Dice notation (e.g., 2d6+5, 4d6kh3, adv)")
    roll_parser.add_argument(
        "-n", "--times",
        type=int,
        default=1,
        help="Number of times to roll (default: 1)",
    )

    # AI chat command
    ai_parser = subparsers.add_parser("ask", help="Ask the AI assistant a D&D question")
    ai_parser.add_argument("question", nargs="*", help="Question to ask (or enter interactive mode)")
    ai_parser.add_argument(
        "-c", "--character",
        help="Character name for context",
    )
    ai_parser.add_argument(
        "--provider",
        default="gemini",
        help="AI provider (gemini, anthropic, openai, ollama)",
    )
    ai_parser.add_argument(
        "--model",
        help="Specific model to use",
    )
    ai_parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive chat session",
    )
    ai_parser.add_argument(
        "--quota",
        action="store_true",
        help="Show current quota status (Gemini only)",
    )
    ai_parser.add_argument(
        "-m", "--mode",
        choices=["assistant", "dm", "roleplay", "rules", "homebrew"],
        default="assistant",
        help="AI mode (default: assistant)",
    )
    ai_parser.add_argument(
        "--homebrew-type",
        choices=["spell", "magic_item", "race", "class", "subclass", "feat", "background"],
        help="Type of homebrew content to create (only with --mode homebrew)",
    )
    ai_parser.add_argument(
        "--tools",
        action="store_true",
        help="Enable tool calling for character manipulation (requires --character)",
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration settings")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config commands")

    # config list
    config_list_parser = config_subparsers.add_parser("list", help="List all settings")
    config_list_parser.add_argument(
        "--show-keys",
        action="store_true",
        help="Show full API keys (not masked)",
    )

    # config get
    config_get_parser = config_subparsers.add_parser("get", help="Get a setting value")
    config_get_parser.add_argument("key", help="Setting key (e.g., ai.gemini.api_key)")

    # config set
    config_set_parser = config_subparsers.add_parser("set", help="Set a setting value")
    config_set_parser.add_argument("key", help="Setting key (e.g., ai.gemini.api_key)")
    config_set_parser.add_argument("value", help="Value to set")

    # config reset
    config_subparsers.add_parser("reset", help="Reset all settings to defaults")

    # config path
    config_subparsers.add_parser("path", help="Show config file location")

    # Custom content command
    custom_parser = subparsers.add_parser("custom", help="Manage custom homebrew content")
    custom_subparsers = custom_parser.add_subparsers(dest="custom_command", help="Custom content commands")

    # custom list
    custom_list_parser = custom_subparsers.add_parser("list", help="List all custom content")
    custom_list_parser.add_argument(
        "--type",
        choices=["spells", "items", "feats", "all"],
        default="all",
        help="Type of content to list (default: all)",
    )

    # custom add spell
    custom_add_spell_parser = custom_subparsers.add_parser("add-spell", help="Add a custom spell")
    custom_add_spell_parser.add_argument("name", help="Spell name")
    custom_add_spell_parser.add_argument("--level", type=int, default=1, help="Spell level (0-9, default: 1)")
    custom_add_spell_parser.add_argument("--school", default="Evocation", help="Spell school")
    custom_add_spell_parser.add_argument("--classes", nargs="+", default=["Wizard"], help="Classes that can use this spell")
    custom_add_spell_parser.add_argument("--description", default="", help="Spell description")

    # custom add item
    custom_add_item_parser = custom_subparsers.add_parser("add-item", help="Add a custom item")
    custom_add_item_parser.add_argument("name", help="Item name")
    custom_add_item_parser.add_argument("--type", dest="item_type", default="wondrous", help="Item type")
    custom_add_item_parser.add_argument("--rarity", default="uncommon", help="Item rarity")
    custom_add_item_parser.add_argument("--description", default="", help="Item description")
    custom_add_item_parser.add_argument("--attunement", action="store_true", help="Requires attunement")

    # custom import
    custom_import_parser = custom_subparsers.add_parser("import", help="Import custom content from YAML")
    custom_import_parser.add_argument("file", type=Path, help="YAML file to import")

    # custom export
    custom_export_parser = custom_subparsers.add_parser("export", help="Export custom content to YAML")
    custom_export_parser.add_argument("file", type=Path, help="Output YAML file")

    # custom validate
    custom_subparsers.add_parser("validate", help="Validate all custom content")

    # custom path
    custom_subparsers.add_parser("path", help="Show custom content directory")

    # Guidelines command
    guide_parser = subparsers.add_parser("guidelines", help="View and manage homebrew balance guidelines")
    guide_subparsers = guide_parser.add_subparsers(dest="guide_command", help="Guidelines commands")

    # guidelines show
    guide_show_parser = guide_subparsers.add_parser("show", help="Show guidelines for a content type")
    guide_show_parser.add_argument(
        "type",
        choices=["spell", "magic_item", "race", "class", "subclass", "feat", "background", "general"],
        help="Type of content",
    )

    # guidelines list
    guide_subparsers.add_parser("list", help="List all available guideline sections")

    # guidelines path
    guide_subparsers.add_parser("path", help="Show guidelines file locations")

    # guidelines reset
    guide_subparsers.add_parser("reset", help="Reset to default guidelines")

    # Session notes command
    notes_parser = subparsers.add_parser("notes", help="Manage session notes with vector search")
    notes_subparsers = notes_parser.add_subparsers(dest="notes_command", help="Notes commands")

    # notes list
    notes_list_parser = notes_subparsers.add_parser("list", help="List session notes")
    notes_list_parser.add_argument(
        "--campaign",
        help="Filter by campaign name",
    )
    notes_list_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of notes to show (default: 20)",
    )

    # notes add
    notes_add_parser = notes_subparsers.add_parser("add", help="Add a new session note")
    notes_add_parser.add_argument("title", help="Note title")
    notes_add_parser.add_argument(
        "-c", "--content",
        help="Note content (or opens editor if not provided)",
    )
    notes_add_parser.add_argument(
        "--campaign",
        help="Campaign name",
    )
    notes_add_parser.add_argument(
        "--date",
        help="Session date (YYYY-MM-DD, default: today)",
    )
    notes_add_parser.add_argument(
        "--tags",
        nargs="+",
        default=[],
        help="Tags for the note",
    )

    # notes search
    notes_search_parser = notes_subparsers.add_parser("search", help="Search session notes")
    notes_search_parser.add_argument("query", help="Search query")
    notes_search_parser.add_argument(
        "--semantic",
        action="store_true",
        default=True,
        help="Use semantic search (default: True)",
    )
    notes_search_parser.add_argument(
        "--keyword",
        action="store_true",
        help="Use keyword search only",
    )
    notes_search_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum results (default: 10)",
    )

    # notes show
    notes_show_parser = notes_subparsers.add_parser("show", help="Show a specific note")
    notes_show_parser.add_argument("id", type=int, help="Note ID")

    # notes delete
    notes_delete_parser = notes_subparsers.add_parser("delete", help="Delete a note")
    notes_delete_parser.add_argument("id", type=int, help="Note ID")

    # notes stats
    notes_subparsers.add_parser("stats", help="Show session notes statistics")

    # notes reindex
    notes_subparsers.add_parser("reindex", help="Regenerate embeddings for all notes")

    # Library command (CLIMR Homebrew Library)
    lib_parser = subparsers.add_parser("library", help="CLIMR Homebrew Library - browse and share content")
    lib_subparsers = lib_parser.add_subparsers(dest="lib_command", help="Library commands")

    # library browse
    lib_browse_parser = lib_subparsers.add_parser("browse", help="Browse homebrew content")
    lib_browse_parser.add_argument(
        "--type",
        choices=["spell", "magic_item", "race", "class", "subclass", "feat", "background", "monster"],
        help="Filter by content type",
    )
    lib_browse_parser.add_argument(
        "--sort",
        choices=["rating", "downloads", "recent", "name"],
        default="rating",
        help="Sort order (default: rating)",
    )
    lib_browse_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum results (default: 20)",
    )

    # library search
    lib_search_parser = lib_subparsers.add_parser("search", help="Search library content")
    lib_search_parser.add_argument("query", help="Search query")
    lib_search_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum results (default: 10)",
    )

    # library show
    lib_show_parser = lib_subparsers.add_parser("show", help="Show content details")
    lib_show_parser.add_argument("id", help="Content ID")

    # library install
    lib_install_parser = lib_subparsers.add_parser("install", help="Install content to your collection")
    lib_install_parser.add_argument("id", help="Content ID")

    # library uninstall
    lib_uninstall_parser = lib_subparsers.add_parser("uninstall", help="Remove installed content")
    lib_uninstall_parser.add_argument("id", help="Content ID")

    # library installed
    lib_subparsers.add_parser("installed", help="List installed content")

    # library rate
    lib_rate_parser = lib_subparsers.add_parser("rate", help="Rate content (1-5 stars)")
    lib_rate_parser.add_argument("id", help="Content ID")
    lib_rate_parser.add_argument("rating", type=int, choices=[1, 2, 3, 4, 5], help="Rating (1-5)")
    lib_rate_parser.add_argument("--review", help="Optional review text")

    # library publish
    lib_publish_parser = lib_subparsers.add_parser("publish", help="Publish your content")
    lib_publish_parser.add_argument("id", help="Content ID")

    # library my
    lib_subparsers.add_parser("my", help="List your published content")

    # library import
    lib_import_parser = lib_subparsers.add_parser("import", help="Import custom content to library")

    # library stats
    lib_subparsers.add_parser("stats", help="Show library statistics")

    return parser


def cmd_list() -> int:
    """List all characters."""
    store = CharacterStore()
    characters = store.get_character_info()

    if not characters:
        print("No characters found.")
        print(f"Characters are stored in: {store.directory}")
        return 0

    print(f"Characters ({len(characters)}):")
    print("-" * 60)

    for char in characters:
        class_info = char["class"]
        if char["subclass"]:
            class_info += f" ({char['subclass']})"

        print(f"  {char['name']}")
        print(f"    Level {char['level']} {class_info}")
        print(f"    Species: {char['species'] or 'Not set'}")
        print(f"    Ruleset: {char['ruleset']}")
        print(f"    Modified: {char['modified'].strftime('%Y-%m-%d %H:%M')}")
        print()

    return 0


def cmd_new(name: str, char_class: str, level: int) -> int:
    """Create a new character."""
    store = CharacterStore()

    if store.exists(name):
        print(f"Error: Character '{name}' already exists.")
        return 1

    character = store.create_new(name=name, class_name=char_class, level=level)
    path = store.save(character)

    print(f"Created new character: {name}")
    print(f"  Class: {char_class} (Level {level})")
    print(f"  Saved to: {path}")

    return 0


def cmd_delete(name: str, force: bool) -> int:
    """Delete a character with confirmation."""
    store = CharacterStore()

    if not store.exists(name):
        print(f"Error: Character '{name}' not found.")
        return 1

    if not force:
        print(f"Type the character name to confirm deletion: {name}")
        confirmation = input("> ").strip()
        if confirmation != name:
            print("Deletion cancelled (name did not match).")
            return 1

    if store.delete(name):
        print(f"Deleted character: {name}")
        return 0

    print("Error: Failed to delete character.")
    return 1


def cmd_export(name: str, output: Optional[Path], format: str) -> int:
    """Export character to Markdown, PDF, or HTML."""
    store = CharacterStore()
    character = store.load(name)

    if not character:
        print(f"Error: Character '{name}' not found.")
        return 1

    # Determine format and default output path
    safe_name = name.lower().replace(" ", "_")

    if format in ("md", "markdown"):
        from dnd_manager.export import export_to_markdown
        if output is None:
            output = Path(f"{safe_name}.md")
        content = export_to_markdown(character, output)
        print(f"Exported {name} to {output}")
        print(f"  {len(content)} characters written")

    elif format == "pdf":
        from dnd_manager.export import export_to_pdf
        if output is None:
            output = Path(f"{safe_name}.pdf")
        try:
            export_to_pdf(character, output)
            print(f"Exported {name} to {output}")
            print(f"  PDF character sheet created")
        except ImportError as e:
            print(f"Error: {e}")
            return 1

    elif format == "html":
        from dnd_manager.export import export_to_html
        if output is None:
            output = Path(f"{safe_name}.html")
        export_to_html(character, output)
        print(f"Exported {name} to {output}")
        print(f"  HTML character sheet created")

    return 0


def cmd_roll(dice: str, times: int) -> int:
    """Roll dice."""
    from dnd_manager.dice import DiceRoller
    from dnd_manager.dice.parser import is_valid_dice_notation

    if not is_valid_dice_notation(dice):
        print(f"Error: Invalid dice notation '{dice}'")
        print("Examples: 1d20, 2d6+5, 4d6kh3, adv, dis")
        return 1

    roller = DiceRoller()

    for i in range(times):
        result = roller.roll(dice)
        if times > 1:
            print(f"Roll {i + 1}: {result}")
        else:
            print(result)

    if times > 1:
        totals = [r.total for r in roller.history[-times:]]
        print(f"\nSum: {sum(totals)}  Avg: {sum(totals) / len(totals):.1f}")

    return 0


def cmd_ask(
    question: list[str],
    character_name: Optional[str],
    provider: str,
    model: Optional[str],
    interactive: bool,
    show_quota: bool,
    mode: str = "assistant",
    homebrew_type: Optional[str] = None,
    enable_tools: bool = False,
) -> int:
    """Ask the AI assistant a D&D question."""
    import asyncio
    from dnd_manager.ai import get_provider, build_system_prompt
    from dnd_manager.ai.context import build_homebrew_system_prompt

    # Get provider
    ai = get_provider(provider)
    if not ai:
        print(f"Error: Provider '{provider}' not available.")
        print("Available providers: gemini, anthropic, openai, ollama")
        return 1

    if not ai.is_configured():
        env_var = {
            "gemini": "GEMINI_API_KEY or GOOGLE_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "ollama": "(no key needed, ensure Ollama is running)",
        }.get(provider, "API_KEY")
        print(f"Error: {provider} not configured. Set {env_var}")
        return 1

    # Show quota status if requested (Gemini router only)
    if show_quota:
        if hasattr(ai, "get_quota_status"):
            print("Gemini Quota Status:")
            print("-" * 50)
            for model_name, status in ai.get_quota_status().items():
                available = "Available" if status["available"] else "Limited"
                print(f"  {model_name}:")
                print(f"    Requests: {status['requests_today']}/{status['daily_limit']} ({available})")
                if status["rate_limited_until"]:
                    print(f"    Rate limited until: {status['rate_limited_until']}")
        else:
            print("Quota status only available for Gemini router")
        return 0

    # Load character for context if specified
    character = None
    if character_name:
        store = CharacterStore()
        character = store.load(character_name)
        if not character:
            print(f"Warning: Character '{character_name}' not found, proceeding without context.")

    # Build system prompt based on mode
    if mode == "homebrew":
        system_prompt = build_homebrew_system_prompt(
            content_type=homebrew_type or "spell",
            character=character,
        )
    else:
        system_prompt = build_system_prompt(character, mode=mode)

    async def single_query(query: str) -> None:
        """Run a single query."""
        from dnd_manager.ai.base import AIMessage, MessageRole

        messages = [
            AIMessage(role=MessageRole.SYSTEM, content=system_prompt),
            AIMessage(role=MessageRole.USER, content=query),
        ]

        try:
            print()  # Blank line before response
            async for chunk in ai.chat_stream(messages, model=model):
                print(chunk, end="", flush=True)
            print()  # Newline after response
        except Exception as e:
            print(f"\nError: {e}")

    async def interactive_session() -> None:
        """Run interactive chat session."""
        from dnd_manager.ai.base import AIMessage, MessageRole

        messages = [AIMessage(role=MessageRole.SYSTEM, content=system_prompt)]

        mode_names = {
            "assistant": "D&D Assistant",
            "dm": "Dungeon Master Helper",
            "roleplay": "Roleplay Helper",
            "rules": "Rules Expert",
            "homebrew": "Homebrew Designer",
        }
        mode_name = mode_names.get(mode, "D&D Assistant")
        print(f"{mode_name} ({provider})")
        if character:
            print(f"Character context: {character.name}")
        if mode == "homebrew" and homebrew_type:
            print(f"Creating: {homebrew_type}")
        print("Type 'quit' or 'exit' to end, 'clear' to reset conversation")
        print("-" * 50)

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if user_input.lower() == "clear":
                messages = [AIMessage(role=MessageRole.SYSTEM, content=system_prompt)]
                print("Conversation cleared.")
                continue

            messages.append(AIMessage(role=MessageRole.USER, content=user_input))

            try:
                print("\nAssistant: ", end="", flush=True)
                response_text = ""
                async for chunk in ai.chat_stream(messages, model=model):
                    print(chunk, end="", flush=True)
                    response_text += chunk
                print()

                # Add assistant response to history
                messages.append(AIMessage(role=MessageRole.ASSISTANT, content=response_text))

            except Exception as e:
                print(f"\nError: {e}")

    async def interactive_session_with_tools() -> None:
        """Run interactive chat with tool calling support."""
        from dnd_manager.ai.tools import ToolSession

        if not character:
            print("Error: --tools requires --character to be specified")
            return

        store = CharacterStore()
        session = ToolSession(
            provider=ai,
            character=character,
            character_name=character_name,
            store=store,
            mode=mode,
            auto_save=True,
        )

        print(f"D&D Assistant with Tools ({provider})")
        class_name = character.primary_class.name if character.primary_class else "Unknown"
        print(f"Character: {character.name} (Level {character.total_level} {class_name})")
        print("Tool mode: AI can modify your character")
        print("Commands: 'quit' to exit, 'clear' to reset, 'refresh' to reload character")
        print("-" * 50)

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if user_input.lower() == "clear":
                session.clear_history()
                print("Conversation cleared.")
                continue
            if user_input.lower() == "refresh":
                session.refresh_character()
                print(f"Character reloaded: {session.character.name}")
                continue

            try:
                print("\nAssistant: ", end="", flush=True)
                response = await session.chat(
                    user_input,
                    stream_callback=lambda chunk: print(chunk, end="", flush=True),
                )
                # If there's more content after streaming (from tool results)
                if response and not response.endswith("\n"):
                    print()
            except Exception as e:
                print(f"\nError: {e}")

    # Run appropriate mode
    if enable_tools and interactive:
        if not character_name:
            print("Error: --tools requires --character to specify a character")
            return 1
        asyncio.run(interactive_session_with_tools())
    elif interactive or not question:
        asyncio.run(interactive_session())
    else:
        query = " ".join(question)
        asyncio.run(single_query(query))

    return 0


def cmd_show(name: str) -> int:
    """Show character summary."""
    store = CharacterStore()
    character = store.load(name)

    if not character:
        print(f"Error: Character '{name}' not found.")
        return 1

    c = character
    print(f"═══ {c.name} ═══")
    print()

    # Class info
    if c.primary_class:
        class_info = f"Level {c.total_level} {c.primary_class.name}"
        if c.primary_class.subclass:
            class_info += f" ({c.primary_class.subclass})"
    else:
        class_info = f"Level {c.total_level} (No class)"
    print(f"Class: {class_info}")

    if c.species:
        species_info = c.species
        if c.subspecies:
            species_info += f" ({c.subspecies})"
        print(f"Species: {species_info}")

    if c.background:
        print(f"Background: {c.background}")

    print(f"Alignment: {c.alignment.display_name}")
    print()

    # Ability scores
    print("Ability Scores:")
    for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        score = getattr(c.abilities, ability)
        abbr = ability[:3].upper()
        print(f"  {abbr}: {score.total:2d} ({score.modifier_str})")
    print()

    # Combat stats
    print("Combat:")
    print(f"  AC: {c.combat.total_ac}")
    print(f"  HP: {c.combat.hit_points.current}/{c.combat.hit_points.maximum}")
    print(f"  Initiative: {c.get_initiative():+d}")
    print(f"  Speed: {c.combat.total_speed} ft")
    print(f"  Proficiency Bonus: +{c.proficiency_bonus}")
    print()

    # Ruleset
    print(f"Ruleset: {c.meta.ruleset.value}")

    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """Handle config subcommands."""
    manager = get_config_manager()

    if args.config_command == "list":
        settings = manager.list_settings(show_sensitive=args.show_keys)
        print("Configuration Settings:")
        print("-" * 60)
        for key, value in sorted(settings.items()):
            if value is None:
                print(f"  {key}: (not set)")
            elif isinstance(value, bool):
                print(f"  {key}: {str(value).lower()}")
            else:
                print(f"  {key}: {value}")
        print()
        print(f"Config file: {Config.get_config_path()}")
        return 0

    elif args.config_command == "get":
        value = manager.get(args.key)
        if value is None:
            print(f"Setting '{args.key}' not found.")
            return 1
        print(value)
        return 0

    elif args.config_command == "set":
        if manager.set(args.key, args.value):
            print(f"Set {args.key} = {args.value}")
            return 0
        else:
            print(f"Error: Invalid setting key '{args.key}'")
            print("\nAvailable settings:")
            for key in sorted(manager.list_settings().keys()):
                print(f"  {key}")
            return 1

    elif args.config_command == "reset":
        manager.reset()
        print("Configuration reset to defaults.")
        print(f"Config file: {Config.get_config_path()}")
        return 0

    elif args.config_command == "path":
        print(Config.get_config_path())
        return 0

    else:
        # No subcommand, show help
        print("Usage: ccvault config <command>")
        print()
        print("Commands:")
        print("  list        List all settings")
        print("  get <key>   Get a setting value")
        print("  set <key> <value>  Set a setting value")
        print("  reset       Reset all settings to defaults")
        print("  path        Show config file location")
        print()
        print("Examples:")
        print("  ccvaultconfig list")
        print("  ccvaultconfig set ai.gemini.api_key YOUR_API_KEY")
        print("  ccvaultconfig set ai.default_provider anthropic")
        print("  ccvaultconfig get ai.default_provider")
        return 0


def cmd_custom(args: argparse.Namespace) -> int:
    """Handle custom content subcommands."""
    from dnd_manager.data.custom import (
        get_custom_content_store,
        CustomSpell,
        CustomItem,
    )

    store = get_custom_content_store()

    if args.custom_command == "list":
        content = store.content
        content_type = args.type

        if content_type in ("all", "spells"):
            print(f"Custom Spells ({len(content.spells)}):")
            print("-" * 50)
            if content.spells:
                for spell in content.spells:
                    level_str = "Cantrip" if spell.level == 0 else f"Level {spell.level}"
                    print(f"  {spell.name} ({level_str} {spell.school})")
                    if spell.classes:
                        print(f"    Classes: {', '.join(spell.classes)}")
            else:
                print("  (No custom spells)")
            print()

        if content_type in ("all", "items"):
            print(f"Custom Items ({len(content.items)}):")
            print("-" * 50)
            if content.items:
                for item in content.items:
                    attune = " (attunement)" if item.requires_attunement else ""
                    print(f"  {item.name} ({item.rarity} {item.item_type}){attune}")
                    if item.description:
                        desc = item.description[:60] + "..." if len(item.description) > 60 else item.description
                        print(f"    {desc}")
            else:
                print("  (No custom items)")
            print()

        if content_type in ("all", "feats"):
            print(f"Custom Feats ({len(content.feats)}):")
            print("-" * 50)
            if content.feats:
                for feat in content.feats:
                    print(f"  {feat.name} ({feat.category})")
                    if feat.prerequisites:
                        print(f"    Prerequisites: {', '.join(feat.prerequisites)}")
            else:
                print("  (No custom feats)")
            print()

        return 0

    elif args.custom_command == "add-spell":
        spell = CustomSpell(
            name=args.name,
            level=args.level,
            school=args.school,
            classes=args.classes,
            description=args.description,
            casting_time="1 action",
            range="Self",
            components="V, S",
            duration="Instantaneous",
        )

        warnings = store.add_spell(spell)

        if any(w.severity == "error" for w in warnings):
            print("Error: Could not add spell due to validation errors:")
            for w in warnings:
                print(f"  [{w.severity}] {w.message}")
            return 1

        # Save to a file
        store.save("custom_spells.yaml", store.content)

        print(f"Added spell: {args.name}")
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(f"  {w.message}")

        return 0

    elif args.custom_command == "add-item":
        item = CustomItem(
            name=args.name,
            item_type=args.item_type,
            rarity=args.rarity,
            description=args.description,
            requires_attunement=args.attunement,
        )

        warnings = store.add_item(item)

        if any(w.severity == "error" for w in warnings):
            print("Error: Could not add item due to validation errors:")
            for w in warnings:
                print(f"  [{w.severity}] {w.message}")
            return 1

        # Save to a file
        store.save("custom_items.yaml", store.content)

        print(f"Added item: {args.name}")
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(f"  {w.message}")

        return 0

    elif args.custom_command == "import":
        if not args.file.exists():
            print(f"Error: File not found: {args.file}")
            return 1

        imported, warnings = store.import_from_yaml(args.file)

        print(f"Imported content from {args.file}:")
        print(f"  Spells: {len(imported.spells)}")
        print(f"  Items: {len(imported.items)}")
        print(f"  Feats: {len(imported.feats)}")

        if warnings:
            print("\nWarnings:")
            for w in warnings:
                print(f"  [{w.severity}] {w.content_name}: {w.message}")

        return 0

    elif args.custom_command == "export":
        store.export_to_yaml(args.file)
        content = store.content

        print(f"Exported custom content to {args.file}:")
        print(f"  Spells: {len(content.spells)}")
        print(f"  Items: {len(content.items)}")
        print(f"  Feats: {len(content.feats)}")

        return 0

    elif args.custom_command == "validate":
        warnings = store.validate()

        if not warnings:
            print("All custom content is valid!")
            return 0

        errors = [w for w in warnings if w.severity == "error"]
        warns = [w for w in warnings if w.severity == "warning"]

        if errors:
            print(f"Errors ({len(errors)}):")
            for w in errors:
                print(f"  [{w.content_type}] {w.content_name}: {w.message}")

        if warns:
            print(f"\nWarnings ({len(warns)}):")
            for w in warns:
                print(f"  [{w.content_type}] {w.content_name}: {w.message}")

        return 1 if errors else 0

    elif args.custom_command == "path":
        print(store.content_dir)
        return 0

    else:
        # No subcommand, show help
        print("Usage: ccvault custom <command>")
        print()
        print("Commands:")
        print("  list          List all custom content")
        print("  add-spell     Add a custom spell")
        print("  add-item      Add a custom item")
        print("  import <file> Import content from YAML")
        print("  export <file> Export content to YAML")
        print("  validate      Validate all custom content")
        print("  path          Show custom content directory")
        print()
        print("Examples:")
        print('  ccvaultcustom list')
        print('  ccvaultcustom add-spell "Chronal Bolt" --level 2 --school Evocation --classes Wizard Sorcerer')
        print('  ccvaultcustom add-item "Bag of Infinite Snacks" --rarity rare --attunement')
        print('  ccvaultcustom import my_homebrew.yaml')
        print('  ccvaultcustom export all_custom.yaml')
        return 0


def cmd_guidelines(args: argparse.Namespace) -> int:
    """Handle guidelines subcommands."""
    from dnd_manager.data.balance import (
        get_balance_guidelines,
        get_guidelines_manager,
        get_homebrew_prompt,
    )

    manager = get_guidelines_manager()

    if args.guide_command == "show":
        content_type = args.type
        if content_type == "general":
            guidelines = get_balance_guidelines()
            print(guidelines._build_general_prompt())
        else:
            prompt = get_homebrew_prompt(content_type)
            print(prompt)
        return 0

    elif args.guide_command == "list":
        print("Available Guideline Sections:")
        print("-" * 40)
        sections = [
            ("spell", "Spell creation guidelines"),
            ("magic_item", "Magic item creation guidelines"),
            ("race", "Race/species creation guidelines"),
            ("class", "Class creation guidelines"),
            ("subclass", "Subclass creation guidelines"),
            ("feat", "Feat creation guidelines"),
            ("background", "Background creation guidelines"),
            ("general", "General design principles"),
        ]
        for section, desc in sections:
            print(f"  {section:12} - {desc}")
        print()
        print("Usage: ccvault guidelines show <section>")
        return 0

    elif args.guide_command == "path":
        print("Guidelines files:")
        print(f"  Default: {manager._default_path}")
        print(f"  User overrides: {manager._user_path}")
        if manager._user_path.exists():
            print("  (User overrides file exists)")
        else:
            print("  (No user overrides)")
        return 0

    elif args.guide_command == "reset":
        manager.reset_to_defaults()
        print("Guidelines reset to defaults.")
        return 0

    else:
        print("Usage: ccvault guidelines <command>")
        print()
        print("Commands:")
        print("  show <type>  Show guidelines for a content type")
        print("  list         List all available guideline sections")
        print("  path         Show guidelines file locations")
        print("  reset        Reset to default guidelines")
        print()
        print("Examples:")
        print("  ccvault guidelines show spell")
        print("  ccvault guidelines show magic_item")
        print("  ccvault guidelines list")
        return 0


def cmd_library(args: argparse.Namespace) -> int:
    """Handle homebrew library subcommands."""
    from dnd_manager.data.library import (
        get_homebrew_library,
        ContentType,
        ContentStatus,
        LibraryContent,
        LibraryAuthor,
    )

    library = get_homebrew_library()

    if args.lib_command == "browse":
        content_type = ContentType(args.type) if args.type else None
        items = library.browse(
            content_type=content_type,
            sort_by=args.sort,
            limit=args.limit,
        )

        if not items:
            print("No content found in library.")
            print("Use 'ccvault library import' to import your custom content.")
            return 0

        type_filter = f" ({args.type})" if args.type else ""
        print(f"Homebrew Library{type_filter} - sorted by {args.sort}:")
        print("-" * 70)

        for item in items:
            stars = "★" * int(item.rating.average) + "☆" * (5 - int(item.rating.average))
            votes = f"({item.rating.count})" if item.rating.count > 0 else "(no ratings)"
            installed = " [installed]" if library.is_installed(item.id) else ""

            print(f"  [{item.content_type.value:12}] {item.name}{installed}")
            print(f"      {stars} {votes}  Downloads: {item.downloads}")
            print(f"      ID: {item.id[:8]}...  by {item.author.name}")
            print()

        return 0

    elif args.lib_command == "search":
        results = library.search(args.query, limit=args.limit)

        if not results:
            print(f"No content found for: {args.query}")
            return 0

        print(f"Search Results for '{args.query}':")
        print("-" * 60)

        for item in results:
            stars = "★" * int(item.rating.average) + "☆" * (5 - int(item.rating.average))
            print(f"  [{item.content_type.value:12}] {item.name}")
            print(f"      {stars}  ID: {item.id[:8]}...")
            print()

        return 0

    elif args.lib_command == "show":
        item = library.get(args.id)
        if not item:
            # Try partial ID match
            results = [c for c in library.browse(limit=100) if c.id.startswith(args.id)]
            if len(results) == 1:
                item = results[0]
            elif len(results) > 1:
                print(f"Multiple matches for '{args.id}':")
                for r in results[:5]:
                    print(f"  {r.id} - {r.name}")
                return 1
            else:
                print(f"Content not found: {args.id}")
                return 1

        stars = "★" * int(item.rating.average) + "☆" * (5 - int(item.rating.average))
        installed = " [INSTALLED]" if library.is_installed(item.id) else ""

        print(f"═══ {item.name} ═══{installed}")
        print(f"Type: {item.content_type.value}")
        print(f"Ruleset: {item.ruleset}")
        print(f"Rating: {stars} ({item.rating.average:.1f}/5 from {item.rating.count} votes)")
        print(f"Downloads: {item.downloads}")
        print(f"Author: {item.author.name}")
        print(f"Version: {item.version}")
        print(f"ID: {item.id}")
        print()
        print("-" * 40)
        print(f"Description: {item.description}")
        print()
        if item.tags:
            print(f"Tags: {', '.join(item.tags)}")
        print()
        print("Content Data:")
        import json
        print(json.dumps(item.content_data, indent=2))

        # Show user's rating if exists
        user_rating = library.get_user_rating(item.id)
        if user_rating:
            print()
            print(f"Your Rating: {'★' * user_rating.rating}")
            if user_rating.review:
                print(f"Your Review: {user_rating.review}")

        return 0

    elif args.lib_command == "install":
        item = library.get(args.id)
        if not item:
            print(f"Content not found: {args.id}")
            return 1

        if library.is_installed(item.id):
            print(f"Already installed: {item.name}")
            return 0

        library.install(item.id)
        print(f"Installed: {item.name}")
        print("  Content is now available in your collection.")
        return 0

    elif args.lib_command == "uninstall":
        item = library.get(args.id)
        if not item:
            print(f"Content not found: {args.id}")
            return 1

        if not library.is_installed(item.id):
            print(f"Not installed: {item.name}")
            return 0

        library.uninstall(item.id)
        print(f"Uninstalled: {item.name}")
        return 0

    elif args.lib_command == "installed":
        items = library.get_installed()

        if not items:
            print("No installed content.")
            print("Use 'ccvault library browse' to find content to install.")
            return 0

        print(f"Installed Content ({len(items)}):")
        print("-" * 60)

        for item in items:
            print(f"  [{item.content_type.value:12}] {item.name}")
            print(f"      ID: {item.id[:8]}...  by {item.author.name}")
            print()

        return 0

    elif args.lib_command == "rate":
        item = library.get(args.id)
        if not item:
            print(f"Content not found: {args.id}")
            return 1

        library.rate(item.id, args.rating, args.review)
        stars = "★" * args.rating + "☆" * (5 - args.rating)
        print(f"Rated '{item.name}': {stars}")
        if args.review:
            print(f"Review: {args.review}")
        return 0

    elif args.lib_command == "publish":
        item = library.get(args.id)
        if not item:
            print(f"Content not found: {args.id}")
            return 1

        if library.publish(item.id):
            print(f"Published: {item.name}")
            print("  Content is now visible in the library.")
        else:
            print(f"Cannot publish: You are not the author of '{item.name}'")
            return 1
        return 0

    elif args.lib_command == "my":
        items = library.get_my_content()

        if not items:
            print("You haven't created any library content yet.")
            print("Use 'ccvault library import' to import your custom content.")
            return 0

        print(f"Your Content ({len(items)}):")
        print("-" * 60)

        for item in items:
            status_badge = f"[{item.status.value}]"
            print(f"  {status_badge:12} {item.name}")
            print(f"      Type: {item.content_type.value}  ID: {item.id[:8]}...")
            print()

        return 0

    elif args.lib_command == "import":
        from dnd_manager.data.custom import get_custom_content_store

        store = get_custom_content_store()
        content = store.content

        if not content.spells and not content.items and not content.feats:
            print("No custom content to import.")
            print("Use 'ccvault custom add-spell' or 'ccvault custom add-item' first.")
            return 0

        imported = library.import_from_custom(content)

        print(f"Imported {len(imported)} items to library:")
        for item in imported:
            print(f"  [{item.content_type.value}] {item.name}")

        print()
        print("Use 'ccvault library publish <id>' to make content visible.")
        return 0

    elif args.lib_command == "stats":
        stats = library.get_stats()

        print("CLIMR Homebrew Library Statistics:")
        print("-" * 40)
        print(f"  Total content: {stats['total_content']}")
        print(f"  Published: {stats['published']}")
        print(f"  Your content: {stats['my_content']}")
        print(f"  Installed: {stats['installed']}")
        print()

        if stats['by_type']:
            print("By Type:")
            for content_type, count in stats['by_type'].items():
                print(f"    {content_type}: {count}")
            print()

        if stats['top_rated']:
            print("Top Rated:")
            for item in stats['top_rated']:
                stars = "★" * int(item['rating'])
                print(f"    {stars} {item['name']} ({item['votes']} votes)")
            print()

        if stats['most_downloaded']:
            print("Most Downloaded:")
            for item in stats['most_downloaded']:
                print(f"    {item['downloads']:4} downloads - {item['name']}")

        return 0

    else:
        print("Usage: ccvault library <command>")
        print()
        print("CLIMR Homebrew Library - Share and discover D&D homebrew content")
        print()
        print("Commands:")
        print("  browse        Browse published content")
        print("  search <q>    Search for content")
        print("  show <id>     View content details")
        print("  install <id>  Add content to your collection")
        print("  uninstall <id> Remove from collection")
        print("  installed     List your installed content")
        print("  rate <id> <1-5> Rate content")
        print("  publish <id>  Publish your content")
        print("  my            List your created content")
        print("  import        Import custom content to library")
        print("  stats         Show library statistics")
        print()
        print("Examples:")
        print("  ccvault library browse --type spell --sort rating")
        print('  ccvault library search "fire damage"')
        print("  ccvault library install abc123")
        print("  ccvault library rate abc123 5 --review 'Great spell!'")
        return 0


def cmd_notes(args: argparse.Namespace) -> int:
    """Handle session notes subcommands."""
    from datetime import date
    from dnd_manager.storage.notes import get_notes_store, SessionNote

    store = get_notes_store()

    if args.notes_command == "list":
        notes = store.get_all(campaign=args.campaign, limit=args.limit)

        if not notes:
            print("No session notes found.")
            return 0

        print(f"Session Notes ({len(notes)}):")
        print("-" * 60)
        for note in notes:
            date_str = note.session_date.strftime("%Y-%m-%d") if note.session_date else "No date"
            campaign_str = f" [{note.campaign}]" if note.campaign else ""
            print(f"  [{note.id}] {date_str}{campaign_str}")
            print(f"      {note.title}")
            if note.tags:
                print(f"      Tags: {', '.join(note.tags)}")
            print()
        return 0

    elif args.notes_command == "add":
        import os
        import tempfile
        import subprocess

        # Parse date
        if args.date:
            try:
                session_date = date.fromisoformat(args.date)
            except ValueError:
                print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD.")
                return 1
        else:
            session_date = date.today()

        # Get content from editor if not provided
        content = args.content
        if not content:
            config = get_config_manager().config
            fallback = config.ui.fallback_editor
            editor = os.environ.get("EDITOR", os.environ.get("VISUAL", fallback))
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".md",
                prefix="session_note_",
                delete=False,
            ) as f:
                f.write(f"# {args.title}\n\n")
                temp_path = f.name

            try:
                subprocess.run([editor, temp_path])
                with open(temp_path) as f:
                    content = f.read().strip()
            finally:
                os.unlink(temp_path)

        if not content:
            print("Error: Note content cannot be empty.")
            return 1

        note = SessionNote(
            title=args.title,
            content=content,
            session_date=session_date,
            campaign=args.campaign,
            tags=args.tags,
        )

        saved = store.add(note)
        print(f"Created note: {saved.title} (ID: {saved.id})")

        if store.embedding_engine.is_available():
            print("  Semantic search embedding generated.")
        else:
            print("  (Semantic search not available - install sentence-transformers)")

        return 0

    elif args.notes_command == "search":
        use_semantic = not args.keyword
        results = store.search(args.query, use_semantic=use_semantic, limit=args.limit)

        if not results:
            print(f"No notes found for: {args.query}")
            return 0

        search_type = "Semantic" if use_semantic and store.embedding_engine.is_available() else "Keyword"
        print(f"{search_type} Search Results ({len(results)}):")
        print("-" * 60)

        for result in results:
            note = result.note
            date_str = note.session_date.strftime("%Y-%m-%d") if note.session_date else "No date"
            score_str = f" (score: {result.score:.3f})"
            print(f"  [{note.id}] {date_str} - {note.title}{score_str}")

            # Show snippet of content
            snippet = note.content[:100].replace("\n", " ")
            if len(note.content) > 100:
                snippet += "..."
            print(f"      {snippet}")
            print()

        return 0

    elif args.notes_command == "show":
        note = store.get(args.id)
        if not note:
            print(f"Error: Note with ID {args.id} not found.")
            return 1

        print(f"═══ {note.title} ═══")
        print(f"Date: {note.session_date}")
        if note.campaign:
            print(f"Campaign: {note.campaign}")
        if note.tags:
            print(f"Tags: {', '.join(note.tags)}")
        print(f"Created: {note.created_at}")
        print(f"Updated: {note.updated_at}")
        print()
        print("-" * 40)
        print(note.content)
        return 0

    elif args.notes_command == "delete":
        note = store.get(args.id)
        if not note:
            print(f"Error: Note with ID {args.id} not found.")
            return 1

        store.delete(args.id)
        print(f"Deleted note: {note.title}")
        return 0

    elif args.notes_command == "stats":
        stats = store.get_stats()

        print("Session Notes Statistics:")
        print("-" * 40)
        print(f"  Total notes: {stats['total_notes']}")
        print(f"  With embeddings: {stats['notes_with_embeddings']}")
        print(f"  Campaigns: {stats['campaigns']}")
        print(f"  Embedding provider: {stats['embedding_provider']}")

        if stats["date_range"]:
            print(f"  Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")

        # Show available campaigns
        campaigns = store.get_campaigns()
        if campaigns:
            print(f"\nCampaigns:")
            for c in campaigns:
                print(f"    {c}")

        # Show available tags
        tags = store.get_tags()
        if tags:
            print(f"\nTags: {', '.join(tags)}")

        return 0

    elif args.notes_command == "reindex":
        if not store.embedding_engine.is_available():
            print("Error: No embedding provider available.")
            print("Install sentence-transformers: pip install sentence-transformers")
            return 1

        print("Regenerating embeddings for all notes...")
        count = store.reindex_embeddings()
        print(f"Reindexed {count} notes.")
        return 0

    else:
        print("Usage: ccvault notes <command>")
        print()
        print("Commands:")
        print("  list          List all session notes")
        print("  add <title>   Add a new session note")
        print("  search <q>    Search notes (semantic + keyword)")
        print("  show <id>     Show a specific note")
        print("  delete <id>   Delete a note")
        print("  stats         Show notes statistics")
        print("  reindex       Regenerate embeddings for search")
        print()
        print("Examples:")
        print('  ccvault notes list --campaign "Curse of Strahd"')
        print('  ccvault notes add "Session 12" --campaign "CoS" --tags combat boss')
        print('  ccvault notes search "vampire encounter"')
        print("  ccvault notes show 5")
        return 0


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Default to run command if no command specified
    if args.command is None:
        run_app()
        return 0

    if args.command == "run":
        run_app(character_path=args.character)
        return 0

    if args.command == "list":
        return cmd_list()

    if args.command == "new":
        # Use config default if class not specified
        config = get_config_manager().config
        char_class = args.char_class or config.character_defaults.class_name
        return cmd_new(args.name, char_class, args.level)

    if args.command == "show":
        return cmd_show(args.name)

    if args.command == "delete":
        return cmd_delete(args.name, args.force)

    if args.command == "export":
        return cmd_export(args.name, args.output, args.format)

    if args.command == "roll":
        return cmd_roll(args.dice, args.times)

    if args.command == "ask":
        return cmd_ask(
            args.question,
            args.character,
            args.provider,
            args.model,
            args.interactive,
            args.quota,
            args.mode,
            args.homebrew_type,
            args.tools,
        )

    if args.command == "config":
        return cmd_config(args)

    if args.command == "custom":
        return cmd_custom(args)

    if args.command == "guidelines":
        return cmd_guidelines(args)

    if args.command == "notes":
        return cmd_notes(args)

    if args.command == "library":
        return cmd_library(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
