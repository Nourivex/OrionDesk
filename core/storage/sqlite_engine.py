from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


@dataclass
class SQLiteStorageEngine:
    db_path: Path = field(default_factory=lambda: Path(".oriondesk") / "storage" / "oriondesk.db")
    migrations_dir: Path = field(default_factory=lambda: Path(__file__).parent / "migrations")

    def __post_init__(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.apply_migrations()

    def execute(self, query: str, params: Iterable | None = None) -> None:
        values = tuple(params or ())
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(query, values)
            connection.commit()

    def fetch_one(self, query: str, params: Iterable | None = None):
        values = tuple(params or ())
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(query, values)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: Iterable | None = None) -> list[tuple]:
        values = tuple(params or ())
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(query, values)
            return cursor.fetchall()

    def apply_migrations(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
            )
            applied = {
                row[0] for row in connection.execute("SELECT version FROM schema_migrations").fetchall()
            }
            for path in sorted(self.migrations_dir.glob("*.sql")):
                if path.name in applied:
                    continue
                script = path.read_text(encoding="utf-8")
                connection.executescript(script)
                connection.execute(
                    "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                    (path.name, self._now_iso()),
                )
            connection.commit()

    def table_count(self, table_name: str) -> int:
        row = self.fetch_one(f"SELECT COUNT(*) FROM {table_name}")
        return int(row[0]) if row is not None else 0

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")
