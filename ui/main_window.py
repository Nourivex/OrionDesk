from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
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
from PySide6.QtCore import Qt

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
        main_layout.setContentsMargins(16, 14, 16, 16)
        main_layout.setSpacing(10)

        title_bar = QHBoxLayout()
        title_bar.setSpacing(8)
        self.title_label = QLabel("OrionDesk", self)
        self.title_label.setObjectName("titleLabel")
        self.subtitle_label = QLabel("Windows 11 Personal OS Agent", self)
        self.subtitle_label.setObjectName("subtitleLabel")
        title_bar.addWidget(self.title_label)
        title_bar.addWidget(self.subtitle_label)
        title_bar.addStretch()

        top_card = QFrame(self)
        top_card.setObjectName("topCard")
        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(12, 10, 12, 10)
        top_layout.setSpacing(10)

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
        self.execute_button.setMinimumWidth(120)
        self.output_panel = QTextEdit(self)
        self.output_panel.setReadOnly(True)
        self.output_panel.setObjectName("outputPanel")

        top_layout.addLayout(persona_layout)
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.execute_button)
        top_layout.addLayout(command_layout)

        main_layout.addLayout(title_bar)
        main_layout.addWidget(top_card)
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
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            """
            QMainWindow { 
                background-color: #1b1f2a;
                color: #f1f4fb;
            }
            QLabel { color: #e7eaf2; font-weight: 600; }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: 700;
                color: #ffffff;
            }
            QLabel#subtitleLabel {
                font-size: 11px;
                color: #9ea7be;
                font-weight: 500;
            }
            QFrame#topCard {
                background-color: #202636;
                border: 1px solid #313a52;
                border-radius: 14px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #272e42;
                color: #f4f6fc;
                border: 1px solid #39425d;
                border-radius: 11px;
                padding: 8px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #5a8bff;
            }
            QPushButton {
                background-color: #4f8dfd;
                color: white;
                border: none;
                border-radius: 11px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #669cff; }
            QPushButton:pressed { background-color: #3f7de7; }
            QTextEdit#outputPanel {
                border-radius: 14px;
                padding: 10px;
            }
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