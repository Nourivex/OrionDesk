from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

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
        generation_model: str,
        generation_timeout: float,
        generation_token_budget: int,
        generation_temperature: float,
        response_quality: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        layout.setSpacing(theme.spacing_sm)

        container = QWidget(self)
        container.setMaximumWidth(920)
        body = QVBoxLayout(container)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(theme.spacing_sm)

        title = QLabel("Settings Control Center", self)
        title.setObjectName("placeholderTitle")

        appearance_card = QFrame(container)
        appearance_card.setObjectName("topCard")
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        appearance_layout.setSpacing(theme.spacing_sm)
        appearance_title = QLabel("Appearance", appearance_card)
        appearance_title.setObjectName("sectionTitle")

        theme_row = QHBoxLayout()
        theme_label = QLabel("Theme", appearance_card)
        theme_label.setMinimumWidth(140)
        self.theme_selector = QComboBox(appearance_card)
        self.theme_selector.addItems(["dark", "light"])
        self.theme_selector.setCurrentText("dark")
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_selector)

        channel_row = QHBoxLayout()
        channel_label = QLabel("Release Channel", appearance_card)
        channel_label.setMinimumWidth(140)
        self.channel_selector = QComboBox(appearance_card)
        self.channel_selector.addItems(["stable", "beta"])
        self.channel_selector.setCurrentText(release_channel)
        channel_row.addWidget(channel_label)
        channel_row.addWidget(self.channel_selector)

        appearance_layout.addWidget(appearance_title)
        appearance_layout.addLayout(theme_row)
        appearance_layout.addLayout(channel_row)

        runtime_card = QFrame(container)
        runtime_card.setObjectName("topCard")
        runtime_layout = QVBoxLayout(runtime_card)
        runtime_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        runtime_layout.setSpacing(theme.spacing_sm)
        runtime_title = QLabel("Runtime Controls", runtime_card)
        runtime_title.setObjectName("sectionTitle")

        hotkey_row = QHBoxLayout()
        hotkey_label = QLabel("Global Hotkey", runtime_card)
        hotkey_label.setMinimumWidth(140)
        self.hotkey_selector = QComboBox(runtime_card)
        self.hotkey_selector.addItems(["Win+Shift+O", "Ctrl+Shift+O", "Alt+Space"])
        self.hotkey_selector.setCurrentText(active_hotkey)
        hotkey_row.addWidget(hotkey_label)
        hotkey_row.addWidget(self.hotkey_selector)

        self.fast_mode_checkbox = QCheckBox("Fast command surface (focus input on toggle)", runtime_card)
        self.fast_mode_checkbox.setChecked(fast_mode)
        self.minimize_tray_checkbox = QCheckBox("Minimize to tray when closing", runtime_card)
        self.minimize_tray_checkbox.setChecked(minimize_to_tray)

        model_row = QHBoxLayout()
        model_label = QLabel("Chat Model", runtime_card)
        model_label.setMinimumWidth(140)
        self.model_selector = QComboBox(runtime_card)
        self.model_selector.addItems(["gemma3:4b", "llama3.2:3b", "mistral:7b"])
        self.model_selector.setCurrentText(generation_model)
        self.model_selector.setMaximumWidth(420)
        self.refresh_models_button = QPushButton("Refresh", runtime_card)
        self.refresh_models_button.setObjectName("modelRefreshButton")
        refresh_icon = Path(__file__).resolve().parents[1] / "assets" / "refresh_modern.svg"
        self.refresh_models_button.setIcon(QIcon(str(refresh_icon)))
        self.refresh_models_button.setText("")
        self.refresh_models_button.setToolTip("Reload model list from Ollama")
        self.refresh_models_button.setFixedSize(30, 30)
        model_row.addWidget(model_label)
        model_row.addWidget(self.model_selector)
        model_row.addWidget(self.refresh_models_button)
        model_row.addStretch()

        quality_row = QHBoxLayout()
        quality_label = QLabel("Response Quality", runtime_card)
        quality_label.setMinimumWidth(140)
        self.quality_selector = QComboBox(runtime_card)
        self.quality_selector.addItems(["concise", "balanced", "deep"])
        self.quality_selector.setCurrentText(response_quality)
        quality_row.addWidget(quality_label)
        quality_row.addWidget(self.quality_selector)

        token_row = QHBoxLayout()
        token_label = QLabel("Token Budget", runtime_card)
        token_label.setMinimumWidth(140)
        self.token_budget_selector = QComboBox(runtime_card)
        self.token_budget_selector.addItems(["128", "256", "384", "512"])
        self.token_budget_selector.setCurrentText(str(generation_token_budget))
        token_row.addWidget(token_label)
        token_row.addWidget(self.token_budget_selector)

        timeout_row = QHBoxLayout()
        timeout_label = QLabel("Generation Timeout", runtime_card)
        timeout_label.setMinimumWidth(140)
        self.timeout_selector = QComboBox(runtime_card)
        self.timeout_selector.addItems(["4.0", "8.0", "12.0"])
        self.timeout_selector.setCurrentText(f"{generation_timeout:.1f}")
        timeout_row.addWidget(timeout_label)
        timeout_row.addWidget(self.timeout_selector)

        temperature_row = QHBoxLayout()
        temperature_label = QLabel("Temperature", runtime_card)
        temperature_label.setMinimumWidth(140)
        self.temperature_selector = QComboBox(runtime_card)
        self.temperature_selector.addItems(["0.1", "0.2", "0.3", "0.4"])
        self.temperature_selector.setCurrentText(f"{generation_temperature:.1f}")
        temperature_row.addWidget(temperature_label)
        temperature_row.addWidget(self.temperature_selector)

        runtime_layout.addWidget(runtime_title)
        runtime_layout.addLayout(hotkey_row)
        runtime_layout.addLayout(model_row)
        runtime_layout.addLayout(quality_row)
        runtime_layout.addLayout(token_row)
        runtime_layout.addLayout(timeout_row)
        runtime_layout.addLayout(temperature_row)
        runtime_layout.addWidget(self.fast_mode_checkbox)
        runtime_layout.addWidget(self.minimize_tray_checkbox)

        safety_card = QFrame(container)
        safety_card.setObjectName("topCard")
        safety_layout = QVBoxLayout(safety_card)
        safety_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        safety_layout.setSpacing(theme.spacing_sm)
        safety_title = QLabel("Safety Policy", safety_card)
        safety_title.setObjectName("sectionTitle")

        profile_row = QHBoxLayout()
        profile_label = QLabel("Execution Profile", safety_card)
        profile_label.setMinimumWidth(140)
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

        self.settings_status = QLabel("Settings siap digunakan.", container)
        self.settings_status.setObjectName("placeholderText")

        body.addWidget(title)
        body.addWidget(appearance_card)
        body.addWidget(runtime_card)
        body.addWidget(safety_card)
        body.addWidget(self.settings_status)
        layout.addWidget(container, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()

    def set_model_options(self, models: list[dict], selected: str) -> None:
        self.model_selector.blockSignals(True)
        self.model_selector.clear()
        selected_index = -1
        for index, item in enumerate(models):
            if item.get("role") != "chat":
                continue
            name = str(item.get("name", "")).strip()
            badge = str(item.get("gpu_badge", "Unknown"))
            parameter_size = str(item.get("parameter_size", "-"))
            display = f"{name}   [{badge} • {parameter_size}]"
            self.model_selector.addItem(display, name)
            if name == selected:
                selected_index = self.model_selector.count() - 1
        if self.model_selector.count() > 0:
            self.model_selector.setCurrentIndex(selected_index if selected_index >= 0 else 0)
        self.model_selector.blockSignals(False)

    def selected_model_name(self) -> str:
        value = self.model_selector.currentData()
        if isinstance(value, str) and value.strip():
            return value
        text = self.model_selector.currentText().split("[", maxsplit=1)[0].strip()
        return text
