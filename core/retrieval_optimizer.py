from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class CacheEntry:
    value: object
    created_at: datetime


class RetrievalOptimizer:
    def __init__(self, cache_ttl_seconds: int = 180) -> None:
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: dict[str, CacheEntry] = {}

    def optimize_query(self, raw_input: str) -> str:
        text = " ".join(raw_input.strip().lower().split())
        return text

    def get_cache(self, key: str) -> object | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        age = (datetime.now(UTC) - entry.created_at).total_seconds()
        if age > self.cache_ttl_seconds:
            self._cache.pop(key, None)
            return None
        return entry.value

    def set_cache(self, key: str, value: object) -> None:
        self._cache[key] = CacheEntry(value=value, created_at=datetime.now(UTC))

    def rank_session_context(self, entries: list, query: str, limit: int = 4) -> list:
        query_tokens = self._tokens(query)
        ranked = []
        total = len(entries)
        for index, item in enumerate(entries):
            command = getattr(item, "command", "")
            status = getattr(item, "status", "")
            command_tokens = self._tokens(command)
            overlap = self._fuzzy_overlap(query_tokens, command_tokens)
            recency_bonus = (total - index) / max(total, 1)
            success_bonus = 0.2 if status == "success" else 0.0
            score = overlap + recency_bonus + success_bonus
            ranked.append((score, item))
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in ranked[:limit] if _ > 0]

    def reduce_redundant_patterns(self, commands: list[str]) -> list[str]:
        seen: set[str] = set()
        reduced: list[str] = []
        for command in commands:
            normalized = self.optimize_query(command)
            if normalized in seen:
                continue
            seen.add(normalized)
            reduced.append(command)
        return reduced

    def _tokens(self, value: str) -> list[str]:
        words = re.findall(r"[a-z0-9]+", self.optimize_query(value))
        noise = {"tolong", "please", "dong", "cari", "file", "the", "a"}
        return [item for item in words if item and item not in noise]

    def _fuzzy_overlap(self, left: list[str], right: list[str]) -> float:
        score = 0.0
        for token in left:
            for target in right:
                if token == target:
                    score += 1.0
                    break
                if token in target or target in token:
                    score += 0.6
                    break
        return score
