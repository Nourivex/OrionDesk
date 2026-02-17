# OrionDesk

OrionDesk adalah personal OS agent lokal untuk Windows 11 dengan fokus pada keamanan, modularitas, arsitektur headless-compatible, dan pengalaman desktop modern.

## Highlights

- Unified command engine + execution context
- System capability layer (`capability`, `smart`) dengan guardrail
- Smart assist (`autocorrect`, argument hint, explain mode)
- Real action backend untuk command berisiko (`kill`, `delete`, `shutdown`)
- Safe execution profile (`strict`, `balanced`, `power`, `explain-only`)
- UI tabbed modern dengan icon language konsisten
- Visual regression snapshot matrix (v5)

## Arsitektur

- `core/` untuk router, policy, observability, intent, memory, workflow
- `modules/` untuk launcher, file/system tools, dan system actions
- `ui/` untuk shell PySide6 (tanpa business logic)
- `tests/` untuk unit + regression + snapshot tests
- `docs/` untuk roadmap, finish notes, dan wireframe

## Menjalankan Aplikasi

```powershell
pip install -r requirements.txt
python main.py
```

## Menjalankan Test

```powershell
pytest -q
```

## Dokumentasi Utama

- Roadmap: `docs/ROADMAP.md`
- Daftar fase selesai: `docs/FINISHED.md`
- Catatan implementasi per fase: `docs/finish/`
- Wireframe + snapshot terbaru: `docs/WIREFRAME.md`
- Baseline asset aktif: `docs/assets/v5/`

## Status Roadmap

- PHASE 0–26: **Done**
- ROADMAP v4 / v1.4: **Completed** (PHASE 17–21)
- ROADMAP v5 / v1.5: **Completed** (PHASE 22–26)

## Dokumen Penting

- License: `LICENSE`

## Lisensi

Project ini menggunakan lisensi **MIT**. Lihat file `LICENSE` untuk detail lengkap.
