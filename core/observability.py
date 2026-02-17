from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HealthCheckResult:
    name: str
    status: str
    detail: str


class StructuredLogger:
    def __init__(self, log_dir: Path | None = None) -> None:
        self.log_dir = log_dir or (Path(".oriondesk") / "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "events.jsonl"

    def log(self, level: str, event: str, message: str, metadata: dict[str, Any] | None = None) -> None:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            "level": level,
            "event": event,
            "message": message,
            "metadata": metadata or {},
        }
        with self.log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")

    def tail(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.log_file.exists():
            return []
        lines = self.log_file.read_text(encoding="utf-8").splitlines()
        selected = lines[-limit:] if limit > 0 else []
        return [json.loads(item) for item in selected]


class RecoveryManager:
    def __init__(self, snapshot_dir: Path | None = None) -> None:
        self.snapshot_dir = snapshot_dir or (Path(".oriondesk") / "recovery")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, session_name: str, entries: list[dict[str, Any]]) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        target = self.snapshot_dir / f"{session_name}-{timestamp}.json"
        payload = {"session_name": session_name, "entries": entries}
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return target

    def load_latest_snapshot(self) -> dict[str, Any] | None:
        files = sorted(self.snapshot_dir.glob("*.json"))
        if not files:
            return None
        latest = files[-1]
        return json.loads(latest.read_text(encoding="utf-8"))


class HealthMonitor:
    def run(self, router) -> list[HealthCheckResult]:
        checks = [
            self._check_contracts(router),
            self._check_plugins(router),
            self._check_security_guard(router),
            self._check_memory(router),
        ]
        return checks

    def _check_contracts(self, router) -> HealthCheckResult:
        total = len(getattr(router, "contracts", {}))
        status = "ok" if total > 0 else "error"
        return HealthCheckResult("contracts", status, f"total={total}")

    def _check_plugins(self, router) -> HealthCheckResult:
        total = len(getattr(router, "handlers", {}))
        status = "ok" if total > 0 else "error"
        return HealthCheckResult("handlers", status, f"total={total}")

    def _check_security_guard(self, router) -> HealthCheckResult:
        guard = getattr(router, "security_guard", None)
        status = "ok" if guard is not None else "error"
        detail = "available" if guard is not None else "missing"
        return HealthCheckResult("security_guard", status, detail)

    def _check_memory(self, router) -> HealthCheckResult:
        memory = getattr(router, "memory_engine", None)
        status = "ok" if memory is not None else "error"
        detail = "available" if memory is not None else "missing"
        return HealthCheckResult("memory_engine", status, detail)


class DiagnosticReporter:
    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or (Path(".oriondesk") / "diagnostics")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, checks: list[HealthCheckResult], recent_logs: list[dict[str, Any]]) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        target = self.output_dir / f"diagnostic-{timestamp}.json"
        payload = {
            "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "checks": [asdict(item) for item in checks],
            "recent_logs": recent_logs,
        }
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return target
