from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from pathlib import Path


@dataclass(frozen=True)
class SessionEntry:
    timestamp: str
    command: str
    message: str
    status: str


@dataclass
class SessionLayer:
    session_name: str = "default"
    entries: list[SessionEntry] = field(default_factory=list)

    def record(self, command: str, message: str, status: str) -> SessionEntry:
        entry = SessionEntry(
            timestamp=self._timestamp(),
            command=command,
            message=message,
            status=status,
        )
        self.entries.append(entry)
        return entry

    def recent(self, limit: int = 20) -> list[SessionEntry]:
        if limit <= 0:
            return []
        return self.entries[-limit:]

    def clear(self) -> None:
        self.entries.clear()

    def export_json(self, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_name": self.session_name,
            "count": len(self.entries),
            "entries": [asdict(item) for item in self.entries],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path

    def _timestamp(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")
