# System Dynamics Enforcement

## Purpose

This document defines **mandatory system-dynamics reasoning** the AI must satisfy before, during, and after implementation of any feature involving concurrency, state transitions, asynchronous processing, multi-context behavior, or temporal dependencies. These rules close the gap between structural correctness and production realism.

Static structure enforcement (ENF-PRE, ENF-POST, ENF-GATE) ensures the AI builds things correctly.
System dynamics enforcement ensures the AI builds things that **survive real production stress**.

---

## Block 1 — Pre-Implementation System Modeling

<!-- RULE START: ENF-SYS-001 -->
## Rule ENF-SYS-001: Concurrency Simulation Phase

**Domain**: System Dynamics  
**Severity**: Critical

### Statement
Before implementing any feature that involves shared state, database writes, message queues, or multi-consumer processing, the AI must produce a written **Concurrency Model** that answers:

1. **Actors**: Who are all concurrent actors that may execute this code simultaneously? (multiple consumers, queue retries, duplicate publishes, admin + cron, REST + GraphQL)
2. **Race windows**: For each write operation, what happens if two actors reach it at the same time? Describe the interleaving explicitly.
3. **Atomic boundaries**: Which operations MUST be atomic? What SQL pattern enforces atomicity? (`INSERT ON DUPLICATE KEY UPDATE`, `UPDATE WHERE status=`, `SELECT FOR UPDATE`, transaction isolation level)
4. **Double-delivery**: What happens if the same message is processed twice? Is the outcome identical?
5. **Crash recovery**: What happens if the process crashes mid-transaction? Is partial state left behind?

### Action
If the AI cannot model all race windows for a given feature, it must halt and declare the gap. Implementing concurrent code without an explicit concurrency model is a constraint violation.

The concurrency model must be written as prose before any implementation code is produced. Each race window must include:
- The two (or more) actors involved
- The specific interleaving that causes the problem
- The SQL or application-level guard that prevents it

### Rationale
The most dangerous production bugs are not structural — they are temporal. Code that passes all unit tests but fails under concurrent load is the definition of "clean but naive." Forcing explicit race-window modeling before implementation prevents the AI from defaulting to check-then-act patterns that break under concurrency.
<!-- RULE END: ENF-SYS-001 -->

---

<!-- RULE START: ENF-SYS-002 -->
## Rule ENF-SYS-002: Temporal Truth Source Declaration

**Domain**: System Dynamics  
**Severity**: Critical

### Statement
For any validation, check, or decision that depends on a prior state transition (e.g., "is this product salable?", "has this order been paid?", "is this coupon still valid?"), the AI must declare:

1. **Authoritative decision point**: Which system event is the source of truth for this fact? (e.g., order placement, invoice creation, payment capture)
2. **Temporal position**: Is this check happening BEFORE or AFTER the authoritative event?
3. **Re-evaluation validity**: Is it semantically valid to re-evaluate this fact now? Or has the authoritative decision already been made?
4. **Staleness risk**: Can this fact change between the authoritative event and the current check? If yes, what is the correct behavior?

### Action
If the AI introduces a validation check for a fact that was already authoritatively decided by a prior event, and re-evaluation could contradict that decision, the check is a constraint violation.

Example violation: Checking product availability after an order has been placed. The order placement flow already validated availability through the inventory system. Re-checking post-placement can produce false negatives (product became unavailable after the order was legitimately placed), leading to skipped downstream processing for valid orders.

### Rationale
"Respect the upstream authority" does not mean "re-evaluate the upstream authority." Temporal truth source confusion is a recurring pattern where the AI adds defensive checks that actually introduce logic flaws. Declaring the authoritative decision point forces the AI to reason about WHEN a fact was established, not just WHETHER it is true now.

> **Framework-specific guidance**: See `bible/frameworks/magento/runtime-constraints.md` for Magento 2 examples (MSI salability, order state machine, payment transitions).
<!-- RULE END: ENF-SYS-002 -->

---

<!-- RULE START: ENF-SYS-003 -->
## Rule ENF-SYS-003: State Transition Atomicity Rule

**Domain**: System Dynamics  
**Severity**: Critical

### Statement
For any status/state transition in the system (e.g., `reserved → released`, `pending → processing`, `active → expired`), the AI must:

