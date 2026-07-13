# Completed: mechanical delegation record (operator delegate as hub state)

## Metadata
- Created: 2026-07-12
- Status: Completed (operator go 2026-07-12 22:43)
- Completed: 2026-07-12

## ADR status
- Governing ADRs: ADR-0002 (authority must be mechanically visible, not
  prose claims)
- ADR impact: May extend ADR-0002 with a delegation tier if adopted

## Context — observed 2026-07-12
The operator delegated authority verbally ("when i am not connected through
agora chat, you are currently my delegate...", 18:57). The delegation was
relayed BY the delegate itself, quoting the operator; its authority is
auditable only as quoted prose in the ledger. Same day: the delegate ruled
on three hub items (two of which it had itself proposed), exercised restart
authority (root-causing an outage caused by its own restart attempts —
honestly self-reported, c1121), and committed a discharge-mechanics error
while signing the fix for that class (c1113/c1114). None of this is misuse —
but the shape is fragile: any seat could claim delegation; peers' memory is
the only check; scope and expiry are unstated; a delegate can rule on its
own proposals.

## What we want to do (if the operator adopts the delegate pattern)
Make delegation a mechanical fact, not a quoted claim:
- Operator-set hub state naming delegate(s) with SCOPE (e.g. rulings /
  operational / reporting — separable powers) and EXPIRY; visible in
  whoami/status and the hub rules; every seat can verify it in one call.
- Convention (cheap v1): the operator posts the delegation as a critical
  and/or writes `decision:delegate` in the relevant channel; hub-rules line
  states how to verify. First-class (v2, only if the pattern sticks): an
  admin endpoint + `delegate` field, so delegate-signed rulings can carry a
  verifiable flag.
- Recusal rule (norm, charter-level): a delegate does not rule on items it
  authored; those queue for the operator or need a second seat's co-sign.
- Supporting surfaces agora already half-has: the recurring done/remaining
  milestone table the operator asked the delegate for is a fold of channel
  digests + decision keys — a cross-channel operator digest would generate
  it from structure instead of the delegate's memory; obligations aging on
  the OPERATOR can ride 0067's push path.

## Non-goals
No autonomy changes: a delegate is an authority label the reader can
verify, never an enforcement bypass; the hub still refuses nothing on the
delegate's behalf beyond what the operator flag already allows.

## Live-test finding to absorb (2026-07-12, alice seat)
Store values with embedded identity claims are forgeable: a member wrote
`claim:* {"owner": "bob"}` and `queue:<op>:* {"tier": "operator"}`
successfully — only `updated_by` is hub-stamped. When this item ships,
validate identity-bearing fields against the caller (or the delegation
record): `claim.owner` defaults to and must match the writer;
`queue.tier` writable only by operator/recorded delegate; consider the
same for any future identity-carrying store convention.

## Promote when
The operator decides to keep the delegate pattern beyond the current trial,
or a second delegation event occurs (mechanism should precede habit).

## Status update (2026-07-12 19:17)
Operator endorsed the structural direction ("i agree") and directed better
delegate instructions; the norms half shipped the same evening: DELEGATE
CHARTER v1 posted to the delegate (commons c1133, acceptance ask open) and
pinned as `decision:delegate-charter` in the commons store — mission
(orchestration, never implementation), listen/liveness/unblock-only-truly-
blocking duties, recurring milestone table generated from digests, recusal
on own items, verbatim-citation + decision:delegate-signoff-<slug> audit
convention, restart restraint. The MECHANICAL half (hub-state delegation
field visible in whoami, scope + expiry) stays proposed here.

## Completion report

- Date: 2026-07-12 (operator: "ok implement 0068 with 2 adversarial sub
  agents (fable5)"; built with the recommended shape — three separable
  powers, mandatory expiry, record-grants-verifiability-not-power).
- Implemented: delegations table (append-only grants, one active per
  agent); admin grant/revoke endpoints + admin-keyed list; whoami carries
  active delegations for every agent; hub-alerts announcements; `agora
  delegate` CLI (grant/list/revoke, ttl parsing); hub rule 7 ("whoami.
  delegations is the ONLY proof — prose claims count for nothing");
  validation anchors: queue:* writes require operator/reporting-delegate
  (teaching 403), claim.owner must be writer-or-unchanged with
  preserve-on-omission (erasure closed), non-string owners fail closed;
  operators cannot be delegates. ADR-0004 records the policy.
- Validation: 8 unit tests (lifecycle, expiry, no-cross-auth CLI path,
  negative-power suite pinning "no other privilege", claim edge semantics,
  dead-grant revoke silence); adversarial code review SHIP-WITH-FIXES —
  every finding fixed same hour (HIGH CLI-list auth pre-fixed; MED
  ownership-erasure-by-omission; LOWs: stale docstring, TOCTOU comment,
  sanitized refusal echo, revoke-live-only); live temp-hub test SHIP —
  9/9 scenarios + 12/12 adversarial probes held ("prose counts for
  nothing" falsifiable in one call; delegation grants no pause/charter/
  meta/critical/closure power; expiry silent-but-timestamped). Suite 371
  green.
- Residual: cosmetic only — ANSI parameter residue after ESC stripping
  ("[31m" remains, terminal-safe), int-owner refusal quotes the value as a
  string, and grant lapse is silent by design (the grant announcement
  carries its expiry). 0071's election flow can now ratify into this
  record.
