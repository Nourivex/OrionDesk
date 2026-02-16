from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileManager:
    search_root: Path | None = None
    max_results: int = 10

    def search_file(self, query: str) -> str:
        clean_query = query.strip()
        if not clean_query:
            return "Query pencarian kosong."

        root = self.search_root or Path.home()
        if not root.exists():
            return f"Lokasi pencarian tidak ditemukan: {root}"

        matches: list[Path] = []
        keyword = clean_query.lower()

        try:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if keyword in path.name.lower():
                    matches.append(path)
                if len(matches) >= self.max_results:
                    break
        except OSError as error:
            return f"Gagal melakukan pencarian file: {error}"

        if not matches:
            return f"File dengan kata kunci '{clean_query}' tidak ditemukan di {root}."

        lines = [f"Hasil pencarian '{clean_query}' (maks {self.max_results}):"]
        lines.extend(f"- {item}" for item in matches)
        return "\n".join(lines)