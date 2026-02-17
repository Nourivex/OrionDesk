# PHASE 25 — Safe Execution Profiles + Risk-aware Command Policies

## Ringkasan

PHASE 25 menambahkan policy engine berbasis profile untuk mengatur perilaku command berisiko secara adaptif. OrionDesk sekarang mendukung mode `strict`, `balanced`, `power`, dan `explain-only`.

## Scope yang Diselesaikan

- Profile execution policy:
  - `strict`
  - `balanced`
  - `power`
  - `explain-only`
- Risk level mapping per command.
- Decision layer profile-aware:
  - `blocked`
  - `allow + confirmation`
  - `allow`
  - `explain-only`
- Command runtime untuk mengganti profile:
  - `profile <strict|balanced|power|explain-only>`

## Perubahan Teknis

- `core/execution_profile.py`
  - `ExecutionProfilePolicy`
  - `ProfileDecision`
- `core/router.py`
  - Integrasi profile policy di jalur execute.
  - Risk level pada execution context kini profile-driven.
  - Handler baru `_handle_profile`.
- `plugins/core_commands_plugin.py`
  - registrasi command `profile`.
- `tests/test_execution_profile.py`
  - unit test policy evaluation + integrasi router.

## Dampak

- Command berisiko tidak lagi hanya bergantung pada safe mode global.
- User dapat memilih tingkat agresivitas eksekusi sesuai kebutuhan.
- Mode `explain-only` memberikan jalur aman untuk review sebelum aksi nyata.

## Validasi

- Unit test phase 25 lulus.
- Full regression suite tetap lulus.
