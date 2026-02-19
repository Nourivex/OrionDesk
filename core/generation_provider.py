from __future__ import annotations

import json
import re
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


@dataclass(frozen=True)
class GenerationModelInfo:
    name: str
    parameter_size: str
    role: str
    gpu_badge: str


class GenerationProvider:
    def config(self) -> GenerationConfig:
        raise NotImplementedError()

    def health(self) -> GenerationHealth:
        raise NotImplementedError()

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        raise NotImplementedError()

    def list_models(self) -> list[GenerationModelInfo]:
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

    def list_models(self) -> list[GenerationModelInfo]:
        payload = self._request_json(f"{self._config.host}/api/tags", None, self._config.timeout_seconds)
        models = payload.get("models", []) if isinstance(payload, dict) else []
        result: list[GenerationModelInfo] = []
        for item in models:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            details = item.get("details", {}) if isinstance(item.get("details"), dict) else {}
            parameter_size = str(details.get("parameter_size", item.get("parameter_size", "-")))
            role = "embed" if "embed" in name.lower() else "chat"
            result.append(
                GenerationModelInfo(
                    name=name,
                    parameter_size=parameter_size,
                    role=role,
                    gpu_badge=self._classify_gpu_badge(parameter_size, role),
                )
            )
        return result

    def _classify_gpu_badge(self, parameter_size: str, role: str) -> str:
        if role == "embed":
            return "Lowest/Embed"
        value = self._parse_billions(parameter_size)
        if value is None:
            return "Unknown"
        if value <= 8:
            return "Aman"
        if value <= 13:
            return "Borderline"
        if value < 30:
            return "High"
        return "Jangan dipaksa"

    def _parse_billions(self, parameter_size: str) -> float | None:
        cleaned = parameter_size.lower().replace(" ", "")
        match = re.search(r"(\d+(?:\.\d+)?)b", cleaned)
        if match is None:
            match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
        if match is None:
            return None
        return float(match.group(1))

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
