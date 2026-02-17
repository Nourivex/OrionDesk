# Roadmap v6 Planning (v1.6)

## Theme

Performance, Automation, and Utility.

## Strategic Goals

- Replace file-centric storage bottlenecks with SQLite-backed persistence.
- Upgrade OrionDesk from command runner to automation hub.
- Expand utility modules for developer and power-user workflows.
- Improve launch speed and command accessibility via global hotkey UX.
- Close with profiling-driven release hardening.

## Planned Phases

- PHASE 27 — Storage Engine Migration (JSON to SQLite)
- PHASE 28 — Trigger-Action Automation Engine (Watcher + Scheduler)
- PHASE 29 — Utility & Developer Modules Expansion
- PHASE 30 — Global Hotkey UX + Fast Command Surface
- PHASE 31 — Reliability, Profiling, and Release Hardening

## Key Technical Decision

SQLite is selected as the primary storage engine for v6 due to:

- Incremental-write performance
- Concurrency safety for UI + background workers
- Strong query capability for history and diagnostics

## Success Criteria

- Storage migration completes with backward-compatible adapters.
- Automation engine runs trigger-action rules safely.
- Utility modules deliver measurable workflow speed gains.
- Hotkey UX is stable and conflict-aware.
- Profiling baseline and release checklist pass for v1.6 readiness.
