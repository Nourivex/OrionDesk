from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AutoCorrection:
    original: str
    corrected: str
    confidence: float
    requires_confirmation: bool


class SmartAssistEngine:
    def __init__(self) -> None:
        self.argument_map = {
            "search": ["file <query>"],
            "sys": ["info"],
            "capability": ["file list <path>", "network interface_summary", "process list", "utility time"],
            "smart": ["cek koneksi lambat gak sih", "bersihin folder download"],
            "open": ["vscode", "notepad", "chrome"],
        }

    def autocorrect(self, raw: str, keywords: list[str]) -> AutoCorrection | None:
        clean = raw.strip()
        if not clean:
            return None

        tokens = clean.split()
        keyword = tokens[0].lower()
        if keyword in keywords:
            return None

        candidate, score = self._best_keyword_match(keyword, keywords)
        if candidate is None or score < 0.50:
            return None

        corrected = " ".join([candidate, *tokens[1:]])
        needs_confirmation = score < 0.92
        return AutoCorrection(clean, corrected, score, needs_confirmation)

    def argument_hints(self, raw: str) -> list[str]:
        first = raw.strip().split(" ")[0].lower() if raw.strip() else ""
        if not first:
            return []
        return self.argument_map.get(first, [])

    def explain(self, command: str) -> str:
        clean = command.strip()
        if not clean:
            return "Command kosong."
        keyword = clean.split(" ")[0].lower()
        hints = self.argument_map.get(keyword, [])
        if not hints:
            return f"Explain: command '{keyword}' akan dieksekusi sesuai contract aktif."
        joined = " | ".join(hints)
        return f"Explain: command '{keyword}' akan dieksekusi. Contoh argumen: {joined}"

    def _best_keyword_match(self, keyword: str, keywords: list[str]) -> tuple[str | None, float]:
        best_keyword = None
        best_score = 0.0
        for item in keywords:
            distance = self._levenshtein(keyword, item)
            scale = max(len(keyword), len(item), 1)
            score = 1.0 - (distance / scale)
            if score > best_score:
                best_keyword = item
                best_score = score
        return best_keyword, best_score

    def _levenshtein(self, left: str, right: str) -> int:
        if left == right:
            return 0
        if not left:
            return len(right)
        if not right:
            return len(left)

        previous = list(range(len(right) + 1))
        for i, left_char in enumerate(left, start=1):
            current = [i]
            for j, right_char in enumerate(right, start=1):
                insert_cost = current[j - 1] + 1
                delete_cost = previous[j] + 1
                replace_cost = previous[j - 1] + (left_char != right_char)
                current.append(min(insert_cost, delete_cost, replace_cost))
            previous = current
        return previous[-1]
