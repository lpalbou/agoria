# Backlog Maintenance Checklists

Use this file when moving items across lifecycle states or when the backlog feels stale.

## Complete A Planned Item

1. Finish implementation, docs, and tests.
2. Run the strongest practical validation.
3. If the work introduced or revised a durable rule, create or update the governing ADR before
   closure, or record why ADR impact is still `None`.
4. Append `## Completion report` to the item.
5. Include date, summary, files or symbols touched, tests, docs updates, behavior changes,
   residual risks, backlog or code drift, follow-ups, and any priority impact.
6. Preserve `Created`, set `Status: Completed`, and set `Completed: <YYYY-MM-DD>`.
7. Move the file from `planned/` or `planned/<topic>/` to `completed/` or a matching completed
   topic folder if the repo uses completed tracks.
8. Update `overview.md` counts, tables, priorities, notes, and links.
9. Record the work in the completed-work ledger with original path, final path, dates, outcome,
   topic track when relevant, short comment, and key validation.
10. Search docs for stale links to the old path.
11. Run post-completion insight review.
12. Run post-completion follow-up triage for the new report and recent completed items only when
    the completion report produced real residual risk, uncertainty, or new opportunities.
13. Scan recurrent tasks and run any newly triggered passes.

## Deprecate A Planned Item

1. Append `## Deprecation report`.
2. Explain what replaced the item or why it should not be built.
3. Preserve `Created`, set `Status: Deprecated`, keep `Completed: N/A` unless it was already
   completed, and add `Deprecated: <YYYY-MM-DD>` if the repo uses that field.
4. Move the file from `planned/`, `planned/<topic>/`, `proposed/`, or `proposed/<topic>/` to
   `deprecated/` or a matching deprecated topic folder if the repo uses deprecated tracks.
5. Update `overview.md` counts, tables, notes, and links.
6. Search docs for stale links.
7. Scan recurrent tasks and run any newly triggered passes.

## Run Backlog And ADR Hygiene

Use this checklist after completing or deprecating work, before a release, after architecture
discoveries, or when multiple agents worked in the repo.

- Read `overview.md`.
- Check `planned/`, `proposed/`, `completed/`, `deprecated/`, and `recurrent/`.
- Include nested topic tracks such as `planned/<topic>/` and `proposed/<topic>/`.
- Verify overview counts and priority ordering.
- Verify that overview counts match on-disk reality for every state bucket.
- Verify every backlog item filename starts with a globally unique four-digit `NNNN_` prefix across
  root lifecycle folders and all topic subfolders. In legacy three-digit repos, treat `NNN` and
  `0NNN` as the same numeric identifier while auditing, and use four digits for any new or renamed
  item.
- Flag date-prefixed or unnumbered backlog item files such as `YYYY-MM-DD_slug.md` or `slug.md`.
  Dates belong in item metadata and reports, not filenames.
- Verify topic README files exist for multi-item tracks and that nested items are listed from both
  the topic README and the main overview.
- Verify each item has coherent metadata and that completed items have completion reports.
- Verify architecture-significant backlog items have explicit ADR state rather than only generic
  dependency prose.
- Verify recent completion-report follow-ups are cross-referenced, triaged, or explicitly stale.
- Verify completed and deprecated items live in the correct directories.
- Check for duplicate copies of the same item across lifecycle directories unless the duplication is
  clearly intentional and explained.
- Sample planned items against current code and docs. Update stale items before anyone implements
  against them.
- Search for stale links to moved backlog files, including topic subfolder paths.
- Review ADRs for decisions that are no longer true, unenforced, or missing validation.
- Verify accepted ADRs link back to implementing, adoption, or drift-tracking backlog items, or say
  explicitly that they currently have no backlog impact.
- Check for silent fallbacks, silent truncation, hidden timeout behavior, or similar silent
  degradation introduced by recent work.
- Tell the user which insights should become backlog or ADR updates.

## Run Post-Completion Follow-Up Triage

Review recent completed items and classify each follow-up signal as:

- already covered by planned work;
- already covered by proposed work;
- documentation or process note only;
- stale because later work resolved it;
- new proposed work worth preserving;
- urgent planned work that should bypass `proposed/`.

Prefer `proposed/` for uncertain signals. Promote directly to `planned/` only when evidence shows
that the risk is urgent, blocking, or already well understood.

## Avoid Common Backlog Failures

- Do not write backlog items from memory without inspecting the code.
- Do not treat backlog text as more authoritative than the repository.
- Do not let vague ideas inflate `planned/`.
- Do not silently lose history by overwriting or deleting old intent.
- Do not reuse numeric prefixes inside topic subfolders. The prefix is a global item identifier,
  not a local sort key.
- Do not create date-prefixed or unnumbered backlog item filenames. Use `NNNN_slug.md` only.
- Do not mark work complete without validation and a completion report.
- Do not let recurrent process tasks disappear once the first cleanup pass lands.
