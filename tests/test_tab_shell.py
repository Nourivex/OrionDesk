from PySide6.QtWidgets import QApplication

from core.router import CommandRouter
from ui.main_window import MainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_has_phase18_tabs() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    names = [window.tab_widget.tabText(index) for index in range(window.tab_widget.count())]
    assert names == ["Command", "Memory", "Settings", "Diagnostics", "About"]

    window.close()


def test_phase18_about_and_diagnostics_panels() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(4)
    app.processEvents()
    assert "OrionDesk v1.6" in window.about_info.toPlainText()

    window.tab_widget.setCurrentIndex(3)
    app.processEvents()
    diagnostics_text = window.diagnostics_info.toPlainText()
    assert "Diagnostics panel siap" in diagnostics_text

    window.close()


def test_phase19_command_assist_updates() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.command_input.setText("sys")
    app.processEvents()

    assert "sys info" in window.command_hint_label.text()
    assert "sys info" in window.command_suggestions.text()

    window.command_input.setText("tolong bukakan vscode")
    app.processEvents()
    assert "Did you mean" in window.intent_hint_label.text()

    window.close()


def test_phase21_settings_theme_selection_light_mode() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(2)
    app.processEvents()

    window.theme_selector.setCurrentText("light")
    app.processEvents()

    assert window.theme_selector.currentText() == "light"
    assert "Theme active: light" in window.settings_status.text()

    window.close()


def test_phase24_command_assist_argument_hints() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.command_input.setText("capability")
    app.processEvents()

    assert "Args:" in window.command_hint_label.text()
    assert "file list <path>" in window.command_hint_label.text()

    window.close()


def test_search_command_runs_in_async_mode() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    assert window._should_run_async("search report.pdf") is True
    assert window._should_run_async("open notepad") is False

    window.close()


def test_tab_shell_has_icons_for_modern_ui() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    for index in range(window.tab_widget.count()):
        assert window.tab_widget.tabIcon(index).isNull() is False

    window.close()


def test_main_window_default_close_does_not_minimize_to_tray() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    window.show()
    app.processEvents()

    assert window.minimize_to_tray is False
    window.close()
    app.processEvents()
    assert window.isVisible() is False


def test_phase30_settings_hotkey_and_fast_surface_controls() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(2)
    app.processEvents()

    assert window.hotkey_selector.currentText() in {"Win+Shift+O", "Ctrl+Shift+O", "Alt+Space"}
    assert window.fast_mode_checkbox.isChecked() is True

    window.close()


def test_phase30_fast_surface_focuses_command_input() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(3)
    app.processEvents()
    window._activate_fast_command_surface()
    app.processEvents()

    assert window.tab_widget.currentIndex() == 0

    window.close()