"""Session notes storage with vector search capability.

This module provides:
- SQLite-based session note storage
- Vector embeddings for semantic search
- Date-based organization
- Character and campaign association
"""

import atexit
import logging
import re
import sqlite3
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

from platformdirs import user_data_dir


class EmbeddingProvider(Enum):
    """Available embedding providers."""
    NONE = "none"  # No embeddings, text search only
    OLLAMA = "ollama"
    SENTENCE_TRANSFORMERS = "sentence_transformers"


@dataclass
class SessionNote:
    """A single session note entry."""
    id: Optional[int] = None
    session_date: date = field(default_factory=date.today)
    title: str = ""
    content: str = ""
    campaign: Optional[str] = None
    character_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    embedding: Optional[list[float]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "title": self.title,
            "content": self.content,
            "campaign": self.campaign,
            "character_id": self.character_id,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "SessionNote":
        """Create from database row.

        Handles corrupted JSON fields gracefully by returning defaults.
        """
        # Safely parse JSON fields with logging
        tags: list[str] = []
        if row["tags"]:
            try:
                tags = json.loads(row["tags"])
            except json.JSONDecodeError as e:
                logger.warning(f"Corrupted tags JSON in note {row['id']}: {e}")

        embedding: Optional[list[float]] = None
        if row["embedding"]:
            try:
                embedding = json.loads(row["embedding"])
            except json.JSONDecodeError as e:
                logger.warning(f"Corrupted embedding JSON in note {row['id']}: {e}")

        # Safely parse dates with logging
        session_date_val = date.today()
        if row["session_date"]:
            try:
                session_date_val = date.fromisoformat(row["session_date"])
            except ValueError as e:
                logger.warning(f"Invalid session_date in note {row['id']}: {e}")

        created_at_val: Optional[datetime] = None
        if row["created_at"]:
            try:
                created_at_val = datetime.fromisoformat(row["created_at"])
            except ValueError:
                pass

        updated_at_val: Optional[datetime] = None
        if row["updated_at"]:
            try:
                updated_at_val = datetime.fromisoformat(row["updated_at"])
            except ValueError:
                pass

        return cls(
            id=row["id"],
            session_date=session_date_val,
            title=row["title"] or "",
            content=row["content"] or "",
            campaign=row["campaign"],
            character_id=row["character_id"],
            tags=tags,
            created_at=created_at_val,
            updated_at=updated_at_val,
            embedding=embedding,
        )


@dataclass
class SearchResult:
    """A search result with relevance score."""
    note: SessionNote
    score: float  # Higher is more relevant
    match_type: str  # "semantic", "keyword", "exact"


class EmbeddingEngine:
    """Handles text embedding generation."""

    # Default model for sentence-transformers (small, fast, ~80MB)
    DEFAULT_MODEL = "all-MiniLM-L6-v2"

    def __init__(
        self,
        provider: EmbeddingProvider = EmbeddingProvider.NONE,
        show_progress: bool = True,
    ):
        self.provider = provider
        self.show_progress = show_progress
        self._model = None
        self._ollama_client = None
        self._dimension = 384  # Default for all-MiniLM-L6-v2
        self._model_loaded = False

    def is_available(self) -> bool:
        """Check if the embedding provider is available."""
        if self.provider == EmbeddingProvider.NONE:
            return True

        if self.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
            try:
                from sentence_transformers import SentenceTransformer
                return True
            except ImportError:
                return False

        if self.provider == EmbeddingProvider.OLLAMA:
            try:
                import ollama
                return True
            except ImportError:
                return False

        return False

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self._dimension

    def embed(self, text: str) -> Optional[list[float]]:
        """Generate embedding for text."""
        if self.provider == EmbeddingProvider.NONE:
            return None

        if self.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
            return self._embed_sentence_transformers(text)

        if self.provider == EmbeddingProvider.OLLAMA:
            return self._embed_ollama(text)

        return None

    def embed_batch(self, texts: list[str]) -> list[Optional[list[float]]]:
        """Generate embeddings for multiple texts."""
        if self.provider == EmbeddingProvider.NONE:
            return [None] * len(texts)

        if self.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
            return self._embed_batch_sentence_transformers(texts)

        # Fall back to individual embedding for other providers
        return [self.embed(text) for text in texts]

    def _load_sentence_transformer_model(self) -> bool:
        """Load the sentence-transformers model with progress indication.

        Returns True if model loaded successfully, False otherwise.
        """
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer
            import sys

            # Check if model needs downloading by looking for cached path
            model_name = self.DEFAULT_MODEL
            needs_download = not self._is_model_cached(model_name)

            if needs_download and self.show_progress:
                print(
                    f"Downloading embedding model '{model_name}' (~80MB)...",
                    file=sys.stderr,
                )
                print(
                    "This is a one-time download for semantic search.",
                    file=sys.stderr,
                )

            # Load model - sentence-transformers shows its own progress bar
            self._model = SentenceTransformer(model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
            self._model_loaded = True

            if needs_download and self.show_progress:
                print(f"Model '{model_name}' ready.", file=sys.stderr)

            return True
        except Exception as e:
            if self.show_progress:
                import sys
                print(f"Failed to load embedding model: {e}", file=sys.stderr)
            return False

    def _is_model_cached(self, model_name: str) -> bool:
        """Check if a sentence-transformers model is already cached."""
        try:
            from pathlib import Path
            import os

            # Check common cache locations
            cache_dirs = [
                Path.home() / ".cache" / "torch" / "sentence_transformers",
                Path.home() / ".cache" / "huggingface" / "hub",
            ]

            # Also check HF_HOME environment variable
            hf_home = os.environ.get("HF_HOME")
            if hf_home:
                cache_dirs.append(Path(hf_home) / "hub")

            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    # Look for model directory
                    for item in cache_dir.iterdir():
                        if model_name.replace("/", "_") in item.name or model_name in item.name:
                            return True
            return False
        except (OSError, PermissionError):
            # If we can't check cache directories, assume not cached
            return False

    def _embed_sentence_transformers(self, text: str) -> Optional[list[float]]:
        """Embed using sentence-transformers."""
        try:
            if not self._load_sentence_transformer_model():
                return None

            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except (ImportError, RuntimeError, ValueError, TypeError) as e:
            # ImportError: sentence-transformers not installed
            # RuntimeError: model loading/encoding issues
            # ValueError/TypeError: invalid input
            import sys
            print(f"Embedding error: {e}", file=sys.stderr)
            return None

    def _embed_batch_sentence_transformers(self, texts: list[str]) -> list[Optional[list[float]]]:
        """Batch embed using sentence-transformers."""
        try:
            if not self._load_sentence_transformer_model():
                return [None] * len(texts)

            embeddings = self._model.encode(texts, convert_to_numpy=True)
            return [e.tolist() for e in embeddings]
        except (ImportError, RuntimeError, ValueError, TypeError) as e:
            import sys
            print(f"Batch embedding error: {e}", file=sys.stderr)
            return [None] * len(texts)

    def _embed_ollama(self, text: str) -> Optional[list[float]]:
        """Embed using Ollama."""
        try:
            import ollama

            if self._ollama_client is None:
                self._ollama_client = ollama.Client()

            response = self._ollama_client.embeddings(
                model="nomic-embed-text",  # Small, fast embedding model
                prompt=text,
            )
            embedding = response.get("embedding", [])
            if embedding:
                self._dimension = len(embedding)
            return embedding if embedding else None
        except ImportError:
            # Ollama not installed
            return None
        except (ConnectionError, TimeoutError, OSError) as e:
            # Network/connection issues with Ollama server
            import sys
            print(f"Ollama connection error: {e}", file=sys.stderr)
            return None
        except (ValueError, TypeError, KeyError) as e:
            # Response parsing issues
            import sys
            print(f"Ollama response error: {e}", file=sys.stderr)
            return None


class SessionNotesStore:
    """SQLite-based session notes storage with vector search.

    Supports context manager protocol for proper resource cleanup:
        with SessionNotesStore() as store:
            store.add(note)
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        embedding_provider: EmbeddingProvider = EmbeddingProvider.NONE,
        show_progress: bool = True,
    ):
        if db_path is None:
            data_dir = Path(user_data_dir("dnd-manager", "dnd-manager"))
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "session_notes.db"

        self.db_path = db_path
        self.embedding_engine = EmbeddingEngine(embedding_provider, show_progress)
        self._conn: Optional[sqlite3.Connection] = None
        try:
            self._init_db()
        except sqlite3.Error:
            # Ensure connection is closed if init fails
            self.close()
            raise

    def __enter__(self) -> "SessionNotesStore":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager, ensuring connection is closed."""
        self.close()

    def __del__(self) -> None:
        """Destructor to ensure connection is closed."""
        self.close()

    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection with proper cleanup on error."""
        if self._conn is None:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                # Enable FTS5 for full-text search
                conn.execute("PRAGMA journal_mode=WAL")
                self._conn = conn
            except sqlite3.Error:
                conn.close()
                raise
        return self._conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_conn()

        # Main notes table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                campaign TEXT,
                character_id TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                embedding TEXT
            )
        """)

        # Full-text search index
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
                title,
                content,
                tags,
                content='session_notes',
                content_rowid='id'
            )
        """)

        # Triggers to keep FTS in sync
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON session_notes BEGIN
                INSERT INTO notes_fts(rowid, title, content, tags)
                VALUES (new.id, new.title, new.content, new.tags);
            END
        """)

        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON session_notes BEGIN
                INSERT INTO notes_fts(notes_fts, rowid, title, content, tags)
                VALUES ('delete', old.id, old.title, old.content, old.tags);
            END
        """)

        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON session_notes BEGIN
                INSERT INTO notes_fts(notes_fts, rowid, title, content, tags)
                VALUES ('delete', old.id, old.title, old.content, old.tags);
                INSERT INTO notes_fts(rowid, title, content, tags)
                VALUES (new.id, new.title, new.content, new.tags);
            END
        """)

        # Indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_date ON session_notes(session_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_campaign ON session_notes(campaign)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_character ON session_notes(character_id)")

        conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def add(self, note: SessionNote) -> SessionNote:
        """Add a new session note."""
        conn = self._get_conn()
        now = datetime.now()

        # Generate embedding if provider available
        embedding = None
        if self.embedding_engine.is_available():
            text = f"{note.title}\n\n{note.content}"
            embedding = self.embedding_engine.embed(text)

        cursor = conn.execute(
            """
            INSERT INTO session_notes
            (session_date, title, content, campaign, character_id, tags, created_at, updated_at, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                note.session_date.isoformat(),
                note.title,
                note.content,
                note.campaign,
                note.character_id,
                json.dumps(note.tags),
                now.isoformat(),
                now.isoformat(),
                json.dumps(embedding) if embedding else None,
            ),
        )
        conn.commit()

        note.id = cursor.lastrowid
        note.created_at = now
        note.updated_at = now
        note.embedding = embedding
        return note

    def update(self, note: SessionNote) -> SessionNote:
        """Update an existing session note."""
        if note.id is None:
            raise ValueError("Cannot update note without ID")

        conn = self._get_conn()
        now = datetime.now()

        # Regenerate embedding
        embedding = None
        if self.embedding_engine.is_available():
            text = f"{note.title}\n\n{note.content}"
            embedding = self.embedding_engine.embed(text)

        conn.execute(
            """
            UPDATE session_notes SET
                session_date = ?,
                title = ?,
                content = ?,
                campaign = ?,
                character_id = ?,
                tags = ?,
                updated_at = ?,
                embedding = ?
            WHERE id = ?
            """,
            (
                note.session_date.isoformat(),
                note.title,
                note.content,
                note.campaign,
                note.character_id,
                json.dumps(note.tags),
                now.isoformat(),
                json.dumps(embedding) if embedding else None,
                note.id,
            ),
        )
        conn.commit()

        note.updated_at = now
        note.embedding = embedding
        return note

    def delete(self, note_id: int) -> bool:
        """Delete a session note."""
        conn = self._get_conn()
        cursor = conn.execute("DELETE FROM session_notes WHERE id = ?", (note_id,))
        conn.commit()
        return cursor.rowcount > 0

    def get(self, note_id: int) -> Optional[SessionNote]:
        """Get a note by ID."""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM session_notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        return SessionNote.from_row(row) if row else None

    def get_all(
        self,
        campaign: Optional[str] = None,
        character_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SessionNote]:
        """Get all notes with optional filtering."""
        # Validate limit and offset to prevent DoS
        limit = max(1, min(limit, 1000))  # Clamp to 1-1000
        offset = max(0, min(offset, 100000))  # Clamp to 0-100000

        conn = self._get_conn()

        query = "SELECT * FROM session_notes WHERE 1=1"
        params: list[Any] = []

        if campaign:
            query += " AND campaign = ?"
            params.append(campaign)

        if character_id:
            query += " AND character_id = ?"
            params.append(character_id)

        query += " ORDER BY session_date DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = conn.execute(query, params)
        return [SessionNote.from_row(row) for row in cursor.fetchall()]

    def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        campaign: Optional[str] = None,
    ) -> list[SessionNote]:
        """Get notes within a date range."""
        conn = self._get_conn()

        query = "SELECT * FROM session_notes WHERE session_date BETWEEN ? AND ?"
        params: list[Any] = [start_date.isoformat(), end_date.isoformat()]

        if campaign:
            query += " AND campaign = ?"
            params.append(campaign)

        query += " ORDER BY session_date DESC"

        cursor = conn.execute(query, params)
        return [SessionNote.from_row(row) for row in cursor.fetchall()]

    def _sanitize_fts5_query(self, query: str) -> str:
        """Sanitize user input for FTS5 MATCH to prevent injection and DoS.

        FTS5 has special syntax (AND, OR, NOT, *, quotes, etc.) that could be
        abused. This escapes the query to treat it as literal text.
        """
        if not query or not query.strip():
            return '""'  # Empty query returns nothing

        # Escape double quotes by doubling them
        escaped = query.replace('"', '""')
        # Wrap in quotes to treat as literal phrase
        return f'"{escaped}"'

    def search_text(self, query: str, limit: int = 20) -> list[SearchResult]:
        """Full-text search using FTS5."""
        # Validate limit
        limit = max(1, min(limit, 100))

        # Sanitize query to prevent FTS5 injection
        safe_query = self._sanitize_fts5_query(query)

        conn = self._get_conn()

        try:
            cursor = conn.execute(
                """
                SELECT session_notes.*, bm25(notes_fts) as score
                FROM notes_fts
                JOIN session_notes ON notes_fts.rowid = session_notes.id
                WHERE notes_fts MATCH ?
                ORDER BY score
                LIMIT ?
                """,
                (safe_query, limit),
            )

            results = []
            for row in cursor.fetchall():
                note = SessionNote.from_row(row)
                # BM25 returns negative scores where lower (more negative) is better
                # Convert to positive score where higher is better
                score = -row["score"] if row["score"] else 0.0
                results.append(SearchResult(note=note, score=score, match_type="keyword"))

            return results
        except sqlite3.OperationalError as e:
            # Log and return empty results on FTS5 errors
            logger.warning(f"FTS5 search error: {e}")
            return []

    def search_semantic(self, query: str, limit: int = 20) -> list[SearchResult]:
        """Semantic search using vector similarity."""
        if not self.embedding_engine.is_available():
            # Fall back to text search
            return self.search_text(query, limit)

        # Generate query embedding
        query_embedding = self.embedding_engine.embed(query)
        if not query_embedding:
            return self.search_text(query, limit)

        conn = self._get_conn()

        # Get all notes with embeddings
        cursor = conn.execute(
            "SELECT * FROM session_notes WHERE embedding IS NOT NULL"
        )

        results = []
        for row in cursor.fetchall():
            note = SessionNote.from_row(row)
            if note.embedding:
                # Calculate cosine similarity
                score = self._cosine_similarity(query_embedding, note.embedding)
                results.append(SearchResult(note=note, score=score, match_type="semantic"))

        # Sort by score (higher is better) and limit
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def search(
        self,
        query: str,
        use_semantic: bool = True,
        limit: int = 20,
    ) -> list[SearchResult]:
        """Search notes using both semantic and keyword search.

        Results are combined and deduplicated, with semantic matches
        preferred when available.
        """
        results: dict[int, SearchResult] = {}

        # Semantic search if available
        if use_semantic and self.embedding_engine.is_available():
            for result in self.search_semantic(query, limit):
                if result.note.id:
                    results[result.note.id] = result

        # Text search
        for result in self.search_text(query, limit):
            if result.note.id and result.note.id not in results:
                results[result.note.id] = result

        # Sort combined results
        sorted_results = sorted(results.values(), key=lambda r: r.score, reverse=True)
        return sorted_results[:limit]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def get_campaigns(self) -> list[str]:
        """Get list of all unique campaigns."""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT DISTINCT campaign FROM session_notes WHERE campaign IS NOT NULL ORDER BY campaign"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_tags(self) -> list[str]:
        """Get list of all unique tags."""
        conn = self._get_conn()
        cursor = conn.execute("SELECT id, tags FROM session_notes WHERE tags IS NOT NULL")

        all_tags: set[str] = set()
        for row in cursor.fetchall():
            if row[1]:
                try:
                    tags = json.loads(row[1])
                    all_tags.update(tags)
                except json.JSONDecodeError as e:
                    logger.warning(f"Corrupted tags JSON in note {row[0]}: {e}")

        return sorted(all_tags)

    def reindex_embeddings(self) -> int:
        """Regenerate embeddings for all notes."""
        if not self.embedding_engine.is_available():
            return 0

        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM session_notes")
        notes = [SessionNote.from_row(row) for row in cursor.fetchall()]

        # Batch embed
        texts = [f"{n.title}\n\n{n.content}" for n in notes]
        embeddings = self.embedding_engine.embed_batch(texts)

        count = 0
        for note, embedding in zip(notes, embeddings):
            if embedding and note.id:
                conn.execute(
                    "UPDATE session_notes SET embedding = ? WHERE id = ?",
                    (json.dumps(embedding), note.id),
                )
                count += 1

        conn.commit()
        return count

    def get_stats(self) -> dict:
        """Get statistics about stored notes."""
        conn = self._get_conn()

        stats = {
            "total_notes": 0,
            "notes_with_embeddings": 0,
            "campaigns": 0,
            "date_range": None,
            "embedding_provider": self.embedding_engine.provider.value,
        }

        cursor = conn.execute("SELECT COUNT(*) FROM session_notes")
        stats["total_notes"] = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM session_notes WHERE embedding IS NOT NULL")
        stats["notes_with_embeddings"] = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(DISTINCT campaign) FROM session_notes WHERE campaign IS NOT NULL")
        stats["campaigns"] = cursor.fetchone()[0]

        cursor = conn.execute("SELECT MIN(session_date), MAX(session_date) FROM session_notes")
        row = cursor.fetchone()
        if row[0] and row[1]:
            stats["date_range"] = {"start": row[0], "end": row[1]}

        return stats


# Global instance with thread-safe initialization
_notes_store: Optional[SessionNotesStore] = None
_notes_store_lock = threading.Lock()


def _cleanup_notes_store() -> None:
    """Cleanup function called at exit to close database connection (thread-safe)."""
    global _notes_store
    with _notes_store_lock:
        if _notes_store is not None:
            _notes_store.close()
            _notes_store = None


# Register cleanup handler
atexit.register(_cleanup_notes_store)


def get_notes_store(
    embedding_provider: Optional[EmbeddingProvider] = None,
    show_progress: bool = True,
) -> SessionNotesStore:
    """Get the global session notes store (thread-safe).

    Args:
        embedding_provider: Which provider to use for embeddings. If None,
            will auto-detect available providers.
        show_progress: If True, show progress messages during model downloads.
    """
    global _notes_store

    # Use lock for all access to ensure thread safety with cleanup
    with _notes_store_lock:
        if _notes_store is not None:
            return _notes_store

        # Try to detect available embedding provider
        if embedding_provider is None:
            # Check for sentence-transformers first (preferred)
            try:
                from sentence_transformers import SentenceTransformer
                embedding_provider = EmbeddingProvider.SENTENCE_TRANSFORMERS
            except ImportError:
                # Check for Ollama
                try:
                    import ollama
                    embedding_provider = EmbeddingProvider.OLLAMA
                except ImportError:
                    embedding_provider = EmbeddingProvider.NONE

        _notes_store = SessionNotesStore(
            embedding_provider=embedding_provider,
            show_progress=show_progress,
        )

        return _notes_store
