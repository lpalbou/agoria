# Proposed: one-command development-channel provisioning

## Metadata
- Created: 2026-07-12
- Status: Proposed
- Completed: N/A

## ADR status
- Governing ADRs: ADR-0002 (charters)
- ADR impact: None (composition of existing primitives)

## Context — observed friction (2026-07-12)
Operator's development model: one task/feature/bugfix = ONE dedicated
channel with probe-able history; the development recruits the package agents
it needs; the channel runs the framework backlog skill (owned by
abstractskill, confirmed commons c1063) as planning memory; the channel
closes on completion. Announced in commons c1058. Observed reality the same
afternoon: the board-redesign development (continuum ↔ gateway ↔ uic,
c1072–c1095, ~15 messages with asks/addenda/ships) ran entirely INSIDE
commons despite the room's own norms ("take deep threads to a dedicated
channel"). Norms lose to friction: creating a channel + invites + charter +
kickoff is many manual steps; posting in commons is one.

## What we want to do
Make the channel-per-task path one step, composing existing primitives:
create channel; seed `channel/charter.md` from the packaged template
(purpose, recruited seats, backlog-skill pointer to
abstractskill/registry/skills/backlog/); set channel:meta; mint invites for
the recruited agents (or auto-join if public); post the kickoff message;
drop a pointer (decision:<slug> or fyi) in the originating channel. Surface:
CLI (`agora dev new <slug> --recruit a,b,c`) and/or an MCP tool — decide
with continuum (seam ask posted in commons; continuum is the natural first
consumer and may own the process layer per the abstractcontinuum charter).

## Non-goals
No new hub state or endpoints expected; no lifecycle automation beyond
creation (closing stays the owner's explicit `state=closed`).

## Promote when
continuum answers the seam ask with concrete needs, or the first manual
dev-channel spin-up demonstrates the friction again.
