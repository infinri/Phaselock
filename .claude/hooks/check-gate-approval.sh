#!/bin/bash
# Gate sequencing hook — blocks writes until phase approval markers exist.
# PreToolUse: fires before every Write/Edit/MultiEdit.
# Gate markers are ALWAYS project-specific: {PROJECT_ROOT}/.claude/gates/

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

GATE_DIR="$PROJECT_ROOT/.claude/gates"
mkdir -p "$GATE_DIR"

# Phase A — call-path must be approved before observers/plugins/event wiring
if [[ "$FILE" == *Observer*.php || "$FILE" == *Plugin*.php || \
      "$FILE" == *Listener*.php || "$FILE" == *EventSubscriber*.php || \
      "$FILE" == */etc/events.xml || "$FILE" == */etc/di.xml ]]; then
  if [ ! -f "$GATE_DIR/phase-a.approved" ]; then
    echo "GATE BLOCKED: Observers/plugins/event wiring require Phase A approval."
    echo "Review Phase A output, then: touch $GATE_DIR/phase-a.approved"
    exit 1
  fi
fi

# Phase D — concurrency modeling must be approved before consumers and queue config
if [[ "$FILE" == */Consumer/*.php || "$FILE" == *consumer*.py || \
      "$FILE" == *worker*.go || "$FILE" == *Consumer*.java || \
      "$FILE" == */etc/queue_*.xml || "$FILE" == */etc/communication.xml ]]; then
  if [ ! -f "$GATE_DIR/phase-d.approved" ]; then
    echo "GATE BLOCKED: Consumer/queue files require Phase D approval."
    echo "Review Phase D output, then: touch $GATE_DIR/phase-d.approved"
    exit 1
  fi
fi

# Test skeletons — must be approved before Model/Service/Repository implementation
# (ENF-GATE-007: tests before implementation)
if [[ "$FILE" == */Model/*.php || "$FILE" == */ResourceModel/*.php || \
      "$FILE" == */Service/*.php || "$FILE" == */Repository/*.php || \
      "$FILE" == */service*.py || "$FILE" == */model*.py || \
      "$FILE" == */service*.ts || "$FILE" == */model*.ts ]]; then
  if [ ! -f "$GATE_DIR/test-skeletons.approved" ]; then
    echo "GATE BLOCKED: Implementation files require approved test skeletons (ENF-GATE-007)."
    echo "Review test skeletons, then: touch $GATE_DIR/test-skeletons.approved"
    exit 1
  fi
fi

exit 0
