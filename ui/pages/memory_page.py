from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QStyle, QTextBrowser, QVBoxLayout, QWidget

from ui.theme_tokens import ThemeTokens


class MemoryPage(QWidget):
    refreshRequested = Signal()

    def __init__(self, theme: ThemeTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        layout.setSpacing(theme.spacing_sm)

        title = QLabel("Memory Intelligence", self)
        title.setObjectName("placeholderTitle")

        summary_card = QFrame(self)
        summary_card.setObjectName("topCard")
        summary_layout = QGridLayout(summary_card)
        summary_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        summary_layout.setHorizontalSpacing(theme.spacing_md)
        summary_layout.setVerticalSpacing(theme.spacing_sm)

        total_title = QLabel("⚡ Total Commands", summary_card)
        total_title.setObjectName("sectionHint")
        self.total_commands_value = QLabel("0", summary_card)
        self.total_commands_value.setObjectName("statsValue")

        top_title = QLabel("📊 Top Command", summary_card)
        top_title.setObjectName("sectionHint")
        self.top_command_value = QLabel("-", summary_card)
        self.top_command_value.setObjectName("sectionTitle")

        refresh_title = QLabel("🕒 Last Refresh", summary_card)
        refresh_title.setObjectName("sectionHint")
        self.last_refresh_value = QLabel("-", summary_card)
        self.last_refresh_value.setObjectName("sectionTitle")

        summary_layout.addWidget(total_title, 0, 0)
        summary_layout.addWidget(top_title, 0, 1)
        summary_layout.addWidget(refresh_title, 0, 2)
        summary_layout.addWidget(self.total_commands_value, 1, 0)
        summary_layout.addWidget(self.top_command_value, 1, 1)
        summary_layout.addWidget(self.last_refresh_value, 1, 2)

        button_row = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Memory", self)
        self.refresh_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.refresh_button.clicked.connect(self.refreshRequested.emit)
        button_row.addWidget(self.refresh_button)
        button_row.addStretch()

        insight_grid = QGridLayout()
        insight_grid.setHorizontalSpacing(theme.spacing_md)
        insight_grid.setVerticalSpacing(theme.spacing_sm)

        recent_card = QFrame(self)
        recent_card.setObjectName("topCard")
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        recent_layout.setSpacing(theme.spacing_sm)
        recent_title = QLabel("Recent Activity (5)", recent_card)
        recent_title.setObjectName("sectionTitle")
        self.recent_activity_list = QListWidget(recent_card)
        self.recent_activity_list.setObjectName("memoryRecentList")
        recent_layout.addWidget(recent_title)
        recent_layout.addWidget(self.recent_activity_list)

        risk_card = QFrame(self)
        risk_card.setObjectName("topCard")
        risk_layout = QVBoxLayout(risk_card)
        risk_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        risk_layout.setSpacing(theme.spacing_sm)
        risk_title = QLabel("Risk Insights", risk_card)
        risk_title.setObjectName("sectionTitle")
        self.safe_mode_triggers_value = QLabel("0", risk_card)
        self.safe_mode_triggers_value.setObjectName("sectionHint")
        self.blocked_count_value = QLabel("0", risk_card)
        self.blocked_count_value.setObjectName("sectionHint")
        self.warning_count_value = QLabel("0", risk_card)
        self.warning_count_value.setObjectName("sectionHint")
        self.session_start_value = QLabel("-", risk_card)
        self.session_start_value.setObjectName("sectionHint")
        self.session_duration_value = QLabel("-", risk_card)
        self.session_duration_value.setObjectName("sectionHint")
        risk_layout.addWidget(risk_title)
        risk_layout.addWidget(self.safe_mode_triggers_value)
        risk_layout.addWidget(self.blocked_count_value)
        risk_layout.addWidget(self.warning_count_value)
        risk_layout.addWidget(self.session_start_value)
        risk_layout.addWidget(self.session_duration_value)
        risk_layout.addStretch()

        insight_grid.addWidget(recent_card, 0, 0)
        insight_grid.addWidget(risk_card, 0, 1)

        self.memory_info = QTextBrowser(self)
        self.memory_info.setObjectName("memoryInfo")

        layout.addWidget(title)
        layout.addWidget(summary_card)
        layout.addLayout(button_row)
        layout.addLayout(insight_grid)
        layout.addWidget(self.memory_info)
