from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from core.storage import CommandHistoryRepository, NoteRepository, PreferenceRepository, SQLiteStorageEngine


@dataclass(frozen=True)
class MemoryNote:
    tag: str
    text: str
    created_at: str


@dataclass
class MemoryEngine:
    storage_dir: Path = field(default_factory=lambda: Path(".oriondesk") / "memory")
    retention_days: int = 30
    db_path: Path | None = None

    def __post_init__(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.preferences_file = self.storage_dir / "preferences.json"
        self.notes_file = self.storage_dir / "notes.json"
        self.commands_file = self.storage_dir / "commands.json"
        database_path = self.db_path or (self.storage_dir / "memory.db")
        self.storage_engine = SQLiteStorageEngine(db_path=database_path)
        self.preference_repo = PreferenceRepository(self.storage_engine)
        self.note_repo = NoteRepository(self.storage_engine)
        self.command_repo = CommandHistoryRepository(self.storage_engine)
        self._migrate_legacy_json_if_present()

    def set_preference(self, key: str, value: str) -> None:
        self.preference_repo.set(key, value)

    def get_preference(self, key: str, default: str | None = None) -> str | None:
        return self.preference_repo.get(key, default)

    def add_note(self, tag: str, text: str) -> MemoryNote:
        note = MemoryNote(tag=tag, text=text, created_at=self._now_iso())
        self.note_repo.add(tag=tag, text=text, created_at=note.created_at)
        return note

    def recent_notes(self, limit: int = 10) -> list[MemoryNote]:
        rows = self.note_repo.recent(limit=limit)
        return [MemoryNote(**item) for item in rows]

    def record_command(self, command: str, status: str) -> None:
        self.command_repo.add(command=command, status=status, created_at=self._now_iso())

    def top_commands(self, limit: int = 5) -> list[tuple[str, int]]:
        return self.command_repo.top_commands(limit=limit)

    def export_memory(self, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "preferences": self.preference_repo.all(),
            "notes": self.note_repo.all(),
            "commands": self.command_repo.all(),
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path

    def purge_older_than(self, days: int | None = None) -> int:
        cutoff_days = days if days is not None else self.retention_days
        threshold = datetime.now(UTC) - timedelta(days=cutoff_days)

        threshold_iso = threshold.isoformat(timespec="seconds")
        removed_notes = self.note_repo.purge_older_than(threshold_iso)
        removed_commands = self.command_repo.purge_older_than(threshold_iso)
        return removed_notes + removed_commands

    def purge_all(self) -> None:
        self.preference_repo.clear()
        self.note_repo.clear()
        self.command_repo.clear()

    def _migrate_legacy_json_if_present(self) -> None:
        if self.storage_engine.table_count("preferences") > 0:
            return
        if self.storage_engine.table_count("notes") > 0:
            return
        if self.storage_engine.table_count("commands") > 0:
            return

        preferences = self._read_json(self.preferences_file, {})
        for key, value in preferences.items():
            self.preference_repo.set(str(key), str(value))

        notes = self._read_json(self.notes_file, [])
        for item in notes:
            tag = str(item.get("tag", ""))
            text = str(item.get("text", ""))
            created_at = str(item.get("created_at", self._now_iso()))
            self.note_repo.add(tag=tag, text=text, created_at=created_at)

        commands = self._read_json(self.commands_file, [])
        for item in commands:
            command = str(item.get("command", ""))
            status = str(item.get("status", ""))
            created_at = str(item.get("created_at", self._now_iso()))
            self.command_repo.add(command=command, status=status, created_at=created_at)

    def _read_json(self, path: Path, fallback):
        if not path.exists():
            return fallback
        raw = path.read_text(encoding="utf-8")
        return json.loads(raw) if raw.strip() else fallback

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")
