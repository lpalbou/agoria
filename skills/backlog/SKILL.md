---
name: backlog
description: Create, audit, normalize, and maintain backlog artifacts that track execution-planning work, implementation history, and follow-up triage. Use when Codex needs to set up a backlog system, write or revise backlog items, update backlog overviews or ledgers, move work between planned/proposed/completed/deprecated states, run backlog hygiene, or preserve post-completion follow-ups. Do not use backlog alone to define durable cross-task policy; cite or escalate relevant ADRs instead.
---

# Backlog System

Use the backlog as durable planning memory, not as authority over the code. Keep enough history
that a later agent can answer what was built, what is next, what was considered, what should not
be built, why priorities changed, and what evidence proved completion.

## Start With The Right Pass

- If asked to create a backlog system from scratch, read `references/layout-and-templates.md`
  first and establish the directory layout, overview, and recurrent tasks before adding many
  items.
- If asked to add or revise a backlog item, inspect the current code and docs first. Then read
  `references/layout-and-templates.md` for the correct item shape.
- If asked to complete or deprecate work, read `references/maintenance-checklists.md` first so
  history, ledgers, links, and follow-ups are preserved.
- If asked to clean up, normalize, triage, or sync the backlog, run the hygiene and follow-up
  flows in `references/maintenance-checklists.md`.

## Apply The Operating Rules

- Read the repository before writing backlog text. Treat stale backlog text as a bug.
- Keep every item standalone enough for a future agent to execute without the original chat.
- `backlog` owns work-item lifecycle, planning state, and implementation history. `adr` owns
  durable cross-task policy.
- Separate committed work from speculative work:
  - `planned/` for intended implementation work.
  - `proposed/` for plausible but uncommitted ideas, risks, or experiments.
  - `completed/` for closed audit records.
  - `deprecated/` for superseded, rejected, or indefinitely deferred work.
  - `recurrent/` for periodic process tasks.
- Keep one durable overview that records counts, priorities, next recommended work, ledgers, and
  operating rules.
- Every backlog item file must start with a four-digit global ID prefix: `NNNN_<slug>.md`. This is
  mandatory across `planned/`, `proposed/`, `completed/`, `deprecated/`, and topic subfolders.
  A number such as `0044` should identify one durable backlog item for search and references.
- Do not put dates in backlog item filenames. Dates belong inside item metadata such as `Created`,
  `Completed`, `Deprecated`, or completion reports.
- Preserve history instead of rewriting it away. Move items across states and append reports; do
  not silently replace earlier intent.
- Cross-reference relevant ADRs, docs, code, tests, and related backlog items.
- If a backlog item creates a rule that should outlive the task, do not leave that rule buried in
  backlog prose. Create or update an ADR before closure, or record explicit ADR state explaining
  why not.
- When creating or updating an ADR from backlog work, use the `adr` skill when available and keep
  the ADR reader-first: title, status, `Context`, then `Decision` before optional metadata.
- Use topical subfolders when several backlog items form one larger track. `planned/<topic>/...`
  and `proposed/<topic>/...` are valid when the topic README explains the track and the main
  overview still indexes the items.
- Prefer one focused problem per item. Split oversized items instead of hiding multiple decisions
  inside one file.
- Record explicit validation expectations. A backlog item is not done because code changed; it is
  done because required behavior and evidence landed.
- After completion, review residual risks, open questions, optimization ideas, documentation gaps,
  and architecture insights. Preserve only the useful signals.
- Tell the user when backlog and code disagree, and patch the backlog before implementation unless
  the user explicitly overrides that process.

## Write Or Revise Items

- Use the planned-item template in `references/layout-and-templates.md` for committed work.
- Use the proposed-item template in `references/layout-and-templates.md` for ideas that deserve
  memory but are not implementation commitments.
- Keep `Current code reality` or equivalent code-audit notes in every new or materially revised
  planned item.
- Allow lightweight item variants only when they still preserve the same core signal: summary,
  reason, scope, dependencies, expected outcomes, current code reality, and validation.
- State scope and non-goals explicitly so future agents know what not to build.
- Prefer decision-grade explanation when an item changes architecture, orchestration, safety,
  routing, security, cost, or other consequential system behavior.
- Add optional sections only when they improve clarity: `Plain description`, `Area`, `Version`,
  `Decision boundaries`, `Acceptance criteria`, or `Recent validation`.
- When splitting a larger effort into several related items, create a topic track under the
  appropriate lifecycle directory instead of flattening every item into one long list.
- Assign each new item the next unused global `NNNN` prefix and name it
  `NNNN_short_descriptive_slug.md`. Do not restart numbering inside a topic subfolder. Do not use
  `YYYY-MM-DD_...`, unnumbered slugs, or folder-local numbering.
- In mixed cases, use backlog first when the primary job is execution planning, sequencing,
  triage, or completion history. Use ADR first only when the primary job is to establish or revise
  durable policy.

## Update The Backlog As A System

- Update `overview.md` in the same pass whenever counts, priorities, item states, or ledgers
  change.
- Include topic-track items in counts, ledgers, and priority lists. Do not let nested backlog files
  become invisible because they live below `planned/<topic>/` or `proposed/<topic>/`.
- Check filename compliance and global numeric-prefix uniqueness when adding, moving, or auditing
  items. Rename or flag item files that lack `NNNN_`, reuse a number, or start with a date.
- Treat overview or ledger count drift as a real backlog bug and fix it during the same hygiene
  pass.
- Keep completed work visible. Record original planned paths, final paths, dates, outcomes,
  comments, and key validation.
- Prefer `proposed/` for uncertain follow-ups. Promote directly to `planned/` only when evidence
  shows urgency, blocking risk, or a clear implementation mandate.
- Run recurrent tasks when their triggers apply. At minimum, keep backlog/ADR hygiene and
  post-completion follow-up triage alive.
- Search for stale links after moving files.

## Adapt Without Losing The Invariants

- If the repository already has a backlog system, preserve its local conventions unless they block
  traceability, code-first planning, or reliable handoff.
- If the existing system is looser, upgrade it incrementally toward explicit lifecycle states,
  overview-led planning, completion reports, and recurrent hygiene.
- For small repos or one-off work, use the minimum viable layout and required core fields from
  `references/layout-and-templates.md` instead of forcing the full governance shape immediately.
- If another project has useful patterns, borrow them selectively. Good additions include package
  or area metadata, plain-language summaries, acceptance criteria, decision boundaries, and
  incident-specific completed records tied to a concrete run, report, or failure. Do not import
  weaker habits such as duplicate planned and completed files, vague status-only items, or items
  with no code reality or validation.

## Use References Selectively

- Read `references/layout-and-templates.md` when creating or reshaping backlog files.
- Read `references/maintenance-checklists.md` when closing work, deprecating work, or running
  backlog hygiene and follow-up triage.
