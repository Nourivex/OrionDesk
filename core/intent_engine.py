from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class IntentResolution:
    original: str
    resolved: str
    confidence: float
    reason: str


class LocalIntentEngine:
    def __init__(self) -> None:
        self.open_markers = {"open", "buka", "bukakan", "launch", "jalankan"}
        self.search_markers = {"search", "cari", "find", "temukan"}
        self.sys_markers = {"sys", "status", "info"}

    def resolve(self, raw: str, allowed_keywords: set[str]) -> IntentResolution:
        clean = raw.strip()
        if not clean:
            return IntentResolution(raw, clean, 1.0, "empty")

        strict = self._strict_match(clean, allowed_keywords)
        if strict is not None:
            return strict

        semantic = self._semantic_match(clean, allowed_keywords)
        if semantic is not None:
            return semantic

        return IntentResolution(raw, clean, 0.0, "unresolved")

    def _strict_match(self, clean: str, allowed_keywords: set[str]) -> IntentResolution | None:
        first = clean.split(maxsplit=1)[0].lower()
        if first in allowed_keywords:
            return IntentResolution(clean, clean, 1.0, "strict_keyword")
        return None

    def _semantic_match(self, clean: str, allowed_keywords: set[str]) -> IntentResolution | None:
        lowered = clean.lower()
        words = self._words(lowered)

        open_candidate = self._resolve_open(words, allowed_keywords)
        if open_candidate is not None:
            return IntentResolution(clean, open_candidate, 0.78, "semantic_open")

        search_candidate = self._resolve_search(words, lowered, allowed_keywords)
        if search_candidate is not None:
            return IntentResolution(clean, search_candidate, 0.76, "semantic_search")

        has_sys_hint = self._contains(words, self.sys_markers)
        has_system_pair = "system" in words and ("status" in words or "info" in words)
        if (has_sys_hint or has_system_pair) and "sys" in allowed_keywords:
            return IntentResolution(clean, "sys info", 0.72, "semantic_sys")

        return None

    def _resolve_open(self, words: list[str], allowed_keywords: set[str]) -> str | None:
        if "open" not in allowed_keywords:
            return None
        if not self._contains(words, self.open_markers):
            return None

        app_aliases = ["vscode", "chrome", "notepad"]
        for alias in app_aliases:
            if alias in words:
                return f"open {alias}"
        return None

    def _resolve_search(self, words: list[str], lowered: str, allowed_keywords: set[str]) -> str | None:
        if "search" not in allowed_keywords:
            return None
        if not self._contains(words, self.search_markers):
            return None

        marker = "file"
        query = self._extract_query(lowered)
        if not query:
            return None
        return f"search {marker} {query}"

    def _extract_query(self, lowered: str) -> str:
        match = re.search(r"([a-z0-9_\-]+\.[a-z0-9]{2,8})", lowered)
        if match:
            return match.group(1)

        words = [item for item in self._words(lowered) if item not in self.search_markers]
        noise = {"tolong", "dong", "berkas", "file", "carikan", "ya", "please"}
        filtered = [item for item in words if item not in noise]
        if not filtered:
            return ""
        return " ".join(filtered[:4])

    def _words(self, lowered: str) -> list[str]:
        return re.findall(r"[a-z0-9_.-]+", lowered)

    def _contains(self, words: list[str], markers: set[str]) -> bool:
        return any(item in markers for item in words)
