from pathlib import Path

from modules.system_actions import SystemActions


def test_delete_path_removes_file(tmp_path: Path) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("hello", encoding="utf-8")

    actions = SystemActions()
    message = actions.delete_path(str(target))

    assert "dihapus" in message
    assert target.exists() is False


def test_terminate_process_unknown_name_returns_message() -> None:
    actions = SystemActions()
    message = actions.terminate_process("process-yang-pasti-tidak-ada-12345.exe")

    assert "tidak ditemukan" in message


def test_terminate_process_unknown_pid_returns_message() -> None:
    actions = SystemActions()
    message = actions.terminate_process("999999")

    assert "tidak ditemukan" in message
