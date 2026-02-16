# PHASE 1 — Core Command Router

- Tanggal: 2026-02-16
- Status: Selesai

## Ringkasan Perubahan

PHASE 1 menyelesaikan command pattern berbasis keyword tanpa NLP, sesuai roadmap awal.
Router kini memiliki parser command terpisah, dispatcher berbasis handler map, serta validasi format command yang konsisten.

## Modul yang Ditambahkan/Diubah

- Diubah: `core/router.py`
- Diubah: `tests/test_router.py`
- Ditambahkan: `.gitignore`

## Jumlah Test

- Total test saat ini: 16
- Test baru/diupdate untuk PHASE 1: 3 test tambahan pada router

## Status Test

- `pytest -q` lulus

## Catatan Teknis Penting

- Arsitektur tetap headless-compatible: router tidak bergantung GUI.
- Command yang didukung tetap fokus pada scope awal:
  - `open <app>`
  - `search file <query>`
  - `sys info`
- Parser menormalisasi keyword ke lowercase agar command case-insensitive.

## Potensi Dampak ke Fase Berikutnya

- PHASE 2 dapat langsung fokus ke implementasi real modul (`subprocess`, `pathlib`, `psutil`) tanpa mengubah kontrak router.
- Struktur handler map memudahkan penambahan command baru secara modular.
