# Architecture Principles

## Purpose

This document defines **architectural principles and design patterns** that govern how code is organized, extended, and maintained in this codebase.

---

<!-- RULE START: ARCH-ORG-001 -->
## Rule ARCH-ORG-001: Code Organization -- Layer Separation

**Domain**: Architecture
**Severity**: High
**Scope**: module

### Trigger
When creating or modifying a class that contains logic belonging to a different architectural layer (e.g., SQL queries in a controller, HTML in a service class, business logic in a resource model).

### Statement
Each class must belong to exactly one architectural layer: presentation (controllers, templates, view models), business logic (services, handlers, processors), or data access (repositories, resource models). A class must not contain logic from a different layer.

### Violation (bad)
```php
// Controller contains SQL query -- presentation layer doing data access
class OrderController extends Action
{
    public function execute()
    {
        $connection = $this->resourceConnection->getConnection();
        $orders = $connection->fetchAll(
            "SELECT * FROM sales_order WHERE customer_id = :id",
            [':id' => $this->getRequest()->getParam('customer_id')]
        );
        return $this->resultJsonFactory->create()->setData($orders);
    }
}
```

### Pass (good)
```php
// Controller delegates to service, service delegates to repository
class OrderController extends Action
{
    public function __construct(
        private readonly OrderServiceInterface $orderService
    ) {}

    public function execute()
    {
        $customerId = (int) $this->getRequest()->getParam('customer_id');
        $orders = $this->orderService->getByCustomerId($customerId);
        return $this->resultJsonFactory->create()->setData($orders);
    }
}
```

### Enforcement
Per-slice findings table (ENF-POST-006) must verify layer separation for each generated file. Code review.

### Rationale
Mixed layers create classes that are untestable, unreusable, and fragile. A controller with SQL queries cannot be unit tested without a database, and its query logic cannot be reused by a CLI command or queue consumer.
<!-- RULE END: ARCH-ORG-001 -->

---

<!-- RULE START: ARCH-EXT-001 -->
## Rule ARCH-EXT-001: Extend, Don't Modify Core

**Domain**: Architecture
**Severity**: High
**Scope**: file

### Trigger
When a task requires changing behavior of a vendor/core class, and the proposed change involves directly editing the vendor file or copying it into the project.

### Statement
Behavior changes to vendor or core classes must use the framework's extension mechanism (plugin, preference, event observer, layout override). Direct modification of vendor files or copy-paste of vendor classes into the project is forbidden.

### Violation (bad)
```php
// Directly editing vendor file or copying it
// vendor/magento/module-sales/Model/Order.php -- modified line 234
public function canCancel()
{
    // CUSTOM: added check for custom status
    if ($this->getStatus() === 'custom_hold') {
        return false;
    }
    return parent::canCancel();
}
```

### Pass (good)
```php
// Plugin on the concrete class
class CanCancelPlugin
{
    public function afterCanCancel(Order $subject, bool $result): bool
    {
        if ($subject->getStatus() === 'custom_hold') {
            return false;
        }
        return $result;
    }
}
```

### Enforcement
Static analysis (ENF-POST-007) -- Magento Coding Standard flags direct core modifications. Per-slice findings table (ENF-POST-006). Code review.

### Rationale
Direct core modifications are lost on composer update. Extension-based changes survive upgrades and make customizations discoverable.
<!-- RULE END: ARCH-EXT-001 -->

---

<!-- RULE START: ARCH-DI-001 -->
## Rule ARCH-DI-001: Constructor Injection Over Direct Instantiation

**Domain**: Architecture
**Severity**: Critical
**Scope**: file

### Trigger
When a class constructor or method body contains `new SomeClass(` where SomeClass is a service, repository, handler, or factory -- not a DTO, value object, or exception.

### Statement
Dependencies must be received via constructor injection typed to an interface. Direct instantiation (`new`) is permitted only for DTOs, value objects, exceptions, and test doubles.

### Violation (bad)
```php
class OrderProcessor
{
    public function process(int $orderId): void
    {
        $repo = new OrderRepository($this->connection);
        $order = $repo->getById($orderId);
    }
}
```

### Pass (good)
```php
class OrderProcessor
{
    public function __construct(
        private readonly OrderRepositoryInterface $orderRepository
    ) {}

    public function process(int $orderId): void
    {
        $order = $this->orderRepository->getById($orderId);
    }
}
```

