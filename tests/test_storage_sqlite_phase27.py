from core.storage import (
    CommandHistoryRepository,
    NoteRepository,
    PreferenceRepository,
    SQLiteStorageEngine,
)


def test_sqlite_repositories_roundtrip(tmp_path) -> None:
    db_path = tmp_path / "storage" / "oriondesk.db"
    engine = SQLiteStorageEngine(db_path=db_path)

    preferences = PreferenceRepository(engine)
    notes = NoteRepository(engine)
    commands = CommandHistoryRepository(engine)

    preferences.set("theme", "dark")
    notes.add("dev", "phase27 ready", "2026-02-18T10:00:00+00:00")
    commands.add("open vscode", "success", "2026-02-18T10:00:00+00:00")
    commands.add("open vscode", "success", "2026-02-18T10:01:00+00:00")

    assert preferences.get("theme") == "dark"
    assert notes.recent(limit=1)[0]["tag"] == "dev"
    assert commands.top_commands(limit=1) == [("open vscode", 2)]


def test_sqlite_migrations_applied(tmp_path) -> None:
    db_path = tmp_path / "storage" / "oriondesk.db"
    engine = SQLiteStorageEngine(db_path=db_path)

    applied = engine.fetch_all("SELECT version FROM schema_migrations ORDER BY version ASC")

    assert any(version == "0001_initial.sql" for version, in applied)
