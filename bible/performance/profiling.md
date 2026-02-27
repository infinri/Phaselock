# Performance & Profiling

## Purpose

This document defines **performance principles and optimization guidelines** for maintaining efficient, scalable code.

---

<!-- RULE START: PERF-BIGO-001 -->
## Rule PERF-BIGO-001: Algorithm Complexity Awareness

**Domain**: Performance  
**Severity**: High

### Statement
All code must consider time and space complexity:

- **O(1)** - Constant: Hash lookups, array access
- **O(log n)** - Logarithmic: Binary search
- **O(n)** - Linear: Single loop iterations
- **O(n log n)** - Linearithmic: Efficient sorting
- **Avoid O(n²) or worse** unless dataset is guaranteed small

### Action
Before implementing loops, consider if there's a more efficient approach.

### Rationale
Poor algorithm choice can cause exponential performance degradation as data grows. A seemingly simple nested loop can bring production systems to a halt.
<!-- RULE END: PERF-BIGO-001 -->

---

<!-- RULE START: PERF-OPT-001 -->
## Rule PERF-OPT-001: Optimization Order

**Domain**: Performance  
**Severity**: Medium

### Statement
Follow this optimization order:

1. **Make it work** - Correct functionality first
2. **Make it right** - Clean, maintainable code
3. **Make it fast** - Optimize only when measured

### Action
Profile before optimizing; measure, don't assume.

### Rationale
Premature optimization leads to complex, hard-to-maintain code. Optimization without measurement often targets the wrong bottlenecks.
<!-- RULE END: PERF-OPT-001 -->

---

<!-- RULE START: PERF-LAZY-001 -->
## Rule PERF-LAZY-001: Lazy Loading

**Domain**: Performance  
**Severity**: Medium

### Statement
Load resources only when needed:

- **Lazy Loading**: Defer loading until first access
- **Caching**: Cache expensive computations and frequently accessed data
- **Database Queries**: Minimize N+1 queries, use eager loading when appropriate

### Action
Evaluate whether data is needed immediately or can be deferred.

### Rationale
Eager loading of unused resources wastes memory and CPU cycles. Lazy loading improves startup time and reduces unnecessary work.
<!-- RULE END: PERF-LAZY-001 -->

---

<!-- RULE START: PERF-QBUDGET-001 -->
## Rule PERF-QBUDGET-001: Query Budget Declaration Gate

**Domain**: Performance  
**Severity**: Critical

### Statement
When requirements specify a DB query budget (e.g., "must not introduce more than N additional DB queries per cycle"), the AI must produce a **Query Budget Plan** before writing any implementation code. The plan must include:

1. **Expected query count**: List each DB query the implementation will execute, with the exact repository method or resource model call that triggers it.
2. **Worst-case analysis**: Repository `getList()` calls may trigger multiple underlying queries (entity query, count query, extension attribute loads, EAV attribute loads). The AI must not assume a single repository call = a single DB query. If uncertain about internal query behavior, state the uncertainty and design to worst case.
3. **Caching strategy**: If the query budget is tight, state whether results will be cached per-request (e.g., instance variable, registry, identity map) and under what invalidation conditions.
4. **Fallback if budget is exceeded**: If the standard service contract approach cannot meet the budget, propose a specialized resource model query that retrieves only the needed field(s) — and justify the trade-off explicitly.
5. **Measurement plan**: State how query count will be verified (e.g., MySQL general log, `db_query` profiler, integration test with query counter).

### Action
If a query budget is in the requirements and the AI cannot produce a concrete plan that provably meets it, the AI must halt and declare the gap. Optimistic statements like "this is 1 query" without verifying the repository's internal behavior are constraint violations.

### Rationale
Repository and service contract abstractions hide query complexity. A single `getList()` call can generate 2–5+ queries depending on the entity type, collection implementation, and loaded extension attributes. Assuming query behavior without verification is the primary source of performance budget violations in Magento custom modules.
<!-- RULE END: PERF-QBUDGET-001 -->
