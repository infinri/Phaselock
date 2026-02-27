# Magento 2 Implementation Constraints

## Purpose

This document defines **Magento 2-specific implementation constraints** that govern how domain logic, data access, and plugin interception must be implemented. These are hard rules, not suggestions.

---

<!-- RULE START: FW-M2-001 -->
## Rule FW-M2-001: Validation Must Be Backed by Persistence

**Domain**: Frameworks / Magento 2  
**Severity**: Critical

### Statement
Any validation that determines whether a domain entity is legitimate must use a repository, service contract, or resource model lookup. String matching, prefix checking, or format inference alone does not constitute validation of a domain entity's legitimacy.

### Action
If format validation is intentional and explicitly required, it must be documented in a code comment referencing the specific business requirement that justifies it. Otherwise, every legitimacy check must hit the persistence layer.

### Rationale
Format-based validation creates false positives (entities that look valid but don't exist) and false negatives (entities that exist but don't match expected format). Only the persistence layer is the source of truth for entity legitimacy.
<!-- RULE END: FW-M2-001 -->

---

<!-- RULE START: FW-M2-002 -->
## Rule FW-M2-002: Factory and Model::load() Patterns Are Forbidden

**Domain**: Frameworks / Magento 2  
**Severity**: Critical

### Statement
The AI must not use `SomeFactory->create()->load($id)` or `Model::loadByCode()` patterns in new implementations. All entity retrieval must go through the repository layer.

### Action
If a repository method does not exist for the required lookup, the AI must state this gap explicitly rather than fall back to the model layer silently. The gap must be resolved by creating a repository method or requesting guidance — never by reverting to deprecated patterns.

### Rationale
Factory/model-load patterns bypass service contracts, skip event dispatching, ignore extension attributes, and create tight coupling to the persistence layer. Repository-based retrieval is the Magento 2 architectural standard.
<!-- RULE END: FW-M2-002 -->

---

<!-- RULE START: FW-M2-003 -->
## Rule FW-M2-003: Quote State Must Be Read at the Correct Execution Point

**Domain**: Frameworks / Magento 2  
**Severity**: Critical

### Statement
If logic depends on quote totals, subtotal, or applied discounts:

- It must execute **after** `collect_totals` has run
- If logic executes in a `before` plugin, it must **not** read totals-dependent data
- If an `around` plugin is used and the logic depends on post-apply state, the data must be read **after** `proceed()` has been called and the quote re-fetched

### Action
Any implementation that reads totals-dependent data before `collect_totals` has completed is a constraint violation. The AI must verify the execution sequence before placing totals-dependent logic.

### Rationale
Quote totals are computed lazily and cached. Reading them before collection returns stale or zero values, causing silent logical errors that are extremely difficult to reproduce and diagnose.
<!-- RULE END: FW-M2-003 -->

---

<!-- RULE START: FW-M2-004 -->
## Rule FW-M2-004: Target Concrete Classes for Plugins by Default

**Domain**: Frameworks / Magento 2  
**Severity**: High

### Statement
The concrete class must be targeted for plugins, not the interface, unless multi-implementation coverage is explicitly required. Plugins on interfaces are valid in Magento 2 but are less predictable than plugins on concrete classes.

### Action
The AI must target the concrete class by default. If the interface is targeted, the AI must explicitly justify why interface-level interception is required and which concrete implementations are covered.

### Rationale
Interface-level plugins intercept all implementations, which may include internal or framework classes not intended for interception. Concrete-class targeting provides precise, predictable interception scope.
<!-- RULE END: FW-M2-004 -->
