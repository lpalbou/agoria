---
name: coredoc
description: Create, audit, normalize, and maintain a professional external-facing repository documentation system for users, contributors, and tools, including the core doc set, cross-linked topic deep dives, and faithful AI-readable `llms.txt` and `llms-full.txt` files. Use when Codex needs to bootstrap docs for a new repo, repair stale or missing project docs, add or revise `docs/*.md` pages, keep root and `docs/` documents coherent, or regenerate AI-actionable documentation indexes for LLMs and tooling.
---

# Core Doc

Use this skill to make a repository explain itself clearly to external users, contributors, and
tools. Core docs should teach what the package is, how it works, how to use it, and what current
limits matter. Write in a professional, positive tone that addresses external readers directly.
Prefer faithful, maintainable docs over aspirational prose. If the code and docs disagree, the
code wins and the docs must be repaired.

## Start With The Right Pass

- If the repo already has documentation, inspect it before writing anything new. Preserve useful
  structure and tighten drift rather than replacing everything blindly.
- If the repo has no stable doc system, create the core set described in
  `references/core-doc-set.md`.
- If the task is mainly about creating or repairing `llms.txt` or `llms-full.txt`, read
  `references/llms-files.md` before editing.
- If the task is broad documentation maintenance, read
  `references/maintenance-playbook.md` and work through the audit flow.
- If the user is preparing or publishing a specific release, prefer the `release` skill when
  available. Use this skill for the release's user-facing documentation, changelog, and LLM index
  updates.

## Apply The Operating Rules

- Keep documentation faithful to the current repository. Do not describe features, APIs, or
  workflows that do not exist.
- Write as if you are speaking to an external user or contributor who needs clear guidance now.
  Prefer direct phrasing such as "you can", "use", and "see" where it improves clarity. Keep the
  tone professional, positive, and matter-of-fact rather than defensive, forensic, or
  self-referential.
- Write external-facing docs for users and contributors, not as project memory or a review of the
  team's mistakes. Explain current behavior, correct usage, guarantees, limits, and migration
  impact. Do not include repair narratives such as "the earlier value was bad observability" in
  README or topic docs. If old behavior matters for compatibility, describe it as a concise
  migration note without root-cause or blame narrative.
- Avoid time-relative or transition-heavy framing such as "current host", "active redesign path",
  "earlier host", "new path", or "now uses" in public docs unless the user explicitly asked for
  migration guidance. State the supported product plainly. Put timelines and step-by-step evolution
  in `CHANGELOG.md`, or in a tightly scoped FAQ entry when a compatibility question genuinely
  matters to users.
- If the product depends on one canonical named workflow, bundle, profile, route, or entrypoint,
  state that public name directly in the user docs where it affects setup or usage. Do not make
  readers infer the supported runtime surface from internal file names, ADRs, backlog items, or
  implementation notes.
- Prefer stable public examples over machine-specific ones. When the CLI supports a stable handle,
  repo id, relative path, or documented collection-style reference, use that instead of absolute
  local cache paths, snapshot hashes, home-directory paths, or other machine-specific examples in
  public docs.
- Do not explain maintainer implementation details in public docs when the user-facing takeaway is
  simply that a profile, route, or package now works. Examples that belong in backlog, ADRs,
  reports, or `untracked/comments/` instead of core docs include whether a package had to be
  rebuilt, which internal layers were kept at BF16 versus q8, which runtime carve-outs were added,
  or why an earlier experiment failed. In user docs, say what works, how to run it, what was
  measured, and what limits still matter.
- Every core documentation page must answer stable user or contributor needs, not internal
  incidents. This applies to `README.md`, `CHANGELOG.md`, root policy docs, `docs/*.md`,
  `docs/examples/*.md`, `llms.txt`, and `llms-full.txt`, not only FAQ pages. Do not add headings,
  callouts, notes, tables, captions, changelog entries, or example prose like "Why did our previous
  result...", "What went wrong...", "we discovered...", or "this failed before..." to end-user
  docs. Convert them into neutral usage guidance such as "How to compare memory measurements" or
  put the analysis in backlog, ADRs, reports, or `untracked/comments/`.
- Benchmark, quantization, and performance docs may include exact settings, hardware, command
  profiles, and metric definitions. They must not include personal commentary, blame, forensic
  narratives, release-gate drama, or explanations of documentation mistakes. If unrelated benchmark
  profiles should not be compared, state the supported comparison scope neutrally and keep the
  diagnostic history out of core docs.
- Do not surface maintainer-only commentary in core docs, including internal validation recipes,
  smoke-test instructions, "real model caveat" blocks, debugging narratives, or notes about how
  the documentation was generated. If that information matters only to the owner, maintainer, or
  developer, write it in `untracked/comments/<timestamp>_<topic>.md` instead, and keep it out of
  `README.md`, `CHANGELOG.md`, `docs/*.md`, `llms.txt`, and `llms-full.txt`.
- Keep the core doc set present even when a section is currently thin. If a doc is not yet
  applicable, say so explicitly instead of omitting it.
