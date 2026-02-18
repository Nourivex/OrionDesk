from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from pathlib import Path

from core.storage import SessionLogRepository, SQLiteStorageEngine


@dataclass(frozen=True)
class SessionEntry:
    timestamp: str
    command: str
    message: str
    status: str


@dataclass
class SessionLayer:
    session_name: str = "default"
    storage_dir: Path = field(default_factory=lambda: Path(".oriondesk") / "session")
    db_path: Path | None = None

    def __post_init__(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        database_path = self.db_path or (self.storage_dir / "session.db")
        self.storage_engine = SQLiteStorageEngine(db_path=database_path)
        self.session_repo = SessionLogRepository(self.storage_engine)

    def record(self, command: str, message: str, status: str) -> SessionEntry:
        entry = SessionEntry(
            timestamp=self._timestamp(),
            command=command,
            message=message,
            status=status,
        )
        self.session_repo.add(
            session_name=self.session_name,
            timestamp=entry.timestamp,
            command=entry.command,
            message=entry.message,
            status=entry.status,
        )
        return entry

    def recent(self, limit: int = 20) -> list[SessionEntry]:
        rows = self.session_repo.recent(session_name=self.session_name, limit=limit)
        return [SessionEntry(**item) for item in rows]

    @property
    def entries(self) -> list[SessionEntry]:
        rows = self.session_repo.recent(session_name=self.session_name, limit=None)
        return [SessionEntry(**item) for item in rows]

    def clear(self) -> None:
        self.session_repo.clear(self.session_name)

    def export_json(self, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        entries = self.entries
        payload = {
            "session_name": self.session_name,
            "count": len(entries),
            "entries": [asdict(item) for item in entries],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path

    def _timestamp(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")
