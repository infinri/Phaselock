# Phaselock — Navigation

The Coding Bible lives in the Phaselock skill.
Never load the entire Bible at task start.
Load only what the current phase requires.

---

## What to load and when

### Before any task
Read: SKILL.md
Read: enforcement/reasoning-discipline.md → ENF-CTX-004 (context pressure limits)

### Phase A — call-path declaration
Read: enforcement/reasoning-discipline.md → ENF-PRE-001, ENF-GATE-001

### Phase B — domain invariants
Read: enforcement/reasoning-discipline.md → ENF-PRE-002, ENF-GATE-002

### Phase C — seam justification + API safety
Read: enforcement/reasoning-discipline.md → ENF-PRE-003, ENF-PRE-004, ENF-GATE-003

### Phase D — concurrency + failure modeling (only if triggered)
Read: enforcement/system-dynamics.md (full)
Read: enforcement/operational-claims.md (full)

### Before writing any code (all languages)
Read: rules/CORE_PRINCIPLES.md

### Before writing PHP
Read: bible/languages/php/coding-standards.md
Read: bible/languages/php/error-handling.md

### Before writing PHP in Magento 2

Identify which features the module uses from the Phase A declaration, then load only the matching subset. Do not load both files in full for every module.

**Always load** (universal — applies to all Magento 2 modules):
Read: bible/frameworks/magento/implementation-constraints.md → FW-M2-001, FW-M2-002

**Module has plugins** → also load:
Read: bible/frameworks/magento/implementation-constraints.md → FW-M2-004

**Module has a totals collector or discount** → also load:
Read: bible/frameworks/magento/implementation-constraints.md → FW-M2-003, FW-M2-005, FW-M2-006

**Module processes orders or reacts to order state events** → also load:
Read: bible/frameworks/magento/runtime-constraints.md → FW-M2-RT-001, FW-M2-RT-002

**Module has admin-configurable values** → also load:
Read: bible/frameworks/magento/runtime-constraints.md → FW-M2-RT-003

**Module exposes REST, GraphQL, or admin endpoints** → also load:
Read: bible/frameworks/magento/runtime-constraints.md → FW-M2-RT-004

**Module uses message queues / consumers** → also load:
Read: bible/frameworks/magento/runtime-constraints.md → FW-M2-RT-005

**Module touches inventory or runs in multi-website context** → also load:
Read: bible/frameworks/magento/runtime-constraints.md → FW-M2-RT-001, FW-M2-RT-006

### Before writing database schema or queries
Read: bible/database/sql-authoring.md

### Before writing tests
Read: bible/testing/unit-testing.md
Read: enforcement/reasoning-discipline.md → ENF-GATE-007, ENF-POST-004, ENF-POST-005

### Before exposing any endpoint (REST, GraphQL, etc.)
Read: enforcement/security-boundaries.md
Read: bible/security/boundaries.md

### Before building any queue-based feature
Read: bible/playbooks/queue-feature.md

### Before building any API endpoint
Read: bible/playbooks/api-endpoint.md

### After each slice
Hooks run automatically. If they fail: fix before proceeding.
Then: Spawn static-analysis as an isolated subagent Task — pass only the slice file paths, no session context.
  The agent calls `bin/run-analysis.sh` (not raw tool commands). Results are structured JSON.
Then: Spawn plan-guardian as an isolated Task — pass only plan.md path + slice file paths. No session context.
  The agent calls `bin/verify-files.sh`, `bin/scan-deps.sh`, `bin/verify-matrix.sh` (not manual file reads).
Then: Produce slice handoff JSON (see slice-builder.md format) → write to {PROJECT_ROOT}/.claude/handoffs/slice-N.json
Do NOT proceed to slice N+1 until plan-guardian Task returns all OK.
When spawning slice N+1: provide slice-N.json handoff + slice N+1 specification only — not the full session history.

