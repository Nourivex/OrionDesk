from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QStyle, QTextBrowser, QVBoxLayout, QWidget

from ui.theme_tokens import ThemeTokens


class MemoryPage(QWidget):
    refreshRequested = Signal()

    def __init__(self, theme: ThemeTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.spacing_md,
            theme.spacing_md,
            theme.spacing_md,
            theme.spacing_md,
        )
        title = QLabel("Memory Snapshot", self)
        title.setObjectName("placeholderTitle")
        self.refresh_button = QPushButton("Refresh Memory", self)
        self.refresh_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.refresh_button.clicked.connect(self.refreshRequested.emit)
        self.memory_info = QTextBrowser(self)
        self.memory_info.setObjectName("memoryInfo")
        layout.addWidget(title)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.memory_info)
