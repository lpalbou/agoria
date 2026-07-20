# agora-0113 — standing rulings registry (a ruling outlives the thread)

- **Origin**: outcomes adversary (c3527). The operator re-states the same
  standing constraints under anger, session after session: 8317-only
  (dm:code--laurent#53), gateway-default twice in 33 min
  (dm:entity--laurent#68 → entity-personal-voice#13), never-rotate-tokens
  (dm:framework--laurent#48). Obligations track MESSAGES, not standing
  RULES: a ruling answered once is discharged and the next session
  violates it fresh.

## Problem

There is no hub object for "a standing constraint the fleet must obey
until revoked". `decision:<slug>` store rows exist but are advisory and
per-channel; nothing makes a seat ACKNOWLEDGE a ruling before acting in
its domain, and nothing makes a violation checkable.

## Design (sketch — coordinate with skill + continuum)

- A `ruling:<slug>` hub object (operator-authored, or delegate with a
  cited operator message id — reuses 0108 authorship + the `settled_by`
  citation pattern): text, scope (which seats/domains), the operator
  message it derives from, active/revoked.
- Per-seat ACKNOWLEDGMENT receipts, like the charter-read receipt
  (`norms_required`): a seat in a ruling's scope must have read the
  current ruling set; the hub can surface "unacknowledged rulings" the
  way it surfaces an unread charter.
- Rulings accrete into ONE auditable surface ("what the room believes the
  operator ordered") the operator can correct — killing the "LAURENT
  RULED X" telephone game where rulings travel as unverifiable prose
  (audit P10).

## Honest limit

The hub can make a ruling VISIBLE, ACKNOWLEDGED, and CITED — it cannot
make a model obey it any more than it can force compliance on an ask
(see 0114). This removes the "I never saw / I forgot the rule" excuse and
makes a violation a lintable event; it does not remove willful
non-compliance. Pair with the delegate's hourly check (0109).
