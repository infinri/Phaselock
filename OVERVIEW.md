# AI Workflow — Directory Index

## Purpose

This document is the **complete directory index** for the AI Workflow knowledge base.

It describes what each directory contains so AI and humans can quickly locate relevant guidance.

**Key files:**
- `SKILL.md` — Skill entry point and task→document navigation (start here)
- `OVERVIEW.md` — This file (directory index)
- `CONTRIBUTING.md` — How to add rules to this knowledge base
- `README.md` — Human-readable project overview
- `MANIFEST.md` — Extended task-to-document mapping

---

## Top-Level Directories

### `bible/`
**Institutional knowledge and enforceable rules**

Contains domain-specific technical guidance organized by decision area. See detailed breakdown below.

---

### `enforcement/`
**AI behavior and code generation standards**

Contains:
- Pre-implementation checklists
- Code modification approach
- Minimal code generation rules

Current files:
- `ai-checklist.md` — Code generation standards, pre-implementation checklist
- `reasoning-discipline.md` — Mandatory pre-implementation reasoning, phased gate protocol (incl. phased code generation and test-first gate), post-generation verification (incl. structured findings table, static analysis gate, operational proof traces), context retrieval discipline (`ENF-PRE-001`–`004`, `ENF-GATE-001`–`007`, `ENF-POST-001`–`008`, `ENF-CTX-001`–`003`)
- `system-dynamics.md` — Concurrency simulation, temporal truth sources, state transition atomicity, policy vs mechanism separation, integration reality check (`ENF-SYS-001`–`005`), Phase D protocol
- `security-boundaries.md` — Access boundary declarations, data exposure minimization (`ENF-SEC-001`–`002`)
- `operational-claims.md` — Operational claim validation, queue configuration completeness (`ENF-OPS-001`–`002`)

---

### `prompts/`
**Templates and best practices for AI interaction**

Contains:
- Prompt engineering guidelines
- Request templates

Current files:
- `cascade-best-practices.md` — How to write effective prompts

---

### `rules/`
**Global coding principles**

Contains:
- Universal best practices (DRY, SOLID, KISS, Composition)
- Principles that apply across all code

Current files:
- `CORE_PRINCIPLES.md` — DRY, SOLID, KISS, Composition Over Inheritance

---

## Bible Subdirectories

### `bible/architecture/`
**System-wide structure and design decisions**

Contains:
- Core architectural principles
- Code organization rules
- Extension patterns
- Dependency management
- Named constants for business rules

Current files:
- `principles.md` — ARCH-ORG-001, ARCH-EXT-001, ARCH-DI-001, ARCH-CONST-001, ARCH-SSOT-001

---

### `bible/database/`
**SQL, data access, and query authoring**

Contains:
- SQL authoring standards
- Bind parameter rules
- Query formatting guidelines

Current files:
- `sql-authoring.md` — DB-SQL-001, DB-SQL-002, DB-SQL-003

---

### `bible/languages/`
**Language-specific coding standards**

Subdirectories:
- `php/` — PHP coding standards, error handling

Current files:
- `php/coding-standards.md` — PHP-TYPE-001, PHP-ERR-002
- `php/error-handling.md` — PHP-ERR-001, PHP-ERR-002

---

### `bible/performance/`
**Scalability, efficiency, and optimization**

Contains:
- Algorithm complexity rules
- Optimization order
- Lazy loading guidelines

Current files:
- `profiling.md` — PERF-BIGO-001, PERF-OPT-001, PERF-LAZY-001, PERF-QBUDGET-001

---

### `bible/testing/`
**Verification, confidence, and regression prevention**

Contains:
- Unit testing standards
- Integration testing guidelines
- Test isolation rules

Current files:
- `unit-testing.md` — TEST-TDD-001, TEST-ISO-001, TEST-INT-001

---

### `bible/frameworks/magento/`
**Magento 2-specific implementation constraints**

Contains:
- Persistence-backed validation requirements
- Repository-only entity retrieval
- Quote state execution timing
- Plugin targeting rules

Current files:
- `magento/implementation-constraints.md` — FW-M2-001, FW-M2-002, FW-M2-003, FW-M2-004, FW-M2-005, FW-M2-006
- `magento/runtime-constraints.md` — FW-M2-RT-001, FW-M2-RT-002, FW-M2-RT-003, FW-M2-RT-004, FW-M2-RT-005, FW-M2-RT-006

---

### Empty directories (awaiting rules)

- `bible/security/` — Data protection and system integrity (`SEC-` prefix)
- `bible/playbooks/` — Step-by-step workflows (`PLAY-` prefix)

---

## Quick Reference

| Directory | Domain | Rule Prefix |
|-----------|--------|-------------|
| `bible/architecture/` | System design | `ARCH-` |
| `bible/database/` | SQL / Data | `DB-` |
| `bible/frameworks/magento/` | Magento 2 | `FW-M2-`, `FW-M2-RT-` |
| `bible/languages/php/` | PHP | `PHP-` |
| `bible/performance/` | Performance | `PERF-` |
| `bible/security/` | Security | `SEC-` |
| `bible/testing/` | Testing | `TEST-` |
| `bible/playbooks/` | Workflows | `PLAY-` |
| `enforcement/` | AI Behavior | `ENF-` |
| `enforcement/` | System Dynamics | `ENF-SYS-` |
| `enforcement/` | Security | `ENF-SEC-` |
| `enforcement/` | Operations | `ENF-OPS-` |
| `prompts/` | Templates | — |
| `rules/` | Global Principles | — |
