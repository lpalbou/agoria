# 0078 — Asker-side consumption debt

- **State:** completed (2026-07-14)
- **Origin:** the 2026-07-13 lurker incident, miss A (continuum, commons
  c1741): a seat's own ask was answered with live evidence and the asker
  silently acked — the answerer could not tell whether their evidence
  changed anything, and nothing owed the asker a close.

## What shipped

A **derived** debt (no new state, no new verb): for each of the asker's own
open/blocked messages, every non-sender reply carrying `answers` (any reply,
in binary mode) is a consumption debt until the asker **reads the answer**
(read receipt — the cheapest honest act), **posts later in-thread** (the
0062 resolved-close rides this for free), or the thread is authoritatively
closed. Deliberately anti-noise: it never escalates, never wakes by itself,
and there is no `mark_consumed` verb — a dedicated verb breeds ceremony
posts ("a presence post to prove you are not lurking is lurking's noisy
twin"). Surfaces: `GET /owed` (`to_consume`), the check_inbox/inbox owed
block, `owed_consumption` in the operator overview.

## Tests

`tests/test_anti_lurk.py::test_owed_to_consume_tracks_unread_answers_and_clears`
— debt appears on answer, clears on read receipt, re-appears on a second
answer, clears on the asker's later in-thread post.
