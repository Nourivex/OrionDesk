from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str = ""


@dataclass
class CapabilityGuardrail:
    permission_tier: str = "basic"
    protected_processes: set[str] = field(
        default_factory=lambda: {"explorer.exe", "winlogon.exe", "lsass.exe", "csrss.exe"}
    )

    def evaluate(self, domain: str, action: str, args: list[str]) -> GuardrailDecision:
        lowered_domain = domain.lower()
        lowered_action = action.lower()
        if lowered_domain == "process" and lowered_action == "terminate":
            return self._evaluate_terminate(args)
        if lowered_domain == "file" and lowered_action in {"delete", "move"}:
            return self._evaluate_destructive_file_action()
        return GuardrailDecision(True, False, "")

    def _evaluate_terminate(self, args: list[str]) -> GuardrailDecision:
        target = " ".join(args).strip().lower()
        if target in self.protected_processes:
            return GuardrailDecision(False, True, "Target process termasuk protected process list.")
        if self.permission_tier == "basic":
            return GuardrailDecision(False, True, "Permission tier basic tidak boleh terminate process.")
        return GuardrailDecision(True, True, "Terminate process butuh konfirmasi manual.")

    def _evaluate_destructive_file_action(self) -> GuardrailDecision:
        if self.permission_tier == "basic":
            return GuardrailDecision(False, True, "Permission tier basic hanya boleh preview action file berisiko.")
        return GuardrailDecision(True, True, "Aksi file berisiko butuh konfirmasi manual.")
