from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class GenerationConfig:
    host: str = "http://localhost:11434"
    model: str = "gemma3:4b"
    timeout_seconds: float = 8.0
    token_budget: int = 256
    temperature: float = 0.2


@dataclass(frozen=True)
class GenerationHealth:
    ok: bool
    message: str


class GenerationProvider:
    def config(self) -> GenerationConfig:
        raise NotImplementedError()

    def health(self) -> GenerationHealth:
        raise NotImplementedError()

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        raise NotImplementedError()


class OllamaGenerationProvider(GenerationProvider):
    def __init__(
        self,
        config: GenerationConfig,
        request_json: Callable[[str, dict | None, float], dict] | None = None,
    ) -> None:
        self._config = config
        self._request_json = request_json or self._default_request_json

    def config(self) -> GenerationConfig:
        return self._config

    def health(self) -> GenerationHealth:
        try:
            payload = self._request_json(f"{self._config.host}/api/tags", None, self._config.timeout_seconds)
        except (OSError, ValueError) as error:
            return GenerationHealth(False, f"Generation model offline: {error}")

        models = payload.get("models", []) if isinstance(payload, dict) else []
        available = any(item.get("name") == self._config.model for item in models if isinstance(item, dict))
        if available:
            return GenerationHealth(True, f"Generation model ready ({self._config.model})")
        return GenerationHealth(False, f"Generation model not found: {self._config.model}")

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        clean = prompt.strip()
        if not clean:
            return ""

        payload = {
            "model": self._config.model,
            "prompt": clean,
            "stream": False,
            "options": {
                "temperature": self._config.temperature,
                "num_predict": self._config.token_budget,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt.strip()

        response = self._request_json(
            f"{self._config.host}/api/generate",
            payload,
            self._config.timeout_seconds,
        )
        text = response.get("response", "") if isinstance(response, dict) else ""
        return text.strip() if isinstance(text, str) else ""

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
