from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QTextBrowser, QVBoxLayout, QWidget

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

        hero_card = QFrame(self)
        hero_card.setObjectName("topCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        hero_layout.setSpacing(theme.spacing_sm)

        self.about_headline = QLabel("Local-First OS Intelligence Layer", hero_card)
        self.about_headline.setObjectName("sectionTitle")
        self.about_subtitle = QLabel("Policy-driven • Modular • Fast command orchestration", hero_card)
        self.about_subtitle.setObjectName("sectionHint")
        self.about_subtitle.setWordWrap(True)
        hero_layout.addWidget(self.about_headline)
        hero_layout.addWidget(self.about_subtitle)

        self.about_info = QTextBrowser(self)
        self.about_info.setObjectName("aboutInfo")
        layout.addWidget(title)
        layout.addWidget(hero_card)
        layout.addWidget(self.about_info)
