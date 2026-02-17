# PHASE 17 — Tab Shell Refactor (UI Information Architecture)

- Tanggal: 2026-02-17
- Status: Selesai

## Ringkasan Perubahan

PHASE 17 mengubah UI OrionDesk dari single-screen menjadi shell bertab untuk fondasi arsitektur UI yang scalable.

## Implementasi

- Menambahkan tab utama:
  - `Command`
  - `About`
  - `Settings`
  - `Memory`
  - `Diagnostics`
- Command workflow existing dipindah ke tab `Command` tanpa memindahkan business logic ke GUI.
- Menambahkan event routing sederhana antar-tab melalui `currentChanged` + active tab indicator.
- Menambahkan placeholder panel terisolasi untuk tab non-command (siap dipakai PHASE 18+).

## File Diubah

- Diubah: `ui/main_window.py`
- Ditambahkan: `tests/test_tab_shell.py`

## Validasi

- `pytest -q` lulus setelah refactor.
