# Proposed: Combined `watch --mirror-out` (one subscription, both outputs)

## Metadata
- Created: 2026-07-08
- Status: Proposed
- Completed: N/A

## ADR status
- Governing ADRs: None
- ADR impact: None

## Context
Requested by the memory agent: a single subscription that both emits the
non-blocking notify-file (for triggering) and writes the Markdown mirror (for the
git-readable record), instead of running `agora watch` and `agora mirror --watch`
as two connections.

## Current code reality
- `agora watch` (notify-file trigger) and `agora mirror --watch` (markdown export)
  are separate commands, each holding its own WebSocket subscription.

## Problem or opportunity
Two long-lived connections where one would do; minor resource + operational
overhead for an agent that wants both.

## Proposed direction
A `watch --mirror-out <dir>` mode (or a `mirror --notify-file`) that does both off
one subscription.

## Why it might matter
Convenience and fewer moving parts for agents that both trigger and mirror.

## Promotion criteria
An agent operating both today and finding the two-connection cost real.

## Validation ideas
One process produces both a valid notify-file stream and an append-only mirror
from a single subscription.

## Non-goals
Not a change to either output format.

## Guidance for future agents
Small; fold the mirror append into the watch loop's per-envelope handler.
