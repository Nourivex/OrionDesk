from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import psutil


class SystemActions:
    def terminate_process(self, target: str) -> str:
        clean = target.strip()
        if not clean:
            return "Target process kosong."

        if clean.isdigit():
            try:
                process = psutil.Process(int(clean))
                process.terminate()
                process.wait(timeout=3)
                return f"Process pid={clean} berhasil dihentikan."
            except psutil.NoSuchProcess:
                return f"Process pid={clean} tidak ditemukan."
            except psutil.TimeoutExpired:
                return f"Process pid={clean} tidak merespons terminate dalam batas waktu."
            except psutil.AccessDenied:
                return f"Akses ditolak untuk menghentikan process pid={clean}."

        lowered = clean.lower()
        candidates = {lowered, f"{lowered}.exe"}
        matched = [
            proc
            for proc in psutil.process_iter(["pid", "name"])
            if (proc.info.get("name") or "").lower() in candidates
        ]
        if not matched:
            return f"Process '{clean}' tidak ditemukan."

        killed = 0
        for proc in matched:
            try:
                proc.terminate()
                proc.wait(timeout=3)
                killed += 1
            except (psutil.NoSuchProcess, psutil.TimeoutExpired, psutil.AccessDenied):
                continue

        if killed == 0:
            return f"Process '{clean}' tidak dapat dihentikan."
        return f"Process '{clean}' berhasil dihentikan ({killed} instance)."

    def delete_path(self, target: str) -> str:
        path = Path(target)
        if not path.exists():
            return f"Target tidak ditemukan: {target}"
        if path.is_file():
            path.unlink()
            return f"File dihapus: {target}"
        shutil.rmtree(path)
        return f"Folder dihapus: {target}"

    def shutdown_now(self) -> str:
        subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
        return "Shutdown command dikirim ke sistem operasi."
