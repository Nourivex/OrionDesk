from dataclasses import dataclass, field


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
        return (
            f"[PHASE 0] Perintah open diterima untuk '{clean_alias}' "
            f"({resolved_name}). Implementasi launch real akan ditambahkan di PHASE 2."
        )