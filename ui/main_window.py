from __future__ import annotations

import ctypes
import ctypes.wintypes

from PySide6.QtCore import QEasingCurve, QEvent, Qt, QVariantAnimation
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.router import CommandRouter
from persona.persona_engine import PersonaEngine
from ui.output_highlighter import OutputHighlighter
from ui.win11_effects import apply_mica_or_acrylic


WM_HOTKEY = 0x0312
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
HOTKEY_ID = 1
KEY_O = 0x4F


class MainWindow(QMainWindow):
    def __init__(self, router: CommandRouter, persona_engine: PersonaEngine | None = None) -> None:
        super().__init__()
        self.router = router
        self.persona_engine = persona_engine or PersonaEngine(persona_name="calm")
        self._input_focus_color = "#5A8BFF"
        self._explicit_quit = False
        self.minimize_to_tray = False
        self._hotkey_registered = False
        self.tray_icon: QSystemTrayIcon | None = None

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
        main_layout.setContentsMargins(16, 14, 16, 16)
        main_layout.setSpacing(10)

        title_bar = QHBoxLayout()
        title_bar.setSpacing(8)
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
        about_tab = self._build_placeholder_tab(
            title="About",
            text="Informasi aplikasi akan ditampilkan di PHASE 18.",
        )
        settings_tab = self._build_placeholder_tab(
            title="Settings",
            text="Konfigurasi user akan ditampilkan pada fase berikutnya.",
        )
        memory_tab = self._build_placeholder_tab(
            title="Memory",
            text="Panel memory lokal akan ditampilkan pada fase berikutnya.",
        )
        diagnostics_tab = self._build_placeholder_tab(
            title="Diagnostics",
            text="Panel health/log diagnostics akan ditampilkan di PHASE 18.",
        )

        self.tab_widget.addTab(command_tab, "Command")
        self.tab_widget.addTab(about_tab, "About")
        self.tab_widget.addTab(settings_tab, "Settings")
        self.tab_widget.addTab(memory_tab, "Memory")
        self.tab_widget.addTab(diagnostics_tab, "Diagnostics")
        self.tab_widget.currentChanged.connect(self._handle_tab_changed)
        main_layout.addLayout(title_bar)
        main_layout.addWidget(self.tab_widget)

        self.execute_button.clicked.connect(self._handle_execute)
        self.command_input.returnPressed.connect(self._handle_execute)
        self.persona_selector.currentTextChanged.connect(self._handle_persona_change)
        self._setup_shortcuts()

        self.setTabOrder(self.persona_selector, self.command_input)
        self.setTabOrder(self.command_input, self.execute_button)
        self.setTabOrder(self.execute_button, self.output_panel)

    def _build_command_tab(self) -> QWidget:
        page = QWidget(self)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(10)

        top_card = QFrame(page)
        top_card.setObjectName("topCard")
        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(12, 10, 12, 10)
        top_layout.setSpacing(10)

        persona_layout = QHBoxLayout()
        command_layout = QHBoxLayout()

        self.persona_label = QLabel("Persona:", page)
        self.persona_selector = QComboBox(page)
        self.persona_selector.addItems(["calm", "hacker"])
        self.persona_selector.setCurrentText(self.persona_engine.persona_name)

        persona_layout.addWidget(self.persona_label)
        persona_layout.addWidget(self.persona_selector)
        persona_layout.addStretch()

        self.command_input = QLineEdit(page)
        self.command_input.setPlaceholderText("Masukkan command, contoh: open vscode")

        self.execute_button = QPushButton("Execute", page)
        self.execute_button.setMinimumWidth(120)
        self.output_panel = QTextEdit(page)
        self.output_panel.setReadOnly(True)
        self.output_panel.setObjectName("outputPanel")
        self.highlighter = OutputHighlighter(self.output_panel.document())

        self.command_input.setAccessibleName("command-input")
        self.persona_selector.setAccessibleName("persona-selector")
        self.execute_button.setAccessibleName("execute-button")
        self.output_panel.setAccessibleName("output-panel")

        top_layout.addLayout(persona_layout)
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.execute_button)
        top_layout.addLayout(command_layout)

        page_layout.addWidget(top_card)
        page_layout.addWidget(self.output_panel)
        return page

    def _build_placeholder_tab(self, title: str, text: str) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 12)
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

    def _handle_execute(self) -> None:
        command = self.command_input.text()
        result = self.router.execute(command)

        if command.strip():
            self.output_panel.append(f"> {command}")

        if result.requires_confirmation:
            warning = self.persona_engine.format_warning(
                result.message,
                detail=f"Command: {result.pending_command}",
            )
            self.output_panel.append(self._with_status_badge(warning))
            approved = self._show_confirmation(result.pending_command or command)
            response = self.router.confirm_pending(approved)
            styled_response = self.persona_engine.format_output(response.message)
            self.output_panel.append(self._with_status_badge(styled_response))
        else:
            styled_response = self.persona_engine.format_output(result.message)
            self.output_panel.append(self._with_status_badge(styled_response))

        self.output_panel.append("")
        self.command_input.clear()

    def _handle_persona_change(self, persona_name: str) -> None:
        self._animate_output_fade()
        self.persona_engine.set_persona(persona_name)
        self.output_panel.append(self.persona_engine.format_output(f"Persona aktif: {persona_name}"))
        self.output_panel.append("")

    def _apply_windows11_style(self) -> None:
        self.setFont(QFont("Segoe UI Variable Text", 10))
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(self._build_stylesheet(self._input_focus_color))

    def _build_stylesheet(self, focus_color: str) -> str:
        return f"""
            QMainWindow {{ background-color: #1b1f2a; color: #f1f4fb; }}
            QLabel {{ color: #e7eaf2; font-weight: 600; }}
            QLabel#titleLabel {{ font-size: 18px; font-weight: 700; color: #ffffff; }}
            QLabel#subtitleLabel {{ font-size: 11px; color: #9ea7be; font-weight: 500; }}
            QLabel#activeTabLabel {{ font-size: 10px; color: #8bb4ff; font-weight: 600; }}
            QFrame#topCard {{
                background-color: #202636;
                border: 1px solid #313a52;
                border-radius: 8px;
            }}
            QTabWidget#mainTabs::pane {{
                border: 1px solid #313a52;
                border-radius: 8px;
                background-color: #1e2434;
            }}
            QTabBar::tab {{
                background: #222a3d;
                color: #b9c2db;
                padding: 8px 12px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background: #2d3853;
                color: #ffffff;
            }}
            QLabel#placeholderTitle {{ font-size: 15px; color: #ffffff; font-weight: 700; }}
            QLabel#placeholderText {{ font-size: 11px; color: #b3bbd4; }}
            QLineEdit, QComboBox {{
                background-color: #272e42;
                color: #f4f6fc;
                border: 1px solid #39425d;
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit#commandInput {{ border: 1px solid {focus_color}; }}
            QPushButton {{
                background-color: #4f8dfd;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #669cff; }}
            QPushButton:pressed {{ background-color: #3f7de7; }}
            QTextEdit#outputPanel {{
                background-color: #272e42;
                color: #f4f6fc;
                border: 1px solid #39425d;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Cascadia Code';
                font-size: 10pt;
                line-height: 1.4;
            }}
        """

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
        self.shortcut_clear.activated.connect(self.output_panel.clear)

    def _with_status_badge(self, message: str) -> str:
        lowered = message.lower()
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
        registered = user32.RegisterHotKey(None, HOTKEY_ID, MOD_WIN | MOD_SHIFT, KEY_O)
        self._hotkey_registered = bool(registered)

    def _toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
            return
        self.showNormal()
        self.activateWindow()
        self.raise_()

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
        color = value.name() if isinstance(value, QColor) else "#5A8BFF"
        self._input_focus_color = color
        self.setStyleSheet(self._build_stylesheet(color))

    def eventFilter(self, watched, event):
        if watched is self.command_input and event.type() == QEvent.Type.FocusIn:
            self.focus_animation.stop()
            self.focus_animation.setStartValue(QColor("#39425d"))
            self.focus_animation.setEndValue(QColor("#79A5FF"))
            self.focus_animation.start()
        if watched is self.command_input and event.type() == QEvent.Type.FocusOut:
            self.focus_animation.stop()
            self.focus_animation.setStartValue(QColor("#79A5FF"))
            self.focus_animation.setEndValue(QColor("#39425d"))
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
        reply = QMessageBox.question(
            self,
            "Konfirmasi Safe Mode",
            f"Command berisiko terdeteksi:\n{command}\n\nLanjutkan aksi ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes