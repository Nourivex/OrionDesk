# PHASE 20 — Theme Tokens + UI Scalability + Snapshot Refresh

## Ringkasan

PHASE 20 menyelesaikan fondasi maintainable UI v1.4 dengan memisahkan design tokens, style layer, dan acceptance checks. Fokus utama fase ini adalah konsistensi visual/struktur, kebersihan theming, serta snapshot matrix yang lebih stabil dan scalable.

## Scope yang Diselesaikan

### Visual Consistency

- Radius dipusatkan di token (`radius_sm`, `radius_md`, `radius_lg`).
- Spacing dipusatkan di token (`spacing_xs`, `spacing_sm`, `spacing_md`, `spacing_lg`).
- Hardcoded color di `ui/main_window.py` dihilangkan.
- Button states konsisten (`default`, `hover`, `pressed`) dari style layer yang sama.

### Structural Consistency

- Semua tab content memakai padding standar berbasis token spacing.
- Header/top spacing diseragamkan menggunakan token.
- Snapshot matrix diperluas per-tab untuk menjaga konsistensi lintas layout.

### Theming

- Theme tokens dipisah ke file independen (`ui/theme_tokens.py`).
- Semantic token dipetakan ke stylesheet melalui `ui/style_layers.py`.
- Theme override mendukung swap/eksperimen tanpa ubah logic UI.

### Maintainability

- Stylesheet utama dipisahkan dari GUI class.
- Rule style duplikat untuk state kritikal diminimalkan dan dites.
- Acceptance test ditambahkan untuk menjaga guardrail UI v1.4.

## Perubahan Teknis

- `ui/theme_tokens.py`
  - Menambahkan `ThemeTokens` dan `default_dark_tokens()`.
- `ui/style_layers.py`
  - Menambahkan `build_main_window_stylesheet(tokens, focus_color)`.
- `ui/main_window.py`
  - Refactor penggunaan warna/spacing/radius agar token-driven.
  - Delegasi stylesheet ke style layer.
  - Fokus animation color memakai semantic token.
- `tests/test_theme_system.py`
  - Test override token, mapping stylesheet, dan button states.
- `tests/test_ui_acceptance_v14.py`
  - Test guardrail untuk no-hardcoded-color, scale consistency, dan duplicate-rule checks.
- `tests/test_ui_snapshot.py`
  - Snapshot otomatis per tab + auto-clean asset png versi lama berdasar roadmap aktif.

## Validasi

- Seluruh test lulus.
- Snapshot baseline v4 diperbarui untuk semua tab utama dan dua ukuran layar.
