from core.router import CommandRouter
from core.safe_mode_policy import SafeModePolicy
from core.security_guard import SecurityGuard
from core.embedding_provider import EmbeddingConfig, EmbeddingHealth, EmbeddingProvider
from core.generation_provider import GenerationConfig, GenerationHealth, GenerationModelInfo, GenerationProvider


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


class DummySystemActions:
    def shutdown_now(self) -> str:
        return "Shutdown command dikirim ke sistem operasi."

    def terminate_process(self, target: str) -> str:
        return f"Process '{target}' berhasil dihentikan (1 instance)."

    def delete_path(self, target: str) -> str:
        return f"File dihapus: {target}"


class DummyProjectManager:
    def open_project(self, name: str) -> str:
        return f"project:{name}"


class DummyClipboardManager:
    def __init__(self) -> None:
        self.items: list[str] = []

    def push(self, text: str) -> None:
        self.items.insert(0, text)

    def recent(self, limit: int = 5) -> list[str]:
        return self.items[:limit]

    def clear(self) -> None:
        self.items.clear()


class DummyFocusModeManager:
    def __init__(self) -> None:
        self.current = "off"

    def enable(self, mode: str) -> str:
        self.current = mode
        return f"mode:{mode}:on"

    def disable(self) -> str:
        self.current = "off"
        return "mode:off"

    def status(self) -> str:
        return f"mode:{self.current}"


class DummyNetworkDiagnostics:
    def ping_profile(self, host: str, count: int = 2) -> str:
        return f"ping:{host}:{count}"

    def dns_lookup(self, host: str) -> str:
        return f"dns:{host}"

    def public_ip(self) -> str:
        return "ip:127.0.0.1"


class DummyEmbeddingProvider(EmbeddingProvider):
    def config(self) -> EmbeddingConfig:
        return EmbeddingConfig(host="http://localhost:11434", model="nomic-embed-text:latest", timeout_seconds=2.5)

    def health(self) -> EmbeddingHealth:
        return EmbeddingHealth(ok=True, message="Ollama ready (nomic-embed-text:latest)")

    def embed(self, text: str) -> list[float]:
        return [float(len(text))]


class CountingEmbeddingProvider(DummyEmbeddingProvider):
    def __init__(self) -> None:
        self.health_calls = 0

    def health(self) -> EmbeddingHealth:
        self.health_calls += 1
        return super().health()


class DummyGenerationProvider(GenerationProvider):
    def __init__(self, healthy: bool = True, response: str = "Jawaban dari Gemma") -> None:
        self.healthy = healthy
        self.response = response

    def config(self) -> GenerationConfig:
        return GenerationConfig(
            host="http://localhost:11434",
            model="gemma3:4b",
            timeout_seconds=6.0,
            token_budget=180,
            temperature=0.1,
        )

    def health(self) -> GenerationHealth:
        if self.healthy:
            return GenerationHealth(ok=True, message="Generation model ready (gemma3:4b)")
        return GenerationHealth(ok=False, message="Generation model offline")

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        if not self.healthy:
            return ""
        return self.response

    def list_models(self) -> list[GenerationModelInfo]:
        return [
            GenerationModelInfo(name="gemma3:4b", parameter_size="4B", role="chat", gpu_badge="Aman"),
            GenerationModelInfo(name="nomic-embed-text:latest", parameter_size="-", role="embed", gpu_badge="Lowest/Embed"),
        ]


class CapturingGenerationProvider(DummyGenerationProvider):
    def __init__(self) -> None:
        super().__init__(healthy=True, response="ok")
        self.last_prompt = ""

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        self.last_prompt = prompt
        return super().generate(prompt, system_prompt)


