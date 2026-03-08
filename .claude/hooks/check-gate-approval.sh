#!/bin/bash
# Gate sequencing hook — blocks writes until phase approval markers exist.
# PreToolUse: fires before every Write/Edit/MultiEdit.
# Gate markers are ALWAYS project-specific: {PROJECT_ROOT}/.claude/gates/
# Output: structured JSON.

SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
source "$SKILL_DIR/bin/lib/common.sh"

FILE=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

if [ -z "$FILE" ]; then exit 0; fi

PROJECT_ROOT=$(detect_project_root "$FILE")
GATE_DIR="$PROJECT_ROOT/.claude/gates"
mkdir -p "$GATE_DIR"

json_block() {
  json_finding "true" "$1" "$2" "$FILE" "touch $GATE_DIR/$3.approved"
}

# Phase A — call-path must be approved before observers/plugins/event wiring
if [[ "$FILE" == *Observer*.php || "$FILE" == *Plugin*.php || \
      "$FILE" == *Listener*.php || "$FILE" == *EventSubscriber*.php || \
      "$FILE" == */etc/events.xml || "$FILE" == */etc/di.xml ]]; then
  if [ ! -f "$GATE_DIR/phase-a.approved" ]; then
    json_block "ENF-GATE-001" "Observers/plugins/event wiring require Phase A approval" "phase-a"
    exit 1
  fi
fi

# Phase D — concurrency modeling must be approved before consumers and queue config
if [[ "$FILE" == */Consumer/*.php || "$FILE" == *consumer*.py || \
      "$FILE" == *worker*.go || "$FILE" == *Consumer*.java || \
      "$FILE" == */etc/queue_*.xml || "$FILE" == */etc/communication.xml ]]; then
  if [ ! -f "$GATE_DIR/phase-d.approved" ]; then
    json_block "ENF-GATE-005" "Consumer/queue files require Phase D approval" "phase-d"
    exit 1
  fi
fi

# Test skeletons — must be approved before Model/Service/Repository implementation
if [[ "$FILE" == */Model/*.php || "$FILE" == */ResourceModel/*.php || \
      "$FILE" == */Service/*.php || "$FILE" == */Repository/*.php || \
      "$FILE" == */service*.py || "$FILE" == */model*.py || \
      "$FILE" == */service*.ts || "$FILE" == */model*.ts ]]; then
  if [ ! -f "$GATE_DIR/test-skeletons.approved" ]; then
    json_block "ENF-GATE-007" "Implementation files require approved test skeletons" "test-skeletons"
    exit 1
  fi
fi

exit 0
