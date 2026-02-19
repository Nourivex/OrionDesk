from __future__ import annotations

from ui.theme_tokens import ThemeTokens


def build_main_window_stylesheet(tokens: ThemeTokens, focus_color: str) -> str:
    return f"""
        QMainWindow {{ background-color: {tokens.window_bg}; color: {tokens.text_primary}; }}
        QLabel {{ color: {tokens.text_primary}; font-weight: 600; }}
        QLabel#titleLabel {{ font-size: 18px; font-weight: 700; color: {tokens.text_title}; }}
        QLabel#subtitleLabel {{ font-size: 11px; color: {tokens.text_secondary}; font-weight: 500; }}
        QLabel#systemStatusPill {{
            font-size: 10px;
            color: {tokens.input_focus_active};
            border: 1px solid {tokens.panel_border};
            border-radius: {tokens.radius_md + 5}px;
            padding: {tokens.spacing_xs}px {tokens.spacing_md}px;
            background-color: {tokens.card_bg};
        }}
        QLabel#activeTabLabel {{ font-size: 10px; color: {tokens.hint_text}; font-weight: 600; }}
        QLabel#placeholderTitle {{ font-size: 15px; color: {tokens.text_title}; font-weight: 700; }}
        QLabel#placeholderText {{ font-size: 11px; color: {tokens.text_muted}; }}
        QLabel#sectionTitle {{ font-size: 13px; color: {tokens.text_title}; font-weight: 700; }}
        QLabel#sectionHint {{ font-size: 10px; color: {tokens.text_secondary}; font-weight: 500; }}
        QLabel#commandSuggestions {{ font-size: 10px; color: {tokens.suggestion_text}; }}
        QLabel#commandHint {{ font-size: 10px; color: {tokens.hint_text}; }}
        QLabel#intentHint {{ font-size: 10px; color: {tokens.intent_text}; }}
        QLabel#loadingHint {{ font-size: 10px; color: {tokens.hint_text}; font-weight: 600; }}
        QLabel#typingIndicator {{ font-size: 11px; color: {tokens.text_secondary}; font-weight: 600; }}
        QLabel#statsValue {{ font-size: 22px; color: {tokens.hint_text}; font-weight: 700; }}
        QLabel#statsLabel {{ font-size: 10px; color: {tokens.text_secondary}; font-weight: 600; }}
        QCheckBox {{ color: {tokens.text_primary}; font-weight: 600; spacing: {tokens.spacing_sm}px; }}
        QCheckBox::indicator {{
            width: 14px;
            height: 14px;
            border: 1px solid {tokens.input_border};
            border-radius: 4px;
            background-color: {tokens.input_bg};
        }}
        QCheckBox::indicator:checked {{
            background-color: {tokens.input_focus};
            border: 1px solid {tokens.input_focus_active};
        }}
        QFrame#commandSidebar,
        QFrame#personaCard,
        QFrame#quickActionsCard,
        QFrame#commandStatsCard,
        QFrame#inputShellCard {{
            background-color: {tokens.card_bg};
            border: 1px solid {tokens.panel_border};
            border-radius: {tokens.radius_md}px;
        }}
        QTabWidget#mainTabs::pane {{
            border: 1px solid {tokens.panel_border};
            border-radius: {tokens.radius_md}px;
            background-color: {tokens.panel_bg};
        }}
        QTabBar::tab {{
            background: {tokens.tab_bg};
            color: {tokens.tab_text};
            padding: {tokens.spacing_sm}px {tokens.spacing_md}px;
            margin-right: {tokens.spacing_xs}px;
            border-top-left-radius: {tokens.radius_sm + 2}px;
            border-top-right-radius: {tokens.radius_sm + 2}px;
        }}
        QTabBar::tab:selected {{
            background: {tokens.tab_active_bg};
            color: {tokens.tab_active_text};
            border-bottom: 2px solid {tokens.input_focus};
        }}
        QLineEdit, QComboBox, QTextBrowser#aboutInfo, QTextBrowser#memoryInfo, QTextBrowser#diagnosticsInfo {{
            background-color: {tokens.input_bg};
            color: {tokens.input_text};
            border: 1px solid {tokens.input_border};
            border-radius: {tokens.radius_sm}px;
            padding: {tokens.spacing_sm}px;
        }}
        QListWidget#memoryRecentList {{
            background-color: {tokens.input_bg};
            color: {tokens.input_text};
            border: 1px solid {tokens.input_border};
            border-radius: {tokens.radius_sm}px;
            padding: {tokens.spacing_sm}px;
        }}
        QListWidget#memoryRecentList::item {{ padding: {tokens.spacing_sm}px; }}
        QListWidget#memoryRecentList::item:selected {{
            background-color: {tokens.tab_active_bg};
            color: {tokens.tab_active_text};
        }}
        QComboBox {{ padding-right: {tokens.spacing_lg + 6}px; }}
        QComboBox:hover {{ border: 1px solid {tokens.input_focus}; }}
        QComboBox::drop-down {{ border: none; width: 18px; }}
        QComboBox QAbstractItemView {{
            background-color: {tokens.input_bg};
            color: {tokens.input_text};
            border: 1px solid {tokens.panel_border};
            selection-background-color: {tokens.tab_active_bg};
            selection-color: {tokens.input_text};
        }}
        QPushButton#quickActionButton,
        QPushButton#clearChatButton,
        QPushButton#suggestionChip {{
            background-color: {tokens.tab_bg};
            color: {tokens.tab_text};
            border: 1px solid {tokens.panel_border};
            border-left: 3px solid {tokens.input_focus};
            border-radius: {tokens.radius_sm + 3}px;
            padding: {tokens.spacing_sm}px {tokens.spacing_md}px;
            font-weight: 600;
            text-align: left;
        }}
        QPushButton#sendButton {{
            background-color: {tokens.button_bg};
            color: {tokens.button_text};
            border: none;
            border-radius: {tokens.radius_md}px;
            padding: {tokens.spacing_sm}px {tokens.spacing_lg}px;
            font-weight: 700;
        }}
        QLineEdit#commandInput {{ border: 1px solid {focus_color}; }}
        QLineEdit#commandInput:focus {{
            border: 1px solid {tokens.input_focus_active};
            background-color: {tokens.tab_active_bg};
        }}
        QPushButton {{
            background-color: {tokens.button_bg};
            color: {tokens.button_text};
            border: none;
            border-radius: {tokens.radius_md}px;
            padding: {tokens.spacing_sm}px {tokens.spacing_lg}px;
            font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {tokens.button_hover}; }}
        QPushButton:pressed {{ background-color: {tokens.button_pressed}; }}
        QScrollArea#outputPanel {{
            background-color: {tokens.output_bg};
            color: {tokens.output_text};
            border: 1px solid {tokens.panel_border};
            border-radius: {tokens.radius_md}px;
            padding: {tokens.spacing_md}px;
            font-family: 'Cascadia Code';
            font-size: 10pt;
            line-height: 1.4;
        }}
    """
