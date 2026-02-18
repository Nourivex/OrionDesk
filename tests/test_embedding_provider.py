from core.embedding_provider import EmbeddingConfig, OllamaEmbeddingProvider


def test_ollama_embedding_health_ok_when_model_available() -> None:
    def fake_request(url: str, payload, timeout: float) -> dict:
        assert "/api/tags" in url
        return {"models": [{"name": "nomic-embed-text:latest"}]}

    provider = OllamaEmbeddingProvider(
        config=EmbeddingConfig(model="nomic-embed-text:latest"),
        request_json=fake_request,
    )

    health = provider.health()
    assert health.ok is True
    assert "ready" in health.message.lower()


def test_ollama_embedding_health_fallback_when_offline() -> None:
    def fake_request(_url: str, _payload, _timeout: float) -> dict:
        raise OSError("connection refused")

    provider = OllamaEmbeddingProvider(config=EmbeddingConfig(), request_json=fake_request)

    health = provider.health()
    assert health.ok is False
    assert "offline" in health.message.lower()


def test_ollama_embedding_embed_returns_vector() -> None:
    def fake_request(url: str, payload, timeout: float) -> dict:
        assert "/api/embeddings" in url
        assert payload["prompt"] == "hello"
        assert timeout == 3.0
        return {"embedding": [0.1, 0.2, 0.3]}

    provider = OllamaEmbeddingProvider(
        config=EmbeddingConfig(timeout_seconds=3.0),
        request_json=fake_request,
    )

    vector = provider.embed("hello")
    assert vector == [0.1, 0.2, 0.3]
