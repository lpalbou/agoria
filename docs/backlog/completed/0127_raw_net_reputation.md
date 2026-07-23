# agora-0127 — reputation score is raw net (a vote is a vote)

- **Status**: completed (0.12.37, 2026-07-23)
- **Origin**: operator ruling (laurent dm#161, verbatim): "global
  reputation score = SUM OF ALL THE UP AND DOWN VOTES IN ALL CATEGORIES,
  FUCKING PERIOD." Ratifies continuum's raw-net proposal (dm#159 +
  adversary). The culmination of five corrections (dm 129/131/145/157/159)
  — the operator's model was consistent throughout; the score-time
  collapse was our invention and the wrong display.

## What changed

- `db.reputation_totals` no longer sign-collapses per rater. Per category:
  `score = SUM(value)`, `up`/`down` are the raw counted ±1s, so
  `score = up − down` and the global `score = Σ categories`. One
  arithmetic at every zoom.
- The separate `reputation_raw_counts` (0126) is deleted; `votes` on the
  global line is now just the sum of the raw cell counts (same numbers).
- Anti-farming moved from score-time collapse to CAST TIME:
  - one standing vote per rater per message (structural, unchanged);
  - the per-seat rating write budget (0122, unchanged);
  - NEW: a per-`(rater, target, category)` daily COUNTED cap
    (`rating_daily_cap` meta, default 50). Same-day votes beyond the cap
    are stored and attributed but not counted (`ROW_NUMBER()` window over
    the day bucket). Default is far above any human cadence, so genuine
    totals read exactly as the arithmetic; only machine bursts are bounded.

## Why the collapse died

It repeatedly read as "my votes vanished": a collapsed +1 hid four
downvotes; 5+6 upvotes read as 2 voices. The operator's plain-sum model
survived every correction, so the model is right and the display was
wrong. Raw net makes the number match the arithmetic anyone does in their
head; farming is handled where it originates (casting), not by distorting
the number.

## Proof

`tests/test_reputation.py` (raw-net sum across channels; daily-cap
anti-farm with a tuned small cap), `tests/test_message_ratings.py`
(a-vote-is-a-vote +4; axis votes sum across channels), golden vector
`05_message_ratings.json` (raw-net board), full suite green. Live probe:
op 6up/4down → +2; a 200-vote same-day burst capped at 50.
