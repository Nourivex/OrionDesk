from core.latency_budget import LatencyBudget, MainThreadResponsivenessGuard


def test_latency_budget_collects_stage_reports() -> None:
    tracker = LatencyBudget(budgets_ms={"intent": 1.0, "policy": 1.0, "execution": 5.0, "total": 20.0})

    tracker.timed("intent", lambda: "ok")
    tracker.timed("policy", lambda: "ok")
    tracker.timed("execution", lambda: "ok")

    summary = tracker.summary()

    assert summary["total_elapsed_ms"] >= 0
    assert len(summary["stages"]) == 3
    assert {item["stage"] for item in summary["stages"]} == {"intent", "policy", "execution"}


def test_main_thread_guard_detects_blocking_non_execution_stage() -> None:
    guard = MainThreadResponsivenessGuard(frame_budget_ms=10.0)
    stage_report = [
        {"stage": "intent", "elapsed_ms": 12.0, "budget_ms": 20.0, "exceeded": False},
        {"stage": "execution", "elapsed_ms": 800.0, "budget_ms": 1200.0, "exceeded": False},
    ]

    result = guard.evaluate(stage_report)

    assert result["is_responsive"] is False
    assert "intent" in result["blocked_stages"]
