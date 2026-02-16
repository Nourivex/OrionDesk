# PHASE 5 — UI Polish (Windows 11 Feel)

- Tanggal: 2026-02-16
- Status: Selesai

## Ringkasan Perubahan

PHASE 5 menyelesaikan polishing UI dengan tampilan modern minimalis dan menambahkan test snapshot otomatis berbasis PNG.

## UI Update

- Menambahkan tema dark mode dengan gaya rounded controls.
- Menggunakan font `Segoe UI`.
- Menambahkan selector persona di bagian atas window.
- Menjaga flow input command + execute + output panel tetap sederhana.

## Snapshot Test Flow

Test baru menjalankan alur otomatis berikut:

1. Buka window OrionDesk.
2. Ambil screenshot window.
3. Simpan sebagai PNG current.
4. Arsipkan ke folder archive bertimestamp.
5. Bandingkan dengan baseline PNG jika baseline sudah ada.
6. Jika baseline belum ada, baseline dibuat otomatis.

## Peningkatan Keterbacaan Snapshot

- Snapshot offscreen kini distabilkan dengan skala DPI tetap (`QT_SCALE_FACTOR=1`).
- Font komponen utama diperbesar saat capture agar teks terbaca jelas.
- Konten contoh ditulis ke output panel sebelum screenshot untuk validasi visual yang lebih informatif.

## File Diubah

- Diubah: `ui/main_window.py`
- Ditambahkan: `tests/test_ui_snapshot.py`
- Diubah: `.gitignore`

## Validasi

- Semua test lulus setelah PHASE 5.
- Snapshot pipeline aktif di `pytest`.
