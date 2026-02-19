from __future__ import annotations

from datetime import datetime

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
        result = self.router.execute_with_enhanced_response(self.command)
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


def memory_insight_payload(router: CommandRouter) -> dict:
    summary = router.memory_summary()
    top_commands = summary.get("top_commands", [])
    total_commands = sum(count for _, count in top_commands)
    session_entries = router.session_layer.entries
    recent_entries = list(reversed(router.session_layer.recent(limit=5)))

    lines = ["Top Commands:"]
    if not top_commands:
        lines.append("- (belum ada data)")
        top_command_label = "-"
    else:
        for command, count in top_commands:
            lines.append(f"- {command}: {count}")
        top_command_label = f"{top_commands[0][0]} ({top_commands[0][1]})"

    blocked_count = sum(1 for entry in session_entries if entry.status in {"blocked", "invalid", "failed"})
    pending_count = sum(1 for entry in session_entries if entry.status == "pending_confirmation")
    warning_count = sum(1 for entry in session_entries if entry.status in {"pending_confirmation", "cancelled"})

    if session_entries:
        session_start = datetime.fromisoformat(session_entries[0].timestamp).astimezone()
        now_local = datetime.now().astimezone()
        elapsed = now_local - session_start
        duration = f"{elapsed.seconds // 3600:02d}:{(elapsed.seconds % 3600) // 60:02d}:{elapsed.seconds % 60:02d}"
        offset_hours = int(session_start.utcoffset().total_seconds() // 3600)
        gmt_label = f"GMT{offset_hours:+d}"
        session_start_label = f"{session_start.strftime('%H:%M:%S')} {gmt_label}"
    else:
        duration = "-"
        session_start_label = "-"

    recent_rows = ["(belum ada aktivitas)"] if not recent_entries else [
        (
            f"{datetime.fromisoformat(entry.timestamp).astimezone().strftime('%H:%M:%S')} "
            f"| {entry.status.upper()} | {entry.command}"
        )
        for entry in recent_entries
    ]

    now_local = datetime.now().astimezone()
    offset_hours = int(now_local.utcoffset().total_seconds() // 3600)
    return {
        "total_commands": total_commands,
        "top_command_label": top_command_label,
        "blocked_count": blocked_count,
        "pending_count": pending_count,
        "warning_count": warning_count,
        "session_start_label": session_start_label,
        "duration": duration,
        "recent_rows": recent_rows,
        "top_command_lines": "\n".join(lines),
        "refreshed_at": f"{now_local.strftime('%H:%M:%S')} GMT{offset_hours:+d}",
    }
