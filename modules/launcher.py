from dataclasses import dataclass, field
import subprocess


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
            process = subprocess.Popen(resolved_name, shell=True)
        except OSError as error:
            return f"Gagal membuka '{clean_alias}': {error}"

        return (
            f"Membuka '{clean_alias}' menggunakan '{resolved_name}'. "
            f"PID: {process.pid}."
        )