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
- Knowledge & memory engine local-first (preferences, notes, command memory)
- Observability & recovery (structured logs, health checks, diagnostics, snapshots)
- Deployment/upgrade managers (release channel, config migration, profile backup-restore)
- UI accessibility polish (shortcuts, tab order, multi-size snapshot matrix)
- System capability layer (`capability` + `smart`) dengan guardrail permission tier dan preview-safe actions
- Smart command assist (autocorrect typo, argument hint, explain mode)
- Real risky actions backend (`kill`, `delete`, `shutdown`) dengan guard confirmation themed
- Safe execution profiles (`strict`, `balanced`, `power`, `explain-only`) dengan risk-aware policy

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
- Baseline tampilan aktif (berdasarkan roadmap): `docs/assets/v5/`

## Status Fase

- PHASE 0–25: Done
- ROADMAP v4 / v1.4: Completed (PHASE 17–21)
- ROADMAP v5 / v1.5: Active Planning (PHASE 22–26)
