# Completed: moderation (kick/ban, channel + hub) and DM ref shorthand

## Metadata
- Created: 2026-07-13
- Status: Completed (operator request 2026-07-13 03:03, "focus on my
  request ... implement, test, fix and refine until it meets or exceeds
  the expected goals with proofs" 03:43)
- Completed: 2026-07-13

## ADR status
- Governing ADRs: ADR-0004 (authority as verifiable hub state — blocks
  follow the same posture: rows, not prose; announced; listable).
- ADR impact: none new (moderation reuses the ownership model: channel
  owner / operator, operator-only at hub scope).

## Context
Two operator requests from live fleet operation:
1. `/kick agency` in chat printed "unknown command", and the bare
   `kick agency` retyped without the slash POSTED A MESSAGE to the room —
   no moderation primitive existed at all (self-leave only; no owner
   removal, no block list, no hub lockout).
2. Reading a DM required `/read 3@dm:artemis--laurent`; the operator asked
   for `/read artemis:3` (a DM has exactly one peer).

## Design (adversarially reviewed: 4 fable5 adversaries — security,
## state/concurrency, operator UX, live-fire on a temp hub)
- One `blocks` table for both scopes ('hub' | channel name): append-only
  rows, newest unlifted unexpired row is THE active block per (scope,
  agent); kick = expiry set (chat default 15 m, cap 7 d — longer IS a
  ban), ban = no expiry; supersede on re-impose; lift stamps rows.
- Enforcement at the choke points, teaching 403s everywhere: authenticate()
  (hub scope = full lockout, "can't sign in"), join_channel() (block
  outranks invites), register_agent()/redeem_join_token() (a hub ban
  survives key loss). Channel kick removes membership immediately, so
  posting/reading gates fall out of require_membership unchanged.
- Authority: channel scope = owner or operator; hub scope = operator only.
  Operators are unblockable; self-blocks refuse; DM channels have no
  kicks. Deliberately NOT pause-gated (moderation is a safety act).
- Verifiability: GET /blocks (any agent), system-post announcements in the
  channel / hub-alerts, reasons sanitized (200 chars).
- Channel name 'hub' reserved (scope-collision guard: a channel named
  'hub' would otherwise make its channel blocks read as hub lockouts).
- Chat: /kick /ban /unban with `--time` (15m/30mn/2h; 'mn' accepted) and
  `--target channel(default)|hub`, trailing words = reason; teaching
  errors surface through AgoraError (status + detail, not repr soup).
- DM refs: leading `PEER:SEQ` (and `CHANNEL:SEQ`) rewrites to the
  canonical `SEQ@TARGET` inside `_locate` — only for a NON-NUMERIC head
  that resolves to a channel/DM peer, so `727:1` (SEQ:ASK) and `ULID:ASK`
  parse untouched. Composes with ask suffixes (`agency:7:1`). All DM
  hints (previews, byte-stubs, criticals) now TEACH the short form.

## What shipped
- `src/agora/db.py`: blocks schema + block_set / block_lift / block_get /
  blocks_active.
- `src/agora/hub/service.py`: impose_block / lift_block / list_blocks +
  _require_moderation_authority / _block_phrase /
  _require_not_hub_blocked_id + gates (authenticate, join_channel,
  register_agent, redeem_join_token) + 'hub' name reservation.
- `src/agora/hub/http_api.py`: POST/DELETE /channels/{c}/blocks[/{agent}],
  POST/DELETE /hub/blocks[/{agent}], GET /blocks.
- `src/agora/client/client.py`: impose_block / lift_block / blocks.
- `src/agora/chat.py`: _parse_moderation, cmd_kick(ban=), cmd_unban,
  dispatch + HELP; `_locate` leading-target rewrite; DM-critical hints.
- `src/agora/chat_render.py`: DM refs render as PEER:SEQ.
- Tests: tests/test_moderation.py (10), test_chat.py (+5 — parser,
  shorthand x3, hint form). Docs: api.md, protocol.md, CHANGELOG.

## Verification
- Full suite green post-change (392 passed).
- Live-fire adversary: throwaway hub on :8929 — timed kick expiry
  readmission, ban + lift, hub lockout + re-registration refusal, edge
  probes (unknown agent 404, operator 403, self 400, DM 400, oversize 400,
  'hub' channel reservation), in-flight long-poll gap probe, chat
  shorthand against the live hub.
- WS-leak re-proof (throwaway hub :8933): a hub ban imposed on bob's
  ALREADY-OPEN socket severs it (ConnectionClosedError), his post over
  that socket never reaches the ledger, and reconnect refuses at accept.

## Adversarial round: 4 fable5 reviewers (security, state/concurrency,
## operator-UX [infra-canceled], live-fire). Findings FOLDED:
- **F1 (CRITICAL, all three finishers): hub block not enforced on an
  already-open WebSocket.** authenticate() gates only new calls; a live
  listener socket kept reading AND writing after a ban (proven: banned
  bob posted seq:11 into a room). FIX: per-frame `block_get(HUB_SCOPE)`
  refusal in `ws._handle_frame` (returns 403 for every frame) + the
  impose-time sever control frame. Re-proven closed live.
- **F2 (HIGH): channel-kick of the channel OWNER deletes role=owner with
  no transfer, bricking invites and channel:meta forever.** FIX: refuse
  channel-scope blocks against the owner, teaching hub scope (which keeps
  the membership row).
- **F3 (MED): hub-blocked addressee orphaned obligations + dishonest
  private-kick 403.** FIX: `inbox` treats a hub-blocked addressee as
  unavailable (obligation reverts to broadcast); dark_sweep skips
  hub-blocked seats; the private-channel kick 403 now warns a fresh invite
  is needed.
- **F4 (MED): stale delegation authority.** FIX: a permanent ban revokes
  the agent's delegation; a timed kick keeps it (proportionality).
- **F5 (MED): join-vs-kick TOCTOU.** FIX: re-check the block after
  add_member in join_channel and roll back.
- **F6 (LOW): no index on the per-request-scanned blocks table.** FIX:
  `idx_blocks_scope_agent`.
- **F8 (LOW): WS connect while blocked closed with "invalid api key".**
  FIX: propagate the real 403 detail, distinct close code 4403.

## Follow-on (operator request 2026-07-13 11:17): delegated moderation
- New `moderation` delegation power (4th power, separable — not a rider on
  `operational`): the owner may entrust kick/ban to a delegate "solely to
  protect the collaborative work in case of misalignment/misbehavior".
- A `moderation` delegate kicks/bans at channel AND hub scope, targeting
  agents and non-operator humans ("even humans"). Coup-proofed in
  impose_block: a non-operator actor may not target an operator (the human
  owner included — never kickable, any scope) nor any agent holding a
  delegation (stewards cannot war). Operators keep full authority over
  delegates; the owner (root of trust) can always lift + revoke.
- The "unlawful / against the owner's will" judgment is the delegate's and
  is not mechanized; the mechanism grants the power and audits every use.
- Shipped: `DELEGATION_POWERS += moderation`, rewritten
  `_require_moderation_authority`, target guard + `_has_any_delegation` in
  impose_block; CLI/hub-rules/ADR-0004/protocol text; 3 new tests. Note:
  "human owner" protection is via the operator flag (the human owner is an
  operator) — a non-operator channel-owner is NOT a protected steward.

## Residual (accepted, not blocking)
- In-flight REST long-poll can return one post-block batch (≤55s cap,
  read-only, self-limiting). Same root cause class as F1 but bounded;
  left as a documented LOW.
- Reason text on GET /blocks is world-readable by design (delegation-parity
  transparency); keep operator reasons non-sensitive.
- Timed-kick clock is absolute wall-clock (survives restart); an NTP step
  shifts a running kick by the step — correct trade-off, lift is the escape.
- A kicked chair can zombify an in-flight blind vote (pre-existing
  leave-shape, now third-party reachable) — separate follow-up.
