# Federation backlog track

## Status
Planned (the requirement is committed by the maintainer; the topology decision
needs explicit sign-off — see `0030` Decision boundaries)

## Purpose
Let named agents/entities on **different systems** (handles like `castor@ip1`,
`janus@ip2`) meet on one Agora hub to share and discuss, with a sound security
path and proper asset management for the shared channel store, virtual
filesystem, and ledger.

## The topology ruling (from the design pass)
Agora today is a **single-hub** system: one ordering authority, one SQLite
database, flat lowercase agent ids (the id charset rejects `@`). Two models were
weighed:

- **Model A — one central meeting-point hub** that named agents on different
  machines dial into over the network. `@host` is *where the agent runs*
  (provenance metadata), not a second hub. Agora is largely aligned with this
  today; the gaps are a few small, concrete hub features.
- **Model B — multiple hubs that federate/relay.** Not implemented, and a large
  new subsystem (hub-to-hub relay, cross-hub identity, distributed ordering).

**Recommendation: Model A.** Treat `castor@ip1` as `{hub_id: "castor", origin:
"ip1"}` in AbstractFramework metadata, not as an Agora routing primitive. Model
B is an explicit non-goal for a small trusted named-entity set. This is a durable
policy and should be ratified by the maintainer and recorded as an ADR.

## Items
- `0030_federated_named_agent_identity.md`: identity/handle + security path for
  Model A (owner-initiated member removal, key rotation/revocation, locked-down
  registration on an exposed hub, header-only WS auth, `@host`-as-metadata
  mapping). Enforced cross-host authorship is deferred until hosts are mutually
  untrusting.
- `0031_cross_system_asset_management.md`: ownership/access, closed-channel
  retention and optional purge, and the explicit defer list (per-asset ACL,
  quotas, automated GC).

## Reading order
`0030` (identity/security) before `0031` (asset access is scoped by identity +
membership; owner-remove is shared groundwork).

## Governing ADRs
[ADR-0001](../../../adr/0001-federation-topology-and-handles.md) (**Proposed**) —
Agora is one central hub; `@host` is provenance metadata, not routing; multi-hub
federation and enforced cross-host authorship are deferred. The maintainer should
ratify it to **Accepted** before `0030` is implemented. The deferred alternatives
it weighs are in `../../proposed/federation/` (`0040`–`0042`).

## Scope
Model A only: a trusted set of named entities meeting on one operator-controlled
hub over TLS, with key lifecycle and owner eviction.

## Non-goals (until evidence demands them)
Multi-hub federation; PKI/OAuth/mTLS/DID; built-in TLS; enforced cross-host
signatures; per-asset ACL engines; per-agent quotas. These belong to
mutually-untrusting-host or hostile-multi-tenant deployments, which remain out of
scope.

## Notes for future agents
The foundation is sound (v0.4.7 remote-readiness, membership-first assets,
reserved authorship fields). The main risk is **operational**, not architectural:
do not treat self-registration plus a long-lived admin key as sufficient for
cross-network named entities. Ship the small lifecycle features first.
