# ADR-0001: Adopt SQLite as Primary Storage Engine

- Status: Accepted
- Date: 2026-02-17
- Decision Makers: OrionDesk Core Team

## Context

OrionDesk currently stores multiple runtime artifacts in file-based formats. As command history and automation events grow, file-level writes become expensive and harder to coordinate safely under concurrent access.

## Decision

Adopt SQLite as the primary production storage engine for OrionDesk v6.

## Rationale

- Better write performance for incremental updates
- Transactional safety (ACID)
- Safe concurrent access for UI and background workers
- First-class query support for diagnostics and history analysis

## Consequences

### Positive

- Lower latency for frequent write paths
- Better reliability under automation workloads
- Easier analytics and filtering for history/memory features

### Trade-offs

- Requires schema design and migration discipline
- Adds database lifecycle management to release process

## Implementation Notes

- Recommended ORM/query layer: SQLModel
- Introduce migration scripts and schema version table
- Keep compatibility adapter during phased migration
