from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat


@dataclass(frozen=True)
class HighlightRule:
    token: str
    color: str


class OutputHighlighter(QSyntaxHighlighter):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.rules = [
            HighlightRule(token="[Calm]", color="#9BE7A7"),
            HighlightRule(token="[Hacker]", color="#7CFF8E"),
            HighlightRule(token="[SUCCESS]", color="#9BE7A7"),
            HighlightRule(token="[INVALID]", color="#FFCC8E"),
            HighlightRule(token="[BLOCKED]", color="#FF9DA3"),
            HighlightRule(token="Error", color="#FF9DA3"),
            HighlightRule(token="Blocked", color="#FF9DA3"),
            HighlightRule(token="ditolak", color="#FF9DA3"),
            HighlightRule(token="invalid", color="#FF9DA3"),
            HighlightRule(token="success", color="#9BE7A7"),
        ]

    def highlightBlock(self, text: str) -> None:
        for rule in self.rules:
            start = text.lower().find(rule.token.lower())
            if start < 0:
                continue

            fmt = QTextCharFormat()
            fmt.setForeground(QColor(rule.color))
            self.setFormat(start, len(rule.token), fmt)
