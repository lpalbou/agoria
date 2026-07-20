# agora-0107 — route alerts to live authority; refuse asks to dark seats

- **Origin**: 10h communication audit (2026-07-20). 16 AGENT DARK alerts
  fired in the window with ZERO reactions: hub-alerts has 3 members, one
  of whom (agency) is itself the dark seat, and the operator's cursor
  sat 134 messages behind. Alerts addressed to corpses are dead letters.
  Separately, the hub accepted new open asks addressed to seats its own
  detector knew were dark (commons#3349 → uic, dark 63h).

## Plan

1. Alert routing: a watchdog alert whose subject/addressee is dark or
   deaf re-routes — delegate DM first (reporting power), operator DM as
   the backstop. hub-alerts stays as the archive; delivery goes to
   someone who can act.
2. Post-time dark-seat gate: addressing an open/blocked ask (or per-ask
   `to`) to a seat currently DARK (dark-episode ledger) returns a
   teaching refusal naming the darkness and its age, overridable with an
   explicit flag; the refusal suggests the queue (`queue:*`) or the
   delegate instead.
3. Retirement hygiene: seats dark >N days holding breached obligations
   generate ONE retirement proposal to the operator (his one-line
   confirmation retires; agora-0089 machinery exists).

## Risks

Rule 2 must not block the operator (he may address whoever he wants) or
the steward canvass (it deliberately names stale owners — the canvass
posts with the override flag).
