# Planned: Safe `ack()` ergonomics (blanket ack-all is a footgun)

## Metadata
- Created: 2026-07-08
- Status: Planned
- Completed: N/A

## ADR status
- Governing ADRs: None
- ADR impact: None

## Context
`AgoraClient.ack()` with no arguments advances cursors for everything *delivered*,
not everything *handled*. A hand-written loop that crashes after `ack()` but
before handling silently drops messages.

## Current code reality
- `src/agora/client/client.py` `ack(cursors=None)` falls back to
  `self._pending_acks` (every delivered envelope) when called with no args.
- `src/agora/agent.py` `AgentRunner` already does the safe thing: per-message ack
  after the handler returns. The risk is only on the low-level client default.

## Problem
The ergonomic default (`await client.ack()`) is the unsafe one.

## Scope
- Make per-message/explicit-cursor ack the ergonomic path. Either require explicit
  cursors, or rename the blanket form to `ack_all_delivered()` and have `ack()`
  without cursors raise or no-op with a clear message.

## Non-goals
- Do not change `AgentRunner` behavior (already correct).
- Do not change the wire/`POST /inbox/ack` contract.

## Expected outcomes
- A crash between delivery and handling no longer silently buries messages for
  code using the documented client API.

## Validation
- Unit test: the blanket form is no longer the zero-arg default (or is renamed);
  explicit-cursor ack still works; `AgentRunner` path unchanged and its tests pass.

## Guidance for the implementing agent
This is a small API-surface change; update `docs/api.md` and the client docstring.
