from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class IntentStep:
    step_id: str
    step_type: str
    raw_input: str
    resolved_command: str
    depends_on: list[str]
    reason: str


@dataclass(frozen=True)
class IntentGraph:
    title: str
    confidence: float
    steps: list[IntentStep]

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "confidence": round(self.confidence, 4),
            "steps": [
                {
                    "step_id": step.step_id,
                    "step_type": step.step_type,
                    "raw_input": step.raw_input,
                    "resolved_command": step.resolved_command,
                    "depends_on": step.depends_on,
                    "reason": step.reason,
                }
                for step in self.steps
            ],
        }


class IntentGraphPlanner:
    def __init__(self) -> None:
        self._type_map = {
            "search": "read",
            "sys": "analyze",
            "capability": "execute",
            "open": "execute",
            "smart": "analyze",
            "profile": "verify",
            "clip": "execute",
            "mode": "execute",
            "net": "analyze",
        }

    def build(self, raw_input: str, resolve_intent: Callable[[str], object]) -> IntentGraph:
        segments = self._split_steps(raw_input)
        steps: list[IntentStep] = []
        confidence_total = 0.0

        for index, segment in enumerate(segments):
            resolved = resolve_intent(segment)
            resolved_command = getattr(resolved, "resolved", segment).strip()
            confidence = float(getattr(resolved, "confidence", 0.0))
            reason_source = getattr(resolved, "reason", "rule-match")
            confidence_total += confidence

            keyword = resolved_command.split(" ")[0].lower() if resolved_command else "open"
            step_type = self._type_map.get(keyword, "execute")
            step_id = f"S{index + 1}"
            depends_on = [] if index == 0 else [f"S{index}"]
            reason = f"{segment} -> {resolved_command} ({reason_source}, confidence={confidence:.2f})"
            steps.append(
                IntentStep(
                    step_id=step_id,
                    step_type=step_type,
                    raw_input=segment,
                    resolved_command=resolved_command,
                    depends_on=depends_on,
                    reason=reason,
                )
            )

        confidence_avg = confidence_total / len(steps) if steps else 0.0
        title = f"Multi-step intent plan ({len(steps)} steps)"
        return IntentGraph(title=title, confidence=confidence_avg, steps=steps)

    def _split_steps(self, text: str) -> list[str]:
        clean = text.strip()
        if not clean:
            return []

        normalized = (
            clean.replace(";", "|")
            .replace(" kemudian ", "|")
            .replace(" lalu ", "|")
            .replace(" and then ", "|")
        )
        segments = [item.strip() for item in normalized.split("|") if item.strip()]
        return segments or [clean]
