# PHASE 19 — Command Assist & Discoverability

## Ringkasan

PHASE 19 menambahkan bantuan interaktif di tab `Command` agar user tidak trial-error saat mengetik command. UI sekarang memberikan suggestion command valid, usage hint, dan intent explanation ringan secara real-time.

## Scope yang Diselesaikan

- Suggestion list command valid berbasis kontrak command router.
- Usage hint inline saat keyword command terdeteksi.
- Intent explanation (`Did you mean`) untuk input natural/semantic.
- Snapshot test diperluas untuk semua tab utama OrionDesk (bukan hanya default tab).

## Perubahan Teknis

- `core/router.py`
  - API discoverability baru:
    - `suggest_commands(raw_input, limit=5)`
    - `usage_hint(raw_input)`
    - `explain_intent(raw_input)`
    - `list_command_keywords()`
- `ui/main_window.py`
  - Menambahkan komponen assist pada panel command:
    - `command_suggestions`
    - `command_hint_label`
    - `intent_hint_label`
  - Menambahkan update real-time via `command_input.textChanged`.
- `tests/test_router.py`
  - Menambahkan test untuk suggestion, usage hint, dan intent explanation.
- `tests/test_tab_shell.py`
  - Menambahkan test update command assist di UI.
- `tests/test_ui_snapshot.py`
  - Snapshot matrix sekarang capture per tab:
    - `Command`, `Memory`, `Settings`, `Diagnostics`, `About`
  - Masing-masing pada ukuran `1280x760` dan `1024x640`.
  - Auto-clean asset PNG versi lama mengikuti roadmap versi aktif.

## Dampak

- Onboarding command lebih cepat karena command valid terlihat langsung.
- Input natural user lebih mudah dipahami lewat intent explanation ringan.
- Baseline visual regression menjadi lebih kuat karena mencakup seluruh tab utama.

## Validasi

- Seluruh unit test lulus setelah implementasi.
- Snapshot baseline v4 berhasil diperbarui untuk setiap tab utama.
