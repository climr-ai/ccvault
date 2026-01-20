"""Storage layer for character persistence."""

from dnd_manager.storage.yaml_store import (
    YAMLStore,
    CharacterStore,
    LoadResult,
    StorageError,
    CorruptedFileError,
)
from dnd_manager.storage.sync import (
    SyncStatus,
    SyncResult,
    SyncMetadata,
    SyncProvider,
    SyncManager,
    get_sync_manager,
)
from dnd_manager.storage.migrations import (
    MigrationResult,
    CharacterMigrator,
    migrate_character_file,
    batch_migrate,
)
from dnd_manager.storage.notes import (
    SessionNote,
    SearchResult,
    EmbeddingProvider,
    EmbeddingEngine,
    SessionNotesStore,
    get_notes_store,
)

__all__ = [
    "YAMLStore",
    "CharacterStore",
    "LoadResult",
    "StorageError",
    "CorruptedFileError",
    # Sync
    "SyncStatus",
    "SyncResult",
    "SyncMetadata",
    "SyncProvider",
    "SyncManager",
    "get_sync_manager",
    # Migrations
    "MigrationResult",
    "CharacterMigrator",
    "migrate_character_file",
    "batch_migrate",
    # Session Notes
    "SessionNote",
    "SearchResult",
    "EmbeddingProvider",
    "EmbeddingEngine",
    "SessionNotesStore",
    "get_notes_store",
]