### After all slices — ENF-GATE-FINAL
Read: enforcement/reasoning-discipline.md → ENF-GATE-FINAL
Read: docs/plan-format.md (plan.md must have a structured capabilities block)
Spawn plan-guardian as an isolated Task:
  Input: plan.md path + complete generated file manifest only
  No session context — plan-guardian gets a clean window at 0% context
  The Task runs all four ENF-GATE-FINAL passes via bin/ scripts:
    Pass 1: `bin/verify-matrix.sh plan.md file1 file2 ...` (capability scan)
    Pass 2: `bin/verify-files.sh --project-root DIR file1 file2 ...` (filesystem scan)
    Pass 3: `bin/scan-deps.sh --project-root DIR file1 file2 ...` (dependency scan)
    Pass 4: `bin/check-gates.sh DIR` (gate status)
Verify: Task output shows zero MISSING rows in completion matrix
Then: touch {PROJECT_ROOT}/.claude/gates/gate-final.approved
Then: write app/code/{Vendor}/{ModuleName}/plan.md

---

## Gate approval files (always project-specific — never in skill)

  mkdir -p {PROJECT_ROOT}/.claude/gates
  mkdir -p {PROJECT_ROOT}/.claude/handoffs
  touch {PROJECT_ROOT}/.claude/gates/phase-a.approved
  touch {PROJECT_ROOT}/.claude/gates/phase-b.approved
  touch {PROJECT_ROOT}/.claude/gates/phase-c.approved
  touch {PROJECT_ROOT}/.claude/gates/phase-d.approved
  touch {PROJECT_ROOT}/.claude/gates/test-skeletons.approved
  touch {PROJECT_ROOT}/.claude/gates/gate-final.approved

## plan.md location (per module — never project root)

Each module writes its own plan.md to its module directory:
  app/code/{Vendor}/{ModuleName}/plan.md

Never write plan.md to the project root. Modules sharing a project root will overwrite
each other's architectural record. The enforce-final-gate.sh hook checks for plan.md
writes — the file path must be under the module directory.

## Session metrics (persist at every gate halt)

At every ENF-GATE halt point, append to {PROJECT_ROOT}/.claude/session-metrics.md:
  ## Gate: [gate-name] — [timestamp]
  Context: [N]% ([tokens] tokens)

This survives context compaction. See ENF-CTX-004.

---

## Verification scripts (bin/)

All mechanical verification uses standalone scripts in `bin/`. These replace raw bash
commands in agents and eliminate duplicate analysis logic in hooks.

| Script | Purpose | Used by |
|---|---|---|
| `bin/lib/common.sh` | Shared functions (project root, JSON output, tool finding) | All hooks + scripts |
| `bin/run-analysis.sh` | Static analysis (PHPStan, ESLint, ruff, xmllint, etc.) | validate-file hook, static-analysis agent |
| `bin/check-gates.sh` | Gate approval status check | plan-guardian agent |
| `bin/verify-files.sh` | Batch file existence check | plan-guardian agent |
| `bin/scan-deps.sh` | Import/use statement scanning + dependency verification | plan-guardian agent |
| `bin/verify-matrix.sh` | Completion matrix from plan.md capabilities block | plan-guardian agent |
| `bin/validate-handoff.sh` | Handoff JSON schema validation | plan-guardian agent, validate-handoff hook |

All scripts output structured JSON. Exit 0 = pass, exit 1 = failures found, exit 2 = usage error.

---

## Context hygiene
- Context > 75%: spawn slice-builder subagent for remaining implementation slices
- Context > 70%: do not run ENF-GATE-FINAL in the current session — spawn a fresh one (ENF-CTX-004)
- Never load ai_digest or equivalent context bundles fully (ENF-CTX-001)
- CLAUDE.md is the router. The skill is the rulebook. Never copy rules here.
- Adding a new Bible document? Update this file under the correct phase section.
  A document with no navigation entry here is dark — it will never be loaded.
