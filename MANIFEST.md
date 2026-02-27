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

## Always-applicable documents

These apply to any code task regardless of domain:

- [rules/CORE_PRINCIPLES.md](rules/CORE_PRINCIPLES.md) — DRY, SOLID, KISS, Composition
- [enforcement/ai-checklist.md](enforcement/ai-checklist.md) — Pre-implementation checklist
- [enforcement/reasoning-discipline.md](enforcement/reasoning-discipline.md) — Mandatory reasoning constraints (pre-implementation, post-generation, context retrieval)

## Maintenance notes

- Adding a new bible document requires updating [SKILL.md](SKILL.md) task navigation and this MANIFEST
- Adding a new domain directory requires updating [OVERVIEW.md](OVERVIEW.md)
- If a section grows too large, split it and update references in both files
