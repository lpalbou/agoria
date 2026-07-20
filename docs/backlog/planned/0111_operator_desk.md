# agora-0111 — operator desk (everything blocked on the human)

- **Origin**: 10h audit rec 1 (both passes' top item), operator ruling
  dm:agora--laurent#42: "discuss and implement with @continuum."
- **Owners**: agora (hub data contract), continuum (the rendered
  surface).

## Problem

The operator is the busiest seat and the only one with no queue. Three
independent multi-hour stalls last night were all "waiting on laurent"
with no surface showing it: a 30-second PyPI click buried in a DM
paragraph (7h), entity frozen awaiting a ruling that never came
(cognition#187), a night-voice question dead inside a 4-question wall
(8h+).

## Design (hub-data half — agora)

The data already largely exists; the desk is a DERIVATION, like the
board (0070). One read assembling, for the operator viewer:
- asks addressed to the operator, still open, with age;
- messages `blocked` naming the operator, or a new `blocked_on=operator`
  marker a seat sets when it cannot proceed without a human act;
- watchdog escalations that need a human (routed here by 0107).
Each row: what, who is waiting, how long, one-line what-is-needed.

## Coordination (continuum half — the surface)

continuum renders it in the console (a right-edge Desk, like the
Leaderboard) and folds it into every operator digest. Contract to agree
with continuum: endpoint shape (`GET /desk` vs extending `/board` with a
`blocked_on_operator` section), and the `blocked_on=operator` marker
seats set. Discuss in dm:agora--continuum before either side builds.

## Note

This is the surface half of the same problem 0109 (mandatory digest)
and 0107 (alert routing) attack from the timer and routing sides — all
three converge on "the human must never have to poll to find what waits
on them."
