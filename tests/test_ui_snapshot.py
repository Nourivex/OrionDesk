import os
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from core.router import CommandRouter
from ui.main_window import MainWindow


def _configure_snapshot_platform() -> None:
    if os.name == "nt":
        os.environ.setdefault("QT_QPA_PLATFORM", "windows")
    else:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_SCALE_FACTOR", "1")
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "0")


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi)
        app = QApplication([])
    return app


def _images_equal(first: Path, second: Path) -> bool:
    image_one = QImage(str(first))
    image_two = QImage(str(second))
    if image_one.size() != image_two.size():
        return False
    return image_one == image_two


def _prepare_readable_snapshot(window: MainWindow, app: QApplication) -> None:
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 13)
    font.setFamilies(["Segoe UI", "Cascadia Code", "Arial", "Sans Serif"])

    window.setAttribute(Qt.WidgetAttribute.WA_DontCreateNativeAncestors)
    window.resize(1280, 760)

    window.command_input.setFont(font)
    window.output_panel.setFont(font)

    window.output_panel.clear()
    window.output_panel.append("Lycus@Nourivex - main")
    window.output_panel.append("> open notepad")
    window.output_panel.append("[Calm] Membuka 'notepad' menggunakan 'notepad'. PID: 12345.")

    for _ in range(5):
        app.processEvents()
        QTest.qWait(60)


def test_window_snapshot_compare_or_archive() -> None:
    _configure_snapshot_platform()

    root = Path(__file__).resolve().parents[1]
    baseline_dir = root / "docs" / "assets" / "v2"
    artifacts_dir = root / "tests" / "artifacts"
    archive_dir = artifacts_dir / "archive"

    baseline_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    baseline_file = baseline_dir / "oriondesk-baseline.png"
    current_file = artifacts_dir / "oriondesk-current.png"
    archive_file = archive_dir / f"oriondesk-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"

    app = _app()
    window = MainWindow(router=CommandRouter())
    window.show()
    QTest.qWait(120)
    _prepare_readable_snapshot(window, app)

    captured = window.grab()
    if captured.isNull():
        raise RuntimeError("Gagal mengambil snapshot (QPixmap is null).")
    
    success = captured.save(str(current_file), "PNG")
    if not success:
        raise RuntimeError(f"Gagal menyimpan file ke {current_file}")

    shutil.copyfile(current_file, archive_file)

    if not baseline_file.exists():
        shutil.copyfile(current_file, baseline_file)
    else:
        assert _images_equal(current_file, baseline_file) is True

    window.close()