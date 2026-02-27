# Architecture Principles

## Purpose

This document defines **architectural principles and design patterns** that govern how code is organized, extended, and maintained in this codebase.

These rules ensure consistency, maintainability, and proper separation of concerns.

---

<!-- RULE START: ARCH-ORG-001 -->
## Rule ARCH-ORG-001: Code Organization

**Domain**: Architecture  
**Severity**: High

### Statement
Code must be organized following these principles:

- **Centralized Logic**: Place shared logic in central, reusable components
- **Decoupling**: Minimize dependencies between modules/classes
- **Layered Architecture**: Separate concerns (presentation, business logic, data access)

### Action
Always ask "where is the single best place for this code?"

### Rationale
Centralized, decoupled code is easier to maintain, test, and extend. Scattered logic leads to inconsistencies and bugs.
<!-- RULE END: ARCH-ORG-001 -->

---

<!-- RULE START: ARCH-EXT-001 -->
## Rule ARCH-EXT-001: Extension Points

**Domain**: Architecture  
**Severity**: High

### Statement
Systems must be designed to accept extensions without core modifications:

- **Plugin Architecture**: Design systems to accept extensions without core modifications
- **Interfaces**: Define clear contracts for extensibility
- **Factory Patterns**: Use factories for object creation to enable easy swapping

### Action
When adding features, extend existing systems rather than modifying core code.

### Rationale
Extension-based design preserves stability of existing functionality while allowing new capabilities.
<!-- RULE END: ARCH-EXT-001 -->

---

<!-- RULE START: ARCH-DI-001 -->
## Rule ARCH-DI-001: Dependency Management

**Domain**: Architecture  
**Severity**: Critical

### Statement
Dependencies must be managed through injection, not instantiation:

- **Dependency Injection**: Pass dependencies explicitly, don't create them internally
- **Interface-Based**: Depend on interfaces/abstractions, not concrete implementations
- **Inversion of Control**: Let the framework/container manage object lifecycles

### Action
Never use `new` for dependencies inside classes; inject them.

### Rationale
Dependency injection enables testability, flexibility, and proper separation of concerns. Hard-coded dependencies create tight coupling and make testing difficult.
<!-- RULE END: ARCH-DI-001 -->

---

<!-- RULE START: ARCH-CONST-001 -->
## Rule ARCH-CONST-001: Named Constants for Business Rules

**Domain**: Architecture  
**Severity**: High

### Statement
Every named constant must correspond to a documented business rule. Magic numbers and magic strings are forbidden. Every threshold, group ID, prefix, or flag must be a named constant with a comment referencing the business requirement it encodes.

If the value is environment-specific or configurable, it must be sourced from config, not hardcoded.

### Action
Before hardcoding any threshold, ID, or string literal that encodes business logic, define it as a named constant with a comment that references the business requirement. If the value varies by environment, source it from system configuration.

### Rationale
Magic values obscure intent, make maintenance error-prone, and create implicit dependencies between business rules and code. Named constants with documented origins ensure traceability and safe modification.
<!-- RULE END: ARCH-CONST-001 -->
