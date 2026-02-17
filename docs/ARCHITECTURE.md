<div align="center">
	<h1>OrionDesk Technical Architecture</h1>
	<p>System design reference for core contributors and plugin developers.</p>
</div>

## System Overview

OrionDesk is a local-first Windows automation and utility agent with strict layering between presentation, command orchestration, and system capabilities.

## Architectural Principles

- Keep business logic headless-compatible.
- Keep GUI as a thin presentation layer.
- Apply policy and guardrails before high-risk actions.
- Prefer deterministic behavior over opaque inference.
- Build for incremental extensibility through plugins and capability layers.

## High-Level Components

### Core Layer (`core/`)

- Command router and unified executor
- Execution context and profile policies
- Safety and security policies
- Intent mapping and smart assist
- Observability, diagnostics, and recovery
- Automation and workflow orchestration (roadmap v6)

### Module Layer (`modules/`)

- App launcher and file utilities
- System tools and system actions
- Domain-specific capability primitives

### UI Layer (`ui/`)

- Tab-based shell (`Command`, `Memory`, `Settings`, `Diagnostics`, `About`)
- Theme-aware controls and feedback surfaces
- Async-safe command interactions for long-running actions

### Data Layer

- Current: mixed local storage and JSON-based artifacts
- Roadmap v6 direction: SQLite as primary storage engine for performance and concurrency safety

## Command Request Lifecycle

1. UI captures command input.
2. Router resolves intent and optional smart-assist correction.
3. Policy engines evaluate risk profile and guardrails.
4. Unified executor dispatches command handler.
5. Result envelope is persisted to session and logs.
6. UI renders persona-formatted response.

## Safety Model

- Command whitelist enforcement
- Path and process restrictions
- Profile-based risk policy (`strict`, `balanced`, `power`, `explain-only`)
- Manual confirmation for high-risk actions

## Extensibility Model

- Plugin command definitions are discovered from the `plugins/` package.
- New command handlers are registered through command contracts.
- Capability primitives are reusable from smart/automation plans.

## Related Documentation

- Product roadmap: `docs/ROADMAP.md`
- ADR records: `docs/architecture/`
- Plugin API guide: `docs/api/PLUGIN_DEVELOPER_GUIDE.md`
- User manual: `docs/manual/USER_GUIDE.md`
