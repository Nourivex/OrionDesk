Target kita (Roadmap v4 / Update v1.4):  
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

## 🚀 ROADMAP v4 (Active / v1.4)

- PHASE 17 — Tab Shell Refactor (UI Information Architecture)
- PHASE 18 — About + Diagnostics Panels
- PHASE 19 — Command Assist & Discoverability
- PHASE 20 — Theme Tokens + UI Scalability + Snapshot Refresh

## 📌 Status Fase

### Roadmap v1 (Arsip)

- PHASE 0–5: **Done**
- Detail dipindahkan ke: `docs/FINISHED.md`

### Roadmap v2 (Aktif)

- PHASE 6: **Done** — Command Contract Hardening
- PHASE 7: **Done** — Command History & Session Layer
- PHASE 8: **Done** — Plugin Architecture
- PHASE 9: **Done** — Security Hardening
- PHASE 10: **Done** — Windows 11 Native Feel Upgrade

### Roadmap v3 (Aktif / v1.3)

- PHASE 11: **Done** — Local Intent Intelligence Layer
- PHASE 12: **Done** — Workflow Automation & Task Recipes
- PHASE 13: **Done** — Knowledge & Memory Engine (Local-first)
- PHASE 14: **Done** — Observability, Reliability, and Recovery
- PHASE 15: **Done** — Deployment, Distribution, and Upgrade Manager
- PHASE 16: **Done** — UI Excellence & Accessibility Polish

### Roadmap v4 (Aktif / v1.4)

- PHASE 17: **Planned** — Tab Shell Refactor (UI Information Architecture)
- PHASE 18: **Planned** — About + Diagnostics Panels
- PHASE 19: **Planned** — Command Assist & Discoverability
- PHASE 20: **Planned** — Theme Tokens + UI Scalability + Snapshot Refresh

### Catatan Perubahan Arah

- Nama root project diseragamkan menjadi `OrionDesk/` (bukan `CuaOS/`).
- PHASE 1 dipertahankan tanpa NLP, fokus pada kontrak command stabil untuk fondasi PHASE 2.

## 📚 Arsip Spesifikasi v2 (PHASE 6-10)

## 🔹 PHASE 6 — Command Contract Hardening

Tujuan: Kontrak command lebih ketat dan seragam.

Cakupan:

- Command whitelist terpusat
- Usage/format validation per command
- Argument min/max validation
- Subcommand validation (`search file`, `sys info`)
- Batas panjang input command

Output fase:

- Parser dan validator command stabil untuk pengembangan lanjutan.

---

## 🔹 PHASE 7 — Command History & Session Layer

Tujuan: Menyediakan histori command per sesi secara headless.

Cakupan:

- Session layer terpisah dari GUI
- Record command, result message, dan status
- Recent history retrieval
- Session export ke JSON

Output fase:

- Riwayat command siap dipakai untuk fitur history UI dan audit ringan.

---

## 🔹 PHASE 8 — Plugin Architecture

Tujuan: Modul dapat auto-register tanpa edit router utama.

Cakupan:

- Interface plugin command handler
- Registry plugin terpusat
- Auto-discovery/auto-register plugin lokal
- Router membaca command dari registry

Output fase:

- Ekosistem modul lebih extensible dan scalable.

---

## 🔹 PHASE 9 — Security Hardening

Tujuan: Menguatkan keamanan OrionDesk sebagai local safe agent.

Cakupan:

- Command whitelist enforcement
- Path restriction enforcement
- Process permission guard
- Safe mode policy object

Output fase:

- Command berisiko lebih terkendali dan policy-driven.

---

## 🔹 PHASE 10 — Windows 11 Native Feel Upgrade

Tujuan: Meningkatkan pengalaman visual dan interaksi agar lebih native.

Cakupan:

- Penyelarasan spacing/typography
- Native-like control behavior
- Polishing visual state (hover/focus/active)
- Stabilitas snapshot visual regression

Output fase:

- UI lebih konsisten, modern, dan siap iterasi lanjutan.

## 📚 Arsip Spesifikasi v3 (PHASE 11-16)

## 🔹 PHASE 11 — Local Intent Intelligence Layer

Tujuan: OrionDesk memahami intent user lebih natural tanpa mengorbankan kontrol dan keamanan lokal.

Cakupan:

- Intent classifier lokal berbasis rules + scoring
- Intent fallback chain (strict parser -> semantic parser)
- Confidence score dan reason trace untuk tiap keputusan
- Prompt-less command assist (saran command valid)

