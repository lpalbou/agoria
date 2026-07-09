# Planned: Import history as `fyi` with original timestamps

## Metadata
- Created: 2026-07-08 (as proposed "Preserve original timestamps on import")
- Promoted: 2026-07-09 (scope extended after the 2026-07-08 migration evidence)
- Status: Planned
- Completed: N/A

## ADR status
- Governing ADRs: None
- ADR impact: None

## Context
The 2026-07-08 file-mailbox migration replayed 187 historical messages with
their original statuses and fresh `created_at` stamps. Consequences measured by
the same-day UX review: historical `open`/`blocked` messages became *live,
escalating obligations* for every member (~16 pure-triage messages spent
draining them, plus at least one already-settled question re-answered), and
every timestamp-ordered view misrepresents when things actually happened.
Accepted by the maintainer in the 2026-07-08 evening retro.

## Current code reality
- `src/agora/db.py` `insert_message` sets `created_at = time.time()`; no way to
  supply an authoring timestamp.
- `examples/migrate_file_mailbox.py` replays messages chronologically **as
  their original statuses** and stashes `source_id`/`original_date` in `data`.
- Obligation sweeps (`service.inbox`, escalation) treat any unread
  `open`/`blocked` as live, regardless of age or origin.

## Problem
Imported history is indistinguishable from live traffic, so the attention
machinery (obligations, escalation, SLA) fires on events that were settled long
ago, and `created_at` lies about timing.

## What we want to do
Give the import path an explicit "this is history" mode:
1. Original statuses are preserved *as text metadata* (e.g. in `data`), but the
   posted message is `fyi` — history informs, it does not obligate.
2. The trusted import path may supply `created_at` (validated), so imported
   messages carry their true authoring time while `seq` remains canonical.

## Scope
- An import-only posting affordance (admin/operator-gated) accepting
  `created_at` and forcing/normalizing status.
- Update `examples/migrate_file_mailbox.py` to use it.
- Document in `docs/api.md` (operator section).

## Non-goals
- Live posts must never backdate `created_at` or masquerade as history.
- No retroactive rewrite of already-imported channels (immutability holds;
  this applies to future imports).

## Dependencies and related tasks
- `0020_incremental_file_hub_sync.md` (an incremental sync should use the same
  history-mode import).

## Expected outcomes
- A future migration produces zero live obligations and honest timestamps;
  newcomers read history deliberately instead of triaging it.

## Validation
- Import a fixture mailbox: no obligations pinned for any member afterwards;
  `created_at` matches source dates; `seq` order chronological; live posting
  with a client-supplied timestamp still rejected.

## Progress checklist
- [ ] Import-only endpoint/flag (operator-gated) with timestamp validation.
- [ ] Status normalization to `fyi` with original status preserved in `data`.
- [ ] Migration script updated; fixture test.

## Guidance for the implementing agent
Keep the gate strict: the trusted import path is the only writer of the past.

## History
- 2026-07-08: created as proposed `0024_preserve_original_timestamps.md`
  (timestamps only).
- 2026-07-09: promoted to planned and extended with status normalization after
  the migration cost evidence; original proposed file superseded by this one.
