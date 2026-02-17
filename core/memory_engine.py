from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path


@dataclass(frozen=True)
class MemoryNote:
    tag: str
    text: str
    created_at: str


@dataclass
class MemoryEngine:
    storage_dir: Path = field(default_factory=lambda: Path(".oriondesk") / "memory")
    retention_days: int = 30

    def __post_init__(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.preferences_file = self.storage_dir / "preferences.json"
        self.notes_file = self.storage_dir / "notes.json"
        self.commands_file = self.storage_dir / "commands.json"
        self._ensure_files()

    def set_preference(self, key: str, value: str) -> None:
        payload = self._read_json(self.preferences_file, {})
        payload[key] = value
        self._write_json(self.preferences_file, payload)

    def get_preference(self, key: str, default: str | None = None) -> str | None:
        payload = self._read_json(self.preferences_file, {})
        return payload.get(key, default)

    def add_note(self, tag: str, text: str) -> MemoryNote:
        notes = self._read_json(self.notes_file, [])
        note = MemoryNote(tag=tag, text=text, created_at=self._now_iso())
        notes.append(note.__dict__)
        self._write_json(self.notes_file, notes)
        return note

    def recent_notes(self, limit: int = 10) -> list[MemoryNote]:
        notes = self._read_json(self.notes_file, [])
        sliced = notes[-limit:] if limit > 0 else []
        return [MemoryNote(**item) for item in sliced]

    def record_command(self, command: str, status: str) -> None:
        rows = self._read_json(self.commands_file, [])
        rows.append({"command": command, "status": status, "created_at": self._now_iso()})
        self._write_json(self.commands_file, rows)

    def top_commands(self, limit: int = 5) -> list[tuple[str, int]]:
        rows = self._read_json(self.commands_file, [])
        bucket: dict[str, int] = {}
        for row in rows:
            command = row.get("command", "")
            bucket[command] = bucket.get(command, 0) + 1
        ordered = sorted(bucket.items(), key=lambda item: item[1], reverse=True)
        return ordered[:limit]

    def export_memory(self, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "preferences": self._read_json(self.preferences_file, {}),
            "notes": self._read_json(self.notes_file, []),
            "commands": self._read_json(self.commands_file, []),
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path

    def purge_older_than(self, days: int | None = None) -> int:
        cutoff_days = days if days is not None else self.retention_days
        threshold = datetime.now(UTC) - timedelta(days=cutoff_days)

        notes = self._read_json(self.notes_file, [])
        kept_notes = [item for item in notes if self._to_datetime(item.get("created_at", "")) >= threshold]

        commands = self._read_json(self.commands_file, [])
        kept_commands = [
            item for item in commands if self._to_datetime(item.get("created_at", "")) >= threshold
        ]

        removed = (len(notes) - len(kept_notes)) + (len(commands) - len(kept_commands))
        self._write_json(self.notes_file, kept_notes)
        self._write_json(self.commands_file, kept_commands)
        return removed

    def purge_all(self) -> None:
        self._write_json(self.preferences_file, {})
        self._write_json(self.notes_file, [])
        self._write_json(self.commands_file, [])

    def _ensure_files(self) -> None:
        if not self.preferences_file.exists():
            self._write_json(self.preferences_file, {})
        if not self.notes_file.exists():
            self._write_json(self.notes_file, [])
        if not self.commands_file.exists():
            self._write_json(self.commands_file, [])

    def _read_json(self, path: Path, fallback):
        if not path.exists():
            return fallback
        raw = path.read_text(encoding="utf-8")
        return json.loads(raw) if raw.strip() else fallback

    def _write_json(self, path: Path, payload) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    def _to_datetime(self, value: str) -> datetime:
        if not value:
            return datetime.fromtimestamp(0, tz=UTC)
        return datetime.fromisoformat(value)
