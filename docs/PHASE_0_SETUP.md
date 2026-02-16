# PHASE 0 — Setup Project

## Tujuan

Dokumen ini menjelaskan implementasi awal OrionDesk agar skeleton project dapat berjalan sesuai roadmap:

- Window PySide6 tampil
- Ada input command
- Ada output panel
- Ada tombol execute
- Routing command dasar sudah terhubung
- Arsitektur tetap headless-compatible

## Struktur Folder

```text
OrionDesk/
├── main.py
├── core/
│   └── router.py
├── modules/
│   ├── launcher.py
│   ├── file_manager.py
│   └── system_tools.py
├── persona/
│   ├── persona_engine.py
│   └── profiles/
│       ├── calm.json
│       └── hacker.json
├── ui/
│   └── main_window.py
└── tests/
    ├── test_router.py
    ├── test_launcher.py
    ├── test_file_manager.py
    ├── test_system_tools.py
    └── test_persona_engine.py
```

## Cara Kerja Singkat

1. GUI menerima input command dari user.
2. GUI meneruskan command ke `CommandRouter`.
3. Router memetakan keyword ke modul terkait (`open`, `search file`, `sys info`).
4. Hasil modul diformat oleh `PersonaEngine`.
5. Output ditampilkan kembali ke panel GUI.

Business logic tidak ditaruh di layer UI agar engine dapat diuji tanpa GUI.

## Menjalankan Aplikasi

```powershell
pip install -r requirements.txt
python main.py
```

## Menjalankan Test

```powershell
pytest -q
```

## Contoh Command

- `open vscode`
- `search file report.pdf`
- `sys info`

Pada PHASE 0, modul masih berupa implementasi dasar (stub) untuk menyiapkan fondasi arsitektur.