# AI Workflow Checklist

## Purpose

This document defines **guidelines and checklists for AI-assisted development**.

It ensures AI agent actions are consistent, safe, and aligned with project standards.

---

## Code Modification Approach

- **Minimal Edits**: Make the smallest change that solves the problem
- **Focused Changes**: One concern per edit/commit
- **Existing Patterns**: Follow patterns already established in the codebase
- **No Placeholders**: Always provide complete, runnable code
- **Action**: Use file editing tools directly; avoid outputting code in chat unless requested

---

## Investigation & Analysis

- **Search First**: Search the codebase for existing implementations before writing new code
- **Read Context**: Read surrounding code to understand context
- **Verify Assumptions**: Don't assume; check the actual codebase
- **Action**: Always search for similar code before implementing new functionality

---

## File Operations

- **No Clutter**: Don't create unnecessary files or directories
- **Existing Files First**: Prefer modifying existing files over creating new ones
- **Proper Structure**: Follow project structure conventions
- **Action**: Check if a file exists before creating; use existing organizational patterns

---

## Communication

- **Terse & Direct**: Be concise; avoid verbose explanations
- **Fact-Based**: Make no ungrounded assertions
- **Implementation Over Suggestion**: Implement changes directly rather than suggesting
- **Action**: Show, don't tell - use tools to make changes rather than describing them

---

## Minimal Code Generation

- **Absolute Minimalism**: Always use the fewest lines, expressions, and operations to accomplish a task
- **Single Expression Preference**: Favor a single expression over multiple statements whenever feasible
- **No Redundant Assignments**: Avoid temporary variables or steps that can be combined
- **Inline Logic Over Expansion**: Merge conditionals, computations, and string interpolation inline if it reduces code size without harming clarity
- **Compact but Clear**: Prioritize minimizing code while ensuring output remains understandable and correct
- **Avoid Boilerplate**: Skip optional wrappers, comments, or structural repetition unless essential for correctness or maintainability
- **Action**: Every generated snippet should be audited for absolute code reduction while preserving functionality and readability

---

## Pre-Implementation Checklist

Before writing any code, verify:

- [ ] Similar functionality doesn't already exist (search first)
- [ ] Change is in the right location (centralized, follows project structure)
- [ ] Solution is the simplest that works (KISS)
- [ ] Code is reusable and doesn't duplicate existing logic (DRY)
- [ ] Design uses composition/injection over inheritance where appropriate
- [ ] Each component has a single, clear responsibility (SRP)
- [ ] New code extends rather than modifies existing stable code (Open/Closed)
- [ ] Algorithm complexity is appropriate for the use case (Big O)
- [ ] Dependencies are injected, not instantiated (Dependency Inversion)
- [ ] Tests are planned or implemented
- [ ] **Phased Implementation Protocol completed** — if the task involves plugins, observers, validation, or entity retrieval, all phases (A: call-path, B: domain invariant, C: seam justification, D: system dynamics when triggered) must be individually presented and approved before code generation begins. See `ENF-GATE-001`–`005` in [enforcement/reasoning-discipline.md](enforcement/reasoning-discipline.md).
- [ ] **Test skeletons generated and approved** — test skeletons with specific assertions must be generated and reviewed BEFORE implementation code. See `ENF-GATE-007`.
- [ ] **Code generation is sliced** — implementation must be generated in dependency-ordered slices (schema → persistence → domain → integration → exposure → wiring), each with self-validation and human gate. See `ENF-GATE-006`.
- [ ] **Post-generation verification planned** — structured findings table (`ENF-POST-006`), static analysis (`ENF-POST-007`), and operational proof traces (`ENF-POST-008`) must be produced per slice.

**Core philosophy**: Write code once in the right place, make it reusable, keep it simple, and design for extension rather than modification.
