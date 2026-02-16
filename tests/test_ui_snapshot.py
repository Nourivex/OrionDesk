import os
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QImage, QFontDatabase
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from core.router import CommandRouter
from ui.main_window import MainWindow

def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        # Set atribut DPI sebelum aplikasi dibuat agar rendering konsisten
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
    
    # Gunakan font yang biasanya mendukung simbol atau fallback ke Monospace
    # 'Segoe UI Symbol' sangat bagus di Windows untuk menangani emoji/simbol
    test_font = QFont("Segoe UI", 12)
    test_font.setFamilies(["Segoe UI", "Segoe UI Symbol", "Cascadia Code", "Monospace"])
    
    window.setAttribute(Qt.WidgetAttribute.WA_DontCreateNativeAncestors)
    window.resize(1280, 760)
    
    window.command_input.setFont(test_font)
    window.output_panel.setFont(test_font)
    
    window.output_panel.clear()
    # Simulasi prompt ala Oh My Posh kamu
    window.output_panel.append("⚡ Lycus@Nourivex ~  main")
    window.output_panel.append("> open notepad")
    window.output_panel.append("[Calm] Membuka 'notepad' menggunakan 'notepad'. PID: 12345.")
    
    # Berikan waktu lebih bagi engine 'offscreen' untuk proses rendering teks
    for _ in range(10):
        app.processEvents()
        QTest.qWait(100)

def test_window_snapshot_compare_or_archive() -> None:
    # Menggunakan 'offscreen' lebih stabil untuk font rendering dibanding 'minimal'
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["QT_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

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
    window.show()
    
    # Tambahkan jeda kecil setelah show sebelum memanipulasi UI
    QTest.qWait(100)
    
    _prepare_readable_snapshot(window, app)

    # Ambil snapshot
    captured = window.grab()
    
    if captured.isNull():
        raise RuntimeError("Gagal mengambil snapshot (QPixmap is null).")
        
    success = captured.save(str(current_file), "PNG")
    if not success:
        raise RuntimeError(f"Gagal menyimpan file ke {current_file}")
        
    shutil.copyfile(current_file, archive_file)

    if not baseline_file.exists():
        shutil.copyfile(current_file, baseline_file)
        print(f"\nBaseline baru dibuat: {baseline_file}")
    else:
        # Bandingkan hasil
        assert _images_equal(current_file, baseline_file) is True

    window.close()