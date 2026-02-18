# PHASE 32 — Command Workspace Refresh (Persona Rail + Chat Command Surface)

## Ringkasan

Dokumen ini mencatat pembaruan perencanaan ROADMAP v7 untuk PHASE 32 agar fokus pada redesign halaman `Command` mengikuti wireframe Pro Ops Console.

## Scope yang Ditetapkan

- Reframe PHASE 32 dari audit UI umum menjadi refresh command workspace yang konkret.
- Menetapkan struktur layout dua area:
  - Sidebar kiri: `Persona`, `Quick Actions`, `Stats`
  - Area kanan: `Chat Container`, `Input Area`, `Suggestion Chips`
- Menetapkan daftar persona target: `calm`, `professional`, `hacker`, `friendly`, `minimal`.
- Menetapkan quick action utama: `open vscode`, `open notepad`, `mode focus on`, `system status`, `clear chat`.
- Menegaskan batas arsitektur: business logic tetap headless di `core/`, UI hanya orchestration/presentation.

## Perubahan Dokumen

- `docs/ROADMAP.md`
  - Label PHASE 32 di roadmap summary diperbarui.
  - Label PHASE 32 di status fase diperbarui.
  - Ditambahkan blok `Spesifikasi v7 (PHASE 32-35)` dengan detail PHASE 32.

## Validasi

- Konsistensi istilah PHASE 32 sudah sinkron pada bagian ringkasan roadmap dan status fase.
- Scope PHASE 32 kini memiliki acceptance target UI yang jelas sebelum implementasi.

## Dampak

- Planning v1.7 menjadi lebih presisi untuk eksekusi desain/engineering pada iterasi berikutnya.
- Risiko ambigu pada “UX debt audit” berkurang karena output visual target sudah didefinisikan.
