# Phaselock — Coding Bible

```
              & &&&&  &&&&&        && &       &&&&&  &&&& &
         &&& &&&&& &&&&  &&&  && &&&&&&  &&&  &&&& &&&&& &&
         & &&     &&&& &&&&&&&& &&&&& &&&&&&&& &&&&     && &
         &   &  & &&& &&&&&&&&&& &&& &&&&&&&&&& &&& &  &   &
          &      &  &&&&&&&&&&& &&&&& &&&&&&&&&&&  &      &
      &    &&  & && &&&&&&&&&& &&&&&&& &&&&&&&&&  && &  &&    &&
        &&         &    &&&&&  &&&&&&&  &&&&&    &         &&&
          &&        &    &  &&&&&&&&&&&&&  &    &        &&
     &&&&&    &&     & &   &&&&&&&&&&&&&&&   & &      &     &&&&
     &&&&&&&   &&&   &&  &&&&&&&&&&&&&&&&&&&  &&   &&&   &&&&&&&
            &  & &     & &&&&&&&&&&&&&&&&&&& &     & &
      &&&&&     &&     &    &&&&&&&&&&&&&    &     &&   & &&&&&
         &&&  &  &&&   &&     &&&&&&&&&     &&   &&&  &  &&&
       & &  && &&&      &&&  & &&&&&&& &  &&&      &&& &&  &&&
       &   &  &   &&      &&&&& &&&&& &&&&&      &&   &  &   &
        &  &&  &&          & &&&&&&&&&&& &          &&  &&  &&
            &&            & & &&&&&&&&& & &            &&
                         && & &&&&&&&&& & &&
                        &&&   &       &   & &
                        & &  &&&&   &&&& &&&
                        &  &&   &        &&&
                          &&&&& &&&&&  & &&&
                          &&&&  &     & &&
                           &   &&&& & & &&
                            && &&&&&&&& &
                              &  &&&&&
                                  &&

```

A structured knowledge base of **62 enforceable rules** across 16 documents that govern how AI agents generate, review, and verify code. Every rule exists because something went wrong without it.

