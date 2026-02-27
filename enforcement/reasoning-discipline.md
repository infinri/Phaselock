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

- Combine two or more phases (A, B, C, D) into a single output
- Skip a phase because it appears trivial or obvious
- Produce implementation code before all applicable phases have been individually presented and approved
- Produce implementation code before test skeletons have been approved (ENF-GATE-007)
- Generate multiple code slices in a single output without justification (ENF-GATE-006)
- Infer approval (e.g., "since the call-path is straightforward, I'll proceed to code")

### Action
Any output that contains content from multiple phases, or that contains implementation code before all phases and test skeletons are approved, is a constraint violation. The AI must revise and re-present the current phase or slice only.

### Rationale
Without an explicit anti-collapse rule, the AI's generative behavior will optimize for output completeness over review quality. This rule is the structural enforcement that prevents regression to single-pass code generation. It applies to the full protocol: planning phases (A–D), test-first gate (ENF-GATE-007), and sliced code generation (ENF-GATE-006).
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

<!-- RULE START: ENF-GATE-006 -->
## Rule ENF-GATE-006: Phased Code Generation — Verified Slices

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
After all planning phases (A–D) are approved, the AI must NOT generate all implementation files in a single pass. Code generation must be broken into **verified slices**, where each slice is a small surface area that the AI self-validates against the approved plan before proceeding.

The slice order follows dependency layers:

1. **Slice 1 — Schema & Interfaces**: Database schema (`db_schema.xml` or migration), service contract interfaces, DTOs/data models. The AI generates ONLY these files, self-validates against the approved Phase B (domain invariants) and Phase C (seam justification), then halts for human review.
2. **Slice 2 — Persistence Layer**: Resource models, repositories, collection classes. The AI generates ONLY these files, self-validates that every repository method satisfies an interface declared in Slice 1, then halts for human review.
3. **Slice 3 — Domain Logic**: Service classes, handlers, processors, state machines. The AI generates ONLY these files, self-validates that every injected dependency uses interfaces from Slice 1 and that state transitions match Phase D declarations, then halts for human review.
4. **Slice 4 — Integration Layer**: Consumers, observers, plugins, cron jobs, CLI commands. The AI generates ONLY these files, self-validates against the approved call-path (Phase A) and concurrency model (Phase D), then halts for human review.
5. **Slice 5 — Exposure Layer**: REST endpoints, GraphQL schema/resolvers, admin UI controllers, `webapi.xml`, `schema.graphqls`. The AI generates ONLY these files, self-validates against security boundary declarations (ENF-SEC-001), then halts for human review.
6. **Slice 6 — Configuration & Wiring**: `di.xml`, `events.xml`, `queue_topology.xml`, `system.xml`, `config.xml`, ACL resources. The AI generates ONLY these files, self-validates that every wired class exists from prior slices, then halts for human review.

### Slice Self-Validation Requirement
At the end of each slice, BEFORE presenting to the human, the AI must produce a brief validation statement:
- Which approved phase outputs did it check this slice against?
- Were any deviations found? If yes, describe and justify each.
- Does every file in this slice reference only types/interfaces that exist in already-approved slices?

### Adaptation
Not every task requires all 6 slices. The AI must declare which slices apply and why at the start of code generation. For small tasks (1–3 files), slices may be combined — but the AI must justify the combination and still produce the self-validation statement.

### Action
The AI must NOT:
- Generate files from multiple dependency layers in a single slice without justification
- Skip the self-validation statement for any slice
- Proceed to the next slice before the current slice is approved
- Generate 30 files in one output and call it "implementation"

Any output that contains files from more than one dependency layer without explicit justification is a constraint violation.

### Rationale
Generating all implementation files in a single pass is where drift happens. The AI "forgets" what it approved earlier as the context window fills with generated code. Breaking code generation into dependency-ordered slices with per-slice validation catches drift when the surface is 3 files, not 30. This is the same principle that makes Phases A–D effective — small surfaces with gates prevent error accumulation.
<!-- RULE END: ENF-GATE-006 -->

---

<!-- RULE START: ENF-GATE-007 -->
## Rule ENF-GATE-007: Test-First Gate — Test Skeletons Before Implementation

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
After all planning phases (A–D) are approved and BEFORE generating any implementation code (Slice 1+), the AI must generate **test skeletons and assertions first**. This is a mandatory gate — implementation code cannot be produced until test skeletons are reviewed and approved.

