from core.multi_command_executor import MultiCommandExecutor


def test_multi_command_executor_bundle_modes() -> None:
    executor = MultiCommandExecutor()

    bundles = executor.bundle(
        commands=["search file report", "open vscode", "delete C:/tmp/a.txt"],
        risk_level=lambda keyword: "high" if keyword == "delete" else "low",
    )

    assert bundles[0]["execution_mode"] == "parallel-eligible"
    assert bundles[1]["execution_mode"] == "chain"
    assert bundles[2]["execution_mode"] == "guarded"


def test_multi_command_executor_reports_execution() -> None:
    executor = MultiCommandExecutor()
    bundles = [{"command": "open vscode", "risk_level": "low", "execution_mode": "chain"}]

    reports = executor.execute(bundles, run_command=lambda _cmd: ("success", "ok"))

    assert len(reports) == 1
    assert reports[0]["status"] == "success"
    assert reports[0]["message"] == "ok"
