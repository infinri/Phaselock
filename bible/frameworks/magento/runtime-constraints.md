# Magento 2 Runtime Constraints

## Purpose

This document defines **Magento 2-specific runtime constraints** that provide framework-specific implementation guidance for the generic enforcement rules in `enforcement/system-dynamics.md`, `enforcement/security-boundaries.md`, and `enforcement/operational-claims.md`.

These are the Magento 2 answers to questions those generic rules force the AI to ask.

---

## System Dynamics — Magento 2 Specifics

### Temporal Truth Sources in Magento (applies to ENF-SYS-002)

<!-- RULE START: FW-M2-RT-001 -->
## Rule FW-M2-RT-001: MSI Salability Is Decided at Order Placement

**Domain**: Frameworks / Magento 2  
**Severity**: Critical

### Statement
When Magento's Multi-Source Inventory (MSI) system allows an order to be placed, salability has been authoritatively decided. Post-placement code must NOT re-evaluate salability.

Authoritative decision points for common Magento facts:

| Fact | Authoritative Event | Re-evaluation Valid? |
|------|---------------------|---------------------|
| Product salability | `sales_order_place_after` | No — order placement is the authority |
| Payment authorization | `sales_order_payment_pay` | No — payment gateway is the authority |
| Coupon validity | `sales_order_place_after` | No — validated at cart-to-order transition |
| Stock assignment (source) | MSI source selection at shipment | No — re-selecting sources contradicts allocation |
| Credit memo eligibility | `sales_order_creditmemo_save_after` | No — Magento validates qty constraints |

### Action
If post-placement code checks `StockRegistryInterface::getStockStatusBySku()` or equivalent to decide whether to process an already-placed order, it is a constraint violation. The order was placed — MSI already said yes.

### Rationale
"Respect MSI" means "trust MSI's placement decision," not "re-evaluate MSI after the fact." Re-checking salability post-placement produces false negatives when stock levels change between placement and processing, causing valid orders to be silently skipped.
<!-- RULE END: FW-M2-RT-001 -->

---

### Magento Order State Machine (applies to ENF-SYS-003)

<!-- RULE START: FW-M2-RT-002 -->
## Rule FW-M2-RT-002: Magento Order State Transitions Must Be Declared

**Domain**: Frameworks / Magento 2  
**Severity**: Critical

### Statement
When building features that depend on or react to order state changes, the AI must declare which Magento order states and statuses are involved and how transitions work.

Key Magento order states and their semantics:

| State | Meaning | Typical Triggers |
|-------|---------|------------------|
| `new` | Order created, not yet processed | `sales_order_place_after` |
| `pending_payment` | Awaiting payment confirmation | Offline/deferred payment methods |
| `processing` | Payment received, fulfillment in progress | `sales_order_payment_pay` |
| `complete` | Shipped and invoiced | All items shipped + invoiced |
| `closed` | Fully refunded | Credit memo covers all items |
| `canceled` | Order canceled | Admin action or payment failure |
| `holded` | Manually held | Admin action |
| `payment_review` | Fraud/payment review | Gateway fraud detection |

Transitions that commonly trigger custom module logic:
- `new` / `pending_payment` → `processing` (payment confirmed — create reservations)
- `processing` → `canceled` (cancel — release reservations)
- `processing` → `closed` (full refund — release reservations)
- Partial refund does NOT change state to `closed`

### Action
Any feature that reacts to order state changes must explicitly list which transitions it handles and which it ignores. Silent assumptions about state transitions are a constraint violation.

### Rationale
Magento's order state machine has non-obvious behaviors: partial refunds don't change state, `pending_payment` may or may not transition to `processing` depending on payment method, and custom states can be added by third-party modules. Explicit declaration prevents the AI from assuming a simplified state model.
<!-- RULE END: FW-M2-RT-002 -->

---

### Magento Configuration Patterns (applies to ENF-SYS-004)

<!-- RULE START: FW-M2-RT-003 -->
## Rule FW-M2-RT-003: Policy Configuration Must Use system.xml + ScopeConfigInterface

