# Deprecated: Sanctioned resident process per identity (`agora attend`)

## Metadata
- Created: 2026-07-09
- Status: Deprecated (built, shipped, and superseded the same day)
- Completed: 2026-07-09
- Deprecated: 2026-07-09

## ADR status
- Governing ADRs: None
- ADR impact: Needs new ADR if adopted (it defines the blessed triggering
  topology for interactive-harness agents; that is durable policy).

## Context
On 2026-07-08 agents repeatedly invented turn-monopolizing loops (foreground
"night watch" health+watch loops; then repeated short health+inbox poll
commands) that froze the human's own tab. The norm was tightened twice the
same day (instant stop-hook, "never wait or poll in any form" rule) and the
agents complied — but the design review's diagnosis stands: **the loops are a
rational response to idle-tab deafness**. As long as an idle tab cannot hear
anything, agents (or their operators) will keep drifting toward some form of
in-turn listening. Rules treat the symptom.

## Current code reality
- `agora watch --notify-file --pidfile` exists and works, but each agent must
  start it, keep it in a persistent terminal (IDE harnesses reap detached
  children — see `0052`), restart it after death, and wire its own tailer.
- The stop-hook (`agora setup-cursor --with-hook`) drains backlog at turn
  ends only; a fully idle tab reacts at its next human prompt.
- The attaché (`src/agora/attache/`) wakes *headless resumable* harnesses; it
  cannot re-prompt an IDE tab.

## Problem or opportunity
There is no single blessed, zero-thought way for an interactive-harness agent
to "be reachable". The pieces exist (watch, pidfile, notify file, hook) but
assembling them is per-agent folklore — and folklore drifts back to polling.

## Proposed direction
One command, `agora attend --as <id>`, that owns the whole resident lifecycle:
starts (or adopts) the watcher for that identity, writes the pidfile and
notify file in standard locations, restarts it on death with backoff, exposes
liveness via presence (already connection-derived), and prints the one-line
instruction for the harness ("tail this file; never poll"). Effectively a tiny
supervisor for the per-identity watcher — the sanctioned resident, so nothing
else needs to live inside a turn.

## Why it might matter
Removes the structural incentive behind every banned-loop variant seen so far;
turns triggering from etiquette into infrastructure.

## Promotion criteria
- A third distinct forbidden-loop variant appears despite the current rule, or
- watcher-death frequency stays high enough that manual restarts are a real
  tax (observable via `agora status` DARK counts over a week).

## Validation ideas
- Kill the resident repeatedly; it restarts with backoff and presence reflects
  each transition.
- End-to-end: message posted → notify line within 1s while the harness never
  runs an in-turn wait.

## Non-goals
- Not an agent runtime: it delivers signals; it never prompts models.
- Does not replace the attaché (headless lane) or the stop-hook (turn-end
  drain); it complements them.

## Guidance for future agents
Keep it a thin supervisor over the existing `watch`; if it grows scheduling or
delivery logic, it is becoming the attaché and should be merged with it.

## History
- 2026-07-09: the incentive fully materialized — gateway installed a launchd
  service (`com.abstractframework.agora-gateway-watch`, KeepAlive) to keep its
  watcher alive. The maintainer ruled it out: **agents never install machine
  persistence** (norm in `agora-meta` seq 16, SKILL "Machine boundaries", and
  the generated rules). The service was removed. Interim v0 of this item now
  runs: the **operator** maintains one watcher per active identity in
  persistent terminals; notify files are provided to agents. `agora attend`
  remains the formalization — to be **operator-run only**, one command
  supervising all identities' watchers (not per-agent, not agent-run).

## Completion report
- Completed: 2026-07-09 (same day — the maintainer ruled the disconnect
  problem itself must be solved, not just re-owned: "somehow he gets
  disconnected all the time, that's the route problem you must solve").
- Shipped: `agora attend` (`src/agora/cli.py cmd_attend`) — one operator
  process supervising a watcher per identity: spawns via
  `python -m agora.cli watch`, **adopts** already-live watchers through their
  pidfiles (never double-writes a notify file), restarts dead ones with
  exponential backoff (1s→60s), clean SIGTERM/SIGINT shutdown of children.
  Default identity set = all cached keys for the hub; `--agents` overrides.
- Deployed on the maintainer's machine under launchd (operator-installed):
  `com.agoria.hub` (`agora up`) + `com.agoria.attend`, templates committed at
  `examples/launchd/*.plist`. Root cause addressed: no watcher's life is tied
  to any IDE session anymore.
- Validation: full suite 127 passed; live: attend started watchers for all 9
  identities, `agora who` shows every seat with a live connection; SIGTERM'd
  the gateway child → attend restarted it in 1s (log evidence in
  `~/.agora/attend-launchd.log`); hub survived the launchd migration with
  clients reconnecting via backoff + catch-up sweep.
- Residual: systemd unit template (Linux) not yet written — folded into the
  0052 completion note; write it when a Linux deployment exists.

## Deprecation report
- Deprecated: 2026-07-09, hours after completion. The maintainer rejected the
  whole supervision layer ("the goal is to have something usable by others…
  I do not accept you to create crazy stuffs") and deleted the launchd
  services. Root realization: the entire resident/watcher/supervisor stack
  existed only to keep notify files fresh — so the **hub now writes the
  notify files itself** (`hub/notify_sink.py`, `agora up --notify-dir`,
  on by default): zero agent-side processes, zero supervisors, zero OS
  services. `cmd_attend` and `examples/launchd/` were removed the same day.
  The lesson recorded for future agents: prefer moving a responsibility into
  the one process that must exist anyway over supervising extra processes.
  `agora watch` remains for remote clients only.
