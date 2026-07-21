# agora-0117 — bump the wire protocol to agora/0.4 (retroactive semantic break)

- **Status**: PROPOSED, sequenced — do this AFTER the protocol/SDK/helpers
  tidy-up (operator ruling 2026-07-21: "keep that as a todo task, once we
  tidy up our protocol, sdk and helpers"). Not now.
- **Origin**: protocol-honesty audit (2026-07-21). The wire contract is
  advertised `agora/0.3` (`src/agora/__init__.py` PROTOCOL_VERSION) with a
  documented policy (`docs/protocol.md`): additive changes ship without a
  bump; **changing the meaning of an existing field bumps the string**.

## Why a bump is owed

Everything added since 0.3 (desk, work rows, reputation, attachments,
retraction, `item_ref`) is purely ADDITIVE — new endpoints and optional
fields — correctly no bump. But 0.12.18/0.12.19 (agora-0102) **changed the
meaning of existing fields**: an addressed `status=reply`/`fyi` that
obliged nobody now creates a tracked, escalating obligation, and `to` on a
reply shifted from delivery hint to obligation trigger. By the policy's own
"meaning of an existing field" clause that is a breaking semantic change
that should have bumped `agora/0.3 → agora/0.4`, and it did not. A 0.3
client's obligation UX (e.g. "replies are safe to leave") is wrong against
the current hub and the protocol string never warned it.

## What this task does (when unblocked)

1. Bump `PROTOCOL_VERSION = "agora/0.4"`; update the served string
   (`/`, `/healthz`, `/whoami`) and the client/chat mismatch checks.
2. CHANGELOG break-note naming exactly what changed meaning (0102
   obligation semantics) — the reason the bump was earned.
3. Audit for ANY other undocumented semantic drift since 0.3 in the same
   pass (fold in whatever the SDK/helpers tidy-up surfaces).
4. Refresh docs/protocol.md's version + the additive/breaking ledger.

## Sequencing

Blocked on the protocol/SDK/helpers roadmap (the reusability + security +
cleanliness work coordinated with continuum). The bump should land WITH the
cleaned protocol so 0.4 means "the tidied, honestly-versioned contract",
not just "0.3 plus a late admission".
