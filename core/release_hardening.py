from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class ReleaseChecklistItem:
    key: str
    title: str
    completed: bool


@dataclass
class ReleaseHardeningPlan:
    checklist: list[ReleaseChecklistItem] = field(
        default_factory=lambda: [
            ReleaseChecklistItem("tests", "Regression tests pass", False),
            ReleaseChecklistItem("profiling", "Performance baseline recorded", False),
            ReleaseChecklistItem("diagnostics", "Diagnostics smoke check", False),
            ReleaseChecklistItem("rollback", "Rollback procedure verified", False),
            ReleaseChecklistItem("safety_drill", "Safety drill simulation pass", False),
        ]
    )
    rollback_steps: list[str] = field(
        default_factory=lambda: [
            "Restore last stable release package.",
            "Restore user profile backup.",
            "Revert roadmap status to prior stable phase.",
            "Publish incident note in changelog.",
        ]
    )

    def mark_completed(self, key: str) -> None:
        refreshed: list[ReleaseChecklistItem] = []
        for item in self.checklist:
            if item.key == key:
                refreshed.append(ReleaseChecklistItem(item.key, item.title, True))
            else:
                refreshed.append(item)
        self.checklist = refreshed

    def summary(self) -> dict:
        done = sum(1 for item in self.checklist if item.completed)
        total = len(self.checklist)
        return {
            "completed": done,
            "total": total,
            "all_passed": done == total,
            "rollback_steps": list(self.rollback_steps),
        }

    def run_simulation_mode(
        self,
        workflow_steps: list[dict] | None = None,
        panic_at_step: int = 2,
        rollback_window_seconds: int = 30,
    ) -> dict:
        now = datetime.now(UTC)
        steps = workflow_steps or [
            {"step_id": "S1", "name": "prepare-context", "rollback_supported": True, "age_seconds": 10},
            {"step_id": "S2", "name": "fetch-session", "rollback_supported": True, "age_seconds": 12},
            {"step_id": "S3", "name": "apply-volatile-change", "rollback_supported": True, "age_seconds": 8},
        ]

        executed: list[dict] = []
        panic_triggered = False
        for index, step in enumerate(steps, start=1):
            executed.append(
                {
                    "step_id": str(step.get("step_id", f"S{index}")),
                    "name": str(step.get("name", f"step-{index}")),
                    "rollback_supported": bool(step.get("rollback_supported", False)),
                    "age_seconds": int(step.get("age_seconds", 0)),
                    "status": "executed",
                }
            )
            if index == max(1, panic_at_step):
                panic_triggered = True
                break

        if not panic_triggered:
            self.mark_completed("safety_drill")
            return {
                "status": "Simulation Success",
                "panic_triggered": False,
                "cancelled_pending_actions": 0,
                "rollback_reports": [],
                "message": "Simulation selesai tanpa panic trigger.",
            }

        threshold = now - timedelta(seconds=max(1, rollback_window_seconds))
        rollback_reports: list[dict] = []
        conflicts = 0
        for item in reversed(executed):
            age_seconds = int(item["age_seconds"])
            executed_at = now - timedelta(seconds=age_seconds)
            within_window = executed_at >= threshold
            if not within_window:
                rollback_reports.append(
                    {
                        "step_id": item["step_id"],
                        "status": "rollback_skipped",
                        "reason": "outside rollback window",
                    }
                )
                continue
            if not item["rollback_supported"]:
                conflicts += 1
                rollback_reports.append(
                    {
                        "step_id": item["step_id"],
                        "status": "rollback_conflict",
                        "reason": "step not reversible",
                    }
                )
                continue
            rollback_reports.append(
                {
                    "step_id": item["step_id"],
                    "status": "rolled_back",
                    "reason": "simulation rollback applied",
                }
            )

        status = "Rollback Conflict" if conflicts > 0 else "Simulation Success"
        if conflicts == 0:
            self.mark_completed("safety_drill")
        return {
            "status": status,
            "panic_triggered": True,
            "cancelled_pending_actions": max(0, len(steps) - len(executed)),
            "rollback_reports": rollback_reports,
            "message": "Dummy workflow replay selesai tanpa mutasi file sistem asli.",
        }
