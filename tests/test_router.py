from core.router import CommandRouter
from core.safe_mode_policy import SafeModePolicy
from core.security_guard import SecurityGuard


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
    assert "command whitelist" in router.route("foobar")


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


def test_safe_mode_requires_confirmation_for_dangerous_command() -> None:
    router = build_router()
    result = router.execute("shutdown")

    assert result.requires_confirmation is True
    assert result.pending_command == "shutdown"
    assert router.pending_confirmation is not None


def test_safe_mode_reject_confirmation() -> None:
    router = build_router()
    router.execute("delete C:/temp/file.txt")
    response = router.confirm_pending(False)

    assert "dibatalkan" in response.message
    assert router.pending_confirmation is None


def test_safe_mode_approve_confirmation() -> None:
    router = build_router()
    router.execute("kill 1234")
    response = router.confirm_pending(True)

    assert "Simulasi kill process" in response.message
    assert router.pending_confirmation is None


def test_dangerous_command_executes_when_safe_mode_disabled() -> None:
    router = build_router()
    router.safe_mode = False

    result = router.execute("shutdown")
    assert result.requires_confirmation is False
    assert "Simulasi shutdown" in result.message


def test_contract_rejects_invalid_sys_args() -> None:
    router = build_router()
    result = router.execute("sys info now")
    assert "Format salah" in result.message
    assert "sys info" in result.message


def test_contract_rejects_shutdown_with_extra_args() -> None:
    router = build_router()
    router.safe_mode = False
    result = router.execute("shutdown now")
    assert "Format salah" in result.message
    assert "shutdown" in result.message


def test_contract_rejects_unknown_keyword() -> None:
    router = build_router()
    result = router.execute("hack system")
    assert "command whitelist" in result.message


def test_contract_rejects_too_long_command() -> None:
    router = build_router()
    long_payload = "open " + ("a" * 301)
    result = router.execute(long_payload)
    assert "terlalu panjang" in result.message


def test_contract_rejects_kill_without_target() -> None:
    router = build_router()
    result = router.execute("kill")
    assert "Format salah" in result.message
    assert "kill <process_name_or_pid>" in result.message


def test_router_records_session_for_success_command() -> None:
    router = build_router()
    router.execute("open vscode")
    latest = router.session_layer.recent(limit=1)[0]

    assert latest.command == "open vscode"
    assert latest.status == "success"


def test_router_records_session_for_pending_and_cancelled() -> None:
    router = build_router()
    router.execute("shutdown")
    pending = router.session_layer.recent(limit=1)[0]
    assert pending.status == "pending_confirmation"

    router.confirm_pending(False)
    cancelled = router.session_layer.recent(limit=1)[0]
    assert cancelled.status == "cancelled"


def test_router_auto_registers_plugin_commands() -> None:
    router = build_router()
    registered = set(router.contracts.keys())

    assert {"open", "search", "sys", "delete", "kill", "shutdown"}.issubset(registered)
    assert {"delete", "kill", "shutdown"}.issubset(router.dangerous_keywords)


def test_router_semantic_intent_open() -> None:
    router = build_router()
    result = router.execute("tolong bukakan notepad")

    assert result.message == "open:notepad"


def test_router_semantic_intent_search() -> None:
    router = build_router()
    result = router.execute("tolong cari file report.pdf")

    assert result.message == "search:report.pdf"


def test_delete_restricted_by_path_policy_when_safe_mode_off(tmp_path) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    guard = SecurityGuard(
        command_whitelist={"delete", "kill", "shutdown", "open", "search", "sys"},
        allowed_delete_roots=[allowed_root],
    )
    router = build_router()
    router.safe_mode = False
    router.security_guard = guard

    result = router.execute("delete C:/Windows/System32")
    assert "path restriction" in result.message


def test_kill_protected_process_denied_when_safe_mode_off() -> None:
    guard = SecurityGuard(
        command_whitelist={"delete", "kill", "shutdown", "open", "search", "sys"},
    )
    router = build_router()
    router.safe_mode = False
    router.security_guard = guard

    result = router.execute("kill lsass.exe")
    assert "process permission guard" in result.message


def test_safe_mode_policy_can_block_shutdown() -> None:
    policy = SafeModePolicy(blocked_actions=("shutdown",))
    router = build_router()
    router.safe_mode_policy = policy

    result = router.execute("shutdown")
    assert "safe mode policy" in result.message


def test_router_memory_summary_tracks_commands() -> None:
    router = build_router()
    router.execute("open vscode")
    router.execute("open vscode")

    summary = router.memory_summary()
    counts = dict(summary["top_commands"])
    assert counts.get("open vscode", 0) >= 2


def test_router_recovery_snapshot_and_diagnostic() -> None:
    router = build_router()
    router.execute("open vscode")

    snapshot = router.save_recovery_snapshot()
    report = router.create_diagnostic_report()

    assert snapshot is not None
    assert report is not None


def test_router_release_channel_api() -> None:
    router = build_router()
    channel = router.set_release_channel("beta")
    assert channel == "beta"
    assert router.get_release_channel() == "beta"


def test_router_command_assist_suggestions() -> None:
    router = build_router()
    suggestions = router.suggest_commands("se")

    assert "search file <query>" in suggestions


def test_router_usage_hint_matches_contract() -> None:
    router = build_router()
    assert router.usage_hint("sys") == "sys info"


def test_router_explain_intent_for_semantic_input() -> None:
    router = build_router()
    explanation = router.explain_intent("tolong bukakan vscode")

    assert "Did you mean" in explanation
    assert "open vscode" in explanation