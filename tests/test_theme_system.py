from ui.style_layers import build_main_window_stylesheet
from ui.theme_tokens import default_dark_tokens


def test_theme_tokens_override_changes_value() -> None:
    tokens = default_dark_tokens()
    custom = tokens.with_overrides(button_bg="#101010")

    assert custom.button_bg == "#101010"
    assert tokens.button_bg != custom.button_bg


def test_stylesheet_uses_theme_tokens() -> None:
    tokens = default_dark_tokens().with_overrides(button_bg="#123456", input_focus="#654321")
    css = build_main_window_stylesheet(tokens, focus_color=tokens.input_focus)

    assert "#123456" in css
    assert "#654321" in css


def test_stylesheet_contains_button_states() -> None:
    tokens = default_dark_tokens()
    css = build_main_window_stylesheet(tokens, focus_color=tokens.input_focus)

    assert "QPushButton:hover" in css
    assert "QPushButton:pressed" in css
