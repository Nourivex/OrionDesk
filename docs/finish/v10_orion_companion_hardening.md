# V10 Plan Revision — Orion Companion Hardening

## Ringkasan

Dokumen ini mencatat penguatan companion sesuai revisi Plan V10 dengan 3 tambahan wajib: `Fatigue Factor`, `Ghost Writing Indicator`, dan `Safety Drill Simulation`.

## Implementasi Wajib

### 1) Fatigue Factor (Action Pacing)

- `core/companion_policy.py`
  - `ActionPacingConfig(window_seconds, threshold_calm, threshold_hacker, threshold_command_tab)`
  - `FatigueState(auto_action_timestamps, fatigue_penalty, force_confirmation, threshold_used, count_in_window)`
  - `AutoActionDecision` memuat `fatigue_penalty`, `fatigue_reason`, `force_confirmation`
- `core/router.py`
  - `evaluate_auto_action(..., ui_context)` menggunakan profil/tab aktif untuk threshold adaptif
  - audit log `companion_auto_action` menyimpan alasan fatigue + forced confirmation

### 2) Ghost Writing Indicator (Dynamic Typing)

- `ui/chat_surface.py`
  - `show_typing_indicator(stage, expected_ms)`
  - `update_typing_stage(stage, elapsed_ms)`
  - `hide_typing_indicator(final_state)`
  - stage visual: `impact_assessment`, `generation`, `final_validation`
- `core/router.py` + `ui/window_helpers.py`
  - telemetry stage reasoning dikirim ke UI worker (`stageTelemetry`) untuk sinkron typing non-blocking
  - fallback telemetry tetap tersedia untuk kompatibilitas

### 3) Safety Drill Simulation

- `core/release_hardening.py`
  - checklist key `safety_drill`
  - `run_simulation_mode(...)` untuk dummy workflow/journal replay
  - status drill: `Simulation Success` / `Rollback Conflict`
- `core/router.py`
  - `run_safety_drill(...)` untuk diagnostics/release flow

## Validasi Utama

- `tests/test_companion_policy.py`
- `tests/test_chat_surface_typing_sync.py`
- `tests/test_release_hardening_simulation.py`
- `tests/test_router.py`
- `tests/test_latency_budget.py`
- `tests/test_performance_profiler.py`

Semua tetap local-first, policy-first, dan headless-compatible.