**Domain**: Frameworks / Magento 2  
**Severity**: High

### Statement
When ENF-SYS-004 classifies a value as store-specific policy, the Magento 2 implementation must:

1. Declare the setting in `etc/adminhtml/system.xml` with appropriate:
   - Section, group, field structure
   - Source model (if multiselect or dropdown)
   - `showInDefault`, `showInWebsite`, `showInStore` scope flags
2. Set the default value in `etc/config.xml`
3. Read the value via `Magento\Framework\App\Config\ScopeConfigInterface::getValue()` with appropriate scope (`ScopeInterface::SCOPE_STORE` or `SCOPE_WEBSITE`)
4. Encapsulate config reads in a dedicated Config model class (not inline `scopeConfig->getValue()` calls scattered through business logic)

### Example
```php
// ✅ Correct: dedicated config class
class ReservationConfig
{
    public function __construct(
        private readonly ScopeConfigInterface $scopeConfig
    ) {}

    public function getSkipStates(): array
    {
        $value = $this->scopeConfig->getValue(
            'custom_reservation/general/skip_states',
            ScopeInterface::SCOPE_STORE
        );
        return $value ? explode(',', $value) : [];
    }
}

// ❌ Violation: inline config read in business logic
$skipStates = $this->scopeConfig->getValue('custom_reservation/general/skip_states');
```

### Action
Hardcoded business logic values in Magento modules are a constraint violation when the value is store-dependent. The AI must produce `system.xml`, `config.xml`, source model (if needed), and a Config class.

### Rationale
Magento's multi-store architecture requires per-store configuration. `ScopeConfigInterface` with proper scope resolution is the only mechanism that correctly handles default → website → store fallback. Inline reads without scope are unreliable in multi-website setups.
<!-- RULE END: FW-M2-RT-003 -->

---

## Security — Magento 2 Specifics

### Access Control Patterns (applies to ENF-SEC-001)

<!-- RULE START: FW-M2-RT-004 -->
## Rule FW-M2-RT-004: Magento Endpoint Authorization Patterns

**Domain**: Frameworks / Magento 2  
**Severity**: Critical

### Statement
When ENF-SEC-001 requires an Access Boundary Declaration, the Magento 2 implementation must use these specific mechanisms:

**REST endpoints (`webapi.xml`)**:
```xml
<route url="/V1/example/:id" method="GET">
    <service class="Vendor\Module\Api\ExampleInterface" method="getById"/>
    <resources>
        <resource ref="Magento_Sales::sales"/>  <!-- ACL resource -->
    </resources>
</route>
```
- `resource ref="anonymous"` requires explicit justification
- `resource ref="self"` restricts to authenticated customer accessing own data

**GraphQL resolvers**:
```php
$userId = $context->getUserId();
$userType = $context->getUserType();

// Admin/integration: unrestricted
if ($userType === UserContextInterface::USER_TYPE_ADMIN
    || $userType === UserContextInterface::USER_TYPE_INTEGRATION) {
    return;
}

// Anonymous: deny
if (!$userId || $userType !== UserContextInterface::USER_TYPE_CUSTOMER) {
    throw new GraphQlAuthorizationException(__('Not authorized.'));
}

// Customer: verify ownership
if ((int) $order->getCustomerId() !== (int) $userId) {
    throw new GraphQlAuthorizationException(__('Not authorized for this resource.'));
}
```

**Admin controllers**:
```php
protected function _isAllowed(): bool
{
    return $this->_authorization->isAllowed('Vendor_Module::resource_id');
}
```

**ACL resource declaration** (`etc/acl.xml`):
```xml
<resource id="Vendor_Module::resource_id" title="Resource Title"
          sortOrder="10">
</resource>
```

### Action
- REST endpoints without `<resource>` are a constraint violation
- GraphQL resolvers without `$context->getUserType()` checks are a constraint violation
- Admin controllers without `_isAllowed()` are a constraint violation
- Customer-facing endpoints without ownership verification are a constraint violation

