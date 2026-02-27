# AI Reasoning Discipline

## Purpose

This document defines **mandatory reasoning constraints** the AI must satisfy before, during, and after code generation. These are hard rules, not suggestions. The AI must satisfy each rule before proceeding to the next phase of implementation.

---

## Block 1 — Mandatory Pre-Implementation Reasoning

<!-- RULE START: ENF-PRE-001 -->
## Rule ENF-PRE-001: Call-Path Declaration Required Before Plugin/Observer Code

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
Before writing any plugin, observer, or event listener, the AI must produce a written call-path declaration that answers:

- What is the entry point for this feature in each execution context (frontend, REST, GraphQL, admin, guest, CLI)?
- Does the same concrete class handle all contexts, or are there separate implementations?
- Will a plugin on the chosen class intercept all required contexts?
- If not, which contexts are missed and why is that acceptable?

This declaration must be written as prose before any code is produced.

### Action
If the AI cannot answer from the provided context, it must state the gap explicitly and halt. Silent assumption is a constraint violation.

### Rationale
Plugins and observers that appear correct in one context often fail silently in others. A written call-path declaration forces the AI to reason about coverage before committing to an implementation.
<!-- RULE END: ENF-PRE-001 -->

---

<!-- RULE START: ENF-PRE-002 -->
## Rule ENF-PRE-002: Domain Invariant Declaration Required Before Validation Logic

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
Before writing any validation method, the AI must produce a written domain invariant declaration that answers:

- What makes this entity legitimate at the domain level?
- Is legitimacy a structural property (format, prefix) or a persistence fact (exists in DB, rule is active)?
- If persistence-based: which repository or service contract is used to verify existence?
- If format-based: is there an explicit business requirement stating that format alone is sufficient?

### Action
If the answer is persistence-based and no repository or service contract lookup is present in the implementation, the AI must treat this as a constraint violation and revise.

### Rationale
Validation logic that infers domain legitimacy from format alone (string matching, prefix checking) instead of persistence verification is a recurring source of false positives and missed edge cases.
<!-- RULE END: ENF-PRE-002 -->

---

<!-- RULE START: ENF-PRE-003 -->
## Rule ENF-PRE-003: Plugin Seam Justification Required Before di.xml

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
Before writing any plugin declaration, the AI must justify:

- Why this specific class (not the interface, not a parent class)?
- Why this hook type (before / around / after)?
- What state is available at this point in the execution sequence?
- Does the logic depend on data that is only reliable after a specific side effect (e.g. totals collection, quote persistence)?

### Action
If timing-dependent logic is present, the AI must explicitly state which side effects have occurred before the plugin executes. Missing justification is a constraint violation.

### Rationale
Incorrect plugin seam selection causes silent failures that are extremely difficult to diagnose. Explicit justification prevents the AI from defaulting to the most obvious interception point without verifying it is the correct one.
<!-- RULE END: ENF-PRE-003 -->

---

<!-- RULE START: ENF-PRE-004 -->
## Rule ENF-PRE-004: API Safety Check Required Before Dependency Injection

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
Before injecting any class or interface as a constructor dependency, the AI must verify:

- Is this API safe in all execution contexts where this class will be invoked?
- If the class is called via REST or GraphQL, does the dependency assume UI context (session, message manager, layout)?
- If the dependency is conditional, has the AI isolated it behind an interface that can be safely no-op'd in non-UI contexts?

### Action
Any MessageManager, session, or UI-dependent class injected into a service-layer class is a constraint violation unless explicitly justified.

### Rationale
Dependencies that assume UI context cause fatal errors or undefined behavior in headless execution contexts (REST, GraphQL, CLI). This is a common source of production incidents.
<!-- RULE END: ENF-PRE-004 -->

---

## Block 2 — Phased Implementation Protocol

<!-- RULE START: ENF-GATE-001 -->
## Rule ENF-GATE-001: Phase A — Call-Path Declaration Gate

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
When a code-generation task involves plugins, observers, or event listeners, the AI must begin with **Phase A only**:

1. Produce the call-path declaration required by ENF-PRE-001
2. Present it to the user as the **sole output** of this phase
3. **Halt and wait for explicit human review/approval** before proceeding

