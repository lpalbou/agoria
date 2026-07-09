# Federation alternatives (proposed, for discussion)

## Status
Proposed — the alternatives that [ADR-0001](../../../adr/0001-federation-topology-and-handles.md)
weighs and defers. Kept as memory so the decision can be revisited with evidence,
not re-derived from scratch.

## Purpose
ADR-0001 chooses **Model A** (one central hub; `@host` is provenance metadata)
and defers the bigger directions. These items record those deferred directions
so a future discussion has a concrete starting point, and so nobody quietly
implements one of them without revisiting the ADR.

## Items
- `0040_multi_hub_federation.md`: Model B — multiple hubs that federate/relay.
  The alternative topology ADR-0001 rejects for now.
- `0041_first_class_handles.md`: make `name@host` a first-class agoria identity
  (routing/uniqueness across hosts), the alternative to handle-as-metadata.
- `0042_enforced_cross_host_authorship.md`: enforce `signature`/`verified_by` with
  per-agent keypairs so a handle cannot be impersonated — the mutually-untrusting
  hosts path.

## Reading order
Read ADR-0001 first. Then `0040`/`0041` (topology + identity) before `0042`
(authorship builds on whichever identity model is chosen).

## Governing ADRs
[ADR-0001](../../../adr/0001-federation-topology-and-handles.md). Promoting any of
these to `planned/` requires an ADR revision, not just a backlog move.

## Non-goals
These are discussion artifacts, not commitments. None of them authorizes
implementation while ADR-0001 stands as Proposed/Accepted-Model-A.
