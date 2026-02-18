# PHASE 32 — Command Workspace Refresh (Persona Rail + Chat Command Surface)

## Ringkasan

PHASE 32 menyelesaikan pembaruan halaman `Command` ke format workspace chat modern dengan sidebar persona, quick actions, stats, input shell, dan suggestion chips sesuai target wireframe v7.

## Scope yang Diselesaikan

- Refactor layout tab `Command` menjadi dua kolom: sidebar kiri dan chat area kanan.
- Menambahkan selector persona dengan opsi `calm`, `professional`, `hacker`, `friendly`, `minimal`.
- Menambahkan quick actions: `Open VSCode`, `Open Notepad`, `Focus Mode`, `System Status`, `Clear Chat`.
- Menambahkan kartu statistik `Messages` dan `Commands` yang update setelah eksekusi command.
- Menambahkan suggestion chips (`capability system info`, `clip show`, `mode game on`) untuk input cepat.
- Menambahkan alur clear chat yang mereset panel output, statistik, dan mengembalikan welcome message.
- Menyesuaikan tampilan chat ke format bubble user/assistant agar lebih dekat ke wireframe target.
- Migrasi rendering chat ke arsitektur native (`QScrollArea` + `ChatBubbleWidget`) untuk kontrol layout yang lebih presisi.
- Memecah setiap tab UI ke `ui/pages/*.py` agar `MainWindow` fokus ke orchestration.
- Menurunkan ukuran `ui/main_window.py` menjadi <= 500 baris untuk maintainability.

## Perubahan Dokumen

- `docs/ROADMAP.md`
  - PHASE 32 ditandai `Done` pada status fase.
  - Ringkasan roadmap v7 menampilkan PHASE 32 dengan penanda selesai.

## Perubahan Teknis

- `ui/main_window.py`
  - Refactor command tab ke model sidebar + chat area.
  - Penambahan quick action handlers, clear chat handler, stats counters, suggestion chip handlers.
  - Integrasi counters dengan lifecycle eksekusi command dan perubahan persona.
  - Integrasi output chat berbasis widget-native.
- `ui/chat_surface.py`
  - `ChatBubbleWidget` untuk bubble user/assistant.
  - `ChatSurface` sebagai container chat berbasis `QScrollArea`.
- `ui/pages/command_page.py`
- `ui/pages/memory_page.py`
- `ui/pages/settings_page.py`
- `ui/pages/diagnostics_page.py`
- `ui/pages/about_page.py`
- `ui/pages/__init__.py`
- `ui/window_helpers.py`
  - `CommandWorker`, `with_status_badge`, dan `show_confirmation_dialog`.
- `ui/style_layers.py`
  - Penambahan style token-driven untuk komponen command workspace baru.
- `tests/test_tab_shell.py`
  - `test_phase32_command_workspace_components`
  - `test_phase32_command_workspace_stats_and_clear_chat`

## Validasi

- `pytest -q tests/test_tab_shell.py tests/test_ui_acceptance_v14.py`
- Hasil: `16 passed`

## Dampak

- Halaman `Command` kini selaras dengan baseline visual v7 yang lebih modern dan padat informasi.
- UX command lebih cepat lewat quick actions, suggestion chips, dan input flow bergaya chat.
- Batas arsitektur tetap terjaga: business logic tetap di layer non-GUI.
