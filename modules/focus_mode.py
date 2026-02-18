from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FocusModeManager:
    active_mode: str | None = None
    cpu_guard_percent: int = 80
    blocked_notifications: bool = False
    blocked_updates: bool = False
    _profiles: dict[str, dict[str, bool]] = field(
        default_factory=lambda: {
            "focus": {"blocked_notifications": True, "blocked_updates": False},
            "game": {"blocked_notifications": True, "blocked_updates": True},
        }
    )

    def enable(self, mode: str) -> str:
        key = mode.strip().lower()
        profile = self._profiles.get(key)
        if profile is None:
            return "Mode tidak dikenali. Gunakan: focus atau game."

        self.active_mode = key
        self.blocked_notifications = profile["blocked_notifications"]
        self.blocked_updates = profile["blocked_updates"]
        return f"Mode '{key}' aktif. CPU guard {self.cpu_guard_percent}%."

    def disable(self) -> str:
        self.active_mode = None
        self.blocked_notifications = False
        self.blocked_updates = False
        return "Mode performa dinonaktifkan."

    def status(self) -> str:
        if self.active_mode is None:
            return "Mode performa: off"
        return (
            f"Mode performa: {self.active_mode} | notifications_blocked={self.blocked_notifications} "
            f"| updates_blocked={self.blocked_updates}"
        )
