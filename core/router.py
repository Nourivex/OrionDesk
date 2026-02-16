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


@dataclass
class CommandRouter:
    launcher: Launcher | None = None
    file_manager: FileManager | None = None
    system_tools: SystemTools | None = None
    handlers: dict[str, Callable[[ParsedCommand], str]] | None = None

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

    def route(self, command: str) -> str:
        parsed = self.parse(command)
        if parsed is None:
            return "Perintah kosong. Silakan isi command terlebih dahulu."

        handler = self.handlers.get(parsed.keyword)
        if handler is None:
            return "Perintah tidak dikenali. Gunakan: open, search file, atau sys info."
        return handler(parsed)

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
        if len(command.args) < 1:
            return "Format salah. Contoh: open vscode"
        app_alias = " ".join(command.args)
        return self.launcher.open_app(app_alias)

    def _handle_search(self, command: ParsedCommand) -> str:
        if len(command.args) < 2 or command.args[0].lower() != "file":
            return "Format salah. Contoh: search file report.pdf"
        query = " ".join(command.args[1:]).strip()
        if not query:
            return "Format salah. Contoh: search file report.pdf"
        return self.file_manager.search_file(query)

    def _handle_sys(self, command: ParsedCommand) -> str:
        if len(command.args) >= 1 and command.args[0].lower() == "info":
            return self.system_tools.system_info()
        return "Format salah. Contoh: sys info"