---
name: phaselock
description: >
  Provides institutional coding knowledge ("Coding Bible") covering architectural
  decisions, coding standards, framework-specific rules, security expectations,
  performance guidelines, and approved patterns for AI-assisted development.
  Guides code generation, refactoring, architecture decisions, database query
  authoring, error handling, testing, and performance optimization. Activates on
  ALL software engineering tasks: code generation, code review, design decisions,
  research, auditing, debugging, SQL queries, PHP development, security review,
  explaining existing code, or when project conventions and domain-specific rules
  must be consulted before proposing solutions. The Bible is always consulted --
  task complexity only determines the level of ceremony (gates, phases, slices),
  not whether the skill activates.
metadata:
  author: lucio-saldivar
  version: "1.0"
---

# Phaselock -- Coding Bible

## Workflow

1. **Identify the task domain** from the navigation table below
2. **Read only the relevant documents** -- do not load the entire knowledge base. The Bible is always consulted, regardless of task complexity.
3. **Classify the task** per `ENF-ROUTE-001` ([enforcement/reasoning-discipline.md](enforcement/reasoning-discipline.md)). State the tier and reason before proceeding.
4. **State which documents were consulted** before proposing any solution
5. **Follow the protocol for the declared tier**:

   **Tier 0 -- Research**: Read relevant Bible docs. Deliver findings. No code generation unless explicitly requested.

   **Tier 1 -- Patch**: Read relevant Bible docs + CORE_PRINCIPLES.md. Write code. Run static analysis (`ENF-POST-007`). Done.

   **Tier 2 -- Standard**: Read relevant Bible docs + CORE_PRINCIPLES.md. Present Phases A-C as a single combined analysis → one human approval. Generate test skeletons (`ENF-GATE-007`) → human approval. Implement in a single slice. Run static analysis.

   **Tier 3 -- Complex**: Full Phased Implementation Protocol (`ENF-GATE-001`–`007`):
   - **Phase A** → Call-path declaration ONLY → halt for review
   - **Phase B** → Domain invariant declaration ONLY → halt for review
   - **Phase C** → Seam justification ONLY → halt for review
   - **Phase D** → Failure & concurrency modeling ONLY (when triggered) → halt for review
   - **Test Skeletons** → Generate test skeletons with assertions BEFORE implementation → halt for review (`ENF-GATE-007`)
   - **Sliced Code Generation** → Generate implementation in dependency-ordered slices, each with self-validation and human gate (`ENF-GATE-006`)
   - **Post-generation verification**: structured findings table (`ENF-POST-006`), static analysis (`ENF-POST-007`), and operational proof traces (`ENF-POST-008`) per slice
   - **ENF-GATE-FINAL** after all slices

6. **If the task involves concurrency, async processing, state transitions, or multi-actor writes**: Phase D is mandatory -- this forces Tier 3. See trigger conditions in [enforcement/system-dynamics.md](enforcement/system-dynamics.md).
7. **Escalation**: If the task grows beyond the declared tier during implementation, escalate (never downgrade). See `ENF-ROUTE-001`.
8. **If guidance is missing or ambiguous**: state it explicitly, ask for clarification, propose a conservative default. Silent guessing is never allowed.

## Task → document navigation

Read the documents listed for each matching task type. Start with [rules/CORE_PRINCIPLES.md](rules/CORE_PRINCIPLES.md) for any code task.

### Architecture & design decisions

When introducing modules, changing system boundaries, or modifying core flows:

- [bible/architecture/principles.md](bible/architecture/principles.md) -- Code organization, extension points, dependency injection, named constants, single source of truth for multi-channel data (`ARCH-ORG-001`, `ARCH-EXT-001`, `ARCH-DI-001`, `ARCH-CONST-001`, `ARCH-SSOT-001`)

### Database / SQL

When writing queries, diagnosing query performance, or handling transactions:

- [bible/database/sql-authoring.md](bible/database/sql-authoring.md) -- Named binds, minimal string fragmentation, readable formatting (`DB-SQL-001`, `DB-SQL-002`, `DB-SQL-003`)

### PHP development

When writing PHP code, handling errors, or enforcing type safety:

- [bible/languages/php/coding-standards.md](bible/languages/php/coding-standards.md) -- DocBlock types, try-catch standards (`PHP-TYPE-001`, `PHP-TRY-001`)
- [bible/languages/php/error-handling.md](bible/languages/php/error-handling.md) -- Fail fast, graceful degradation (`PHP-ERR-001`, `PHP-ERR-002`)

