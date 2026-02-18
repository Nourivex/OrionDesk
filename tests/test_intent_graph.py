from core.intent_graph import IntentGraphPlanner


class DummyResolution:
    def __init__(self, resolved: str, confidence: float, reason: str) -> None:
        self.resolved = resolved
        self.confidence = confidence
        self.reason = reason


def test_intent_graph_planner_builds_dependency_chain() -> None:
    planner = IntentGraphPlanner()

    mapping = {
        "open vscode": DummyResolution("open vscode", 0.9, "keyword"),
        "sys info": DummyResolution("sys info", 0.8, "keyword"),
        "search report": DummyResolution("search file report", 0.85, "semantic"),
    }

    graph = planner.build(
        raw_input="open vscode lalu sys info kemudian search report",
        resolve_intent=lambda text: mapping[text],
    )

    payload = graph.to_dict()
    assert payload["title"].startswith("Multi-step intent plan")
    assert len(payload["steps"]) == 3
    assert payload["steps"][1]["depends_on"] == ["S1"]
    assert payload["steps"][2]["depends_on"] == ["S2"]
    assert payload["steps"][2]["resolved_command"] == "search file report"


def test_intent_graph_planner_step_type_mapping() -> None:
    planner = IntentGraphPlanner()

    graph = planner.build(
        raw_input="sys info; open vscode",
        resolve_intent=lambda text: DummyResolution(text, 0.9, "keyword"),
    )

    payload = graph.to_dict()
    assert payload["steps"][0]["step_type"] == "analyze"
    assert payload["steps"][1]["step_type"] == "execute"
