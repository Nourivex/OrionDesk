from modules.launcher import Launcher


def test_open_app_known_alias() -> None:
    launcher = Launcher(alias_map={"vscode": "code"})
    message = launcher.open_app("vscode")
    assert "Perintah open diterima" in message
    assert "vscode" in message


def test_open_app_unknown_alias() -> None:
    launcher = Launcher(alias_map={"vscode": "code"})
    message = launcher.open_app("unknown")
    assert "belum terdaftar" in message