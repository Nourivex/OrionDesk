from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer
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
        self.avatar.setFixedSize(30, 30)

        self.bubble = QFrame(self)
        self.bubble.setObjectName("chatBubble")
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(12, 10, 12, 10)
        bubble_layout.setSpacing(6)

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
        message_color = theme.text_primary

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
                f"background: {bubble_bg};"
                f"border: none;"
                "border-top-left-radius: 8px;"
                "border-top-right-radius: 8px;"
                "border-bottom-left-radius: 18px;"
                "border-bottom-right-radius: 18px;"
            )
        )
        if self._is_user:
            self.bubble.setStyleSheet(
                (
                    f"background: {bubble_bg};"
                    "border: none;"
                    "border-top-left-radius: 18px;"
                    "border-top-right-radius: 8px;"
                    "border-bottom-left-radius: 18px;"
                    "border-bottom-right-radius: 18px;"
                )
            )
        self.header.setStyleSheet(
            f"font-size: 10px; font-weight: 500; color: {theme.text_muted}; margin-bottom: 4px;"
        )
        self.message_label.setStyleSheet(
            f"font-size: 13px; color: {message_color};"
        )
        if self.subtitle_label is not None:
            self.subtitle_label.setStyleSheet(
                f"font-size: 11px; color: {theme.text_muted};"
            )


