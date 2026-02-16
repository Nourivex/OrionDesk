# PHASE 2 — Module Implementation

- Tanggal: 2026-02-16
- Status: Selesai

## Ringkasan Perubahan

PHASE 2 menyelesaikan implementasi real untuk tiga modul utama:

- `Launcher` membuka aplikasi via `subprocess.Popen`
- `FileManager` melakukan pencarian file berbasis `pathlib`
- `SystemTools` menampilkan info CPU, RAM, dan daftar proses via `psutil`

## Perubahan Kode

- Diubah: `modules/launcher.py`
- Diubah: `modules/file_manager.py`
- Diubah: `modules/system_tools.py`
- Diubah: `tests/test_launcher.py`
- Diubah: `tests/test_file_manager.py`
- Diubah: `tests/test_system_tools.py`

## Detail Teknis

### Launcher

- Alias aplikasi dipetakan dari `alias_map`.
- Eksekusi dilakukan dengan `subprocess.Popen(..., shell=True)`.
- Menampilkan PID proses saat berhasil.
- Menangani error OS dan alias yang tidak terdaftar.

### File Manager

- Akar pencarian default: `Path.home()`.
- Traversal file: `Path.rglob("*")`.
- Matching: substring case-insensitive pada nama file.
- Mendukung batas hasil melalui `max_results`.
- Menangani kondisi root tidak ada dan error I/O.

### System Tools

- CPU usage dari `psutil.cpu_percent`.
- RAM usage dari `psutil.virtual_memory`.
- Daftar proses aktif dari `psutil.process_iter`.
- Output multiline yang siap ditampilkan di GUI.

## Validasi

- `pytest -q` lulus setelah perubahan PHASE 2.

## Dampak ke Fase Berikutnya

- PHASE 3 dapat fokus pada persona output style tanpa perubahan besar di modul.
- Fondasi data sistem sudah siap untuk integrasi warning verbosity dan risk messaging.
