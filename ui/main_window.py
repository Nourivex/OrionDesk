from __future__ import annotations
import ctypes
import ctypes.wintypes
from pathlib import Path
from PySide6.QtCore import QEasingCurve, QEvent, QThread, Qt, QVariantAnimation
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QShortcut
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QMenu, QStyle, QSystemTrayIcon, QTabWidget, QVBoxLayout, QWidget
from core.app_metadata import APP_BUILD_FOCUS, APP_MODE, APP_NAME, APP_VERSION
from core.hotkey_manager import GlobalHotkeyManager
from core.router import CommandRouter
from persona.persona_engine import PersonaEngine
from ui.pages import AboutPage, CommandPage, DiagnosticsPage, MemoryPage, SettingsPage
from ui.style_layers import build_main_window_stylesheet
from ui.theme_tokens import default_dark_tokens, default_light_tokens
from ui.window_helpers import CommandWorker, memory_insight_payload, show_confirmation_dialog, with_status_badge
from ui.win11_effects import apply_mica_or_acrylic
WM_HOTKEY, HOTKEY_ID = 0x0312, 1
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
        self.message_count, self.command_count = 0, 0
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
        main_layout.setContentsMargins(self.theme.spacing_lg, self.theme.spacing_md, self.theme.spacing_lg, self.theme.spacing_lg)
        main_layout.setSpacing(self.theme.spacing_sm + 2)
        title_bar = QHBoxLayout()
        title_bar.setSpacing(self.theme.spacing_sm)
        logo_path = Path(__file__).resolve().parent / "assets" / "oriondesk_logo.svg"
        self.logo_widget = QSvgWidget(str(logo_path), self)
        self.logo_widget.setFixedSize(156, 36)
        self.subtitle_label = QLabel("Windows 11 Personal OS Agent", self)
        self.subtitle_label.setObjectName("subtitleLabel")
        self.system_status_label = QLabel("System Online", self)
        self.system_status_label.setObjectName("systemStatusPill")
        self.active_tab_label = QLabel("Tab: Command", self)
        self.active_tab_label.setObjectName("activeTabLabel")
        title_bar.addWidget(self.logo_widget)
        title_bar.addWidget(self.subtitle_label)
        title_bar.addStretch()
        title_bar.addWidget(self.system_status_label)
        title_bar.addWidget(self.active_tab_label)
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setObjectName("mainTabs")
        self.tab_widget.setDocumentMode(True)
        self.command_page = CommandPage(self.theme, self.persona_engine.persona_name, self)
        self.memory_page = MemoryPage(self.theme, self)
        generation_config = self.router.generation_config()
        self.settings_page = SettingsPage(theme=self.theme, release_channel=self.router.get_release_channel(), active_hotkey=self.hotkey_manager.active_hotkey, minimize_to_tray=self.minimize_to_tray, fast_mode=self.fast_command_mode, safe_mode=self.router.safe_mode, execution_profile=self.router.execution_profile_policy.profile, generation_model=generation_config["model"], generation_timeout=float(generation_config["timeout_seconds"]), generation_token_budget=int(generation_config["token_budget"]), generation_temperature=float(generation_config["temperature"]), response_quality=self.router.response_quality, parent=self)
        self.diagnostics_page = DiagnosticsPage(self.theme, self)
        self.about_page = AboutPage(self.theme, self)
        self.tab_widget.addTab(self.command_page, "Command")
        self.tab_widget.addTab(self.memory_page, "Memory")
        self.tab_widget.addTab(self.settings_page, "Settings")
        self.tab_widget.addTab(self.diagnostics_page, "Diagnostics")
        self.tab_widget.addTab(self.about_page, "About")
        self._apply_tab_icons()
        self.tab_widget.currentChanged.connect(self._handle_tab_changed)
        main_layout.addLayout(title_bar)
        main_layout.addWidget(self.tab_widget)
        self._expose_page_widgets()
        self._wire_signals()
        self._refresh_model_catalog(force_reload=False)
        self._refresh_about_panel()
        self._refresh_memory_panel()
        self._refresh_diagnostics_panel()
        self._append_welcome_message()
        self._refresh_command_assist("")
        self._update_command_stats()
        self.setTabOrder(self.persona_selector, self.command_input)
        self.setTabOrder(self.command_input, self.execute_button)
        self.setTabOrder(self.execute_button, self.output_panel)
    def _expose_page_widgets(self) -> None:
        self.persona_selector, self.command_input = self.command_page.persona_selector, self.command_page.command_input
        self.execute_button, self.clear_chat_button = self.command_page.execute_button, self.command_page.clear_chat_button
        self.output_panel, self.command_suggestions = self.command_page.output_panel, self.command_page.command_suggestions
        self.command_hint_label, self.intent_hint_label = self.command_page.command_hint_label, self.command_page.intent_hint_label
        self.loading_label, self.message_count_label = self.command_page.loading_label, self.command_page.message_count_label
        self.command_count_label, self.quick_action_buttons = self.command_page.command_count_label, self.command_page.quick_action_buttons
        self.memory_info, self.about_info = self.memory_page.memory_info, self.about_page.about_info
        self.diagnostics_info, self.theme_selector = self.diagnostics_page.diagnostics_info, self.settings_page.theme_selector
        self.channel_selector, self.minimize_tray_checkbox = self.settings_page.channel_selector, self.settings_page.minimize_tray_checkbox
        self.hotkey_selector, self.fast_mode_checkbox = self.settings_page.hotkey_selector, self.settings_page.fast_mode_checkbox
        self.profile_selector, self.safe_mode_checkbox = self.settings_page.profile_selector, self.settings_page.safe_mode_checkbox
        self.model_selector, self.quality_selector = self.settings_page.model_selector, self.settings_page.quality_selector
        self.token_budget_selector, self.timeout_selector = self.settings_page.token_budget_selector, self.settings_page.timeout_selector
        self.temperature_selector = self.settings_page.temperature_selector
        self.refresh_models_button = self.settings_page.refresh_models_button
        self.settings_status = self.settings_page.settings_status
    def _wire_signals(self) -> None:
        self.execute_button.clicked.connect(self._handle_execute)
        self.command_input.returnPressed.connect(self._handle_execute)
        self.command_input.textChanged.connect(self._refresh_command_assist)
        self.persona_selector.currentTextChanged.connect(self._handle_persona_change)
        self.theme_selector.currentTextChanged.connect(self._handle_theme_change)
        self.channel_selector.currentTextChanged.connect(self._handle_channel_change)
        self.minimize_tray_checkbox.toggled.connect(self._handle_minimize_tray_toggled)
        self.hotkey_selector.currentTextChanged.connect(self._handle_hotkey_change)
        self.fast_mode_checkbox.toggled.connect(self._handle_fast_mode_toggled)
        self.model_selector.currentTextChanged.connect(lambda _value: self._apply_generation_runtime_settings())
        self.token_budget_selector.currentTextChanged.connect(lambda _value: self._apply_generation_runtime_settings())
        self.timeout_selector.currentTextChanged.connect(lambda _value: self._apply_generation_runtime_settings())
        self.temperature_selector.currentTextChanged.connect(lambda _value: self._apply_generation_runtime_settings())
        self.quality_selector.currentTextChanged.connect(self._handle_quality_change)
        self.refresh_models_button.clicked.connect(lambda: self._refresh_model_catalog(force_reload=True))
        self.profile_selector.currentTextChanged.connect(lambda profile: self.settings_status.setText(f"Execution profile active: {self.router.execution_profile_policy.set_profile(profile)}"))
        self.safe_mode_checkbox.toggled.connect(lambda enabled: (setattr(self.router, "safe_mode", enabled), self.settings_status.setText(f"Safe mode: {'on' if enabled else 'off'}")))
        self.command_page.quickActionRequested.connect(self._handle_quick_action)
        self.command_page.suggestionRequested.connect(self._handle_suggestion_chip)
        self.command_page.clearChatRequested.connect(self._handle_clear_chat)
        self.memory_page.refreshRequested.connect(self._refresh_memory_panel)
        self.diagnostics_page.generateReportRequested.connect(self._generate_diagnostic_report)
        self.diagnostics_page.performanceBaselineRequested.connect(self._run_performance_baseline)
        self.diagnostics_page.saveSnapshotRequested.connect(self._save_recovery_snapshot)
        self._setup_shortcuts()
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
        payload = memory_insight_payload(self.router)
        self.memory_page.total_commands_value.setText(str(payload["total_commands"]))
        self.memory_page.top_command_value.setText(payload["top_command_label"])
        self.memory_page.last_refresh_value.setText(payload["refreshed_at"])
        self.memory_page.safe_mode_triggers_value.setText(f"Safe Mode Trigger: {payload['pending_count']}")
        self.memory_page.blocked_count_value.setText(f"Blocked Events: {payload['blocked_count']}")
        self.memory_page.warning_count_value.setText(f"Warning Events: {payload['warning_count']}")
        self.memory_page.session_start_value.setText(f"Session Start: {payload['session_start_label']}")
        self.memory_page.session_duration_value.setText(f"Session Duration: {payload['duration']}")
        self.memory_page.recent_activity_list.clear()
        self.memory_page.recent_activity_list.addItems(payload["recent_rows"])
        self.memory_info.setText(payload["top_command_lines"])
    def _refresh_diagnostics_panel(self) -> None:
        release_summary = self.router.release_hardening_summary()
        embed_health = self.router.embedding_health()
        self.diagnostics_page.health_state_label.setText("Online" if embed_health["ok"] else "Degraded")
        self.diagnostics_page.release_checklist_label.setText(f"{release_summary['completed']}/{release_summary['total']}")
        self.diagnostics_page.profile_state_label.setText(self.router.execution_profile_policy.profile)
        lines = [
            "Diagnostics panel siap.",
            f"Embedding: {embed_health['message']}",
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
        self.theme = default_light_tokens() if theme_name == "light" else default_dark_tokens()
        self._input_focus_color = self.theme.input_focus
        self.setStyleSheet(self._build_stylesheet(self._input_focus_color))
        self.output_panel.set_theme(self.theme)
        self.settings_status.setText(f"Theme active: {theme_name}")
    def _handle_channel_change(self, channel: str) -> None:
        applied = self.router.set_release_channel(channel)
        self.settings_status.setText(f"Release channel active: {applied}")
        self._refresh_about_panel()
    def _handle_minimize_tray_toggled(self, enabled: bool) -> None:
        self.minimize_to_tray = enabled
        self.settings_status.setText(f"Minimize to tray: {'on' if enabled else 'off'}")
    def _handle_hotkey_change(self, hotkey: str) -> None:
        conflict, reason = self.hotkey_manager.is_conflicted(hotkey, local_shortcuts={"Ctrl+Return", "Ctrl+L", "Ctrl+K"})
        if conflict: self.settings_status.setText(reason); return
        self.hotkey_manager.set_hotkey(hotkey)
        self._register_global_hotkey()
        self.settings_status.setText(f"Global hotkey active: {self.hotkey_manager.active_hotkey}")
    def _handle_fast_mode_toggled(self, enabled: bool) -> None:
        self.fast_command_mode = enabled
        self.settings_status.setText(f"Fast command surface: {'on' if enabled else 'off'}")
    def _apply_generation_runtime_settings(self) -> None:
        config = self.router.set_generation_runtime(model=self.settings_page.selected_model_name(), timeout_seconds=float(self.timeout_selector.currentText()), token_budget=int(self.token_budget_selector.currentText()), temperature=float(self.temperature_selector.currentText()))
        self.settings_status.setText(f"Chat runtime updated: {config['model']} | token={config['token_budget']} | timeout={config['timeout_seconds']}")
    def _refresh_model_catalog(self, force_reload: bool) -> None:
        models = self.router.available_generation_models(force_reload=force_reload)
        selected = self.settings_page.selected_model_name()
        if models: self.settings_page.set_model_options(models, selected)
    def _handle_quality_change(self, quality: str) -> None:
        self.settings_status.setText(f"Response quality active: {self.router.set_response_quality(quality)}")
    def _refresh_command_assist(self, text: str) -> None:
        suggestions = self.router.suggest_commands(text)
        self.command_suggestions.setText(f"Suggestions: {' | '.join(suggestions)}" if suggestions else "Suggestions: -")
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
        self.intent_hint_label.setText("Intent: -" if not intent_explanation else f"Intent: {intent_explanation}")
    def _append_welcome_message(self) -> None:
        self._append_chat_bubble(
            "Halo! Saya OrionDesk AI Assistant. Saya siap membantu Anda mengelola sistem. Ketik command atau pilih quick action di samping.",
            align_right=False,
            subtitle="💡 Contoh: open vscode, mode focus on",
        )
    def _append_chat_bubble(self, message: str, align_right: bool, subtitle: str | None = None) -> None:
        self.output_panel.add_message(text=message, is_user=align_right, subtitle=subtitle)
    def _handle_quick_action(self, command: str) -> None:
        if command == "clear chat": self._handle_clear_chat(); return
        self.command_input.setText(command)
        self._handle_execute()
    def _handle_suggestion_chip(self, command: str) -> None:
        self.command_input.setText(command)
        self.command_input.setFocus()
    def _handle_clear_chat(self) -> None:
        self.output_panel.clear()
        self.message_count = 0; self.command_count = 0
        self._update_command_stats()
        self._append_welcome_message()
        self.command_input.clear()
        self._refresh_command_assist("")
    def _update_command_stats(self) -> None:
        self.message_count_label.setText(str(self.message_count))
        self.command_count_label.setText(str(self.command_count))
    def _handle_execute(self) -> None:
        command = self.command_input.text()
        if command.strip(): self.output_panel.show_typing_indicator()
        if self._should_run_async(command): self._run_async_command(command); return
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
        self._active_thread = None; self._active_worker = None
        self.execute_button.setEnabled(True)
        self.command_input.setEnabled(True)
        self.loading_label.setText("")
    def _render_execution_result(self, command: str, result) -> None:
        self.output_panel.hide_typing_indicator()
        if command.strip():
            self._append_chat_bubble(command, align_right=True, subtitle="Command")
            self.message_count += 1
            self.command_count += 1
        if result.requires_confirmation:
            warning = self.persona_engine.format_warning(
                result.message,
                detail=f"Command: {result.pending_command}",
            )
            self._append_chat_bubble(with_status_badge(warning), align_right=False, subtitle="Safe mode confirmation")
            self.message_count += 1
            approved = show_confirmation_dialog(self, self.theme, result.pending_command or command)
            response = self.router.confirm_pending(approved)
            styled_response = self.persona_engine.format_output(response.message)
            self._append_chat_bubble(with_status_badge(styled_response), align_right=False)
            self.message_count += 1
        else:
            styled_response = self.persona_engine.format_output(result.message)
            self._append_chat_bubble(with_status_badge(styled_response), align_right=False)
            self.message_count += 1
        self._update_command_stats()
        self.command_input.clear()
        self._refresh_command_assist("")
        self.output_panel.scroll_to_latest()
        self.output_panel.setFocus()
    def _handle_persona_change(self, persona_name: str) -> None:
        self._animate_output_fade()
        self.persona_engine.set_persona(persona_name)
        persona_message = self.persona_engine.format_output(f"Persona aktif: {persona_name}")
        self._append_chat_bubble(persona_message, align_right=False)
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
    def _setup_output_animation(self) -> None:
        self.output_effect = None
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
        if self.output_effect is not None:
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
