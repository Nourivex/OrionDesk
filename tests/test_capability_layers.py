from pathlib import Path

from core.capability_guardrail import CapabilityGuardrail
from core.capability_layer import SystemCapabilityLayer
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


def test_capability_file_list_works(tmp_path: Path) -> None:
    (tmp_path / "alpha.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "beta.txt").write_text("beta", encoding="utf-8")

    layer = SystemCapabilityLayer()
    result = layer.execute("file", "list", [str(tmp_path)])

    assert "alpha.txt" in result
    assert "beta.txt" in result


def test_capability_guardrail_blocks_protected_process() -> None:
    guardrail = CapabilityGuardrail(permission_tier="admin")
    decision = guardrail.evaluate("process", "terminate", ["explorer.exe"])

    assert decision.allowed is False
    assert "protected process" in decision.reason.lower()


def test_router_capability_process_terminate_needs_confirmation() -> None:
    router = build_router()
    result = router.execute("capability process terminate notepad.exe")

    assert "Guardrail blocked" in result.message
    assert "Permission tier basic" in result.message


def test_router_smart_network_plan_executes_capability_steps() -> None:
    router = build_router()
    result = router.execute("smart cek koneksi lambat gak sih")

    assert "Plan: Network Health Check" in result.message
    assert "capability network ping google.com" in result.message


def test_router_smart_cleanup_download_maps_preview() -> None:
    router = build_router()
    result = router.execute("smart bersihin folder download")

    assert "Download Cleanup Preview" in result.message
    assert "approval manual" in result.message.lower()
