"""PDF export for character sheets using WeasyPrint."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, PackageLoader, select_autoescape

from dnd_manager.models.character import Character
from dnd_manager.models.abilities import Ability, Skill


class PDFExporter:
    """Export characters to PDF format using WeasyPrint."""

    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("dnd_manager.export", "templates"),
            autoescape=select_autoescape(default_for_string=True, default=True),
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

    def render_html(
        self,
        character: Character,
        template_name: str = "character_sheet.html.j2",
    ) -> str:
        """Render character to HTML.

        Args:
            character: The character to export
            template_name: Name of the Jinja2 template to use

        Returns:
            HTML string
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

    def export(self, character: Character, output_path: Path) -> Path:
        """Export a character to PDF.

        Args:
            character: The character to export
            output_path: Path for the output PDF file

        Returns:
            Path to the created PDF file
        """
        try:
            from weasyprint import HTML
        except ImportError:
            raise ImportError(
                "PDF export requires weasyprint. Install with:\n"
                "  uv tool install ccvault[pdf]  # or: pip install weasyprint\n\n"
                "WeasyPrint requires system dependencies:\n"
                "  macOS:   brew install pango libffi\n"
                "  Ubuntu:  sudo apt install libpango-1.0-0 libpangoft2-1.0-0\n"
                "  Windows: See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows\n\n"
                "Alternative: Use HTML export with --format html"
            )

        html_content = self.render_html(character)

        # Create PDF
        html = HTML(string=html_content)
        html.write_pdf(output_path)

        return output_path

    def export_html(self, character: Character, output_path: Path) -> Path:
        """Export a character to HTML file (for debugging or alternative use).

        Args:
            character: The character to export
            output_path: Path for the output HTML file

        Returns:
            Path to the created HTML file
        """
        html_content = self.render_html(character)
        output_path.write_text(html_content, encoding="utf-8")
        return output_path


def is_pdf_available() -> bool:
    """Check if PDF export is available (WeasyPrint installed)."""
    try:
        import weasyprint  # noqa: F401
        return True
    except ImportError:
        return False


# Convenience function
def export_to_pdf(character: Character, output_path: Path) -> Path:
    """Export a character to PDF.

    Args:
        character: The character to export
        output_path: Path for the output PDF file

    Returns:
        Path to the created PDF file
    """
    exporter = PDFExporter()
    return exporter.export(character, output_path)


def export_to_html(character: Character, output_path: Path) -> Path:
    """Export a character to HTML.

    Args:
        character: The character to export
        output_path: Path for the output HTML file

    Returns:
        Path to the created HTML file
    """
    exporter = PDFExporter()
    return exporter.export_html(character, output_path)
