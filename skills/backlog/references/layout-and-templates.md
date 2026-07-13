# Backlog Layout And Templates

Use this file when creating a backlog system or when a repository's current backlog needs stronger
structure.

## Recommended Layout

```text
docs/
  backlog/
    overview.md
    planned/
      0001_roadmap.md
      0010_first_task.md
      speech/
        README.md
        0020_runtime_foundation.md
        0030_provider_integration.md
    proposed/
      0040_future_idea.md
      scenema/
        README.md
        0044_package_owned_directed_speech_request_and_capabilities.md
        0045_shared_runtime_foundation_for_advanced_speech_engines.md
    completed/
    deprecated/
    recurrent/
      README.md
      backlog-and-adr-hygiene.md
      post-completion-follow-up-triage.md
```

Every backlog item filename must start with a four-digit global ID prefix:
`NNNN_<short_descriptive_slug>.md`. Use four-digit numeric prefixes as global backlog item
identifiers, not folder-local counters. A prefix such as `0044` should refer to one durable backlog
item across `planned/`, `proposed/`, `completed/`, `deprecated/`, and every topic subfolder. Leave
gaps so urgent work can be inserted without renumbering everything.

Do not put dates in backlog item filenames. Put dates inside the file metadata instead:

- `Created: <YYYY-MM-DD>`
- `Completed: <YYYY-MM-DD | N/A>`
- `Deprecated: <YYYY-MM-DD>` when applicable
- completion or deprecation report dates

Before creating a new numbered item, scan every backlog lifecycle directory and nested topic
folder for existing `NNNN_*.md` or `NNNN-*.md` files, then choose the next unused global number.
For legacy repos that already use three-digit prefixes, also scan `NNN_*.md` and `NNN-*.md`, treat
`044` as the same numeric identifier as `0044` for uniqueness checks, and use `0044_...` for any
new or renamed item. Do not restart numbering inside `planned/<topic>/` or `proposed/<topic>/`.

Invalid item filenames:

- `2026-05-20_audio-capability-matrix.md`
- `audio-capability-matrix.md`
- `044_audio-capability-matrix.md` for new items

Valid item filenames:

- `0044_audio_capability_matrix.md`
- `0721_runtime_ready_multimodal_package.md`

Topic subfolders are allowed and encouraged when several backlog items belong to one larger track,
feature family, initiative, package, or investigation. Valid examples include:

- `docs/backlog/planned/<topic>/README.md`
- `docs/backlog/planned/<topic>/<NNNN>_<item>.md`
- `docs/backlog/proposed/<topic>/README.md`
- `docs/backlog/proposed/<topic>/<NNNN>_<item>.md`

Use a topic subfolder when it improves navigation or keeps related decisions together. Do not use a
subfolder for a single isolated item unless more related items are expected soon.

Each topic subfolder should include a short `README.md` that states:

- the purpose of the track;
- why the items are grouped;
- whether the track is planned, proposed, or mixed across lifecycle states;
- the intended reading or implementation order;
- relevant ADRs, docs, modules, and parent backlog items;
- any explicit non-goals for the track.

The main `overview.md` remains the canonical backlog map. It must list or summarize topic tracks,
include nested items in counts, and link to both the topic README and important child items.

For a small repo or one-off workflow, minimum viable layout is:

```text
docs/
  backlog/
    overview.md
    planned/
    completed/
```

Add `proposed/`, `deprecated/`, and `recurrent/` as soon as uncertainty, supersession history, or
repeated maintenance becomes real.

## `overview.md` Contents

Keep `overview.md` as the long-term planning memory. Include:

- a plain-language project summary;
- current counts for planned, proposed, completed, deprecated, and recurrent work;
- next recommended work or priority bands;
- a table or ledger of planned items;
- a table of proposed items with promotion criteria or rationale;
- a table or short section for topic tracks, with links to their README files and child items;
- enough item IDs or paths for a reader to find each backlog item by its global number;
- a completed-work ledger with original path, final path, dates, outcome, comment, and key
  validation;
- a table or list of deprecated items with reason;
- the completion, deprecation, recurrent-scan, and adding-new-item process;
- planning notes and major backlog-state changes.

## Planned Item Template

Required core for any planned-item variant:

- metadata;
- context;
- current code reality;
- problem or goal;
- scope and non-goals;
- expected outcomes;
- validation;
- explicit ADR state.

