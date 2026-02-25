# Core Coding Principles

These principles apply globally to all code in this codebase. The focus below is on **project-specific enforcement actions** — the principles themselves (DRY, SOLID, KISS, Composition) are assumed knowledge.

## DRY

- **Action**: Before writing new code, search the existing codebase for similar implementations
- **Action**: When encountering duplicate code, consolidate it immediately
- Common functionality must exist in one location only

## SOLID

- **SRP Action**: If describing a class requires "and", it likely violates SRP — split it
- **Open/Closed Action**: Extend behavior through new classes, not by modifying existing ones
- **Liskov Action**: Ensure subclasses can replace parent classes without altering correctness
- **ISP Action**: Split large interfaces into smaller, role-specific ones
- **DI Action**: Inject dependencies through constructors/methods; use interfaces/abstractions

## KISS

- **Action**: If a solution feels complex, step back and find a simpler approach
- Do not add complexity for hypothetical future needs

## Composition Over Inheritance

- **Action**: Before creating inheritance hierarchies, consider if composition achieves the same goal with less coupling
- Prefer "has-a" over "is-a" relationships
