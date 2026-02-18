from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from core.storage.sqlite_engine import SQLiteStorageEngine


@dataclass
class PreferenceRepository:
    engine: SQLiteStorageEngine

    def set(self, key: str, value: str) -> None:
        self.engine.execute(
            """
            INSERT INTO preferences(key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (key, value, self._now_iso()),
        )

    def get(self, key: str, default: str | None = None) -> str | None:
        row = self.engine.fetch_one("SELECT value FROM preferences WHERE key = ?", (key,))
        if row is None:
            return default
        return str(row[0])

    def all(self) -> dict[str, str]:
        rows = self.engine.fetch_all("SELECT key, value FROM preferences")
        return {str(key): str(value) for key, value in rows}

    def clear(self) -> None:
        self.engine.execute("DELETE FROM preferences")

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass
class NoteRepository:
    engine: SQLiteStorageEngine

    def add(self, tag: str, text: str, created_at: str) -> None:
        self.engine.execute(
            "INSERT INTO notes(tag, text, created_at) VALUES (?, ?, ?)",
            (tag, text, created_at),
        )

    def recent(self, limit: int = 10) -> list[dict[str, str]]:
        if limit <= 0:
            return []
        rows = self.engine.fetch_all(
            """
            SELECT tag, text, created_at
            FROM notes
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        ordered = reversed(rows)
        return [
            {"tag": str(tag), "text": str(text), "created_at": str(created_at)}
            for tag, text, created_at in ordered
        ]

    def all(self) -> list[dict[str, str]]:
        rows = self.engine.fetch_all(
            "SELECT tag, text, created_at FROM notes ORDER BY id ASC"
        )
        return [
            {"tag": str(tag), "text": str(text), "created_at": str(created_at)}
            for tag, text, created_at in rows
        ]

    def purge_older_than(self, threshold_iso: str) -> int:
        before = self.engine.table_count("notes")
        self.engine.execute("DELETE FROM notes WHERE created_at < ?", (threshold_iso,))
        after = self.engine.table_count("notes")
        return before - after

    def clear(self) -> None:
        self.engine.execute("DELETE FROM notes")


@dataclass
class CommandHistoryRepository:
    engine: SQLiteStorageEngine

    def add(self, command: str, status: str, created_at: str) -> None:
        self.engine.execute(
            "INSERT INTO commands(command, status, created_at) VALUES (?, ?, ?)",
            (command, status, created_at),
        )

    def all(self) -> list[dict[str, str]]:
        rows = self.engine.fetch_all(
            "SELECT command, status, created_at FROM commands ORDER BY id ASC"
        )
        return [
            {"command": str(command), "status": str(status), "created_at": str(created_at)}
            for command, status, created_at in rows
        ]

    def top_commands(self, limit: int = 5) -> list[tuple[str, int]]:
        if limit <= 0:
            return []
        rows = self.engine.fetch_all(
            """
            SELECT command, COUNT(*) as frequency
            FROM commands
            GROUP BY command
            ORDER BY frequency DESC, command ASC
            LIMIT ?
            """,
            (limit,),
        )
        return [(str(command), int(freq)) for command, freq in rows]

    def purge_older_than(self, threshold_iso: str) -> int:
        before = self.engine.table_count("commands")
        self.engine.execute("DELETE FROM commands WHERE created_at < ?", (threshold_iso,))
        after = self.engine.table_count("commands")
        return before - after

    def clear(self) -> None:
        self.engine.execute("DELETE FROM commands")


@dataclass
class SessionLogRepository:
    engine: SQLiteStorageEngine

    def add(self, session_name: str, timestamp: str, command: str, message: str, status: str) -> None:
        self.engine.execute(
            """
            INSERT INTO session_logs(session_name, timestamp, command, message, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_name, timestamp, command, message, status),
        )

    def recent(self, session_name: str, limit: int | None = 20) -> list[dict[str, str]]:
        if limit is not None and limit <= 0:
            return []
        if limit is None:
            rows = self.engine.fetch_all(
                """
                SELECT timestamp, command, message, status
                FROM session_logs
                WHERE session_name = ?
                ORDER BY id ASC
                """,
                (session_name,),
            )
        else:
            rows = self.engine.fetch_all(
                """
                SELECT timestamp, command, message, status
                FROM session_logs
                WHERE session_name = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_name, limit),
            )
            rows = list(reversed(rows))

        return [
            {
                "timestamp": str(timestamp),
                "command": str(command),
                "message": str(message),
                "status": str(status),
            }
            for timestamp, command, message, status in rows
        ]

    def clear(self, session_name: str) -> None:
        self.engine.execute("DELETE FROM session_logs WHERE session_name = ?", (session_name,))
