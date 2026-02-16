from modules.file_manager import FileManager


def test_search_file_with_query(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    file_path = root / "report.pdf"
    file_path.write_text("dummy", encoding="utf-8")

    file_manager = FileManager(search_root=root, max_results=5)
    message = file_manager.search_file("report")

    assert "Hasil pencarian" in message
    assert "report.pdf" in message


def test_search_file_empty_query() -> None:
    file_manager = FileManager()
    message = file_manager.search_file("   ")
    assert "Query pencarian kosong" in message


def test_search_file_not_found(tmp_path) -> None:
    root = tmp_path / "root_empty"
    root.mkdir()

    file_manager = FileManager(search_root=root, max_results=5)
    message = file_manager.search_file("unknown-file")

    assert "tidak ditemukan" in message