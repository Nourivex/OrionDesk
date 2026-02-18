from core.reasoning_engine import ComplexReasoningEngine


def test_reasoning_engine_fallback_for_low_confidence() -> None:
    engine = ComplexReasoningEngine(min_confidence=0.5)
    graph = {
        "steps": [
            {
                "step_id": "S1",
                "resolved_command": "open vscode",
                "reason": "a -> open vscode (semantic, confidence=0.20)",
            }
        ]
    }

    plan = engine.build_plan(
        graph_payload=graph,
        embed_text=lambda _text: [0.1],
        risk_level=lambda _keyword: "low",
    ).to_dict()

    assert plan["fallback_used"] is True
    assert plan["decisions"][0]["mode"] == "fallback"
    assert plan["decisions"][0]["command"].startswith("explain")


def test_reasoning_engine_prunes_high_risk_low_confidence() -> None:
    engine = ComplexReasoningEngine(min_confidence=0.5)
    graph = {
        "steps": [
            {
                "step_id": "S1",
                "resolved_command": "delete c:/tmp/a.txt",
                "reason": "x -> delete c:/tmp/a.txt (semantic, confidence=0.30)",
            }
        ]
    }

    plan = engine.build_plan(
        graph_payload=graph,
        embed_text=lambda _text: [0.1],
        risk_level=lambda _keyword: "high",
    ).to_dict()

    assert plan["decisions"][0]["mode"] == "pruned"
    assert "pruned" in plan["decisions"][0]["reason"]