### Test Skeleton Requirements
The test skeletons must include:

1. **Unit test classes** for every service, handler, and domain logic class identified in the approved plan
2. **Test method stubs with assertions** that encode the approved domain invariants from Phase B:
   - Positive case: valid entity passes validation
   - Negative case: invalid entity fails at exact boundary
   - Persistence failure case: repository returns empty/throws
   - Exception path: unexpected error returns safe default
3. **State transition tests** (when Phase D was triggered) that assert:
   - Each legal transition succeeds with correct pre-conditions
   - Illegal transitions are rejected
   - Concurrent transition attempts: second actor gets failure (affected rows = 0, exception)
4. **Integration test structure** for behaviors identified in ENF-SYS-005 as unprovable-by-mocks
5. **Security boundary tests** for every endpoint:
   - Unauthorized caller is rejected
   - Ownership violation returns 403/exception
   - Valid caller with ownership gets data

### Assertion Specificity
Test assertions must be specific enough to serve as executable specifications. The following are NOT acceptable test skeletons:
- `$this->assertTrue($result)` — asserts nothing meaningful
- `$this->assertNotNull($response)` — proves existence, not correctness
- Empty test methods with `// TODO` comments

Acceptable: `$this->assertEquals(1, $record->getAttempts())`, `$this->expectException(AuthorizationException::class)`, `$this->assertEquals('released', $reservation->getStatus())`

### Process Flow
```
Phase A → ✅ → Phase B → ✅ → Phase C → ✅ → [Phase D → ✅] →
Test Skeletons → ✅ (human reviews tests) →
Slice 1 → ✅ → Slice 2 → ✅ → ... → Slice N → ✅
```

The AI generates implementation code with the explicit instruction to itself: **"make these approved tests pass."**

### Action
The AI must NOT:
- Generate implementation code before test skeletons are approved
- Generate test skeletons that only cover happy paths
- Skip test generation because "the task is simple"
- Generate tests and implementation in the same output

Implementation delivered without corresponding pre-approved test skeletons is a constraint violation.

### Rationale
When tests are generated after implementation, they become an afterthought — the AI writes tests that validate what it already built, not what was approved. Flipping the order to test-first makes it structurally harder for the AI to drift: if a `ReconciliationHandler` doesn't increment attempts, a pre-existing test asserting `$record->getAttempts() === 1` will catch it. This is TDD enforced at the process level, not just as an aspirational principle.
<!-- RULE END: ENF-GATE-007 -->

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

<!-- RULE START: ENF-POST-006 -->
## Rule ENF-POST-006: Structured Findings Table — Per-File Rule Audit

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
After generating each code slice (per ENF-GATE-006), the AI must produce a **structured findings table** — not a prose checklist. Self-reporting in natural language ("I checked for load(), no results found") is not enforcement; it is unverifiable narrative.

### Evidence Standard — Quote the Code, Not Your Belief
**"I believe it complies" is not acceptable.** Evidence must be a direct quote from the generated code — the specific line(s) that satisfy or violate the rule. If you cannot quote a satisfying line, the rule is violated. Halt, fix, re-verify before continuing.

This is the difference between a checklist and an audit:
- **Checklist** (not acceptable): "All injected deps are interfaces; no session/UI deps"
- **Audit** (required): `__construct(ReservationRepositoryInterface $reservationRepository, LoggerInterface $logger)` — line 23. All constructor params are interfaces.

### Required Table Format
For every file generated in the current slice, the AI must first **state which ENF/FW rules apply to that file specifically**, then produce a table with these columns:

| File | Rule | Violation? | Quoted Evidence |
|------|------|------------|-----------------|
| `Model/ReservationRepository.php` | ENF-PRE-004 (API safety) | No | `__construct(ResourceConnection $resource, LoggerInterface $logger)` — line 15. No session/UI deps. |
| `Model/ReservationHandler.php` | ENF-SYS-003 (state atomicity) | No | `$affected = $connection->update($table, ['status' => self::STATUS_RELEASED], ['status = ?' => self::STATUS_RESERVED, 'item_id = ?' => $itemId]);` — line 47. CAS pattern, second actor gets affected=0. |
| `Model/ReservationHandler.php` | ENF-SYS-003 (contention) | No | `if ($affected === 0) { throw new AlreadyReleasedException(...); }` — line 49. Graceful failure on contention. |
| `Api/ReservationInterface.php` | ENF-POST-003 (interface match) | **YES** | `release(int $itemId, string $sku)` in interface vs `release(string $sku, int $itemId)` in implementation — param order mismatch. |

