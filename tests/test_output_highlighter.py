from PySide6.QtGui import QTextDocument

from ui.output_highlighter import OutputHighlighter


def test_output_highlighter_has_persona_and_status_rules() -> None:
    document = QTextDocument()
    highlighter = OutputHighlighter(document)
    tokens = {rule.token for rule in highlighter.rules}

    assert "[Calm]" in tokens
    assert "[Hacker]" in tokens
    assert "Blocked" in tokens
