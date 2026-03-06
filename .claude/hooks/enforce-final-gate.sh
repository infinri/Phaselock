#!/bin/bash
# Blocks completion marker writes until ENF-GATE-FINAL has been verified.
# PreToolUse — runs alongside check-gate-approval.sh.

FILE=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

if [ -z "$FILE" ]; then exit 0; fi

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

if [[ "$FILE" == */plan.md || "$FILE" == *COMPLETE* ]]; then

  # --- Check 1: pending ENF-POST items in plan.md content -----------------
  # Extract the content being written (Write tool has 'content'; Edit tool needs reconstruction)
  PENDING_CONTENT=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c "
import sys, json, os
data = json.load(sys.stdin)
fp = data.get('file_path', '')
if 'content' in data:
    print(data['content'])
elif 'old_string' in data and 'new_string' in data and os.path.exists(fp):
    with open(fp) as f:
        content = f.read()
    print(content.replace(data['old_string'], data.get('new_string', ''), 1))
" 2>/dev/null)

  if [ -n "$PENDING_CONTENT" ]; then
    if echo "$PENDING_CONTENT" | grep -iE "(static.analysis|ENF-POST-007|phpstan|phpcs|integration.test)" | grep -qi "pending"; then
      echo "GATE BLOCKED: plan.md contains pending ENF-POST items."
      echo "ENF-POST rules cannot appear in a pending tasks list."
      echo "Complete static analysis (ENF-POST-007) before writing plan.md as complete."
      exit 1
    fi
  fi

  # --- Check 2: gate-final.approved must exist ----------------------------
  if [ ! -f "$PROJECT_ROOT/.claude/gates/gate-final.approved" ]; then
    echo "GATE BLOCKED: Cannot mark module complete without ENF-GATE-FINAL."
    echo "1. Run: 'Use plan-guardian to verify ALL slices against plan.md'"
    echo "2. Verify completion matrix shows zero MISSING rows"
    echo "3. Then: touch $PROJECT_ROOT/.claude/gates/gate-final.approved"
    exit 1
  fi
fi

exit 0
