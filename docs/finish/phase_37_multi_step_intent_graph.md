# PHASE 37 — Multi-step Intent Graph

## Ringkasan

PHASE 37 menambahkan fondasi intent graph untuk memecah input kompleks menjadi langkah berurutan yang dapat ditrace.

## Scope yang Diselesaikan

- Intent decomposition dari satu input menjadi beberapa step.
- Step typing (`read`, `analyze`, `execute`, `verify`) berdasarkan command semantics.
- Dependency ordering antar-step (`S1 -> S2 -> S3`).
- Reason trace per-step dengan confidence metadata.
- Router API baru: `intent_graph(raw_input)`.

## Perubahan Teknis

- `core/intent_graph.py`
- `core/router.py`
- `tests/test_intent_graph.py`
- `tests/test_router.py`

## Validasi

- `pytest -q tests/test_intent_graph.py tests/test_router.py`

## Dampak

- OrionDesk v2.1 kini memiliki planning graph lokal untuk request multi-step.
- Fondasi ini siap dipakai di PHASE 38 (complex reasoning engine).
