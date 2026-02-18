from core.performance_profiler import PerformanceProfiler
from core.release_hardening import ReleaseHardeningPlan


def test_performance_profiler_measures_storage_io() -> None:
    profiler = PerformanceProfiler()
    result = profiler.measure_storage_io(iterations=3)

    assert result.metric == "storage_io_ms"
    assert result.iterations == 3
    assert result.average_ms >= 0


def test_performance_profiler_measures_command_latency() -> None:
    profiler = PerformanceProfiler()
    calls: list[str] = []

    def executor(command: str) -> str:
        calls.append(command)
        return "ok"

    result = profiler.measure_command_latency(executor, "sys info", iterations=2)

    assert result.metric == "command_latency_ms"
    assert result.iterations == 2
    assert calls == ["sys info", "sys info"]


def test_release_hardening_plan_summary() -> None:
    plan = ReleaseHardeningPlan()
    plan.mark_completed("tests")
    summary = plan.summary()

    assert summary["completed"] == 1
    assert summary["total"] >= 1
    assert isinstance(summary["rollback_steps"], list)
