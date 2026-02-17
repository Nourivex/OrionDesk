from core.intent_engine import LocalIntentEngine


def test_intent_engine_strict_keyword() -> None:
    engine = LocalIntentEngine()
    result = engine.resolve("open notepad", allowed_keywords={"open", "search", "sys"})

    assert result.resolved == "open notepad"
    assert result.reason == "strict_keyword"


def test_intent_engine_semantic_open() -> None:
    engine = LocalIntentEngine()
    result = engine.resolve("tolong bukakan notepad", allowed_keywords={"open", "search", "sys"})

    assert result.resolved == "open notepad"
    assert result.reason == "semantic_open"


def test_intent_engine_semantic_search_file() -> None:
    engine = LocalIntentEngine()
    result = engine.resolve("tolong cari file report.pdf dong", allowed_keywords={"open", "search", "sys"})

    assert result.resolved == "search file report.pdf"
    assert result.reason == "semantic_search"


def test_intent_engine_semantic_sys() -> None:
    engine = LocalIntentEngine()
    result = engine.resolve("status system sekarang", allowed_keywords={"open", "search", "sys"})

    assert result.resolved == "sys info"
    assert result.reason == "semantic_sys"


def test_intent_engine_unresolved() -> None:
    engine = LocalIntentEngine()
    result = engine.resolve("abcdef ghijk", allowed_keywords={"open", "search", "sys"})

    assert result.reason == "unresolved"