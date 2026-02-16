from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QFont

from core.router import CommandRouter
from persona.persona_engine import PersonaEngine


class MainWindow(QMainWindow):
    def __init__(self, router: CommandRouter, persona_engine: PersonaEngine | None = None) -> None:
        super().__init__()
        self.router = router
        self.persona_engine = persona_engine or PersonaEngine(persona_name="calm")
        self.setWindowTitle("OrionDesk")
        self.resize(800, 480)
        self._setup_ui()
        self._apply_windows11_style()

    def _setup_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        persona_layout = QHBoxLayout()
        command_layout = QHBoxLayout()

        self.persona_label = QLabel("Persona:", self)
        self.persona_selector = QComboBox(self)
        self.persona_selector.addItems(["calm", "hacker"])
        self.persona_selector.setCurrentText(self.persona_engine.persona_name)

        persona_layout.addWidget(self.persona_label)
        persona_layout.addWidget(self.persona_selector)
        persona_layout.addStretch()

        self.command_input = QLineEdit(self)
        self.command_input.setPlaceholderText("Masukkan command, contoh: open vscode")

        self.execute_button = QPushButton("Execute", self)
        self.output_panel = QTextEdit(self)
        self.output_panel.setReadOnly(True)

        main_layout.addLayout(persona_layout)
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.execute_button)
        main_layout.addLayout(command_layout)
        main_layout.addWidget(self.output_panel)

        self.execute_button.clicked.connect(self._handle_execute)
        self.command_input.returnPressed.connect(self._handle_execute)
        self.persona_selector.currentTextChanged.connect(self._handle_persona_change)

    def _handle_execute(self) -> None:
        command = self.command_input.text()
        result = self.router.execute(command)

        if command.strip():
            self.output_panel.append(f"> {command}")

        if result.requires_confirmation:
            warning = self.persona_engine.format_warning(
                result.message,
                detail=f"Command: {result.pending_command}",
            )
            self.output_panel.append(warning)
            approved = self._show_confirmation(result.pending_command or command)
            response = self.router.confirm_pending(approved)
            styled_response = self.persona_engine.format_output(response.message)
            self.output_panel.append(styled_response)
        else:
            styled_response = self.persona_engine.format_output(result.message)
            self.output_panel.append(styled_response)

        self.output_panel.append("")
        self.command_input.clear()

    def _handle_persona_change(self, persona_name: str) -> None:
        self.persona_engine.set_persona(persona_name)
        self.output_panel.append(self.persona_engine.format_output(f"Persona aktif: {persona_name}"))
        self.output_panel.append("")

    def _apply_windows11_style(self) -> None:
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            """
            QMainWindow { background-color: #1f2128; }
            QLabel { color: #e4e7ef; font-weight: 600; }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #2a2d37;
                color: #f4f6fc;
                border: 1px solid #3a3f4d;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton {
                background-color: #3f8cff;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #5298ff; }
            QPushButton:pressed { background-color: #2f76e7; }
            """
        )

    def _show_confirmation(self, command: str) -> bool:
        reply = QMessageBox.question(
            self,
            "Konfirmasi Safe Mode",
            f"Command berisiko terdeteksi:\n{command}\n\nLanjutkan aksi ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes