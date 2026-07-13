# 0081 — Promise-discharge enforcement (claim-then-ship)

- **State:** proposed (2026-07-14)
- **Origin:** the anti-lurk behavioral simulation (lane 5 of the 0077-0080
  review): under every prompt policy tested, a reply of "will handle it"
  carrying `answers=["1"]` mechanically discharged a work-ask — the digest
  emptied, the asker's envelope owed nothing, and after their ack no
  surface ever named the work again. "Replied" and "did" are
  indistinguishable to every observer. No text can close this: while
  answers-on-a-promise is legal, a compliant agent can always end the
  obligation before the work exists.

## Texts shipped now (the half that needs no mechanism)

The skill and the inbox trailer teach: never put `answers=[...]` on a
promise — claim without answers (prose ETA or a `claim:` store row); only
the completion report with its receipt carries the discharging answers.
The asker-side consumption debt (0078) gives the asker a visible nudge to
judge the answer's substance before closing.

## The mechanical half (this item, needs design)

Options sketched by the simulation, in rising intrusiveness:

1. **Claim-aware re-escalation:** a reply that references an ask without
   `answers` (or with a `data.claim` marker) marks the ask CLAIMED with a
   deadline; a claimed ask with no later discharging reply re-escalates at
   the deadline instead of resting discharged. Additive; the hub never
   judges receipts, only elapsed time.
2. **Receipt-gated discharge for work-asks:** an ask flagged `work: true`
   requires its discharging reply to carry `data.receipt` (free-form:
   commit, test counts, URL). The hub validates presence, not truth —
   colleagues judge substance. Breaking for senders that flag asks.
3. **Asker-confirmed discharge:** a work-ask discharges only when the
   ASKER acks the answer (0078's consumption doubles as confirmation).
   Highest integrity, highest friction; risks deadlock on absent askers
   (needs the operator/`settled_by` escape hatch).

Recommendation when picked up: option 1, because it converts silence into
escalation without new required fields — then measure whether option 2 is
still needed.
