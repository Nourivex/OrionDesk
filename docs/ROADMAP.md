<div align="center">

# 🗺 OrionDesk Roadmap

Strategic roadmap for OrionDesk product evolution, split clearly between legacy Application V1 and active Application V2.1 planning.

</div>

---

## 📌 Document Intent

Roadmap ini sekarang dibagi menjadi dua jalur agar jelas:

1. **Legacy Track (Application V1 / Roadmap v1-v7)** → arsip implementasi yang sudah selesai
2. **Active Track (Application V2.1 / Roadmap v8)** → fokus pengembangan berikutnya

---

## 🚀 Active Track — Application V2.1

### Roadmap v8 (Completed / v2.1)

**North Star**

> OrionDesk menjadi local-first reasoning assistant yang bisa memahami intent kompleks, menyusun multi-step action, dan mengeksekusi multi-command secara aman.

**Core Focus v8_v2.1**

- Local LLM embedding via Ollama (`nomic-embed-text:latest`)
- Multi-step intent planning
- Complex reasoning pipeline
- Detail argument extraction
- Multi-command execution (`2+` perintah dalam satu input) dengan safety guard

### Progress v8 Saat Ini

- ✅ PHASE 36 selesai: Ollama embedding foundation (`nomic-embed-text:latest`, health + config surface)
- ✅ PHASE 37 selesai: multi-step intent graph (decomposition, step typing, dependency chain, reason trace)
- ✅ PHASE 38 selesai: complex reasoning plan (confidence scoring, fallback branch, risk pruning)
- ✅ PHASE 39 selesai: argument extraction detail + multi-command executor report
- ✅ PHASE 40 selesai: stabilization + release gate v2.1

---

## 🎯 Scope V2.1 (What Must Work)

Versi v2.1 harus bisa:

- Menerima input natural yang berisi **lebih dari satu instruksi**
- Memecah input menjadi **intent graph** terstruktur
- Mengekstrak argumen dengan detail (path, target, mode, flags)
- Menjalankan langkah secara berurutan dengan observability dan rollback-aware behavior
- Tetap policy-driven (safe mode, profile risk, confirmation hooks)

Tidak termasuk (pada cycle awal v8):

- Cloud dependency wajib
- Agent autonomy tanpa guardrail
- Arbitrary unrestricted tool execution

---

## 🧩 PHASE Plan — Roadmap v8 / v2.1

### PHASE 36 — Ollama Embedding Foundation ✅

Tujuan:

- Integrasi adapter embedding lokal via Ollama.

Cakupan:

- Embedding provider interface + Ollama implementation
- Default model: `nomic-embed-text:latest`
- Health check endpoint dan fallback status message
- Config surface untuk host/model/timeout

Output:

- Foundation semantic embedding siap dipakai intent/ranking layer.

---

### PHASE 37 — Multi-step Intent Graph ✅

Tujuan:

- Input kompleks diubah menjadi graph langkah aksi yang terstruktur.

Cakupan:

- Intent decomposition (`goal -> steps`)
- Step typing (`read`, `analyze`, `execute`, `verify`)
- Dependency ordering antar-step
- Explainable trace untuk setiap mapping keputusan

Output:

- OrionDesk bisa memahami request multi-step secara deterministik.

---

### PHASE 38 — Complex Reasoning Engine ✅

Tujuan:

- Menambah reasoning orchestration untuk memilih urutan aksi yang paling relevan dan aman.

Cakupan:

- Reasoning loop berbasis local context + embedding recall
- Confidence scoring per-step
- Branch fallback strategy untuk ambiguity
- Safety-aware plan pruning

Output:

- Engine reasoning lokal yang lebih kuat tanpa melepas kontrol policy.

---

### PHASE 39 — Argument Extraction + Multi-command Executor ✅

Tujuan:

- Menjamin input natural dapat dieksekusi menjadi 2+ command nyata secara aman.

Cakupan:

- Fine-grained argument extraction (`target`, `path`, `mode`, `scope`)
- Multi-command bundling (`chain`, `parallel-eligible`, `guarded`)
- Execution report per command (status, duration, reason)
- Confirmation gates untuk high-risk command dalam chain

