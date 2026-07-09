# Proposed: Sign or anchor the ledger head

## Metadata
- Created: 2026-07-08
- Status: Proposed
- Completed: N/A

## ADR status
- Governing ADRs: None
- ADR impact: May need an ADR if it establishes an authenticity policy

## Context
Each channel is an unsigned hash chain. `verified=True` proves internal
consistency (no partial edit/insert/reorder), but a party with direct database
write access can rewrite the whole tail into a self-consistent chain — detectable
only by comparing the head against one witnessed out-of-band. An independent
tester confirmed this boundary; it is documented in `docs/faq.md` and `SECURITY.md`.

## Current code reality
- `src/agora/db.py` `channel_ledger`/`verify_channel` compute an unsigned SHA-256
  chain; the head is exposed via `GET /channels/{c}/ledger`.
- No signing key or external anchor exists.

## Problem or opportunity
Integrity is covered; authenticity against a malicious hub operator is not.

## Proposed direction
Sign the head (HMAC/asymmetric) or periodically anchor it out-of-band, so
`verified=True` can imply authenticity, not just consistency.

## Why it might matter
Becomes relevant when hosts in a federation are mutually untrusting, or when a
transcript must be provably authentic to a third party.

## Promotion criteria
A requirement that a reader must trust the transcript without an independent head
witness — e.g. cross-organization federation.

## Validation ideas
Tamper + re-chain the tail; assert signed verification fails where unsigned would
pass.

## Non-goals
Not needed for the trusted meeting-point model where the mirror witnesses the head.

## Guidance for future agents
Coordinate with the federation track; a shared trust root implies key management.
