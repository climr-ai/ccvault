"""AI-related screens for the D&D Manager application."""

import asyncio
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Input, RichLog, Static

from dnd_manager.config import get_config_manager
from dnd_manager.models.character import Character


class AIChatScreen(Screen):
    """Screen for AI chat assistant."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("ctrl+l", "clear", "Clear Chat"),
        Binding("m", "switch_mode", "Switch Mode"),
    ]

    MODES = [
        ("assistant", "General D&D Assistant"),
        ("dm", "Dungeon Master"),
        ("roleplay", "Roleplay Helper"),
        ("rules", "Rules Expert"),
        ("homebrew", "Homebrew Creator"),
    ]

    def __init__(self, character: Optional[Character] = None, mode: str = "assistant", **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.current_mode = mode
        self._messages: list = []
        self._provider = None

    def compose(self) -> ComposeResult:
        char_name = self.character.name if self.character else "No character"
        mode_name = dict(self.MODES).get(self.current_mode, "Assistant")
        yield Header()
        yield Container(
            Static(f"AI {mode_name} - {char_name}", id="chat-title", classes="title"),
            Static("\\[M] Switch Mode  \\[Ctrl+L] Clear  \\[Esc] Back", classes="subtitle"),
            Horizontal(
                *[Button(name, id=f"mode-{mode}", variant="primary" if mode == self.current_mode else "default", classes="mode-btn")
                  for mode, name in self.MODES],
                classes="mode-row",
            ),
            RichLog(id="chat-log", wrap=True, markup=True),
            Horizontal(
                Input(placeholder="Ask a question...", id="chat-input"),
                Button("Send", id="btn-send", variant="primary"),
                classes="chat-input-row",
            ),
            id="chat-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize chat on mount."""
        self.query_one("#chat-input", Input).focus()
        self._show_mode_intro()

    def _show_mode_intro(self) -> None:
        """Show introduction for current mode."""
        log = self.query_one("#chat-log", RichLog)
        mode_name = dict(self.MODES).get(self.current_mode, "Assistant")
        log.write(f"[bold cyan]{mode_name} ready![/]")

        if self.current_mode == "assistant":
            log.write("Ask about D&D rules, character builds, or anything else.")
        elif self.current_mode == "dm":
            log.write("Get help with encounters, NPCs, worldbuilding, and more.")
        elif self.current_mode == "roleplay":
            log.write("I'll help you roleplay your character authentically.")
        elif self.current_mode == "rules":
            log.write("Ask me about mechanics, edge cases, and rule clarifications.")
        elif self.current_mode == "homebrew":
            log.write("Describe your homebrew concept and I'll help balance it.")
            log.write("Examples: custom spells, magic items, races, classes, feats...")

        log.write("")

    def _update_mode_buttons(self) -> None:
        """Update mode button styles."""
        for mode, _ in self.MODES:
            btn = self.query_one(f"#mode-{mode}", Button)
            btn.variant = "primary" if mode == self.current_mode else "default"

        # Update title
        char_name = self.character.name if self.character else "No character"
        mode_name = dict(self.MODES).get(self.current_mode, "Assistant")
        self.query_one("#chat-title", Static).update(f"AI {mode_name} - {char_name}")

    async def _get_provider(self):
        """Get the AI provider."""
        if self._provider is None:
            from dnd_manager.ai import get_provider
            manager = get_config_manager()
            provider_name = manager.get("ai.default_provider") or "gemini"
            self._provider = get_provider(provider_name)
        return self._provider

    async def _send_message(self, message: str) -> None:
        """Send a message to the AI."""
        from dnd_manager.ai import build_system_prompt
        from dnd_manager.ai.context import build_homebrew_system_prompt
        from dnd_manager.ai.base import AIMessage, MessageRole

        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold green]You:[/] {message}")

        provider = await self._get_provider()
        if not provider:
            log.write("[bold red]Error:[/] No AI provider configured.")
            log.write("Run: ccvault config set ai.gemini.api_key YOUR_KEY")
            return

        if not provider.is_configured():
            log.write(f"[bold red]Error:[/] {provider.name} not configured.")
            log.write(f"Run: ccvault config set ai.{provider.name}.api_key YOUR_KEY")
            return

        # Build system prompt based on mode
        if self.current_mode == "homebrew":
            system_prompt = build_homebrew_system_prompt(
                content_type="",  # General homebrew mode
                character=self.character,
            )
        else:
            system_prompt = build_system_prompt(self.character, mode=self.current_mode)

        self._messages.append(AIMessage(role=MessageRole.USER, content=message))

        all_messages = [
            AIMessage(role=MessageRole.SYSTEM, content=system_prompt),
            *self._messages,
        ]

        log.write("[bold blue]Assistant:[/] ", end="")

        try:
            response_text = ""
            async for chunk in provider.chat_stream(all_messages):
                log.write(chunk, end="")
                response_text += chunk
            log.write("")  # Newline after response

            # Save assistant response
            self._messages.append(AIMessage(role=MessageRole.ASSISTANT, content=response_text))

        except Exception as e:
            log.write(f"\n[bold red]Error:[/] {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id
        if btn_id == "btn-send":
            self._submit_message()
        elif btn_id and btn_id.startswith("mode-"):
            mode = btn_id.replace("mode-", "")
            self._switch_to_mode(mode)

    def _switch_to_mode(self, mode: str) -> None:
        """Switch to a different chat mode."""
        if mode != self.current_mode:
            self.current_mode = mode
            self._messages.clear()
            self._update_mode_buttons()
            log = self.query_one("#chat-log", RichLog)
            log.clear()
            self._show_mode_intro()
            self.notify(f"Switched to {dict(self.MODES).get(mode, mode)} mode")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key."""
        if event.input.id == "chat-input":
            self._submit_message()

    def _submit_message(self) -> None:
        """Submit the current message."""
        input_widget = self.query_one("#chat-input", Input)
        message = input_widget.value.strip()
        if message:
            input_widget.value = ""
            asyncio.create_task(self._send_message(message))

    def action_back(self) -> None:
        """Return to dashboard."""
        self.app.pop_screen()

    def action_switch_mode(self) -> None:
        """Cycle to the next mode."""
        mode_ids = [m[0] for m in self.MODES]
        current_idx = mode_ids.index(self.current_mode)
        next_idx = (current_idx + 1) % len(mode_ids)
        self._switch_to_mode(mode_ids[next_idx])

    def action_clear(self) -> None:
        """Clear chat history."""
        self._messages.clear()
        log = self.query_one("#chat-log", RichLog)
        log.clear()
        self._show_mode_intro()
        self.notify("Chat cleared")


class AIOverlayScreen(ModalScreen):
    """Global AI overlay modal that can be accessed from any screen.

    This provides a unified AI assistant that can answer questions about D&D,
    help with the current screen context, and create characters through
    natural conversation - all in one interface.
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("ctrl+l", "clear", "Clear Chat"),
    ]

    def __init__(self, screen_context: dict = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.screen_context = screen_context or {}
        self._messages: list = []
        self._provider = None
        self._tool_session = None
        self._creation_session_id = "overlay_creation"

    def compose(self) -> ComposeResult:
        context_type = self.screen_context.get("screen_type", "General")

        yield Container(
            Static("AI Assistant", id="overlay-title", classes="title"),
            Static(f"Context: {context_type}", id="overlay-context", classes="subtitle"),
            RichLog(id="overlay-log", wrap=True, markup=True),
            Horizontal(
                Input(placeholder="Ask a question or describe your character...", id="overlay-input"),
                Button("Send", id="btn-overlay-send", variant="primary"),
                classes="chat-input-row",
            ),
            id="ai-overlay-container",
            classes="ai-overlay",
        )

    def on_mount(self) -> None:
        """Initialize on mount."""
        self.query_one("#overlay-input", Input).focus()
        self._show_intro()

    def _show_intro(self) -> None:
        """Show introduction message."""
        log = self.query_one("#overlay-log", RichLog)
        log.write("[bold cyan]AI Assistant[/]")

        screen_type = self.screen_context.get("screen_type", "")
        description = self.screen_context.get("description", "")
        if screen_type:
            log.write(f"You're on: {screen_type}")
        if description:
            log.write(f"{description}")

        log.write("")
        log.write("I can help you with:")
        log.write("  - Creating characters through conversation")
        log.write("  - D&D rules, mechanics, and optimization")
        log.write("  - Questions about what you're looking at")
        log.write("")

    async def _get_provider(self):
        """Get the AI provider."""
        if self._provider is None:
            from dnd_manager.ai import get_provider
            manager = get_config_manager()
            provider_name = manager.get("ai.default_provider") or "gemini"
            self._provider = get_provider(provider_name)
        return self._provider

    def _build_system_prompt(self) -> str:
        """Build unified system prompt for AI assistant."""
        # Build context section
        context_info = ""
        if self.screen_context:
            screen_type = self.screen_context.get('screen_type', '')
            description = self.screen_context.get('description', '')
            if screen_type:
                context_info = f"\nCURRENT CONTEXT:\nScreen: {screen_type}"
                if description:
                    context_info += f"\nDescription: {description}"

            if 'character' in self.screen_context:
                char = self.screen_context['character']
                context_info += f"""
Character: {char.get('name', 'Unknown')}
Class: {char.get('class', 'Unknown')}
Level: {char.get('level', 1)}"""

            if 'data' in self.screen_context:
                context_info += f"\nRelevant Data: {self.screen_context['data']}"

        return f"""You are an expert D&D assistant. You can help with anything D&D-related:
- Answer rules questions and explain mechanics
- Help create characters through natural conversation
- Provide optimization advice and build suggestions
- Explain what the user is looking at in the application
{context_info}

AVAILABLE TOOLS:
You have access to tools for looking up D&D data and creating characters. Use them when appropriate:

CHARACTER CREATION TOOLS (use when the user wants to create a character):
- create_character: Initialize a new character session with a ruleset
- set_character_name, set_character_class, set_character_species, set_character_background
- assign_ability_scores: Set all six ability scores
- set_ability_bonuses: Apply racial/background bonuses
- add_skill_proficiency: Add skill proficiencies
- select_cantrips, select_spells: For spellcasters
- select_origin_feat: For 2024 rules
- get_character_preview: Show current character state
- finalize_character: Complete and save the character

PLANNING TOOLS:
- suggest_build: Get build recommendations for a concept
- create_advancement_plan: Plan levels 1-20

LOOKUP TOOLS (use to get accurate D&D data):
- lookup_class, lookup_species, list_species: Class and species info
- lookup_spell, get_class_spells: Spell information
- lookup_feat, search_feats: Feat information

GUIDELINES:
- Be conversational and helpful like a knowledgeable friend
- Use tools to look up data rather than guessing
- When creating characters, ask one or two questions at a time
- For optimization, prioritize the class's primary ability
- Remember: 2024 rules have backgrounds give ability bonuses, 2014 has races give them
- Always confirm before finalizing a character

You don't need to use tools for every question - for general D&D knowledge questions, just answer directly. Use tools when you need accurate game data or when helping create a character."""

    async def _send_message(self, message: str) -> None:
        """Send a message to the AI with tool support."""
        from dnd_manager.ai.base import AIMessage, MessageRole

        log = self.query_one("#overlay-log", RichLog)
        log.write(f"\n[bold green]You:[/] {message}")

        provider = await self._get_provider()
        if not provider:
            log.write("[bold red]Error:[/] No AI provider configured.")
            return

        if not provider.is_configured():
            log.write(f"[bold red]Error:[/] {provider.name} not configured.")
            return

        system_prompt = self._build_system_prompt()
        await self._send_with_tools(message, system_prompt, log)

    async def _send_with_tools(self, message: str, system_prompt: str, log: RichLog) -> None:
        """Send a message with tool calling support for character creation."""
        from dnd_manager.ai.base import AIMessage, MessageRole
        from dnd_manager.ai.tools.session import ToolSession
        from dnd_manager.ai.tools.registry import get_tool_registry

        provider = await self._get_provider()

        # Initialize tool session if needed
        if self._tool_session is None:
            registry = get_tool_registry()
            # Get only creation-related tools
            creation_tool_names = [
                "create_character", "set_character_name", "set_character_class",
                "set_character_species", "set_character_background",
                "assign_ability_scores", "set_ability_bonuses",
                "add_skill_proficiency", "select_cantrips", "select_spells",
                "select_origin_feat", "get_character_preview", "finalize_character",
                "suggest_build", "create_advancement_plan",
                # Also include lookup tools for the AI to reference data
                "lookup_class", "lookup_species", "list_species",
                "lookup_spell", "get_class_spells", "lookup_feat", "search_feats",
            ]
            tools = [registry.get_tool(name) for name in creation_tool_names if registry.get_tool(name)]
            self._tool_session = ToolSession(
                provider=provider,
                tools=tools,
                system_prompt=system_prompt,
            )

        self._messages.append(AIMessage(role=MessageRole.USER, content=message))
        log.write("[bold blue]Assistant:[/] ", end="")

        try:
            # Use tool session which handles the full AI <-> tool loop
            result = await self._tool_session.run(message)

            # Display the final response
            log.write(result.final_response)

            # Show any tool calls that were made
            if result.tool_calls:
                log.write("")
                log.write("[dim]Actions taken:[/]")
                for call in result.tool_calls:
                    if call.result and "changes" in call.result:
                        for change in call.result["changes"]:
                            log.write(f"  [green]\u2713[/] {change}")

            # Check if character was finalized
            if result.tool_calls:
                for call in result.tool_calls:
                    if call.name == "finalize_character" and call.result:
                        if call.result.get("data", {}).get("character_created"):
                            # Character was created - get it from the handler
                            if "character" in call.result:
                                created_char = call.result["character"]
                                # Save it
                                self.app.store.save(created_char)
                                log.write("")
                                log.write(f"[bold green]Character saved![/] {created_char.name}")
                                log.write("Press [bold]Escape[/] to close and load your new character.")

            self._messages.append(AIMessage(role=MessageRole.ASSISTANT, content=result.final_response))

        except Exception as e:
            log.write(f"\n[bold red]Error:[/] {e}")
            import traceback
            log.write(f"[dim]{traceback.format_exc()}[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id
        if btn_id == "btn-overlay-send":
            self._submit_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key."""
        if event.input.id == "overlay-input":
            self._submit_message()

    def _submit_message(self) -> None:
        """Submit the current message."""
        input_widget = self.query_one("#overlay-input", Input)
        message = input_widget.value.strip()
        if message:
            input_widget.value = ""
            asyncio.create_task(self._send_message(message))

    def action_close(self) -> None:
        """Close the overlay."""
        self.dismiss()

    def action_clear(self) -> None:
        """Clear chat history."""
        self._messages.clear()
        self._tool_session = None
        log = self.query_one("#overlay-log", RichLog)
        log.clear()
        self._show_intro()
        self.notify("Chat cleared")


class HomebrewScreen(Screen):
    """Screen for viewing balance guidelines and creating homebrew content."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back"),
        Binding("1", "show_spells", "Spells"),
        Binding("2", "show_items", "Magic Items"),
        Binding("3", "show_races", "Races"),
        Binding("4", "show_classes", "Classes"),
        Binding("5", "show_feats", "Feats"),
        Binding("a", "ai_homebrew", "AI Homebrew Chat"),
        Binding("l", "library", "Library"),
    ]

    def __init__(self, character: Optional[Character] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.current_type = "spell"
        self.content_types = [
            ("spell", "Spells"),
            ("magic_item", "Magic Items"),
            ("race", "Races/Species"),
            ("class", "Classes"),
            ("subclass", "Subclasses"),
            ("feat", "Feats"),
            ("background", "Backgrounds"),
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Homebrew Balance Guidelines", classes="title"),
            Static("\\[1-5] Switch Type  \\[A] AI Chat  \\[L] Library  \\[Esc] Back", classes="subtitle"),
            Horizontal(
                Vertical(
                    Static("CONTENT TYPES", classes="panel-title"),
                    VerticalScroll(id="type-list", classes="type-list"),
                    classes="panel type-panel",
                ),
                Vertical(
                    Static(id="guidelines-title", classes="panel-title"),
                    VerticalScroll(id="guidelines-content", classes="guidelines-content"),
                    classes="panel guidelines-panel wide",
                ),
                classes="homebrew-row",
            ),
            id="homebrew-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen."""
        self._refresh_type_list()
        self._load_guidelines()

    def _refresh_type_list(self) -> None:
        """Refresh the content type list."""
        type_list = self.query_one("#type-list", VerticalScroll)
        type_list.remove_children()

        for i, (type_id, type_name) in enumerate(self.content_types):
            selected = "▶ " if type_id == self.current_type else "  "
            type_list.mount(Static(
                f"{selected}[{i+1}] {type_name}",
                classes=f"type-item {'selected' if type_id == self.current_type else ''}",
            ))

    def _load_guidelines(self) -> None:
        """Load and display guidelines for the current content type."""
        try:
            from dnd_manager.data.balance import get_balance_guidelines

            guidelines = get_balance_guidelines()

            # Update title
            title = self.query_one("#guidelines-title", Static)
            type_name = dict(self.content_types).get(self.current_type, self.current_type)
            title.update(f"{type_name.upper()} BALANCE GUIDELINES")

            # Get guidelines content
            content = self.query_one("#guidelines-content", VerticalScroll)
            content.remove_children()

            # Get the specific guidelines for this content type
            prompt = guidelines.get_prompt_for_content_type(self.current_type)

            if prompt:
                # Split into lines and display
                for line in prompt.split("\n"):
                    content.mount(Static(f"  {line}", classes="guideline-line"))
            else:
                content.mount(Static("  No specific guidelines found for this content type.", classes="no-content"))
                content.mount(Static(""))
                content.mount(Static("  Use the AI Homebrew Chat \\[A] to create balanced content", classes="hint"))
                content.mount(Static("  with AI assistance.", classes="hint"))

            # Add general tips at the bottom
            content.mount(Static(""))
            content.mount(Static("  ─────────────────────────────────────────", classes="separator"))
            content.mount(Static("  TIPS FOR BALANCED HOMEBREW:", classes="section-header"))
            content.mount(Static("  • Compare to similar official content", classes="tip"))
            content.mount(Static("  • Start conservative, buff if needed", classes="tip"))
            content.mount(Static("  • Consider edge cases and combos", classes="tip"))
            content.mount(Static("  • Playtest before finalizing", classes="tip"))
            content.mount(Static(""))
            content.mount(Static("  Press \\[A] to start an AI-assisted homebrew session", classes="hint"))

        except Exception as e:
            content = self.query_one("#guidelines-content", VerticalScroll)
            content.remove_children()
            content.mount(Static(f"  Error loading guidelines: {e}", classes="error"))
            content.mount(Static(""))
            content.mount(Static("  You can still use AI Homebrew Chat \\[A] for assistance.", classes="hint"))

    def _switch_type(self, type_id: str) -> None:
        """Switch to a different content type."""
        self.current_type = type_id
        self._refresh_type_list()
        self._load_guidelines()

    def action_show_spells(self) -> None:
        """Show spell guidelines."""
        self._switch_type("spell")

    def action_show_items(self) -> None:
        """Show magic item guidelines."""
        self._switch_type("magic_item")

    def action_show_races(self) -> None:
        """Show race/species guidelines."""
        self._switch_type("race")

    def action_show_classes(self) -> None:
        """Show class guidelines."""
        self._switch_type("class")

    def action_show_feats(self) -> None:
        """Show feat guidelines."""
        self._switch_type("feat")

    def action_ai_homebrew(self) -> None:
        """Open AI chat in homebrew mode."""
        self.app.push_screen(HomebrewChatScreen(self.character, self.current_type))

    def action_library(self) -> None:
        """Open the homebrew library browser."""
        # Lazy import to avoid circular dependency
        from dnd_manager.app import LibraryBrowserScreen
        self.app.push_screen(LibraryBrowserScreen())

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


class HomebrewChatScreen(Screen):
    """Screen for AI-assisted homebrew creation."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("ctrl+l", "clear", "Clear Chat"),
    ]

    def __init__(
        self,
        character: Optional[Character] = None,
        content_type: str = "spell",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.character = character
        self.content_type = content_type
        self._messages: list = []
        self._provider = None

    def compose(self) -> ComposeResult:
        type_name = self.content_type.replace("_", " ").title()
        yield Header()
        yield Container(
            Static(f"AI Homebrew Assistant - {type_name}", classes="title"),
            Static("Create balanced homebrew content with AI guidance", classes="subtitle"),
            RichLog(id="chat-log", wrap=True, markup=True),
            Horizontal(
                Input(placeholder="Describe your homebrew idea...", id="chat-input"),
                Button("Send", id="btn-send", variant="primary"),
                classes="chat-input-row",
            ),
            id="chat-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize chat on mount."""
        self.query_one("#chat-input", Input).focus()
        log = self.query_one("#chat-log", RichLog)

        type_name = self.content_type.replace("_", " ").title()
        log.write(f"[bold cyan]AI Homebrew Assistant - {type_name}[/]")
        log.write("")
        log.write("I'll help you create balanced homebrew content. Tell me about")
        log.write("your concept and I'll guide you through the design process.")
        log.write("")
        log.write("[bold]Example prompts:[/]")

        if self.content_type == "spell":
            log.write("• 'Create a 3rd level fire spell that also slows enemies'")
            log.write("• 'I want a cantrip that creates a small light construct'")
        elif self.content_type == "magic_item":
            log.write("• 'A rare sword that deals extra damage to undead'")
            log.write("• 'A cloak that grants limited invisibility'")
        elif self.content_type == "race":
            log.write("• 'A race of living crystals with psychic abilities'")
            log.write("• 'Small fey creatures with illusion magic'")
        elif self.content_type == "class":
            log.write("• 'A half-caster focused on time manipulation'")
            log.write("• 'A martial class that uses cooking as magic'")
        elif self.content_type == "feat":
            log.write("• 'A feat for characters who fight with two shields'")
            log.write("• 'A feat that improves counterspelling'")
        else:
            log.write("• Describe your concept and desired power level")
            log.write("• I'll suggest mechanics and balance considerations")

        log.write("")

    async def _get_provider(self):
        """Get the AI provider."""
        if self._provider is None:
            from dnd_manager.ai import get_provider
            manager = get_config_manager()
            provider_name = manager.get("ai.default_provider") or "gemini"
            self._provider = get_provider(provider_name)
        return self._provider

    async def _send_message(self, message: str) -> None:
        """Send a message to the AI."""
        from dnd_manager.ai.context import build_homebrew_system_prompt
        from dnd_manager.ai.base import AIMessage, MessageRole

        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold green]You:[/] {message}")

        provider = await self._get_provider()
        if not provider:
            log.write("[bold red]Error:[/] No AI provider configured.")
            log.write("Run: ccvault config set ai.gemini.api_key YOUR_KEY")
            return

        if not provider.is_configured():
            log.write(f"[bold red]Error:[/] {provider.name} not configured.")
            log.write(f"Run: ccvault config set ai.{provider.name}.api_key YOUR_KEY")
            return

        # Build homebrew-specific system prompt
        system_prompt = build_homebrew_system_prompt(
            content_type=self.content_type,
            character=self.character,
        )
        self._messages.append(AIMessage(role=MessageRole.USER, content=message))

        all_messages = [
            AIMessage(role=MessageRole.SYSTEM, content=system_prompt),
            *self._messages,
        ]

        log.write("[bold blue]Assistant:[/] ", end="")

        try:
            response_text = ""
            async for chunk in provider.chat_stream(all_messages):
                log.write(chunk, end="")
                response_text += chunk
            log.write("")  # Newline after response

            # Save assistant response
            self._messages.append(AIMessage(role=MessageRole.ASSISTANT, content=response_text))

        except Exception as e:
            log.write(f"\n[bold red]Error:[/] {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle send button."""
        if event.button.id == "btn-send":
            self._submit_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key."""
        if event.input.id == "chat-input":
            self._submit_message()

    def _submit_message(self) -> None:
        """Submit the current message."""
        input_widget = self.query_one("#chat-input", Input)
        message = input_widget.value.strip()
        if message:
            input_widget.value = ""
            asyncio.create_task(self._send_message(message))

    def action_back(self) -> None:
        """Return to homebrew screen."""
        self.app.pop_screen()

    def action_clear(self) -> None:
        """Clear chat history."""
        self._messages.clear()
        log = self.query_one("#chat-log", RichLog)
        log.clear()
        log.write("[bold cyan]Chat cleared![/]")
        log.write("Describe your homebrew concept to get started.\n")
        self.notify("Chat cleared")
