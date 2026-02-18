from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.theme_tokens import ThemeTokens


class SettingsPage(QWidget):
    def __init__(
        self,
        theme: ThemeTokens,
        release_channel: str,
        active_hotkey: str,
        minimize_to_tray: bool,
        fast_mode: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.spacing_md,
            theme.spacing_md,
            theme.spacing_md,
            theme.spacing_md,
        )
        layout.setSpacing(theme.spacing_sm)

        title = QLabel("Settings", self)
        title.setObjectName("placeholderTitle")

        theme_row = QHBoxLayout()
        theme_label = QLabel("Theme", self)
        self.theme_selector = QComboBox(self)
        self.theme_selector.addItems(["dark", "light"])
        self.theme_selector.setCurrentText("dark")
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_selector)
        theme_row.addStretch()

        channel_row = QHBoxLayout()
        channel_label = QLabel("Release Channel", self)
        self.channel_selector = QComboBox(self)
        self.channel_selector.addItems(["stable", "beta"])
        self.channel_selector.setCurrentText(release_channel)
        channel_row.addWidget(channel_label)
        channel_row.addWidget(self.channel_selector)
        channel_row.addStretch()

        self.minimize_tray_checkbox = QCheckBox("Minimize to tray when closing", self)
        self.minimize_tray_checkbox.setChecked(minimize_to_tray)

        hotkey_row = QHBoxLayout()
        hotkey_label = QLabel("Global Hotkey", self)
        self.hotkey_selector = QComboBox(self)
        self.hotkey_selector.addItems(["Win+Shift+O", "Ctrl+Shift+O", "Alt+Space"])
        self.hotkey_selector.setCurrentText(active_hotkey)
        hotkey_row.addWidget(hotkey_label)
        hotkey_row.addWidget(self.hotkey_selector)
        hotkey_row.addStretch()

        self.fast_mode_checkbox = QCheckBox("Fast command surface (focus input on toggle)", self)
        self.fast_mode_checkbox.setChecked(fast_mode)

        self.settings_status = QLabel("Settings siap digunakan.", self)
        self.settings_status.setObjectName("placeholderText")

        layout.addWidget(title)
        layout.addLayout(theme_row)
        layout.addLayout(channel_row)
        layout.addWidget(self.minimize_tray_checkbox)
        layout.addLayout(hotkey_row)
        layout.addWidget(self.fast_mode_checkbox)
        layout.addWidget(self.settings_status)
        layout.addStretch()
