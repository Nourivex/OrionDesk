# PHASE 18 — About + Diagnostics Panels

## Ringkasan

PHASE 18 menambahkan panel `About` dan `Diagnostics` yang benar-benar fungsional pada tab shell v1.4. Informasi aplikasi kini visible langsung di GUI, dan fitur observability/recovery dari backend dapat diakses user lewat tombol UI.

## Scope yang Diselesaikan

- `About` panel menampilkan:
  - versi aplikasi (`v1.4`)
  - release channel aktif
  - mode operasi
  - build focus
- `Diagnostics` panel menampilkan:
  - status panel dan instruksi penggunaan
  - tombol `Generate Report` (integrasi `router.create_diagnostic_report()`)
  - tombol `Save Recovery Snapshot` (integrasi `router.save_recovery_snapshot()`)
- Reorder tab sesuai arahan terbaru:
  - `Command`, `Memory`, `Settings`, `Diagnostics`, `About`
- Memory tab diaktifkan sebagai panel ringkasan (`router.memory_summary()`) dengan tombol refresh.

## Perubahan Teknis

- `ui/main_window.py`
  - menambahkan builder panel:
    - `_build_about_tab()`
    - `_build_memory_tab()`
    - `_build_diagnostics_tab()`
  - menambahkan refresh/action handler:
    - `_refresh_about_panel()`
    - `_refresh_memory_panel()`
    - `_refresh_diagnostics_panel()`
    - `_generate_diagnostic_report()`
    - `_save_recovery_snapshot()`
  - update event tab change agar panel dapat refresh saat dipilih.
  - update stylesheet untuk komponen informasi berbasis `QTextBrowser`.
- `tests/test_tab_shell.py`
  - update ekspektasi urutan tab phase 18.
  - tambah test panel `About` dan `Diagnostics`.

## Dampak

- Fitur observability backend kini usable dari UI tanpa command manual.
- About panel menjadi sumber cepat untuk metadata build/channel.
- Struktur tab lebih konsisten untuk flow kerja user:
  command-first, lalu memory/settings/diagnostics, dengan about di posisi terakhir.

## Validasi

- Unit test UI shell dan panel phase 18 lulus.
- Snapshot regression tetap dijaga melalui baseline v4.
