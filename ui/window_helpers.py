from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from core.router import CommandRouter
from ui.theme_tokens import ThemeTokens


class CommandWorker(QObject):
    finished = Signal(str, object)

    def __init__(self, router: CommandRouter, command: str) -> None:
        super().__init__()
        self.router = router
        self.command = command

    def run(self) -> None:
        result = self.router.execute(self.command)
        self.finished.emit(self.command, result)


def with_status_badge(message: str) -> str:
    lowered = message.lower()
    if "warning" in lowered or "konfirmasi manual" in lowered:
        return f"[WARNING] {message}"
    if "ditolak" in lowered or "blocked" in lowered or "error" in lowered:
        return f"[BLOCKED] {message}"
    if "format salah" in lowered or "invalid" in lowered:
        return f"[INVALID] {message}"
    return f"[SUCCESS] {message}"


def show_confirmation_dialog(parent, theme: ThemeTokens, command: str) -> bool:
    dialog = QMessageBox(parent)
    dialog.setWindowTitle("Konfirmasi Safe Mode")
    dialog.setText(f"Command berisiko terdeteksi:\n{command}\n\nLanjutkan aksi ini?")
    dialog.setIcon(QMessageBox.Icon.Warning)
    dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    dialog.setDefaultButton(QMessageBox.StandardButton.No)
    dialog.setStyleSheet(
        f"""
        QMessageBox {{ background-color: {theme.window_bg}; color: {theme.text_primary}; }}
        QLabel {{ color: {theme.text_primary}; }}
        QPushButton {{
            background-color: {theme.button_bg};
            color: {theme.button_text};
            border-radius: {theme.radius_md}px;
            padding: {theme.spacing_sm}px {theme.spacing_md}px;
        }}
        QPushButton:hover {{ background-color: {theme.button_hover}; }}
        QPushButton:pressed {{ background-color: {theme.button_pressed}; }}
        """
    )
    reply = dialog.exec()
    return reply == int(QMessageBox.StandardButton.Yes)
