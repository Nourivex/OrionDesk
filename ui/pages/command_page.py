from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QStyle, QVBoxLayout, QWidget

from ui.chat_surface import ChatSurface
from ui.theme_tokens import ThemeTokens


class CommandPage(QWidget):
    quickActionRequested = Signal(str)
    suggestionRequested = Signal(str)
    clearChatRequested = Signal()

    def __init__(self, theme: ThemeTokens, persona_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(theme.spacing_sm + 2)

        sidebar = QFrame(self)
        sidebar.setObjectName("commandSidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(theme.spacing_sm + 2)

        persona_card = QFrame(sidebar)
        persona_card.setObjectName("personaCard")
        persona_layout = QVBoxLayout(persona_card)
        persona_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        persona_layout.setSpacing(theme.spacing_sm)
        persona_title = QLabel("Persona", persona_card)
        persona_title.setObjectName("sectionTitle")
        self.persona_selector = QComboBox(persona_card)
        self.persona_selector.addItems(["calm", "professional", "hacker", "friendly", "minimal"])
        selected = persona_name if persona_name in {"calm", "professional", "hacker", "friendly", "minimal"} else "calm"
        self.persona_selector.setCurrentText(selected)
        persona_hint = QLabel("Choose AI personality style", persona_card)
        persona_hint.setObjectName("sectionHint")
        persona_hint.setWordWrap(True)
        persona_layout.addWidget(persona_title)
        persona_layout.addWidget(self.persona_selector)
        persona_layout.addWidget(persona_hint)

        quick_card = QFrame(sidebar)
        quick_card.setObjectName("quickActionsCard")
        quick_layout = QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        quick_layout.setSpacing(theme.spacing_sm)
        quick_title = QLabel("Quick Actions", quick_card)
        quick_title.setObjectName("sectionTitle")
        quick_layout.addWidget(quick_title)
        self.quick_action_buttons = []
        for label, command in [
            ("Open VSCode", "open vscode"),
            ("Open Notepad", "open notepad"),
            ("Focus Mode", "mode focus on"),
            ("System Status", "system status"),
            ("Clear Chat", "clear chat"),
        ]:
            button = QPushButton(label, quick_card)
            button.setObjectName("quickActionButton")
            button.clicked.connect(lambda _checked=False, cmd=command: self.quickActionRequested.emit(cmd))
            quick_layout.addWidget(button)
            self.quick_action_buttons.append(button)
        quick_layout.addStretch()

        stats_card = QFrame(sidebar)
        stats_card.setObjectName("commandStatsCard")
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        stats_layout.setSpacing(theme.spacing_md)

        message_tile = QVBoxLayout()
        self.message_count_label = QLabel("0", stats_card)
        self.message_count_label.setObjectName("statsValue")
        message_text = QLabel("Messages", stats_card)
        message_text.setObjectName("statsLabel")
        message_tile.addWidget(self.message_count_label, alignment=Qt.AlignmentFlag.AlignCenter)
        message_tile.addWidget(message_text, alignment=Qt.AlignmentFlag.AlignCenter)

        command_tile = QVBoxLayout()
        self.command_count_label = QLabel("0", stats_card)
        self.command_count_label.setObjectName("statsValue")
        command_text = QLabel("Commands", stats_card)
        command_text.setObjectName("statsLabel")
        command_tile.addWidget(self.command_count_label, alignment=Qt.AlignmentFlag.AlignCenter)
        command_tile.addWidget(command_text, alignment=Qt.AlignmentFlag.AlignCenter)

        stats_layout.addLayout(message_tile)
        stats_layout.addLayout(command_tile)

        sidebar_layout.addWidget(persona_card)
        sidebar_layout.addWidget(quick_card)
        sidebar_layout.addWidget(stats_card)

        chat_area = QWidget(self)
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(theme.spacing_sm + 2)

        self.output_panel = ChatSurface(theme, chat_area)

        input_card = QFrame(chat_area)
        input_card.setObjectName("inputShellCard")
        input_layout = QHBoxLayout(input_card)
        input_layout.setContentsMargins(theme.spacing_sm, theme.spacing_sm, theme.spacing_sm, theme.spacing_sm)
        input_layout.setSpacing(theme.spacing_sm)

        self.command_input = QLineEdit(chat_area)
        self.command_input.setPlaceholderText("Ketik command Anda di sini...")
        self.clear_chat_button = QPushButton("Clear", chat_area)
        self.clear_chat_button.setObjectName("clearChatButton")
        self.clear_chat_button.clicked.connect(self.clearChatRequested.emit)
        self.execute_button = QPushButton("Send", chat_area)
        self.execute_button.setObjectName("sendButton")
        self.execute_button.setMinimumWidth(110)
        self.execute_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))

        input_layout.addWidget(self.command_input, 1)
        input_layout.addWidget(self.clear_chat_button)
        input_layout.addWidget(self.execute_button)

        suggestion_row = QHBoxLayout()
        suggestion_row.setSpacing(theme.spacing_sm)
        suggestion_title = QLabel("Suggestions:", chat_area)
        suggestion_title.setObjectName("sectionHint")
        suggestion_row.addWidget(suggestion_title)
        self.suggestion_buttons = []
        for command in ["capability system info", "clip show", "mode game on"]:
            chip = QPushButton(command, chat_area)
            chip.setObjectName("suggestionChip")
            chip.clicked.connect(lambda _checked=False, cmd=command: self.suggestionRequested.emit(cmd))
            suggestion_row.addWidget(chip)
            self.suggestion_buttons.append(chip)
        suggestion_row.addStretch()

        self.command_suggestions = QLabel(chat_area)
        self.command_suggestions.setObjectName("commandSuggestions")
        self.command_suggestions.setWordWrap(True)
        self.command_hint_label = QLabel(chat_area)
        self.command_hint_label.setObjectName("commandHint")
        self.command_hint_label.setWordWrap(True)
        self.intent_hint_label = QLabel(chat_area)
        self.intent_hint_label.setObjectName("intentHint")
        self.intent_hint_label.setWordWrap(True)
        self.loading_label = QLabel("", chat_area)
        self.loading_label.setObjectName("loadingHint")
        self.loading_label.setWordWrap(True)

        self.command_input.setAccessibleName("command-input")
        self.persona_selector.setAccessibleName("persona-selector")
        self.execute_button.setAccessibleName("execute-button")
        self.output_panel.setAccessibleName("output-panel")

        chat_layout.addWidget(self.output_panel, 1)
        chat_layout.addWidget(input_card)
        chat_layout.addLayout(suggestion_row)
        chat_layout.addWidget(self.command_suggestions)
        chat_layout.addWidget(self.command_hint_label)
        chat_layout.addWidget(self.intent_hint_label)
        chat_layout.addWidget(self.loading_label)

        layout.addWidget(sidebar)
        layout.addWidget(chat_area, 1)
