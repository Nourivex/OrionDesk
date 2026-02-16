from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

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

    def _setup_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        command_layout = QHBoxLayout()

        self.command_input = QLineEdit(self)
        self.command_input.setPlaceholderText("Masukkan command, contoh: open vscode")

        self.execute_button = QPushButton("Execute", self)
        self.output_panel = QTextEdit(self)
        self.output_panel.setReadOnly(True)

        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.execute_button)
        main_layout.addLayout(command_layout)
        main_layout.addWidget(self.output_panel)

        self.execute_button.clicked.connect(self._handle_execute)
        self.command_input.returnPressed.connect(self._handle_execute)

    def _handle_execute(self) -> None:
        command = self.command_input.text()
        response = self.router.route(command)
        styled_response = self.persona_engine.format_output(response)

        if command.strip():
            self.output_panel.append(f"> {command}")
        self.output_panel.append(styled_response)
        self.output_panel.append("")
        self.command_input.clear()