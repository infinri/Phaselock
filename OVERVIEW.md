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

Current files:
- `principles.md` — ARCH-ORG-001, ARCH-EXT-001, ARCH-DI-001

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
- `profiling.md` — PERF-BIGO-001, PERF-OPT-001, PERF-LAZY-001

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

### Empty directories (awaiting rules)

- `bible/frameworks/` — Framework-specific rules (`FW-` prefix)
- `bible/security/` — Data protection and system integrity (`SEC-` prefix)
- `bible/playbooks/` — Step-by-step workflows (`PLAY-` prefix)

---

## Quick Reference

| Directory | Domain | Rule Prefix |
|-----------|--------|-------------|
| `bible/architecture/` | System design | `ARCH-` |
| `bible/database/` | SQL / Data | `DB-` |
| `bible/frameworks/` | Frameworks | `FW-` |
| `bible/languages/php/` | PHP | `PHP-` |
| `bible/performance/` | Performance | `PERF-` |
| `bible/security/` | Security | `SEC-` |
| `bible/testing/` | Testing | `TEST-` |
| `bible/playbooks/` | Workflows | `PLAY-` |
| `enforcement/` | AI Behavior | — |
| `prompts/` | Templates | — |
| `rules/` | Global Principles | — |
