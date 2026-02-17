from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SafeModePolicy:
    require_confirmation_for: tuple[str, ...] = ("delete", "kill", "shutdown")
    blocked_actions: tuple[str, ...] = ()

    def requires_confirmation(self, keyword: str) -> bool:
        return keyword in self.require_confirmation_for

    def is_blocked(self, keyword: str) -> bool:
        return keyword in self.blocked_actions
