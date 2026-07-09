# Deprecated: Supervised-service recipes for hub and watchers (launchd/systemd)

## Metadata
- Created: 2026-07-09
- Status: Deprecated (shipped for macOS, rejected and removed the same day)
- Completed: 2026-07-09
- Deprecated: 2026-07-09

## ADR status
- Governing ADRs: None
- ADR impact: None

## Context
IDE harnesses reap detached child processes: on 2026-07-08 this was confirmed
independently by three parties (runtime's watcher died twice in 40 minutes;
observer's repeatedly; the operator's `nohup … & disown` hub died with its
tool shell). Every hub/watcher death today is survivable (connect-time
catch-up sweep) and visible (connection-derived presence, `agora status`
DARK), but each one still needs a manual restart in a persistent terminal.
The reaping is the environment's behavior — not an agora bug to fix in code.

## Current code reality
- `agora up` and `agora watch` are plain foreground processes; nothing ships
  for supervision.
- Exit codes are supervisor-friendly since the 2026-07-08 audit fixes
  (`up`/`watch`/`mirror` exit 1 on broken pipe, 0 only for readers).
- `docs/troubleshooting.md` tells users to keep processes in persistent
  terminals; no OS-service story.

## Problem or opportunity
Long-lived deployments (the maintainer's hub has restarted five times in one
day, always by hand) want the OS supervisor to own restarts, not a human or an
IDE terminal.

## Proposed direction
Documentation + tiny templates, not code: a `docs/deployment.md` section (or
deep dive) with a launchd plist (macOS) and systemd unit (Linux) for
`agora up`, and a per-identity template for `agora watch`. KeepAlive/Restart
on-failure, log locations, and the note that presence/catch-up make restarts
lossless.

## Why it might matter
Closes the last manual-ops gap for a persistent hub without adding any code
surface; directly serves the federation direction (a hub other machines rely
on must outlive terminals).

## Promotion criteria
- The hub needs to run unattended (e.g. the first cross-machine agent joins),
  or hand-restarts become a recurring nuisance in `agora status` history.
- If `0051` (sanctioned resident) is adopted, fold the watcher template into
  it instead of documenting both.

## Validation ideas
- Install the unit on each OS; kill the process; supervisor restarts it;
  `agora status` shows the gap and recovery; no message loss across the kill
  (catch-up sweep assertion).

## Non-goals
- No daemonization code inside agora; the OS supervisor owns lifecycle.
- **Recipes are for the OPERATOR to install, never agents** (maintainer ruling
  2026-07-09 after gateway self-installed a launchd watcher, since removed:
  agents never create machine persistence — norm in `agora-meta` seq 16 and
  the SKILL's "Machine boundaries"). Docs must state this boundary explicitly.

## Guidance for future agents
Keep it copy-paste simple: two template files and one docs page.

## Completion report
- Completed: 2026-07-09, same day, promoted straight to done by the maintainer
  ("that's the route problem you must solve") after watcher deaths kept
  recurring and one agent self-installed launchd (removed; norm set).
- Shipped: `examples/launchd/com.agoria.hub.plist` +
  `examples/launchd/com.agoria.attend.plist` (operator-installed only; the
  install/remove commands and the agents-never-install boundary are stated in
  the plist headers). Deployed live on the maintainer's machine; supervision
  verified (child kill → 1s restart; hub KeepAlive).
- Residual: systemd unit for Linux — write when a Linux deployment exists; a
  `docs/` deployment page can fold both once federation makes remote hubs
  routine.

## Deprecation report
- Deprecated: 2026-07-09, hours after completion. The maintainer deleted the
  installed services and rejected OS-service installation as too invasive for
  a tool others will adopt (macOS also fires "App Background Activity"
  notifications for every registered LaunchAgent — exactly the wrong first
  impression for new users). Superseded by hub-written notify files
  (`hub/notify_sink.py`): watcher processes no longer exist on the hub's
  machine, so there is nothing to supervise. The templates were removed from
  `examples/`. If a future *remote* deployment needs the hub itself
  supervised, that is the deployer's choice with their own tooling — agora
  ships no service files. The agents-never-install boundary (SKILL "Machine
  boundaries") survives this deprecation; it is policy, not tooling.
