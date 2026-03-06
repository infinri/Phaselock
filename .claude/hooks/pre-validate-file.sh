#!/bin/bash
# Pre-write validation hook — validates content BEFORE the file is written.
# PreToolUse: fires before every Write/Edit/MultiEdit.
# Exit non-zero = BLOCKS the write. Errors are injected back into Claude's context.

TMPFILE=""
cleanup() { [ -n "$TMPFILE" ] && rm -f "$TMPFILE"; }
trap cleanup EXIT

# Write the proposed content to a temp file so validators can inspect it.
# Write: uses the `content` field directly.
# Edit:  reconstructs the full file by applying old_string -> new_string.
TMPFILE=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c "
import sys, json, os, tempfile

data = json.load(sys.stdin)
fp = data.get('file_path', '')
if not fp:
    sys.exit(0)

ext = os.path.splitext(fp)[1]

if 'content' in data:
    content = data['content']
elif 'old_string' in data and os.path.exists(fp):
    with open(fp) as f:
        content = f.read()
    content = content.replace(data['old_string'], data.get('new_string', ''), 1)
else:
    sys.exit(0)

tf = tempfile.mktemp(suffix=ext, prefix='claude-preval-', dir='/tmp')
with open(tf, 'w') as f:
    f.write(content)
print(tf)
" 2>/dev/null)

if [ -z "$TMPFILE" ] || [ ! -f "$TMPFILE" ]; then exit 0; fi

FILE=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

# Detect project root
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
    echo "=== PHPStan (level $LEVEL) — pre-write check for $FILE ==="
    # Replace temp path with real path in output so errors are actionable
    "$PHPSTAN" analyse "$TMPFILE" --level="$LEVEL" --no-progress 2>&1 \
      | sed "s|$TMPFILE|$FILE|g"
    [ ${PIPESTATUS[0]} -ne 0 ] && FAILED=1
  else
    echo "WARNING: PHPStan not found — install: composer require --dev phpstan/phpstan"
  fi

fi

# ─── JavaScript / TypeScript ───────────────────────────────────────────────
if [[ "$FILE" == *.js || "$FILE" == *.ts || "$FILE" == *.jsx || "$FILE" == *.tsx ]]; then
  ESLINT=""
  [ -f "$PROJECT_ROOT/node_modules/.bin/eslint" ] && ESLINT="$PROJECT_ROOT/node_modules/.bin/eslint"
  command -v eslint &>/dev/null && [ -z "$ESLINT" ] && ESLINT="eslint"

  if [ -n "$ESLINT" ]; then
    echo "=== ESLint — pre-write check for $FILE ==="
    "$ESLINT" "$TMPFILE" 2>&1 | sed "s|$TMPFILE|$FILE|g"
    [ ${PIPESTATUS[0]} -ne 0 ] && FAILED=1
  else
    echo "WARNING: ESLint not found — install: npm install --save-dev eslint"
  fi
fi

# ─── Python ────────────────────────────────────────────────────────────────
if [[ "$FILE" == *.py ]]; then
  if command -v ruff &>/dev/null; then
    echo "=== Ruff — pre-write check for $FILE ==="
    ruff check "$TMPFILE" 2>&1 | sed "s|$TMPFILE|$FILE|g"
    [ ${PIPESTATUS[0]} -ne 0 ] && FAILED=1
  elif command -v flake8 &>/dev/null; then
    echo "=== Flake8 — pre-write check for $FILE ==="
    flake8 "$TMPFILE" 2>&1 | sed "s|$TMPFILE|$FILE|g"
    [ ${PIPESTATUS[0]} -ne 0 ] && FAILED=1
  fi
fi

if [ $FAILED -ne 0 ]; then
  echo ""
  echo "PRE-WRITE GATE FAILED: The write to $FILE has been BLOCKED."
  echo "Fix all errors above, then retry writing the file."
  exit 1
fi

exit 0