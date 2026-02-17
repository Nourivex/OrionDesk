from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SecurityGuard:
    command_whitelist: set[str] = field(default_factory=set)
    allowed_delete_roots: list[Path] = field(default_factory=lambda: [Path.home(), Path.cwd()])
    protected_process_names: set[str] = field(
        default_factory=lambda: {
            "system",
            "system idle process",
            "wininit.exe",
            "csrss.exe",
            "lsass.exe",
            "services.exe",
        }
    )
    protected_pids: set[int] = field(default_factory=lambda: {0, 4})

    def is_command_allowed(self, keyword: str) -> bool:
        return keyword in self.command_whitelist

    def is_path_allowed(self, target: str) -> bool:
        normalized_target = Path(target).expanduser().resolve(strict=False)
        for root in self.allowed_delete_roots:
            normalized_root = root.expanduser().resolve(strict=False)
            if normalized_target == normalized_root:
                return True
            if normalized_root in normalized_target.parents:
                return True
        return False

    def is_process_target_allowed(self, target: str) -> bool:
        clean_target = target.strip().lower()
        if not clean_target:
            return False

        if clean_target.isdigit():
            return int(clean_target) not in self.protected_pids
        return clean_target not in self.protected_process_names
