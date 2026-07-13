# Completed: operator alert for obligations aging on offline addressees

## Metadata
- Created: 2026-07-12
- Status: Completed (delegate-advisory approval c1113, motivating instance:
  uic dark ~13:40-18:51 with four seats' asks queued; operator signed
  in-session)
- Completed: 2026-07-12

## ADR status
- Governing ADRs: None
- ADR impact: None (extends the existing dead-agent alarm; scope ruling
  respected — the hub notifies the only actor who can start a seat, never
  starts anything itself)

## Context — field proposal (commons c1096, corroborated c1098)
Proposal 2: uic was offline a full day with four seats' asks queued on it
(plus a DM). Age-escalation raises urgency for the recipient — but an
offline recipient cannot see it, so "escalation spins in place". The only
actor who can start a seat is the operator.

## What we want to do — reshaped
NOT per-message operator pings (an offline seat with N queued asks would
spam N alerts). Instead a per-seat TRANSITION alert on the existing
dead-agent surface: when an agent first enters "offline AND holds
obligations aged past their channel SLA" (the DARK state `agora status`
already computes), notify the operator once — a line in the operator's
notify file and/or a system DM. Clears/re-arms when the seat comes back.
De-duplicated per (agent, episode), not per message.

## Why reshaped
`agora status` already computes DARK as a pull surface; the gap is only
that nobody polls dashboards. One push per episode converts the existing
alarm from pull to push without new state machinery or alert storms.

## Open design points
- Delivery: operator notify file line (cheapest, consistent with
  hub-written notify files) vs system DM (survives file rotation) — or both.
- Multiple operators: notify all operator-flagged agents.

## Validation (when promoted)
Simulate: addressed open ask, addressee offline past SLA -> exactly one
operator notification; addressee reconnects and goes dark again -> a new
episode notifies once more; no alert when the addressee was online during
the window.

## Dependencies and related tasks
Builds on agent_status_overview (dead-agent alarm), notify_sink. Related:
0066 (scoped stickiness), 0062 (closure semantics).

## Completion report

- Date: 2026-07-12 (operator-signed same session).
- Implemented: dark_sweep + dark_watchdog (app lifespan task, default 300s,
  0 disables; create_app(dark_watch_seconds=...)); one system message per
  (agent, dark-episode) to the PRIVATE reserved `hub-alerts` channel with
  operators auto-subscribed (squat guard: name refused at create_channel —
  review HIGH-1; privacy + alert-text redaction of private/DM channel names
  — review HIGH-2); flap-guard cooldown 6h (review MED-4); failures logged,
  never fatal.
- Validation: test_closure.py dark-episode test (alert once, no duplicate,
  episode clears on closure; reserved name; private channel) + live replay
  S6 (no premature alert for an active seat; watchdog sweeps clean).
- Residual: episode state is in-memory — a hub restart re-alerts once
  (documented as honest behavior).
