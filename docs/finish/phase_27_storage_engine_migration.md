# PHASE 27 — Storage Engine Migration (JSON to SQLite)

## Ringkasan

PHASE 27 memindahkan storage utama OrionDesk dari file JSON ke SQLite untuk meningkatkan reliability, queryability, dan kesiapan skenario concurrent access.

## Scope yang Diselesaikan

- Menambahkan storage engine SQLite dengan migration runner versioned.
- Menambahkan repository layer untuk `preferences`, `notes`, `command history`, dan `session logs`.
- Memigrasikan `MemoryEngine` ke backend SQLite tanpa mengubah public API.
- Memigrasikan `SessionLayer` ke backend SQLite dengan kompatibilitas API (`record`, `recent`, `clear`, `export_json`, `entries`).
- Menambahkan compatibility adapter import data lama dari JSON (`preferences.json`, `notes.json`, `commands.json`) saat bootstrap.

## Perubahan Teknis

- `core/storage/sqlite_engine.py`
  - Engine SQLite headless-compatible.
  - Migration applier berbasis folder `core/storage/migrations`.
- `core/storage/migrations/0001_initial.sql`
  - Schema awal: `preferences`, `notes`, `commands`, `session_logs`, `schema_migrations`.
- `core/storage/repositories.py`
  - Repository modular per domain data.
- `core/memory_engine.py`
  - JSON file storage diganti repository SQLite.
  - Legacy JSON import tetap tersedia untuk transisi.
- `core/session.py`
  - Session persistence berpindah ke SQLite per `session_name`.

## Validasi

- Test terfokus PHASE 27 lulus:
  - `tests/test_memory_engine.py`
  - `tests/test_session_layer.py`
  - `tests/test_storage_sqlite_phase27.py`

## Dampak

- Data layer lebih stabil dan siap untuk fase lanjutan automation/watcher.
- Query agregasi command history lebih efisien dari backend SQL.
- Modul lama tetap berjalan karena API memory/session tidak berubah.
