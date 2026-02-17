from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class ErrorCode(StrEnum):
    NONE = "none"
    EMPTY_COMMAND = "empty_command"
    COMMAND_TOO_LONG = "command_too_long"
    COMMAND_BLOCKED = "command_blocked"
    CONTRACT_INVALID = "contract_invalid"
    SAFE_MODE_BLOCKED = "safe_mode_blocked"
    CONFIRMATION_REQUIRED = "confirmation_required"
    UNKNOWN_HANDLER = "unknown_handler"


@dataclass(frozen=True)
class ExecutionContext:
    user: str
    profile_policy: str
    session_id: str
    timestamp: str
    risk_level: str
    dry_run: bool


@dataclass(frozen=True)
class ResponseEnvelope:
    ok: bool
    status: str
    message: str
    error_code: ErrorCode = ErrorCode.NONE
    requires_confirmation: bool = False
    pending_command: str | None = None
    context: ExecutionContext | None = None


class UnifiedCommandExecutor:
    def run(self, router, command: str, context: ExecutionContext) -> ResponseEnvelope:
        parsed = router.parse(command)
        if parsed is None:
            return self._result(False, "invalid", "Perintah kosong. Silakan isi command terlebih dahulu.", ErrorCode.EMPTY_COMMAND, context)

        if len(parsed.raw) > 300:
            return self._result(False, "invalid", "Perintah terlalu panjang. Batas maksimal 300 karakter.", ErrorCode.COMMAND_TOO_LONG, context)

        if not router.security_guard.is_command_allowed(parsed.keyword):
            return self._result(False, "blocked", "Perintah ditolak oleh command whitelist policy.", ErrorCode.COMMAND_BLOCKED, context)

        usage_error = self._validate_contract(router.contracts, parsed.keyword, parsed.args)
        if usage_error is not None:
            return self._result(False, "invalid", usage_error, ErrorCode.CONTRACT_INVALID, context)

        if parsed.keyword in router.dangerous_keywords:
            return self._run_dangerous(router, parsed, context)

        handler = router.handlers.get(parsed.keyword)
        if handler is None:
            return self._result(False, "invalid", "Perintah tidak dikenali. Gunakan: open, search file, atau sys info.", ErrorCode.UNKNOWN_HANDLER, context)
        return self._result(True, "success", handler(parsed), ErrorCode.NONE, context)

    def confirm(self, router, approved: bool, context: ExecutionContext) -> ResponseEnvelope:
        if router.pending_confirmation is None:
            return self._result(False, "invalid", "Tidak ada aksi yang menunggu konfirmasi.", ErrorCode.CONTRACT_INVALID, context)

        command = router.pending_confirmation
        router.pending_confirmation = None
        if not approved:
            return self._result(False, "cancelled", "Aksi dibatalkan oleh pengguna.", ErrorCode.NONE, context)

        result = router._execute_dangerous(command)
        return self._result(True, "success", result.message, ErrorCode.NONE, context)

    def _run_dangerous(self, router, parsed, context: ExecutionContext) -> ResponseEnvelope:
        if router.safe_mode_policy.is_blocked(parsed.keyword):
            return self._result(False, "blocked", "Aksi ditolak oleh safe mode policy.", ErrorCode.SAFE_MODE_BLOCKED, context)

        if router.safe_mode and router.safe_mode_policy.requires_confirmation(parsed.keyword):
            router.pending_confirmation = parsed
            return self._result(
                False,
                "pending_confirmation",
                "Safe Mode aktif. Aksi ini membutuhkan konfirmasi manual.",
                ErrorCode.CONFIRMATION_REQUIRED,
                context,
                requires_confirmation=True,
                pending_command=parsed.raw,
            )

        result = router._execute_dangerous(parsed)
        return self._result(True, "success", result.message, ErrorCode.NONE, context)

    def _validate_contract(self, contracts, keyword: str, args: list[str]) -> str | None:
        contract = contracts.get(keyword)
        if contract is None:
            allowed = ", ".join(sorted(contracts.keys()))
            return f"Perintah tidak dikenali. Gunakan command yang terdaftar: {allowed}."

        count = len(args)
        if count < contract.min_args:
            return f"Format salah. Contoh: {contract.usage}"
        if contract.max_args is not None and count > contract.max_args:
            return f"Format salah. Contoh: {contract.usage}"

        if contract.first_arg_equals is None:
            return None
        first_arg = args[0].lower() if args else ""
        if first_arg == contract.first_arg_equals:
            return None
        return f"Format salah. Contoh: {contract.usage}"

    def _result(
        self,
        ok: bool,
        status: str,
        message: str,
        error_code: ErrorCode,
        context: ExecutionContext,
        requires_confirmation: bool = False,
        pending_command: str | None = None,
    ) -> ResponseEnvelope:
        return ResponseEnvelope(
            ok=ok,
            status=status,
            message=message,
            error_code=error_code,
            requires_confirmation=requires_confirmation,
            pending_command=pending_command,
            context=context,
        )


def build_execution_timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")
