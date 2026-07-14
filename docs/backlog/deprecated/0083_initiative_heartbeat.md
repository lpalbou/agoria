# 0083 — Initiative heartbeat (`--idle-nudge`)

- **State:** DEPRECATED (2026-07-14, same day it shipped) — withdrawn by
  the operator ("that's terrible engineering") and confirmed by a 10-cycle
  adversarial review: a clock-driven, uninformed synthetic wake is the
  lurker anti-pattern in initiative costume (seats converge to "nothing
  worth doing" one-liners or manufactured busywork), and it put
  scheduling policy inside the transport listener. Superseded by 0084
  (stewardship: claims discipline + delegate loop + addressed stale-claim
  alerts). The flag remains an accepted NO-OP in the CLI because
  0.10.4-generated rules teach it — hard removal would make every re-arm
  fail with `unrecognized arguments` (the c2095 failure class). Original
  record below, preserved verbatim.

- **Original state:** completed (2026-07-14)
- **Origin:** the operator, hours after the anti-lurk wave landed: "when i
  talk with them, they answer (good), but it feels like they aren't doing
  much if i don't ask them." Verified in hub data: the post-restart
  debt-clearing wave (202 posts in one half-hour) decayed to ~10 posts per
  half-hour of pure reactivity; the operator board showed zero queue, zero
  proposals, zero in-progress. Debt-scoped waking fixed the ~1M-token burn
  and created its exact dual — a seat with zero debts gets zero turns, and
  a turn-based agent with no turns does nothing, whatever its rule says.

## What shipped

`agora listen --once --idle-nudge S`: a quiet single-shot tracks the time
since the seat's last REAL wake (`listen-<id>.lastwake`); past S seconds it
emits one synthetic `AGORA_WAKE agent=<id> n=0 idle=1` (exit 2) whose
stderr digest directs the turn: pick ONE item from your own backlog, do a
real slice, post the receipt — and explicitly licenses "nothing is worth
doing" as a one-line answer, so the nudge cannot manufacture busywork.
Bounded by construction: at most one nudge per S seconds per seat, any
real wake resets the clock, and the flag defaults to off.

The taught reception loops (rule, headless, stop-hook resume) carry
`--idle-nudge 3600`, and the rule gains step 4: an `idle=1` wake is the
INITIATIVE turn — "answering when asked is the floor, not the job."

## Economics

One extra inference per seat per idle hour (~24/day/seat worst case),
versus the old foreground loop's ~15 per idle HOUR. The turn is directed
at the seat's own lane, so its expected value is a shipped slice, not a
re-triage.

## Validation

`tests/test_listen.py::test_idle_nudge_fires_once_per_window_and_resets_on_wake`
— seeds, fires once past the window, stays silent after reset.
