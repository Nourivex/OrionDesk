import json

from core.session import SessionLayer


def test_session_record_and_recent(tmp_path) -> None:
    session = SessionLayer(session_name="test", db_path=tmp_path / "session_record.db")
    session.record("open vscode", "ok", "success")
    session.record("sys info", "ok", "success")

    items = session.recent(limit=1)
    assert len(items) == 1
    assert items[0].command == "sys info"


def test_session_clear(tmp_path) -> None:
    session = SessionLayer(db_path=tmp_path / "session_clear.db")
    session.record("open notepad", "ok", "success")
    session.clear()
    assert session.recent() == []


def test_session_export_json(tmp_path) -> None:
    session = SessionLayer(session_name="export-test", db_path=tmp_path / "session_export.db")
    session.record("search file report", "ok", "success")

    output = tmp_path / "session.json"
    exported = session.export_json(output)
    payload = json.loads(exported.read_text(encoding="utf-8"))

    assert payload["session_name"] == "export-test"
    assert payload["count"] == 1
    assert payload["entries"][0]["command"] == "search file report"


def test_session_persists_across_instances(tmp_path) -> None:
    db_path = tmp_path / "session" / "session.db"

    first = SessionLayer(session_name="persist", db_path=db_path)
    first.record("open vscode", "ok", "success")

    second = SessionLayer(session_name="persist", db_path=db_path)
    recent = second.recent(limit=5)

    assert len(recent) == 1
    assert recent[0].command == "open vscode"