1. **Define the state machine**: List all legal states and all legal transitions between them.
2. **Define transition guards**: For each transition, what conditions must be true?
3. **Enforce atomically**: Show the mechanism that ensures the transition is atomic. The AI must choose and **declare** one of the following strategies:
   - **Atomic CAS (compare-and-swap)**: `UPDATE ... SET status = :new WHERE status = :old` — second actor gets affected rows = 0
   - **Pessimistic locking**: `SELECT ... FOR UPDATE` followed by status check + update in same transaction
   - **Idempotent upsert**: `INSERT ... ON DUPLICATE KEY UPDATE` for idempotent creation
   - **Optimistic locking with version column**: Read version → update with `WHERE version = :read_version` → retry or fail on mismatch
   - **Transaction isolation + unique constraint**: Rely on DB unique constraint within a serializable or repeatable-read transaction to reject duplicates
   - **Event sourcing / append-only log**: State derived from event sequence; no mutable status column to race on
4. **Justify the choice**: Why is this strategy appropriate for this specific transition? What are the tradeoffs?
5. **Handle contention**: What happens if two actors attempt the same transition simultaneously? The second must fail gracefully (affected rows = 0, constraint violation caught, version mismatch), not corrupt state.

### Action
State transitions involving multi-actor writes must use one of the declared atomicity strategies above. The chosen mechanism must be **explicitly declared and justified** in the Phase D output.

The following is always a constraint violation:
- Bare read-then-write: `SELECT` to check status → `UPDATE` to change status without any concurrency guard (no `FOR UPDATE`, no `WHERE status=`, no version check, no unique constraint)

The following are NOT violations if declared and justified:
- Optimistic locking with retry logic
- Unique constraint enforcement at the DB level
- Event sourcing where state is derived, not mutated
- Service-layer enforcement backed by DB constraints

### Rationale
Naive read-then-write patterns are the #1 source of race conditions in queue-driven systems. Two consumers can both read `status = 'reserved'`, both decide to release, and both attempt the update. Without a concurrency guard, the second update silently succeeds on an already-released row, potentially triggering duplicate side effects. However, atomic SQL `WHERE` guards are not the only valid strategy — the rule requires that *some* declared mechanism prevents concurrent corruption, not that one specific SQL pattern is always used.
<!-- RULE END: ENF-SYS-003 -->

---

<!-- RULE START: ENF-SYS-004 -->
## Rule ENF-SYS-004: Policy vs Mechanism Separation

**Domain**: System Dynamics  
**Severity**: High

### Statement
Before hardcoding any business-semantic decision into implementation, the AI must classify it into one of three categories:

1. **Deployment-variable policy** — behavior that differs (or may reasonably differ) per store, website, tenant, or deployment. Examples: which order states skip reservation, which payment methods defer processing, threshold quantities for alerts.
2. **Universal domain constant** — behavior that is semantically fixed for all deployments and changing it would break domain integrity. Examples: status enum values (`reserved`, `released`), entity relationship definitions, atomic SQL guard patterns.
3. **Infrastructure mechanism** — purely technical plumbing with no business semantics. Examples: UUID generation, transaction management, queue serialization format, table/column names.

Configurability requirements by category:

**Deployment-variable policy** → MUST be configurable:
- The value MUST be configurable via the framework's admin-accessible configuration system
- The implementation MUST read from configuration services, not hardcoded constants
- The default value MUST be documented

**Universal domain constant** → MAY be hardcoded:
- Named constants are required (no magic strings or numbers)
- The AI must justify why the value is universal, not deployment-variable

**Infrastructure mechanism** → MAY be hardcoded:
- Constants are preferred over magic values

### Action
Any hardcoded value that represents deployment-variable business logic is a constraint violation. The AI must extract it to configuration.

The AI must NOT over-configure universal domain constants. Making status enum values or atomic SQL guards configurable creates fragile, bloated modules. The test is: **"Would a different store/tenant reasonably need a different value?"** If no, it stays hardcoded as a named constant.

Examples of deployment-variable policy (must be configurable):
- Order states that trigger/skip reservation
- Payment methods that defer processing
- Threshold quantities for alerts
- Retry counts and backoff intervals

Examples of universal domain constants (hardcode as named constants):
- Status enum values (`reserved`, `released`)
- Entity relationship definitions
- Atomic SQL guard patterns
- State machine transition definitions

Examples of infrastructure mechanism (hardcode):
- Table names, column names
- UUID format
- SQL patterns

