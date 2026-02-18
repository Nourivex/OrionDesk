from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ReasoningDecision:
    step_id: str
    command: str
    confidence: float
    mode: str
    risk_level: str
    reason: str


@dataclass(frozen=True)
class ReasoningPlan:
    overall_confidence: float
    decisions: list[ReasoningDecision]
    fallback_used: bool

    def to_dict(self) -> dict:
        return {
            "overall_confidence": round(self.overall_confidence, 4),
            "fallback_used": self.fallback_used,
            "decisions": [
                {
                    "step_id": item.step_id,
                    "command": item.command,
                    "confidence": round(item.confidence, 4),
                    "mode": item.mode,
                    "risk_level": item.risk_level,
                    "reason": item.reason,
                }
                for item in self.decisions
            ],
        }


class ComplexReasoningEngine:
    def __init__(self, min_confidence: float = 0.45) -> None:
        self.min_confidence = min_confidence

    def build_plan(
        self,
        graph_payload: dict,
        embed_text: Callable[[str], list[float]],
        risk_level: Callable[[str], str],
    ) -> ReasoningPlan:
        decisions: list[ReasoningDecision] = []
        fallback_used = False
        confidence_total = 0.0

        for step in graph_payload.get("steps", []):
            command = step.get("resolved_command", "").strip()
            keyword = command.split(" ")[0].lower() if command else "open"
            level = risk_level(keyword)
            confidence = self._extract_confidence(step.get("reason", ""))
            confidence = self._apply_semantic_bonus(confidence, embed_text(command))

            mode = "execute"
            reason = "reasoning confidence valid"
            if confidence < self.min_confidence:
                mode = "fallback"
                fallback_used = True
                reason = "low confidence, fallback to explain"
                command = f"explain {command}" if command else "explain"

            if level in {"high", "critical"} and confidence < 0.6:
                mode = "pruned"
                reason = "high-risk step pruned due low confidence"

            confidence_total += confidence
            decisions.append(
                ReasoningDecision(
                    step_id=step.get("step_id", "S?"),
                    command=command,
                    confidence=confidence,
                    mode=mode,
                    risk_level=level,
                    reason=reason,
                )
            )

        overall = confidence_total / len(decisions) if decisions else 0.0
        return ReasoningPlan(overall_confidence=overall, decisions=decisions, fallback_used=fallback_used)

    def _extract_confidence(self, reason: str) -> float:
        marker = "confidence="
        if marker not in reason:
            return 0.5
        tail = reason.split(marker, maxsplit=1)[1]
        number_text = "".join(char for char in tail if char.isdigit() or char == ".")
        if not number_text:
            return 0.5
        return max(0.0, min(1.0, float(number_text)))

    def _apply_semantic_bonus(self, confidence: float, embedding: list[float]) -> float:
        if not embedding:
            return max(0.0, confidence - 0.08)
        return min(1.0, confidence + 0.05)
