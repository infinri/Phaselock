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

---

<!-- RULE START: FW-M2-005 -->
## Rule FW-M2-005: Totals Collector Idempotency and State Reset

**Domain**: Frameworks / Magento 2  
**Severity**: Critical

### Statement
Every custom totals collector's `collect()` method must be fully idempotent. Specifically:

1. **Zero owned total amounts first**: Call `parent::collect()` (which resets `_setAmount(0)` / `_setBaseAmount(0)` for the collector's code), AND explicitly zero any additional amounts the collector writes (e.g., `$total->setDiscountAmount()`, `$address->setCustomField()`).
2. **Clear owned extension attributes**: If the collector populates extension attributes on the address, quote, or items, those must be explicitly cleared to empty/null at the top of `collect()` — before any eligibility check.
3. **Clear on ineligibility**: If the collector determines the cart is not eligible, it must still clear all previously-set values and return. A collector that only writes when eligible and skips cleanup when ineligible will leave stale data from a prior `collectTotals()` cycle.
4. **No additive accumulation across calls**: Never use `addTotalAmount()` without first zeroing. The collector must compute its output from scratch each invocation.
5. **Implement `_resetState()`**: Override `_resetState(): void` to clear any instance-level aggregation state (arrays, caches, flags) and re-set the collector code via `$this->setCode()`.

Reference pattern: `Magento\SalesRule\Model\Quote\Discount::collect()` — lines 164–165 explicitly call `$address->setDiscountDescription([])` and `$address->getExtensionAttributes()->setDiscounts([])` before any rule processing.

### Action
Before writing any totals collector, the AI must produce an **idempotency checklist** listing every piece of state the collector writes (total amounts, address fields, extension attributes, item fields) and confirm each is zeroed at the top of `collect()`. If any state is written but not reset, the implementation is a constraint violation.

### Rationale
Totals collectors run multiple times per request (item add, address change, shipping change, payment change). Without idempotent reset, stale values from a prior cycle persist, causing: (a) discounts that don't reverse when conditions change, (b) double-application on re-collection, (c) ghost line items in REST/GraphQL responses. This is the #1 source of totals-related bugs in custom Magento modules.
<!-- RULE END: FW-M2-005 -->

---

<!-- RULE START: FW-M2-006 -->
## Rule FW-M2-006: CartTotalRepository Does Not Call collectTotals for Non-Virtual Quotes

**Domain**: Frameworks / Magento 2  
**Severity**: High

### Statement
`Magento\Quote\Model\Cart\CartTotalRepository::get()` only calls `$quote->collectTotals()` for **virtual** quotes. For non-virtual quotes, it reads existing address data and totals directly without re-collecting.

This means:

- REST `GET /V1/carts/mine/totals` for non-virtual quotes returns **previously collected** totals, not freshly computed ones.
- Any custom collector's output is only visible in this endpoint if `collectTotals()` was called by a prior operation (e.g., `saveAddressInformation`, item update).
- The `fetch()` method of the collector is called by `getTotals()` on the address — this reads from the `Total` object's stored amounts, not re-computing.

### Action
The AI must not assume REST totals endpoints trigger fresh collection for all quote types. If the implementation requires guaranteed freshness, the AI must state this limitation and document which upstream operations ensure totals are current.

### Rationale
Assuming `collectTotals()` runs in all REST paths leads to implementations that appear to work in testing (where item/address changes precede totals retrieval) but fail in production when totals are fetched without a preceding mutation.
<!-- RULE END: FW-M2-006 -->
