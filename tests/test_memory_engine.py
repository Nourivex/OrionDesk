import json
from pathlib import Path

from core.memory_engine import MemoryEngine


def test_memory_preference_roundtrip(tmp_path) -> None:
    engine = MemoryEngine(storage_dir=tmp_path / "memory")
    engine.set_preference("persona", "calm")

    assert engine.get_preference("persona") == "calm"


def test_memory_note_and_top_commands(tmp_path) -> None:
    engine = MemoryEngine(storage_dir=tmp_path / "memory")
    engine.add_note("work", "ingat buka vscode")
    engine.record_command("open vscode", "success")
    engine.record_command("open vscode", "success")
    engine.record_command("sys info", "success")

    notes = engine.recent_notes(limit=1)
    top = engine.top_commands(limit=1)

    assert notes[0].tag == "work"
    assert top[0][0] == "open vscode"
    assert top[0][1] == 2


def test_memory_export_and_purge(tmp_path) -> None:
    engine = MemoryEngine(storage_dir=tmp_path / "memory")
    engine.set_preference("persona", "hacker")
    engine.record_command("open notepad", "success")

    exported = engine.export_memory(tmp_path / "export" / "memory.json")
    assert Path(exported).exists() is True

    engine.purge_all()
    assert engine.get_preference("persona") is None
    assert engine.top_commands(limit=1) == []


def test_memory_engine_imports_legacy_json(tmp_path) -> None:
    storage_dir = tmp_path / "memory"
    storage_dir.mkdir(parents=True, exist_ok=True)

    (storage_dir / "preferences.json").write_text(
        json.dumps({"persona": "calm"}),
        encoding="utf-8",
    )
    (storage_dir / "notes.json").write_text(
        json.dumps([
            {"tag": "legacy", "text": "old note", "created_at": "2025-01-01T00:00:00+00:00"}
        ]),
        encoding="utf-8",
    )
    (storage_dir / "commands.json").write_text(
        json.dumps([
            {"command": "open vscode", "status": "success", "created_at": "2025-01-01T00:00:00+00:00"}
        ]),
        encoding="utf-8",
    )

    engine = MemoryEngine(storage_dir=storage_dir)

    assert engine.get_preference("persona") == "calm"
    assert engine.recent_notes(limit=1)[0].tag == "legacy"
    assert engine.top_commands(limit=1)[0] == ("open vscode", 1)
    assert (storage_dir / "memory.db").exists() is True