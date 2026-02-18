# PHASE 36 — Ollama Embedding Foundation

## Ringkasan

PHASE 36 menambahkan foundation embedding lokal berbasis Ollama untuk roadmap v8 / v2.1.

## Scope yang Diselesaikan

- Embedding provider interface ditambahkan.
- Implementasi provider Ollama ditambahkan dengan default model `nomic-embed-text:latest`.
- Health check endpoint untuk validasi runtime Ollama/model ditambahkan.
- Config surface host/model/timeout ditambahkan melalui environment variable:
  - `ORIONDESK_OLLAMA_HOST`
  - `ORIONDESK_EMBED_MODEL`
  - `ORIONDESK_OLLAMA_TIMEOUT`
- Router API untuk embedding foundation ditambahkan:
  - `embedding_config()`
  - `embedding_health()`
  - `embed_text(...)`
- Diagnostics panel menampilkan status embedding runtime.

## Perubahan Teknis

- `core/embedding_provider.py`
- `core/router.py`
- `ui/main_window.py`
- `tests/test_embedding_provider.py`
- `tests/test_router.py`

## Validasi

- `pytest -q tests/test_embedding_provider.py tests/test_router.py`
- Test UI terkait tetap lulus pada suite yang berjalan.

## Dampak

- OrionDesk v2.1 memiliki fondasi semantic embedding lokal siap untuk PHASE 37 (multi-step intent graph).
- Status embedding bisa dipantau langsung dari panel diagnostics.
