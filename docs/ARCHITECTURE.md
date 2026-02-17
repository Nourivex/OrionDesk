<div align="center">

# 🏗 OrionDesk Technical Architecture

System design reference for core contributors, plugin developers, and platform evolution.

</div>

---

## 1. System Overview

OrionDesk is a local-first Windows OS intelligence layer designed for safe command orchestration, structured automation, and modular capability expansion.

The architecture enforces strict separation between presentation, orchestration, policy evaluation, and system capability execution.

---

## 2. Architectural Principles

- **Headless-first logic** — Business logic must remain GUI-independent.
- **Thin presentation layer** — UI is a rendering surface, not an execution engine.
- **Policy-before-execution** — Guardrails and risk evaluation precede all high-risk actions.
- **Deterministic over opaque inference** — Predictability is preferred over probabilistic behavior.
- **Composable extensibility** — Capabilities and plugins must be incrementally attachable.

---

## 3. Layered Architecture

### 3.1 Core Layer (`core/`)

Responsible for orchestration and policy governance.

Includes:

- Command router and unified executor
- Execution context & profile policies
- Guardrail and security enforcement
- Intent mapping & smart assist
- Observability, diagnostics, recovery
- Workflow orchestration engine (Roadmap v6)

This layer must remain UI-agnostic and testable headlessly.

---

### 3.2 Capability Layer (`modules/`)

Provides deterministic system primitives.

Includes:

- Application launchers
- File operations
- Process utilities
- Network utilities
- Domain-specific actions

Capability modules must not contain UI logic.

---

### 3.3 UI Layer (`ui/`)

Presentation shell built with PySide6.

Includes:

- Tab-based navigation (`Command`, `Memory`, `Settings`, `Diagnostics`, `About`)
- Persona-aware response rendering
- Async-safe command handling
- Theming and accessibility controls

The UI subscribes to execution results via signals and state updates.

---

### 3.4 Data Layer

Current:
- JSON artifacts and mixed local storage

Roadmap v6 direction:
- SQLite as primary storage engine
- Structured session persistence
- Concurrency-safe execution logging

---

## 4. Command Execution Lifecycle

1. UI captures command input.
2. Router resolves intent and applies smart-assist corrections (if enabled).
3. Risk engine evaluates execution profile and guardrails.
4. Unified executor dispatches capability handler.
5. Result envelope is generated and persisted.
6. UI renders structured response.

All execution must pass through policy validation before capability dispatch.

---

## 5. Safety & Risk Model

- Command whitelist enforcement
- Path and process restriction policies
- Execution profiles:
  - `strict`
  - `balanced`
  - `power`
  - `explain-only`
- Manual confirmation gates for high-risk actions

Safety enforcement is centralized in the Core Layer.

---

## 6. Extensibility Model

- Plugins are auto-discovered from the `plugins/` package.
- Commands are registered via explicit command contracts.
- Capability primitives are reusable by automation workflows.
- Plugin boundaries must respect policy enforcement contracts.

---

## 7. Evolution Direction

OrionDesk is evolving toward:

> A deterministic, policy-aware OS intelligence layer for Windows.

Future directions include:

- Persistent execution memory
- Automation planning engine
- Structured state registry
- Performance-optimized storage backend

---

## 8. Related Documentation

- Product Roadmap → `docs/ROADMAP.md`
- Architecture Decision Records → `docs/architecture/`
- Plugin Developer Guide → `docs/api/PLUGIN_DEVELOPER_GUIDE.md`
- User Manual → `docs/manual/USER_GUIDE.md`
