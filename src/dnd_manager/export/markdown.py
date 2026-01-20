"""Markdown export for character sheets."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, PackageLoader, select_autoescape

from dnd_manager.models.character import Character
from dnd_manager.models.abilities import Ability, Skill


class MarkdownExporter:
    """Export characters to Markdown format using Jinja2 templates."""

    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("dnd_manager.export", "templates"),
            autoescape=select_autoescape(default=False),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Add custom filters
        self.env.filters["signed"] = self._signed_filter
        self.env.globals["ordinal_suffix"] = self._ordinal_suffix

    @staticmethod
    def _signed_filter(value: int) -> str:
        """Format a number with explicit sign."""
        if value >= 0:
            return f"+{value}"
        return str(value)

    @staticmethod
    def _ordinal_suffix(n: int) -> str:
        """Get ordinal suffix for a number (1st, 2nd, 3rd, 4th, etc.)."""
        if 11 <= n % 100 <= 13:
            return "th"
        return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")

    def export(self, character: Character, template_name: str = "character_sheet.md.j2") -> str:
        """Export a character to Markdown.

        Args:
            character: The character to export
            template_name: Name of the Jinja2 template to use

        Returns:
            Markdown string
        """
        template = self.env.get_template(template_name)

        # Get ruleset info
        ruleset = character.get_ruleset()
        species_term = character.get_species_term()
        ruleset_name = ruleset.name if ruleset else "Unknown"

        # Build abilities dict for template
        abilities = {
            "Strength": character.abilities.strength,
            "Dexterity": character.abilities.dexterity,
            "Constitution": character.abilities.constitution,
            "Intelligence": character.abilities.intelligence,
            "Wisdom": character.abilities.wisdom,
            "Charisma": character.abilities.charisma,
        }

        return template.render(
            character=character,
            abilities=abilities,
            all_abilities=list(Ability),
            all_skills=list(Skill),
            species_term=species_term,
            ruleset_name=ruleset_name,
            now=datetime.now(),
        )

    def export_to_file(
        self,
        character: Character,
        output_path: Path,
        template_name: str = "character_sheet.md.j2",
    ) -> Path:
        """Export a character to a Markdown file.

        Args:
            character: The character to export
            output_path: Path for the output file
            template_name: Name of the Jinja2 template to use

        Returns:
            Path to the created file
        """
        content = self.export(character, template_name)
        output_path.write_text(content, encoding="utf-8")
        return output_path


# Convenience function
def export_to_markdown(character: Character, output_path: Optional[Path] = None) -> str:
    """Export a character to Markdown.

    Args:
        character: The character to export
        output_path: Optional path to write the file

    Returns:
        The Markdown content as a string
    """
    exporter = MarkdownExporter()
    content = exporter.export(character)

    if output_path:
        output_path.write_text(content, encoding="utf-8")

    return content
