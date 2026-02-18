# PHASE 30 — Global Hotkey UX + Fast Command Surface

## Ringkasan

PHASE 30 menghadirkan akses OrionDesk yang lebih instan melalui global hotkey configurable, conflict detection, dan fast command surface yang fokus ke command input.

## Scope yang Diselesaikan

- Menambahkan manager global hotkey terpisah dan headless-compatible.
- Menambahkan conflict detection terhadap shortcut OS/global dan shortcut internal app.
- Menambahkan pengaturan hotkey di tab Settings.
- Menambahkan mode fast command surface untuk fokus cepat ke command tab/input.
- Menambahkan shortcut lokal `Ctrl+K` untuk membuka fast command surface.

## Perubahan Teknis

- `core/hotkey_manager.py`
  - Normalisasi hotkey
  - Conflict detection
  - Windows hotkey binding parser
- `ui/main_window.py`
  - Settings controls: global hotkey selector + fast mode toggle
  - Runtime re-register global hotkey
  - Fast command surface activation logic
- `tests/test_hotkey_manager.py`
- `tests/test_tab_shell.py`
  - test phase30 settings + fast command behavior

## Validasi

- Unit test hotkey manager lulus.
- UI shell test untuk fitur phase30 lulus.
- Full regression suite lulus.

## Dampak

- Akses command OrionDesk lebih cepat dan launcher-like.
- Konflik shortcut dapat dihindari sebelum hotkey diterapkan.
- Implementasi tetap modular dan menjaga business logic di layer non-GUI.
