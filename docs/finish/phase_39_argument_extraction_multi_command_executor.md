# PHASE 39 — Argument Extraction + Multi-command Executor

## Ringkasan

PHASE 39 menambahkan fondasi parsing argumen detail dan eksekusi multi-command dengan mode bundling, report status, dan guarded handling.

## Scope yang Diselesaikan

- Fine-grained argument extraction per command:
  - `keyword`
  - `args`
  - `target`
  - `path`
  - `mode`
  - `flags`
- Multi-command bundling mode:
  - `chain`
  - `parallel-eligible`
  - `guarded`
- Multi-command execution report:
  - `status`
  - `duration_ms`
  - `message`
  - `risk_level`
- Router API:
  - `multi_command_bundle(raw_input)`
  - `execute_multi(raw_input, dry_run=True)`

## Perubahan Teknis

- `core/argument_extractor.py`
- `core/multi_command_executor.py`
- `core/router.py`
- `tests/test_argument_extractor.py`
- `tests/test_multi_command_executor.py`
- `tests/test_router.py`

## Validasi

- `pytest -q tests/test_argument_extractor.py tests/test_multi_command_executor.py tests/test_router.py`

## Dampak

- OrionDesk v2.1 kini mampu memproses satu input menjadi beberapa command dengan struktur argumen yang jelas dan report eksekusi terukur.
- Fondasi siap untuk PHASE 40 stabilization + release gate.
