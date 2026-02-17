from __future__ import annotations

import getpass
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable
from uuid import uuid4

from core.capability_guardrail import CapabilityGuardrail
from core.capability_layer import SystemCapabilityLayer
from core.deployment_manager import ConfigMigrationManager, ProfileBackupManager, ReleaseChannelManager
from core.execution_profile import ExecutionProfilePolicy
from core.executor import ExecutionContext, UnifiedCommandExecutor, build_execution_timestamp
from core.intent_engine import LocalIntentEngine
from core.memory_engine import MemoryEngine
from core.observability import DiagnosticReporter, HealthMonitor, RecoveryManager, StructuredLogger
from core.plugin_registry import PluginRegistry
from core.safe_mode_policy import SafeModePolicy
from core.security_guard import SecurityGuard
from core.session import SessionLayer
from core.smart_assist import SmartAssistEngine
from core.system_intent_mapper import SystemIntentMapper
from modules.file_manager import FileManager
from modules.launcher import Launcher
from modules.system_actions import SystemActions
from modules.system_tools import SystemTools


@dataclass(frozen=True)
class ParsedCommand:
    keyword: str
    args: list[str]
    raw: str


@dataclass(frozen=True)
class CommandResult:
    message: str
    requires_confirmation: bool = False
    pending_command: str | None = None


@dataclass(frozen=True)
class CommandContract:
    keyword: str
    usage: str
    min_args: int = 0
    max_args: int | None = None
    first_arg_equals: str | None = None


