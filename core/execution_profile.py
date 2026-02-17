from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileDecision:
    mode: str
    requires_confirmation: bool
    risk_level: str
    reason: str = ""


class ExecutionProfilePolicy:
    def __init__(self, profile: str = "strict") -> None:
        self.profile = profile
        self._risk_map = {
            "open": "low",
            "search": "low",
            "sys": "low",
            "capability": "medium",
            "smart": "medium",
            "profile": "low",
            "kill": "high",
            "delete": "high",
            "shutdown": "critical",
        }

    def set_profile(self, profile: str) -> str:
        allowed = {"strict", "balanced", "power", "explain-only"}
        if profile not in allowed:
            return self.profile
        self.profile = profile
        return self.profile

    def risk_level(self, keyword: str) -> str:
        return self._risk_map.get(keyword.lower(), "low")

    def evaluate(self, keyword: str) -> ProfileDecision:
        risk = self.risk_level(keyword)
        if self.profile == "explain-only" and risk in {"high", "critical"}:
            return ProfileDecision("explain", False, risk, "Explain-only profile memblokir execute command berisiko.")

        if self.profile == "strict" and risk == "critical":
            return ProfileDecision("blocked", True, risk, "Strict profile memblokir command critical.")

        if self.profile in {"strict", "balanced"} and risk in {"high", "critical"}:
            return ProfileDecision("allow", True, risk, "Profile membutuhkan konfirmasi manual untuk command berisiko.")

        if self.profile == "power" and risk in {"high", "critical"}:
            return ProfileDecision("allow", False, risk, "Power profile mengizinkan execute command berisiko.")

        return ProfileDecision("allow", False, risk, "")
