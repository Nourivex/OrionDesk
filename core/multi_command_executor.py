from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class MultiCommandItem:
    command: str
    risk_level: str
    execution_mode: str

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "risk_level": self.risk_level,
            "execution_mode": self.execution_mode,
        }


class MultiCommandExecutor:
    def bundle(self, commands: list[str], risk_level: Callable[[str], str]) -> list[dict]:
        bundles: list[dict] = []
        for command in commands:
            keyword = command.split(" ")[0].lower() if command.strip() else ""
            level = risk_level(keyword)
            mode = self._execution_mode(keyword, level)
            bundles.append(MultiCommandItem(command=command, risk_level=level, execution_mode=mode).to_dict())
        return bundles

    def execute(
        self,
        bundles: list[dict],
        run_command: Callable[[str], tuple[str, str]],
    ) -> list[dict]:
        reports: list[dict] = []
        for item in bundles:
            start = time.perf_counter()
            status, message = run_command(item["command"])
            duration_ms = (time.perf_counter() - start) * 1000.0
            reports.append(
                {
                    "command": item["command"],
                    "risk_level": item["risk_level"],
                    "execution_mode": item["execution_mode"],
                    "status": status,
                    "duration_ms": round(duration_ms, 2),
                    "message": message,
                }
            )
        return reports

    def _execution_mode(self, keyword: str, risk_level: str) -> str:
        if risk_level in {"high", "critical"}:
            return "guarded"
        if keyword in {"search", "sys", "capability", "net"}:
            return "parallel-eligible"
        return "chain"
