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