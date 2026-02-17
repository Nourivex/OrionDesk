from __future__ import annotations

import getpass
from dataclasses import asdict, dataclass
from uuid import uuid4
from typing import Callable

from core.executor import ExecutionContext, UnifiedCommandExecutor, build_execution_timestamp
from core.deployment_manager import ConfigMigrationManager, ProfileBackupManager, ReleaseChannelManager
from core.intent_engine import LocalIntentEngine
from core.memory_engine import MemoryEngine
from core.observability import DiagnosticReporter, HealthMonitor, RecoveryManager, StructuredLogger
from core.plugin_registry import PluginRegistry
from core.safe_mode_policy import SafeModePolicy
from core.security_guard import SecurityGuard
from core.session import SessionLayer
from modules.file_manager import FileManager
from modules.launcher import Launcher
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

    def __post_init__(self) -> None:
        if self.launcher is None:
            self.launcher = Launcher()
        if self.file_manager is None:
            self.file_manager = FileManager()
        if self.system_tools is None:
            self.system_tools = SystemTools()
        self.handlers = {}
        self.contracts = {}
        self.dangerous_keywords = set()
        if self.session_layer is None:
            self.session_layer = SessionLayer(session_name="router-session")
        if self.safe_mode_policy is None:
            self.safe_mode_policy = SafeModePolicy()
        if self.intent_engine is None:
            self.intent_engine = LocalIntentEngine()
        if self.memory_engine is None:
            self.memory_engine = MemoryEngine()
        if self.logger is None:
            self.logger = StructuredLogger()
        if self.recovery_manager is None:
            self.recovery_manager = RecoveryManager()
        if self.health_monitor is None:
            self.health_monitor = HealthMonitor()
        if self.diagnostic_reporter is None:
            self.diagnostic_reporter = DiagnosticReporter()
        if self.release_channel_manager is None:
            self.release_channel_manager = ReleaseChannelManager()
        if self.migration_manager is None:
            self.migration_manager = ConfigMigrationManager()
        if self.backup_manager is None:
            self.backup_manager = ProfileBackupManager()
        if self.executor is None:
            self.executor = UnifiedCommandExecutor()
        if self.session_id is None:
            self.session_id = uuid4().hex
        self._register_plugins()
        if self.security_guard is None:
            self.security_guard = SecurityGuard(command_whitelist=set(self.contracts.keys()))

    def route(self, command: str) -> str:
        return self.execute(command).message

    def execute(self, command: str, dry_run: bool = False) -> CommandResult:
        normalized = self._resolve_intent(command)
        context = self._build_execution_context(normalized, dry_run=dry_run)
        envelope = self.executor.run(self, normalized, context)
        self._record_session(normalized or command, envelope.message, envelope.status, envelope.context)
        return self._to_command_result(envelope)

    def confirm_pending(self, approved: bool) -> CommandResult:
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
        clean_command = command.strip()
        if not clean_command:
            return None
        tokens = clean_command.split()
        return ParsedCommand(
            keyword=tokens[0].lower(),
            args=tokens[1:],
            raw=clean_command,
        )

    def _handle_open(self, command: ParsedCommand) -> str:
        app_alias = " ".join(command.args)
        return self.launcher.open_app(app_alias)

    def _handle_search(self, command: ParsedCommand) -> str:
        query = " ".join(command.args[1:]).strip()
        return self.file_manager.search_file(query)

    def _handle_sys(self, command: ParsedCommand) -> str:
        return self.system_tools.system_info()

    def _execute_dangerous(self, command: ParsedCommand) -> CommandResult:
        if self.safe_mode_policy.is_blocked(command.keyword):
            return CommandResult("Aksi ditolak oleh safe mode policy.")

        if command.keyword == "shutdown":
            return CommandResult("Simulasi shutdown dijalankan.")

        if command.keyword == "kill":
            target = " ".join(command.args)
            if not self.security_guard.is_process_target_allowed(target):
                return CommandResult("Kill process ditolak oleh process permission guard.")
            return CommandResult(f"Simulasi kill process untuk '{target}' dijalankan.")

        if command.keyword == "delete":
            target = " ".join(command.args)
            if not self.security_guard.is_path_allowed(target):
                return CommandResult("Delete ditolak oleh path restriction policy.")
            return CommandResult(f"Simulasi delete untuk '{target}' dijalankan.")

        return CommandResult("Aksi berbahaya tidak dikenali.")

    def _record_session(self, command: str, message: str, status: str, context: ExecutionContext | None = None) -> None:
        if self.session_layer is None:
            return
        self.session_layer.record(command=command, message=message, status=status)
        if self.memory_engine is not None:
            self.memory_engine.record_command(command=command, status=status)
        if self.logger is not None:
            level = "error" if status in {"invalid", "blocked", "failed"} else "info"
            metadata = {"command": command, "status": status}
            if context is not None:
                metadata["execution_context"] = asdict(context)
            self.logger.log(level=level, event="command", message=message, metadata=metadata)

    def _to_command_result(self, envelope) -> CommandResult:
        return CommandResult(
            message=envelope.message,
            requires_confirmation=envelope.requires_confirmation,
            pending_command=envelope.pending_command,
        )

    def _build_execution_context(self, command: str, dry_run: bool) -> ExecutionContext:
        parsed = self.parse(command)
        risk_level = "low"
        if parsed is not None and parsed.keyword in self.dangerous_keywords:
            risk_level = "high"
        profile_policy = "strict" if self.safe_mode else "power"
        return ExecutionContext(
            user=getpass.getuser(),
            profile_policy=profile_policy,
            session_id=self.session_id or "router-session",
            timestamp=build_execution_timestamp(),
            risk_level=risk_level,
            dry_run=dry_run,
        )

    def memory_summary(self) -> dict:
        if self.memory_engine is None:
            return {"top_commands": [], "persona": None}
        return {
            "top_commands": self.memory_engine.top_commands(limit=5),
            "persona": self.memory_engine.get_preference("persona", None),
        }

    def list_command_keywords(self) -> list[str]:
        return sorted(self.contracts.keys())

    def suggest_commands(self, raw_input: str, limit: int = 5) -> list[str]:
        typed = raw_input.strip().lower()
        usages = [contract.usage for contract in self.contracts.values()]
        if not typed:
            return sorted(usages)[:limit]

        matched: list[str] = []
        for usage in sorted(usages):
            if usage.startswith(typed):
                matched.append(usage)
            elif usage.split(" ")[0].startswith(typed):
                matched.append(usage)

        seen: set[str] = set()
        unique = []
        for item in matched:
            if item in seen:
                continue
            seen.add(item)
            unique.append(item)
        return unique[:limit]

    def usage_hint(self, raw_input: str) -> str | None:
        command = raw_input.strip().split(" ")[0].lower() if raw_input.strip() else ""
        if not command:
            return None
        contract = self.contracts.get(command)
        if contract is None:
            return None
        return contract.usage

    def explain_intent(self, raw_input: str) -> str:
        text = raw_input.strip()
        if not text:
            return ""
        if self.intent_engine is None:
            return ""
        resolution = self.intent_engine.resolve(text, allowed_keywords=set(self.contracts.keys()))
        if resolution.resolved == text:
            return ""
        return f"Did you mean: {resolution.resolved}"

    def save_recovery_snapshot(self):
        if self.recovery_manager is None or self.session_layer is None:
            return None
        entries = [item.__dict__ for item in self.session_layer.entries]
        return self.recovery_manager.save_snapshot("router-session", entries)

    def create_diagnostic_report(self):
        if self.health_monitor is None or self.diagnostic_reporter is None or self.logger is None:
            return None
        checks = self.health_monitor.run(self)
        recent_logs = self.logger.tail(limit=30)
        return self.diagnostic_reporter.generate(checks, recent_logs)

    def get_release_channel(self) -> str:
        if self.release_channel_manager is None:
            return "stable"
        return self.release_channel_manager.get_channel()

    def set_release_channel(self, channel: str) -> str:
        if self.release_channel_manager is None:
            return channel
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

            handler = getattr(self, item.handler_name)
            self.handlers[item.keyword] = handler

    def _resolve_intent(self, raw_command: str) -> str:
        if self.intent_engine is None:
            return raw_command

        allowed = set(self.contracts.keys())
        resolution = self.intent_engine.resolve(raw_command, allowed_keywords=allowed)
        if resolution.reason.startswith("semantic"):
            self._record_session(
                raw_command,
                f"Intent resolved -> {resolution.resolved} (confidence={resolution.confidence:.2f})",
                "intent_resolved",
            )
        return resolution.resolved