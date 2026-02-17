# PHASE 21 — Settings Priority Panel + Theme Selection (Light Mode)

## Ringkasan

PHASE 21 mengubah tab `Settings` dari placeholder menjadi panel pengaturan inti yang benar-benar bisa dipakai. Fitur utama fase ini adalah `theme selection` dengan dukungan `light mode` yang apply real-time.

## Scope yang Diselesaikan

- Settings panel berisi pengaturan prioritas:
  - Theme (`dark` / `light`)
  - Release channel (`stable` / `beta`)
  - Minimize to tray on close
- Theme selection apply langsung tanpa restart aplikasi.
- About panel otomatis sinkron saat release channel berubah.

## Perubahan Teknis

- `ui/theme_tokens.py`
  - menambahkan `default_light_tokens()`.
- `ui/main_window.py`
  - menambahkan builder `Settings` tab fungsional.
  - menambahkan handler:
    - `_handle_theme_change()`
    - `_handle_channel_change()`
    - `_handle_minimize_tray_toggled()`
  - wiring signal settings controls ke runtime state.
- `tests/test_tab_shell.py`
  - menambahkan test untuk theme selection `light mode`.

## Dampak

- User bisa mengubah tampilan aplikasi langsung dari Settings.
- Pengaturan channel dan behavior close app lebih discoverable.
- Fondasi settings siap diperluas untuk fase berikutnya.

## Validasi

- Unit test lulus termasuk skenario selection `light` di Settings tab.
