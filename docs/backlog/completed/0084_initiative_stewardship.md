# 0084 — Initiative as stewardship (claims + delegate loop)

- **State:** completed (2026-07-14)
- **Origin:** the fleet went purely reactive after debt-scoped waking
  (zero debts = zero turns). The first fix — 0083's clock-driven synthetic
  wake — was withdrawn the same day (see deprecated/0083). This design
  came out of a 10-cycle adversarial review (5 Fable 5 reviewers × 2
  rounds; every cycle produced at least one adopted improvement), anchored
  to the operator's own framing: "we have a delegate who can talk to other
  agents; they have tasks, they should look into it, and then they should
  investigate the problems they found during their work."

## The design (initiative rides debt, never clocks)

- **Claims discipline (text, hub rule 2 + the workspace rule + skill):**
  every seat holds ONE live claim; progress = evidence receipt; no
  evidence = blocked naming the blocker; receipts name the follow-ups the
  work revealed (your next claim normally starts there; an empty list is
  a finding — never invent one). The claim-row overwrite IS the progress
  receipt.
- **The steward loop (delegate charter, Stewardship section):** radar on
  every wake (owed/board/presence); flag unowned proposals, claimless
  seats, stale claims, served-and-silent counterparties; nudge
  acked-past-no-reply seats only, one bundled message per seat per SLA
  window, two strikes then a queue row; a promise is not a claim (hold
  the ask open until claim:<task> exists); problems named in receipts
  become owned items the same wake; audit-not-funnel (assign orphans
  only); report four sections on operator ask or major settlement, never
  on a clock.
- **The mechanical spine (all additive):**
  1. `_steward_sweep` inside the existing dark watchdog: a claim row
     untouched past its channel SLA produces ONE coalesced hub-alert
     ADDRESSED to the reporting delegates (addressed rides the proven
     to-me wake path and the owed ledger; broadcast alerts decay on a
     bare read). Episode-deduped like AGENT DARK; touching the claim ends
     the episode; no delegates = no scan.
  2. `GET /status`: the operator overview served to reporting delegates
     (the steward could not see `acked_unanswered` behind the admin key),
     refusal details redacted for non-operators (HIGH-2).
  3. A dark DELEGATE alerts on ANY pending obligation, not only
     escalated ones (a stalled steward is the reactive fleet one layer
     deeper).
  4. Reporting delegates are enrolled in hub-alerts (redaction already
     covers the wider audience).
  5. `LISTEN_CMD` single-sourcing: the taught listener command has ONE
     definition rendered into the rule, headless rule, and stop-hook nag
     (four hand-spelled copies drifted within one release — c2095).
- **Accepted stalls (by design):** a fleet with every claim finished and
  every ask answered sleeps until the operator speaks — the human is the
  prime mover. A delegate neglecting its charter while staying online
  emits no mechanical alarm; the operator's probe is the backstop, and
  ignoring an ADDRESSED stewardship alert shows as `acked_unanswered`.

## What was deliberately NOT built

- No synthetic wakes anywhere (clock turns are the withdrawn 0083).
- No claims ledger in `/owed` and no claim-SLA constant: board
  `in_progress` rows already carry `updated_at`; a second derivation and
  a second aging policy were cut by the minimalist lane.
- No claim-aware stop hook: an addressed ask already rides a five-layer
  enforcement stack (to-me wake, sticky pin until engagement, turn-end
  unread nag with backoff, waiting_on, LURK/status); a second nag channel
  at ~48/day would train seats to ignore the hook.

## Validation

`tests/test_anti_lurk.py`: stale-claim alert addressed to the delegate
(episode dedup, receipt-clears, no-delegate silence); `GET /status`
gating + redaction. Suite 434 green.
