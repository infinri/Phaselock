# Phaselock -- Directory Index

## Purpose

Complete directory index for the Phaselock knowledge base. Describes what each directory contains so AI and humans can quickly locate relevant guidance.

**Key files:**
- `SKILL.md` -- Skill entry point and task-to-document navigation (start here)
- `OVERVIEW.md` -- This file (directory index)
- `CONTRIBUTING.md` -- How to add rules to this knowledge base
- `README.md` -- Human-readable project overview
- `MANIFEST.md` -- Multi-domain task mapping

---

## Top-Level Directories

### `bible/`
**Institutional knowledge and enforceable rules**

Contains domain-specific technical guidance organized by decision area. See detailed breakdown below.

---

### `enforcement/`
**AI behavior and code generation standards**

Contains:
- Task complexity routing (tier classification)
- Pre-implementation reasoning gates
- Phased code generation protocol
- Post-generation verification (findings tables, static analysis, proof traces)
- Context retrieval discipline
- System dynamics enforcement (concurrency, state machines)
- Security boundary enforcement
- Operational claims enforcement

Current files:
- `ai-checklist.md` -- Code generation standards, pre-implementation checklist
- `reasoning-discipline.md` -- Tier routing (`ENF-ROUTE-001`), mandatory pre-implementation reasoning (`ENF-PRE-001`-`004`), phased gate protocol (`ENF-GATE-001`-`007`, `ENF-GATE-FINAL`), post-generation verification (`ENF-POST-001`-`008`), context discipline (`ENF-CTX-001`-`004`)
- `system-dynamics.md` -- Concurrency simulation, temporal truth sources, state transition atomicity, policy vs mechanism, integration reality check, dead state detection (`ENF-SYS-001`-`006`)
- `security-boundaries.md` -- Access boundary declarations, data exposure minimization (`ENF-SEC-001`-`002`)
- `operational-claims.md` -- Operational claim validation, queue configuration completeness (`ENF-OPS-001`-`002`)

---

### `rules/`
**Global coding principles**

Contains:
- Universal best practices (DRY, SOLID, KISS, Composition)
- Principles that apply across all code
- Not enforceable rules -- judgment guidelines

Current files:
- `CORE_PRINCIPLES.md` -- DRY, SOLID, KISS, Composition Over Inheritance

---

## Bible Subdirectories

### `bible/architecture/`
**System-wide structure and design decisions**

Current files:
- `principles.md` -- ARCH-ORG-001, ARCH-EXT-001, ARCH-DI-001, ARCH-CONST-001, ARCH-SSOT-001

---

### `bible/database/`
**SQL, data access, and query authoring**

Current files:
- `sql-authoring.md` -- DB-SQL-001, DB-SQL-002, DB-SQL-003

---

### `bible/languages/`
**Language-specific coding standards**

Subdirectories:
- `php/` -- PHP coding standards, error handling

Current files:
- `php/coding-standards.md` -- PHP-TYPE-001, PHP-TRY-001
- `php/error-handling.md` -- PHP-ERR-001, PHP-ERR-002

---

### `bible/performance/`
**Scalability, efficiency, and optimization**

Current files:
- `profiling.md` -- PERF-BIGO-001, PERF-OPT-001, PERF-LAZY-001, PERF-QBUDGET-001

---

### `bible/testing/`
**Verification, confidence, and regression prevention**

Current files:
- `unit-testing.md` -- TEST-TDD-001, TEST-ISO-001, TEST-INT-001

---

### `bible/frameworks/magento/`
**Magento 2-specific implementation constraints**

Current files:
- `implementation-constraints.md` -- FW-M2-001, FW-M2-002, FW-M2-003, FW-M2-004, FW-M2-005, FW-M2-006
- `runtime-constraints.md` -- FW-M2-RT-001, FW-M2-RT-002, FW-M2-RT-003, FW-M2-RT-004, FW-M2-RT-005, FW-M2-RT-006

---

### `bible/security/`
**Data protection and system integrity**

Current files:
- `boundaries.md` -- SEC-UNI-001, SEC-UNI-002, SEC-UNI-003, SEC-UNI-004

---

### `bible/playbooks/`
**Step-by-step build workflows**

Playbooks reference rules but do not define them. They provide end-to-end build sequences for common task types.

Current files:
- `api-endpoint.md` -- End-to-end checklist for building API endpoints
- `queue-feature.md` -- End-to-end checklist for building queue-based features

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
| `bible/playbooks/` | Workflows | (no rules -- references only) |
| `enforcement/` | AI Behavior | `ENF-ROUTE-`, `ENF-PRE-`, `ENF-GATE-`, `ENF-POST-`, `ENF-CTX-` |
| `enforcement/` | System Dynamics | `ENF-SYS-` |
| `enforcement/` | Security | `ENF-SEC-` |
| `enforcement/` | Operations | `ENF-OPS-` |
| `rules/` | Global Principles | (no rule IDs -- judgment guidelines) |
