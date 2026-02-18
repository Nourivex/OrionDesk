from __future__ import annotations

from dataclasses import dataclass, field


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
