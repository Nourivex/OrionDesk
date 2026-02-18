from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class EmbeddingConfig:
    host: str = "http://localhost:11434"
    model: str = "nomic-embed-text:latest"
    timeout_seconds: float = 3.0


@dataclass(frozen=True)
class EmbeddingHealth:
    ok: bool
    message: str


class EmbeddingProvider:
    def config(self) -> EmbeddingConfig:
        raise NotImplementedError()

    def health(self) -> EmbeddingHealth:
        raise NotImplementedError()

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError()


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        config: EmbeddingConfig,
        request_json: Callable[[str, dict | None, float], dict] | None = None,
    ) -> None:
        self._config = config
        self._request_json = request_json or self._default_request_json

    def config(self) -> EmbeddingConfig:
        return self._config

    def health(self) -> EmbeddingHealth:
        try:
            payload = self._request_json(f"{self._config.host}/api/tags", None, self._config.timeout_seconds)
        except (OSError, ValueError) as error:
            return EmbeddingHealth(False, f"Ollama offline: {error}")

        models = payload.get("models", []) if isinstance(payload, dict) else []
        target = self._config.model
        available = any(item.get("name") == target for item in models if isinstance(item, dict))
        if available:
            return EmbeddingHealth(True, f"Ollama ready ({target})")
        return EmbeddingHealth(False, f"Model not found: {target}")

    def embed(self, text: str) -> list[float]:
        clean = text.strip()
        if not clean:
            return []

        payload = self._request_json(
            f"{self._config.host}/api/embeddings",
            {"model": self._config.model, "prompt": clean},
            self._config.timeout_seconds,
        )
        values = payload.get("embedding", []) if isinstance(payload, dict) else []
        if not isinstance(values, list):
            return []
        return [float(item) for item in values]

    def _default_request_json(self, url: str, payload: dict | None, timeout_seconds: float) -> dict:
        data = None
        headers = {"Content-Type": "application/json"}
        method = "GET"
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            method = "POST"

        request = urllib.request.Request(url=url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
        return json.loads(body)
