# Phaselock — Contributing Guide

How rules and guidance are added to this knowledge base.

## Authority model

All rules originate from **explicit human intent**. The AI acts as a structural assistant — it may format rules, assign IDs, apply metadata, and place rules in the correct location, but it may **not** invent rules, infer unstated constraints, or merge/split rules without instruction.

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

Every rule **must** be wrapped in START/END markers and include metadata. Use this template:

```md
<!-- RULE START: PREFIX-NAME-NNN -->
## Rule PREFIX-NAME-NNN: Short Title

**Domain**: Domain Name  
**Severity**: Critical | High | Medium | Low

### Statement
What must or must not be done.

### Example
Code example (if applicable).

### Action
What the developer/agent should do in practice.

### Rationale
Why this rule exists.
<!-- RULE END: PREFIX-NAME-NNN -->
```

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
4. Commit both files together — a doc without a nav entry is not a valid commit

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
