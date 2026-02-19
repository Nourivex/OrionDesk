# PHASE 41 — Gemma Runtime Adapter

## Ringkasan

PHASE 41 menambahkan adapter model generatif lokal berbasis Ollama untuk `gemma3:4b`, lengkap dengan health check, config surface, dan fallback strategy saat model tidak tersedia.

## Scope yang Diselesaikan

- Provider abstraksi generasi teks:
  - `GenerationProvider`
  - `OllamaGenerationProvider`
- Config runtime generation dari environment:
  - `host`
  - `model`
  - `timeout_seconds`
  - `token_budget`
  - `temperature`
- Router API baru:
  - `generation_config()`
  - `generation_health()`
  - `generate_reasoned_answer(raw_input)`
- Fallback strategy:
  - Jika model offline/empty response, jawaban fallback berbasis hasil reasoning plan.

## Perubahan Teknis

- `core/generation_provider.py`
- `core/router.py`
- `tests/test_generation_provider.py`
- `tests/test_router.py`

## Validasi

- `pytest -q tests/test_generation_provider.py tests/test_router.py`

## Dampak

- OrionDesk v2.2 siap menggunakan `gemma3:4b` sebagai local generation runtime.
- Jalur fallback memastikan sistem tetap memberikan output yang aman saat model tidak tersedia.
