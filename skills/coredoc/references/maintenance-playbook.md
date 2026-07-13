# Documentation Maintenance Playbook

Use this file for broad repository documentation work.

## Audit Flow

1. Inspect current docs, README, package metadata, build files, scripts, and entry points.
2. Compare reality against the core set in `core-doc-set.md`.
3. Gather evidence before making claims:
   - manifests and package metadata;
   - executable entry points;
   - CLI help or command surfaces;
   - config files, schemas, and environment variables;
   - tests, CI commands, and documented example workflows.
4. Identify:
   - missing files;
   - stale claims;
   - conflicting explanations;
   - broken links;
   - orphan `docs/<topic>.md` pages;
   - missing `llms.txt` / `llms-full.txt`;
   - docs that should exist but are crammed into README only.
5. Fix the highest-value inconsistencies first:
   - installation and first-run instructions;
   - missing or stale troubleshooting for common user-facing failures;
   - architecture or API drift;
   - missing contributor/security/license basics;
   - broken AI-readable indexes.

## Writing Rules

- Prefer short, concrete prose over marketing language.
- Use a professional, positive tone that addresses external users and contributors directly when it
  helps clarity.
- Use absolute claims only when the repo supports them.
- Separate current behavior from future plans.
- Keep front-facing docs focused on current user value: what the package is, how it works, how to
  use it, and what limitations matter. Do not narrate internal mistakes, debugging history, or why
  an earlier implementation was wrong.
- Keep maintainer-only notes out of tracked core docs. Internal validation commands, private
  reminders, documentation-generation comments, and smoke-test caveats belong in
  `untracked/comments/<timestamp>_<topic>.md`.
- Preserve one canonical place for each concept. Link rather than duplicate when possible.
- If a design is governed by ADRs, link the relevant ADRs instead of restating all policy.

## User-Facing Rewrite Rules

When documentation is updated after a bug fix, observability fix, or architecture correction:

- describe the current behavior and any user-visible migration impact;
- include old behavior only as compatibility context when users may have depended on it or need to
  interpret older outputs;
- put a concise user-visible fix or migration note in `CHANGELOG.md` when appropriate;
- move root cause, "what went wrong", and internal blame/history to backlog, ADR, report, or
  incident notes;
- move maintainer-only validation guidance and similar internal notes to
  `untracked/comments/<timestamp>_<topic>.md`;
- remove temporary wording such as "earlier", "previously broken", "bad observability", "we fixed",
  and "after investigation" from README and topic docs.

## Deep-Dive Election Rules

Create `docs/<topic>.md` when:

- the topic is important to correct usage or maintenance;
- the explanation would bloat a core doc;
- the topic has enough independent structure to deserve its own page;
- multiple core docs would otherwise repeat the same explanation.

Do not create a topic page for trivial one-paragraph notes that belong in FAQ or README.

## Troubleshooting Rules

Use `docs/troubleshooting.md` for user-facing failure modes that benefit from a fix workflow. Keep
`docs/faq.md` for conceptual questions, recurring confusion, limits, and short answers.

Each troubleshooting entry should usually include:

- the symptom a user can recognize;
- likely causes;
- checks or commands that confirm the cause;
- the fix or workaround;
- how to verify recovery;
- links to the canonical setup, API, configuration, architecture, FAQ, or topic page.

Do not turn troubleshooting into an internal postmortem. Mention older behavior only when users
need it to interpret logs, migration impact, or compatibility boundaries.

## Completion Checklist

- Every required core file exists or has been intentionally and truthfully minimized.
- Root docs and `docs/` docs agree on the project’s current shape.
- Installation and example commands were checked against runnable or inspectable repo evidence.
- `docs/troubleshooting.md` covers known user-facing setup, runtime, configuration, integration, or
  packaging failures when the repo has enough evidence to document them.
- `docs/README.md` lists every topic deep dive with a short explanation.
- `README.md` points readers into the docs tree.
- `llms.txt` and `llms-full.txt` match the current docs corpus.
- Links resolve and point to the canonical target.
- Front-facing docs do not contain internal mistake narratives. Changelog entries, when needed,
  state only user-visible changes and migration impact.
- Front-facing docs do not contain maintainer-only validation recipes, smoke-test caveats, or
  documentation-generation comments.

## Common Failures

- README claims features that only exist in backlog or roadmap.
- `docs/api.md` omits the real entry points or public surface.
- `docs/README.md` exists but does not actually index the docs tree.
- topic deep dives are added but never linked.
- known user-facing failures are buried in FAQ, changelog, issues, or README instead of a focused
  troubleshooting page.
- `llms.txt` lists docs that no longer exist or no longer matter.
- `llms-full.txt` contains stale or duplicated material instead of a faithful aggregate.
- topic docs include ephemeral repair commentary instead of stable current behavior.
- generated docs leak maintainer-only notes, test recipes, or internal caveats into external
  documentation.
