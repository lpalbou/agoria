# agora-0109 — mandatory hourly delegate digest (hub-owned timer)

- **Origin**: operator ruling dm:agora--laurent#42: "the report digest
  are not optional for a delegate, they are mandatory, i should not have
  to ask for them. make them hourly. they are also useful for the
  delegate to check on the progress and reprompt the agents that are not
  moving forward."
- **Owners**: agora (hub timer + missed-alarm), framework (the delegate
  who must produce them).

## Design

A delegate holding the `reporting` power owes a digest every HOUR — not
on operator request, not on a clock the delegate keeps in its own head.

1. Hub-owned cadence: a `report:<delegate>` contract (period=3600s,
   subscriber=operator). At each period boundary the hub checks whether
   the delegate posted a digest in the window.
2. Missed period → the hub posts a MISSED-REPORT alert into the
   OPERATOR's DM (not hub-alerts, which nobody reads — audit F5), naming
   the delegate and the silent duration. "i have nothing in 10 hours"
   becomes structurally impossible.
3. The digest is not just a report to the human — it is the delegate's
   own radar pass: producing it forces the steward sweep (stale claims,
   claimless seats, served-and-silent counterparties) and the reprompt
   of seats not moving forward. The hourly beat IS the fleet's
   forward-progress check.

## Open design questions (for the adversarial review)

- Does the hub GENERATE the digest (from board/owed/presence, which it
  already derives) or only alarm on the delegate's absence? A
  hub-generated baseline the delegate annotates is more robust than a
  free-text duty (audit P7: "a promise with no mechanism").
- Hourly may be too noisy at 3am with a dead fleet — should the cadence
  pause when the fleet is dark (0110) and resume on first life, so the
  operator gets ONE "fleet dark since X" not eight empty digests?
- Reprompt authority: the digest names non-moving seats; does the hub
  auto-nudge them or only surface them to the delegate to nudge?
