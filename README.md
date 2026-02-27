# AI Workflow

A structured, versioned knowledge base of institutional coding knowledge for AI-assisted development.

## What this is

This is an [Agent Skill](https://agentskills.io/) — a portable, open format for extending AI agent capabilities. It provides:

- Architectural decisions and rationale
- Coding standards and constraints
- Framework-specific rules and limitations
- Security expectations
- Performance and scalability guidelines
- Approved patterns and known anti-patterns

Compatible with Windsurf Cascade, Claude Code, Cursor, and any skill-compatible agent. See the [specification](https://agentskills.io/specification).

## Getting started

- **AI agents**: Read [SKILL.md](SKILL.md) — the skill entry point with task→document navigation
- **Humans**: Read [OVERVIEW.md](OVERVIEW.md) for a complete directory index, or [CONTRIBUTING.md](CONTRIBUTING.md) to add rules

## Directory structure

```
ai-workflow/
├── SKILL.md             # Skill entry point (agents start here)
├── README.md            # This file (human overview)
├── MANIFEST.md          # Multi-domain task mapping
├── OVERVIEW.md          # Complete directory index
├── CONTRIBUTING.md      # How to add rules
│
├── rules/               # Universal coding principles (DRY, SOLID, KISS)
├── enforcement/         # AI behavior and code generation standards
├── prompts/             # Prompt engineering guidelines
│
└── bible/               # Domain-specific technical rules
    ├── architecture/    # ARCH- rules
    ├── database/        # DB- rules
    ├── languages/php/   # PHP- rules
    ├── performance/     # PERF- rules
    ├── testing/         # TEST- rules
    ├── frameworks/magento/  # FW-M2- rules
    ├── security/        # SEC- rules (awaiting)
    └── playbooks/       # Workflows (awaiting)
```

## What belongs here

**Include**: Non-obvious constraints, architectural decisions, framework-specific rules, known foot-guns, approved patterns, explicit anti-patterns, rationale ("why") behind decisions.

**Exclude**: Generic language tutorials, obvious best practices, style preferences without architectural impact, temporary or experimental guidance.

## Guiding principle

> **Preserve architectural intent, not constrain engineering judgment.**

Engineers remain responsible for decisions. The AI exists to assist, not to override.
