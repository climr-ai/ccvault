"""CLIMR Homebrew Library - Community homebrew content sharing.

This module provides LOCAL homebrew library functionality:
- Local homebrew library storage with SQLite
- Rating and voting system
- Content publishing and discovery (local only)

NOTE: Cloud sync with CLIMR servers is PLANNED but not yet implemented.
All content is stored and shared locally only at this time.
"""

import logging
import sqlite3
import json
import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
from enum import Enum

from platformdirs import user_data_dir

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of homebrew content."""
    SPELL = "spell"
    MAGIC_ITEM = "magic_item"
    RACE = "race"
    CLASS = "class"
    SUBCLASS = "subclass"
    FEAT = "feat"
    BACKGROUND = "background"
    MONSTER = "monster"
    ITEM = "item"
    OTHER = "other"  # Fallback for unknown types


class ContentStatus(Enum):
    """Status of library content."""
    DRAFT = "draft"  # Not yet published
    PUBLISHED = "published"  # Available in library
    ARCHIVED = "archived"  # Hidden from search
    FEATURED = "featured"  # Promoted content
    LOCAL = "local"  # Local-only content not synced


@dataclass
class LibraryAuthor:
    """Author information for library content."""
    id: str
    name: str
    email: Optional[str] = None
    profile_url: Optional[str] = None
    verified: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "profile_url": self.profile_url,
            "verified": self.verified,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryAuthor":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", "Anonymous"),
            email=data.get("email"),
            profile_url=data.get("profile_url"),
            verified=data.get("verified", False),
        )


@dataclass
class ContentRating:
    """Rating information for content."""
    average: float = 0.0
    count: int = 0
    user_rating: Optional[int] = None  # Current user's rating (1-5)

    def to_dict(self) -> dict:
        return {
            "average": self.average,
            "count": self.count,
            "user_rating": self.user_rating,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContentRating":
        return cls(
            average=data.get("average", 0.0),
            count=data.get("count", 0),
            user_rating=data.get("user_rating"),
        )


@dataclass
class LibraryContent:
    """A piece of homebrew content in the library."""
    id: str = ""
    content_type: ContentType = ContentType.SPELL
    name: str = ""
    description: str = ""
    content_data: dict = field(default_factory=dict)  # The actual homebrew content
    tags: list[str] = field(default_factory=list)
    ruleset: str = "dnd2024"  # dnd2014, dnd2024, tov, universal
    author: LibraryAuthor = field(default_factory=lambda: LibraryAuthor(id="", name="Anonymous"))
    status: ContentStatus = ContentStatus.DRAFT
    rating: ContentRating = field(default_factory=ContentRating)
    downloads: int = 0
    version: str = "1.0.0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    synced_at: Optional[datetime] = None  # Last sync with CLIMR servers
    local_only: bool = True  # Not yet synced to cloud
    checksum: str = ""  # For content integrity

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.checksum:
            self._update_checksum()

    def _update_checksum(self) -> None:
        """Update content checksum for integrity verification."""
        content_str = json.dumps(self.content_data, sort_keys=True)
        self.checksum = hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content_type": self.content_type.value,
            "name": self.name,
            "description": self.description,
            "content_data": self.content_data,
            "tags": self.tags,
            "ruleset": self.ruleset,
            "author": self.author.to_dict(),
            "status": self.status.value,
            "rating": self.rating.to_dict(),
            "downloads": self.downloads,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "local_only": self.local_only,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryContent":
        """Create from dictionary with safe parsing of enums and dates."""
        # Safely parse enums
        try:
            content_type = ContentType(data.get("content_type", "spell"))
        except ValueError:
            logger.warning(f"Invalid content_type: {data.get('content_type')}, using OTHER")
            content_type = ContentType.OTHER

        try:
            status = ContentStatus(data.get("status", "draft"))
        except ValueError:
            logger.warning(f"Invalid status: {data.get('status')}, using LOCAL")
            status = ContentStatus.LOCAL

        # Safely parse dates
        created_at: Optional[datetime] = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except ValueError:
                logger.warning(f"Invalid created_at date: {data.get('created_at')}")

        updated_at: Optional[datetime] = None
        if data.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except ValueError:
                logger.warning(f"Invalid updated_at date: {data.get('updated_at')}")

        synced_at: Optional[datetime] = None
        if data.get("synced_at"):
            try:
                synced_at = datetime.fromisoformat(data["synced_at"])
            except ValueError:
                logger.warning(f"Invalid synced_at date: {data.get('synced_at')}")

        return cls(
            id=data.get("id", ""),
            content_type=content_type,
            name=data.get("name", ""),
            description=data.get("description", ""),
            content_data=data.get("content_data", {}),
            tags=data.get("tags", []),
            ruleset=data.get("ruleset", "dnd2024"),
            author=LibraryAuthor.from_dict(data.get("author", {})),
            status=status,
            rating=ContentRating.from_dict(data.get("rating", {})),
            downloads=data.get("downloads", 0),
            version=data.get("version", "1.0.0"),
            created_at=created_at,
            updated_at=updated_at,
            synced_at=synced_at,
            local_only=data.get("local_only", True),
            checksum=data.get("checksum", ""),
        )

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "LibraryContent":
        """Create from database row.

        Handles corrupted JSON fields gracefully by returning defaults.
        """
        # Safely parse JSON fields with logging
        content_data: dict = {}
        if row["content_data"]:
            try:
                content_data = json.loads(row["content_data"])
            except json.JSONDecodeError as e:
                logger.warning(f"Corrupted content_data JSON in row {row['id']}: {e}")

        tags: list[str] = []
        if row["tags"]:
            try:
                tags = json.loads(row["tags"])
            except json.JSONDecodeError as e:
                logger.warning(f"Corrupted tags JSON in row {row['id']}: {e}")

        author = LibraryAuthor(id="", name="Anonymous")
        if row["author"]:
            try:
                author = LibraryAuthor.from_dict(json.loads(row["author"]))
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.warning(f"Corrupted author data in row {row['id']}: {e}")

        # Safely parse dates with logging
        created_at: Optional[datetime] = None
        if row["created_at"]:
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except ValueError as e:
                logger.warning(f"Invalid created_at in row {row['id']}: {e}")

        updated_at: Optional[datetime] = None
        if row["updated_at"]:
            try:
                updated_at = datetime.fromisoformat(row["updated_at"])
            except ValueError as e:
                logger.warning(f"Invalid updated_at in row {row['id']}: {e}")

        synced_at: Optional[datetime] = None
        if row["synced_at"]:
            try:
                synced_at = datetime.fromisoformat(row["synced_at"])
            except ValueError as e:
                logger.warning(f"Invalid synced_at in row {row['id']}: {e}")

        # Safely parse enums with logging
        try:
            content_type = ContentType(row["content_type"])
        except ValueError:
            logger.warning(f"Invalid content_type '{row['content_type']}' in row {row['id']}, using OTHER")
            content_type = ContentType.OTHER

        try:
            status = ContentStatus(row["status"])
        except ValueError:
            logger.warning(f"Invalid status '{row['status']}' in row {row['id']}, using LOCAL")
            status = ContentStatus.LOCAL

        return cls(
            id=row["id"],
            content_type=content_type,
            name=row["name"] or "Unnamed",
            description=row["description"] or "",
            content_data=content_data,
            tags=tags,
            ruleset=row["ruleset"] or "dnd2024",
            author=author,
            status=status,
            rating=ContentRating(
                average=row["rating_avg"] or 0.0,
                count=row["rating_count"] or 0,
            ),
            downloads=row["downloads"] or 0,
            version=row["version"] or "1.0.0",
            created_at=created_at,
            updated_at=updated_at,
            synced_at=synced_at,
            local_only=bool(row["local_only"]),
            checksum=row["checksum"] or "",
        )


@dataclass
class UserRating:
    """A user's rating of content."""
    content_id: str
    rating: int  # 1-5 stars
    review: Optional[str] = None
    created_at: Optional[datetime] = None


