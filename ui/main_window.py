from __future__ import annotations

import ctypes
import ctypes.wintypes
import html

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QThread, Qt, Signal, QVariantAnimation
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.hotkey_manager import GlobalHotkeyManager
from core.app_metadata import APP_BUILD_FOCUS, APP_MODE, APP_NAME, APP_VERSION
from core.router import CommandRouter
from persona.persona_engine import PersonaEngine
from ui.output_highlighter import OutputHighlighter
from ui.style_layers import build_main_window_stylesheet
from ui.theme_tokens import default_dark_tokens, default_light_tokens
from ui.win11_effects import apply_mica_or_acrylic


WM_HOTKEY = 0x0312
HOTKEY_ID = 1


class CommandWorker(QObject):
    finished = Signal(str, object)

    def __init__(self, router: CommandRouter, command: str) -> None:
        super().__init__()
        self.router = router
        self.command = command

    def run(self) -> None:
        result = self.router.execute(self.command)
        self.finished.emit(self.command, result)


class MainWindow(QMainWindow):
    def __init__(self, router: CommandRouter, persona_engine: PersonaEngine | None = None) -> None:
        super().__init__()
        self.router = router
        self.persona_engine = persona_engine or PersonaEngine(persona_name="calm")
        self.theme = default_dark_tokens()
        self._input_focus_color = self.theme.input_focus
        self._explicit_quit = False
        self.minimize_to_tray = False
        self._hotkey_registered = False
        self.fast_command_mode = True
        self.hotkey_manager = GlobalHotkeyManager()
        self.tray_icon: QSystemTrayIcon | None = None
        self._active_thread: QThread | None = None
        self._active_worker: CommandWorker | None = None
        self.message_count = 0
        self.command_count = 0

        self.setWindowTitle("OrionDesk")
        self.resize(800, 480)
        self._setup_ui()
        self._apply_windows11_style()
        self._setup_focus_animation()
        self._setup_output_animation()
        self._setup_system_tray()
        self._register_global_hotkey()
        apply_mica_or_acrylic(int(self.winId()))

    def _setup_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(
            self.theme.spacing_lg,
            self.theme.spacing_md,
            self.theme.spacing_lg,
            self.theme.spacing_lg,
        )
        main_layout.setSpacing(self.theme.spacing_sm + 2)

        title_bar = QHBoxLayout()
        title_bar.setSpacing(self.theme.spacing_sm)
        self.title_label = QLabel("OrionDesk", self)
        self.title_label.setObjectName("titleLabel")
        self.subtitle_label = QLabel("Windows 11 Personal OS Agent", self)
        self.subtitle_label.setObjectName("subtitleLabel")
        self.active_tab_label = QLabel("Tab: Command", self)
        self.active_tab_label.setObjectName("activeTabLabel")
        title_bar.addWidget(self.title_label)
        title_bar.addWidget(self.subtitle_label)
        title_bar.addStretch()
        title_bar.addWidget(self.active_tab_label)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setObjectName("mainTabs")
        self.tab_widget.setDocumentMode(True)

        command_tab = self._build_command_tab()
        memory_tab = self._build_memory_tab()
        settings_tab = self._build_settings_tab()
        diagnostics_tab = self._build_diagnostics_tab()
        about_tab = self._build_about_tab()

        self.tab_widget.addTab(command_tab, "Command")
        self.tab_widget.addTab(memory_tab, "Memory")
        self.tab_widget.addTab(settings_tab, "Settings")
        self.tab_widget.addTab(diagnostics_tab, "Diagnostics")
        self.tab_widget.addTab(about_tab, "About")
        self._apply_tab_icons()
        self.tab_widget.currentChanged.connect(self._handle_tab_changed)
        main_layout.addLayout(title_bar)
        main_layout.addWidget(self.tab_widget)

        self.execute_button.clicked.connect(self._handle_execute)
        self.command_input.returnPressed.connect(self._handle_execute)
        self.command_input.textChanged.connect(self._handle_command_text_changed)
        self.persona_selector.currentTextChanged.connect(self._handle_persona_change)
        self.theme_selector.currentTextChanged.connect(self._handle_theme_change)
        self.channel_selector.currentTextChanged.connect(self._handle_channel_change)
        self.minimize_tray_checkbox.toggled.connect(self._handle_minimize_tray_toggled)
        self.hotkey_selector.currentTextChanged.connect(self._handle_hotkey_change)
        self.fast_mode_checkbox.toggled.connect(self._handle_fast_mode_toggled)
        self._setup_shortcuts()

        self.setTabOrder(self.persona_selector, self.command_input)
        self.setTabOrder(self.command_input, self.execute_button)
        self.setTabOrder(self.execute_button, self.output_panel)

    def _build_command_tab(self) -> QWidget:
        page = QWidget(self)
        page_layout = QHBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(self.theme.spacing_sm + 2)

        page_layout.addWidget(self._build_command_sidebar(page))
        page_layout.addWidget(self._build_command_chat_area(page), 1)
        self._update_command_stats()
        return page

    def _build_command_sidebar(self, parent: QWidget) -> QWidget:
        sidebar = QFrame(parent)
        sidebar.setObjectName("commandSidebar")
        sidebar.setFixedWidth(240)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.theme.spacing_sm + 2)

        persona_card = QFrame(sidebar)
        persona_card.setObjectName("personaCard")
        persona_layout = QVBoxLayout(persona_card)
        persona_layout.setContentsMargins(
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
        )
        persona_layout.setSpacing(self.theme.spacing_sm)
        persona_title = QLabel("Persona", persona_card)
        persona_title.setObjectName("sectionTitle")
        self.persona_selector = QComboBox(persona_card)
        self.persona_selector.addItems(["calm", "professional", "hacker", "friendly", "minimal"])
        selected_persona = self.persona_engine.persona_name
        if selected_persona not in {"calm", "professional", "hacker", "friendly", "minimal"}:
            selected_persona = "calm"
        self.persona_selector.setCurrentText(selected_persona)
        persona_hint = QLabel("Choose AI personality style", persona_card)
        persona_hint.setObjectName("sectionHint")
        persona_hint.setWordWrap(True)
        persona_layout.addWidget(persona_title)
        persona_layout.addWidget(self.persona_selector)
        persona_layout.addWidget(persona_hint)

        quick_card = QFrame(sidebar)
        quick_card.setObjectName("quickActionsCard")
        quick_layout = QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
        )
        quick_layout.setSpacing(self.theme.spacing_sm)
        quick_title = QLabel("Quick Actions", quick_card)
        quick_title.setObjectName("sectionTitle")
        quick_layout.addWidget(quick_title)
        quick_actions = [
            ("Open VSCode", "open vscode"),
            ("Open Notepad", "open notepad"),
            ("Focus Mode", "mode focus on"),
            ("System Status", "system status"),
            ("Clear Chat", "clear chat"),
        ]
        self.quick_action_buttons = []
        for label, command in quick_actions:
            button = QPushButton(label, quick_card)
            button.setObjectName("quickActionButton")
            button.clicked.connect(lambda _checked=False, cmd=command: self._handle_quick_action(cmd))
            quick_layout.addWidget(button)
            self.quick_action_buttons.append(button)
        quick_layout.addStretch()

        stats_card = QFrame(sidebar)
        stats_card.setObjectName("commandStatsCard")
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
        )
        stats_layout.setSpacing(self.theme.spacing_md)

        message_tile = QVBoxLayout()
        self.message_count_label = QLabel("0", stats_card)
        self.message_count_label.setObjectName("statsValue")
        message_text = QLabel("Messages", stats_card)
        message_text.setObjectName("statsLabel")
        message_tile.addWidget(self.message_count_label, alignment=Qt.AlignmentFlag.AlignCenter)
        message_tile.addWidget(message_text, alignment=Qt.AlignmentFlag.AlignCenter)

        command_tile = QVBoxLayout()
        self.command_count_label = QLabel("0", stats_card)
        self.command_count_label.setObjectName("statsValue")
        command_text = QLabel("Commands", stats_card)
        command_text.setObjectName("statsLabel")
        command_tile.addWidget(self.command_count_label, alignment=Qt.AlignmentFlag.AlignCenter)
        command_tile.addWidget(command_text, alignment=Qt.AlignmentFlag.AlignCenter)

        stats_layout.addLayout(message_tile)
        stats_layout.addLayout(command_tile)

        layout.addWidget(persona_card)
        layout.addWidget(quick_card)
        layout.addWidget(stats_card)
        return sidebar

    def _build_command_chat_area(self, parent: QWidget) -> QWidget:
        area = QWidget(parent)
        layout = QVBoxLayout(area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.theme.spacing_sm + 2)

        self.output_panel = QTextEdit(area)
        self.output_panel.setReadOnly(True)
        self.output_panel.setObjectName("outputPanel")
        self.highlighter = OutputHighlighter(self.output_panel.document())
        self._append_welcome_message()

        input_card = QFrame(area)
        input_card.setObjectName("inputShellCard")
        input_layout = QHBoxLayout(input_card)
        input_layout.setContentsMargins(
            self.theme.spacing_sm,
            self.theme.spacing_sm,
            self.theme.spacing_sm,
            self.theme.spacing_sm,
        )
        input_layout.setSpacing(self.theme.spacing_sm)

        self.command_input = QLineEdit(area)
        self.command_input.setPlaceholderText("Ketik command Anda di sini...")
        self.clear_chat_button = QPushButton("Clear", area)
        self.clear_chat_button.setObjectName("clearChatButton")
        self.clear_chat_button.clicked.connect(self._handle_clear_chat)
        self.execute_button = QPushButton("Send", area)
        self.execute_button.setObjectName("sendButton")
        self.execute_button.setMinimumWidth(110)
        self.execute_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))

        input_layout.addWidget(self.command_input, 1)
        input_layout.addWidget(self.clear_chat_button)
        input_layout.addWidget(self.execute_button)

        suggestion_row = QHBoxLayout()
        suggestion_row.setSpacing(self.theme.spacing_sm)
        suggestion_title = QLabel("Suggestions:", area)
        suggestion_title.setObjectName("sectionHint")
        suggestion_row.addWidget(suggestion_title)
        for command in ["capability system info", "clip show", "mode game on"]:
            chip = QPushButton(command, area)
            chip.setObjectName("suggestionChip")
            chip.clicked.connect(lambda _checked=False, cmd=command: self._handle_suggestion_chip(cmd))
            suggestion_row.addWidget(chip)
        suggestion_row.addStretch()

        self.command_suggestions = QLabel(area)
        self.command_suggestions.setObjectName("commandSuggestions")
        self.command_suggestions.setWordWrap(True)
        self.command_hint_label = QLabel(area)
        self.command_hint_label.setObjectName("commandHint")
        self.command_hint_label.setWordWrap(True)
        self.intent_hint_label = QLabel(area)
        self.intent_hint_label.setObjectName("intentHint")
        self.intent_hint_label.setWordWrap(True)
        self.loading_label = QLabel("", area)
        self.loading_label.setObjectName("loadingHint")
        self.loading_label.setWordWrap(True)

        self.command_input.setAccessibleName("command-input")
        self.persona_selector.setAccessibleName("persona-selector")
        self.execute_button.setAccessibleName("execute-button")
        self.output_panel.setAccessibleName("output-panel")

        layout.addWidget(self.output_panel, 1)
        layout.addWidget(input_card)
        layout.addLayout(suggestion_row)
        layout.addWidget(self.command_suggestions)
        layout.addWidget(self.command_hint_label)
        layout.addWidget(self.intent_hint_label)
        layout.addWidget(self.loading_label)
        self._refresh_command_assist("")
        return area

    def _build_placeholder_tab(self, title: str, text: str) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
        )
        heading = QLabel(title, page)
        heading.setObjectName("placeholderTitle")
        body = QLabel(text, page)
        body.setWordWrap(True)
        body.setObjectName("placeholderText")
        layout.addWidget(heading)
        layout.addWidget(body)
        layout.addStretch()
        return page

    def _handle_tab_changed(self, index: int) -> None:
        name = self.tab_widget.tabText(index)
        self.active_tab_label.setText(f"Tab: {name}")
        if name == "About":
            self._refresh_about_panel()
        if name == "Memory":
            self._refresh_memory_panel()
        if name == "Diagnostics":
            self._refresh_diagnostics_panel()

    def _apply_tab_icons(self) -> None:
        icons = [
            QStyle.StandardPixmap.SP_ComputerIcon,
            QStyle.StandardPixmap.SP_DriveHDIcon,
            QStyle.StandardPixmap.SP_FileDialogContentsView,
            QStyle.StandardPixmap.SP_MessageBoxWarning,
            QStyle.StandardPixmap.SP_MessageBoxInformation,
        ]
        for index, pixmap in enumerate(icons):
            self.tab_widget.setTabIcon(index, self.style().standardIcon(pixmap))

    def _build_about_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
        )
        title = QLabel("About OrionDesk", page)
        title.setObjectName("placeholderTitle")
        self.about_info = QTextBrowser(page)
        self.about_info.setObjectName("aboutInfo")
        layout.addWidget(title)
        layout.addWidget(self.about_info)
        self._refresh_about_panel()
        return page

    def _build_memory_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
        )
        title = QLabel("Memory Snapshot", page)
        title.setObjectName("placeholderTitle")
        self.memory_info = QTextBrowser(page)
        self.memory_info.setObjectName("memoryInfo")
        refresh = QPushButton("Refresh Memory", page)
        refresh.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        refresh.clicked.connect(self._refresh_memory_panel)
        layout.addWidget(title)
        layout.addWidget(refresh)
        layout.addWidget(self.memory_info)
        self._refresh_memory_panel()
        return page

    def _build_diagnostics_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
        )
        title = QLabel("Diagnostics", page)
        title.setObjectName("placeholderTitle")
        button_row = QHBoxLayout()
        run_button = QPushButton("Generate Report", page)
        run_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        run_button.clicked.connect(self._generate_diagnostic_report)
        profile_button = QPushButton("Run Performance Baseline", page)
        profile_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        profile_button.clicked.connect(self._run_performance_baseline)
        snapshot_button = QPushButton("Save Recovery Snapshot", page)
        snapshot_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        snapshot_button.clicked.connect(self._save_recovery_snapshot)
        button_row.addWidget(run_button)
        button_row.addWidget(profile_button)
        button_row.addWidget(snapshot_button)
        button_row.addStretch()
        self.diagnostics_info = QTextBrowser(page)
        self.diagnostics_info.setObjectName("diagnosticsInfo")
        layout.addWidget(title)
        layout.addLayout(button_row)
        layout.addWidget(self.diagnostics_info)
        self._refresh_diagnostics_panel()
        return page

    def _build_settings_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
            self.theme.spacing_md,
        )
        layout.setSpacing(self.theme.spacing_sm)

        title = QLabel("Settings", page)
        title.setObjectName("placeholderTitle")

        theme_row = QHBoxLayout()
        theme_label = QLabel("Theme", page)
        self.theme_selector = QComboBox(page)
        self.theme_selector.addItems(["dark", "light"])
        self.theme_selector.setCurrentText("dark")
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_selector)
        theme_row.addStretch()

        channel_row = QHBoxLayout()
        channel_label = QLabel("Release Channel", page)
        self.channel_selector = QComboBox(page)
        self.channel_selector.addItems(["stable", "beta"])
        self.channel_selector.setCurrentText(self.router.get_release_channel())
        channel_row.addWidget(channel_label)
        channel_row.addWidget(self.channel_selector)
        channel_row.addStretch()

        self.minimize_tray_checkbox = QCheckBox("Minimize to tray when closing", page)
        self.minimize_tray_checkbox.setChecked(self.minimize_to_tray)

        hotkey_row = QHBoxLayout()
        hotkey_label = QLabel("Global Hotkey", page)
        self.hotkey_selector = QComboBox(page)
        self.hotkey_selector.addItems(["Win+Shift+O", "Ctrl+Shift+O", "Alt+Space"])
        self.hotkey_selector.setCurrentText(self.hotkey_manager.active_hotkey)
        hotkey_row.addWidget(hotkey_label)
        hotkey_row.addWidget(self.hotkey_selector)
        hotkey_row.addStretch()

        self.fast_mode_checkbox = QCheckBox("Fast command surface (focus input on toggle)", page)
        self.fast_mode_checkbox.setChecked(self.fast_command_mode)

        self.settings_status = QLabel("Settings siap digunakan.", page)
        self.settings_status.setObjectName("placeholderText")

        layout.addWidget(title)
        layout.addLayout(theme_row)
        layout.addLayout(channel_row)
        layout.addWidget(self.minimize_tray_checkbox)
        layout.addLayout(hotkey_row)
        layout.addWidget(self.fast_mode_checkbox)
        layout.addWidget(self.settings_status)
        layout.addStretch()
        return page

    def _refresh_about_panel(self) -> None:
        channel = self.router.get_release_channel()
        lines = [
            f"{APP_NAME} {APP_VERSION}",
            f"Release Channel: {channel}",
            f"Mode: {APP_MODE}",
            f"Build Focus: {APP_BUILD_FOCUS}",
        ]
        self.about_info.setText("\n".join(lines))

    def _refresh_memory_panel(self) -> None:
        summary = self.router.memory_summary()
        top_commands = summary.get("top_commands", [])
        lines = ["Top Commands:"]
        if not top_commands:
            lines.append("- (belum ada data)")
        else:
            for command, count in top_commands:
                lines.append(f"- {command}: {count}")
        self.memory_info.setText("\n".join(lines))

    def _refresh_diagnostics_panel(self) -> None:
        lines = [
            "Diagnostics panel siap.",
            "Klik 'Generate Report' untuk membuat diagnostic JSON.",
            "Klik 'Save Recovery Snapshot' untuk simpan session snapshot.",
        ]
        self.diagnostics_info.setText("\n".join(lines))

    def _generate_diagnostic_report(self) -> None:
        report = self.router.create_diagnostic_report()
        if report is None:
            self.diagnostics_info.append("\n[Error] Gagal membuat report.")
            return
        self.diagnostics_info.append(f"\n[Success] Report dibuat: {report}")

    def _save_recovery_snapshot(self) -> None:
        snapshot = self.router.save_recovery_snapshot()
        if snapshot is None:
            self.diagnostics_info.append("\n[Error] Gagal menyimpan snapshot.")
            return
        self.diagnostics_info.append(f"\n[Success] Snapshot disimpan: {snapshot}")

    def _run_performance_baseline(self) -> None:
        baseline = self.router.build_performance_baseline()
        release_summary = self.router.release_hardening_summary()
        lines = [
            "[Performance Baseline]",
            f"startup_ms: {baseline['startup_ms']}",
            f"command_latency_ms: {baseline['command_latency_ms']}",
            f"storage_io_ms: {baseline['storage_io_ms']}",
            (
                "release_checklist: "
                f"{release_summary['completed']}/{release_summary['total']} completed"
            ),
        ]
        self.diagnostics_info.append("\n" + "\n".join(lines))

    def _handle_theme_change(self, theme_name: str) -> None:
        if theme_name == "light":
            self.theme = default_light_tokens()
        else:
            self.theme = default_dark_tokens()
        self._input_focus_color = self.theme.input_focus
        self.setStyleSheet(self._build_stylesheet(self._input_focus_color))
        self.settings_status.setText(f"Theme active: {theme_name}")

    def _handle_channel_change(self, channel: str) -> None:
        applied = self.router.set_release_channel(channel)
        self.settings_status.setText(f"Release channel active: {applied}")
        self._refresh_about_panel()

    def _handle_minimize_tray_toggled(self, enabled: bool) -> None:
        self.minimize_to_tray = enabled
        self.settings_status.setText(f"Minimize to tray: {'on' if enabled else 'off'}")

    def _handle_hotkey_change(self, hotkey: str) -> None:
        conflict, reason = self.hotkey_manager.is_conflicted(
            hotkey,
            local_shortcuts={"Ctrl+Return", "Ctrl+L", "Ctrl+K"},
        )
        if conflict:
            self.settings_status.setText(reason)
            return

        self.hotkey_manager.set_hotkey(hotkey)
        self._register_global_hotkey()
        self.settings_status.setText(f"Global hotkey active: {self.hotkey_manager.active_hotkey}")

    def _handle_fast_mode_toggled(self, enabled: bool) -> None:
        self.fast_command_mode = enabled
        self.settings_status.setText(f"Fast command surface: {'on' if enabled else 'off'}")

    def _handle_command_text_changed(self, text: str) -> None:
        self._refresh_command_assist(text)

    def _refresh_command_assist(self, text: str) -> None:
        suggestions = self.router.suggest_commands(text)
        if suggestions:
            suggestion_text = " | ".join(suggestions)
            self.command_suggestions.setText(f"Suggestions: {suggestion_text}")
        else:
            self.command_suggestions.setText("Suggestions: -")

        usage_hint = self.router.usage_hint(text)
        argument_hint = self.router.argument_hint(text)
        if usage_hint is None:
            self.command_hint_label.setText("Usage: -")
        else:
            if argument_hint:
                self.command_hint_label.setText(f"Usage: {usage_hint} | Args: {argument_hint}")
            else:
                self.command_hint_label.setText(f"Usage: {usage_hint}")

        intent_explanation = self.router.explain_intent(text)
        if not intent_explanation:
            self.intent_hint_label.setText("Intent: -")
        else:
            self.intent_hint_label.setText(f"Intent: {intent_explanation}")

    def _append_welcome_message(self) -> None:
        self._append_assistant_bubble(
            "Halo! Saya OrionDesk AI Assistant. Saya siap membantu Anda mengelola sistem. Ketik command atau pilih quick action di samping.",
            "Contoh: open vscode, mode focus on",
        )

    def _append_user_bubble(self, message: str) -> None:
        self._append_chat_bubble(message, align_right=True, subtitle="Command")

    def _append_assistant_bubble(self, message: str, subtitle: str | None = None) -> None:
        self._append_chat_bubble(message, align_right=False, subtitle=subtitle)

    def _append_chat_bubble(
        self,
        message: str,
        align_right: bool,
        subtitle: str | None = None,
    ) -> None:
        alignment = "right" if align_right else "left"
        bubble_bg = self.theme.tab_active_bg if align_right else self.theme.card_bg
        border = self.theme.panel_border
        text_color = self.theme.text_primary
        subtitle_color = self.theme.text_secondary
        safe_message = html.escape(message)
        subtitle_html = ""
        if subtitle:
            safe_subtitle = html.escape(subtitle)
            subtitle_html = (
                f"<div style='margin-top:6px;font-size:11px;color:{subtitle_color};'>{safe_subtitle}</div>"
            )

        bubble_html = (
            f"<div style='margin:8px 0;text-align:{alignment};'>"
            f"<div style='display:inline-block;max-width:82%;"
            f"background-color:{bubble_bg};border:1px solid {border};"
            f"color:{text_color};border-radius:{self.theme.radius_md + 6}px;"
            f"padding:10px 12px;line-height:1.45;'>"
            f"<div style='font-size:13px;'>{safe_message}</div>"
            f"{subtitle_html}</div></div>"
        )
        self.output_panel.append(bubble_html)

    def _handle_quick_action(self, command: str) -> None:
        if command == "clear chat":
            self._handle_clear_chat()
            return
        self.command_input.setText(command)
        self._handle_execute()

    def _handle_suggestion_chip(self, command: str) -> None:
        self.command_input.setText(command)
        self.command_input.setFocus()

    def _handle_clear_chat(self) -> None:
        self.output_panel.clear()
        self.message_count = 0
        self.command_count = 0
        self._update_command_stats()
        self._append_welcome_message()
        self.command_input.clear()
        self._refresh_command_assist("")

    def _update_command_stats(self) -> None:
        self.message_count_label.setText(str(self.message_count))
        self.command_count_label.setText(str(self.command_count))

    def _handle_execute(self) -> None:
        command = self.command_input.text()
        if self._should_run_async(command):
            self._run_async_command(command)
            return

        result = self.router.execute(command)
        self._render_execution_result(command, result)

    def _should_run_async(self, command: str) -> bool:
        return command.strip().lower().startswith("search ")

    def _run_async_command(self, command: str) -> None:
        if self._active_thread is not None:
            self.loading_label.setText("Search sedang berjalan. Tunggu proses selesai.")
            return

        self.loading_label.setText("Loading search...")
        self.execute_button.setEnabled(False)
        self.command_input.setEnabled(False)

        worker = CommandWorker(self.router, command)
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._handle_async_result)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_async_state)
        self._active_thread = thread
        self._active_worker = worker
        thread.start()

    def _handle_async_result(self, command: str, result) -> None:
        self._render_execution_result(command, result)

    def _clear_async_state(self) -> None:
        self._active_thread = None
        self._active_worker = None
        self.execute_button.setEnabled(True)
        self.command_input.setEnabled(True)
        self.loading_label.setText("")

    def _render_execution_result(self, command: str, result) -> None:

        if command.strip():
            self._append_user_bubble(command)
            self.message_count += 1
            self.command_count += 1

        if result.requires_confirmation:
            warning = self.persona_engine.format_warning(
                result.message,
                detail=f"Command: {result.pending_command}",
            )
            self._append_assistant_bubble(self._with_status_badge(warning), "Safe mode confirmation")
            self.message_count += 1
            approved = self._show_confirmation(result.pending_command or command)
            response = self.router.confirm_pending(approved)
            styled_response = self.persona_engine.format_output(response.message)
            self._append_assistant_bubble(self._with_status_badge(styled_response))
            self.message_count += 1
        else:
            styled_response = self.persona_engine.format_output(result.message)
            self._append_assistant_bubble(self._with_status_badge(styled_response))
            self.message_count += 1

        self._update_command_stats()
        self.command_input.clear()
        self._refresh_command_assist("")

    def _handle_persona_change(self, persona_name: str) -> None:
        self._animate_output_fade()
        self.persona_engine.set_persona(persona_name)
        persona_message = self.persona_engine.format_output(f"Persona aktif: {persona_name}")
        self._append_assistant_bubble(persona_message)
        self.message_count += 1
        self._update_command_stats()

    def _apply_windows11_style(self) -> None:
        self.setFont(QFont("Segoe UI Variable Text", 10))
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(self._build_stylesheet(self._input_focus_color))

    def _build_stylesheet(self, focus_color: str) -> str:
        return build_main_window_stylesheet(self.theme, focus_color)

    def _setup_focus_animation(self) -> None:
        self.command_input.setObjectName("commandInput")
        self.command_input.installEventFilter(self)
        self.focus_animation = QVariantAnimation(self)
        self.focus_animation.setDuration(180)
        self.focus_animation.valueChanged.connect(self._on_focus_color_changed)

    def _setup_shortcuts(self) -> None:
        self.shortcut_execute = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut_execute.activated.connect(self._handle_execute)

        self.shortcut_clear = QShortcut(QKeySequence("Ctrl+L"), self)
        self.shortcut_clear.activated.connect(self._handle_clear_chat)

        self.shortcut_fast_surface = QShortcut(QKeySequence("Ctrl+K"), self)
        self.shortcut_fast_surface.activated.connect(self._activate_fast_command_surface)

    def _with_status_badge(self, message: str) -> str:
        lowered = message.lower()
        if "warning" in lowered or "konfirmasi manual" in lowered:
            return f"[WARNING] {message}"
        if "ditolak" in lowered or "blocked" in lowered or "error" in lowered:
            return f"[BLOCKED] {message}"
        if "format salah" in lowered or "invalid" in lowered:
            return f"[INVALID] {message}"
        return f"[SUCCESS] {message}"

    def _setup_output_animation(self) -> None:
        self.output_effect = QGraphicsOpacityEffect(self.output_panel)
        self.output_panel.setGraphicsEffect(self.output_effect)
        self.output_effect.setOpacity(1.0)
        self.output_animation = QVariantAnimation(self)
        self.output_animation.setDuration(220)
        self.output_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.output_animation.valueChanged.connect(self._on_output_opacity_changed)

    def _setup_system_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon = QSystemTrayIcon(icon, self)
        tray_menu = QMenu(self)

        show_action = QAction("Show OrionDesk", self)
        show_action.triggered.connect(self._show_from_tray)
        quit_action = QAction("Quit OrionDesk", self)
        quit_action.triggered.connect(self._quit_app)

        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _register_global_hotkey(self) -> None:
        if not hasattr(ctypes, "windll"):
            return

        user32 = ctypes.windll.user32
        if self._hotkey_registered:
            user32.UnregisterHotKey(None, HOTKEY_ID)

        binding = self.hotkey_manager.to_windows_binding(self.hotkey_manager.active_hotkey)
        if binding is None:
            self._hotkey_registered = False
            return

        modifiers, key_code = binding
        registered = user32.RegisterHotKey(None, HOTKEY_ID, modifiers, key_code)
        self._hotkey_registered = bool(registered)

    def _toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
            return
        self.showNormal()
        self.activateWindow()
        self.raise_()
        if self.fast_command_mode:
            self._activate_fast_command_surface()

    def _activate_fast_command_surface(self) -> None:
        self.tab_widget.setCurrentIndex(0)
        if not self.isVisible():
            self.showNormal()
            self.activateWindow()
            self.raise_()
        self.command_input.setFocus()
        self.command_input.selectAll()

    def _show_from_tray(self) -> None:
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _quit_app(self) -> None:
        self._explicit_quit = True
        self.close()

    def _cleanup_runtime_hooks(self) -> None:
        if self._hotkey_registered and hasattr(ctypes, "windll"):
            ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID)
            self._hotkey_registered = False
        if self.tray_icon is not None:
            self.tray_icon.hide()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_visibility()

    def _animate_output_fade(self) -> None:
        self.output_animation.stop()
        self.output_animation.setStartValue(0.6)
        self.output_animation.setEndValue(1.0)
        self.output_animation.start()

    def _on_output_opacity_changed(self, value: float) -> None:
        self.output_effect.setOpacity(float(value))

    def _on_focus_color_changed(self, value) -> None:
        color = value.name() if isinstance(value, QColor) else self.theme.input_focus
        self._input_focus_color = color
        self.setStyleSheet(self._build_stylesheet(color))

    def eventFilter(self, watched, event):
        if watched is self.command_input and event.type() == QEvent.Type.FocusIn:
            self.focus_animation.stop()
            self.focus_animation.setStartValue(QColor(self.theme.input_border))
            self.focus_animation.setEndValue(QColor(self.theme.input_focus_active))
            self.focus_animation.start()
        if watched is self.command_input and event.type() == QEvent.Type.FocusOut:
            self.focus_animation.stop()
            self.focus_animation.setStartValue(QColor(self.theme.input_focus_active))
            self.focus_animation.setEndValue(QColor(self.theme.input_border))
            self.focus_animation.start()
        return super().eventFilter(watched, event)

    def nativeEvent(self, event_type, message):
        if event_type == "windows_generic_MSG" and self._hotkey_registered:
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                self._toggle_visibility()
                return True, 0
        return super().nativeEvent(event_type, message)

    def closeEvent(self, event) -> None:
        if self.minimize_to_tray and not self._explicit_quit and self.tray_icon is not None:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "OrionDesk",
                "Aplikasi tetap berjalan di System Tray.",
                QSystemTrayIcon.MessageIcon.Information,
                1500,
            )
            return

        self._cleanup_runtime_hooks()
        return super().closeEvent(event)

    def _show_confirmation(self, command: str) -> bool:
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Konfirmasi Safe Mode")
        dialog.setText(f"Command berisiko terdeteksi:\n{command}\n\nLanjutkan aksi ini?")
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        dialog.setStyleSheet(
            f"""
            QMessageBox {{ background-color: {self.theme.window_bg}; color: {self.theme.text_primary}; }}
            QLabel {{ color: {self.theme.text_primary}; }}
            QPushButton {{
                background-color: {self.theme.button_bg};
                color: {self.theme.button_text};
                border-radius: {self.theme.radius_md}px;
                padding: {self.theme.spacing_sm}px {self.theme.spacing_md}px;
            }}
            QPushButton:hover {{ background-color: {self.theme.button_hover}; }}
            QPushButton:pressed {{ background-color: {self.theme.button_pressed}; }}
            """
        )
        reply = dialog.exec()
        return reply == int(QMessageBox.StandardButton.Yes)