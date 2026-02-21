from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class ActionPacingConfig:
    window_seconds: int = 300
    threshold_calm: int = 6
    threshold_hacker: int = 12
    threshold_command_tab: int = 12


@dataclass(frozen=True)
class FatigueState:
    auto_action_timestamps: list[float]
    fatigue_penalty: float
    force_confirmation: bool
    threshold_used: int
    count_in_window: int


@dataclass(frozen=True)
class ImpactAssessment:
    is_read_only: bool
    confidence: float
    reason: str


@dataclass(frozen=True)
class AutoActionDecision:
    normalized_command: str
    can_auto_execute: bool
    base_score: float
    final_score: float
    risk_level: str
    fatigue_penalty: float
    fatigue_reason: str
    force_confirmation: bool
    reason: str


class CompanionPolicy:
    def __init__(self, pacing: ActionPacingConfig | None = None) -> None:
        self.pacing = pacing or ActionPacingConfig()

    def evaluate_fatigue(
        self,
        timestamps: list[float],
        profile_name: str,
        active_tab: str,
        now: float | None = None,
    ) -> FatigueState:
        current = time.monotonic() if now is None else float(now)
        window_start = current - float(self.pacing.window_seconds)
        pruned = [stamp for stamp in timestamps if stamp >= window_start]
        threshold = self._threshold_for(profile_name=profile_name, active_tab=active_tab)
        count = len(pruned)
        excess = max(0, count - threshold)
        penalty = min(0.40, 0.08 * excess)
        force_confirmation = count >= threshold
        return FatigueState(
            auto_action_timestamps=pruned,
            fatigue_penalty=round(penalty, 3),
            force_confirmation=force_confirmation,
            threshold_used=threshold,
            count_in_window=count,
        )

    def _threshold_for(self, profile_name: str, active_tab: str) -> int:
        profile = profile_name.strip().lower()
        tab = active_tab.strip().lower()
        if tab == "command":
            return self.pacing.threshold_command_tab
        if profile in {"hacker", "aggressive"}:
            return self.pacing.threshold_hacker
        return self.pacing.threshold_calm