class HomebrewLibrary:
    """Local homebrew library with SQLite storage."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            data_dir = Path(user_data_dir("dnd-manager", "dnd-manager"))
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "homebrew_library.db"

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._user_id: Optional[str] = None
        try:
            self._init_db()
        except sqlite3.Error:
            self.close()
            raise

    def __enter__(self) -> "HomebrewLibrary":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager, ensuring connection is closed."""
        self.close()

    def __del__(self) -> None:
        """Destructor to ensure connection is closed."""
        self.close()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection with proper cleanup on error."""
        if self._conn is None:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA journal_mode=WAL")
                self._conn = conn
            except sqlite3.Error:
                conn.close()
                raise
        return self._conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_conn()

        # Library content table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS library_content (
                id TEXT PRIMARY KEY,
                content_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                content_data TEXT,
                tags TEXT,
                ruleset TEXT DEFAULT 'dnd2024',
                author TEXT,
                status TEXT DEFAULT 'draft',
                rating_avg REAL DEFAULT 0,
                rating_count INTEGER DEFAULT 0,
                downloads INTEGER DEFAULT 0,
                version TEXT DEFAULT '1.0.0',
                created_at TEXT,
                updated_at TEXT,
                synced_at TEXT,
                local_only INTEGER DEFAULT 1,
                checksum TEXT
            )
        """)

        # User ratings table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_ratings (
                content_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                review TEXT,
                created_at TEXT,
                PRIMARY KEY (content_id, user_id),
                FOREIGN KEY (content_id) REFERENCES library_content(id) ON DELETE CASCADE
            )
        """)

        # Downloaded/installed content tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS installed_content (
                content_id TEXT PRIMARY KEY,
                installed_at TEXT,
                source TEXT DEFAULT 'local',
                FOREIGN KEY (content_id) REFERENCES library_content(id) ON DELETE CASCADE
            )
        """)

        # User settings
        conn.execute("""
            CREATE TABLE IF NOT EXISTS library_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON library_content(content_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_content_status ON library_content(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_content_rating ON library_content(rating_avg DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_content_downloads ON library_content(downloads DESC)")

        # Full-text search
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS library_fts USING fts5(
                name,
                description,
                tags,
                content='library_content',
                content_rowid='rowid'
            )
        """)

        # FTS triggers
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS library_ai AFTER INSERT ON library_content BEGIN
                INSERT INTO library_fts(rowid, name, description, tags)
                VALUES (new.rowid, new.name, new.description, new.tags);
            END
        """)

        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS library_ad AFTER DELETE ON library_content BEGIN
                INSERT INTO library_fts(library_fts, rowid, name, description, tags)
                VALUES ('delete', old.rowid, old.name, old.description, old.tags);
            END
        """)

        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS library_au AFTER UPDATE ON library_content BEGIN
                INSERT INTO library_fts(library_fts, rowid, name, description, tags)
                VALUES ('delete', old.rowid, old.name, old.description, old.tags);
                INSERT INTO library_fts(rowid, name, description, tags)
                VALUES (new.rowid, new.name, new.description, new.tags);
            END
        """)

        conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def user_id(self) -> str:
        """Get or create user ID for ratings."""
        if self._user_id is None:
            conn = self._get_conn()
            cursor = conn.execute(
                "SELECT value FROM library_settings WHERE key = 'user_id'"
            )
            row = cursor.fetchone()
            if row:
                self._user_id = row[0]
            else:
                self._user_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO library_settings (key, value) VALUES ('user_id', ?)",
                    (self._user_id,),
                )
                conn.commit()
        return self._user_id

    def add(self, content: LibraryContent) -> LibraryContent:
        """Add content to the library."""
        conn = self._get_conn()
        now = datetime.now()

        content.created_at = now
        content.updated_at = now
        content._update_checksum()

        conn.execute(
            """
            INSERT INTO library_content
            (id, content_type, name, description, content_data, tags, ruleset,
             author, status, rating_avg, rating_count, downloads, version,
             created_at, updated_at, synced_at, local_only, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                content.id,
                content.content_type.value,
                content.name,
                content.description,
                json.dumps(content.content_data),
                json.dumps(content.tags),
                content.ruleset,
                json.dumps(content.author.to_dict()),
                content.status.value,
                content.rating.average,
                content.rating.count,
                content.downloads,
                content.version,
                content.created_at.isoformat(),
                content.updated_at.isoformat(),
                content.synced_at.isoformat() if content.synced_at else None,
                1 if content.local_only else 0,
                content.checksum,
            ),
        )
        conn.commit()
        return content

    def update(self, content: LibraryContent) -> LibraryContent:
        """Update existing content."""
        conn = self._get_conn()
        content.updated_at = datetime.now()
        content._update_checksum()

        conn.execute(
            """
            UPDATE library_content SET
                content_type = ?,
                name = ?,
                description = ?,
                content_data = ?,
                tags = ?,
                ruleset = ?,
                author = ?,
                status = ?,
                version = ?,
                updated_at = ?,
                local_only = ?,
                checksum = ?
            WHERE id = ?
            """,
            (
                content.content_type.value,
                content.name,
                content.description,
                json.dumps(content.content_data),
                json.dumps(content.tags),
                content.ruleset,
                json.dumps(content.author.to_dict()),
                content.status.value,
                content.version,
                content.updated_at.isoformat(),
                1 if content.local_only else 0,
                content.checksum,
                content.id,
            ),
        )
        conn.commit()
        return content

    def delete(self, content_id: str) -> bool:
        """Delete content from library."""
        conn = self._get_conn()
        cursor = conn.execute("DELETE FROM library_content WHERE id = ?", (content_id,))
        conn.commit()
        return cursor.rowcount > 0

    def get(self, content_id: str) -> Optional[LibraryContent]:
        """Get content by ID."""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM library_content WHERE id = ?", (content_id,))
        row = cursor.fetchone()
        if row:
            content = LibraryContent.from_row(row)
            # Add user's rating if exists
            rating_cursor = conn.execute(
                "SELECT rating FROM user_ratings WHERE content_id = ? AND user_id = ?",
                (content_id, self.user_id),
            )
            rating_row = rating_cursor.fetchone()
            if rating_row:
                content.rating.user_rating = rating_row[0]
            return content
        return None

    def browse(
        self,
        content_type: Optional[ContentType] = None,
        status: ContentStatus = ContentStatus.PUBLISHED,
        ruleset: Optional[str] = None,
        tags: Optional[list[str]] = None,
        sort_by: str = "rating",  # rating, downloads, recent, name
        limit: int = 50,
        offset: int = 0,
    ) -> list[LibraryContent]:
        """Browse library content."""
        conn = self._get_conn()

        query = "SELECT * FROM library_content WHERE status = ?"
        params: list[Any] = [status.value]

        if content_type:
            query += " AND content_type = ?"
            params.append(content_type.value)

        if ruleset:
            query += " AND ruleset = ?"
            params.append(ruleset)

        if tags:
            # Check if any tag matches
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            query += f" AND ({' OR '.join(tag_conditions)})"

        # Sorting
        sort_map = {
            "rating": "rating_avg DESC, rating_count DESC",
            "downloads": "downloads DESC",
            "recent": "created_at DESC",
            "name": "name ASC",
            "updated": "updated_at DESC",
        }
        query += f" ORDER BY {sort_map.get(sort_by, 'rating_avg DESC')}"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = conn.execute(query, params)
        return [LibraryContent.from_row(row) for row in cursor.fetchall()]

    def search(self, query: str, limit: int = 20) -> list[LibraryContent]:
        """Full-text search library content."""
        # Validate limit to prevent DoS
        limit = max(1, min(limit, 100))

        conn = self._get_conn()

        cursor = conn.execute(
            """
            SELECT library_content.*, bm25(library_fts) as score
            FROM library_fts
            JOIN library_content ON library_fts.rowid = library_content.rowid
            WHERE library_fts MATCH ? AND library_content.status = 'published'
            ORDER BY score
            LIMIT ?
            """,
            (query, limit),
        )
        return [LibraryContent.from_row(row) for row in cursor.fetchall()]

    def rate(self, content_id: str, rating: int, review: Optional[str] = None) -> bool:
        """Rate content (1-5 stars)."""
        if not 1 <= rating <= 5:
            return False

        conn = self._get_conn()
        now = datetime.now()

        # Insert or update rating
        conn.execute(
            """
            INSERT INTO user_ratings (content_id, user_id, rating, review, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(content_id, user_id) DO UPDATE SET
                rating = excluded.rating,
                review = excluded.review
            """,
            (content_id, self.user_id, rating, review, now.isoformat()),
        )

        # Update content average rating
        cursor = conn.execute(
            """
            SELECT AVG(rating) as avg, COUNT(*) as count
            FROM user_ratings WHERE content_id = ?
            """,
            (content_id,),
        )
        row = cursor.fetchone()
        if row:
            conn.execute(
                "UPDATE library_content SET rating_avg = ?, rating_count = ? WHERE id = ?",
                (row["avg"], row["count"], content_id),
            )

        conn.commit()
        return True

    def get_user_rating(self, content_id: str) -> Optional[UserRating]:
        """Get current user's rating for content."""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM user_ratings WHERE content_id = ? AND user_id = ?",
            (content_id, self.user_id),
        )
        row = cursor.fetchone()
        if row:
            return UserRating(
                content_id=row["content_id"],
                rating=row["rating"],
                review=row["review"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            )
        return None

    def install(self, content_id: str) -> bool:
        """Mark content as installed/downloaded."""
        conn = self._get_conn()
        now = datetime.now()

        conn.execute(
            """
            INSERT OR REPLACE INTO installed_content (content_id, installed_at, source)
            VALUES (?, ?, 'library')
            """,
            (content_id, now.isoformat()),
        )

        # Increment download count
        conn.execute(
            "UPDATE library_content SET downloads = downloads + 1 WHERE id = ?",
            (content_id,),
        )

        conn.commit()
        return True

    def uninstall(self, content_id: str) -> bool:
        """Remove content from installed list."""
        conn = self._get_conn()
        cursor = conn.execute(
            "DELETE FROM installed_content WHERE content_id = ?",
            (content_id,),
        )
        conn.commit()
        return cursor.rowcount > 0

    def get_installed(self) -> list[LibraryContent]:
        """Get all installed content."""
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT library_content.*
            FROM library_content
            JOIN installed_content ON library_content.id = installed_content.content_id
            ORDER BY installed_content.installed_at DESC
            """
        )
        return [LibraryContent.from_row(row) for row in cursor.fetchall()]

    def is_installed(self, content_id: str) -> bool:
        """Check if content is installed."""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT 1 FROM installed_content WHERE content_id = ?",
            (content_id,),
        )
        return cursor.fetchone() is not None

    def get_my_content(self) -> list[LibraryContent]:
        """Get content created by current user."""
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT * FROM library_content
            WHERE json_extract(author, '$.id') = ?
            ORDER BY updated_at DESC
            """,
            (self.user_id,),
        )
        return [LibraryContent.from_row(row) for row in cursor.fetchall()]

    def publish(self, content_id: str) -> bool:
        """Publish content (mark as published)."""
        conn = self._get_conn()
        now = datetime.now()
        cursor = conn.execute(
            """
            UPDATE library_content
            SET status = 'published', updated_at = ?
            WHERE id = ? AND json_extract(author, '$.id') = ?
            """,
            (now.isoformat(), content_id, self.user_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def archive(self, content_id: str) -> bool:
        """Archive content (hide from search)."""
        conn = self._get_conn()
        now = datetime.now()
        cursor = conn.execute(
            """
            UPDATE library_content
            SET status = 'archived', updated_at = ?
            WHERE id = ? AND json_extract(author, '$.id') = ?
            """,
            (now.isoformat(), content_id, self.user_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def get_stats(self) -> dict:
        """Get library statistics."""
        conn = self._get_conn()

        stats = {
            "total_content": 0,
            "published": 0,
            "my_content": 0,
            "installed": 0,
            "by_type": {},
            "top_rated": [],
            "most_downloaded": [],
        }

        # Total counts
        cursor = conn.execute("SELECT COUNT(*) FROM library_content")
        stats["total_content"] = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM library_content WHERE status = 'published'")
        stats["published"] = cursor.fetchone()[0]

        cursor = conn.execute(
            "SELECT COUNT(*) FROM library_content WHERE json_extract(author, '$.id') = ?",
            (self.user_id,),
        )
        stats["my_content"] = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM installed_content")
        stats["installed"] = cursor.fetchone()[0]

        # By type
        cursor = conn.execute(
            "SELECT content_type, COUNT(*) as count FROM library_content GROUP BY content_type"
        )
        stats["by_type"] = {row["content_type"]: row["count"] for row in cursor.fetchall()}

        # Top rated
        cursor = conn.execute(
            """
            SELECT name, rating_avg, rating_count FROM library_content
            WHERE status = 'published' AND rating_count > 0
            ORDER BY rating_avg DESC, rating_count DESC
            LIMIT 5
            """
        )
        stats["top_rated"] = [
            {"name": row["name"], "rating": row["rating_avg"], "votes": row["rating_count"]}
            for row in cursor.fetchall()
        ]

        # Most downloaded
        cursor = conn.execute(
            """
            SELECT name, downloads FROM library_content
            WHERE status = 'published'
            ORDER BY downloads DESC
            LIMIT 5
            """
        )
        stats["most_downloaded"] = [
            {"name": row["name"], "downloads": row["downloads"]}
            for row in cursor.fetchall()
        ]

        return stats

    def get_tags(self) -> list[str]:
        """Get all unique tags."""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT tags FROM library_content WHERE status = 'published' AND tags IS NOT NULL"
        )

        all_tags: set[str] = set()
        for row in cursor.fetchall():
            if row[0]:
                try:
                    tags = json.loads(row[0])
                    if isinstance(tags, list):
                        all_tags.update(tags)
                except json.JSONDecodeError:
                    pass  # Skip corrupted JSON

        return sorted(all_tags)

    def import_from_custom(self, custom_content: Any) -> list[LibraryContent]:
        """Import content from CustomContent to library.

        Args:
            custom_content: CustomContent object from data/custom.py

        Returns:
            List of created LibraryContent items
        """
        imported = []

        # Import spells
        for spell in getattr(custom_content, "spells", []):
            content = LibraryContent(
                content_type=ContentType.SPELL,
                name=spell.name,
                description=spell.description,
                content_data={
                    "level": spell.level,
                    "school": spell.school,
                    "casting_time": spell.casting_time,
                    "range": spell.range,
                    "components": spell.components,
                    "duration": spell.duration,
                    "classes": spell.classes,
                    "ritual": getattr(spell, "ritual", False),
                    "concentration": getattr(spell, "concentration", False),
                },
                tags=["spell", spell.school.lower()],
                author=LibraryAuthor(id=self.user_id, name="Local User"),
            )
            imported.append(self.add(content))

        # Import items
        for item in getattr(custom_content, "items", []):
            content = LibraryContent(
                content_type=ContentType.MAGIC_ITEM,
                name=item.name,
                description=item.description,
                content_data={
                    "item_type": item.item_type,
                    "rarity": item.rarity,
                    "requires_attunement": item.requires_attunement,
                    "properties": getattr(item, "properties", []),
                },
                tags=["item", item.rarity.lower()],
                author=LibraryAuthor(id=self.user_id, name="Local User"),
            )
            imported.append(self.add(content))

        # Import feats
        for feat in getattr(custom_content, "feats", []):
            content = LibraryContent(
                content_type=ContentType.FEAT,
                name=feat.name,
                description=feat.description,
                content_data={
                    "category": feat.category,
                    "prerequisites": feat.prerequisites,
                    "benefits": feat.benefits,
                },
                tags=["feat", feat.category.lower()],
                author=LibraryAuthor(id=self.user_id, name="Local User"),
            )
            imported.append(self.add(content))

        return imported


# Global instance
_library: Optional[HomebrewLibrary] = None


def get_homebrew_library() -> HomebrewLibrary:
    """Get the global homebrew library instance."""
    global _library
    if _library is None:
        _library = HomebrewLibrary()
    return _library