### Action
The AI must not produce domain invariant analysis, seam justification, or any implementation code in the same output as the call-path declaration. Combining Phase A with any subsequent phase is a constraint violation.

### Rationale
Forcing a single-phase output prevents the AI from front-loading all reasoning in one pass, which collapses review into a rubber-stamp exercise and masks errors in call-path analysis.
<!-- RULE END: ENF-GATE-001 -->

---

<!-- RULE START: ENF-GATE-002 -->
## Rule ENF-GATE-002: Phase B — Domain Invariant Declaration Gate

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
After receiving human approval of Phase A, the AI must proceed to **Phase B only**:

1. Produce the domain invariant declaration required by ENF-PRE-002
2. Present it to the user as the **sole output** of this phase
3. **Halt and wait for explicit human review/approval** before proceeding

### Action
The AI must not produce seam justification or any implementation code in the same output as the domain invariant declaration. Combining Phase B with any subsequent phase is a constraint violation.

### Rationale
Domain invariant analysis depends on a reviewed call-path. Presenting it separately ensures the invariant is evaluated against the approved call-path, not a provisional one.
<!-- RULE END: ENF-GATE-002 -->

---

<!-- RULE START: ENF-GATE-003 -->
## Rule ENF-GATE-003: Phase C — Seam Justification Gate

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
After receiving human approval of Phase B, the AI must proceed to **Phase C only**:

1. Produce the plugin seam justification required by ENF-PRE-003 and the API safety check required by ENF-PRE-004
2. Present them to the user as the **sole output** of this phase
3. **Halt and wait for explicit human review/approval** before proceeding to code generation

### Action
The AI must not produce any implementation code in the same output as the seam justification. Combining Phase C with implementation is a constraint violation.

### Rationale
Seam justification depends on approved call-paths and domain invariants. Presenting it separately ensures timing and state dependencies are evaluated against the approved analysis chain, not assumptions.
<!-- RULE END: ENF-GATE-003 -->

---

<!-- RULE START: ENF-GATE-004 -->
## Rule ENF-GATE-004: Anti-Collapse — No Phase Combination or Skipping

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
The AI must never:

- Combine two or more phases (A, B, C) into a single output
- Skip a phase because it appears trivial or obvious
- Produce implementation code before all three phases have been individually presented and approved
- Infer approval (e.g., "since the call-path is straightforward, I'll proceed to code")

### Action
Any output that contains content from multiple phases, or that contains implementation code before all phases are approved, is a constraint violation. The AI must revise and re-present the current phase only.

### Rationale
Without an explicit anti-collapse rule, the AI's generative behavior will optimize for output completeness over review quality. This rule is the structural enforcement that prevents regression to single-pass code generation.
<!-- RULE END: ENF-GATE-004 -->

---

<!-- RULE START: ENF-GATE-005 -->
## Rule ENF-GATE-005: Phase D — System Dynamics Gate (Hard Block)

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
When a task triggers any ENF-SYS-* rule (see trigger conditions in [system-dynamics.md](system-dynamics.md)), the AI must complete **Phase D** before producing implementation code:

1. Produce the system dynamics analysis required by the triggered ENF-SYS-* rules
2. Present Phase D as the **sole output** of this phase
3. **Halt and wait for explicit human review/approval** before proceeding to implementation

Phase D is a **hard blocking gate**, identical in enforcement to Phases A, B, and C.

### Action
The AI must NOT:
- Produce implementation code in the same output as Phase D analysis
- Skip Phase D because the concurrency model "seems straightforward"
- Infer Phase D approval (e.g., "the race conditions are simple, so I'll proceed")
- Combine Phase D with any other phase
- Proceed to implementation if any ENF-SYS-* declaration is incomplete or contains gaps

If the AI produces implementation code before Phase D is individually presented and approved, it is a constraint violation. The AI must revise and re-present Phase D only.

### Hard Gate Checklist
Before the AI may proceed past Phase D, ALL of the following must be true:

