import subprocess

from modules.launcher import Launcher


def test_open_app_known_alias() -> None:
    calls: list[tuple[list[str], bool]] = []

    class DummyProcess:
        pid = 1234

        def poll(self):
            return None

    def fake_popen(command: list[str], shell: bool) -> DummyProcess:
        calls.append((command, shell))
        return DummyProcess()

    original = subprocess.Popen
    subprocess.Popen = fake_popen

    launcher = Launcher(alias_map={"vscode": "code"})
    try:
        message = launcher.open_app("vscode")
    finally:
        subprocess.Popen = original

    assert calls == [(["code"], False)]
    assert "Membuka 'vscode'" in message
    assert "PID: 1234" in message


def test_open_app_unknown_alias() -> None:
    launcher = Launcher(alias_map={"vscode": "code"})
    message = launcher.open_app("unknown")
    assert "belum terdaftar" in message


def test_open_app_process_error() -> None:
    def fake_popen(command: list[str], shell: bool) -> None:
        raise OSError("not found")

    original = subprocess.Popen
    subprocess.Popen = fake_popen

    launcher = Launcher(alias_map={"vscode": "code"})
    try:
        message = launcher.open_app("vscode")
    finally:
        subprocess.Popen = original

    assert "Gagal membuka" in message