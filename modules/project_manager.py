from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectManager:
    roots: list[Path] = field(default_factory=lambda: [Path.home()])
    projects: dict[str, Path] = field(default_factory=dict)

    def register(self, name: str, path: Path) -> None:
        self.projects[name.lower()] = path

    def open_project(self, name: str) -> str:
        key = name.strip().lower()
        if not key:
            return "Format salah. Contoh: proj open <name>"

        target = self.projects.get(key)
        if target is None:
            target = self._discover(key)
        if target is None:
            return f"Project '{name}' tidak ditemukan."
        return f"Project '{key}' siap dibuka: {target}"

    def _discover(self, key: str) -> Path | None:
        for root in self.roots:
            if not root.exists() or not root.is_dir():
                continue
            for child in root.iterdir():
                if child.is_dir() and child.name.lower() == key:
                    self.projects[key] = child
                    return child
        return None
