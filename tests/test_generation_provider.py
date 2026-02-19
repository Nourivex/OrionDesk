from core.generation_provider import GenerationConfig, OllamaGenerationProvider


def test_ollama_generation_health_ok_when_model_available() -> None:
    def fake_request(url: str, payload: dict | None, timeout: float) -> dict:
        assert "/api/tags" in url
        assert payload is None
        assert timeout == 4.0
        return {"models": [{"name": "gemma3:4b"}]}

    provider = OllamaGenerationProvider(
        config=GenerationConfig(host="http://localhost:11434", model="gemma3:4b", timeout_seconds=4.0),
        request_json=fake_request,
    )

    health = provider.health()
    assert health.ok is True
    assert "ready" in health.message.lower()


def test_ollama_generation_returns_text_response() -> None:
    def fake_request(url: str, payload: dict | None, timeout: float) -> dict:
        assert "/api/generate" in url
        assert payload is not None
        assert payload["model"] == "gemma3:4b"
        assert payload["stream"] is False
        return {"response": "  jawaban model  "}

    provider = OllamaGenerationProvider(
        config=GenerationConfig(model="gemma3:4b", token_budget=64, temperature=0.3),
        request_json=fake_request,
    )

    text = provider.generate("ringkas ini")
    assert text == "jawaban model"


def test_ollama_generation_health_offline() -> None:
    def fake_request(url: str, payload: dict | None, timeout: float) -> dict:
        raise OSError("connection refused")

    provider = OllamaGenerationProvider(
        config=GenerationConfig(model="gemma3:4b"),
        request_json=fake_request,
    )

    health = provider.health()
    assert health.ok is False
    assert "offline" in health.message.lower()


def test_ollama_generation_list_models_with_gpu_badges() -> None:
    def fake_request(url: str, payload: dict | None, timeout: float) -> dict:
        return {
            "models": [
                {"name": "gemma3:4b", "details": {"parameter_size": "4B"}},
                {"name": "llama3:13b", "details": {"parameter_size": "13B"}},
                {"name": "mega:30b", "details": {"parameter_size": "30B"}},
                {"name": "nomic-embed-text:latest", "details": {"parameter_size": "274M"}},
            ]
        }

    provider = OllamaGenerationProvider(config=GenerationConfig(), request_json=fake_request)

    models = provider.list_models()

    badges = {item.name: item.gpu_badge for item in models}
    assert badges["gemma3:4b"] == "Aman"
    assert badges["llama3:13b"] == "Borderline"
    assert badges["mega:30b"] == "Jangan dipaksa"
    assert badges["nomic-embed-text:latest"] == "Lowest/Embed"
