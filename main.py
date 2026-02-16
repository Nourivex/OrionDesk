from PySide6.QtWidgets import QApplication

from core.router import CommandRouter
from ui.main_window import MainWindow


def main() -> int:
    app = QApplication([])
    router = CommandRouter()
    window = MainWindow(router=router)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())