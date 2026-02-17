from pathlib import Path

from core.observability import DiagnosticReporter, HealthMonitor, RecoveryManager, StructuredLogger
from core.router import CommandRouter


def test_structured_logger_writes_and_tails(tmp_path) -> None:
    logger = StructuredLogger(log_dir=tmp_path / "logs")
    logger.log("info", "test", "hello", {"a": 1})
    rows = logger.tail(limit=1)

    assert len(rows) == 1
    assert rows[0]["event"] == "test"


def test_health_monitor_returns_checks() -> None:
    router = CommandRouter()
    monitor = HealthMonitor()
    checks = monitor.run(router)

    names = {item.name for item in checks}
    assert {"contracts", "handlers", "security_guard", "memory_engine"}.issubset(names)


def test_recovery_manager_snapshot_roundtrip(tmp_path) -> None:
    manager = RecoveryManager(snapshot_dir=tmp_path / "recovery")
    manager.save_snapshot("test-session", [{"command": "open vscode", "status": "success"}])
    payload = manager.load_latest_snapshot()

    assert payload is not None
    assert payload["session_name"] == "test-session"
    assert payload["entries"][0]["command"] == "open vscode"


def test_diagnostic_report_generation(tmp_path) -> None:
    reporter = DiagnosticReporter(output_dir=tmp_path / "diag")
    checks = []
    logs = [{"event": "ok"}]
    report_path = reporter.generate(checks, logs)

    assert Path(report_path).exists() is True