class FileManager:
    def search_file(self, query: str) -> str:
        clean_query = query.strip()
        if not clean_query:
            return "Query pencarian kosong."
        return (
            f"[PHASE 0] Pencarian file untuk '{clean_query}' diterima. "
            "Implementasi search real akan ditambahkan di PHASE 2."
        )