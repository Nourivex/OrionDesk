from modules.file_manager import FileManager


def test_search_file_with_query() -> None:
    file_manager = FileManager()
    message = file_manager.search_file("report.pdf")
    assert "report.pdf" in message


def test_search_file_empty_query() -> None:
    file_manager = FileManager()
    message = file_manager.search_file("   ")
    assert "Query pencarian kosong" in message