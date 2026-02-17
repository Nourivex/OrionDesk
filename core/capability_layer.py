from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import psutil


@dataclass
class SystemCapabilityLayer:
    def execute(self, domain: str, action: str, args: list[str]) -> str:
        lowered_domain = domain.lower()
        lowered_action = action.lower()
        if lowered_domain == "file":
            return self._run_file(lowered_action, args)
        if lowered_domain == "process":
            return self._run_process(lowered_action, args)
        if lowered_domain == "network":
            return self._run_network(lowered_action, args)
        if lowered_domain == "utility":
            return self._run_utility(lowered_action, args)
        return "Capability domain tidak dikenali. Gunakan: file, process, network, utility."

    def _run_file(self, action: str, args: list[str]) -> str:
        target = Path(args[0]) if args else Path.cwd()
        if action == "list":
            if not target.exists() or not target.is_dir():
                return f"Folder tidak ditemukan: {target}"
            items = sorted(item.name for item in target.iterdir())[:15]
            return "File List:\n- " + "\n- ".join(items) if items else "Folder kosong."

        if action == "read":
            if not target.exists() or not target.is_file():
                return f"File tidak ditemukan: {target}"
            text = target.read_text(encoding="utf-8", errors="ignore")
            preview = text[:600].strip() or "(file kosong)"
            return f"File Preview ({target.name}):\n{preview}"

        if action == "hash":
            if not target.exists() or not target.is_file():
                return f"File tidak ditemukan: {target}"
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            return f"SHA256 {target.name}: {digest}"

        if action == "preview_cleanup":
            return self._preview_cleanup(target)

        return "File action tidak dikenali. Gunakan: list, read, hash, preview_cleanup."

    def _preview_cleanup(self, folder: Path) -> str:
        if not folder.exists() or not folder.is_dir():
            return f"Folder tidak ditemukan: {folder}"

        files = [item for item in folder.iterdir() if item.is_file()]
        large_files = sorted(files, key=lambda item: item.stat().st_size, reverse=True)[:5]
        duplicates = self._find_duplicates(files)

        large_lines = [f"{item.name} ({item.stat().st_size // 1024} KB)" for item in large_files]
        duplicate_lines = [", ".join(group) for group in duplicates[:5]]

        lines = [
            f"Cleanup Preview: {folder}",
            "Large files:",
            *(large_lines or ["(none)"]),
            "Duplicate candidates:",
            *(duplicate_lines or ["(none)"]),
            "No destructive action executed. Gunakan approval sebelum move/delete.",
        ]
        return "\n".join(lines)

    def _find_duplicates(self, files: list[Path]) -> list[list[str]]:
        bucket: dict[tuple[int, str], list[str]] = {}
        for item in files:
            size = item.stat().st_size
            key = (size, item.suffix.lower())
            bucket.setdefault(key, []).append(item.name)
        return [names for names in bucket.values() if len(names) > 1]

    def _run_process(self, action: str, args: list[str]) -> str:
        if action == "list":
            names = sorted({proc.info.get("name", "") for proc in psutil.process_iter(["name"])})
            filtered = [name for name in names if name][:20]
            return "Process List:\n- " + "\n- ".join(filtered) if filtered else "Tidak ada data process."

        if action == "detail":
            target = " ".join(args).strip().lower()
            for proc in psutil.process_iter(["pid", "name", "memory_info"]):
                name = (proc.info.get("name") or "").lower()
                pid = str(proc.info.get("pid", ""))
                if target and target not in {name, pid}:
                    continue
                memory = getattr(proc.info.get("memory_info"), "rss", 0)
                return f"Process Detail: {proc.info.get('name')} (pid={pid}, rss={memory // 1024} KB)"
            return "Process tidak ditemukan."

        if action == "terminate":
            target = " ".join(args).strip()
            return f"Terminate Preview: '{target}' tidak dieksekusi. Butuh konfirmasi policy."

        return "Process action tidak dikenali. Gunakan: list, detail, terminate."

    def _run_network(self, action: str, args: list[str]) -> str:
        if action == "ping":
            host = args[0] if args else "google.com"
            return f"Network Preview: ping {host} (simulasi aman)."

        if action == "interface_summary":
            stats = psutil.net_if_stats()
            lines = []
            for name, detail in list(stats.items())[:10]:
                status = "up" if detail.isup else "down"
                lines.append(f"{name}: {status}, speed={detail.speed}Mbps")
            return "Interface Summary:\n- " + "\n- ".join(lines) if lines else "Interface network tidak tersedia."

        return "Network action tidak dikenali. Gunakan: ping, interface_summary."

    def _run_utility(self, action: str, args: list[str]) -> str:
        if action == "time":
            from datetime import UTC, datetime

            return datetime.now(UTC).isoformat(timespec="seconds")
        if action == "env":
            key = args[0] if args else "PATH"
            return f"{key}={os.environ.get(key, '')}"
        if action == "path":
            return str(Path.cwd())
        return "Utility action tidak dikenali. Gunakan: time, env, path."
