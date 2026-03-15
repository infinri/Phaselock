# Phaselock -- Contributing Guide

How rules and guidance are added to this knowledge base.

## Authority model

All rules originate from **explicit human intent**. The AI acts as a structural assistant -- it may format rules, assign IDs, apply metadata, and place rules in the correct location, but it may **not** invent rules, infer unstated constraints, or merge/split rules without instruction.

## When to add a rule

Add a rule when:
- a mistake has occurred more than once
- a constraint is non-obvious
- a framework behavior is surprising
- violating the guidance causes real risk
- architectural intent must be preserved

Do **not** add rules for obvious language syntax, personal style preferences, temporary experiments, or speculative best practices.

## Rule placement

Place rules under the appropriate domain directory in `bible/`:

- Database rules → `bible/database/`
- Security rules → `bible/security/`
- Architecture rules → `bible/architecture/`
- Framework rules → `bible/frameworks/`

If a rule spans multiple domains, place it in the most specific domain and cross-reference from others.

## Rule format

Every rule **must** be wrapped in START/END markers and use the enforceable rule schema. Rules must be concrete enough for an AI agent to make a binary pass/fail decision.

### Bible rules (code pattern rules)

```md
<!-- RULE START: PREFIX-NAME-NNN -->
## Rule PREFIX-NAME-NNN: Short Title

**Domain**: Domain Name
**Severity**: Critical | High | Medium | Low
**Scope**: file | module | slice | PR

### Trigger
When {specific, measurable condition that activates this rule}.

### Statement
{Concrete requirement -- 1-2 sentences, no abstractions.}

### Violation (bad)
```lang
// concrete code that breaks this rule
```

### Pass (good)
```lang
// concrete code that satisfies this rule
```

### Enforcement
{Which gate, hook, or verification step catches this violation.}

### Rationale
{Brief why -- one paragraph max.}
<!-- RULE END: PREFIX-NAME-NNN -->
```

### Enforcement rules (AI process rules)

Same schema, but violation/pass examples show AI behavior/output instead of application code:

```md
### Violation (bad)
AI produces a plugin without declaring which execution contexts it covers.
Output: "I'll create an after plugin on CartRepositoryInterface::save()"
-- no mention of REST, GraphQL, admin, CLI coverage.

### Pass (good)
AI lists all contexts:
"Plugin targets QuoteRepository::save() (concrete).
Covers: frontend (session save), REST (POST /V1/carts), GraphQL (setPaymentMethod mutation).
Does NOT cover: admin (uses AdminQuoteRepository -- separate class). Gap documented."
```

### What makes a rule enforceable

| Field | Required | Purpose |
|-------|----------|---------|
| Trigger | Yes | When does this rule activate? Must be a specific, observable condition. |
| Statement | Yes | What is required? Must enable binary pass/fail -- no "consider" or "be aware of." |
| Violation example | Yes | Concrete bad code/output. The agent sees this and knows it fails. |
| Pass example | Yes | Concrete good code/output. The agent sees this and knows it passes. |
| Enforcement | Yes | What mechanically catches violations (gate, hook, static analysis, findings table). |
| Scope | Yes | What is being checked: file, module, slice, PR, or session. |

Rules that use words like "consider," "be aware of," "where appropriate," or "when possible" are **principles, not rules**. Principles belong in `rules/CORE_PRINCIPLES.md`. Rules must be binary.

### Rule ID conventions

- Format: `PREFIX-NAME-NNN` (e.g., `DB-SQL-001`, `ARCH-DI-001`)
- Prefix must match the domain (see [OVERVIEW.md](OVERVIEW.md) Quick Reference table)
- Numbers are zero-padded to 3 digits
- IDs must be unique across the entire knowledge base

### After adding a rule

1. Update [SKILL.md](SKILL.md) task navigation if rule IDs changed
2. Update [MANIFEST.md](MANIFEST.md) if a new domain was added
3. Update [OVERVIEW.md](OVERVIEW.md) file listings with new rule IDs

---

## The dark-file rule

A Bible document is ACTIVE only when:
1. The file exists in the correct directory
2. The .claude/CLAUDE.md navigation map has an entry pointing to it
3. The entry specifies WHEN to load it (which phase or condition)

A file that exists but has no CLAUDE.md navigation entry is DARK.
Dark files are never loaded and their rules are never enforced.

### When adding a new Bible document
1. Create the file in the correct bible/ subdirectory
2. Open .claude/CLAUDE.md
3. Add the document under the correct 'What to load and when' section
4. Commit both files together -- a doc without a nav entry is not a valid commit

### When adding a new enforcement rule
1. Add the rule to the appropriate enforcement/ document
2. Update SKILL.md task navigation if the rule affects routing
3. If the rule references a new Bible section, that section must exist
4. Cross-reference both directions: rule ID → Bible section, Bible section → rule ID

### When adding a new framework or language
1. Create bible/frameworks/{name}/ or bible/languages/{name}/
2. Add at minimum one .md file with enforceable rules
3. Update OVERVIEW.md directory index
4. Update MANIFEST.md multi-domain task examples
5. Add navigation entry to .claude/CLAUDE.md under the relevant phase section
