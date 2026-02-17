from PySide6.QtWidgets import QApplication

from core.router import CommandRouter
from ui.main_window import MainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_has_phase17_tabs() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    names = [window.tab_widget.tabText(index) for index in range(window.tab_widget.count())]
    assert names == ["Command", "About", "Settings", "Memory", "Diagnostics"]

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