Output fase:

- Interaksi command lebih cerdas tanpa kehilangan determinisme.

---

## 🔹 PHASE 12 — Workflow Automation & Task Recipes

Tujuan: User dapat menjalankan rangkaian task berulang sebagai recipe.

Cakupan:

- Format recipe YAML/JSON lokal
- Step runner dengan precondition/postcondition
- Retry policy per step
- Manual approval hook untuk step berisiko

Output fase:

- OrionDesk mampu menjalankan automasi harian secara aman dan dapat diaudit.

---

## 🔹 PHASE 13 — Knowledge & Memory Engine (Local-first)

Tujuan: Menyimpan konteks penting user secara lokal untuk personalisasi yang nyata.

Cakupan:

- Session memory persistence (ringkas, terstruktur)
- Knowledge index untuk preferensi dan shortcut user
- Memory privacy controls (retention, purge, export)
- Query memory API untuk router/persona

Output fase:

- Agent menjadi lebih personal tanpa cloud dependency.

---

## 🔹 PHASE 14 — Observability, Reliability, and Recovery

Tujuan: Menjadikan OrionDesk stabil untuk pemakaian harian jangka panjang.

Cakupan:

- Structured logging dan error taxonomy
- Health checks untuk modul/plugin
- Crash recovery session snapshot
- Diagnostic report generator (lokal)

Output fase:

- Masalah operasional lebih mudah dilacak, diperbaiki, dan dicegah berulang.

---

## 🔹 PHASE 15 — Deployment, Distribution, and Upgrade Manager

Tujuan: Distribusi aplikasi lebih rapi dan update lebih aman untuk user akhir.

Cakupan:

- Build packaging Windows installer
- Channel update (`stable`, `beta`) lokal-aware
- Config migration manager antar versi
- One-click backup/restore profile

Output fase:

- OrionDesk siap dipakai sebagai aplikasi personal OS agent yang matang.

---

## 🔹 PHASE 16 — UI Excellence & Accessibility Polish

Tujuan: Menyempurnakan pengalaman visual dan aksesibilitas agar kualitas desktop app setara produk harian premium.

Cakupan:

- Design token cleanup (spacing, typography scale, radius consistency)
- Accessibility pass (contrast, keyboard traversal, focus visibility)
- Rich output UX (status badges, semantic coloring, readability)
- Snapshot visual matrix (multi-size baseline + regression checks)

Output fase:

- UI OrionDesk konsisten, nyaman dipakai lama, dan siap kualitas rilis publik.

## 🧩 Spesifikasi v4 (PHASE 17-20)

## 🔹 PHASE 17 — Tab Shell Refactor (UI Information Architecture)

Tujuan: Mengubah UI dari single-screen menjadi shell bertab agar fitur bisa scale tanpa menumpuk layout.

Cakupan:

- Tab architecture utama (`Command`, `About`, `Settings`, `Memory`, `Diagnostics`)
- Isolasi komponen per tab
- Routing event antar-tab yang bersih

Output fase:

- Fondasi UI modular siap menampung fitur baru.

---

## 🔹 PHASE 18 — About + Diagnostics Panels

Tujuan: Menyediakan surface user-visible untuk informasi aplikasi dan kesehatan sistem.

Cakupan:

- About panel (versi, channel, info build)
- Diagnostics panel (health checks, log tail, recovery snapshot info)
- Tombol ekspor report diagnostics

Output fase:

- Observability backend menjadi fitur UI yang mudah dipakai user.

---

## 🔹 PHASE 19 — Command Assist & Discoverability

Tujuan: Mengurangi trial-error input command melalui bantuan interaktif di UI.

Cakupan:

- Suggestion list command valid berdasarkan kontrak plugin
- Inline hint usage saat user mengetik
- Intent explanation ringan ("did you mean")

Output fase:

- UX command lebih discoverable dan onboarding lebih cepat.

---

## 🔹 PHASE 20 — Theme Tokens + UI Scalability + Snapshot Refresh

Tujuan: Mengurangi hardcoded styling agar iterasi desain besar lebih murah dan terukur.

Cakupan:

- Refactor stylesheet ke design tokens
- Konsolidasi spacing/radius/typography constants
- Snapshot matrix refresh untuk seluruh layout tab utama
- Milestone rilis UI v1.4 dengan acceptance checklist

Output fase:

- UI maintainable, scalable, dan siap evolusi roadmap berikutnya.

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
