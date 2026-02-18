import json
from datetime import UTC, datetime, timedelta

from core.automation_engine import (
    TriggerActionAutomationEngine,
    TriggerActionRegistry,
    TriggerActionRule,
)
from core.router import CommandResult


class DummyExecutor:
    def __init__(self) -> None:
        self.commands: list[str] = []

    def __call__(self, command: str) -> CommandResult:
        self.commands.append(command)
        return CommandResult(message=f"executed: {command}")


def test_registry_load_from_json(tmp_path) -> None:
    payload = {
        "rules": [
            {
                "rule_id": "sched-1",
                "name": "run sys info",
                "trigger_type": "schedule",
                "trigger_config": {"interval_seconds": 60},
                "action_command": "sys info",
                "risk_level": "low",
            }
        ]
    }
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    registry = TriggerActionRegistry()
    loaded = registry.load_from_file(path)

    assert loaded == 1
    assert registry.rules["sched-1"].action_command == "sys info"


def test_scheduler_runs_interval_rule() -> None:
    registry = TriggerActionRegistry()
    registry.register(
        TriggerActionRule(
            rule_id="sched-1",
            name="refresh",
            trigger_type="schedule",
            trigger_config={"interval_seconds": 60},
            action_command="sys info",
        )
    )

    executor = DummyExecutor()
    engine = TriggerActionAutomationEngine(registry=registry, execute_command=executor)

    now = datetime(2026, 2, 18, 9, 0, 0, tzinfo=UTC)
    first_cycle = engine.run_cycle(now=now)
    second_cycle = engine.run_cycle(now=now + timedelta(seconds=30))
    third_cycle = engine.run_cycle(now=now + timedelta(seconds=61))

    assert len(first_cycle) == 1
    assert len(second_cycle) == 0
    assert len(third_cycle) == 1
    assert executor.commands == ["sys info", "sys info"]


def test_file_watcher_triggers_on_file_change(tmp_path) -> None:
    watch_dir = tmp_path / "watch"
    watch_dir.mkdir(parents=True, exist_ok=True)

    registry = TriggerActionRegistry()
    registry.register(
        TriggerActionRule(
            rule_id="watch-1",
            name="watch reports",
            trigger_type="file_watch",
            trigger_config={"path": str(watch_dir), "pattern": "*.txt"},
            action_command="search file report.txt",
        )
    )

    executor = DummyExecutor()
    engine = TriggerActionAutomationEngine(registry=registry, execute_command=executor)
    now = datetime(2026, 2, 18, 9, 0, 0, tzinfo=UTC)

    first_cycle = engine.run_cycle(now=now)
    (watch_dir / "report.txt").write_text("hello", encoding="utf-8")
    second_cycle = engine.run_cycle(now=now + timedelta(seconds=1))

    assert first_cycle == []
    assert len(second_cycle) == 1
    assert second_cycle[0].status == "success"
    assert executor.commands == ["search file report.txt"]


def test_high_risk_rule_requires_approval() -> None:
    registry = TriggerActionRegistry()
    registry.register(
        TriggerActionRule(
            rule_id="sched-risk",
            name="cleanup",
            trigger_type="schedule",
            trigger_config={"interval_seconds": 1},
            action_command="delete C:/tmp/sample.txt",
            risk_level="high",
        )
    )

    executor = DummyExecutor()
    engine = TriggerActionAutomationEngine(
        registry=registry,
        execute_command=executor,
        approval_hook=lambda _rule: False,
    )

    executions = engine.run_cycle(now=datetime(2026, 2, 18, 9, 0, 0, tzinfo=UTC))

    assert len(executions) == 1
    assert executions[0].status == "blocked"
    assert executor.commands == []