def build_router() -> CommandRouter:
    return CommandRouter(
        launcher=DummyLauncher(),
        file_manager=DummyFileManager(),
        system_tools=DummySystemTools(),
        system_actions=DummySystemActions(),
        project_manager=DummyProjectManager(),
        clipboard_manager=DummyClipboardManager(),
        focus_mode_manager=DummyFocusModeManager(),
        network_diagnostics=DummyNetworkDiagnostics(),
        embedding_provider=DummyEmbeddingProvider(),
        generation_provider=DummyGenerationProvider(),
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


def test_route_search_shortcut_without_file_keyword() -> None:
    router = build_router()
    result = router.route("search report.pdf")

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
    assert router.route("search docs") == "search:docs"


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

    assert "berhasil dihentikan" in response.message
    assert router.pending_confirmation is None


def test_dangerous_command_executes_when_safe_mode_disabled() -> None:
    router = build_router()
    router.safe_mode = False

    result = router.execute("shutdown")
    assert result.requires_confirmation is False
    assert "Shutdown command" in result.message


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


def test_router_exposes_embedding_config_and_health() -> None:
    router = build_router()

    config = router.embedding_config()
    health = router.embedding_health()

    assert config["model"] == "nomic-embed-text:latest"
    assert config["timeout_seconds"] == 2.5
    assert health["ok"] is True
    assert "ready" in health["message"].lower()


def test_router_embedding_health_uses_cache() -> None:
    provider = CountingEmbeddingProvider()
    router = CommandRouter(
        launcher=DummyLauncher(),
        file_manager=DummyFileManager(),
        system_tools=DummySystemTools(),
        system_actions=DummySystemActions(),
        project_manager=DummyProjectManager(),
        clipboard_manager=DummyClipboardManager(),
        focus_mode_manager=DummyFocusModeManager(),
        network_diagnostics=DummyNetworkDiagnostics(),
        embedding_provider=provider,
        generation_provider=DummyGenerationProvider(),
    )

    router.embedding_health()
    router.embedding_health()

    assert provider.health_calls == 1


def test_router_embed_text_uses_provider() -> None:
    router = build_router()

    vector = router.embed_text("hello")
    assert vector == [5.0]


def test_router_exposes_generation_config_and_health() -> None:
    router = build_router()

    config = router.generation_config()
    health = router.generation_health()

    assert config["model"] == "gemma3:4b"
    assert config["token_budget"] == 180
    assert health["ok"] is True


def test_router_set_generation_runtime_updates_config() -> None:
    router = build_router()

    updated = router.set_generation_runtime(
        model="llama3.2:3b",
        timeout_seconds=5.0,
        token_budget=320,
        temperature=0.3,
    )

    assert updated["model"] == "llama3.2:3b"
    assert updated["timeout_seconds"] == 5.0
    assert updated["token_budget"] == 320
    assert updated["temperature"] == 0.3


def test_router_response_quality_applies_to_reasoning_prompt() -> None:
    router = build_router()
    router.set_chat_model_enabled(True)
    provider = CapturingGenerationProvider()
    router.generation_provider = provider

    router.set_response_quality("deep")
    router.generate_reasoned_answer("open vscode lalu sys info")

    assert "Response quality: deep" in provider.last_prompt


def test_router_available_generation_models_contains_badges() -> None:
    router = build_router()

    models = router.available_generation_models(force_reload=True)

    assert len(models) >= 1
    assert models[0]["name"] == "gemma3:4b"
    assert models[0]["gpu_badge"] == "Aman"


def test_router_generate_reasoned_answer_uses_gemma_provider() -> None:
    router = build_router()
    router.set_chat_model_enabled(True)

    payload = router.generate_reasoned_answer("open vscode lalu sys info")

    assert payload["mode"] == "gemma"
    assert "Gemma" in payload["message"]


def test_router_generate_reasoned_answer_reuses_cache_on_repeated_query() -> None:
    router = build_router()
    router.set_chat_model_enabled(True)

    first = router.generate_reasoned_answer("open vscode lalu sys info")
    second = router.generate_reasoned_answer("open vscode lalu sys info")

    assert first["message"] == second["message"]
    assert second["mode"] == "cache"


def test_router_generate_reasoned_answer_fallback_when_model_offline() -> None:
    router = build_router()
    router.set_chat_model_enabled(True)
    router.generation_provider = DummyGenerationProvider(healthy=False)

    payload = router.generate_reasoned_answer("open vscode lalu sys info")

    assert payload["mode"] == "fallback"
    assert "Ringkasan reasoning" in payload["message"]


def test_router_execute_with_latency_budget_returns_stage_metrics() -> None:
    router = build_router()

    payload = router.execute_with_latency_budget("sys info")

    assert "latency" in payload
    assert "stages" in payload["latency"]
    assert any(item["stage"] == "execution" for item in payload["latency"]["stages"])


def test_router_execute_reasoning_async_returns_future_payload() -> None:
    router = build_router()
    router.set_chat_model_enabled(True)

    future = router.execute_reasoning_async("open vscode lalu sys info")
    payload = future.result(timeout=2)

    assert payload["mode"] in {"gemma", "fallback"}
    assert "message" in payload


def test_router_intent_graph_decomposes_steps() -> None:
    router = build_router()

    graph = router.intent_graph("open vscode lalu sys info")
    steps = graph["steps"]

    assert len(steps) == 2
    assert steps[0]["step_id"] == "S1"
    assert steps[1]["depends_on"] == ["S1"]


def test_router_intent_graph_contains_reason_trace() -> None:
    router = build_router()

    graph = router.intent_graph("tolong bukakan vscode lalu cek system")
    reasons = [item["reason"] for item in graph["steps"]]

    assert len(reasons) >= 1
    assert all("confidence=" in reason for reason in reasons)


def test_router_reason_plan_contains_graph_and_decisions() -> None:
    router = build_router()

    payload = router.reason_plan("open vscode lalu sys info")

    assert "graph" in payload
    assert "reasoning" in payload
    assert len(payload["graph"]["steps"]) == 2
    assert len(payload["reasoning"]["decisions"]) == 2


def test_router_multi_command_bundle_has_arguments_and_modes() -> None:
    router = build_router()

    payload = router.multi_command_bundle("open vscode lalu sys info")

    assert len(payload["commands"]) == 2
    assert len(payload["arguments"]) == 2
    assert payload["commands"][0]["execution_mode"] in {"chain", "parallel-eligible", "guarded"}


def test_router_multi_command_bundle_reduces_repeated_patterns() -> None:
    router = build_router()

    payload = router.multi_command_bundle("open vscode lalu open vscode lalu sys info")

    commands = [item["command"] for item in payload["commands"]]
    assert commands.count("open vscode") == 1


def test_router_execute_multi_returns_reports() -> None:
    router = build_router()

    payload = router.execute_multi("open vscode lalu sys info", dry_run=True)

    assert payload["dry_run"] is True
    assert len(payload["reports"]) == 2
    assert all("status" in item for item in payload["reports"])


def test_execute_multi_step_natural_input_runs_two_tasks() -> None:
    router = build_router()

    result = router.execute("tolong buka vscode lalu cek sys info")

    assert "[Multi-step Execution]" in result.message
    assert "open:vscode" in result.message
    assert "sys:ok" in result.message


def test_execute_multi_step_ambiguity_shows_reasoned_status() -> None:
    router = build_router()

    result = router.execute("tolong cek sesuatu lalu mungkin hapus file temp")

    assert "[Multi-step Execution]" in result.message
    assert any(marker in result.message for marker in ["FALLBACK", "PRUNED", "GUARDED", "INVALID"])


def test_router_semantic_intent_open() -> None:
    router = build_router()
    result = router.execute("tolong bukakan notepad")

    assert result.message == "open:notepad"


def test_router_execute_with_enhanced_response_for_natural_language() -> None:
    router = build_router()
    router.set_chat_model_enabled(True)

    result = router.execute_with_enhanced_response("tolong bukakan notepad")

    assert "Jawaban dari Gemma" in result.message
    assert "Action Result" in result.message
    assert "open:notepad" in result.message


def test_router_chat_model_disabled_mode_uses_reasoning_fallback() -> None:
    router = build_router()
    router.set_chat_model_enabled(False)

    payload = router.generate_reasoned_answer("open vscode lalu sys info")

    assert payload["mode"] == "disabled"
    assert "fallback" in payload["message"].lower()


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


def test_route_proj_open_command() -> None:
    router = build_router()
    result = router.route("proj open atlas")
    assert result == "project:atlas"


def test_route_clipboard_history_flow() -> None:
    router = build_router()
    assert "diperbarui" in router.route("clip add alpha")
    assert "alpha" in router.route("clip show")
    assert "dibersihkan" in router.route("clip clear")


def test_route_mode_command_flow() -> None:
    router = build_router()
    assert router.route("mode") == "mode:off"
    assert router.route("mode focus on") == "mode:focus:on"
    assert router.route("mode off") == "mode:off"


def test_route_net_command_flow() -> None:
    router = build_router()
    assert router.route("net ping localhost") == "ping:localhost:2"
    assert router.route("net dns localhost") == "dns:localhost"
    assert router.route("net ip") == "ip:127.0.0.1"


def test_router_build_performance_baseline() -> None:
    router = build_router()
    baseline = router.build_performance_baseline()

    assert set(baseline.keys()) == {"startup_ms", "command_latency_ms", "storage_io_ms"}
    assert baseline["startup_ms"] >= 0


def test_router_release_hardening_summary() -> None:
    router = build_router()
    router.build_performance_baseline()
    summary = router.release_hardening_summary()

    assert summary["completed"] >= 1
    assert summary["total"] >= summary["completed"]