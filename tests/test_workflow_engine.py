import json

from core.router import CommandResult
from core.workflow_engine import WorkflowEngine


class DummyRouter:
    def __init__(self, responses: dict[str, list[CommandResult]]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def execute(self, command: str) -> CommandResult:
        self.calls.append(command)
        bucket = self.responses.get(command, [CommandResult("unknown")])
        if len(bucket) > 1:
            return bucket.pop(0)
        return bucket[0]


def _write_recipe(tmp_path, name: str, steps: list[dict]) -> None:
    recipes_dir = tmp_path / "recipes"
    recipes_dir.mkdir(parents=True, exist_ok=True)
    target = recipes_dir / f"{name}.json"
    target.write_text(json.dumps({"name": name, "steps": steps}), encoding="utf-8")


def test_workflow_run_success(tmp_path) -> None:
    _write_recipe(
        tmp_path,
        "daily",
        [
            {"name": "open", "command": "open notepad", "expected_contains": "Membuka"},
            {"name": "sys", "command": "sys info", "expected_contains": "Informasi Sistem"},
        ],
    )
    router = DummyRouter(
        {
            "open notepad": [CommandResult("Membuka notepad")],
            "sys info": [CommandResult("Informasi Sistem: OK")],
        }
    )
    engine = WorkflowEngine(router=router, recipes_dir=tmp_path / "recipes")
    result = engine.run_recipe("daily")

    assert result.success is True
    assert len(result.steps) == 2


def test_workflow_manual_approval_cancel(tmp_path) -> None:
    _write_recipe(
        tmp_path,
        "danger",
        [{"name": "delete", "command": "delete C:/tmp/a.txt", "requires_approval": True}],
    )
    router = DummyRouter({"delete C:/tmp/a.txt": [CommandResult("blocked")]})
    engine = WorkflowEngine(router=router, recipes_dir=tmp_path / "recipes")
    result = engine.run_recipe("danger", approve_step=lambda step: False)

    assert result.success is False
    assert result.steps[0].status == "cancelled"


def test_workflow_retry_policy(tmp_path) -> None:
    _write_recipe(
        tmp_path,
        "retry_case",
        [{"name": "open", "command": "open notepad", "retries": 1, "expected_contains": "Membuka"}],
    )
    router = DummyRouter(
        {
            "open notepad": [
                CommandResult("Error open app"),
                CommandResult("Membuka notepad"),
            ]
        }
    )
    engine = WorkflowEngine(router=router, recipes_dir=tmp_path / "recipes")
    result = engine.run_recipe("retry_case")

    assert result.success is True
    assert result.steps[0].attempts == 2


def test_workflow_missing_recipe(tmp_path) -> None:
    engine = WorkflowEngine(router=DummyRouter({}), recipes_dir=tmp_path / "recipes")
    try:
        engine.run_recipe("not-found")
    except FileNotFoundError as error:
        assert "Recipe tidak ditemukan" in str(error)
    else:
        raise AssertionError("Seharusnya melempar FileNotFoundError")