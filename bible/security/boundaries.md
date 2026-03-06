# Security Boundaries

Universal security rules for all projects and frameworks.
Framework-specific patterns live in bible/frameworks/.

<!-- RULE START: SEC-UNI-001 -->
## Rule SEC-UNI-001: Authentication Is Not Authorization

Proving a caller is authenticated does not prove they have rights to a specific resource.
Both checks are always required. An endpoint that passes auth but skips ownership
verification allows any authenticated user to access any other user's data.
<!-- RULE END: SEC-UNI-001 -->

<!-- RULE START: SEC-UNI-002 -->
## Rule SEC-UNI-002: Ownership Verification Must Be In Code

Ownership rules declared in design documents are not enforcement.
The implementation must contain a code path that compares authenticated caller identity
to resource owner identity. If the comparison fails, the request is rejected.
<!-- RULE END: SEC-UNI-002 -->

<!-- RULE START: SEC-UNI-003 -->
## Rule SEC-UNI-003: Explicit Response Field Selection

API responses must not include sensitive fields by default.
Every response field must be explicitly chosen — not included by returning the full entity.
Internal IDs, credentials, PII, and internal state are excluded unless the endpoint
specifically requires them and the caller has rights to receive them.
<!-- RULE END: SEC-UNI-003 -->

<!-- RULE START: SEC-UNI-004 -->
## Rule SEC-UNI-004: No Secrets in Code

API keys, tokens, passwords, and secrets are never hardcoded.
Read from environment variables or a secrets manager.
Config files that may be committed must never contain secrets, even as defaults.
<!-- RULE END: SEC-UNI-004 -->
