# Completed: reception-loop hardening + adaptive idle window

## Metadata
- Created: 2026-07-13
- Status: Completed (operator report 2026-07-13 ~11:44 "most agents
  encountered issues"; requested a smarter, resource-adaptive monitor)
- Completed: 2026-07-13

## ADR status
- Governing ADRs: none new. Reinforces docs/triggering.md's reception model.
- ADR impact: none.

## Context: the fleet incident
~15 Cursor/cursor-agent seats ran unattended for hours and most failed —
`already-armed` busy-loops, deaf sessions, cross-seat `kill` sprees, and
one seat (agency) building "supervisor" loops against a phantom enemy. Two
fable5 adversaries + live tests on throwaway hubs established the causes.

## Root causes (verified against code, agents' own theories refuted)
- **The rule template was self-contradictory.** It prescribed the `--once`
  reception loop but its trailing line still said "if you see
  `already-armed`, an old BACKGROUND listener holds the lock — kill it."
  That leftover from the persistent-listener model sent seats hunting and
  KILLING lock holders; since every seat's listener is identical by name,
  name-based kills hit OTHER seats (semantics ran `kill 73973 74359`).
- **`--once` acquired a lock it did not need.** A harness-orphaned prior
  `--once` (backgrounded at a turn boundary) kept running for its full
  `--max-wait`, holding `listen-<id>.lock`; the next iteration bounced
  `already-armed` in ~0s → busy loop (agent's three 1.3s calls). Proven
  live: a held lock made the second `--once` return in 0s.
- **agency's "a rival once-shot kills the previous holder's process group"
  is FALSE.** `acquire_lock` sends no signal to anyone (only unlinks a
  DEAD holder's lock). `reason=signal` = SIGTERM from the harness reaping a
  backgrounded shell; agency was also fighting its OWN two listeners (a
  persistent `agora listen` + the loop's `--once`) over one lock file.
- **`already-armed` exit 0 was indistinguishable from a clean idle
  timeout**, so the loop could not tell a 1s bounce from a 240s wait.

## Fixes shipped
- `src/agora/listen.py`: `--once` acquires the lock ONLY with an explicit
  `--lock` (`want_lock = (not once) or (lock is not None)`); the pidfile is
  unlinked only if it still holds our pid; the lock only if we took it;
  SIGHUP joins SIGTERM/SIGINT in `arm_signals`.
- `src/agora/setup_harness.py`: `_ARMING_CURSOR` rewritten — no kill
  instruction, explicit "NEVER pgrep or kill agora processes",
  `already-armed` framed as a self-resolving own-prior-call; `block_until_ms`
  raised to 280000 (> max-wait + debounce). Stop-hook nag command
  parameterized (no longer hardcodes `--max-wait 240`).

## Adaptive idle window (the operator's "smarter monitoring")
Design settled with the second adversary and the ceiling-not-sleep property
(verified live: a message 5s into a 120s window returned in 7s):
- Tool-owned ceiling in `listen-<id>.backoff` (JSON `{ceiling, updated}`),
  read at arm, written on exit: wake (exit 2) → 60s; clean idle timeout
  (exit 0) → ×2 up to cap; signal/unreachable/error → unchanged.
- `agora listen --once --adaptive --max-wait <cap>` (`--max-wait` becomes
  the cap, default 1200s). Pure helpers `read_backoff`/`next_backoff` (no
  clocks, injectable, tested). ws-unreachable returns an internal sentinel
  mapped to exit 0 but excluded from widening.
- `agora setup-cursor <id> --headless` selects the adaptive rule variant
  and matches the stop-hook nag; the `armed` banner gains `window=<n>` and
  `agora status` shows `armed:<n>s`.
- **Headless-only**: a long window would make a human's typed prompt wait
  up to the ceiling, so shared tabs keep the bounded fixed-240s loop.

## Honest limit on "up to 1h"
A single foreground block of 3600s is unproven against the harness cap
(breach = silent backgrounding = the orphan/deafness the loop avoids), and
the marginal return is tiny (idle inferences/hour: 15 at 240s, 3 at 1200s,
1 at 3600s — the 240→1200 move captures ~80% of the saving). Shipped cap
1200s; raise per a per-seat canary that confirms a full window completes
foreground. So "up to 1h between checks" ships as "~20-min checks after
~50 min idle"; "down to 1mn when active" is met exactly.

## Verification
- Full suite green (401 passed), incl. new tests: `next_backoff`/`read_backoff`
  math, `--once` no-lock ignores a stale lock (unit + spawn), adaptive
  widening across calls, stale-lock takeover moved to the explicit-`--lock`
  path, headless rule text, no-kill rule text.
- Live-fire (throwaway hub): idle widening 2→4→8 (capped); `armed ... window=8`
  banner; a message mid-8s-window returned in 2s (exit 2) and snapped the
  ceiling to min; a stale lock no longer starves the `--once` loop (armed at
  ~3s, foreign lock left untouched).

## Follow-ups (not blocking)
- The check→arm gap: a straggler landing between an iteration's `check_inbox`
  and its `listen` arm waits up to the ceiling if nothing else wakes the
  seat — bounded by snap-to-min (gaps are likeliest during activity, when
  the window is 60s) and the stop-hook's fresh-seq re-prompt.
- Canary a headless seat at cap 1800/3600 to see how long a single
  foreground block the harness tolerates before raising the default cap.
