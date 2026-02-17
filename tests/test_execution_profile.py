from core.execution_profile import ExecutionProfilePolicy
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


class DummySystemActions:
    def shutdown_now(self) -> str:
        return "Shutdown command dikirim ke sistem operasi."

    def terminate_process(self, target: str) -> str:
        return f"Process '{target}' berhasil dihentikan (1 instance)."

    def delete_path(self, target: str) -> str:
        return f"File dihapus: {target}"


def build_router() -> CommandRouter:
    return CommandRouter(
        launcher=DummyLauncher(),
        file_manager=DummyFileManager(),
        system_tools=DummySystemTools(),
        system_actions=DummySystemActions(),
    )


def test_execution_profile_policy_explain_only_for_high_risk() -> None:
    policy = ExecutionProfilePolicy(profile="explain-only")
    decision = policy.evaluate("kill")

    assert decision.mode == "explain"
    assert decision.risk_level == "high"


def test_router_profile_command_updates_policy() -> None:
    router = build_router()
    result = router.execute("profile balanced")

    assert "Execution profile aktif: balanced" in result.message
    assert router.execution_profile_policy.profile == "balanced"


def test_router_profile_strict_blocks_critical_shutdown() -> None:
    router = build_router()
    router.safe_mode = False
    router.execute("profile strict")

    result = router.execute("shutdown")
    assert "Execution profile blocked" in result.message


def test_router_profile_explain_only_returns_explain_for_delete() -> None:
    router = build_router()
    router.safe_mode = False
    router.execute("profile explain-only")

    result = router.execute("delete C:/temp/sample.txt")
    assert "explain-only" in result.message
