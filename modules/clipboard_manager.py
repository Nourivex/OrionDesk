from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class ClipboardManager:
    capacity: int = 20
    _history: deque[str] = field(default_factory=deque)

    def push(self, text: str) -> None:
        clean = text.strip()
        if not clean:
            return
        if self.capacity <= 0:
            return
        self._history.appendleft(clean)
        while len(self._history) > self.capacity:
            self._history.pop()

    def recent(self, limit: int = 5) -> list[str]:
        if limit <= 0:
            return []
        return list(self._history)[:limit]

    def clear(self) -> None:
        self._history.clear()
