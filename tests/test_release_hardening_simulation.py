from core.release_hardening import ReleaseHardeningPlan


def test_release_hardening_simulation_mode_success_marks_checklist() -> None:
    plan = ReleaseHardeningPlan()

    payload = plan.run_simulation_mode()
    summary = plan.summary()

    assert payload["status"] == "Simulation Success"
    assert payload["panic_triggered"] is True
    assert any(item["status"] == "rolled_back" for item in payload["rollback_reports"])
    assert summary["completed"] >= 1


def test_release_hardening_simulation_mode_conflict_status() -> None:
    plan = ReleaseHardeningPlan()
    payload = plan.run_simulation_mode(
        workflow_steps=[
            {"step_id": "S1", "name": "prepare", "rollback_supported": True, "age_seconds": 10},
            {"step_id": "S2", "name": "mutate", "rollback_supported": False, "age_seconds": 5},
            {"step_id": "S3", "name": "finalize", "rollback_supported": True, "age_seconds": 3},
        ],
        panic_at_step=2,
        rollback_window_seconds=30,
    )

    assert payload["status"] == "Rollback Conflict"
    assert payload["panic_triggered"] is True
    assert any(item["status"] == "rollback_conflict" for item in payload["rollback_reports"])
