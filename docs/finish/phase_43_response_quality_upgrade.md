# PHASE 43 — Response Quality Upgrade

## Ringkasan

PHASE 43 menyelesaikan upgrade kualitas respons dengan kontrol model chat langsung dari tab Settings serta quality profile untuk menyesuaikan kedalaman jawaban.

## Scope yang Diselesaikan

- Pengaturan chat model di tab Settings:
  - `gemma3:4b`
  - `llama3.2:3b`
  - `mistral:7b`
- Model list otomatis di-load dari Ollama `/api/tags` saat aplikasi startup.
- Tombol `Refresh` di dekat selector model untuk reload catalog model on-demand.
- Badge model berbasis metadata `parameter_size`:
  - `1B–8B` → `Aman`
  - `<=13B` → `Borderline`
  - `<30B` → `High`
  - `>=30B` → `Jangan dipaksa`
  - Model embedding (`embed`) → `Lowest/Embed`
- Runtime tuning controls di Settings:
  - `token_budget`
  - `generation_timeout`
  - `temperature`
- Chat model toggle di Settings:
  - checkbox `Enable chat model (LLM responses)`
  - default test-mode (`pytest`) = nonaktif untuk mempercepat dan menstabilkan pengujian
- Quality profile di Settings:
  - `concise`
  - `balanced`
  - `deep`
- Router controls:
  - `set_generation_runtime(...)`
  - `set_response_quality(...)`
- Prompt composition menyesuaikan quality profile untuk meningkatkan konsistensi output reasoning.
- Badge + metadata membantu memilih model yang lebih aman untuk resource GPU pengguna.
- Layout Settings dipadatkan dengan container max-width terpusat, label alignment lebih rapat, refresh button kecil, dan badge chip di samping model.
- `model_selector` kini menampilkan badge di dalam item list (`[Badge • Size]`) dan tombol refresh memakai ikon SVG modern.

## Perubahan Teknis

- `ui/pages/settings_page.py`
- `ui/main_window.py`
- `core/router.py`
- `core/generation_provider.py`
- `tests/test_tab_shell.py`
- `tests/test_router.py`

## Validasi

- `pytest -q tests/test_router.py tests/test_tab_shell.py`

## Dampak

- Pengguna dapat tuning model dan kualitas respons tanpa mengubah kode.
- OrionDesk v2.2 memiliki jalur quality control yang lebih fleksibel untuk skenario lokal.
