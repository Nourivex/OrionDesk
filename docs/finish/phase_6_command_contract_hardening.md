# PHASE 6 — Command Contract Hardening

- Tanggal: 2026-02-17
- Status: Selesai

## Ringkasan Perubahan

PHASE 6 memperkuat kontrak command pada router agar parsing/validasi lebih ketat dan konsisten.

## Yang Diimplementasikan

- Kontrak command eksplisit melalui model `CommandContract`.
- Whitelist command terdaftar:
  - `open <app_alias>`
  - `search file <query>`
  - `sys info`
  - `delete <path>`
  - `kill <process_name_or_pid>`
  - `shutdown`
- Validasi argumen minimum/maksimum dan subcommand tetap.
- Batas panjang command (`300` karakter) untuk mencegah input berlebihan.
- Pesan error usage yang seragam berbasis kontrak.

## File Diubah

- Diubah: `core/router.py`
- Diubah: `tests/test_router.py`

## Validasi

- Unit test router ditambah untuk:
  - invalid usage pada command contract
  - unknown command rejection
  - long command rejection
  - dangerous command argument enforcement
- `pytest -q` lulus setelah perubahan.
