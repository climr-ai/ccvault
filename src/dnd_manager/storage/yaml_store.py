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


class FilenameCollisionError(StorageError):
    """Raised when a sanitized filename would collide with an existing file."""
    def __init__(self, original_name: str, sanitized_name: str, existing_path: Path):
        self.original_name = original_name
        self.sanitized_name = sanitized_name
        self.existing_path = existing_path
        super().__init__(
            f"Filename collision: '{original_name}' sanitizes to '{sanitized_name}' "
            f"which already exists at {existing_path}"
        )


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

    # Maximum filename length (most filesystems support 255, but we're conservative)
    MAX_FILENAME_LENGTH = 200

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize a string to be a valid, safe filename.

        Security measures:
        - Removes path separators to prevent directory traversal
        - Only allows alphanumeric characters, underscores, and hyphens
        - Enforces maximum length to prevent filesystem issues
        - Returns 'unnamed' for empty/invalid input

        Args:
            name: Raw name string to sanitize

        Returns:
            Safe filename string (without extension)
        """
        if not name or not isinstance(name, str):
            return "unnamed"

        # Normalize and lowercase
        safe = name.strip().lower()

        # Remove any path components (prevent directory traversal)
        # This handles /, \, and any other path separators
        safe = safe.replace("/", "_").replace("\\", "_")

        # Replace spaces with underscores
        safe = safe.replace(" ", "_")

        # Only keep alphanumeric, underscores, and hyphens
        safe = "".join(c for c in safe if c.isalnum() or c in "_-")

        # Remove leading/trailing underscores and hyphens
        safe = safe.strip("_-")

        # Collapse multiple underscores
        while "__" in safe:
            safe = safe.replace("__", "_")

        # Enforce maximum length
        if len(safe) > YAMLStore.MAX_FILENAME_LENGTH:
            safe = safe[:YAMLStore.MAX_FILENAME_LENGTH].rstrip("_-")

        return safe or "unnamed"

    def _check_collision(self, name: str, allow_overwrite: bool = False) -> None:
        """Check if saving a file would cause a collision.

        Args:
            name: Original name to save
            allow_overwrite: If True, allows overwriting a file with the exact same original name

        Raises:
            FilenameCollisionError: If the sanitized name collides with a different file
        """
        sanitized = self._sanitize_filename(name)
        path = self.directory / f"{sanitized}{self.extension}"

        if not path.exists():
            return

        # File exists - check if it's the same logical entity
        # We need to determine if we're overwriting the same character or a different one
        # Read the existing file to check
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing_data = yaml.safe_load(f)

            # If the existing file has a name field, compare it
            existing_name = existing_data.get("name") if existing_data else None

            if existing_name and existing_name.lower() != name.lower():
                # Different logical entity - this is a collision
                raise FilenameCollisionError(name, sanitized, path)
        except (yaml.YAMLError, OSError):
            # Can't read existing file - if we're not allowing overwrite, raise
            if not allow_overwrite:
                raise FilenameCollisionError(name, sanitized, path)

    def save(self, name: str, data: T, create_backup: bool = True, check_collision: bool = True) -> Path:
        """Save a model to YAML file with auto-backup.

        Args:
            name: Name of the file (without extension)
            data: Model to save
            create_backup: Whether to backup existing file before overwriting
            check_collision: Whether to check for filename collisions

        Returns:
            Path to the saved file

        Raises:
            FilenameCollisionError: If the sanitized name collides with a different file
            StorageError: If save fails
        """
        # Check for collision before proceeding
        if check_collision:
            self._check_collision(name, allow_overwrite=True)

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

        except (OSError, IOError) as e:
            # File system errors (permissions, disk full, etc.)
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Failed to save {name} (I/O error): {e}")
            raise StorageError(f"Failed to save {name}: {e}") from e
        except yaml.YAMLError as e:
            # YAML serialization/parsing errors
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Failed to save {name} (YAML error): {e}")
            raise StorageError(f"Failed to save {name}: {e}") from e
        except (TypeError, ValueError) as e:
            # Data conversion errors
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Failed to save {name} (data error): {e}")
            raise StorageError(f"Failed to save {name}: {e}") from e

        return path

    def _create_backup(self, path: Path, max_backups: Optional[int] = None) -> Optional[Path]:
        """Create a backup of a file.

        Keeps only the most recent `max_backups` backup files.
        Uses config defaults if max_backups not specified.
        """
        # Get config values (don't check exists() - just try to copy)
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

            # Clean up old backups with safer validation
            # Use stricter pattern: stem_YYYYMMDD_HHMMSS.extension
            import re
            backup_pattern = re.compile(
                rf"^{re.escape(path.stem)}_\d{{8}}_\d{{6}}{re.escape(path.suffix)}$"
            )

            valid_backups = []
            for candidate in backup_dir.iterdir():
                if not backup_pattern.match(candidate.name):
                    continue
                try:
                    mtime = candidate.stat().st_mtime
                    valid_backups.append((candidate, mtime))
                except (OSError, FileNotFoundError):
                    # File was deleted or inaccessible, skip
                    continue

            # Sort by mtime descending (newest first)
            valid_backups.sort(key=lambda x: x[1], reverse=True)

            # Remove old backups beyond the limit
            for old_backup, _ in valid_backups[max_backups:]:
                try:
                    old_backup.unlink()
                    logger.debug(f"Removed old backup: {old_backup}")
                except (OSError, FileNotFoundError):
                    # File was already deleted, ignore
                    pass

            return backup_path

        except FileNotFoundError:
            # Source file doesn't exist - not an error, just nothing to backup
            return None
        except (OSError, IOError, PermissionError) as e:
            logger.warning(f"Failed to create backup: {e}")
            return None

    def _get_latest_backup(self, name: str) -> Optional[Path]:
        """Get the most recent backup for a file."""
        import re
        _, backup_dir_name = _get_storage_config()
        backup_dir = self.directory / backup_dir_name
        if not backup_dir.exists():
            return None

        # Use stricter pattern: name_YYYYMMDD_HHMMSS.extension
        backup_pattern = re.compile(
            rf"^{re.escape(name)}_\d{{8}}_\d{{6}}{re.escape(self.extension)}$"
        )

        valid_backups = []
        for candidate in backup_dir.iterdir():
            if not backup_pattern.match(candidate.name):
                continue
            try:
                mtime = candidate.stat().st_mtime
                valid_backups.append((candidate, mtime))
            except (OSError, FileNotFoundError):
                continue

        if not valid_backups:
            return None

        # Return newest backup
        valid_backups.sort(key=lambda x: x[1], reverse=True)
        return valid_backups[0][0]

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
        """Save character creation draft (atomic write)."""
        draft_data["_draft_timestamp"] = datetime.now().isoformat()
        temp_file = self._draft_file.with_suffix(".yaml.tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                yaml.dump(draft_data, f, default_flow_style=False, allow_unicode=True)
            # Atomic rename
            temp_file.replace(self._draft_file)
            logger.debug(f"Saved draft: {self._draft_file}")
        except Exception as e:
            # Clean up temp file on failure
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
            logger.warning(f"Failed to save draft: {e}")

    def load_draft(self) -> Optional[dict]:
        """Load character creation draft if exists."""
        try:
            with open(self._draft_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            logger.debug(f"Loaded draft: {self._draft_file}")
            return data
        except FileNotFoundError:
            # No draft exists
            return None
        except (OSError, yaml.YAMLError) as e:
            logger.warning(f"Failed to load draft: {e}")
            return None

    def clear_draft(self) -> None:
        """Delete the draft file."""
        try:
            self._draft_file.unlink()
            logger.debug("Cleared draft")
        except FileNotFoundError:
            # Already deleted, that's fine
            pass
        except OSError as e:
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