### Rationale
Multi-tenant and multi-context platforms (multi-store, multi-site, multi-region) have business semantics that differ per context. Hardcoding policy into mechanism creates technical debt that requires code changes for what should be configuration changes. Without this rule, the AI will always hardcode because it's simpler.

> **Framework-specific guidance**: See `bible/frameworks/magento/runtime-constraints.md` for Magento 2 configuration patterns (`system.xml`, `config.xml`, `ScopeConfigInterface`).
<!-- RULE END: ENF-SYS-004 -->

---

<!-- RULE START: ENF-SYS-005 -->
## Rule ENF-SYS-005: Integration Reality Check

**Domain**: System Dynamics  
**Severity**: Critical

### Statement
For any feature involving asynchronous processing, multi-step state transitions, database constraints, or concurrent actors, the AI must declare:

1. **Which behaviors cannot be proven with mocks alone**: List specific scenarios where unit test mocks cannot validate the actual behavior (e.g., DB unique constraint enforcement, transaction isolation, queue redelivery, actual state machine transitions across multiple service calls).
2. **Which require integration tests**: For each unprovable behavior, describe the integration test that would validate it.
3. **Production-safety assessment**: Can this module be declared production-safe without integration test validation? If not, what is the minimum integration test coverage required?

### Action
If the AI claims concurrency safety, idempotency, or atomicity but provides only unit tests with mocked database operations, it must explicitly state: "These claims are **unproven at the integration level** and require integration tests against a real database to validate."

Claiming production-readiness for concurrent/async features without integration tests is a constraint violation.

### Hard Gate
The AI must not mark implementation as complete for async/concurrent features unless:
- Integration test structure exists (even if tests require a test database to run)
- Each concurrency claim maps to a specific integration test
- The test explicitly validates the DB constraint or atomic operation, not a mock of it

### Rationale
Unit tests with mocked repositories prove logic flow, not system behavior. A mocked `insertOnDuplicate` call proves nothing about whether the actual DB unique constraint prevents duplicates. Integration tests are the only way to validate concurrency claims, and without this rule, the AI will consistently skip them because unit tests "look complete."
<!-- RULE END: ENF-SYS-005 -->

---

<!-- RULE START: ENF-SYS-006 -->
## Rule ENF-SYS-006: State Machine Completeness — Dead State Detection

**Domain**: System Dynamics
**Severity**: Critical

### Statement
For every state declared in a state machine (ENF-SYS-003), verify:
1. Every non-initial state has at least one code path that transitions INTO it.
2. Every non-terminal state has at least one code path that transitions OUT of it.
3. Every declared state constant is referenced in at least one transition assignment.
   A constant with no assignment anywhere in the codebase is a dead declaration.

### The dead-state test
Before marking implementation complete, for each status constant:
- Search all implementation files for assignments TO that status value
- If no assignment exists (only the constant definition): DEAD STATE
- Dead states are constraint violations

### Action
If a state has no incoming transitions: implement the transition or remove it
from the state machine declaration. 'We will implement it later' is not acceptable
if it was in the approved plan.

### Rationale
STATUS_RELEASED in PartialCaptureInventory: constant declared, tests written,
but nothing ever SET the status to released. Structurally present, functionally dead.
This rule requires verifying not just that states are declared but that they are reachable.
<!-- RULE END: ENF-SYS-006 -->

---

## Block 2 — Phased Protocol Integration

### Phase D — Failure & Concurrency Modeling

When a task triggers ENF-SYS-001 through ENF-SYS-005, add **Phase D** to the Phased Implementation Protocol:

**After Phase C approval, before implementation:**

1. Produce the Concurrency Model (ENF-SYS-001)
2. Produce the Temporal Truth Source declarations (ENF-SYS-002)
3. Produce the State Transition definitions (ENF-SYS-003)
4. Produce the Policy vs Mechanism classification (ENF-SYS-004)
5. Produce the Integration Reality Check (ENF-SYS-005)
6. Produce the Dead State audit (ENF-SYS-006)

Present Phase D as a **single output** for review. The AI must halt and wait for approval before proceeding to implementation.

### Trigger conditions for Phase D

Phase D is mandatory when the task involves ANY of:
- Database writes from multiple actors (queue consumers, cron, admin, API)
- Message queue processing
- Status/state transitions
- Asynchronous side effects
- Multi-website or multi-store behavior
- Inventory, payment, or order state management
- Any claim of idempotency, atomicity, or concurrency safety
