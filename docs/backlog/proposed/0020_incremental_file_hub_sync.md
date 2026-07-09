# Proposed: Incremental file→hub sync

## Metadata
- Created: 2026-07-08
- Status: Proposed
- Completed: N/A

## ADR status
- Governing ADRs: None
- ADR impact: None

## Context
The one-time migration script registers agents and creates channels fresh, so
re-syncing a file mailbox into an existing hub needs a clean DB and would clobber
hub-native state.

## Current code reality
- `examples/migrate_file_mailbox.py` is a full replay that assumes an empty hub.
- Migrated messages already store `source_id`/`original_date` in `data`, which an
  incremental importer could use to skip already-imported messages.

## Problem or opportunity
If any workflow keeps a file mailbox authoritative while also using the hub, the
hub goes stale with no safe re-sync.

## Proposed direction
An incremental importer that skips messages whose `source_id` is already present
and appends only new ones, without disturbing hub-native channels.

## Why it might matter
Only if a file mailbox and the hub must coexist. With cross-system named agents
meeting directly on the hub (the federation track), the hub is the source of
truth and this matters less.

## Promotion criteria
A concrete deployment that must mirror an external file log into a live hub.

## Validation ideas
Import a mailbox twice; assert no duplicates and no disturbance to hub-native
channels.

## Non-goals
Not a bidirectional sync engine; import direction only.

## Guidance for future agents
Reassess after the federation direction settles; may be unnecessary.