- [ ] Concurrency model complete (ENF-SYS-001) — all actors and race windows identified
- [ ] Temporal truth sources declared (ENF-SYS-002) — no re-evaluation of upstream authorities
- [ ] State transitions defined with atomicity mechanism (ENF-SYS-003) — chosen strategy declared and justified
- [ ] Policy vs mechanism classified (ENF-SYS-004) — configurable items identified
- [ ] Integration reality check complete (ENF-SYS-005) — unprovable-by-mocks behaviors listed
- [ ] Human has explicitly approved Phase D output

If any item is incomplete, the AI must declare the gap and halt.

### Rationale
Without a formal blocking gate, system dynamics analysis degenerates into prose that the AI writes and then ignores. The existing gates (ENF-GATE-001 through 004) work because they are hard blocks — the AI cannot proceed without approval. Phase D must have identical enforcement weight, or the AI will write a concurrency section, produce some words about race windows, and then proceed without truly enforcing atomic design.
<!-- RULE END: ENF-GATE-005 -->

---

## Block 3 — Post-Generation Verification

<!-- RULE START: ENF-POST-001 -->
## Rule ENF-POST-001: Self-Audit Against Call-Path Declaration

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
After generating all implementation files, the AI must re-read its own call-path declaration from ENF-PRE-001 and verify:

- Does the plugin intercept all declared execution contexts?
- Are there any contexts in the declaration that are not covered by the implementation?
- If gaps exist, are they explicitly documented as known limitations?

### Action
Undeclared coverage gaps are constraint violations. The AI must either close the gap or document it before delivery.

### Rationale
Implementation drift from the original call-path declaration is a primary source of incomplete features that pass code review but fail in production.
<!-- RULE END: ENF-POST-001 -->

---

<!-- RULE START: ENF-POST-002 -->
## Rule ENF-POST-002: Self-Audit Against Domain Invariant Declaration

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
After generating all validation logic, the AI must re-read its domain invariant declaration from ENF-PRE-002 and verify:

- Does every validation method satisfy the declared invariant?
- Is there any place where format inference is used where persistence verification was declared as required?

### Action
If the implementation deviates from the declaration, the deviation must be explicitly justified or corrected. Silent deviation is a constraint violation.

### Rationale
Validation logic that starts with a persistence-based declaration but drifts to format-based checking during implementation defeats the purpose of the invariant analysis.
<!-- RULE END: ENF-POST-002 -->

---

<!-- RULE START: ENF-POST-003 -->
## Rule ENF-POST-003: Interface Consistency Verification

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
The AI must verify that:

- Parameter order in the interface matches parameter order in the concrete implementation
- Parameter order in the concrete implementation matches all call sites
- Return types in the interface match what the implementation actually returns

### Action
Any deviation between interface declaration and implementation is a constraint violation. The AI must fix the inconsistency before delivery.

### Rationale
Interface-implementation mismatches cause subtle runtime errors that are difficult to trace, especially in systems with dependency injection where the mismatch may not surface until a specific execution path is hit.
<!-- RULE END: ENF-POST-003 -->

---

<!-- RULE START: ENF-POST-004 -->
## Rule ENF-POST-004: Unit Tests Must Cover Domain Invariant — Hard Gate

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
Every validation method must have tests that cover:

- The positive case (valid entity passes)
- The negative case at the boundary (invalid entity fails at the exact threshold)
- The persistence failure case (DB unavailable, entity not found, rule inactive)
- The exception path (unexpected error is caught, logged, and returns a safe default)
- The **idempotency case** (for totals collectors: calling collect() twice produces identical results; calling collect() after eligibility changes clears prior values)
- The **state reversal case** (conditions that were true become false; all owned state is cleaned up)

### Hard Gate
The AI must **refuse to mark implementation as complete** if the declared domain invariants from Phase B do not have corresponding test coverage. Specifically:

1. For each invariant declared in Phase B, at least one test must exercise it.
2. For each persistence-based check, a test must mock the repository to return failure/empty and verify the safe default.
3. For each threshold, boundary tests per ENF-POST-005 must exist.
4. If tests are missing, the AI must list which invariants lack coverage and produce the tests before finalizing.

### Action
Tests that only cover format or structural checks on a validator declared as persistence-based are constraint violations. Implementation delivery without matching test coverage for every declared invariant is a constraint violation.

