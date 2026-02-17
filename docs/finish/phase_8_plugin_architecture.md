# PHASE 8 — Plugin Architecture (Auto-Register)

- Tanggal: 2026-02-17
- Status: Selesai

## Ringkasan Perubahan

PHASE 8 menambahkan arsitektur plugin command agar router tidak lagi hardcode command mapping.

## Implementasi

- Package plugin baru di `plugins/`.
- Auto-discovery plugin module dengan pola `*_plugin.py`.
- Registry plugin memuat command definition secara dinamis.
- Router auto-register:
  - command contract
  - handler command non-dangerous
  - daftar dangerous keyword

## Plugin Bawaan

- `plugins/core_commands_plugin.py`
  - `open`, `search`, `sys`
- `plugins/safe_mode_plugin.py`
  - `delete`, `kill`, `shutdown`

## File Diubah

- Ditambahkan: `core/plugin_registry.py`
- Ditambahkan: `plugins/__init__.py`
- Ditambahkan: `plugins/core_commands_plugin.py`
- Ditambahkan: `plugins/safe_mode_plugin.py`
- Diubah: `core/router.py`
- Ditambahkan: `tests/test_plugin_registry.py`
- Diubah: `tests/test_router.py`

## Validasi

- `pytest -q` lulus setelah implementasi.
