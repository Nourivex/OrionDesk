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


TAB_NAMES = ["Command", "Memory", "Settings", "Diagnostics", "About"]


def _detect_active_assets_version(roadmap_file: Path) -> str:
    if not roadmap_file.exists():
        return "v4"
    lines = roadmap_file.read_text(encoding="utf-8").splitlines()
    for line in lines:
        text = line.strip().lower()
        if "roadmap v" in text and "active" in text:
            parts = text.replace("(", " ").replace(")", " ").split()
            for item in parts:
                if item.startswith("v") and item[1:].isdigit():
                    return item
    return "v4"


def _cleanup_outdated_asset_pngs(assets_dir: Path, active_version: str) -> None:
    if not assets_dir.exists():
        return
    for version_dir in assets_dir.iterdir():
        if not version_dir.is_dir():
            continue
        if version_dir.name.lower() == active_version.lower():
            continue
        for png_file in version_dir.glob("*.png"):
            png_file.unlink(missing_ok=True)


def _cleanup_all_asset_pngs(assets_dir: Path) -> None:
    if not assets_dir.exists():
        return
    for png_file in assets_dir.rglob("*.png"):
        png_file.unlink(missing_ok=True)


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


def _capture_snapshot_for_tab(
    window: MainWindow,
    app: QApplication,
    tab_name: str,
    width: int,
    height: int,
    output_file: Path,
) -> None:
    tab_index = TAB_NAMES.index(tab_name)
    window.tab_widget.setCurrentIndex(tab_index)
    app.processEvents()
    QTest.qWait(60)
    window.resize(width, height)
    app.processEvents()
    QTest.qWait(50)

    captured = window.grab()
    if captured.isNull():
        raise RuntimeError("Gagal mengambil snapshot (QPixmap is null).")

    success = captured.save(str(output_file), "PNG")
    if not success:
        raise RuntimeError(f"Gagal menyimpan file ke {output_file}")


def test_cleanup_outdated_assets_based_on_roadmap(tmp_path) -> None:
    docs_dir = tmp_path / "docs"
    assets_dir = docs_dir / "assets"
    v2_dir = assets_dir / "v2"
    v4_dir = assets_dir / "v4"
    v2_dir.mkdir(parents=True)
    v4_dir.mkdir(parents=True)

    old_png = v2_dir / "old.png"
    active_png = v4_dir / "active.png"
    old_png.write_bytes(b"old")
    active_png.write_bytes(b"active")

    roadmap = docs_dir / "ROADMAP.md"
    roadmap.write_text("## ROADMAP v4 (Active / v1.4)", encoding="utf-8")

    active_version = _detect_active_assets_version(roadmap)
    _cleanup_outdated_asset_pngs(assets_dir, active_version)

    assert old_png.exists() is False
    assert active_png.exists() is True


def test_window_snapshot_compare_or_archive() -> None:
    _configure_snapshot_platform()

    root = Path(__file__).resolve().parents[1]
    _cleanup_all_asset_pngs(root / "docs" / "assets")
    active_version = _detect_active_assets_version(root / "docs" / "ROADMAP.md")
    _cleanup_outdated_asset_pngs(root / "docs" / "assets", active_version)

    artifacts_dir = root / "tests" / "artifacts"
    baseline_dir = artifacts_dir / "baseline" / active_version
    archive_dir = artifacts_dir / "archive"

    baseline_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    app = _app()
    sizes = [(1280, 760), (1024, 640)]

    for width, height in sizes:
        suffix = f"{width}x{height}"
        for tab_name in TAB_NAMES:
            tab_slug = tab_name.lower()
            baseline_file = baseline_dir / f"oriondesk-baseline-{tab_slug}-{suffix}.png"
            current_file = artifacts_dir / f"oriondesk-current-{tab_slug}-{suffix}.png"
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            archive_file = archive_dir / f"oriondesk-{tab_slug}-{suffix}-{stamp}.png"

            router = CommandRouter()
            if router.memory_engine is not None:
                router.memory_engine.purge_all()
            router.set_release_channel("stable")

            window = MainWindow(router=router)
            window.show()
            QTest.qWait(120)
            _prepare_readable_snapshot(window, app)
            _capture_snapshot_for_tab(window, app, tab_name, width, height, current_file)

            shutil.copyfile(current_file, archive_file)
            shutil.copyfile(current_file, baseline_file)

            window.close()