```markdown
# Planned: <title>

## Metadata
- Created: <YYYY-MM-DD>
- Status: Planned
- Completed: N/A

## ADR status
- Governing ADRs: <ADR-XXXX, ADR-YYYY | None>
- ADR impact: <None | Needs new ADR | May revise existing ADR | Known drift tracked by <item>>

If `ADR impact` is not `None`, create or revise the ADR with the `adr` skill when available. The
ADR should explain `Context` and `Decision` before optional metadata or implementation inventory.

## Context
What exists now, why this matters, and where to look.

## Current code reality
Files or symbols inspected, behavior already implemented, behavior missing or brittle, and
assumptions to re-check before implementation.

## Problem
What is wrong, missing, confusing, unsafe, or inefficient.

## What we want to do
The intended outcome in plain language.

## Why
Why this matters for users, maintainers, correctness, or strategy.

## Requirements
Concrete behavior and constraints.

## Suggested implementation
Likely approach, without forbidding a better code-first design.

## Scope
What this task includes.

## Non-goals
What this task must not do, and why.

## Dependencies and related tasks
Backlog, ADR, docs, modules, tests, and decisions to read first.

## Expected outcomes
What should be true when the task is complete.

## Validation
A/B/C tests, commands, manual checks, docs checks, or harness steps.

## Progress checklist
- [ ] Small, trackable steps.

## Guidance for the implementing agent
Re-check current code, prefer clean and explicit designs, and report backlog or code drift.
```

Optional sections when they materially help:

- `Plain description`
- `Area`
- `Version`
- `Decision boundaries`
- `Acceptance criteria`
- `Recent validation`
- `Decision summary` or `Strategy` when the item compares options before choosing one

## Proposed Item Template

```markdown
# Proposed: <title>

## Metadata
- Created: <YYYY-MM-DD>
- Status: Proposed
- Completed: N/A

## ADR status
- Governing ADRs: <ADR-XXXX, ADR-YYYY | None>
- ADR impact: <None | Needs new ADR | May revise existing ADR | Known drift tracked by <item>>

## Context
The current project state and evidence that make the idea worth remembering.

## Current code reality
Files, symbols, behaviors, or docs inspected before writing the proposal.

## Problem or opportunity
What might matter later.

## Proposed direction
The idea, without treating it as committed implementation.

## Why it might matter
Why this is worth preserving.

## Promotion criteria
What evidence or dependency changes would justify promotion to `planned/`.

## Validation ideas
What should be tested, measured, or inspected before promotion.

## Non-goals
What this proposal does not authorize.

## Guidance for future agents
How to reassess the idea later.
```

Use `proposed/` for residual risks, architectural options needing more evidence, low-confidence
optimizations, or experiments whose decision boundary is not settled.

## Topic Track README Template

Use this for `planned/<topic>/README.md` or `proposed/<topic>/README.md` when a larger effort is
split into several backlog items.

```markdown
# <Topic> backlog track

## Status
<Planned | Proposed | Mixed>

## Purpose
Why these items are grouped and what larger outcome they support.

## Items
- `<NNNN>_<item>.md`: one-line purpose and current state. `NNNN` must be globally unique across
  the whole backlog, not only this topic folder. Dates stay inside each item file, not in names.

## Reading order
Recommended sequence for future agents.

## Governing ADRs
Relevant ADRs, or `None identified after review`.

## Scope
What this track includes.

## Non-goals
What this track does not authorize.

## Notes for future agents
Current uncertainties, promotion criteria, sequencing constraints, or implementation cautions.
```

Topic README files are indexes, not replacements for item files. Each child item still needs the
core backlog signals: context, code reality, scope, non-goals, validation, and ADR state.

If a repo already uses a lighter local format, keep the core signals even if headings differ:

- summary or context;
- current code reality;
- reason or problem;
- scope and non-goals;
- dependencies;
- expected outcomes;
- validation or tests.
- ADR state.

## Recurrent Task Template

```markdown
# Recurrent: <title>

## Metadata
- Created: <YYYY-MM-DD>
- Status: Recurrent
- Completed: N/A (runs repeatedly)

## Purpose
Why this recurring pass exists.

## Run conditions
When to run it and an optional fallback cadence.

## Scope
What this task may update.

## Checklist
- [ ] Concrete repeatable steps.

## Expected output
What the pass should produce.

## Non-goals
What this pass must not do.
```

At minimum, keep recurrent tasks for backlog/ADR hygiene and post-completion follow-up triage.

## Completion And Deprecation Reports

Do not create standalone templates for completed or deprecated items from scratch. Treat them as
planned items with appended reports:

- append `## Completion report` before moving to `completed/`;
- append `## Deprecation report` before moving to `deprecated/`.

See `maintenance-checklists.md` for the exact move/update flow.
