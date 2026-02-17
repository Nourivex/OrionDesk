from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ThemeTokens:
    window_bg: str
    text_primary: str
    text_secondary: str
    text_muted: str
    text_title: str
    card_bg: str
    panel_bg: str
    panel_border: str
    tab_bg: str
    tab_active_bg: str
    tab_text: str
    tab_active_text: str
    input_bg: str
    input_text: str
    input_border: str
    input_focus: str
    input_focus_active: str
    button_bg: str
    button_hover: str
    button_pressed: str
    button_text: str
    output_bg: str
    output_text: str
    suggestion_text: str
    hint_text: str
    intent_text: str
    radius_sm: int
    radius_md: int
    radius_lg: int
    spacing_xs: int
    spacing_sm: int
    spacing_md: int
    spacing_lg: int

    def with_overrides(self, **kwargs) -> "ThemeTokens":
        return replace(self, **kwargs)


def default_dark_tokens() -> ThemeTokens:
    return ThemeTokens(
        window_bg="#1b1f2a",
        text_primary="#e7eaf2",
        text_secondary="#9ea7be",
        text_muted="#b3bbd4",
        text_title="#ffffff",
        card_bg="#202636",
        panel_bg="#272e42",
        panel_border="#39425d",
        tab_bg="#222a3d",
        tab_active_bg="#2d3853",
        tab_text="#b9c2db",
        tab_active_text="#ffffff",
        input_bg="#272e42",
        input_text="#f4f6fc",
        input_border="#39425d",
        input_focus="#5A8BFF",
        input_focus_active="#79A5FF",
        button_bg="#4f8dfd",
        button_hover="#669cff",
        button_pressed="#3f7de7",
        button_text="#ffffff",
        output_bg="#272e42",
        output_text="#f4f6fc",
        suggestion_text="#b2bdd9",
        hint_text="#95c7ff",
        intent_text="#f5c586",
        radius_sm=4,
        radius_md=8,
        radius_lg=8,
        spacing_xs=4,
        spacing_sm=8,
        spacing_md=12,
        spacing_lg=16,
    )


def default_light_tokens() -> ThemeTokens:
    return ThemeTokens(
        window_bg="#f3f5fb",
        text_primary="#1f2533",
        text_secondary="#4b5670",
        text_muted="#6a748c",
        text_title="#121826",
        card_bg="#ffffff",
        panel_bg="#f9fbff",
        panel_border="#c9d2e3",
        tab_bg="#e8edf7",
        tab_active_bg="#dbe6fb",
        tab_text="#3e4c6b",
        tab_active_text="#1b2a4a",
        input_bg="#ffffff",
        input_text="#1f2533",
        input_border="#b5c1d9",
        input_focus="#4f7fe5",
        input_focus_active="#2f66dd",
        button_bg="#4f7fe5",
        button_hover="#5c8cf2",
        button_pressed="#3d6fd8",
        button_text="#ffffff",
        output_bg="#ffffff",
        output_text="#1f2533",
        suggestion_text="#5a6886",
        hint_text="#355ea8",
        intent_text="#7a5c2b",
        radius_sm=4,
        radius_md=8,
        radius_lg=8,
        spacing_xs=4,
        spacing_sm=8,
        spacing_md=12,
        spacing_lg=16,
    )
