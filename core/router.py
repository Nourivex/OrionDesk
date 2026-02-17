from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from core.intent_engine import LocalIntentEngine
from core.memory_engine import MemoryEngine
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
        self._register_plugins()
        if self.security_guard is None:
            self.security_guard = SecurityGuard(command_whitelist=set(self.contracts.keys()))

    def route(self, command: str) -> str:
        return self.execute(command).message

    def execute(self, command: str) -> CommandResult:
        normalized = self._resolve_intent(command)
        parsed = self.parse(normalized)
        if parsed is None:
            result = CommandResult("Perintah kosong. Silakan isi command terlebih dahulu.")
            self._record_session(command, result.message, "invalid")
            return result

        if len(parsed.raw) > 300:
            result = CommandResult("Perintah terlalu panjang. Batas maksimal 300 karakter.")
            self._record_session(parsed.raw, result.message, "invalid")
            return result

        if not self.security_guard.is_command_allowed(parsed.keyword):
            result = CommandResult("Perintah ditolak oleh command whitelist policy.")
            self._record_session(parsed.raw, result.message, "blocked")
            return result

        validation = self._validate_contract(parsed)
        if validation is not None:
            self._record_session(parsed.raw, validation.message, "invalid")
            return validation

        if self._is_dangerous(parsed.keyword):
            if self.safe_mode_policy.is_blocked(parsed.keyword):
                result = CommandResult("Aksi ditolak oleh safe mode policy.")
                self._record_session(parsed.raw, result.message, "blocked")
                return result

            if self.safe_mode:
                if not self.safe_mode_policy.requires_confirmation(parsed.keyword):
                    result = self._execute_dangerous(parsed)
                    self._record_session(parsed.raw, result.message, "success")
                    return result
                self.pending_confirmation = parsed
                result = CommandResult(
                    "Safe Mode aktif. Aksi ini membutuhkan konfirmasi manual.",
                    requires_confirmation=True,
                    pending_command=parsed.raw,
                )
                self._record_session(parsed.raw, result.message, "pending_confirmation")
                return result
            result = self._execute_dangerous(parsed)
            self._record_session(parsed.raw, result.message, "success")
            return result

        handler = self.handlers.get(parsed.keyword)
        if handler is None:
            result = CommandResult("Perintah tidak dikenali. Gunakan: open, search file, atau sys info.")
            self._record_session(parsed.raw, result.message, "invalid")
            return result
        result = CommandResult(handler(parsed))
        self._record_session(parsed.raw, result.message, "success")
        return result

    def confirm_pending(self, approved: bool) -> CommandResult:
        if self.pending_confirmation is None:
            result = CommandResult("Tidak ada aksi yang menunggu konfirmasi.")
            self._record_session("<confirm>", result.message, "invalid")
            return result

        command = self.pending_confirmation
        self.pending_confirmation = None
        if not approved:
            result = CommandResult("Aksi dibatalkan oleh pengguna.")
            self._record_session(command.raw, result.message, "cancelled")
            return result
        result = self._execute_dangerous(command)
        self._record_session(command.raw, result.message, "success")
        return result

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

    def _is_dangerous(self, keyword: str) -> bool:
        return keyword in self.dangerous_keywords

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

    def _validate_contract(self, command: ParsedCommand) -> CommandResult | None:
        contract = self.contracts.get(command.keyword)
        if contract is None:
            allowed = ", ".join(sorted(self.contracts.keys()))
            return CommandResult(
                f"Perintah tidak dikenali. Gunakan command yang terdaftar: {allowed}."
            )

        arg_count = len(command.args)
        if arg_count < contract.min_args:
            return CommandResult(f"Format salah. Contoh: {contract.usage}")

        if contract.max_args is not None and arg_count > contract.max_args:
            return CommandResult(f"Format salah. Contoh: {contract.usage}")

        if contract.first_arg_equals is None:
            return None

        first_arg = command.args[0].lower() if command.args else ""
        if first_arg != contract.first_arg_equals:
            return CommandResult(f"Format salah. Contoh: {contract.usage}")
        return None

    def _record_session(self, command: str, message: str, status: str) -> None:
        if self.session_layer is None:
            return
        self.session_layer.record(command=command, message=message, status=status)
        if self.memory_engine is not None:
            self.memory_engine.record_command(command=command, status=status)

    def memory_summary(self) -> dict:
        if self.memory_engine is None:
            return {"top_commands": [], "persona": None}
        return {
            "top_commands": self.memory_engine.top_commands(limit=5),
            "persona": self.memory_engine.get_preference("persona", None),
        }

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