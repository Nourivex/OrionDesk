# v6 Interface Closure Audit (Penutupan v6 + Blueprint v7)

## Ringkasan

Dokumen ini menutup v6 dari sisi interface dan menjadi handoff resmi menuju redesign v7 dengan arah visual **Pro Ops Console**.

## Pain Points Saat Ini (v6)

- Hierarki visual antar panel belum cukup tegas untuk workflow operasional cepat.
- Status runtime masih tersebar dan belum hadir sebagai rail global yang konsisten.
- Informasi beberapa tab masih dominan text-dump, belum berbasis struktur ringkas + status badges.
- Snapshot governance sebelumnya terlalu permisif (rawan drift baseline lintas environment).
- Metadata UI (versi/build/channel) sempat tidak tersentralisasi secara konsisten.

## Target UI v7

- Identitas visual `Pro Ops Console`, dark-first dengan light parity.
- Shell 3 zona tetap: header operasional, workspace utama, status rail global.
- Density medium-dense berbasis token (`row height`, `card padding`, `gap`).
- Status semantics kuat (success/warning/blocked/info) lewat token warna khusus.
- Semua tab (`Command`, `Memory`, `Settings`, `Diagnostics`, `About`) dirework dengan struktur state yang konsisten.

## Risiko Migrasi UI

- Risiko regressions visual pada resolusi kecil (`1024x640`).
- Potensi mismatch snapshot bila baseline di-refresh tanpa gate proses.
- Risiko accessibility drop saat densitas dinaikkan.
- Potensi inkonsistensi dark/light parity saat menambah semantic token baru.

## UX KPI Baseline (Awal v7)

- Command execution path time (input → response render).
- Click count ke panel diagnostics utama.
- Time-to-find untuk setting hotkey/theme.
- Navigation friction score antar tab (keyboard traversal).

## Guardrail Implementasi v7

- Native PySide6 only (tanpa dependency eksternal baru).
- Tidak mengubah business logic command engine di luar kebutuhan UI surface.
- Snapshot baseline hanya di-refresh saat milestone desain final, bukan per perubahan kecil.
- UI release checklist wajib: contrast, keyboard traversal, dark/light parity, 2-size snapshot.
