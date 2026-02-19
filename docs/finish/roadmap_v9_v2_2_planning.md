# Roadmap v9 / Application v2.2 Planning

## Ringkasan
Roadmap aktif dipindahkan dari v8/v2.1 ke v9/v2.2 (planning track) dengan fokus:

- Integrasi model lokal `gemma3:4b` untuk peningkatan kualitas respons.
- Runtime ringan dan responsif (low-latency, minim lag).
- Optimalisasi reasoning, memory, dan stabilitas release gate v2.2.

Dokumen ini juga mencatat guard performa awal di chat surface untuk menjaga UX tetap halus pada sesi panjang.

## Perubahan Implementasi

### 1) Planning v9 di Roadmap
`docs/ROADMAP.md` diperbarui dengan section:

- PHASE 41 — Gemma Runtime Adapter
- PHASE 42 — Latency Budget & Non-blocking Runtime
- PHASE 43 — Response Quality Upgrade
- PHASE 44 — Memory + Retrieval Optimization
- PHASE 45 — Stabilization + Release Gate v2.2

Dan status operasi aktif diubah menjadi:

- `Roadmap v9 / Application v2.2 (Planning)`

### 2) Runtime Smoothness Guard (UI)
`ui/chat_surface.py` menambahkan mekanisme pruning message buffer:

- Menetapkan batas histori chat (`_max_messages = 200`).
- Menghapus bubble tertua saat jumlah message melewati ambang.
- Menekan pertumbuhan widget berlebih agar scroll/chat tetap responsif.

## Validasi

- `pytest -q tests/test_tab_shell.py`
- Hasil: **16 passed**
- Test baru: `test_chat_surface_prunes_old_messages_for_performance`

## Dampak

- Roadmap kini sinkron dengan arah v2.2.
- UX command chat lebih stabil untuk sesi panjang.
- Baseline awal untuk target “soft ringan gak ada lag” sudah diterapkan.