@dataclass
class CommandRouter:
    launcher: Launcher | None = None
    file_manager: FileManager | None = None
    system_tools: SystemTools | None = None
    handlers: dict[str, Callable[[ParsedCommand], str]] | None = None
    contracts: dict[str, CommandContract] | None = None
    dangerous_keywords: set[str] | None = None
    safe_mode: bool = True
    pending_confirmation: ParsedCommand | None = None
    pending_autocorrect: str | None = None
    session_layer: SessionLayer | None = None
    safe_mode_policy: SafeModePolicy | None = None
    security_guard: SecurityGuard | None = None
    intent_engine: LocalIntentEngine | None = None
    memory_engine: MemoryEngine | None = None
    logger: StructuredLogger | None = None
    recovery_manager: RecoveryManager | None = None
    health_monitor: HealthMonitor | None = None
    diagnostic_reporter: DiagnosticReporter | None = None
    release_channel_manager: ReleaseChannelManager | None = None
    migration_manager: ConfigMigrationManager | None = None
    backup_manager: ProfileBackupManager | None = None
    executor: UnifiedCommandExecutor | None = None
    session_id: str | None = None
    capability_layer: SystemCapabilityLayer | None = None
    capability_guardrail: CapabilityGuardrail | None = None
    system_intent_mapper: SystemIntentMapper | None = None
    smart_assist: SmartAssistEngine | None = None
    system_actions: SystemActions | None = None
    execution_profile_policy: ExecutionProfilePolicy | None = None

    def __post_init__(self) -> None:
        self.launcher = self.launcher or Launcher()
        self.file_manager = self.file_manager or FileManager()
        self.system_tools = self.system_tools or SystemTools()
        self.handlers = {}
        self.contracts = {}
        self.dangerous_keywords = set()
        self.session_layer = self.session_layer or SessionLayer(session_name="router-session")
        self.safe_mode_policy = self.safe_mode_policy or SafeModePolicy()
        self.intent_engine = self.intent_engine or LocalIntentEngine()
        self.memory_engine = self.memory_engine or MemoryEngine()
        self.logger = self.logger or StructuredLogger()
        self.recovery_manager = self.recovery_manager or RecoveryManager()
        self.health_monitor = self.health_monitor or HealthMonitor()
        self.diagnostic_reporter = self.diagnostic_reporter or DiagnosticReporter()
        self.release_channel_manager = self.release_channel_manager or ReleaseChannelManager()
        self.migration_manager = self.migration_manager or ConfigMigrationManager()
        self.backup_manager = self.backup_manager or ProfileBackupManager()
        self.executor = self.executor or UnifiedCommandExecutor()
        self.capability_layer = self.capability_layer or SystemCapabilityLayer()
        self.capability_guardrail = self.capability_guardrail or CapabilityGuardrail(permission_tier="basic")
        self.system_intent_mapper = self.system_intent_mapper or SystemIntentMapper()
        self.smart_assist = self.smart_assist or SmartAssistEngine()
        self.system_actions = self.system_actions or SystemActions()
        self.execution_profile_policy = self.execution_profile_policy or ExecutionProfilePolicy(profile="power")
        self.session_id = self.session_id or uuid4().hex
        self._register_plugins()
        self.security_guard = self.security_guard or SecurityGuard(command_whitelist=set(self.contracts.keys()))

    def route(self, command: str) -> str:
        return self.execute(command).message

    def execute(self, command: str, dry_run: bool = False, allow_autocorrect: bool = True) -> CommandResult:
        if command.strip().lower().startswith("explain "):
            explain_target = command.strip()[8:]
            message = self.smart_assist.explain(explain_target)
            context = self._build_execution_context(command, dry_run=True)
            self._record_session(command, message, "success", context)
            return CommandResult(message)

        normalized = self._resolve_intent(command)
        normalized = self._normalize_shortcuts(normalized)
        correction = self._resolve_autocorrect(normalized, allow_autocorrect)
        if correction is not None:
            if correction.requires_confirmation:
                self.pending_autocorrect = correction.corrected
                message = f"Smart Assist correction suggested (confidence={correction.confidence:.2f}): {correction.corrected}"
                context = self._build_execution_context(command, dry_run=True)
                self._record_session(command, message, "pending_confirmation", context)
                return CommandResult(message, requires_confirmation=True, pending_command=correction.corrected)
            normalized = correction.corrected

        profile_block = self._apply_profile_policy(normalized)
        if profile_block is not None:
            return profile_block

        context = self._build_execution_context(normalized, dry_run=dry_run)
        envelope = self.executor.run(self, normalized, context)
        self._record_session(normalized or command, envelope.message, envelope.status, envelope.context)
        return self._to_command_result(envelope)

    def confirm_pending(self, approved: bool) -> CommandResult:
        if self.pending_autocorrect is not None:
            corrected = self.pending_autocorrect
            self.pending_autocorrect = None
            if not approved:
                cancelled = "Aksi dibatalkan oleh pengguna."
                context = self._build_execution_context("<confirm-autocorrect>", dry_run=True)
                self._record_session("<confirm-autocorrect>", cancelled, "cancelled", context)
                return CommandResult(cancelled)
            return self.execute(corrected, allow_autocorrect=False)

        context = self._build_execution_context("<confirm>", dry_run=False)
        envelope = self.executor.confirm(self, approved, context)
        self._record_session("<confirm>", envelope.message, envelope.status, envelope.context)
        return self._to_command_result(envelope)

    def execute_enveloped(self, command: str, dry_run: bool = False):
        normalized = self._resolve_intent(command)
        context = self._build_execution_context(normalized, dry_run=dry_run)
        envelope = self.executor.run(self, normalized, context)
        self._record_session(normalized or command, envelope.message, envelope.status, envelope.context)
        return envelope

    def parse(self, command: str) -> ParsedCommand | None:
        clean = command.strip()
        if not clean:
            return None
        tokens = clean.split()
        return ParsedCommand(tokens[0].lower(), tokens[1:], clean)

    def _handle_open(self, command: ParsedCommand) -> str:
        return self.launcher.open_app(" ".join(command.args))

    def _handle_search(self, command: ParsedCommand) -> str:
        query = " ".join(command.args[1:]).strip()
        return self.file_manager.search_file(query)

    def _handle_sys(self, command: ParsedCommand) -> str:
        return self.system_tools.system_info()

    def _handle_capability(self, command: ParsedCommand) -> str:
        if len(command.args) < 2:
            return "Format salah. Contoh: capability <domain> <action> [args]"
        domain, action = command.args[0], command.args[1]
        args = [self._expand_path(item) for item in command.args[2:]]
        decision = self.capability_guardrail.evaluate(domain, action, args)
        if not decision.allowed:
            return f"Guardrail blocked: {decision.reason}"
        preview = self.capability_layer.execute(domain, action, args)
        if decision.requires_confirmation:
            return f"Guardrail confirmation required. {decision.reason}\n{preview}"
        return preview

    def _handle_smart(self, command: ParsedCommand) -> str:
        request = " ".join(command.args).strip()
        if not request:
            return "Format salah. Contoh: smart <permintaan_user>"
        plan = self.system_intent_mapper.map_request(request)
        if plan is None:
            return "Belum ada mapping intent untuk request ini."
        lines = [f"Plan: {plan.title}", *[f"- {step}" for step in plan.steps]]
        for raw in plan.commands:
            parsed = self.parse(raw)
            if parsed is None:
                continue
            lines.append(f"> {raw}")
            lines.append(self._handle_capability(parsed))
        if plan.requires_confirmation:
            lines.append("Note: Plan ini perlu approval manual sebelum aksi destruktif.")
        return "\n".join(lines)

    def _handle_profile(self, command: ParsedCommand) -> str:
        target = command.args[0].lower()
        applied = self.execution_profile_policy.set_profile(target)
        return f"Execution profile aktif: {applied}"

    def _execute_dangerous(self, command: ParsedCommand) -> CommandResult:
        if self.safe_mode_policy.is_blocked(command.keyword):
            return CommandResult("Aksi ditolak oleh safe mode policy.")
        if command.keyword == "shutdown":
            return CommandResult(self.system_actions.shutdown_now())
        if command.keyword == "kill":
            target = " ".join(command.args)
            if not self.security_guard.is_process_target_allowed(target):
                return CommandResult("Kill process ditolak oleh process permission guard.")
            return CommandResult(self.system_actions.terminate_process(target))
        if command.keyword == "delete":
            target = " ".join(command.args)
            if not self.security_guard.is_path_allowed(target):
                return CommandResult("Delete ditolak oleh path restriction policy.")
            return CommandResult(self.system_actions.delete_path(target))
        return CommandResult("Aksi berbahaya tidak dikenali.")

    def _record_session(self, command: str, message: str, status: str, context: ExecutionContext | None = None) -> None:
        self.session_layer.record(command=command, message=message, status=status)
        self.memory_engine.record_command(command=command, status=status)
        level = "error" if status in {"invalid", "blocked", "failed"} else "info"
        metadata = {"command": command, "status": status}
        if context is not None:
            metadata["execution_context"] = asdict(context)
        self.logger.log(level=level, event="command", message=message, metadata=metadata)

    def _to_command_result(self, envelope) -> CommandResult:
        return CommandResult(envelope.message, envelope.requires_confirmation, envelope.pending_command)

    def _build_execution_context(self, command: str, dry_run: bool) -> ExecutionContext:
        parsed = self.parse(command)
        keyword = parsed.keyword if parsed is not None else ""
        risk_level = self.execution_profile_policy.risk_level(keyword)
        profile_policy = self.execution_profile_policy.profile
        return ExecutionContext(
            user=getpass.getuser(),
            profile_policy=profile_policy,
            session_id=self.session_id,
            timestamp=build_execution_timestamp(),
            risk_level=risk_level,
            dry_run=dry_run,
        )

    def _apply_profile_policy(self, normalized: str) -> CommandResult | None:
        parsed = self.parse(normalized)
        if parsed is None:
            return None

        decision = self.execution_profile_policy.evaluate(parsed.keyword)
        if decision.mode == "blocked":
            message = f"Execution profile blocked: {decision.reason}"
            self._record_session(normalized, message, "blocked", self._build_execution_context(normalized, dry_run=True))
            return CommandResult(message)

        if decision.mode == "explain":
            message = f"Execution profile explain-only: {parsed.raw}"
            self._record_session(normalized, message, "success", self._build_execution_context(normalized, dry_run=True))
            return CommandResult(message)

        if decision.requires_confirmation and not self.safe_mode and parsed.keyword in self.dangerous_keywords:
            self.pending_confirmation = parsed
            message = "Execution profile membutuhkan konfirmasi manual."
            self._record_session(normalized, message, "pending_confirmation", self._build_execution_context(normalized, dry_run=True))
            return CommandResult(message, requires_confirmation=True, pending_command=parsed.raw)

        return None

    def _resolve_autocorrect(self, normalized: str, allow_autocorrect: bool):
        if not allow_autocorrect:
            return None
        correction = self.smart_assist.autocorrect(normalized, list(self.contracts.keys()))
        if correction is None:
            return None
        if not correction.requires_confirmation:
            message = f"Smart Assist auto-applied -> {correction.corrected} (confidence={correction.confidence:.2f})"
            self._record_session(normalized, message, "intent_resolved")
        return correction

    def _expand_path(self, value: str) -> str:
        if value.startswith("~/"):
            return str(Path.home() / value[2:])
        return os.path.expandvars(value)

    def _normalize_shortcuts(self, normalized: str) -> str:
        parsed = self.parse(normalized)
        if parsed is None:
            return normalized
        if parsed.keyword == "search" and parsed.args and parsed.args[0].lower() != "file":
            query = " ".join(parsed.args).strip()
            return f"search file {query}"
        return normalized

    def memory_summary(self) -> dict:
        return {
            "top_commands": self.memory_engine.top_commands(limit=5),
            "persona": self.memory_engine.get_preference("persona", None),
        }

    def list_command_keywords(self) -> list[str]:
        return sorted(self.contracts.keys())

    def suggest_commands(self, raw_input: str, limit: int = 5) -> list[str]:
        typed = raw_input.strip().lower()
        usages = sorted(contract.usage for contract in self.contracts.values())
        if not typed:
            return usages[:limit]
        matched = [usage for usage in usages if usage.startswith(typed) or usage.split(" ")[0].startswith(typed)]
        return list(dict.fromkeys(matched))[:limit]

    def usage_hint(self, raw_input: str) -> str | None:
        command = raw_input.strip().split(" ")[0].lower() if raw_input.strip() else ""
        contract = self.contracts.get(command)
        return contract.usage if contract is not None else None

    def argument_hint(self, raw_input: str) -> str:
        return " | ".join(self.smart_assist.argument_hints(raw_input))

    def explain_intent(self, raw_input: str) -> str:
        text = raw_input.strip()
        if not text:
            return ""
        resolution = self.intent_engine.resolve(text, allowed_keywords=set(self.contracts.keys()))
        if resolution.resolved == text:
            return ""
        return f"Did you mean: {resolution.resolved}"

    def save_recovery_snapshot(self):
        entries = [item.__dict__ for item in self.session_layer.entries]
        return self.recovery_manager.save_snapshot("router-session", entries)

    def create_diagnostic_report(self):
        checks = self.health_monitor.run(self)
        recent_logs = self.logger.tail(limit=30)
        return self.diagnostic_reporter.generate(checks, recent_logs)

    def get_release_channel(self) -> str:
        return self.release_channel_manager.get_channel()

    def set_release_channel(self, channel: str) -> str:
        return self.release_channel_manager.set_channel(channel)

    def _register_plugins(self) -> None:
        registry = PluginRegistry(package_name="plugins")
        for item in registry.discover():
            self.contracts[item.keyword] = CommandContract(
                keyword=item.keyword,
                usage=item.usage,
                min_args=item.min_args,
                max_args=item.max_args,
                first_arg_equals=item.first_arg_equals,
            )
            if item.dangerous:
                self.dangerous_keywords.add(item.keyword)
                continue
            self.handlers[item.keyword] = getattr(self, item.handler_name)

    def _resolve_intent(self, raw_command: str) -> str:
        allowed = set(self.contracts.keys())
        resolution = self.intent_engine.resolve(raw_command, allowed_keywords=allowed)
        if resolution.reason.startswith("semantic"):
            message = f"Intent resolved -> {resolution.resolved} (confidence={resolution.confidence:.2f})"
            self._record_session(raw_command, message, "intent_resolved")
        return resolution.resolved