This is an [Agent Skill](https://agentskills.io/) — a portable, open format for extending AI agent capabilities. Compatible with Claude Code, Windsurf Cascade, Cursor, and any skill-compatible agent.

---

## The Problem This Solves

AI code generation fails in predictable, recurring ways:

- **Monolithic output** — the AI generates 30 files in one shot, drifts from the approved plan, and "forgets" earlier decisions
- **Prose self-auditing** — the AI says "I checked for violations, none found" and you trust it. That's self-reporting, not enforcement
- **Tests as afterthought** — implementation first, tests second means the tests validate what was built, not what was approved
- **Dead operational claims** — the plan says `max_retries = 3` and the config exists, but nothing reads it at runtime
- **No tool verification** — the AI reasons about its own code instead of running PHPStan, which would catch the bug instantly
- **Context drift** — long sessions accumulate stale context; the AI reasons from what it remembers, not from what the code says

Phaselock converts each failure mode into a **hard rule with a halt condition**. Phases cannot be skipped. Phases cannot be combined. The AI cannot self-approve.

---

## How It Works

The AI follows a locked, gated protocol. Each phase produces a single artifact, halts for human review, and only proceeds on approval.

### Full Protocol Flow

```
Phase A  → Call-path declaration           → halt → human review
Phase B  → Domain invariant declaration    → halt → human review
Phase C  → Seam justification              → halt → human review
Phase D  → Failure & concurrency modeling  → halt → human review  (when triggered)
           ────────────────────────────────────────────────────
Tests    → Test skeletons with assertions  → halt → human review
           ────────────────────────────────────────────────────
Slice 1  → Schema & interfaces             → findings table → static analysis → halt
Slice 2  → Persistence layer               → findings table → static analysis → halt
Slice 3  → Domain logic                    → findings table → static analysis → halt
Slice 4  → Integration layer               → findings table → static analysis → halt
Slice 5  → Exposure layer (API/GraphQL)    → findings table → static analysis → halt
Slice 6  → Configuration & wiring          → findings table → static analysis → halt
           ────────────────────────────────────────────────────
Final    → Plan-to-code completeness scan  → gate-final.approved
```

**Per slice, the AI must produce:**
- A structured findings table: `[File] [Rule Checked] [Violation?] [Evidence]` — "I cannot verify" is a halt condition
- Static analysis results (PHPStan level 8, PHPMD, PHPCS) — errors are halt conditions, AI cannot self-approve
- Operational proof traces — every claim (retry, DLQ, escalation, config value) must trace from declaration to runtime enforcement

Not every task requires every phase. The AI declares which phases and slices apply and why, before writing a single line of code.

---

## Getting Started

- **AI agents** — Read [SKILL.md](SKILL.md). It is the entry point with task-to-document navigation and the phased protocol.
- **Humans** — Read [OVERVIEW.md](OVERVIEW.md) for the directory index, or [CONTRIBUTING.md](CONTRIBUTING.md) to add rules.

---

## Rule Inventory

**62 rules** across 10 domains:

| Domain | Files | Rules | Prefix |
|--------|-------|-------|--------|
| AI Reasoning & Gates | `enforcement/reasoning-discipline.md` | 22 | `ENF-PRE-`, `ENF-GATE-`, `ENF-POST-`, `ENF-CTX-` |
| System Dynamics | `enforcement/system-dynamics.md` | 5 | `ENF-SYS-` |
| Security (Enforcement) | `enforcement/security-boundaries.md` | 2 | `ENF-SEC-` |
| Security (Bible) | `bible/security/boundaries.md` | — | `SEC-` |
| Operations | `enforcement/operational-claims.md` | 2 | `ENF-OPS-` |
| Architecture | `bible/architecture/principles.md` | 5 | `ARCH-` |
| Magento 2 | `bible/frameworks/magento/*.md` | 12 | `FW-M2-`, `FW-M2-RT-` |
| Database / SQL | `bible/database/sql-authoring.md` | 3 | `DB-SQL-` |
| PHP | `bible/languages/php/*.md` | 4 | `PHP-` |
| Performance | `bible/performance/profiling.md` | 4 | `PERF-` |
| Testing | `bible/testing/unit-testing.md` | 3 | `TEST-` |

### Key Enforcement Rules

- **`ENF-GATE-001`–`005`** — Phased planning gates (call-path → invariants → seams → system dynamics). No phase skipping. No combining.
- **`ENF-GATE-006`** — Sliced code generation in dependency order. No monolithic multi-file outputs.
- **`ENF-GATE-007`** — Test-first gate. Test skeletons with assertions are approved before any implementation code is written.
- **`ENF-GATE-FINAL`** — Plan-to-code completeness verification. Every planned capability must appear in the generated file manifest.
- **`ENF-POST-006`** — Structured findings table per slice. Evidence required. "I cannot verify" halts the slice.
- **`ENF-POST-007`** — Static analysis gate. PHPStan level 8. AI cannot self-approve; tool output is authoritative.
- **`ENF-POST-008`** — Operational proof traces. Config → runtime enforcement must be traceable end-to-end. Broken trace = incomplete slice.
- **`ENF-CTX-004`** — Context pressure limits. At 70% context, spawn a fresh session for ENF-GATE-FINAL. At 75%, spawn a subagent for remaining slices.

---

## Directory Structure

```
phaselock/
├── SKILL.md                 # Agent entry point — task→document navigation
├── README.md                # This file
├── MANIFEST.md              # Multi-domain task mapping
├── OVERVIEW.md              # Complete directory index
├── CONTRIBUTING.md          # How to add rules
│
├── rules/                   # Universal principles (DRY, SOLID, KISS)
│   └── CORE_PRINCIPLES.md
│
├── enforcement/             # AI behavior enforcement (31 rules)
│   ├── reasoning-discipline.md   # Gates, pre/post checks, context discipline
│   ├── system-dynamics.md        # Concurrency, state machines, temporal truth
│   ├── security-boundaries.md    # Access control, ownership enforcement
│   ├── operational-claims.md     # Throughput claims, queue completeness
│   └── ai-checklist.md           # Pre-implementation checklist
│
├── bible/                   # Domain-specific technical rules (31 rules)
│   ├── architecture/        # Code organization, DI, extension points
│   ├── database/            # SQL authoring, bind parameters
│   ├── frameworks/magento/  # Implementation + runtime constraints
│   ├── languages/php/       # Coding standards, error handling
│   ├── performance/         # Big-O, lazy loading, query budgets
│   ├── testing/             # TDD, isolation, integration
│   ├── security/            # Access boundaries, data exposure
│   └── playbooks/           # End-to-end build checklists (API, queues)
│
└── prompts/                 # Prompt engineering guidelines
```

---

## What Belongs Here

**Include**: Non-obvious constraints, architectural decisions with rationale, framework-specific foot-guns, approved patterns, explicit anti-patterns, failure modes discovered in production or audit.

**Exclude**: Generic tutorials, obvious language syntax, personal style preferences, temporary experiments, speculative best practices.

Every rule should answer: *"What went wrong that made this rule necessary?"*

---

## The Dark-File Rule

A Bible document is **active** only when it exists AND has a navigation entry in `.claude/CLAUDE.md` specifying when to load it. A file without a navigation entry is **dark** — it is never loaded and its rules are never enforced.

When adding a new document, the file and its navigation entry must be committed together. A document with no navigation entry is not a valid commit.

---

## Authority Model

All rules originate from **explicit human intent**. The AI may format and structure rules but may never invent them. Phaselock provides reference and reasoning material only — it does not grant file access, override global rules, or authorize actions.

> **Preserve architectural intent, not constrain engineering judgment.** Engineers remain responsible for decisions. The AI exists to assist, not to override.