### Per-File Rule Identification
Before filling the table, the AI must list **which rules apply to each file**. Not every rule applies to every file. The AI must declare the applicable subset and justify why other rules do not apply. Skipping a rule without justification is a constraint violation.

Example:
```
File: Model/ReservationHandler.php
Applicable rules: ENF-PRE-004 (has constructor), ENF-SYS-003 (has state transition),
                  ENF-PRE-002 (has validation logic), ENF-POST-003 (implements interface)
Not applicable:   ENF-SEC-001 (not an endpoint), ENF-SYS-002 (no temporal truth check)
```

### Mandatory Checks Per File
For every file generated, the AI must answer ALL applicable questions:

1. **Interface adherence**: Does this file call any method not declared in its injected interface?
2. **State transition atomicity**: Does every state transition use one of the declared atomicity strategies from ENF-SYS-003 (CAS, pessimistic lock, idempotent upsert, optimistic lock, unique constraint, event sourcing)?
3. **Ownership enforcement**: Does every API endpoint enforce ownership before data access (per ENF-SEC-001)?
4. **Dependency safety**: Are all injected dependencies safe in all execution contexts (per ENF-PRE-004)?
5. **Domain invariant compliance**: Does validation logic use persistence verification where Phase B declared it as required (per ENF-PRE-002)?
6. **Approved plan alignment**: Does this file's behavior match what was approved in Phases A–D?

### The "I Cannot Verify" Rule
If the answer to any check is **"I cannot verify"** — because the source is unavailable, the behavior depends on runtime state the AI cannot inspect, or the check requires information outside the current context — the AI must:

1. State "I cannot verify" explicitly in the Evidence column
2. **Halt and flag** the unverifiable item for human review
3. NOT proceed to the next slice until the human addresses the flag

Assuming compliance when verification is impossible is a constraint violation. The AI must admit uncertainty rather than assume correctness.

### Action
Any slice delivered without a structured findings table is a constraint violation. Each file must have its own row — no grouping multiple files into a single entry. Evidence must quote the most **behaviorally relevant** code, not the most obviously compliant line. A table where every row shows no violation must include a sentence explaining **why this slice was low-risk**, or it is treated as rubber-stamping and the AI must re-examine. After fixing any violation, the **full slice table must be regenerated from scratch** — patching a single row while leaving stale evidence in other rows is not acceptable.

### Rationale
Post-generation checks in prose are declarative self-reporting — the AI says "I checked" and you trust it. A structured table with per-file, per-rule evidence converts self-reporting into an auditable artifact. The "I cannot verify" escape hatch forces the AI to admit its limits rather than paper over gaps with confident prose.
<!-- RULE END: ENF-POST-006 -->

---

<!-- RULE START: ENF-POST-007 -->
## Rule ENF-POST-007: Static Analysis Gate — Tool Verification Required

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
AI-generated code must be validated by static analysis tools before implementation is considered complete. The AI's own reasoning is necessary but **not sufficient** — tools catch errors that reasoning misses.

### Required Tools (PHP / Magento 2)
The following tools must be run against all generated PHP files:

1. **PHPStan (level 8 minimum)**: Catches type errors, method-not-found on interfaces, incorrect return types, undefined variables, and wrong argument counts. PHPStan at level 8 would catch errors like calling `getStore()` on `OrderInterface` (method not found on interface type).
2. **PHPMD (PHP Mess Detector)**: Flags duplicated logic, excessive complexity, unused parameters, and god classes. Would catch duplicated ownership logic across resolvers.
3. **Magento Coding Standard (PHPCS)**: Catches missing `@api` annotations, direct `ObjectManager` usage, session dependencies in service classes, and other Magento-specific anti-patterns.

### Optional Custom Rules
When the project includes custom PHPStan rules or PHPCS sniffs, those must also pass. Examples of high-value custom rules:
- Fail if any class injects a concrete model class instead of an interface
- Fail if any repository method uses `load()` instead of `getById()`/`getList()`
- Fail if any plugin targets a concrete class when the interface is available

### Execution Requirement
The AI must:
1. Run the static analysis tools (or request the human to run them)
2. Paste the tool output inline in the conversation
3. Address every error reported — either fix it or justify why it is a false positive
4. Re-run until zero errors remain (or all remaining are documented false positives)

