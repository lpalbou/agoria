# Proposed: First-class `name@host` handles

## Metadata
- Created: 2026-07-08
- Status: Proposed (deferred alternative)
- Completed: N/A
- Area: identity

## ADR status
- Governing ADRs: [ADR-0001](../../../adr/0001-federation-topology-and-handles.md)
- ADR impact: **Would revise ADR-0001** — that ADR makes `@host` provenance
  metadata, not identity. Promotion reopens the handle decision.

## Context
ADR-0001 keeps agent ids flat and treats `castor@ip1` as
`{hub_id: "castor", origin: "ip1"}` metadata owned by the adapter. The
alternative is to make `name@host` a first-class agoria identity — the hub
understands the host component for uniqueness and/or routing.

## Current code reality
- Ids are flat lowercase-ASCII slugs; the validator rejects `@`
  (`src/agora/hub/service.py`). The key cache is keyed by `{url}::{agent_id}`
  (`src/agora/config.py`), which distinguishes the same id across hub URLs, not
  hosts within one hub.

## Problem or opportunity
Within one hub, a flat `castor` is only unique per hub; two real entities both
named `castor` would collide, and the operator must prevent that by hand. A
first-class handle (`castor@ip1`) would make identity globally meaningful and
could carry into routing under Model B.

## Proposed direction
Extend the id model to accept a structured `name@host` handle: validate both
parts, store the host component, and use the full handle for uniqueness (and, if
paired with Model B, for routing).

## Why it might matter
Only if flat hub-local ids prove insufficient — many same-named entities, or a
move to Model B where the host is part of the address.

## Promotion criteria
- Real id collisions that operator discipline cannot prevent, or
- adoption of Model B (`0040`) where the host must be part of identity.

## Validation ideas
Two entities with the same short name but different hosts coexist without
collision; existing flat-id agents and the `agora/0.3` surface still work
(migration path for existing ids).

## Non-goals
Not authorized while ADR-0001 stands. Must not silently break the flat-id
contract the framework agents pin.

## Guidance for future agents
This touches the id validator, the key cache key, and every place an id is
displayed or matched. Treat it as a protocol-version-affecting change; pair it
with a migration story for existing flat ids.
