Target kita (Roadmap v2):  
**OrionDesk – Windows 11 Personal OS Agent (Local, Safe, Modular)**

---

# 🎯 Visi Awal (Scope Biar Nggak Meledak)

Versi 1.0 harus bisa:

- Launch aplikasi
- Cari file
- Jalankan command aman
- Tampilkan output di GUI
- Punya persona system sederhana
- Safe mode default

Tanpa:
- LLM dulu
- Tanpa async berat
- Tanpa automation mouse/keyboard
- Tanpa sandbox ribet

---

# 🗺️ ROADMAP OrionDesk (PySide6)

## 🚀 ROADMAP v2 (Active)

- PHASE 6 — Command Contract Hardening
- PHASE 7 — Command History & Session Layer
- PHASE 8 — Plugin Architecture (auto-register module ke router)
- PHASE 9 — Security Hardening
  - Command whitelist
  - Path restriction enforcement
  - Process permission guard
  - Safe mode policy object
- PHASE 10 — Windows 11 Native Feel Upgrade

## 📌 Status Fase

### Roadmap v1 (Arsip)

- PHASE 0–5: **Done**
- Detail dipindahkan ke: `docs/FINISHED.md`

### Roadmap v2 (Aktif)

- PHASE 6: **Planned** — Command Contract Hardening
- PHASE 7: **Planned** — Command History & Session Layer
- PHASE 8: **Planned** — Plugin Architecture
- PHASE 9: **Planned** — Security Hardening
- PHASE 10: **Planned** — Windows 11 Native Feel Upgrade

### Catatan Perubahan Arah

- Nama root project diseragamkan menjadi `OrionDesk/` (bukan `CuaOS/`).
- PHASE 1 dipertahankan tanpa NLP, fokus pada kontrak command stabil untuk fondasi PHASE 2.

## 📚 Arsip Spesifikasi v1 (PHASE 0-5)

## 🔹 PHASE 0 — Setup Project (Hari Ini)

Tujuan: Skeleton project jalan.

Struktur:

```
CuaOS/
│
├── main.py
├── ui/
│   ├── main_window.py
│
├── core/
│   ├── router.py
│
├── modules/
│   ├── launcher.py
│   ├── file_manager.py
│   ├── system_tools.py
│
├── persona/
│   ├── profiles/
│   │   ├── calm.json
│   │   ├── hacker.json
│   └── persona_engine.py
```

Install:

```powershell
pip install PySide6 psutil
```

Goal:
Window muncul dengan:
- Input command
- Output panel
- Execute button

---

## 🔹 PHASE 1 — Core Command Router

Bikin command pattern sederhana:

Contoh input:

```
open vscode
search file report.pdf
sys info
```

Router akan:
- Parse keyword pertama
- Kirim ke module yang sesuai

Tidak pakai NLP dulu.
Keyword-based saja.

---

## 🔹 PHASE 2 — Module Implementation

### 1️⃣ Launcher Module
- Map alias → path aplikasi
- Gunakan `subprocess.Popen`

Contoh:
```
open vscode
open chrome
```

---

### 2️⃣ File Manager Module
- Search file pakai pathlib
- Optional: batasi drive dulu (misal C:/Users)

---

### 3️⃣ System Tools Module
- psutil:
  - CPU usage
  - RAM usage
  - Running process list

---

## 🔹 PHASE 3 — Persona Layer

Persona hanya mempengaruhi:

- Cara output ditampilkan
- Warning verbosity
- Risk tolerance

Contoh:

calm:
```
Saya akan membuka VS Code untuk Anda.
```

hacker:
```
Launching VS Code. Stay sharp.
```

Engine tetap sama.
Persona cuma style.

---

## 🔹 PHASE 4 — Safe Mode Engine

Tambahkan:

```
self.safe_mode = True
```

Jika:
- delete
- kill process
- shutdown

Maka:
- Tampilkan dialog konfirmasi
- Butuh klik manual

---

## 🔹 PHASE 5 — UI Polish (Windows 11 Feel)

Di PySide6:

- Dark mode
- Rounded button
- Segoe UI font
- Acrylic-ish background (opsional)
- Minimalist design

Layout ideal:

```
+--------------------------------+
| OrionDesk                     |
+--------------------------------+
| Persona: [calm ▼]             |
+--------------------------------+
| > [ input box               ] |
| [ Execute ]                  |
+--------------------------------+
| Output console area           |
|                               |
+--------------------------------+
```

---

# 🧠 Architecture Philosophy (Penting)

Engine tidak tahu GUI.

GUI hanya:
- Ambil input
- Kirim ke router
- Tampilkan output

Engine harus bisa jalan headless juga.

Itu bikin clean architecture.

---

# ⚙️ Milestone Timeline (Santai Sampai Rabu)

Hari 1:
- Setup PySide6 window
- Basic router

Hari 2:
- Launcher + file search

Hari 3:
- Persona layer

Hari 4:
- Safe mode

Hari 5:
- UI polish

---
