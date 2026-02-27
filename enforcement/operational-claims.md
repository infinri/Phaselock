# Operational Claims Enforcement

## Purpose

This document defines **mandatory operational reasoning** the AI must satisfy when making claims about performance, throughput, scalability, or reliability. Claims without engineering evidence are not claims — they are marketing.

---

<!-- RULE START: ENF-OPS-001 -->
## Rule ENF-OPS-001: Operational Claim Validation

**Domain**: Operations  
**Severity**: Critical

### Statement
If the AI makes any claim about performance, throughput, scalability, or reliability (e.g., "handles 1000 reservations/minute", "scales horizontally", "resilient to failures"), it must provide supporting evidence for EACH claim:

1. **Query count analysis**: How many SQL queries does this operation execute? Per item? Per order? Per batch? What is the N+1 risk?
2. **Index usage**: Which database indexes support the query patterns? Are there table scans? Has `EXPLAIN` output been considered?
3. **Algorithmic complexity**: What is the time complexity relative to input size? (O(n) items per order, O(1) per message, etc.)
4. **Batch strategy**: If processing multiple items, are they batched into single SQL statements or executed individually in a loop?
5. **Retry strategy**: What happens when processing fails?
   - How many retries?
   - What is the backoff interval? (fixed, linear, exponential)
   - Is there a dead-letter queue for messages that exhaust retries?
   - What is the DLQ monitoring/alerting strategy?
6. **Backpressure handling**: What happens when the queue grows faster than consumers can process?
   - Is there a `maxMessages` limit per consumer run?
   - How many concurrent consumers are configured?
   - What happens to messages during consumer restarts?

### Action
Any throughput or performance claim without the above evidence is a constraint violation. The AI must either:
- Provide the evidence
- Downgrade the claim to "untested estimate"
- Remove the claim entirely

Specific violations:
- Claiming "high throughput" without batch insert strategy → violation
- Claiming "resilient" without DLQ configuration → violation
- Claiming "scalable" without index analysis → violation
- Claiming "1000/minute" without profiling or complexity analysis → violation

### Example

Valid operational claim:
```
Throughput: ~1000 records/minute (estimated)
Evidence:
- Batch INSERT ON DUPLICATE KEY UPDATE: 1 SQL statement per batch (not per item)
- Indexes: btree on relevant lookup columns
- Unique constraint on (item_id, status) — used by ON DUPLICATE KEY
- Complexity: O(n) where n = items per batch (typically 1-20)
- Retry: 3 attempts with 30s TTL, then dead-letter queue
- Consumer: maxMessages=1000, single consumer instance, AMQP connection
- Unproven: actual throughput requires load testing against production-like data volume
```

Invalid operational claim:
```
Throughput: 1000 reservations/minute
(No supporting evidence)
```

### Rationale
Performance claims create expectations that influence architecture decisions, capacity planning, and SLA commitments. Unsubstantiated claims are worse than no claims — they create false confidence that leads to production incidents when actual load exceeds the imagined capacity. Forcing evidence for every claim converts optimism into engineering.
<!-- RULE END: ENF-OPS-001 -->

---

<!-- RULE START: ENF-OPS-002 -->
## Rule ENF-OPS-002: Queue Configuration Completeness

**Domain**: Operations  
**Severity**: High

### Statement
Any feature that uses message queues must declare complete queue infrastructure AND consumer behavior guarantees:

**Infrastructure requirements:**

1. **Primary queue**: exchange, binding, queue name, consumer handler
2. **Dead-letter queue**: DLX exchange, DLQ queue name, binding
3. **Retry policy**: delivery limit, message TTL, backoff behavior
4. **Consumer configuration**: `maxMessages`, connection type, consumer instance count
5. **Monitoring hooks**: How are DLQ messages detected? Is there logging for failed processing?

**Consumer behavior requirements:**

6. **Idempotent processing**: The consumer MUST produce the same outcome whether a message is delivered once or multiple times. The AI must declare which mechanism ensures idempotency (DB unique constraint, idempotency key, atomic upsert, etc.).
7. **Duplicate message handling**: The consumer MUST explicitly handle duplicate messages. "Ignore and log" and "process idempotently" are both valid strategies — but the strategy must be declared. Silent re-processing that causes side effects (double inventory deduction, duplicate emails) is a constraint violation.
8. **Retry failure escalation**: When a message exhausts all retries and lands in the DLQ, the AI must declare what happens next. Valid strategies include: alerting/logging for manual review, automated retry after delay, compensating transaction. "Nothing — it sits in the DLQ" without monitoring is a constraint violation.

### Action
Delivering a queue-based feature is a constraint violation if ANY of these are missing:
- DLQ configuration (infrastructure)
- Idempotent consumer behavior (code-level guarantee)
- Duplicate message handling strategy (declared, not assumed)
- Retry failure escalation path (what happens after DLQ?)

Messages that fail processing must have a defined destination — they cannot be silently dropped. Messages that are redelivered must not cause duplicate side effects.

### Rationale
In production systems, queue consumers crash, database connections drop, and messages get redelivered. Without a DLQ, failed messages are retried indefinitely (causing log noise and resource waste) or silently dropped (causing data loss). Complete queue infrastructure is not optional — it is the minimum viable configuration for any production queue.

> **Framework-specific guidance**: See `bible/frameworks/magento/runtime-constraints.md` for Magento 2 queue patterns (`queue_consumer.xml`, `queue_topology.xml`, AMQP configuration).
<!-- RULE END: ENF-OPS-002 -->
