from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget

from ui.theme_tokens import ThemeTokens


class AboutPage(QWidget):
    def __init__(self, theme: ThemeTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.spacing_md,
            theme.spacing_md,
            theme.spacing_md,
            theme.spacing_md,
        )
        title = QLabel("About OrionDesk", self)
        title.setObjectName("placeholderTitle")
        self.about_info = QTextBrowser(self)
        self.about_info.setObjectName("aboutInfo")
        layout.addWidget(title)
        layout.addWidget(self.about_info)
