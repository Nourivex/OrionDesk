from pathlib import Path

from modules.clipboard_manager import ClipboardManager
from modules.focus_mode import FocusModeManager
from modules.network_diagnostics import NetworkDiagnostics
from modules.project_manager import ProjectManager


def test_project_manager_discovery(tmp_path) -> None:
    projects_root = tmp_path / "projects"
    target = projects_root / "oriondesk"
    target.mkdir(parents=True, exist_ok=True)

    manager = ProjectManager(roots=[projects_root])
    message = manager.open_project("oriondesk")

    assert str(target) in message


def test_clipboard_manager_ring_buffer() -> None:
    manager = ClipboardManager(capacity=2)
    manager.push("first")
    manager.push("second")
    manager.push("third")

    assert manager.recent(limit=3) == ["third", "second"]


def test_focus_mode_enable_disable() -> None:
    manager = FocusModeManager(cpu_guard_percent=75)

    enabled = manager.enable("game")
    assert "game" in enabled
    assert "updates_blocked=True" in manager.status()

    disabled = manager.disable()
    assert "dinonaktifkan" in disabled
    assert manager.status() == "Mode performa: off"


def test_network_diagnostics_dns_and_ping() -> None:
    diagnostics = NetworkDiagnostics(
        dns_resolver=lambda host: (host, [], ["127.0.0.1"]),
        ping_runner=lambda _cmd: type("Result", (), {"returncode": 0, "stdout": "Pinging localhost"})(),
    )

    dns_result = diagnostics.dns_lookup("localhost")
    ping_result = diagnostics.ping_profile("localhost")

    assert "127.0.0.1" in dns_result
    assert "ok" in ping_result


def test_project_manager_not_found(tmp_path) -> None:
    manager = ProjectManager(roots=[tmp_path / "missing"])
    result = manager.open_project("none")

    assert "tidak ditemukan" in result


def test_network_diagnostics_invalid_dns() -> None:
    def fail_resolver(_host: str):
        raise OSError("lookup failed")

    diagnostics = NetworkDiagnostics(dns_resolver=fail_resolver)
    assert "gagal" in diagnostics.dns_lookup("example.invalid")
