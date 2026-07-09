#!/bin/bash
# agora `stop`-hook for a Cursor IDE tab.
#
# Fires when this tab finishes a turn. Checks the agora inbox INSTANTLY (no
# long-poll). If messages are already waiting, it returns a `followup_message`
# that re-prompts THIS tab to handle them; otherwise it returns empty in well
# under a second and the tab is immediately free for the human.
#
# NEVER add a long-poll (?wait=) here: a human shares this tab, and a blocking
# hook freezes it and queues their requests behind the agent. True always-on
# wake belongs in a headless runner or the attache (docs/triggering.md).
#
# Requires: curl, jq. Set AGORA_URL / AGORA_API_KEY (same values as this
# workspace's .cursor/mcp.json, e.g. sourced from .cursor/agora.env).
set -euo pipefail

: "${AGORA_URL:=http://127.0.0.1:8765}"
: "${AGORA_API_KEY:?set AGORA_API_KEY for this agent}"

# Instant check for unread envelopes (no wait parameter).
unread=$(curl -s -m 5 \
  -H "Authorization: Bearer ${AGORA_API_KEY}" \
  "${AGORA_URL}/inbox" || echo '[]')

count=$(echo "$unread" | jq 'length' 2>/dev/null || echo 0)

if [ "$count" -gt 0 ]; then
  # Re-prompt this tab. Keep it short: the agent will use its MCP tools
  # (check_inbox / read_message) to actually read and act. This just wakes it.
  jq -n --arg n "$count" '{
    followup_message: ("You have \($n) unread agora message(s). Call check_inbox, "
      + "triage them, read (read_message) what warrants it, act, reply where a "
      + "reply is owed (status open/blocked), then ack_inbox. When done, stop.")
  }'
else
  # Nothing waiting: no follow-up, let the tab rest.
  echo '{}'
fi
