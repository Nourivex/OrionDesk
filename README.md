# OrionDesk

OrionDesk adalah personal OS agent lokal untuk Windows 11 yang fokus pada keamanan, modularitas, dan arsitektur headless-compatible.

## Fitur Saat Ini

- Command router keyword-based (`open`, `search file`, `sys info`)
- Launcher aplikasi berbasis alias map + `subprocess`
- File search berbasis `pathlib`
- System tools berbasis `psutil` (CPU, RAM, process list)
- Persona layer (style output, warning verbosity, risk tolerance)
- Safe mode default untuk command berisiko (`delete`, `kill`, `shutdown`)
- UI PySide6 dengan dark mode, persona selector, dan output console
- UI modern Windows 11 feel (material effect attempt, animation, tray, hotkey)
- Snapshot test PNG untuk validasi tampilan
- Workflow automation engine dengan recipe JSON + retry + approval hook

## Menjalankan Aplikasi

```powershell
pip install -r requirements.txt
python main.py
```

## Menjalankan Test

```powershell
pytest -q
```

## Dokumentasi

- Roadmap: `docs/ROADMAP.md`
- Finish notes: `docs/finish/`
- Baseline tampilan v1: `docs/assets/v1/oriondesk-baseline.png`
- Baseline tampilan v2: `docs/assets/v2/oriondesk-baseline.png`

## Status Fase

- PHASE 0–12: Done
- ROADMAP v3 / v1.3: Active Planning (PHASE 11–15)