Output:

- Satu input bisa menghasilkan multi-command execution yang terukur dan dapat diaudit.

---

### PHASE 40 — Stabilization + Release Gate v2.1 ✅

Tujuan:

- Menutup roadmap v8 dengan quality gate sebelum release v2.1.

Cakupan:

- Reliability matrix untuk flow multi-step dan multi-command
- Snapshot + UI acceptance refresh
- Regression tests untuk parser/intent/reasoning/executor
- Final release checklist + migration notes

Output:

- OrionDesk v2.1 siap release dengan baseline engineering yang stabil.

---

## 🚀 Next Track — Application V2.2

### Roadmap v9 (Planned / v2.2)

**Primary Focus**

- Response quality uplift via local model `gemma3:4b`
- Runtime smoothness: soft interaction, low-latency flow, no obvious UI lag
- Better intelligence behavior for complex command reasoning

### PHASE 41 — Gemma Runtime Adapter ✅

- Model adapter untuk `gemma3:4b`
- Health + fallback strategy antara embedding/reasoning model
- Config surface model, timeout, token budget

Output:

- Runtime generation lokal berbasis Gemma aktif dengan fallback aman saat model unavailable.

### PHASE 42 — Latency Budget & Non-blocking Runtime ✅

- End-to-end latency budget per command stage
- Async execution path untuk reasoning-heavy flows
- UI responsiveness guard (main-thread blocking detection)

Output:

- Telemetry latency stage-level dan guard responsivitas tersedia untuk kontrol performa v2.2.

### PHASE 43 — Response Quality Upgrade ✅

- Better answer composition (clear, contextual, actionable)
- Structured reasoning output style
- Error message rewrite agar lebih human-friendly

Output:

- Model chat dan quality profile kini dapat diatur dari tab Settings untuk tuning kualitas respons lokal.
- Catalog model di-load dari Ollama saat startup + refresh manual, dengan badge rekomendasi GPU berbasis `parameter_size`.

### PHASE 44 — Memory + Retrieval Optimization ✅

- Retrieval caching dan query optimization
- Session context ranking tuning
- Reduksi redundant processing pada repeated command patterns

Output:

- Retrieval cache + session-context ranking aktif, dan reasoning response kini lebih intent-aware sesuai input pengguna.
- Untuk natural-language input, respons LLM diprioritaskan lalu action result dijalankan agar output chat lebih natural.

### PHASE 45 — Stabilization + Release Gate v2.2

- Reliability + soak test for long-running sessions
- Performance baseline compare (`v2.1` vs `v2.2`)
- Final release checklist + rollback notes

---

## 🛡 Guardrail Contract (V2.1)

Semua fase v8 tetap wajib:

- Headless-compatible logic
- No business logic in GUI
- Policy first (`safe_mode`, `execution_profile`, confirmation)
- Test coverage untuk fitur baru
- Documentation sync di `docs/finish/`

---

## ✅ Legacy Track — Application V1 (Archived)

### Status Ringkas

- Roadmap v1 → v7: **Completed**
- Product track v1.x: **Closed**

### Legacy Milestone Summary

- v1-v3: command foundation, persona, safety, intent/memory/observability
- v4-v5: tab shell architecture, command assist, capability layer, risk policy
- v6: storage migration, automation, hotkey UX, reliability hardening
- v7: command workspace revamp, multi-tab visual modernization, stabilization closure

### Legacy References

Detail implementasi legacy tersedia di:

- `docs/FINISHED.md`
- `docs/finish/` (per-phase completion docs)
- changelog dan commit history

---

## 🧭 Versioning Convention

- `Roadmap vX` → planning cycle
- `v1.X` / `v2.X` → product release line
- Phase numbering berlanjut lintas cycle untuk traceability

---

## 📍 Current Operating Mode

**Active development:** `Roadmap v9 / Application v2.2 (Planning)`

**Legacy maintenance only:** `Roadmap v1-v7 / Application v1.x`
