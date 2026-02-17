from dataclasses import dataclass, field
import subprocess
import time

import psutil


@dataclass
class Launcher:
    alias_map: dict[str, str] = field(
        default_factory=lambda: {
            "vscode": "code",
            "chrome": "chrome",
            "notepad": "notepad",
        }
    )

    def open_app(self, alias: str) -> str:
        clean_alias = alias.strip().lower()
        if not clean_alias:
            return "Alias aplikasi kosong."

        if clean_alias not in self.alias_map:
            return f"Aplikasi '{alias}' belum terdaftar pada alias map."

        resolved_name = self.alias_map[clean_alias]
        try:
            process = subprocess.Popen([resolved_name], shell=False)
        except OSError as error:
            return f"Gagal membuka '{clean_alias}': {error}"

        reported_pid = process.pid
        time.sleep(0.25)
        if process.poll() is not None:
            fallback_pid = self._find_latest_pid(clean_alias, resolved_name)
            if fallback_pid is not None:
                reported_pid = fallback_pid

        return (
            f"Membuka '{clean_alias}' menggunakan '{resolved_name}'. "
            f"PID: {reported_pid}."
        )

    def _find_latest_pid(self, alias: str, resolved_name: str) -> int | None:
        candidates = {alias.lower(), resolved_name.lower(), f"{alias.lower()}.exe", f"{resolved_name.lower()}.exe"}
        latest_pid = None
        latest_start = -1.0

        for proc in psutil.process_iter(["pid", "name", "create_time"]):
            name = (proc.info.get("name") or "").lower()
            if name not in candidates:
                continue
            created = float(proc.info.get("create_time") or 0.0)
            if created > latest_start:
                latest_start = created
                latest_pid = int(proc.info.get("pid") or 0)
        return latest_pid