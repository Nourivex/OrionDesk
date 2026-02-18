from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from ui.theme_tokens import ThemeTokens


class ChatBubbleWidget(QFrame):
    def __init__(
        self,
        text: str,
        is_user: bool,
        theme: ThemeTokens,
        subtitle: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._is_user = is_user
        self._subtitle = subtitle
        self._theme = theme
        self._timestamp = datetime.now().strftime("%H:%M:%S")

        self.setObjectName("chatBubbleRow")
        row = QHBoxLayout(self)
        row.setContentsMargins(4, 4, 4, 4)
        row.setSpacing(theme.spacing_sm)

        self.avatar = QLabel("Y" if is_user else "AI", self)
        self.avatar.setObjectName("chatAvatar")
        self.avatar.setFixedSize(24, 24)

        self.bubble = QFrame(self)
        self.bubble.setObjectName("chatBubble")
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(10, 8, 10, 8)
        bubble_layout.setSpacing(4)

        self.header = QLabel(self.bubble)
        self.header.setObjectName("chatMeta")
        self.header.setText(f"{'You' if is_user else 'OrionDesk'} · {self._timestamp}")

        self.message_label = QLabel(text, self.bubble)
        self.message_label.setObjectName("chatMessage")
        self.message_label.setWordWrap(True)

        bubble_layout.addWidget(self.header)
        bubble_layout.addWidget(self.message_label)

        if subtitle:
            self.subtitle_label = QLabel(subtitle, self.bubble)
            self.subtitle_label.setObjectName("chatSubtitle")
            self.subtitle_label.setWordWrap(True)
            bubble_layout.addWidget(self.subtitle_label)
        else:
            self.subtitle_label = None

        if is_user:
            row.addStretch()
            row.addWidget(self.bubble, 0)
            row.addWidget(self.avatar)
        else:
            row.addWidget(self.avatar)
            row.addWidget(self.bubble, 0)
            row.addStretch()

        self.update_theme(theme)

    def update_theme(self, theme: ThemeTokens) -> None:
        self._theme = theme
        bubble_bg = theme.tab_active_bg if self._is_user else theme.card_bg
        avatar_bg = theme.input_focus if self._is_user else theme.button_bg

        self.avatar.setStyleSheet(
            (
                f"background-color: {avatar_bg};"
                f"color: {theme.button_text};"
                "border-radius: 8px;"
                "font-size: 10px;"
                "font-weight: 700;"
                "qproperty-alignment: AlignCenter;"
            )
        )
        self.bubble.setStyleSheet(
            (
                f"background-color: {bubble_bg};"
                f"border: 1px solid {theme.panel_border};"
                f"border-radius: {theme.radius_md + 8}px;"
            )
        )
        self.header.setStyleSheet(
            f"font-size: 10px; font-weight: 700; color: {theme.text_secondary};"
        )
        self.message_label.setStyleSheet(
            f"font-size: 13px; color: {theme.text_primary};"
        )
        if self.subtitle_label is not None:
            self.subtitle_label.setStyleSheet(
                f"font-size: 11px; color: {theme.text_secondary};"
            )


class ChatSurface(QScrollArea):
    def __init__(self, theme: ThemeTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._history: list[tuple[str, bool, str | None]] = []

        self.setWidgetResizable(True)
        self.setObjectName("outputPanel")
        self.container = QWidget(self)
        self.messages_layout = QVBoxLayout(self.container)
        self.messages_layout.setContentsMargins(8, 8, 8, 8)
        self.messages_layout.setSpacing(2)
        self.messages_layout.addStretch()
        self.setWidget(self.container)
        self._apply_frame_theme()

    def append(self, text: str) -> None:
        self.add_message(text=text, is_user=False)

    def add_message(self, text: str, is_user: bool, subtitle: str | None = None) -> None:
        bubble = ChatBubbleWidget(text=text, is_user=is_user, theme=self._theme, subtitle=subtitle, parent=self.container)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        self._history.append((text, is_user, subtitle))
        self._scroll_to_bottom()

    def clear(self) -> None:
        self._history = []
        for index in reversed(range(self.messages_layout.count() - 1)):
            item = self.messages_layout.itemAt(index)
            widget = item.widget()
            if widget is not None:
                self.messages_layout.removeWidget(widget)
                widget.deleteLater()

    def toPlainText(self) -> str:
        lines = []
        for text, is_user, _subtitle in self._history:
            prefix = "You" if is_user else "OrionDesk"
            lines.append(f"{prefix}: {text}")
        return "\n".join(lines)

    def set_theme(self, theme: ThemeTokens) -> None:
        self._theme = theme
        self._apply_frame_theme()
        for index in range(self.messages_layout.count() - 1):
            item = self.messages_layout.itemAt(index)
            widget = item.widget()
            if isinstance(widget, ChatBubbleWidget):
                widget.update_theme(theme)

    def _apply_frame_theme(self) -> None:
        self.setStyleSheet(
            (
                f"QScrollArea {{ background-color: {self._theme.output_bg};"
                f"border: 1px solid {self._theme.panel_border};"
                f"border-radius: {self._theme.radius_md}px; }}"
            )
        )
        self.container.setStyleSheet(f"background-color: {self._theme.output_bg};")

    def _scroll_to_bottom(self) -> None:
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
