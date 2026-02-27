# Security Boundary Enforcement

## Purpose

This document defines **mandatory security reasoning** the AI must satisfy for any feature that exposes data or functionality through an externally accessible interface (REST API, GraphQL, admin UI, storefront, CLI). These rules close the gap between "structurally correct" and "secure by design."

---

<!-- RULE START: ENF-SEC-001 -->
## Rule ENF-SEC-001: Access Boundary Declaration

**Domain**: Security  
**Severity**: Critical

### Statement
Every externally accessible endpoint (REST, GraphQL, admin controller, storefront controller, CLI command) must include a written **Access Boundary Declaration** before implementation. The declaration must answer:

1. **Who can call it?**
   - Anonymous / Guest
   - Authenticated customer (frontend token)
   - Authenticated admin (admin token)
   - Integration (API token)
   - Internal only (queue consumer, cron, CLI)

2. **How is the caller authenticated?**
   - Framework ACL / role-based access control (specify which resource or role)
   - Token-based identity validation (JWT, OAuth, session — specify mechanism)
   - No authentication (public endpoint — must justify why)

3. **What data ownership rules apply?**
   - Does the caller own the requested data? (e.g., customer can only see their own orders)
   - How is ownership verified? (e.g., `order.customer_id === token.customer_id`)
   - What happens if ownership check fails? (403, empty result, exception)

4. **What happens if unauthorized?**
   - REST: HTTP 401/403 with appropriate error message
   - GraphQL: Authorization exception per framework convention
   - Admin/internal UI: redirect or error per framework convention

### Action
Any externally accessible endpoint delivered without an Access Boundary Declaration is a constraint violation.

Specific enforcement rules:
- **REST endpoints**: Must declare an authentication/authorization mechanism. If anonymous access is required, it must be explicitly justified in the declaration.
- **GraphQL resolvers**: Must verify caller identity and type before returning data. Admin/integration types may bypass ownership checks. End-user types must verify data ownership. Anonymous access must be denied unless explicitly justified.
- **Admin/internal controllers**: Must declare ACL or role-based access checks.
- **CLI commands**: Must document that they run with elevated privileges and note any data exposure risks.

> **Framework-specific guidance**: See `bible/frameworks/magento/runtime-constraints.md` for Magento 2 patterns (`webapi.xml`, `$context->getUserId()`, `_isAllowed()`, `GraphQlAuthorizationException`).

### Hard Gate — Ownership Verification Must Exist in Code
The Access Boundary Declaration is necessary but **not sufficient**. The AI must also verify that ownership enforcement is **implemented in the code**, not just written in prose.

For any endpoint where the declaration states ownership rules (e.g., "customer can only see their own orders"):

1. **The implementation MUST contain a code path that compares the authenticated caller's identity to the resource owner's identity** (e.g., `$order->getCustomerId() === $authenticatedUserId`).
2. **If the comparison fails, the endpoint MUST reject the request** — return 403, throw an authorization exception, or return an empty result. It must NOT return the data.
3. **If ownership cannot be verified via the service layer** (e.g., the entity has no owner field, or the relationship is indirect), the endpoint MUST reject access for non-admin callers entirely. Partial security is worse than no access.
4. **"Customer must be logged in" is NOT ownership verification.** Authentication proves identity. Ownership verification proves the authenticated user has a relationship to the specific resource being accessed. Both are required.

The AI must not mark an endpoint as complete if:
- The declaration says "customer can only access their own data"
- But the implementation only checks "customer is authenticated" without comparing IDs

This is the most common security gap in AI-generated code: declaring ownership rules in design but implementing only authentication in code.

### Example

Access Boundary Declaration for `GET /api/v1/orders/:id/reservations`:

```
Who: Admin users with order management role
Auth: Role-based ACL enforced at framework level
Ownership: Admin has unrestricted access to all orders
Unauthorized: 403 Forbidden
```

Access Boundary Declaration for GraphQL `reservations(order_id:)`:

```
Who: Admin (unrestricted), Customer (own orders only), Anonymous (denied)
Auth: Caller identity + type checked in resolver
Ownership: Authenticated user ID must match order.customer_id
Unauthorized: Authorization exception
```

### Rationale
The most common security gap in AI-generated code is not malicious intent — it is omission. The AI builds structurally correct endpoints that work perfectly but forget to ask "who should be allowed to call this?" Adding authorization after the fact is fragile and often incomplete. Forcing the declaration before implementation makes security a first-class design constraint, not an afterthought.
<!-- RULE END: ENF-SEC-001 -->

---

<!-- RULE START: ENF-SEC-002 -->
## Rule ENF-SEC-002: Data Exposure Minimization

**Domain**: Security  
**Severity**: High

### Statement
Every API response (REST or GraphQL) must be reviewed for data exposure. The AI must verify:

1. **No internal IDs leaked unnecessarily**: Entity IDs, database primary keys, and internal references should only be exposed if the consumer needs them.
2. **No sensitive data in default responses**: Customer emails, payment details, addresses, and internal notes must not appear in API responses unless the endpoint is specifically designed for that purpose.
3. **No debug information in production responses**: Stack traces, SQL queries, file paths, and internal error details must never appear in API responses.

### Action
If an API response includes fields that the declared consumer does not need, the AI must justify their inclusion or remove them. Over-exposure of data is a constraint violation.

### Rationale
API responses that return entire entity objects "for convenience" create attack surfaces. Every exposed field is a potential information leak. Minimizing response data reduces the blast radius of any future authorization bypass.
<!-- RULE END: ENF-SEC-002 -->
