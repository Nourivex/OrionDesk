from pathlib import Path

from ui.style_layers import build_main_window_stylesheet
from ui.theme_tokens import default_dark_tokens


def test_main_window_has_no_hardcoded_hex_colors() -> None:
    content = Path("ui/main_window.py").read_text(encoding="utf-8")
    assert "#" not in content


def test_theme_tokens_define_spacing_and_radius_scale() -> None:
    tokens = default_dark_tokens()

    assert tokens.spacing_xs < tokens.spacing_sm < tokens.spacing_md <= tokens.spacing_lg
    assert tokens.radius_sm <= tokens.radius_md <= tokens.radius_lg


def test_stylesheet_rules_not_duplicated_for_button_states() -> None:
    tokens = default_dark_tokens()
    css = build_main_window_stylesheet(tokens, focus_color=tokens.input_focus)

    assert css.count("QPushButton:hover") == 1
    assert css.count("QPushButton:pressed") == 1
