from dataclasses import dataclass

from core.retrieval_optimizer import RetrievalOptimizer


@dataclass
class Entry:
    command: str
    status: str


def test_retrieval_optimizer_cache_roundtrip() -> None:
    optimizer = RetrievalOptimizer(cache_ttl_seconds=60)

    optimizer.set_cache("k", {"value": 1})

    cached = optimizer.get_cache("k")
    assert cached == {"value": 1}


def test_retrieval_optimizer_ranks_relevant_context() -> None:
    optimizer = RetrievalOptimizer()
    entries = [
        Entry(command="open vscode", status="success"),
        Entry(command="search file report.pdf", status="success"),
        Entry(command="mode focus on", status="success"),
    ]

    ranked = optimizer.rank_session_context(entries, "tolong cari report")

    assert len(ranked) >= 1
    assert ranked[0].command == "search file report.pdf"


def test_retrieval_optimizer_reduces_redundant_patterns() -> None:
    optimizer = RetrievalOptimizer()

    reduced = optimizer.reduce_redundant_patterns(
        ["open vscode", "open   vscode", "sys info", "sys info"]
    )

    assert reduced == ["open vscode", "sys info"]
