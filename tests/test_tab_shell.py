from PySide6.QtWidgets import QApplication
from pathlib import Path

from core.router import CommandRouter
from ui.main_window import MainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_has_phase18_tabs() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    names = [window.tab_widget.tabText(index) for index in range(window.tab_widget.count())]
    assert names == ["Command", "Memory", "Settings", "Diagnostics", "About"]

    window.close()


def test_phase18_about_and_diagnostics_panels() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(4)
    app.processEvents()
    assert "OrionDesk v1.6" in window.about_info.toPlainText()

    window.tab_widget.setCurrentIndex(3)
    app.processEvents()
    diagnostics_text = window.diagnostics_info.toPlainText()
    assert "Diagnostics panel siap" in diagnostics_text

    window.close()


def test_memory_page_has_summary_cards() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(1)
    app.processEvents()

    assert window.memory_page.total_commands_value.text().isdigit()
    assert window.memory_page.top_command_value.text() != ""
    assert ":" in window.memory_page.last_refresh_value.text()
    assert window.memory_page.recent_activity_list.count() >= 1
    assert "Safe Mode Trigger" in window.memory_page.safe_mode_triggers_value.text()
    assert "Session Duration" in window.memory_page.session_duration_value.text()

    window.close()


def test_phase19_command_assist_updates() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.command_input.setText("sys")
    app.processEvents()

    assert "sys info" in window.command_hint_label.text()
    assert "sys info" in window.command_suggestions.text()

    window.command_input.setText("tolong bukakan vscode")
    app.processEvents()
    assert "Did you mean" in window.intent_hint_label.text()

    window.close()


def test_phase21_settings_theme_selection_light_mode() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(2)
    app.processEvents()

    window.theme_selector.setCurrentText("light")
    app.processEvents()

    assert window.theme_selector.currentText() == "light"
    assert "Theme active: light" in window.settings_status.text()

    window.close()


def test_phase24_command_assist_argument_hints() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.command_input.setText("capability")
    app.processEvents()

    assert "Args:" in window.command_hint_label.text()
    assert "file list <path>" in window.command_hint_label.text()

    window.close()


def test_search_command_runs_in_async_mode() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    assert window._should_run_async("search report.pdf") is True
    assert window._should_run_async("tolong bukakan notepad") is True
    assert window._should_run_async("open notepad") is False

    window.close()


def test_tab_shell_has_icons_for_modern_ui() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    for index in range(window.tab_widget.count()):
        assert window.tab_widget.tabIcon(index).isNull() is False

    window.close()


def test_main_window_default_close_does_not_minimize_to_tray() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    window.show()
    app.processEvents()

    assert window.minimize_to_tray is False
    window.close()
    app.processEvents()
    assert window.isVisible() is False


def test_phase30_settings_hotkey_and_fast_surface_controls() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(2)
    app.processEvents()

    assert window.hotkey_selector.currentText() in {"Win+Shift+O", "Ctrl+Shift+O", "Alt+Space"}
    assert window.fast_mode_checkbox.isChecked() is True

    window.close()


def test_phase43_settings_chat_model_and_quality_controls() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(2)
    app.processEvents()

    assert window.refresh_models_button.icon().isNull() is False
    assert "[" in window.model_selector.currentText() and "•" in window.model_selector.currentText()

    if window.model_selector.count() > 1:
        window.model_selector.setCurrentIndex(1)
    model_target = window.settings_page.selected_model_name()
    window.chat_model_checkbox.setChecked(True)
    window.token_budget_selector.setCurrentText("384")
    window.timeout_selector.setCurrentText("12.0")
    window.temperature_selector.setCurrentText("0.3")
    window.quality_selector.setCurrentText("deep")
    app.processEvents()

    config = window.router.generation_config()
    assert config["model"] == model_target
    assert config["token_budget"] == 384
    assert window.router.chat_model_enabled is True
    assert window.router.response_quality == "deep"
    assert "Response quality active" in window.settings_status.text()

    window.close()


def test_phase30_fast_surface_focuses_command_input() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.tab_widget.setCurrentIndex(3)
    app.processEvents()
    window._activate_fast_command_surface()
    app.processEvents()

    assert window.tab_widget.currentIndex() == 0

    window.close()


def test_phase32_command_workspace_components() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    personas = [window.persona_selector.itemText(index) for index in range(window.persona_selector.count())]
    assert personas == ["calm", "professional", "hacker", "friendly", "minimal"]

    quick_labels = [button.text() for button in window.quick_action_buttons]
    assert any("Open VSCode" in label for label in quick_labels)
    assert any("Open Notepad" in label for label in quick_labels)
    assert any("Focus Mode" in label for label in quick_labels)
    assert any("System Status" in label for label in quick_labels)
    assert any("Clear Chat" in label for label in quick_labels)

    assert window.execute_button.text() == "Send"
    assert window.clear_chat_button.text() == "Clear"
    assert window.message_count_label.text() == "0"
    assert window.command_count_label.text() == "0"
    assert window.output_panel.__class__.__name__ == "ChatSurface"
    assert hasattr(window.output_panel, "add_message")
    assert "OrionDesk AI Assistant" in window.output_panel.toPlainText()

    window.close()


def test_phase32_command_workspace_stats_and_clear_chat() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.command_input.setText("sys info")
    window._handle_execute()
    app.processEvents()

    assert window.command_count == 1
    assert window.message_count >= 2
    assert window.command_count_label.text() == "1"
    assert "OrionDesk AI Assistant" not in window.output_panel.toPlainText()

    window._handle_quick_action("clear chat")
    app.processEvents()

    assert window.command_count == 0
    assert window.message_count == 0
    assert "Ketik command atau pilih quick action" in window.output_panel.toPlainText()

    window.close()


def test_phase32_main_window_file_size_target() -> None:
    content = Path("ui/main_window.py").read_text(encoding="utf-8")
    assert len(content.splitlines()) <= 500


def test_command_surface_typing_indicator_lifecycle() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    window.show()
    app.processEvents()

    window.output_panel.show_typing_indicator()
    app.processEvents()
    assert window.output_panel.typing_indicator.isHidden() is False

    window.command_input.setText("sys info")
    window._handle_execute()
    app.processEvents()
    assert window.output_panel.typing_indicator.isVisible() is False
    assert all(
        window.output_panel.messages_layout.itemAt(index).widget().objectName() != "chatTypingRow"
        for index in range(window.output_panel.messages_layout.count())
        if window.output_panel.messages_layout.itemAt(index).widget() is not None
    )

    window.close()


def test_chat_surface_prunes_old_messages_for_performance() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    for index in range(210):
        window.output_panel.add_message(text=f"message-{index}", is_user=False)
    app.processEvents()

    assert len(window.output_panel._history) <= 200

    window.close()


def test_chat_surface_typing_tick_safe_when_indicator_deleted() -> None:
    app = _app()
    window = MainWindow(router=CommandRouter())
    app.processEvents()

    window.output_panel.show_typing_indicator()
    window.output_panel.typing_indicator.deleteLater()
    app.processEvents()

    window.output_panel._tick_typing()
    app.processEvents()

    window.close()