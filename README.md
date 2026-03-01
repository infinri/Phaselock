# AI Workflow — Coding Bible

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
A structured knowledge base of **62 enforceable rules** across 14 documents that govern how AI agents generate code in this codebase. Every rule exists because something went wrong without it.

This is an [Agent Skill](https://agentskills.io/) — a portable, open format for extending AI agent capabilities. Compatible with Windsurf Cascade, Claude Code, Cursor, and any skill-compatible agent.

---

## The Problem This Solves

AI code generation fails in predictable ways:

- **Monolithic output** — the AI generates 30 files in one shot, "forgets" what it approved earlier, and drifts from the plan
- **Prose self-auditing** — the AI says "I checked for violations, none found" and you trust it. That's self-reporting, not enforcement
- **Tests as afterthought** — implementation first, tests second means the tests validate what was built, not what was approved
- **Dead operational claims** — the plan says "max_retries = 3" and the config exists, but nothing reads it at runtime
- **No tool verification** — the AI reasons about its own code instead of running PHPStan, which would catch the bug instantly

This knowledge base converts each of those failure modes into a **hard rule with a halt condition**.

---

## How It Works

The AI follows a gated protocol. No phase can be skipped. No phase can be combined with another. Each phase halts for human review before the next begins.

### Full Protocol Flow

```
Phase A  → Call-path declaration           → ✅ human review
Phase B  → Domain invariant declaration    → ✅ human review
Phase C  → Seam justification              → ✅ human review
Phase D  → Failure & concurrency modeling  → ✅ human review (when triggered)
           ─────────────────────────────────
Tests    → Test skeletons with assertions  → ✅ human review
           ─────────────────────────────────
Slice 1  → Schema & interfaces            → self-validate + findings table → ✅
Slice 2  → Persistence layer              → self-validate + findings table → ✅
Slice 3  → Domain logic                   → self-validate + findings table → ✅
Slice 4  → Integration layer              → self-validate + findings table → ✅
Slice 5  → Exposure layer (API/GraphQL)   → self-validate + findings table → ✅
Slice 6  → Configuration & wiring         → self-validate + findings table → ✅
           ─────────────────────────────────
Per slice: Static analysis (PHPStan level 8, PHPMD, PHPCS)
Per slice: Operational proof traces (config → runtime enforcement)
```

Not every task requires every phase. The AI declares which phases and slices apply and why.

---

## Getting Started

- **AI agents** — Read [SKILL.md](SKILL.md). It's the entry point with task-to-document navigation.
- **Humans** — Read [OVERVIEW.md](OVERVIEW.md) for the directory index, or [CONTRIBUTING.md](CONTRIBUTING.md) to add rules.

---

## Rule Inventory

**62 rules** across 8 domains:

| Domain | Files | Rules | Prefix |
|--------|-------|-------|--------|
| AI Reasoning & Gates | `enforcement/reasoning-discipline.md` | 22 | `ENF-PRE-`, `ENF-GATE-`, `ENF-POST-`, `ENF-CTX-` |
| System Dynamics | `enforcement/system-dynamics.md` | 5 | `ENF-SYS-` |
| Security | `enforcement/security-boundaries.md` | 2 | `ENF-SEC-` |
| Operations | `enforcement/operational-claims.md` | 2 | `ENF-OPS-` |
| Architecture | `bible/architecture/principles.md` | 5 | `ARCH-` |
| Magento 2 | `bible/frameworks/magento/*.md` | 12 | `FW-M2-`, `FW-M2-RT-` |
| Database / SQL | `bible/database/sql-authoring.md` | 3 | `DB-SQL-` |
| PHP | `bible/languages/php/*.md` | 4 | `PHP-` |
| Performance | `bible/performance/profiling.md` | 4 | `PERF-` |
| Testing | `bible/testing/unit-testing.md` | 3 | `TEST-` |

### Key Enforcement Rules

- **`ENF-GATE-001`–`005`** — Phased planning gates (call-path → invariants → seams → system dynamics). No phase skipping. No combining.
- **`ENF-GATE-006`** — Phased code generation in dependency-ordered slices. No monolithic 30-file outputs.
- **`ENF-GATE-007`** — Test-first gate. Test skeletons with assertions are generated and approved BEFORE implementation.
- **`ENF-POST-006`** — Structured findings table per slice: `[File] [Rule Checked] [Violation?] [Evidence]`. "I cannot verify" is a halt condition.
- **`ENF-POST-007`** — Static analysis gate. PHPStan level 8 errors are halt conditions. AI cannot self-approve.
- **`ENF-POST-008`** — Operational proof traces. Every claim (retry, DLQ, escalation) must trace from config declaration to runtime enforcement. Broken trace = incomplete.

---

## Directory Structure

```
ai-workflow/
├── SKILL.md                 # Agent entry point — task→document navigation
├── README.md                # This file
├── MANIFEST.md              # Multi-domain task mapping
├── OVERVIEW.md              # Complete directory index
├── CONTRIBUTING.md          # How to add rules
│
├── rules/                   # Universal principles (DRY, SOLID, KISS)
│
├── enforcement/             # AI behavior enforcement (22 + 5 + 2 + 2 = 31 rules)
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
│   ├── security/            # (awaiting rules)
│   └── playbooks/           # (awaiting rules)
│
└── prompts/                 # Prompt engineering guidelines
```

---

## What Belongs Here

**Include**: Non-obvious constraints, architectural decisions with rationale, framework-specific foot-guns, approved patterns, explicit anti-patterns, failure modes discovered in production or audit.

**Exclude**: Generic tutorials, obvious language syntax, personal style preferences, temporary experiments, speculative best practices.

Every rule should answer: *"What went wrong that made this rule necessary?"*

---

## Authority Model

All rules originate from **explicit human intent**. The AI may format and structure rules but may never invent them. This knowledge base provides reference and reasoning material only — it does not grant file access, override global rules, or authorize actions.

> **Preserve architectural intent, not constrain engineering judgment.** Engineers remain responsible for decisions. The AI exists to assist, not to override.
