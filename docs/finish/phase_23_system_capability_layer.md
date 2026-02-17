# PHASE 23 — System Capability Layer

## Ringkasan

PHASE 23 direframe menjadi `System Capability Layer` dengan 3 lapisan: capability primitives, intent mapping, dan safety guardrails. Implementasi ini membuat OrionDesk lebih agentic, tetapi tetap terkendali dan aman.

## Scope yang Diselesaikan

### 1) Capability Layer (Low-level Tools)

- File ops: `list`, `read`, `hash`, `preview_cleanup`
- Process ops: `list`, `detail`, `terminate` (preview-safe)
- Network ops: `ping` (preview-safe), `interface_summary`
- Utility ops: `time`, `env`, `path`

### 2) Intent Mapping Layer

- Mapping intent natural ke capability plan:
  - "cek koneksi lambat gak sih" → network health check
  - "bersihin folder download" → cleanup preview plan
- Eksekusi plan dilakukan melalui command capability yang sama agar tetap konsisten.

### 3) Safety & Guardrail Layer

- Permission tier (`basic/advanced/admin`)
- Confirmation policy untuk aksi berisiko (`delete/move/terminate`)
- Protected process list (contoh: `explorer.exe`, `winlogon.exe`, `lsass.exe`)
- Sandboxed preview untuk aksi destruktif (no destructive execution by default)

## Perubahan Teknis

- `core/capability_layer.py`
- `core/capability_guardrail.py`
- `core/system_intent_mapper.py`
- `core/router.py`
  - handler baru: `_handle_capability`, `_handle_smart`
- `plugins/core_commands_plugin.py`
  - command baru: `capability`, `smart`
- `tests/test_capability_layers.py`
  - unit test capability, guardrail, dan smart intent mapping

## Dampak

- Surface command bertambah signifikan dengan arsitektur lebih modular.
- Natural request mulai dipetakan ke step-by-step execution plan.
- Guardrail mencegah OrionDesk menjadi engine berisiko secara default.

## Validasi

- Unit test phase 23 lulus.
- Regression suite tetap lulus.
