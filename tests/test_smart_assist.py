from core.smart_assist import SmartAssistEngine
from core.router import CommandRouter


class DummyLauncher:
    def open_app(self, alias: str) -> str:
        return f"open:{alias}"


class DummyFileManager:
    def search_file(self, query: str) -> str:
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


def test_smart_assist_levenshtein_autocorrect_candidate() -> None:
    assist = SmartAssistEngine()
    correction = assist.autocorrect("opne vscode", ["open", "search", "sys"])

    assert correction is not None
    assert correction.corrected.startswith("open")


def test_router_explain_mode_returns_non_executing_message() -> None:
    router = build_router()
    result = router.execute("explain open vscode")

    assert "Explain:" in result.message
    assert "open" in result.message


def test_router_autocorrect_requires_confirmation_for_typo() -> None:
    router = build_router()
    result = router.execute("opne vscode")

    assert result.requires_confirmation is True
    assert "Smart Assist correction suggested" in result.message


def test_router_confirm_autocorrect_executes_corrected_command() -> None:
    router = build_router()
    router.execute("opne vscode")
    confirmed = router.confirm_pending(True)

    assert "open:vscode" in confirmed.message
