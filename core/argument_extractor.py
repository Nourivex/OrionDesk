from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArgumentExtraction:
    command: str
    keyword: str
    args: list[str]
    target: str | None
    path: str | None
    mode: str | None
    flags: list[str]

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "keyword": self.keyword,
            "args": self.args,
            "target": self.target,
            "path": self.path,
            "mode": self.mode,
            "flags": self.flags,
        }


class ArgumentExtractor:
    def extract(self, command: str) -> ArgumentExtraction:
        clean = command.strip()
        tokens = clean.split()
        keyword = tokens[0].lower() if tokens else ""
        args = tokens[1:] if len(tokens) > 1 else []

        target = None
        path = None
        mode = None
        flags = [item for item in args if item.startswith("-")]

        if keyword in {"open", "kill", "delete", "search"} and args:
            target = " ".join(item for item in args if not item.startswith("-"))
        if keyword in {"delete", "search"} and target:
            path = target
        if keyword == "mode" and args:
            mode = args[0].lower()

        return ArgumentExtraction(
            command=clean,
            keyword=keyword,
            args=args,
            target=target,
            path=path,
            mode=mode,
            flags=flags,
        )

    def extract_many(self, commands: list[str]) -> list[dict]:
        return [self.extract(command).to_dict() for command in commands]
