"""Character data migration tools.

This module provides tools for migrating character data between:
- Different rulesets (2014 -> 2024, 2024 -> ToV, etc.)
- Different schema versions (when the character format changes)
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
import shutil

from dnd_manager.models.character import Character, RulesetId


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    success: bool
    message: str
    warnings: list[str]
    changes_made: list[str]
    backup_path: Optional[Path] = None


class CharacterMigrator:
    """Handles character data migrations."""

    # Schema version for character files
    CURRENT_SCHEMA_VERSION = "1.0"

    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir

    def migrate_ruleset(
        self,
        character: Character,
        target_ruleset: RulesetId,
    ) -> MigrationResult:
        """Migrate a character from one ruleset to another.

        Args:
            character: The character to migrate
            target_ruleset: The target ruleset

        Returns:
            MigrationResult with details of the migration
        """
        source_ruleset = character.meta.ruleset
        warnings = []
        changes = []

        if source_ruleset == target_ruleset:
            return MigrationResult(
                success=True,
                message="Character is already using this ruleset",
                warnings=[],
                changes_made=[],
            )

        # Handle specific migration paths
        if source_ruleset == RulesetId.DND_2014 and target_ruleset == RulesetId.DND_2024:
            warnings, changes = self._migrate_2014_to_2024(character)
        elif source_ruleset == RulesetId.DND_2024 and target_ruleset == RulesetId.DND_2014:
            warnings, changes = self._migrate_2024_to_2014(character)
        elif target_ruleset == RulesetId.TOV:
            warnings, changes = self._migrate_to_tov(character, source_ruleset)
        else:
            # Generic migration
            warnings.append(f"No specific migration path from {source_ruleset.value} to {target_ruleset.value}")

        # Update the ruleset
        character.meta.ruleset = target_ruleset
        changes.append(f"Changed ruleset from {source_ruleset.value} to {target_ruleset.value}")

        # Sync spell slots for the new ruleset
        character.sync_spell_slots()
        changes.append("Recalculated spell slots for new ruleset")

        return MigrationResult(
            success=True,
            message=f"Migrated character to {target_ruleset.value}",
            warnings=warnings,
            changes_made=changes,
        )

    def _migrate_2014_to_2024(self, character: Character) -> tuple[list[str], list[str]]:
        """Migrate from D&D 2014 to 2024 rules."""
        warnings = []
        changes = []

        # In 2024, subclasses are always at level 3
        if character.primary_class.level >= 3 and not character.primary_class.subclass:
            warnings.append(f"In 2024 rules, {character.primary_class.name} gains subclass at level 3")

        # In 2024, species no longer provide ability bonuses (they come from background)
        warnings.append("In 2024 rules, ability score bonuses come from background, not species")

        # Check for origin feat
        warnings.append("In 2024 rules, backgrounds provide an Origin Feat at level 1")

        return warnings, changes

    def _migrate_2024_to_2014(self, character: Character) -> tuple[list[str], list[str]]:
        """Migrate from D&D 2024 to 2014 rules."""
        warnings = []
        changes = []

        # Some classes get subclasses earlier in 2014
        early_subclass_classes = ["Cleric", "Sorcerer", "Warlock"]
        if character.primary_class.name in early_subclass_classes:
            warnings.append(f"In 2014 rules, {character.primary_class.name} gains subclass at level 1")

        # In 2014, races provide ability bonuses
        warnings.append("In 2014 rules, ability score bonuses typically come from race")

        return warnings, changes

    def _migrate_to_tov(self, character: Character, source: RulesetId) -> tuple[list[str], list[str]]:
        """Migrate to Tales of the Valiant."""
        warnings = []
        changes = []

        # ToV uses Lineage + Heritage instead of Race/Species
        warnings.append("Tales of the Valiant uses Lineage (what you are) + Heritage (how you were raised)")
        warnings.append("Consider selecting appropriate Lineage and Heritage for your character")

        # ToV uses Talents instead of Feats
        warnings.append("Tales of the Valiant uses Talents instead of Feats (they're compatible)")

        # ToV uses Luck instead of Inspiration
        warnings.append("Tales of the Valiant uses Luck instead of Inspiration")

        return warnings, changes

    def backup_character(self, character_path: Path) -> Optional[Path]:
        """Create a backup of a character file before migration."""
        if not character_path.exists():
            return None

        # Determine backup directory
        if self.backup_dir:
            backup_dir = self.backup_dir
        else:
            backup_dir = character_path.parent / "backups"

        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{character_path.stem}_backup_{timestamp}{character_path.suffix}"
        backup_path = backup_dir / backup_name

        shutil.copy2(character_path, backup_path)
        return backup_path

    def check_schema_version(self, character_data: dict) -> tuple[str, bool]:
        """Check the schema version of character data.

        Returns:
            Tuple of (current_version, needs_migration)
        """
        meta = character_data.get("meta", {})
        version = meta.get("version", "1.0")

        needs_migration = version != self.CURRENT_SCHEMA_VERSION
        return version, needs_migration

    def migrate_schema(self, character_data: dict) -> tuple[dict, list[str]]:
        """Migrate character data to the current schema version.

        Args:
            character_data: Raw character data dictionary

        Returns:
            Tuple of (migrated_data, changes_list)
        """
        version, needs_migration = self.check_schema_version(character_data)
        changes = []

        if not needs_migration:
            return character_data, changes

        # Apply migrations in order
        if version == "0.9":
            character_data, v_changes = self._migrate_0_9_to_1_0(character_data)
            changes.extend(v_changes)

        # Update version
        if "meta" not in character_data:
            character_data["meta"] = {}
        character_data["meta"]["version"] = self.CURRENT_SCHEMA_VERSION
        changes.append(f"Updated schema version to {self.CURRENT_SCHEMA_VERSION}")

        return character_data, changes

    def _migrate_0_9_to_1_0(self, data: dict) -> tuple[dict, list[str]]:
        """Migrate from schema 0.9 to 1.0."""
        changes = []

        # Example migration: rename 'race' to 'species'
        if "race" in data.get("character", {}):
            data["character"]["species"] = data["character"].pop("race")
            changes.append("Renamed 'race' field to 'species'")

        return data, changes


def migrate_character_file(
    file_path: Path,
    target_ruleset: Optional[RulesetId] = None,
    create_backup: bool = True,
) -> MigrationResult:
    """Migrate a character file.

    Args:
        file_path: Path to the character YAML file
        target_ruleset: Optional new ruleset to migrate to
        create_backup: Whether to create a backup before migration

    Returns:
        MigrationResult with details of the migration
    """
    from dnd_manager.storage import CharacterStore

    migrator = CharacterMigrator()
    all_warnings = []
    all_changes = []
    backup_path = None

    # Create backup if requested
    if create_backup:
        backup_path = migrator.backup_character(file_path)
        if backup_path:
            all_changes.append(f"Created backup at {backup_path}")

    # Load the character
    store = CharacterStore(file_path.parent)
    character = store.load_path(file_path)

    if not character:
        return MigrationResult(
            success=False,
            message=f"Failed to load character from {file_path}",
            warnings=[],
            changes_made=[],
        )

    # Migrate ruleset if requested
    if target_ruleset and target_ruleset != character.meta.ruleset:
        result = migrator.migrate_ruleset(character, target_ruleset)
        all_warnings.extend(result.warnings)
        all_changes.extend(result.changes_made)

    # Save the migrated character
    store.save(character)
    all_changes.append(f"Saved migrated character to {file_path}")

    return MigrationResult(
        success=True,
        message="Migration completed successfully",
        warnings=all_warnings,
        changes_made=all_changes,
        backup_path=backup_path,
    )


def batch_migrate(
    directory: Path,
    target_ruleset: RulesetId,
    create_backups: bool = True,
) -> list[tuple[Path, MigrationResult]]:
    """Migrate all characters in a directory.

    Args:
        directory: Directory containing character files
        target_ruleset: Ruleset to migrate to
        create_backups: Whether to create backups

    Returns:
        List of (file_path, MigrationResult) tuples
    """
    results = []

    for yaml_file in directory.glob("*.yaml"):
        result = migrate_character_file(yaml_file, target_ruleset, create_backups)
        results.append((yaml_file, result))

    return results
