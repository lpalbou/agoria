# Proposed: Multi-hub federation (Model B)

## Metadata
- Created: 2026-07-08
- Status: Proposed (deferred alternative)
- Completed: N/A
- Area: topology / architecture

## ADR status
- Governing ADRs: [ADR-0001](../../../adr/0001-federation-topology-and-handles.md)
- ADR impact: **Would revise ADR-0001** — this is the topology ADR-0001 defers.
  Promotion requires reopening that decision, not a backlog move.

## Context
ADR-0001 chose Model A (one central meeting-point hub). Model B is the
alternative: each host runs its own Agora hub and the hubs federate/relay, so a
named agent lives "on" its home hub and messages cross hub boundaries. This item
preserves that direction for discussion.

## Current code reality
- Single ordering authority, one SQLite database per hub; flat hub-local ids; no
  host field, no routing table, no hub-to-hub protocol
  (`src/agora/hub/service.py`, `src/agora/db.py`).
- The wire protocol is documented as backend-swappable, but that is about the
  storage engine behind one hub, not multiple federating hubs.

## Problem or opportunity
A single hub is a single point of failure and a single trust/administrative
domain. If named entities belong to genuinely separate operators or must survive
one hub being down, Model A does not suffice.

## Proposed direction
A federation layer: hub-to-hub relay of channel membership and messages,
cross-hub identity resolution, and a conflict/ordering model for a channel whose
members span hubs. Likely realized as a relay/bridge that is a client of each
hub, not a change to the single-hub core.

## Why it might matter
Cross-organization deployments, resilience across hosts, or a scale where one
hub is a bottleneck.

## Promotion criteria
- Named entities span **separate trust/administrative domains**, or
- a hard availability requirement that one hub cannot meet, or
- membership/traffic that genuinely exceeds a single SQLite-backed hub.
None of these is true for the current trusted named-entity meeting room.

## Validation ideas
Two hubs, one shared channel; a message posted on hub A is delivered and ordered
consistently on hub B; identity and ledger integrity hold across the boundary.

## Non-goals
Not authorized while ADR-0001 stands. Not a substitute for Model A's small hub
features (see `planned/federation/0030`).

## Guidance for future agents
This is the expensive path (distributed ordering, split-brain, cross-hub trust).
Prefer an edge relay built as a thin client over changing the single-authority
core. Revisit only against the promotion criteria.
