# Planned: Federated named-agent identity + security path (Model A)

## Metadata
- Created: 2026-07-08
- Status: Planned
- Completed: N/A
- Area: identity / security / hub

## ADR status
- Governing ADRs: [ADR-0001](../../../adr/0001-federation-topology-and-handles.md)
  (Proposed) — topology + handle-as-metadata policy.
- ADR impact: Governed by ADR-0001. **Ratify ADR-0001 to Accepted before
  implementing** this item; the deferred alternatives it weighs are in
  `proposed/federation/` (`0040`–`0042`).

## Context
The maintainer's requirement: named entities on different systems (`castor@ip1`,
`janus@ip2`) meet on one Agora hub to share and discuss. The design pass ruled
**Model A** (one central meeting-point hub; `@host` is provenance metadata). The
foundation is largely there; the gaps are small, concrete hub features plus an
operator registration discipline.

## Current code reality
- Agent ids are flat lowercase-ASCII slugs; the id validator rejects `@`
  (`src/agora/hub/service.py` register-agent validation). No host/origin field,
  no routing, no federation.
- Auth: bearer key hashed at rest (`src/agora/db.py` register/agent_by_key),
  checked on every REST + WS call. WS accepts a query `?token=` as well as the
  `Authorization` header (`src/agora/hub/ws.py`); the client already prefers the
  header.
- Registration: single admin key registers any id (`src/agora/hub/http_api.py`
  `POST /agents`); MCP/CLI self-register any id if the admin key is present
  locally (`src/agora/mcp/server.py`, `src/agora/config.py`).
- Membership: `require_membership` gates all asset ops; self-service
  `leave_channel` exists; there is **no owner-initiated member removal**.
- Authorship: `signature`/`verified_by`/`authorship_required` are reserved and
  **not enforced** (`src/agora/models.py`, `service.py` `_prepare_structured` /
  `_validate_channel_meta`).

## Problem
For a trusted set on a network, the risks are operational: a long-lived admin key
that can register any id (id-squatting), no key rotation/revocation (a leaked key
is permanent until manual DB surgery), and no way for an owner to cut off a
departed/compromised member.

## What we want to do
Make one central hub safe for trusted cross-system named agents, without building
federation or PKI.

## Requirements
- **Owner-initiated member removal**: `POST /channels/{c}/members/{agent_id}/remove`
  (owner only) → `remove_member` + a system message. Ties asset access to current
  membership for eviction.
- **Key rotation/revocation**: `POST /agents/{id}/rotate-key` (admin or self) →
  new key, old hash invalidated; document emergency revoke.
- **Locked-down registration on an exposed hub**: an operator ceremony
  (pre-register `castor`/`janus` with the admin key, distribute `AGORA_API_KEY`
  out-of-band) and a way to disable promiscuous self-registration when the hub is
  network-facing.
- **Header-only WS auth**: deprecate the `?token=` query path; update
  `docs/protocol.md`/`docs/api.md` (currently still show the query param).
- **`@host` mapping**: do NOT parse `@` in the hub; document the convention that
  the AbstractFramework adapter maps `castor@ip1` → `{hub_id: "castor", origin:
  "ip1"}`, with the host in `about` or message `data.origin_host`.

## Suggested implementation
Two small endpoints (remove, rotate-key), a registration-policy switch
(env/flag), a WS-auth doc/code tightening, and an adapter doc. No id-schema change.

## Scope
Model A only. Trusted named entities on one operator-controlled hub over TLS.

## Non-goals
- Multi-hub federation / relay (Model B).
- PKI / OAuth / mTLS / DID.
- Enforced cross-host cryptographic authorship — deferred until hosts are
  mutually untrusting. When needed: per-agent keypairs, enforce
  `authorship_required`, verify `signature`; still not full PKI unless scale
  demands it.

## Dependencies and related tasks
- ADR for the topology/handle policy (write first).
- Shares `remove_member` groundwork with `0031` (asset eviction).
- Relates to `0022` (sign the ledger head) if authenticity is later required.

## Expected outcomes
- An operator can register named agents deliberately, rotate/revoke a key, and an
  owner can evict a member. `@host` is documented as metadata. WS auth is
  header-only. Self-registration cannot silently squat ids on an exposed hub.

## Validation
- Tests: owner-remove cuts a member's asset access; a rotated key authenticates
  and the old key is rejected; self-registration is refused under the
  locked-down policy; WS authenticates via header.
- Doc check: `@host` mapping and the registration ceremony are documented.

## Progress checklist
- [ ] ADR: topology + handle-as-metadata policy (maintainer sign-off).
- [ ] Owner-initiated member removal endpoint + test.
- [ ] Key rotate/revoke endpoint + test.
- [ ] Registration lock-down policy for an exposed hub + test.
- [ ] Header-only WS auth + doc update.
- [ ] AbstractFramework `@host` mapping doc.

## Guidance for the implementing agent
Keep the trusted-set boundary explicit; do not drift into hostile-multi-tenant
hardening. Re-check the current code before implementing and patch any backlog
drift.
