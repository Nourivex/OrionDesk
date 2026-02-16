from core.router import CommandRouter


class DummyLauncher:
    def __init__(self) -> None:
        self.last_alias = None

    def open_app(self, alias: str) -> str:
        self.last_alias = alias
        return f"open:{alias}"


class DummyFileManager:
    def __init__(self) -> None:
        self.last_query = None

    def search_file(self, query: str) -> str:
        self.last_query = query
        return f"search:{query}"


class DummySystemTools:
    def system_info(self) -> str:
        return "sys:ok"


def build_router() -> CommandRouter:
    return CommandRouter(
        launcher=DummyLauncher(),
        file_manager=DummyFileManager(),
        system_tools=DummySystemTools(),
    )


def test_route_open_command() -> None:
    router = build_router()
    result = router.route("open vscode")

    assert result == "open:vscode"
    assert router.launcher.last_alias == "vscode"


def test_route_search_file_command() -> None:
    router = build_router()
    result = router.route("search file report.pdf")

    assert result == "search:report.pdf"
    assert router.file_manager.last_query == "report.pdf"


def test_route_sys_info_command() -> None:
    router = build_router()
    assert router.route("sys info") == "sys:ok"


def test_route_empty_command() -> None:
    router = build_router()
    assert "Perintah kosong" in router.route("   ")


def test_route_unknown_command() -> None:
    router = build_router()
    assert "Perintah tidak dikenali" in router.route("foobar")


def test_route_invalid_search_format() -> None:
    router = build_router()
    assert "Format salah" in router.route("search docs")


def test_parse_command_success() -> None:
    router = build_router()
    parsed = router.parse("search file data.txt")

    assert parsed is not None
    assert parsed.keyword == "search"
    assert parsed.args == ["file", "data.txt"]


def test_parse_command_empty() -> None:
    router = build_router()
    assert router.parse("   ") is None


def test_route_keyword_case_insensitive() -> None:
    router = build_router()
    result = router.route("OPEN VSCode")
    assert result == "open:VSCode"