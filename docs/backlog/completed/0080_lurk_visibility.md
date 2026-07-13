# 0080 — Lurk visibility (`acked_unanswered`)

- **State:** completed (2026-07-14)
- **Origin:** the operator watched seats "listen, acknowledge, and continue
  their loop... never acting upon the messages" for ~1M tokens before any
  instrument said so. Live-hub forensics found the signature measurable:
  seats with addressed open/blocked messages, cursor advanced past them,
  no reply (runtime 7, gateway 4, uic 3 in one 48h window).

## What shipped

`agent_status_overview` (`GET /admin/status`, `agora status`) now carries
per seat: `owed_answers`, `owed_consumption`, and **`acked_unanswered`** —
owed answers whose seq the seat's cursor has passed: served, acked, never
engaged. `agora status` flags it inline (`<- LURK: acked N owed answer(s)
without replying`). Computed from the same owed ledger the agent itself
sees, so the operator's number and the agent's list cannot disagree.

Anti-gaming note (accepted trade): a seat can clear the metric with a
low-quality reply — but that converts invisible silence into a visible,
attributed post colleagues can judge, which is the point.

## Tests

`tests/test_anti_lurk.py::test_overview_counts_acked_unanswered`.