- `docs/architecture.md` MUST contain at least one diagram that represents the system
  architecture (components and how they connect). Add further diagrams whenever they help a
  reader grasp the package quickly — for example a data/message/communication flow, a request
  lifecycle, a state machine, or a deployment topology. Prefer Mermaid fenced code blocks
  (```mermaid) so the diagram renders on GitHub and common docs sites and stays diffable in
  version control; use an image only when a diagram genuinely cannot be expressed in Mermaid,
  and then commit the source alongside it. Keep diagrams faithful to the current code and
  labeled so they are understandable without the surrounding prose.
- Cross-link documents whenever one is a natural prerequisite, authority, or follow-up for another.
- Keep `docs/README.md` as the index for all `docs/*.md` pages, including topic deep dives.
- Treat `docs/<topic>.md` as first-class documentation, not orphan notes. Every topic page should
  be linked and explained from `docs/README.md`.
- Keep the public docs index focused on supported user and contributor guidance. Do not foreground
  internal notes, devnotes, backlog artifacts, or historical drafts from `docs/README.md` unless
  the user explicitly wants maintainer-facing material in the public index.
- Keep root docs and `docs/` docs aligned. If `README.md`, `docs/getting-started.md`, and
  `docs/architecture.md` disagree, fix the inconsistency in the same pass.
- When the repo has ADRs or backlog artifacts, link to them where they materially help readers
  understand policy, roadmap, or design boundaries.
- Put user-visible release history in `CHANGELOG.md`, limited to what changed, who is affected, and
  any migration or compatibility notes. Put process mistakes, root-cause analysis, and internal
  cleanup history in backlog, ADRs, reports, or incident notes. Do not let that internal history
  leak into README or topic docs.
- Default the license to MIT when a new repo has no stated license and the user has not requested
  something else. Use the current year or year range and the best available copyright holder name.
- Verify claims against repository evidence where possible: manifests, package metadata, entry
  points, CLI help, config files, schemas, examples, tests, and working commands.
- Before finishing any core-doc update, scan the external-facing corpus (`README.md`,
  `CHANGELOG.md`, root policy docs, `docs/*.md`, `docs/examples/*.md`, `llms.txt`, and
  `llms-full.txt`) for incident/postmortem language, including headings, callouts, table notes,
  image captions, changelog bullets, and examples. Remove or move anything that reads as maintainer
  memory rather than user guidance.

## Maintain The Core Set

- The default documentation profile is defined in `references/core-doc-set.md`:
  - `README.md`
  - `ACKNOWLEDGEMENTS.md`
  - `CHANGELOG.md`
  - `CODE_OF_CONDUCT.md`
  - `CONTRIBUTING.md`
  - `LICENSE`
  - `SECURITY.md`
  - `docs/README.md`
  - `docs/getting-started.md`
  - `docs/architecture.md`
  - `docs/api.md`
  - `docs/faq.md`
  - `docs/troubleshooting.md`
- For a new project, create the full default set unless the user explicitly asks for a smaller
  starter set or the repo is clearly internal and intentionally minimal.
- For an existing project, normalize missing or stale files incrementally instead of rewriting
  everything at once.

## Maintain `llms.txt` And `llms-full.txt`

- By default, keep both files at the repository root when using this profile.
- `llms.txt` is the concise index: a curated map of the most important documentation and package
  entry points for LLMs and tools.
- `llms-full.txt` is the expanded context file: a faithful, readable aggregation of the core
  documentation corpus in one place.
- Keep them AI-actionable:
  - clear project title and summary;
  - stable links or paths to key docs;
  - concise descriptions of what each doc is for;
  - enough structure for tools to fetch more detail quickly.
- Keep them faithful:
  - no invented capabilities;
  - no hidden policy not present in the real docs;
  - no stale links;
  - no drift from the current documentation set.
- Keep them external-facing:
  - same professional, positive tone as the source docs;
  - no maintainer-only notes or internal validation commentary;
  - no content copied from `untracked/comments/`.
- Treat them as discoverability aids, not the canonical documentation. Important instructions and
  caveats must live in the real docs first.
- Follow the format and usage notes in `references/llms-files.md`.

## Add Deep Dives When Relevant

- Create `docs/<topic>.md` when a topic is too important or too detailed to live only inside
  `README.md`, `docs/getting-started.md`, `docs/architecture.md`, `docs/api.md`, `docs/faq.md`, or
  `docs/troubleshooting.md`.
- Good topics include deployment, configuration, memory model, auth, provider behavior, CLI usage,
  local development, release process, and integration guides.
- Every deep-dive page must:
  - be linked from `docs/README.md`;
  - explain its relationship to the core docs;
  - avoid duplicating large blocks of text that should stay canonical elsewhere.

## Use References Selectively

- Read `references/core-doc-set.md` when creating or repairing the canonical doc set.
- Read `references/maintenance-playbook.md` when doing broad documentation audits or cleanup.
- Read `references/llms-files.md` when creating or updating `llms.txt` or `llms-full.txt`.