### Enforcement
Magento Coding Standard PHPCS (ENF-POST-007) flags direct ObjectManager usage. PHPStan custom rule flags `new` on injectable types. Per-slice findings table (ENF-POST-006) must quote constructor params.

### Rationale
Direct instantiation hides dependencies, breaks testability, and bypasses DI container configuration (preferences, plugins, proxies).
<!-- RULE END: ARCH-DI-001 -->

---

<!-- RULE START: ARCH-CONST-001 -->
## Rule ARCH-CONST-001: Named Constants for Business Rules

**Domain**: Architecture
**Severity**: High
**Scope**: file

### Trigger
When a literal number, string, or ID appears in a conditional, comparison, or assignment that encodes business logic (threshold, group ID, status value, prefix, flag).

### Statement
Every business-logic literal must be a named constant with a comment referencing the business requirement it encodes. If the value varies by environment or store, it must be sourced from configuration (see ENF-SYS-004).

### Violation (bad)
```php
if ($order->getItemCount() > 5) {       // magic number -- what is 5?
    $this->applyBulkDiscount($order);
}

if ($customer->getGroupId() === 4) {     // magic number -- which group is 4?
    return true;
}
```

### Pass (good)
```php
/** Minimum item count for bulk discount eligibility (BUS-REQ-042) */
private const BULK_DISCOUNT_MIN_ITEMS = 5;

/** Wholesale customer group ID (configured in admin > Customers > Groups) */
private const WHOLESALE_GROUP_ID = 4;

if ($order->getItemCount() > self::BULK_DISCOUNT_MIN_ITEMS) {
    $this->applyBulkDiscount($order);
}

if ($customer->getGroupId() === self::WHOLESALE_GROUP_ID) {
    return true;
}
```

### Enforcement
PHPMD magic number detection (ENF-POST-007). Per-slice findings table (ENF-POST-006) must flag any business-logic literal.

### Rationale
Magic values obscure intent, make maintenance error-prone, and create implicit dependencies between business rules and code. Named constants with documented origins ensure traceability and safe modification.
<!-- RULE END: ARCH-CONST-001 -->

---

<!-- RULE START: ARCH-SSOT-001 -->
## Rule ARCH-SSOT-001: Single Source of Truth for Derived Views

**Domain**: Architecture
**Severity**: Critical
**Scope**: module

### Trigger
When a feature produces data visible through multiple channels (REST API total segments, GraphQL response fields, frontend template blocks, quote extension attributes) and the implementation writes the same value to two or more storage locations independently.

### Statement
Multi-channel features must choose one canonical storage location for each computed value. All secondary views must derive from the canonical source during each computation cycle. Never write the same value to two locations independently.

### Violation (bad)
```php
// Totals collector sets discount in Total object
$total->setTotalAmount('custom_discount', -$discount);

// SEPARATELY, a GraphQL resolver computes and sets the same discount on extension attribute
// from a DIFFERENT code path -- no shared source
$quote->getExtensionAttributes()->setCustomDiscount(
    $this->recalculateDiscount($quote) // independent calculation -- can diverge
);
```

### Pass (good)
```php
// Totals collector is the canonical source -- sets both from one computation
$discount = $this->calculateDiscount($quote);
$total->setTotalAmount('custom_discount', -$discount);
$address->getExtensionAttributes()->setCustomDiscount($discount);

// GraphQL resolver READS from the canonical source, never recomputes
public function resolve(/* ... */): array
{
    $totals = $this->cartTotalRepository->get($cartId);
    return ['custom_discount' => $totals->getTotalAmount('custom_discount')];
}
```

### Required declaration
Before implementing any multi-channel feature, declare:
```
Canonical source: [location]
REST reads from: [X]
GraphQL reads from: [Y]
Frontend reads from: [Z]
All derive from [canonical source] via [mechanism]
```

### Enforcement
Phase A call-path declaration must name the canonical source. Per-slice findings table (ENF-POST-006) must verify all channels read from the same source.

### Rationale
Independent population of the same value in multiple locations creates stale data when one location is updated but another isn't, inconsistent behavior between REST and GraphQL, and cleanup/reversal bugs where one location is cleared but the other retains stale data.
<!-- RULE END: ARCH-SSOT-001 -->