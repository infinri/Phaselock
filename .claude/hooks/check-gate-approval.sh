#!/bin/bash
# Gate sequencing hook — blocks writes until phase approval markers exist.
# PreToolUse: fires before every Write/Edit/MultiEdit.
# Gate markers are ALWAYS project-specific: {PROJECT_ROOT}/.claude/gates/
# Output: structured JSON.
#
# Gate sequence: A → B → C → [D] → test-skeletons
# Each gate enforces all prior gates in the chain (sequential ordering).

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

# ── Sequential ordering check ────────────────────────────────────────────────
# Verifies all prior gates in the chain exist before the current gate.
# Returns 0 if all prior gates exist, exits 1 on first missing prior gate.
require_prior_gates() {
  local current_gate="$1"
  local current_rule="$2"
  shift 2
  local prior_gates=("$@")

  for prior in "${prior_gates[@]}"; do
    if [ ! -f "$GATE_DIR/$prior.approved" ]; then
      json_block "ENF-GATE-004" \
        "$current_gate requires $prior approval first (sequential gate ordering)" \
        "$prior"
      exit 1
    fi
  done
}

# ── Phase A — call-path declaration ──────────────────────────────────────────
# Blocks observers, plugins, event wiring until Phase A is approved.
# No prior gates required (Phase A is first in the chain).
if [[ "$FILE" == *Observer*.php || "$FILE" == *Plugin*.php || \
      "$FILE" == *Listener*.php || "$FILE" == *EventSubscriber*.php || \
      "$FILE" == */etc/events.xml || "$FILE" == */etc/di.xml ]]; then
  if [ ! -f "$GATE_DIR/phase-a.approved" ]; then
    json_block "ENF-GATE-001" "Observers/plugins/event wiring require Phase A approval" "phase-a"
    exit 1
  fi
fi

# ── Phase B — domain invariant declaration ───────────────────────────────────
# Blocks validation logic until Phase B is approved.
# Sequential: requires Phase A.
if [[ "$FILE" == *Validator*.php || "$FILE" == *Validation*.php || \
      "$FILE" == */Rule/*.php || "$FILE" == */Rules/*.php || \
      "$FILE" == *Specification*.php || \
      "$FILE" == *validator*.py || "$FILE" == *validation*.py || \
      "$FILE" == *validator*.ts || "$FILE" == *validation*.ts || \
      "$FILE" == *validator*.go || "$FILE" == *validator*.rs ]]; then
  require_prior_gates "Phase B" "ENF-GATE-002" "phase-a"
  if [ ! -f "$GATE_DIR/phase-b.approved" ]; then
    json_block "ENF-GATE-002" "Validation logic requires Phase B (domain invariant) approval" "phase-b"
    exit 1
  fi
fi

# ── Phase C — seam justification + API safety ────────────────────────────────
# Blocks plugin config, DI wiring, and endpoint declarations until Phase C.
# Sequential: requires Phase A and Phase B.
# Note: di.xml and Plugin files also require Phase A (checked above).
# This gate adds the Phase C requirement on top of Phase A for plugin/DI files,
# and gates endpoint declarations (webapi.xml, schema.graphqls) that Phase A
# does not cover.
if [[ "$FILE" == *Plugin*.php || "$FILE" == */etc/di.xml || \
      "$FILE" == */etc/webapi.xml || "$FILE" == *schema.graphqls || \
      "$FILE" == */etc/extension_attributes.xml ]]; then
  require_prior_gates "Phase C" "ENF-GATE-003" "phase-a" "phase-b"
  if [ ! -f "$GATE_DIR/phase-c.approved" ]; then
    json_block "ENF-GATE-003" "Plugin/DI/endpoint files require Phase C (seam justification) approval" "phase-c"
    exit 1
  fi
fi

# ── Phase D — concurrency modeling ───────────────────────────────────────────
# Blocks consumers and queue config until Phase D is approved.
# Sequential: requires Phase A, B, and C.
if [[ "$FILE" == */Consumer/*.php || "$FILE" == *consumer*.py || \
      "$FILE" == *worker*.go || "$FILE" == *Consumer*.java || \
      "$FILE" == */etc/queue_*.xml || "$FILE" == */etc/communication.xml ]]; then
  require_prior_gates "Phase D" "ENF-GATE-005" "phase-a" "phase-b" "phase-c"
  if [ ! -f "$GATE_DIR/phase-d.approved" ]; then
    json_block "ENF-GATE-005" "Consumer/queue files require Phase D approval" "phase-d"
    exit 1
  fi
fi

# ── Test skeletons — must be approved before implementation ──────────────────
# Blocks Model/Service/Repository implementation until test skeletons approved.
# Sequential: requires Phase A, B, and C.
if [[ "$FILE" == */Model/*.php || "$FILE" == */ResourceModel/*.php || \
      "$FILE" == */Service/*.php || "$FILE" == */Repository/*.php || \
      "$FILE" == */service*.py || "$FILE" == */model*.py || \
      "$FILE" == */service*.ts || "$FILE" == */model*.ts ]]; then
  require_prior_gates "Test skeletons" "ENF-GATE-007" "phase-a" "phase-b" "phase-c"
  if [ ! -f "$GATE_DIR/test-skeletons.approved" ]; then
    json_block "ENF-GATE-007" "Implementation files require approved test skeletons" "test-skeletons"
    exit 1
  fi
fi

exit 0