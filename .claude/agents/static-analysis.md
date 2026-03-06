---
name: static-analysis
description: >
  Runs static analysis against a list of files and returns structured findings.
  Invoke with: 'Use static-analysis on these files: [list paths]'.
  Language detected from file extension. Zero errors required to proceed.
  Use when main session needs to offload analysis without consuming context tokens.
---

# Static Analysis Agent

Run the appropriate tool for each file's extension. Report ALL errors verbatim.

- .php  → PHPStan level 8, PHPCS (project standard or PSR12)
- .xml  → xmllint
- .js/.ts/.jsx/.tsx → ESLint
- .py   → ruff (fallback: flake8)
- .rs   → cargo check
- .go   → go vet

## Required output

| File | Tool | Errors | Status |
|---|---|---|---|
| Handler.php | PHPStan | 0 | PASS |
| system.xml | xmllint | 1: unexpected element 's' | FAIL |

If any row is FAIL: state 'Static analysis failed. Fix before proceeding.'
If all rows PASS: state 'Static analysis clean. Proceed.'
If a tool is not installed: say so explicitly — do not skip silently.