class ChatSurface(QScrollArea):
    def __init__(self, theme: ThemeTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._history: list[tuple[str, bool, str | None]] = []
        self._animations: list[QPropertyAnimation] = []
        self._enable_animations = False
        self._max_messages = 200
        self._typing_dots = 0
        self._typing_bubble: ChatBubbleWidget | None = None
        self._typing_stage = "impact_assessment"
        self._typing_expected_ms = 150.0
        self._typing_timer = QTimer(self)
        self._typing_timer.setInterval(300)
        self._typing_timer.timeout.connect(self._tick_typing)

        self.setWidgetResizable(True)
        self.setObjectName("outputPanel")
        self.container = QWidget(self)
        self.messages_layout = QVBoxLayout(self.container)
        self.messages_layout.setContentsMargins(12, 16, 12, 16)
        self.messages_layout.setSpacing(12)
        self.typing_indicator = QLabel("AI is thinking", self.container)
        self.typing_indicator.setObjectName("typingIndicator")
        self.typing_indicator.setVisible(False)
        self.messages_layout.addWidget(self.typing_indicator)
        self.messages_layout.addStretch()
        self.setWidget(self.container)
        self._apply_frame_theme()

    def append(self, text: str) -> None:
        self.add_message(text=text, is_user=False)

    def add_message(self, text: str, is_user: bool, subtitle: str | None = None) -> None:
        should_follow_tail = self._is_near_bottom()
        bubble = ChatBubbleWidget(text=text, is_user=is_user, theme=self._theme, subtitle=subtitle, parent=self.container)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        self._history.append((text, is_user, subtitle))
        self._prune_old_messages()
        if not should_follow_tail:
            return
        if self._enable_animations and self.isVisible():
            self._animate_bubble_in(bubble, is_user)
            QTimer.singleShot(0, self._animate_scroll_to_bottom)
        else:
            QTimer.singleShot(0, self._scroll_to_bottom)

    def clear(self) -> None:
        self._history = []
        self.hide_typing_indicator()
        for index in reversed(range(self.messages_layout.count() - 1)):
            item = self.messages_layout.itemAt(index)
            widget = item.widget()
            if widget is not None:
                self.messages_layout.removeWidget(widget)
                widget.deleteLater()
        try:
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, self.typing_indicator)
        except RuntimeError:
            self._typing_timer.stop()

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

    def scroll_to_latest(self) -> None:
        self._scroll_to_bottom()
        QTimer.singleShot(0, self._scroll_to_bottom)
        QTimer.singleShot(40, self._scroll_to_bottom)

    def show_typing_indicator(self, stage: str = "impact_assessment", expected_ms: float = 150.0) -> None:
        self._typing_dots = 0
        self._typing_stage = self._normalize_stage(stage)
        self._typing_expected_ms = max(1.0, float(expected_ms))
        try:
            self.typing_indicator.setVisible(True)
            self.typing_indicator.setText(self._typing_message())
            if self._typing_bubble is None:
                self._typing_bubble = ChatBubbleWidget(
                    text=self._typing_message(),
                    is_user=False,
                    theme=self._theme,
                    subtitle="typing",
                    parent=self.container,
                )
                self._typing_bubble.setObjectName("chatTypingRow")
                self.messages_layout.insertWidget(self.messages_layout.count() - 1, self._typing_bubble)
        except RuntimeError:
            self._typing_timer.stop()
            return
        self._typing_timer.setInterval(self._typing_interval_ms())
        if not self._typing_timer.isActive():
            self._typing_timer.start()
        self.scroll_to_latest()

    def update_typing_stage(self, stage: str, elapsed_ms: float) -> None:
        self._typing_stage = self._normalize_stage(stage)
        self._typing_expected_ms = max(1.0, float(elapsed_ms))
        if self.typing_indicator.isHidden():
            self.show_typing_indicator(stage=self._typing_stage, expected_ms=self._typing_expected_ms)
            return
        self._typing_timer.setInterval(self._typing_interval_ms())
        try:
            text = self._typing_message()
            self.typing_indicator.setText(text)
            if self._typing_bubble is not None:
                self._typing_bubble.message_label.setText(text)
        except RuntimeError:
            self._typing_timer.stop()

    def hide_typing_indicator(self, final_state: str | None = None) -> None:
        self._typing_timer.stop()
        try:
            self.typing_indicator.setVisible(False)
        except RuntimeError:
            pass
        if self._typing_bubble is not None:
            self.messages_layout.removeWidget(self._typing_bubble)
            self._typing_bubble.deleteLater()
            self._typing_bubble = None

    def _tick_typing(self) -> None:
        self._typing_dots = (self._typing_dots + 1) % 4
        try:
            text = self._typing_message()
            self.typing_indicator.setText(text)
            if self._typing_bubble is not None:
                self._typing_bubble.message_label.setText(text)
        except RuntimeError:
            self._typing_timer.stop()

    def _prune_old_messages(self) -> None:
        while len(self._history) > self._max_messages:
            self._history.pop(0)
            for index in range(self.messages_layout.count()):
                item = self.messages_layout.itemAt(index)
                widget = item.widget()
                if widget is not None and widget.objectName() == "chatBubbleRow":
                    self.messages_layout.removeWidget(widget)
                    widget.deleteLater()
                    break

    def _apply_frame_theme(self) -> None:
        self.setStyleSheet(
            (
                f"QScrollArea {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
                f"stop:0 {self._theme.tab_bg}, stop:1 {self._theme.output_bg});"
                f"border: 1px solid {self._theme.panel_border};"
                f"border-radius: {self._theme.radius_md}px; }}"
                f"QScrollBar:vertical {{"
                f"background: transparent; width: 7px; margin: 4px 2px 4px 2px; }}"
                f"QScrollBar::handle:vertical {{"
                f"background: {self._theme.panel_border}; min-height: 28px; border-radius: 4px; }}"
                f"QScrollBar::handle:vertical:hover {{ background: {self._theme.input_focus}; }}"
                f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}"
            )
        )
        self.container.setStyleSheet("background-color: transparent;")

    def _scroll_to_bottom(self) -> None:
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _animate_bubble_in(self, bubble: QWidget, is_user: bool) -> None:
        start_geometry = bubble.geometry()
        offset = 8 if is_user else -8
        slide = QPropertyAnimation(bubble, b"geometry", self)
        slide.setDuration(180)
        slide.setStartValue(start_geometry.translated(offset, 0))
        slide.setEndValue(start_geometry)
        slide.setEasingCurve(QEasingCurve.Type.InOutQuad)

        slide.start()
        self._animations.append(slide)

    def _animate_scroll_to_bottom(self) -> None:
        scrollbar = self.verticalScrollBar()
        animation = QPropertyAnimation(scrollbar, b"value", self)
        animation.setDuration(180)
        animation.setStartValue(scrollbar.value())
        animation.setEndValue(scrollbar.maximum())
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()
        self._animations.append(animation)

    def _is_near_bottom(self) -> bool:
        scrollbar = self.verticalScrollBar()
        if scrollbar.maximum() <= 0:
            return True
        return scrollbar.maximum() - scrollbar.value() <= 24

    def _typing_message(self) -> str:
        dots = "." * self._typing_dots
        if self._typing_stage == "impact_assessment":
            return f"AI impact assessment{dots}"
        if self._typing_stage == "generation":
            return f"AI ghost writing{dots}"
        if self._typing_stage == "final_validation":
            pulse = "|" if self._typing_dots % 2 == 0 else "/"
            return f"AI final validation {pulse}"
        return f"AI is thinking{dots}"

    def _typing_interval_ms(self) -> int:
        base = {
            "impact_assessment": 360,
            "generation": 120,
            "final_validation": 220,
        }.get(self._typing_stage, 260)
        scale = max(0.7, min(1.7, self._typing_expected_ms / 150.0))
        return int(base * scale)

    def _normalize_stage(self, stage: str) -> str:
        cleaned = stage.strip().lower()
        if cleaned in {"impact_assessment", "generation", "final_validation"}:
            return cleaned
        return "impact_assessment"
