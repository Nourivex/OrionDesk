from core.executor import ErrorCode
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


def test_execute_enveloped_includes_execution_context() -> None:
    router = build_router()
    envelope = router.execute_enveloped("open vscode")

    assert envelope.ok is True
    assert envelope.status == "success"
    assert envelope.error_code == ErrorCode.NONE
    assert envelope.context is not None
    assert envelope.context.session_id == router.session_id
    assert envelope.context.risk_level == "low"


def test_execute_enveloped_uses_error_taxonomy() -> None:
    router = build_router()
    envelope = router.execute_enveloped("   ")

    assert envelope.ok is False
    assert envelope.status == "invalid"
    assert envelope.error_code == ErrorCode.EMPTY_COMMAND


def test_execute_enveloped_dangerous_command_requires_confirmation() -> None:
    router = build_router()
    envelope = router.execute_enveloped("shutdown")

    assert envelope.ok is False
    assert envelope.status == "pending_confirmation"
    assert envelope.error_code == ErrorCode.CONFIRMATION_REQUIRED
    assert envelope.requires_confirmation is True


def test_logger_contains_execution_context_metadata() -> None:
    router = build_router()
    router.execute("open vscode")

    event = router.logger.tail(limit=1)[0]
    metadata = event["metadata"]
    context = metadata["execution_context"]

    assert metadata["status"] == "success"
    assert context["session_id"] == router.session_id
    assert context["profile_policy"] in {"strict", "power"}
