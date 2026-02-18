# PHASE 38 — Complex Reasoning Engine

## Ringkasan

PHASE 38 menambahkan reasoning layer di atas intent graph untuk menghasilkan keputusan plan yang lebih aman dan explainable.

## Scope yang Diselesaikan

- Confidence scoring per-step.
- Semantic confidence adjustment berbasis embedding availability.
- Branch fallback untuk step ambigu (mode `fallback` ke explain path).
- Risk-aware pruning untuk step high-risk dengan confidence rendah.
- Router API baru: `reason_plan(raw_input)`.

## Perubahan Teknis

- `core/reasoning_engine.py`
- `core/router.py`
- `tests/test_reasoning_engine.py`
- `tests/test_router.py`

## Validasi

- `pytest -q tests/test_reasoning_engine.py tests/test_router.py`

## Dampak

- Request kompleks kini tidak hanya dipecah jadi graph, tetapi juga dievaluasi lewat reasoning policy sebelum eksekusi.
- Foundation siap dipakai untuk PHASE 39 (argument extraction + multi-command executor).