### Rationale
Magento has four distinct caller types (admin, customer, integration, guest), each with different authorization mechanisms. The framework does NOT apply authorization automatically for GraphQL — resolvers must check explicitly. REST uses ACL enforcement via `webapi.xml`, but the developer must choose the correct resource.
<!-- RULE END: FW-M2-RT-004 -->

---

## Operations — Magento 2 Specifics

### Queue Infrastructure (applies to ENF-OPS-001, ENF-OPS-002)

<!-- RULE START: FW-M2-RT-005 -->
## Rule FW-M2-RT-005: Magento Message Queue Configuration Completeness

**Domain**: Frameworks / Magento 2  
**Severity**: High

### Statement
When ENF-OPS-002 requires complete queue infrastructure, the Magento 2 implementation must declare:

**Required XML configuration files**:

1. `etc/communication.xml` — Topic and message schema:
```xml
<topic name="vendor.module.process"
       request="Vendor\Module\Api\Data\MessageInterface"/>
```

2. `etc/queue_publisher.xml` — Publisher binding:
```xml
<publisher topic="vendor.module.process">
    <connection name="amqp" exchange="vendor.module.exchange" />
</publisher>
```

3. `etc/queue_topology.xml` — Exchange, bindings, DLQ:
```xml
<!-- Dead-letter exchange -->
<exchange name="vendor.module.dlx" type="topic" connection="amqp">
    <binding id="vendor.module.dlq.binding"
             topic="vendor.module.process"
             destinationType="queue"
             destination="vendor.module.dlq"/>
</exchange>
<!-- Primary exchange with DLX routing -->
<exchange name="vendor.module.exchange" type="topic" connection="amqp">
    <binding id="vendor.module.binding"
             topic="vendor.module.process"
             destinationType="queue"
             destination="vendor.module.queue">
        <arguments>
            <argument name="x-dead-letter-exchange" xsi:type="string">vendor.module.dlx</argument>
            <argument name="x-delivery-limit" xsi:type="number">3</argument>
            <argument name="x-message-ttl" xsi:type="number">30000</argument>
        </arguments>
    </binding>
</exchange>
```

4. `etc/queue_consumer.xml` — Consumer handler:
```xml
<consumer name="vendor.module.consumer"
          queue="vendor.module.queue"
          handler="Vendor\Module\Model\Consumer\Handler::process"
          connection="amqp"
          maxMessages="1000"/>
```

### Action
Delivering a Magento queue-based feature without all four XML files AND a DLQ exchange is a constraint violation.

### Rationale
Magento's queue framework splits configuration across four XML files. Missing any one of them causes silent failures: messages published but never consumed, consumers registered but never bound, or failed messages silently dropped without DLQ routing. The split is non-obvious and a common source of "it works in dev but not in production" bugs.
<!-- RULE END: FW-M2-RT-005 -->

---

### Multi-Website Stock Resolution (applies to ENF-SYS-001, ENF-SYS-002)

<!-- RULE START: FW-M2-RT-006 -->
## Rule FW-M2-RT-006: MSI Website-to-Stock Mapping Must Be Declared

**Domain**: Frameworks / Magento 2  
**Severity**: High

### Statement
In Magento MSI, stock is resolved per website via the `inventory_stock_sales_channel` table. Features that interact with inventory must declare:

1. **Which stock is being referenced**: Default stock (single-source) or MSI stock (multi-source)?
2. **How stock is resolved**: Via `StockResolverInterface` using the sales channel, or via `StockRegistryInterface` (legacy, single-stock only)?
3. **Website dependency**: Does this feature operate correctly in a multi-website setup where different websites map to different stocks?

### Action
If a feature uses `StockRegistryInterface` in a multi-source inventory environment, it must justify why legacy single-stock resolution is acceptable. In MSI-enabled installations, `StockResolverInterface` or `GetProductSalableQtyInterface` should be used with the correct stock ID for the website.

### Rationale
MSI decouples stock from websites. A product can be salable on Website A (mapped to Stock 1) but not on Website B (mapped to Stock 2). Code that assumes a single global stock will produce incorrect results in multi-website, multi-stock configurations — which is the standard MSI setup.
<!-- RULE END: FW-M2-RT-006 -->
