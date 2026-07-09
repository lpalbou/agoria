# Recurrent: Backlog and ADR hygiene

## Metadata
- Created: 2026-07-08
- Status: Recurrent
- Completed: N/A (runs repeatedly)

## Purpose
Keep the backlog faithful to the code and internally consistent, so a future
agent can trust it as planning memory.

## Run conditions
When adding, moving, or completing items; before a release; or at least whenever
the backlog is touched after code changes.

## Scope
`docs/backlog/overview.md`, item files, and lifecycle directories.

## Checklist
- [ ] Every item filename is `NNNN_slug.md` with a globally-unique number; no dates
      in filenames.
- [ ] `overview.md` counts, tables, and the completed ledger match the files on
      disk (fix count drift as a real bug).
- [ ] Each planned item still reflects current code reality; patch stale text.
- [ ] Any rule meant to outlive a task is captured in an ADR (or its absence is
      explained); no durable policy left buried only in item prose.
- [ ] Links to code, docs, and related items resolve.

## Expected output
An overview and item set that a future agent can execute from without the
original chat.

## Non-goals
Do not turn backlog items into public documentation; keep maintainer memory out
of `docs/README.md` and the core doc set.
