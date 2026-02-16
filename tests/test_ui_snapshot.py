import os
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from core.router import CommandRouter
from ui.main_window import MainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _images_equal(first: Path, second: Path) -> bool:
    image_one = QImage(str(first))
    image_two = QImage(str(second))
    if image_one.size() != image_two.size():
        return False
    return image_one == image_two


def test_window_snapshot_compare_or_archive() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    root = Path(__file__).resolve().parents[1]
    baseline_dir = root / "tests" / "baseline"
    artifacts_dir = root / "tests" / "artifacts"
    archive_dir = artifacts_dir / "archive"

    baseline_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    baseline_file = baseline_dir / "oriondesk-baseline.png"
    current_file = artifacts_dir / "oriondesk-current.png"
    archive_file = archive_dir / f"oriondesk-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"

    app = _app()
    window = MainWindow(router=CommandRouter())
    window.resize(900, 560)
    window.show()
    app.processEvents()

    captured = window.grab()
    assert captured.save(str(current_file), "PNG") is True
    shutil.copyfile(current_file, archive_file)

    if not baseline_file.exists():
        shutil.copyfile(current_file, baseline_file)
    else:
        assert _images_equal(current_file, baseline_file) is True

    window.close()