### Performance & optimization

When optimizing slow paths, addressing resource issues, or introducing caching:

- [bible/performance/profiling.md](bible/performance/profiling.md) -- Algorithm complexity, optimization order, lazy loading, query budget declaration (`PERF-BIGO-001`, `PERF-OPT-001`, `PERF-LAZY-001`, `PERF-QBUDGET-001`)

### Frameworks / Magento 2

When writing plugins, observers, validation, or entity retrieval in Magento 2:

- [bible/frameworks/magento/implementation-constraints.md](bible/frameworks/magento/implementation-constraints.md) -- Persistence-backed validation, repository-only retrieval, quote state timing, plugin targeting, totals collector idempotency, CartTotalRepository stale-read behavior (`FW-M2-001`, `FW-M2-002`, `FW-M2-003`, `FW-M2-004`, `FW-M2-005`, `FW-M2-006`)
- [bible/frameworks/magento/runtime-constraints.md](bible/frameworks/magento/runtime-constraints.md) -- MSI salability authority, order state machine, config patterns, endpoint authorization, queue infrastructure, multi-website stock (`FW-M2-RT-001`, `FW-M2-RT-002`, `FW-M2-RT-003`, `FW-M2-RT-004`, `FW-M2-RT-005`, `FW-M2-RT-006`)

### Testing

When adding tests, refactoring with risk, or addressing regressions:

- [bible/testing/unit-testing.md](bible/testing/unit-testing.md) -- TDD, test isolation, integration testing (`TEST-TDD-001`, `TEST-ISO-001`, `TEST-INT-001`)

### System dynamics & concurrency

When building features with concurrent actors, message queues, state machines, async processing, or multi-website behavior:

- [enforcement/system-dynamics.md](enforcement/system-dynamics.md) -- Concurrency simulation, temporal truth sources, state transition atomicity, policy vs mechanism separation, integration reality check (`ENF-SYS-001`, `ENF-SYS-002`, `ENF-SYS-003`, `ENF-SYS-004`, `ENF-SYS-005`)

### Security & access control

When exposing endpoints (REST, GraphQL, admin, storefront) or handling data access:

- [enforcement/security-boundaries.md](enforcement/security-boundaries.md) -- Access boundary declarations, data exposure minimization (`ENF-SEC-001`, `ENF-SEC-002`)

### Operational claims & queue infrastructure

When making performance/throughput claims or configuring message queues:

- [enforcement/operational-claims.md](enforcement/operational-claims.md) -- Operational claim validation, queue configuration completeness (`ENF-OPS-001`, `ENF-OPS-002`)

### AI behavior & code generation

When reviewing AI-generated code or understanding assistant behavior expectations:

- [enforcement/ai-checklist.md](enforcement/ai-checklist.md) -- Pre-implementation checklist, minimal code generation rules
- [enforcement/reasoning-discipline.md](enforcement/reasoning-discipline.md) -- Mandatory pre-implementation reasoning, phased code generation, test-first gate, post-generation verification (structured findings table, static analysis gate, operational proof traces), context retrieval discipline, Phase D hard gate, plan-to-code completeness verification (`ENF-PRE-001`–`004`, `ENF-GATE-001`–`007`, `ENF-GATE-FINAL`, `ENF-POST-001`–`008`, `ENF-CTX-001`–`003`)
- [enforcement/system-dynamics.md](enforcement/system-dynamics.md) -- System dynamics enforcement, Phase D protocol (`ENF-SYS-001`–`006`)
- [enforcement/security-boundaries.md](enforcement/security-boundaries.md) -- Security boundary enforcement (`ENF-SEC-001`–`002`)
- [enforcement/operational-claims.md](enforcement/operational-claims.md) -- Operational claim enforcement (`ENF-OPS-001`–`002`)


## Rule format

All enforceable rules use formal blocks with unique IDs wrapped in `<!-- RULE START/END -->` markers. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full rule format specification.

## Additional references

- [README.md](README.md) -- Human-readable project overview
- [MANIFEST.md](MANIFEST.md) -- Extended task-to-document mapping
- [OVERVIEW.md](OVERVIEW.md) -- Complete directory index with descriptions

## Authority model

This skill provides reference and reasoning material only. It does not grant file access, override global rules, or authorize actions. All rules originate from explicit human intent -- the agent may format but never invent rules.
