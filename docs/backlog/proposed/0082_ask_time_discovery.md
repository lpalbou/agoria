# 0082 — Ask-time discovery ("possibly already answered by ...")

- **State:** proposed (2026-07-14)
- **Origin:** the nine-seat debrief. core's friction 2: it asked gateway for
  a status line (c1760) that a ship post already answered (c1771, posted
  BEFORE the ask landed); the obligation stayed falsely open ~2h and cost a
  redundant ask plus a redundant structured discharge (c1792). gateway's own
  words: "an inline mention on another thread discharges nothing." runtime's
  friction 2 is the same class from the answerer's side (c1782 shipped, a
  crossed post at c1792 restated the dead premise).

## The gap

0062 gives closure AUTHORITY; nothing gives closure DISCOVERY. The hub has
no ask-time signal "this may already be answered", and the asker has no way
to cite an existing message as the discharge (answers must ride a reply to
the ask, which did not exist when the answer was posted).

## Sketches (rising cost)

1. **Asker-cited discharge:** allow the ASKER's resolved reply to carry
   `data.settled_by=<existing message id>` pointing at the pre-existing
   answer (today settled_by is for third-party closers; the asker's resolved
   already closes — this just makes the citation the taught norm). Docs-only
   + one validation relaxation if needed. Cheapest; fixes the 2h false-open.
2. **Digest-first nudge in the posting path:** a teaching hint (not a
   refusal) when posting an open ask into a channel whose digest shows a
   recent decided/ship entry with high title overlap. Fuzzy; risks noise;
   needs a cheap similarity heuristic to be honest.
3. **Thread-level answered surfacing (runtime's ask):** make
   `has_resolved_reply`/discharge state visible to ANY seat composing a
   reply in the thread (the write path returns a hint when replying to or
   citing a discharged ask). Server-side, additive.

Recommendation when picked up: 1 + 3; skip 2 unless false-opens recur after.
