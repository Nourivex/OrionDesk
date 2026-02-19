from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable


@dataclass(frozen=True)
class StageLatency:
    stage: str
    elapsed_ms: float
    budget_ms: float
    exceeded: bool


class LatencyBudget:
    def __init__(self, budgets_ms: dict[str, float] | None = None) -> None:
        self._budgets_ms = budgets_ms or {
            "intent": 40.0,
            "policy": 25.0,
            "execution": 1200.0,
            "total": 1400.0,
        }
        self._stages: list[StageLatency] = []

    def timed(self, stage: str, action: Callable[[], object]) -> object:
        start = perf_counter()
        result = action()
        elapsed_ms = (perf_counter() - start) * 1000
        budget_ms = self._budgets_ms.get(stage, self._budgets_ms["total"])
        self._stages.append(
            StageLatency(
                stage=stage,
                elapsed_ms=elapsed_ms,
                budget_ms=budget_ms,
                exceeded=elapsed_ms > budget_ms,
            )
        )
        return result

    def stage_report(self) -> list[dict]:
        return [
            {
                "stage": item.stage,
                "elapsed_ms": round(item.elapsed_ms, 2),
                "budget_ms": round(item.budget_ms, 2),
                "exceeded": item.exceeded,
            }
            for item in self._stages
        ]

    def summary(self) -> dict:
        total_elapsed = sum(item.elapsed_ms for item in self._stages)
        total_budget = self._budgets_ms.get("total", 1400.0)
        return {
            "total_elapsed_ms": round(total_elapsed, 2),
            "total_budget_ms": round(total_budget, 2),
            "over_budget": total_elapsed > total_budget,
            "stages": self.stage_report(),
        }


class MainThreadResponsivenessGuard:
    def __init__(self, frame_budget_ms: float = 16.0) -> None:
        self.frame_budget_ms = frame_budget_ms

    def evaluate(self, stage_report: list[dict]) -> dict:
        blocked_stages = [
            item["stage"]
            for item in stage_report
            if item["elapsed_ms"] > self.frame_budget_ms and item["stage"] != "execution"
        ]
        return {
            "frame_budget_ms": self.frame_budget_ms,
            "blocked_stages": blocked_stages,
            "is_responsive": len(blocked_stages) == 0,
        }
