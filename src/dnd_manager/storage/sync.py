"""Backend sync interface for future cloud synchronization.

This module provides a stub interface for syncing characters with a backend service.
The actual implementation will be added when the backend is available.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
import uuid

from dnd_manager.models.character import Character


class SyncStatus(Enum):
    """Status of a sync operation."""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    status: SyncStatus
    message: str
    local_modified: Optional[datetime] = None
    remote_modified: Optional[datetime] = None
    conflict_resolution: Optional[str] = None


@dataclass
class SyncMetadata:
    """Metadata for synced characters."""
    sync_id: Optional[str] = None
    last_synced: Optional[datetime] = None
    remote_version: int = 0
    local_version: int = 0
    status: SyncStatus = SyncStatus.PENDING

    def needs_sync(self) -> bool:
        """Check if the character needs to be synced."""
        return self.local_version > self.remote_version

    def is_synced(self) -> bool:
        """Check if the character is fully synced."""
        return self.status == SyncStatus.SYNCED and self.local_version == self.remote_version


class SyncProvider(ABC):
    """Abstract base class for sync providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the provider name."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is configured."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available (online)."""
        pass

    @abstractmethod
    async def authenticate(self, credentials: dict) -> bool:
        """Authenticate with the backend."""
        pass

    @abstractmethod
    async def push_character(self, character: Character) -> SyncResult:
        """Push a character to the backend."""
        pass

    @abstractmethod
    async def pull_character(self, sync_id: str) -> tuple[Optional[Character], SyncResult]:
        """Pull a character from the backend."""
        pass

    @abstractmethod
    async def list_remote_characters(self) -> list[dict]:
        """List all characters on the backend."""
        pass

    @abstractmethod
    async def delete_remote_character(self, sync_id: str) -> SyncResult:
        """Delete a character from the backend."""
        pass

    @abstractmethod
    async def resolve_conflict(
        self,
        local: Character,
        remote: Character,
        resolution: str
    ) -> SyncResult:
        """Resolve a sync conflict."""
        pass


class OfflineSyncProvider(SyncProvider):
    """Offline sync provider (stub implementation).

    This provider always operates in offline mode and stores sync metadata
    locally for future synchronization when a backend becomes available.
    """

    @property
    def name(self) -> str:
        return "offline"

    def is_configured(self) -> bool:
        return True  # Always "configured" in offline mode

    def is_available(self) -> bool:
        return False  # Never available (offline)

    async def authenticate(self, credentials: dict) -> bool:
        return False  # Cannot authenticate offline

    async def push_character(self, character: Character) -> SyncResult:
        """Store sync intent locally."""
        # Generate a local sync ID if not present
        if not character.meta.sync_id:
            character.meta.sync_id = str(uuid.uuid4())

        return SyncResult(
            success=True,
            status=SyncStatus.OFFLINE,
            message="Character saved locally. Will sync when online.",
        )

    async def pull_character(self, sync_id: str) -> tuple[Optional[Character], SyncResult]:
        """Cannot pull in offline mode."""
        return None, SyncResult(
            success=False,
            status=SyncStatus.OFFLINE,
            message="Cannot pull characters while offline.",
        )

    async def list_remote_characters(self) -> list[dict]:
        """No remote characters in offline mode."""
        return []

    async def delete_remote_character(self, sync_id: str) -> SyncResult:
        """Cannot delete remotely in offline mode."""
        return SyncResult(
            success=False,
            status=SyncStatus.OFFLINE,
            message="Cannot delete remote characters while offline.",
        )

    async def resolve_conflict(
        self,
        local: Character,
        remote: Character,
        resolution: str
    ) -> SyncResult:
        """Cannot resolve conflicts in offline mode."""
        return SyncResult(
            success=False,
            status=SyncStatus.OFFLINE,
            message="Cannot resolve conflicts while offline.",
        )


class SyncManager:
    """Manages character synchronization with backends.

    This is a stub implementation that prepares for future backend sync.
    Currently operates in offline-only mode.
    """

    def __init__(self):
        self._provider: SyncProvider = OfflineSyncProvider()
        self._sync_queue: list[str] = []  # Character paths to sync

    @property
    def provider(self) -> SyncProvider:
        """Get the current sync provider."""
        return self._provider

    def set_provider(self, provider: SyncProvider) -> None:
        """Set the sync provider."""
        self._provider = provider

    def is_online(self) -> bool:
        """Check if sync is available."""
        return self._provider.is_available()

    async def sync_character(self, character: Character) -> SyncResult:
        """Sync a single character."""
        if not self._provider.is_available():
            return await self._provider.push_character(character)

        # When online, actually sync
        return await self._provider.push_character(character)

    async def sync_all(self, characters: list[Character]) -> list[SyncResult]:
        """Sync all characters."""
        results = []
        for char in characters:
            result = await self.sync_character(char)
            results.append(result)
        return results

    def get_sync_status(self, character: Character) -> SyncStatus:
        """Get the sync status of a character."""
        if not character.meta.sync_id:
            return SyncStatus.PENDING

        if not self._provider.is_available():
            return SyncStatus.OFFLINE

        # TODO: Check against remote version
        return SyncStatus.SYNCED

    def queue_for_sync(self, character_path: Path) -> None:
        """Queue a character for background sync."""
        path_str = str(character_path)
        if path_str not in self._sync_queue:
            self._sync_queue.append(path_str)

    def get_sync_queue(self) -> list[str]:
        """Get the current sync queue."""
        return self._sync_queue.copy()

    def clear_sync_queue(self) -> None:
        """Clear the sync queue."""
        self._sync_queue.clear()


# Global sync manager instance
_sync_manager: Optional[SyncManager] = None


def get_sync_manager() -> SyncManager:
    """Get the global sync manager instance."""
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = SyncManager()
    return _sync_manager
