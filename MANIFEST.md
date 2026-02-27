# AI Workflow — MANIFEST

Extended task-to-document mapping. For primary navigation, see [SKILL.md](SKILL.md).

## Multi-domain tasks

When a task spans multiple domains, consult all applicable documents. Examples:

- **PHP performance issue** → [bible/languages/php/coding-standards.md](bible/languages/php/coding-standards.md) + [bible/performance/profiling.md](bible/performance/profiling.md)
- **Database security** → [bible/database/sql-authoring.md](bible/database/sql-authoring.md) + `bible/security/` (when populated)
- **Architectural refactor with tests** → [bible/architecture/principles.md](bible/architecture/principles.md) + [bible/testing/unit-testing.md](bible/testing/unit-testing.md)
- **Error handling in PHP** → [bible/languages/php/error-handling.md](bible/languages/php/error-handling.md) + [bible/languages/php/coding-standards.md](bible/languages/php/coding-standards.md)
- **Magento 2 plugin or observer** → [bible/frameworks/magento/implementation-constraints.md](bible/frameworks/magento/implementation-constraints.md) + [enforcement/reasoning-discipline.md](enforcement/reasoning-discipline.md)
- **Magento 2 validation logic** → [bible/frameworks/magento/implementation-constraints.md](bible/frameworks/magento/implementation-constraints.md) + [bible/architecture/principles.md](bible/architecture/principles.md)
- **Async/queue-based feature** → [enforcement/system-dynamics.md](enforcement/system-dynamics.md) + [enforcement/operational-claims.md](enforcement/operational-claims.md) + [bible/testing/unit-testing.md](bible/testing/unit-testing.md)
- **REST or GraphQL endpoint** → [enforcement/security-boundaries.md](enforcement/security-boundaries.md) + [bible/frameworks/magento/implementation-constraints.md](bible/frameworks/magento/implementation-constraints.md)
- **Concurrent state transitions** → [enforcement/system-dynamics.md](enforcement/system-dynamics.md) + [bible/database/sql-authoring.md](bible/database/sql-authoring.md)
- **Inventory, payment, or order state management** → [enforcement/system-dynamics.md](enforcement/system-dynamics.md) + [enforcement/security-boundaries.md](enforcement/security-boundaries.md) + [enforcement/operational-claims.md](enforcement/operational-claims.md)
- **Magento 2 runtime behavior** (MSI, order states, queues, auth) → [bible/frameworks/magento/runtime-constraints.md](bible/frameworks/magento/runtime-constraints.md) + the generic enforcement doc it references

## Always-applicable documents

These apply to any code task regardless of domain:

- [rules/CORE_PRINCIPLES.md](rules/CORE_PRINCIPLES.md) — DRY, SOLID, KISS, Composition
- [enforcement/ai-checklist.md](enforcement/ai-checklist.md) — Pre-implementation checklist
- [enforcement/reasoning-discipline.md](enforcement/reasoning-discipline.md) — Mandatory reasoning constraints: pre-implementation (`ENF-PRE-001`–`004`), **phased gate protocol** (`ENF-GATE-001`–`005`), post-generation (`ENF-POST-001`–`005`), context retrieval (`ENF-CTX-001`–`003`)
- [enforcement/system-dynamics.md](enforcement/system-dynamics.md) — System dynamics: concurrency simulation, temporal truth, state atomicity, policy/mechanism, integration reality (`ENF-SYS-001`–`005`), **Phase D protocol**
- [enforcement/security-boundaries.md](enforcement/security-boundaries.md) — Security: access boundary declarations, data exposure minimization (`ENF-SEC-001`–`002`)
- [enforcement/operational-claims.md](enforcement/operational-claims.md) — Operations: claim validation, queue completeness (`ENF-OPS-001`–`002`)

## Maintenance notes

- Adding a new bible document requires updating [SKILL.md](SKILL.md) task navigation and this MANIFEST
- Adding a new domain directory requires updating [OVERVIEW.md](OVERVIEW.md)
- If a section grows too large, split it and update references in both files
