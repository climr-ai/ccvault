"""YAML-based storage for characters and custom content."""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, TypeVar, Generic
from datetime import datetime
from dataclasses import dataclass

import yaml
from pydantic import BaseModel, ValidationError
from platformdirs import user_data_dir

from dnd_manager.config import get_config_manager
from dnd_manager.models.character import Character


def _get_storage_config():
    """Get storage configuration values."""
    config = get_config_manager().config.storage
    return config.max_backups, config.backup_dir_name


T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


@dataclass
class LoadResult:
    """Result of a load operation with error details."""
    success: bool
    data: Optional[any] = None
    error: Optional[str] = None
    recovered_from_backup: bool = False
    backup_used: Optional[Path] = None


class StorageError(Exception):
    """Base exception for storage errors."""
    pass


class CorruptedFileError(StorageError):
    """Raised when a file is corrupted and cannot be loaded."""
    def __init__(self, path: Path, message: str, original_error: Optional[Exception] = None):
        self.path = path
        self.original_error = original_error
        super().__init__(f"Corrupted file {path}: {message}")


class YAMLStore(Generic[T]):
    """Generic YAML file store for Pydantic models."""

    def __init__(self, directory: Path, model_class: type[T], extension: str = ".yaml"):
        self.directory = directory
        self.model_class = model_class
        self.extension = extension
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure the storage directory exists."""
        self.directory.mkdir(parents=True, exist_ok=True)

    def _get_path(self, name: str) -> Path:
        """Get full path for a file by name."""
        safe_name = self._sanitize_filename(name)
        return self.directory / f"{safe_name}{self.extension}"

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize a string to be a valid filename."""
        # Replace spaces with underscores, remove unsafe characters
        safe = name.lower().replace(" ", "_")
        safe = "".join(c for c in safe if c.isalnum() or c in "_-")
        return safe or "unnamed"

    def save(self, name: str, data: T, create_backup: bool = True) -> Path:
        """Save a model to YAML file with auto-backup.

        Args:
            name: Name of the file (without extension)
            data: Model to save
            create_backup: Whether to backup existing file before overwriting

        Returns:
            Path to the saved file

        Raises:
            StorageError: If save fails
        """
        path = self._get_path(name)

        # Create backup of existing file
        if create_backup and path.exists():
            self._create_backup(path)

        # Convert to dict, handling datetime serialization
        data_dict = data.model_dump(mode="json")

        # Write to temporary file first, then rename (atomic save)
        temp_path = path.with_suffix(".yaml.tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    data_dict,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=100,
                )

            # Verify the written file is valid
            with open(temp_path, "r", encoding="utf-8") as f:
                yaml.safe_load(f)

            # Atomic rename
            temp_path.replace(path)
            logger.debug(f"Saved {name} to {path}")

        except Exception as e:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Failed to save {name}: {e}")
            raise StorageError(f"Failed to save {name}: {e}") from e

        return path

    def _create_backup(self, path: Path, max_backups: Optional[int] = None) -> Optional[Path]:
        """Create a backup of a file.

        Keeps only the most recent `max_backups` backup files.
        Uses config defaults if max_backups not specified.
        """
        if not path.exists():
            return None

        # Get config values
        config_max_backups, backup_dir_name = _get_storage_config()
        if max_backups is None:
            max_backups = config_max_backups

        backup_dir = self.directory / backup_dir_name
        backup_dir.mkdir(exist_ok=True)

        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path.stem}_{timestamp}{path.suffix}"
        backup_path = backup_dir / backup_name

        try:
            shutil.copy2(path, backup_path)
            logger.debug(f"Created backup: {backup_path}")

            # Clean up old backups
            backups = sorted(
                backup_dir.glob(f"{path.stem}_*{path.suffix}"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            for old_backup in backups[max_backups:]:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup}")

            return backup_path

        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
            return None

    def _get_latest_backup(self, name: str) -> Optional[Path]:
        """Get the most recent backup for a file."""
        _, backup_dir_name = _get_storage_config()
        backup_dir = self.directory / backup_dir_name
        if not backup_dir.exists():
            return None

        backups = sorted(
            backup_dir.glob(f"{name}_*{self.extension}"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return backups[0] if backups else None

    def load(self, name: str, try_recovery: bool = True) -> Optional[T]:
        """Load a model from YAML file.

        Args:
            name: Name of the file (without extension)
            try_recovery: Whether to try loading from backup if main file fails

        Returns:
            Loaded model or None if not found
        """
        path = self._get_path(name)
        return self.load_path(path, try_recovery=try_recovery)

    def load_path(self, path: Path, try_recovery: bool = True) -> Optional[T]:
        """Load a model from a specific path.

        Args:
            path: Path to the file
            try_recovery: Whether to try loading from backup if main file fails

        Returns:
            Loaded model or None if not found
        """
        if not path.exists():
            return None

        result = self._try_load(path)

        if result.success:
            return result.data

        # Try recovery from backup
        if try_recovery:
            logger.warning(f"Failed to load {path}: {result.error}")
            backup = self._get_latest_backup(path.stem)

            if backup:
                logger.info(f"Attempting recovery from backup: {backup}")
                backup_result = self._try_load(backup)

                if backup_result.success:
                    logger.info(f"Successfully recovered from backup")
                    # Restore the backup as the main file
                    shutil.copy2(backup, path)
                    return backup_result.data

        logger.error(f"Could not load or recover {path}")
        return None

    def _try_load(self, path: Path) -> LoadResult:
        """Attempt to load a file, returning detailed result."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None:
                return LoadResult(success=False, error="File is empty")

            model = self.model_class.model_validate(data)
            return LoadResult(success=True, data=model)

        except yaml.YAMLError as e:
            return LoadResult(success=False, error=f"YAML parse error: {e}")

        except ValidationError as e:
            return LoadResult(success=False, error=f"Validation error: {e}")

        except Exception as e:
            return LoadResult(success=False, error=f"Unexpected error: {e}")

    def load_with_details(self, name: str) -> LoadResult:
        """Load a model with detailed result information.

        This provides more information about the load operation than the
        simple load() method.
        """
        path = self._get_path(name)

        if not path.exists():
            return LoadResult(success=False, error="File not found")

        result = self._try_load(path)

        if result.success:
            return result

        # Try recovery
        backup = self._get_latest_backup(name)
        if backup:
            backup_result = self._try_load(backup)
            if backup_result.success:
                # Restore backup
                shutil.copy2(backup, path)
                return LoadResult(
                    success=True,
                    data=backup_result.data,
                    recovered_from_backup=True,
                    backup_used=backup,
                )

        return result

    def delete(self, name: str) -> bool:
        """Delete a file. Returns True if deleted, False if not found."""
        path = self._get_path(name)
        if path.exists():
            path.unlink()
            return True
        return False

    def exists(self, name: str) -> bool:
        """Check if a file exists."""
        return self._get_path(name).exists()

    def list_all(self) -> list[str]:
        """List all stored item names (without extension)."""
        if not self.directory.exists():
            return []

        return [
            p.stem
            for p in self.directory.glob(f"*{self.extension}")
            if p.is_file()
        ]

    def list_paths(self) -> list[Path]:
        """List all stored file paths."""
        if not self.directory.exists():
            return []

        return [
            p for p in self.directory.glob(f"*{self.extension}")
            if p.is_file()
        ]


class CharacterStore:
    """Specialized store for D&D characters."""

    def __init__(self, directory: Optional[Path] = None):
        if directory is None:
            # Default to user data directory
            app_dir = Path(user_data_dir("dnd-manager", "dnd"))
            directory = app_dir / "characters"

        self._store = YAMLStore(directory, Character)

    @property
    def directory(self) -> Path:
        """Get the character storage directory."""
        return self._store.directory

    def save(self, character: Character, create_backup: bool = True) -> Path:
        """Save a character, updating modified timestamp.

        Args:
            character: Character to save
            create_backup: Whether to backup existing file before overwriting

        Returns:
            Path to the saved file
        """
        character.update_modified()
        return self._store.save(character.name, character, create_backup=create_backup)

    def load(self, name: str, try_recovery: bool = True) -> Optional[Character]:
        """Load a character by name.

        Args:
            name: Character name
            try_recovery: Whether to try loading from backup if main file fails

        Returns:
            Character or None if not found
        """
        return self._store.load(name, try_recovery=try_recovery)

    def load_path(self, path: Path, try_recovery: bool = True) -> Optional[Character]:
        """Load a character from a specific path.

        Args:
            path: Path to the character file
            try_recovery: Whether to try loading from backup if main file fails

        Returns:
            Character or None if not found
        """
        return self._store.load_path(path, try_recovery=try_recovery)

    def load_with_details(self, name: str) -> LoadResult:
        """Load a character with detailed result information.

        This provides more information about the load operation,
        including whether recovery from backup was needed.
        """
        return self._store.load_with_details(name)

    def list_backups(self, name: str) -> list[Path]:
        """List all backups for a character."""
        _, backup_dir_name = _get_storage_config()
        backup_dir = self._store.directory / backup_dir_name
        if not backup_dir.exists():
            return []

        safe_name = self._store._sanitize_filename(name)
        return sorted(
            backup_dir.glob(f"{safe_name}_*.yaml"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

    def restore_from_backup(self, name: str, backup_path: Path) -> bool:
        """Restore a character from a specific backup.

        Args:
            name: Character name
            backup_path: Path to the backup file

        Returns:
            True if restored successfully
        """
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_path}")
            return False

        target_path = self._store._get_path(name)

        try:
            # Create backup of current file first
            if target_path.exists():
                self._store._create_backup(target_path)

            shutil.copy2(backup_path, target_path)
            logger.info(f"Restored {name} from {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False

    def delete(self, name: str) -> bool:
        """Delete a character."""
        return self._store.delete(name)

    def exists(self, name: str) -> bool:
        """Check if a character exists."""
        return self._store.exists(name)

    def list_characters(self) -> list[str]:
        """List all character names."""
        return self._store.list_all()

    def list_character_files(self) -> list[Path]:
        """List all character file paths."""
        return self._store.list_paths()

    def get_character_info(self) -> list[dict]:
        """Get summary info for all characters."""
        info = []
        for path in self.list_character_files():
            char = self.load_path(path)
            if char:
                info.append({
                    "name": char.name,
                    "path": path,
                    "level": char.total_level,
                    "class": char.primary_class.name,
                    "subclass": char.primary_class.subclass,
                    "species": char.species,
                    "ruleset": char.meta.ruleset.value,
                    "modified": char.meta.modified,
                })

        # Sort by modified date, most recent first
        info.sort(key=lambda x: x["modified"], reverse=True)
        return info

    def create_new(
        self,
        name: str = "New Character",
        class_name: str = "Fighter",
        ruleset_id: Optional["RulesetId"] = None,
        player: Optional[str] = None,
    ) -> Character:
        """Create a new character with ruleset-appropriate defaults."""
        from dnd_manager.models.character import RulesetId

        if ruleset_id is None:
            ruleset_id = RulesetId.DND_2024

        return Character.create_new(
            name=name,
            ruleset_id=ruleset_id,
            class_name=class_name,
            player=player,
        )


def get_default_character_store() -> CharacterStore:
    """Get the default character store using standard paths."""
    return CharacterStore()


def get_project_character_store(project_dir: Path) -> CharacterStore:
    """Get a character store for a specific project directory."""
    return CharacterStore(project_dir / "characters")


class DraftStore:
    """Simple store for character creation drafts."""

    def __init__(self, directory: Optional[Path] = None):
        if directory is None:
            app_dir = Path(user_data_dir("dnd-manager", "dnd"))
            directory = app_dir / ".drafts"

        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self._draft_file = self.directory / "character_creation.yaml"

    def save_draft(self, draft_data: dict) -> None:
        """Save character creation draft."""
        draft_data["_draft_timestamp"] = datetime.now().isoformat()
        try:
            with open(self._draft_file, "w", encoding="utf-8") as f:
                yaml.dump(draft_data, f, default_flow_style=False, allow_unicode=True)
            logger.debug(f"Saved draft: {self._draft_file}")
        except Exception as e:
            logger.warning(f"Failed to save draft: {e}")

    def load_draft(self) -> Optional[dict]:
        """Load character creation draft if exists."""
        if not self._draft_file.exists():
            return None
        try:
            with open(self._draft_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            logger.debug(f"Loaded draft: {self._draft_file}")
            return data
        except Exception as e:
            logger.warning(f"Failed to load draft: {e}")
            return None

    def clear_draft(self) -> None:
        """Delete the draft file."""
        if self._draft_file.exists():
            try:
                self._draft_file.unlink()
                logger.debug("Cleared draft")
            except Exception as e:
                logger.warning(f"Failed to clear draft: {e}")

    def has_draft(self) -> bool:
        """Check if a draft exists."""
        return self._draft_file.exists()

    def get_draft_info(self) -> Optional[dict]:
        """Get summary info about the draft without loading full data."""
        draft = self.load_draft()
        if not draft:
            return None
        return {
            "name": draft.get("name", "Unknown"),
            "class": draft.get("class", "Unknown"),
            "species": draft.get("species", "Unknown"),
            "step": draft.get("_step", 0),
            "timestamp": draft.get("_draft_timestamp"),
        }


def get_default_draft_store() -> DraftStore:
    """Get the default draft store."""
    return DraftStore()
