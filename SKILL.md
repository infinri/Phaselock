---
name: ai-workflow
description: >
  Provides institutional coding knowledge ("Coding Bible") covering architectural
  decisions, coding standards, framework-specific rules, security expectations,
  performance guidelines, and approved patterns for AI-assisted development.
  Guides code generation, refactoring, architecture decisions, database query
  authoring, error handling, testing, and performance optimization. Activates on
  tasks involving code review, design decisions, SQL queries, PHP development,
  security review, or when project conventions and domain-specific rules must be
  consulted before proposing solutions.
metadata:
  author: lucio-saldivar
  version: "1.0"
---

# AI Workflow — Coding Bible

## Workflow

1. **Identify the task domain** from the navigation table below
2. **Read only the relevant documents** — do not load the entire knowledge base
3. **State which documents were consulted** before proposing any solution
4. **If the task involves plugins, observers, validation, or entity retrieval**: follow the **Phased Implementation Protocol** (`ENF-GATE-001`–`004` in [enforcement/reasoning-discipline.md](enforcement/reasoning-discipline.md)):
   - **Phase A** → Call-path declaration ONLY → halt for review
   - **Phase B** → Domain invariant declaration ONLY → halt for review
   - **Phase C** → Seam justification ONLY → halt for review
   - **Only after all phases approved** → proceed to code
5. **If guidance is missing or ambiguous**: state it explicitly, ask for clarification, propose a conservative default. Silent guessing is never allowed.

## Task → document navigation

Read the documents listed for each matching task type. Start with [rules/CORE_PRINCIPLES.md](rules/CORE_PRINCIPLES.md) for any code task.

### Architecture & design decisions

When introducing modules, changing system boundaries, or modifying core flows:

- [bible/architecture/principles.md](bible/architecture/principles.md) — Code organization, extension points, dependency injection, named constants (`ARCH-ORG-001`, `ARCH-EXT-001`, `ARCH-DI-001`, `ARCH-CONST-001`)

### Database / SQL

When writing queries, diagnosing query performance, or handling transactions:

- [bible/database/sql-authoring.md](bible/database/sql-authoring.md) — Named binds, minimal string fragmentation, readable formatting (`DB-SQL-001`, `DB-SQL-002`, `DB-SQL-003`)

### PHP development

When writing PHP code, handling errors, or enforcing type safety:

- [bible/languages/php/coding-standards.md](bible/languages/php/coding-standards.md) — DocBlock types, try-catch standards (`PHP-TYPE-001`, `PHP-ERR-002`)
- [bible/languages/php/error-handling.md](bible/languages/php/error-handling.md) — Fail fast, graceful degradation (`PHP-ERR-001`, `PHP-ERR-002`)

### Performance & optimization

When optimizing slow paths, addressing resource issues, or introducing caching:

- [bible/performance/profiling.md](bible/performance/profiling.md) — Algorithm complexity, optimization order, lazy loading (`PERF-BIGO-001`, `PERF-OPT-001`, `PERF-LAZY-001`)

### Frameworks / Magento 2

When writing plugins, observers, validation, or entity retrieval in Magento 2:

- [bible/frameworks/magento/implementation-constraints.md](bible/frameworks/magento/implementation-constraints.md) — Persistence-backed validation, repository-only retrieval, quote state timing, plugin targeting (`FW-M2-001`, `FW-M2-002`, `FW-M2-003`, `FW-M2-004`)

### Testing

When adding tests, refactoring with risk, or addressing regressions:

- [bible/testing/unit-testing.md](bible/testing/unit-testing.md) — TDD, test isolation, integration testing (`TEST-TDD-001`, `TEST-ISO-001`, `TEST-INT-001`)

### AI behavior & code generation

When reviewing AI-generated code or understanding assistant behavior expectations:

- [enforcement/ai-checklist.md](enforcement/ai-checklist.md) — Pre-implementation checklist, minimal code generation rules
- [enforcement/reasoning-discipline.md](enforcement/reasoning-discipline.md) — Mandatory pre-implementation reasoning, post-generation verification, context retrieval discipline (`ENF-PRE-001`–`004`, `ENF-POST-001`–`005`, `ENF-CTX-001`–`003`)
- [prompts/cascade-best-practices.md](prompts/cascade-best-practices.md) — Prompt engineering guidelines

## Rule format

All enforceable rules use formal blocks with unique IDs wrapped in `<!-- RULE START/END -->` markers. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full rule format specification.

## Additional references

- [README.md](README.md) — Human-readable project overview
- [MANIFEST.md](MANIFEST.md) — Extended task-to-document mapping
- [OVERVIEW.md](OVERVIEW.md) — Complete directory index with descriptions

## Authority model

This skill provides reference and reasoning material only. It does not grant file access, override global rules, or authorize actions. All rules originate from explicit human intent — the agent may format but never invent rules.
