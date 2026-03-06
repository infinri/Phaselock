#!/bin/bash
# Universal validation hook — routes by file extension.
# PostToolUse: fires after every Write/Edit/MultiEdit.
# Exit non-zero = Claude Code injects error into context. Must fix before continuing.

FILE=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

if [ -z "$FILE" ]; then exit 0; fi

# Detect project root (walk up from FILE until a known marker is found)
PROJECT_ROOT=$(python3 -c "
import os, sys
markers = ['composer.json','package.json','Cargo.toml','go.mod','pyproject.toml','.git']
path = os.path.abspath('$FILE')
while path != '/':
    path = os.path.dirname(path)
    if any(os.path.exists(os.path.join(path, m)) for m in markers):
        print(path); sys.exit(0)
print('')
" 2>/dev/null)

FAILED=0

# ─── PHP ───────────────────────────────────────────────────────────────────
if [[ "$FILE" == *.php ]]; then

  LEVEL=8
  [ -f "$PROJECT_ROOT/.claude/phpstan-level" ] && LEVEL=$(cat "$PROJECT_ROOT/.claude/phpstan-level")

  PHPSTAN=""
  [ -f "$PROJECT_ROOT/vendor/bin/phpstan" ] && PHPSTAN="$PROJECT_ROOT/vendor/bin/phpstan"
  command -v phpstan &>/dev/null && [ -z "$PHPSTAN" ] && PHPSTAN="phpstan"

  if [ -n "$PHPSTAN" ]; then
    echo "=== PHPStan (level $LEVEL) ==="
    "$PHPSTAN" analyse "$FILE" --level="$LEVEL" --no-progress 2>&1
    [ $? -ne 0 ] && FAILED=1
  else
    echo "WARNING: PHPStan not found — install: composer require --dev phpstan/phpstan"
  fi

  STANDARD="PSR12"
  [ -f "$PROJECT_ROOT/.claude/phpcs-standard" ] && STANDARD=$(cat "$PROJECT_ROOT/.claude/phpcs-standard")

  PHPCS=""
  [ -f "$PROJECT_ROOT/vendor/bin/phpcs" ] && PHPCS="$PROJECT_ROOT/vendor/bin/phpcs"
  command -v phpcs &>/dev/null && [ -z "$PHPCS" ] && PHPCS="phpcs"

  if [ -n "$PHPCS" ]; then
    echo "=== PHPCS ($STANDARD) ==="
    "$PHPCS" "$FILE" --standard="$STANDARD" --report=summary 2>&1
    [ $? -ne 0 ] && FAILED=1
  else
    echo "WARNING: PHPCS not found — install: composer require --dev squizlabs/php_codesniffer"
  fi

fi

# ─── XML ───────────────────────────────────────────────────────────────────
if [[ "$FILE" == *.xml ]]; then
  if command -v xmllint &>/dev/null; then
    echo "=== xmllint ==="
    xmllint --noout "$FILE" 2>&1
    [ $? -ne 0 ] && FAILED=1
  else
    echo "WARNING: xmllint not found — install: sudo apt install libxml2-utils"
  fi
fi

# ─── JavaScript / TypeScript ───────────────────────────────────────────────
if [[ "$FILE" == *.js || "$FILE" == *.ts || "$FILE" == *.jsx || "$FILE" == *.tsx ]]; then
  ESLINT=""
  [ -f "$PROJECT_ROOT/node_modules/.bin/eslint" ] && ESLINT="$PROJECT_ROOT/node_modules/.bin/eslint"
  command -v eslint &>/dev/null && [ -z "$ESLINT" ] && ESLINT="eslint"

  if [ -n "$ESLINT" ]; then
    echo "=== ESLint ==="
    "$ESLINT" "$FILE" 2>&1
    [ $? -ne 0 ] && FAILED=1
  else
    echo "WARNING: ESLint not found — install: npm install --save-dev eslint"
  fi
fi

# ─── Python ────────────────────────────────────────────────────────────────
if [[ "$FILE" == *.py ]]; then
  if command -v ruff &>/dev/null; then
    echo "=== Ruff ==="
    ruff check "$FILE" 2>&1
    [ $? -ne 0 ] && FAILED=1
  elif command -v flake8 &>/dev/null; then
    echo "=== Flake8 ==="
    flake8 "$FILE" 2>&1
    [ $? -ne 0 ] && FAILED=1
  else
    echo "WARNING: No Python linter found — install: pip install ruff"
  fi
fi

# ─── Rust ──────────────────────────────────────────────────────────────────
if [[ "$FILE" == *.rs ]] && command -v cargo &>/dev/null && [ -n "$PROJECT_ROOT" ]; then
  echo "=== cargo check ==="
  (cd "$PROJECT_ROOT" && cargo check 2>&1)
  [ $? -ne 0 ] && FAILED=1
fi

# ─── Go ────────────────────────────────────────────────────────────────────
if [[ "$FILE" == *.go ]] && command -v go &>/dev/null; then
  echo "=== go vet ==="
  go vet "$FILE" 2>&1
  [ $? -ne 0 ] && FAILED=1
fi

# ─── GraphQL Schema ────────────────────────────────────────────────────────
if [[ "$FILE" == *.graphqls ]]; then
  echo "=== GraphQL PHP class reference check ==="
  GRAPHQL_FAILED=0
  while IFS= read -r classname; do
    [ -z "$classname" ] && continue
    # Convert namespace separators (\\) to path separators (/)
    CLASSPATH=$(echo "$classname" | sed 's|\\\\|/|g; s|\\|/|g')
    BASENAME=$(basename "$CLASSPATH")
    DIRPART=$(dirname "$CLASSPATH")
    if [ -n "$PROJECT_ROOT" ]; then
      if ! find "$PROJECT_ROOT" -type f -name "${BASENAME}.php" 2>/dev/null | grep -qF "$DIRPART"; then
        echo "MISSING: Class '$classname' referenced in $(basename "$FILE") does not exist on disk."
        echo "         Expected at: ${CLASSPATH}.php"
        GRAPHQL_FAILED=1
      fi
    fi
  done < <(grep -oE '(class|cacheIdentity): *"[^"]*"' "$FILE" 2>/dev/null | \
           sed 's/.*: *"//; s/"$//' | \
           grep -v '^$')
  [ $GRAPHQL_FAILED -ne 0 ] && FAILED=1
fi

if [ $FAILED -ne 0 ]; then
  echo ""
  echo "GATE FAILED: Fix all errors above before proceeding."
  exit 1
fi

exit 0
