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
    assert "OrionDesk v1.4" in window.about_info.toPlainText()

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


def test_main_window_default_close_does_not_minimize_to_tray() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    window.show()
    app.processEvents()

    assert window.minimize_to_tray is False
    window.close()
    app.processEvents()
    assert window.isVisible() is False