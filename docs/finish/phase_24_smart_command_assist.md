# PHASE 24 — Smart Command Assist (Auto-correct, Auto-complete, Explain)

## Ringkasan

PHASE 24 menambahkan smart assistance di level engine dan UI: typo correction berbasis confidence, argumen suggestion berbasis context command, dan explain mode sebelum eksekusi.

## Scope yang Diselesaikan

- Auto-correct command typo menggunakan similarity score.
- Candidate ranking memakai Levenshtein distance + command registry introspection.
- Confirmation flow untuk correction yang confidence-nya belum cukup tinggi.
- Auto-complete argument hints per command context.
- Explain mode via command prefix `explain <command>`.

## Perubahan Teknis

- `core/smart_assist.py`
  - `SmartAssistEngine`
  - `AutoCorrection`
  - Levenshtein similarity scorer
- `core/router.py`
  - Integrasi smart assist ke jalur `execute`.
  - Pending autocorrect confirmation flow (`confirm_pending`).
  - API `argument_hint` dan explain-mode handling.
- `ui/main_window.py`
  - Command assist menampilkan `Args:` hint jika tersedia.
- `tests/test_smart_assist.py`
  - Unit test autocorrect, explain mode, dan confirmation execution.
- `tests/test_tab_shell.py`
  - Test UI argument hints pada command assist.

## Dampak

- Input command typo jadi lebih toleran tanpa kehilangan kontrol.
- Discoverability argumen command meningkat di UI.
- User bisa audit intent command lewat explain mode sebelum dieksekusi.

## Validasi

- Unit test phase 24 lulus.
- Regression suite tetap lulus.
