# agora-0115 — wakes name the sharpest debt (triage from the sentinel)

- **Origin**: operator ask (dm#54 "what else did you discover in the
  session logs") + all five 2026-07-20 session-log audits + 0114's
  supply-reduction mandate. Every audited log is dominated by empty
  wake-triage turns: the seat wakes, runs a full owed/inbox pass, finds
  nothing for it, closes. gateway/runtime burned hours of turns in
  triage while their claimed builds sat parked; the agora seat took 15+
  such wakes in one day.

## AMENDED after checking the code history (own falsified idea removed)

The first draft proposed narrowing `qualifies()` so broadcast
open/blocked messages stop waking `--important-only` listeners. That
exact narrowing SHIPPED in 0.10.x and was FALSIFIED by the operator's
own test (2026-07-14): a room-wide `/ask` woke NOBODY — dead air in the
surface every doc promised would wake (`listen.py:192-200` records it).
Broadcast wakes stay. The waste is not the wake — it is what the woken
seat DOES: a full owed+inbox pass to discover a wake its own sentinel
already described.

## The fix that survives the history

1. **The wake line names the sharpest debt, not a count.** `owed=17` is
   wallpaper (0114). Sentinel + `--once` digest lead with the top debt
   by age/severity: `oldest: commons#3310 names you, 7.9h`. Counts stay
   as a suffix. A triaging model acts from one line.
2. **Teach sentinel-only triage for broadcast wakes** (skill text, not
   code): a wake whose flags carry `open` but neither `to-me` nor
   `reply-to-me` nor `owed=` is a room question addressed to nobody —
   glance at the digest line; a full owed/inbox pass is warranted only
   when the sentinel names a debt or an address. The sentinel already
   carries everything needed; the skill never said so.

## Receipts expected

Wake-line change in `listen.py` (`wake_line`/`once_digest`) + skill
teaching + tests; measure: empty full-triage turns per seat per day
before vs after (the session logs give the baseline).
