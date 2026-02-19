# V2.1 Manual Command Checklist

Checklist ini untuk pengujian manual fitur v2.1 (phase 36-40) langsung dari UI command input.

## A. Basic Health

- `sys info`
- `open notepad`
- `search file report`

Ekspektasi:

- Command dieksekusi normal.
- Output muncul sebagai bubble chat.

## B. Embedding Foundation (PHASE 36)

- Buka tab `Diagnostics`.
- Pastikan ada informasi `Embedding: ...`.

Ekspektasi:

- Jika Ollama aktif + model tersedia: status ready.
- Jika tidak aktif: fallback message tetap informatif.

## C. Multi-step Intent Graph (PHASE 37)

Gunakan skenario natural input:

- `tolong buka notepad lalu cek sys info` ⚠️ (Belum berfungsi untuk 2 task)
- `open notepad kemudian search file notes`

Ekspektasi:

- Urutan intent dapat dipetakan menjadi step berantai.
- Tidak crash pada input multi-step.

## D. Complex Reasoning (PHASE 38)

Uji input ambigu:

- `tolong cek sesuatu lalu mungkin hapus file temp` ⚠️ (Kena whitelist policy tanpa pemberitahuan)

Ekspektasi:

- Step low-confidence diarahkan ke fallback/explain.
- Step high-risk dengan confidence rendah dipruning/guarded.

## E. Argument Extraction + Multi-command (PHASE 39)

Uji perintah gabungan:

- `open vscode lalu sys info`
- `search file report lalu mode focus on`

Ekspektasi:

- Setiap command punya argument breakdown yang benar.
- Report eksekusi per command memiliki status dan durasi.

## F. Safety Guard

- `delete C:/temp/demo.txt`
- `kill 1234`

Ekspektasi:

- Safe mode confirmation muncul saat mode aman aktif.
- Tidak ada eksekusi destructive tanpa guard.

## G. Theme + UI Stability

- Switch `dark` ↔ `light` di Settings.
- Coba beberapa command setelah switch.

Ekspektasi:

- Kontras teks tetap terbaca.
- Bubble/controls/list tetap sinkron tema.

## H. Smoke Multi-command (2+)

- `open notepad lalu sys info`
- `mode focus on lalu sys info lalu search file todo`

Ekspektasi:

- Semua step diproses berurutan.
- Tidak freeze UI.

## Catatan Bug Manual

Saat menemukan bug, catat minimal:

- Input command
- Hasil aktual
- Hasil yang diharapkan
- Mode tema (`dark`/`light`)
- Screenshot jika perlu
