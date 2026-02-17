from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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
    safe_mode: bool = True
    pending_confirmation: ParsedCommand | None = None

    def __post_init__(self) -> None:
        if self.launcher is None:
            self.launcher = Launcher()
        if self.file_manager is None:
            self.file_manager = FileManager()
        if self.system_tools is None:
            self.system_tools = SystemTools()
        self.handlers = {
            "open": self._handle_open,
            "search": self._handle_search,
            "sys": self._handle_sys,
        }
        self.contracts = {
            "open": CommandContract(
                keyword="open",
                usage="open <app_alias>",
                min_args=1,
            ),
            "search": CommandContract(
                keyword="search",
                usage="search file <query>",
                min_args=2,
                first_arg_equals="file",
            ),
            "sys": CommandContract(
                keyword="sys",
                usage="sys info",
                min_args=1,
                max_args=1,
                first_arg_equals="info",
            ),
            "delete": CommandContract(
                keyword="delete",
                usage="delete <path>",
                min_args=1,
            ),
            "kill": CommandContract(
                keyword="kill",
                usage="kill <process_name_or_pid>",
                min_args=1,
            ),
            "shutdown": CommandContract(
                keyword="shutdown",
                usage="shutdown",
                min_args=0,
                max_args=0,
            ),
        }

    def route(self, command: str) -> str:
        return self.execute(command).message

    def execute(self, command: str) -> CommandResult:
        parsed = self.parse(command)
        if parsed is None:
            return CommandResult("Perintah kosong. Silakan isi command terlebih dahulu.")

        if len(parsed.raw) > 300:
            return CommandResult("Perintah terlalu panjang. Batas maksimal 300 karakter.")

        validation = self._validate_contract(parsed)
        if validation is not None:
            return validation

        if self._is_dangerous(parsed.keyword):
            if self.safe_mode:
                self.pending_confirmation = parsed
                return CommandResult(
                    "Safe Mode aktif. Aksi ini membutuhkan konfirmasi manual.",
                    requires_confirmation=True,
                    pending_command=parsed.raw,
                )
            return self._execute_dangerous(parsed)

        handler = self.handlers.get(parsed.keyword)
        if handler is None:
            return CommandResult("Perintah tidak dikenali. Gunakan: open, search file, atau sys info.")
        return CommandResult(handler(parsed))

    def confirm_pending(self, approved: bool) -> CommandResult:
        if self.pending_confirmation is None:
            return CommandResult("Tidak ada aksi yang menunggu konfirmasi.")

        command = self.pending_confirmation
        self.pending_confirmation = None
        if not approved:
            return CommandResult("Aksi dibatalkan oleh pengguna.")
        return self._execute_dangerous(command)

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
        return keyword in {"delete", "kill", "shutdown"}

    def _execute_dangerous(self, command: ParsedCommand) -> CommandResult:
        if command.keyword == "shutdown":
            return CommandResult("Simulasi shutdown dijalankan.")

        if command.keyword == "kill":
            target = " ".join(command.args)
            return CommandResult(f"Simulasi kill process untuk '{target}' dijalankan.")

        if command.keyword == "delete":
            target = " ".join(command.args)
            return CommandResult(f"Simulasi delete untuk '{target}' dijalankan.")

        return CommandResult("Aksi berbahaya tidak dikenali.")

    def _validate_contract(self, command: ParsedCommand) -> CommandResult | None:
        contract = self.contracts.get(command.keyword)
        if contract is None:
            return CommandResult(
                "Perintah tidak dikenali. Gunakan command yang terdaftar: "
                "open, search file, sys info, delete, kill, shutdown."
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