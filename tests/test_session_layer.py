import json

from core.session import SessionLayer


def test_session_record_and_recent() -> None:
    session = SessionLayer(session_name="test")
    session.record("open vscode", "ok", "success")
    session.record("sys info", "ok", "success")

    items = session.recent(limit=1)
    assert len(items) == 1
    assert items[0].command == "sys info"


def test_session_clear() -> None:
    session = SessionLayer()
    session.record("open notepad", "ok", "success")
    session.clear()
    assert session.recent() == []


def test_session_export_json(tmp_path) -> None:
    session = SessionLayer(session_name="export-test")
    session.record("search file report", "ok", "success")

    output = tmp_path / "session.json"
    exported = session.export_json(output)
    payload = json.loads(exported.read_text(encoding="utf-8"))

    assert payload["session_name"] == "export-test"
    assert payload["count"] == 1
    assert payload["entries"][0]["command"] == "search file report"