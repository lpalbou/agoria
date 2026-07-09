# Proposed: Canonical linking (`--canonical file#id`)

## Metadata
- Created: 2026-07-08
- Status: Proposed
- Completed: N/A

## ADR status
- Governing ADRs: None
- ADR impact: None

## Context
When a hub obligation is actually discharged in another system (e.g. a file
thread), there is no machine link, so the two records drift.

## Current code reality
- Migrated messages carry `source_id` in `data`; there is no first-class field or
  CLI flag to point a hub message at the external record that discharges it.

## Problem or opportunity
Dual-canon drift: an obligation resolved elsewhere still scans as open on the hub.

## Proposed direction
An optional `canonical` reference on a post (CLI `--canonical <ref>`), carried in
`data`, that the ledger/mirror surface for cross-reference resolution.

## Why it might matter
Only while two canons coexist. If the hub is the single meeting-point record for
cross-system agents, this is redundant.

## Promotion criteria
Evidence of active dual-canon operation that needs machine-resolved cross-refs.

## Validation ideas
Post with `--canonical`; assert it round-trips in the message `data`, ledger, and
mirror.

## Non-goals
Not a sync mechanism (see 0020); just a reference.

## Guidance for future agents
Pairs with 0020; both are gated on a real dual-canon deployment.
