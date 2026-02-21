from PySide6.QtWidgets import QApplication

from ui.chat_surface import ChatSurface
from ui.theme_tokens import default_dark_tokens


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_chat_surface_typing_stage_transition_flow() -> None:
    app = _app()
    surface = ChatSurface(default_dark_tokens())
    surface.show()
    app.processEvents()

    surface.show_typing_indicator(stage="impact_assessment", expected_ms=150)
    app.processEvents()
    assert "impact assessment" in surface.typing_indicator.text()

    surface.update_typing_stage("generation", 180.0)
    app.processEvents()
    assert "ghost writing" in surface.typing_indicator.text()

    surface.update_typing_stage("final_validation", 60.0)
    app.processEvents()
    assert "final validation" in surface.typing_indicator.text()

    surface.hide_typing_indicator(final_state="final_validation")
    app.processEvents()
    assert surface.typing_indicator.isHidden() is True


def test_chat_surface_typing_stage_fallback_for_unknown_stage() -> None:
    app = _app()
    surface = ChatSurface(default_dark_tokens())
    app.processEvents()

    surface.show_typing_indicator(stage="unknown-stage", expected_ms=100)
    app.processEvents()

    assert "impact assessment" in surface.typing_indicator.text()


def test_chat_surface_fallback_trace_path_keeps_typing_visible_then_hides() -> None:
    app = _app()
    surface = ChatSurface(default_dark_tokens())
    surface.show()
    app.processEvents()

    surface.show_typing_indicator(stage="impact_assessment", expected_ms=150)
    surface.update_typing_stage("final_validation", 0.0)
    app.processEvents()
    assert surface.typing_indicator.isVisible() is True

    surface.hide_typing_indicator(final_state="final_validation")
    app.processEvents()
    assert surface.typing_indicator.isHidden() is True


def test_chat_surface_typing_indicator_not_orphan_after_final_hide() -> None:
    app = _app()
    surface = ChatSurface(default_dark_tokens())
    surface.show()
    app.processEvents()

    surface.show_typing_indicator(stage="generation", expected_ms=200)
    app.processEvents()
    assert any(
        surface.messages_layout.itemAt(index).widget() is not None
        and surface.messages_layout.itemAt(index).widget().objectName() == "chatTypingRow"
        for index in range(surface.messages_layout.count())
    )

    surface.hide_typing_indicator(final_state="final_validation")
    app.processEvents()
    assert all(
        surface.messages_layout.itemAt(index).widget() is None
        or surface.messages_layout.itemAt(index).widget().objectName() != "chatTypingRow"
        for index in range(surface.messages_layout.count())
    )
