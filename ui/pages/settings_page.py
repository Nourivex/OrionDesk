from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.theme_tokens import ThemeTokens


class SettingsPage(QWidget):
    def __init__(
        self,
        theme: ThemeTokens,
        release_channel: str,
        active_hotkey: str,
        minimize_to_tray: bool,
        fast_mode: bool,
        safe_mode: bool,
        execution_profile: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        layout.setSpacing(theme.spacing_sm)

        title = QLabel("Settings Control Center", self)
        title.setObjectName("placeholderTitle")

        appearance_card = QFrame(self)
        appearance_card.setObjectName("topCard")
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        appearance_layout.setSpacing(theme.spacing_sm)
        appearance_title = QLabel("Appearance", appearance_card)
        appearance_title.setObjectName("sectionTitle")

        theme_row = QHBoxLayout()
        theme_label = QLabel("Theme", appearance_card)
        self.theme_selector = QComboBox(appearance_card)
        self.theme_selector.addItems(["dark", "light"])
        self.theme_selector.setCurrentText("dark")
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_selector)

        channel_row = QHBoxLayout()
        channel_label = QLabel("Release Channel", appearance_card)
        self.channel_selector = QComboBox(appearance_card)
        self.channel_selector.addItems(["stable", "beta"])
        self.channel_selector.setCurrentText(release_channel)
        channel_row.addWidget(channel_label)
        channel_row.addWidget(self.channel_selector)

        appearance_layout.addWidget(appearance_title)
        appearance_layout.addLayout(theme_row)
        appearance_layout.addLayout(channel_row)

        runtime_card = QFrame(self)
        runtime_card.setObjectName("topCard")
        runtime_layout = QVBoxLayout(runtime_card)
        runtime_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        runtime_layout.setSpacing(theme.spacing_sm)
        runtime_title = QLabel("Runtime Controls", runtime_card)
        runtime_title.setObjectName("sectionTitle")

        hotkey_row = QHBoxLayout()
        hotkey_label = QLabel("Global Hotkey", runtime_card)
        self.hotkey_selector = QComboBox(runtime_card)
        self.hotkey_selector.addItems(["Win+Shift+O", "Ctrl+Shift+O", "Alt+Space"])
        self.hotkey_selector.setCurrentText(active_hotkey)
        hotkey_row.addWidget(hotkey_label)
        hotkey_row.addWidget(self.hotkey_selector)

        self.fast_mode_checkbox = QCheckBox("Fast command surface (focus input on toggle)", runtime_card)
        self.fast_mode_checkbox.setChecked(fast_mode)
        self.minimize_tray_checkbox = QCheckBox("Minimize to tray when closing", runtime_card)
        self.minimize_tray_checkbox.setChecked(minimize_to_tray)

        runtime_layout.addWidget(runtime_title)
        runtime_layout.addLayout(hotkey_row)
        runtime_layout.addWidget(self.fast_mode_checkbox)
        runtime_layout.addWidget(self.minimize_tray_checkbox)

        safety_card = QFrame(self)
        safety_card.setObjectName("topCard")
        safety_layout = QVBoxLayout(safety_card)
        safety_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        safety_layout.setSpacing(theme.spacing_sm)
        safety_title = QLabel("Safety Policy", safety_card)
        safety_title.setObjectName("sectionTitle")

        profile_row = QHBoxLayout()
        profile_label = QLabel("Execution Profile", safety_card)
        self.profile_selector = QComboBox(safety_card)
        self.profile_selector.addItems(["strict", "balanced", "power", "explain-only"])
        self.profile_selector.setCurrentText(execution_profile)
        profile_row.addWidget(profile_label)
        profile_row.addWidget(self.profile_selector)

        self.safe_mode_checkbox = QCheckBox("Safe mode enabled", safety_card)
        self.safe_mode_checkbox.setChecked(safe_mode)

        safety_layout.addWidget(safety_title)
        safety_layout.addLayout(profile_row)
        safety_layout.addWidget(self.safe_mode_checkbox)

        self.settings_status = QLabel("Settings siap digunakan.", self)
        self.settings_status.setObjectName("placeholderText")

        layout.addWidget(title)
        layout.addWidget(appearance_card)
        layout.addWidget(runtime_card)
        layout.addWidget(safety_card)
        layout.addWidget(self.settings_status)
        layout.addStretch()