### Rationale
Happy-path-only tests create false confidence. Validation methods are critical control points that must be tested against the full range of failure modes. Without a hard gate tying tests to declared invariants, the AI will consistently under-test edge cases.
<!-- RULE END: ENF-POST-004 -->

---

<!-- RULE START: ENF-POST-005 -->
## Rule ENF-POST-005: Boundary Values Must Be Tested Explicitly

**Domain**: AI Enforcement  
**Severity**: High

### Statement
For any threshold-based logic (item count, subtotal, customer group ID), the AI must produce tests for:

- Exactly at the threshold (must NOT trigger)
- One unit above the threshold (must trigger)
- Well above the threshold (must trigger)

### Action
Tests that only cover "clearly above" and "clearly below" cases without testing the exact boundary are incomplete and must be revised.

### Rationale
Off-by-one errors at boundaries are among the most common bugs in threshold-based logic. Explicit boundary tests catch these before they reach production.
<!-- RULE END: ENF-POST-005 -->

---

## Block 4 — Context Retrieval Discipline

<!-- RULE START: ENF-CTX-001 -->
## Rule ENF-CTX-001: Retrieve Only Task-Relevant Context

**Domain**: AI Enforcement  
**Severity**: High

### Statement
The AI must not scan the full digest passively and assume it has absorbed what matters. Before each implementation phase, the AI must:

- Explicitly identify which extractors are relevant to the current task
- Pull the specific data from those extractors
- State relevant extractor selection before implementation begins

### Action
Passive scanning without explicit extractor selection is a constraint violation.

### Rationale
Passive absorption of large context windows leads to hallucinated connections and missed critical details. Explicit retrieval forces targeted reasoning.
<!-- RULE END: ENF-CTX-001 -->

---

<!-- RULE START: ENF-CTX-002 -->
## Rule ENF-CTX-002: Missing Context Must Halt Implementation — Verification Checklist

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
The AI must not fill missing context with training data assumptions. If the call-path for a feature is not in the digest, the AI must say so and request the information before proceeding.

### Verification Checklist
Before asserting any of the following in a call-path or architecture declaration, the AI must have **read the actual source file** from the codebase (vendor or app) or found the fact in `.ai-context` data. If neither is available, the assertion must be flagged as **unverified** and the AI must request confirmation:

1. **"Class X calls collectTotals()"** — read the source of class X or find it in `call_graph.json`.
2. **"GraphQL field Y is resolved by class Z"** — read `schema.graphqls` or find it in `call_graph.json` entry points.
3. **"Repository method returns N queries"** — read the repository implementation or flag as unverified.
4. **"Extension attribute A is populated by class B"** — read class B's source or flag as unverified.
5. **"REST endpoint returns field X from source Y"** — read the service contract implementation (e.g., `CartTotalRepository::get()`) or flag as unverified.
6. **"Area code check prevents execution in context C"** — verify `App\State` is injectable in the target class's execution context.

Each assertion in the call-path declaration must be tagged: `[verified: source_file]` or `[unverified: needs confirmation]`.

### Action
Silent assumptions about execution flow, entity relationships, or API safety are constraint violations. The AI must halt and declare the gap. Confident prose that reads as fact but is actually a training-data guess is the most dangerous form of this violation.

### Rationale
Training data assumptions are the primary source of plausible-looking but incorrect implementations. Halting on missing context is safer than generating code based on guesses. The verification checklist converts a subjective rule ("don't assume") into an auditable requirement ("show me the source").
<!-- RULE END: ENF-CTX-002 -->

---

<!-- RULE START: ENF-CTX-003 -->
## Rule ENF-CTX-003: Resist Training Data Bias for Deprecated Patterns

**Domain**: AI Enforcement  
**Severity**: High

### Statement
The AI must treat any pattern that appears frequently in training data but conflicts with the provided context as a constraint violation. Specifically:

- Factory patterns over repositories
- Model load over service contracts
- String inference over persistence verification

### Action
If training data bias is detected in a generated output, the output must be revised before delivery.

### Rationale
AI models are statistically biased toward deprecated patterns that appear frequently in older codebases. Explicit resistance prevents regression to outdated practices.
<!-- RULE END: ENF-CTX-003 -->
