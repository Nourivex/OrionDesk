from core.release_gate_v22 import GateScenario, ReleaseGateV22


def test_release_gate_reliability_matrix() -> None:
    gate = ReleaseGateV22()
    scenarios = [
        GateScenario(name="ok-1", command="a"),
        GateScenario(name="ok-2", command="b"),
    ]

    payload = gate.run_reliability_matrix(lambda _command: {"ok": True, "message": "ok"}, scenarios)

    assert payload["total"] == 2
    assert payload["passed"] == 2
    assert payload["pass_rate"] == 100.0


def test_release_gate_baseline_compare_and_checklist() -> None:
    gate = ReleaseGateV22()

    comparison = gate.compare_baseline(
        v21={"startup_ms": 250, "command_latency_ms": 140, "storage_io_ms": 18},
        v22={"startup_ms": 220, "command_latency_ms": 120, "storage_io_ms": 16},
    )
    checklist = gate.release_checklist(
        reliability={"pass_rate": 95.0},
        comparison=comparison,
    )

    assert comparison["startup_ms"]["delta_ms"] == -30.0
    assert checklist["ready"] is True
    assert checklist["passed"] == checklist["total"]