### Halt Condition
Any PHPStan error at level 8 is a **halt condition**. The AI cannot approve its own code or mark a slice as complete while PHPStan errors exist.

### When Tools Are Not Available
If static analysis tools are not installed or cannot be run in the current environment:
1. The AI must state this explicitly: "Static analysis tools are not available in this environment."
2. The AI must still perform **manual static analysis reasoning** — walk through each generated file and check for the categories of errors these tools would catch (type errors, method-not-found, unused parameters, coding standard violations).
3. The implementation must be flagged as: "**Pending static analysis validation** — manual review performed but tool confirmation required before production deployment."

### Action
Implementation marked as complete without static analysis validation (tool or manual + flag) is a constraint violation. The AI must not claim code is production-ready if it has not been validated by tools.

### Rationale
The AI reasoning about its own code is self-grading — it produces the code and then judges it correct. Static analysis tools are an independent verifier with no reasoning bias. PHPStan at level 8 catches entire categories of bugs (wrong types, missing methods, interface violations) that the AI consistently misses because it "knows what it meant." Running tools before human review means the human reviews code that has already passed a mechanical correctness check.
<!-- RULE END: ENF-POST-007 -->

---

<!-- RULE START: ENF-POST-008 -->
## Rule ENF-POST-008: Operational Proof Trace — Config-to-Enforcement Path

**Domain**: AI Enforcement  
**Severity**: Critical

### Statement
For every operational claim made in Phase D or declared in ENF-OPS-001/ENF-OPS-002 (retry logic, dead-letter queue, escalation, backoff, max retries, idempotency), the AI must produce a **proof trace** — not a statement that "this is implemented," but the exact code path from configuration read to runtime enforcement.

### Proof Trace Format
For each operational claim, the AI must trace:

```
Claim: "Failed messages retry 3 times before DLQ"
Proof trace:
  1. Config declaration: system.xml path "section/group/max_retries", default = 3
  2. Config read: Config\RetryConfig::getMaxRetries() reads from ScopeConfigInterface
  3. Injection: RetryConfig injected into ConsumerHandler via di.xml
  4. Enforcement: ConsumerHandler::process() line 52:
     if ($message->getDeliveryCount() >= $this->retryConfig->getMaxRetries()) {
         $this->deadLetterPublisher->publish($message);
         return;
     }
  5. DLQ publish: DeadLetterPublisher::publish() writes to 'module.dlq' exchange
  6. DLQ consumer: queue_consumer.xml declares consumer for 'module.dlq'
  Status: PROVEN — complete path from config to enforcement
```

### Broken Trace Detection
If at any point the trace is broken — a config value is declared but never read, a config is read but the value is never used in a conditional, a DLQ is referenced but no consumer exists — the trace status must be:

```
  Status: BROKEN at step 3 — Config\RetryConfig is never injected into any consumer
  Action: Implementation is INCOMPLETE. The retry claim is unproven.
```

### Required Traces
The AI must produce proof traces for ALL of the following when they appear in the implementation:

1. **Retry logic**: Config declaration → config read → retry count check → enforcement action
2. **Dead-letter queue**: DLQ exchange declaration → DLQ binding → DLQ consumer → escalation action
3. **Backoff/delay**: Config declaration → delay calculation → sleep/reschedule mechanism
4. **Max attempts**: Config declaration → attempt counter increment → max check → halt action
5. **Escalation**: Trigger condition → notification mechanism → recipient configuration
6. **Idempotency**: Unique key declaration → duplicate check mechanism → skip/merge action

### Action
Any operational claim without a complete proof trace is **unproven**. Unproven claims must be either:
- Completed (fix the broken trace by implementing the missing link)
- Downgraded ("this claim is not yet implemented")
- Removed from the implementation description

Delivering code where operational claims are declared in design but have broken traces in implementation is a constraint violation.

### Rationale
The audit pattern that exposed this gap: the plan said "max_retries config exists" — and it did — but nothing read it. The config was declared, the constant was defined, and the implementation looked complete on the surface. But the actual code path from `Config::getMaxRetries()` to the line that enforces it was broken. A proof trace forces the AI to find its own dead code before the human does. It converts "this is implemented" from an assertion into a verifiable chain.
<!-- RULE END: ENF-POST-008 -->

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
