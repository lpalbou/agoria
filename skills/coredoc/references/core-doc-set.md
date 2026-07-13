# Core Repository Documentation Set

Use this file when bootstrapping or normalizing a repository's documentation.

## Default Documentation Profile

This skill uses the following default profile for repository documentation. Treat it as the
preferred baseline, not a universal law for every tiny or internal repo.

## Core Files

### Root

- `README.md`
  - project identity, summary, audience, major capabilities, quick start, links to deeper docs
- `ACKNOWLEDGEMENTS.md`
  - credits, upstream lineage, inspiration, major borrowed work, sponsorship or thanks where relevant
- `CHANGELOG.md`
  - user-visible changes, version or date-based history, migration notes, release links if relevant
- `CODE_OF_CONDUCT.md`
  - contributor behavior expectations and reporting path
- `CONTRIBUTING.md`
  - development workflow, setup, tests, style expectations, PR guidance
- `LICENSE`
  - default to MIT unless the repo already uses or requires something else
- `SECURITY.md`
  - how to report vulnerabilities, support boundaries, disclosure expectations

### `docs/`

- `docs/README.md`
  - navigation hub for the docs tree; must list and explain all topic deep dives
- `docs/getting-started.md`
  - installation, first run, local setup, first successful workflow
- `docs/architecture.md`
  - system shape, major components, invariants, and design boundaries
  - MUST include at least one architecture diagram (components and their connections);
    add flow/lifecycle/topology diagrams when they aid understanding. Prefer Mermaid
    (```mermaid) fenced blocks so diagrams render on GitHub and docs sites and stay diffable.
- `docs/api.md`
  - public or internal API surface, or the canonical CLI/reference surface when the project is not
    API-first
- `docs/faq.md`
  - recurring user and contributor questions, including known limitations and confusion points
- `docs/troubleshooting.md`
  - symptom-oriented diagnosis and fixes for common setup, runtime, configuration, integration,
    packaging, and performance problems

## Generated AI-Readable Files

- `llms.txt`
  - concise index into the documentation corpus for LLMs and tooling
- `llms-full.txt`
  - expanded aggregate of the core docs when this profile is adopted

## Default Layout

```text
README.md
ACKNOWLEDGEMENTS.md
CHANGELOG.md
CODE_OF_CONDUCT.md
CONTRIBUTING.md
LICENSE
SECURITY.md
llms.txt
llms-full.txt
docs/
  README.md
  getting-started.md
  architecture.md
  api.md
  faq.md
  troubleshooting.md
  <topic>.md
```

## Cross-Link Expectations

- `README.md` should point to `docs/README.md`, `docs/getting-started.md`, `docs/architecture.md`,
  `docs/api.md`, `docs/faq.md`, `docs/troubleshooting.md`, `CONTRIBUTING.md`, `SECURITY.md`, and
  `CHANGELOG.md` when useful.
- `docs/README.md` should summarize the doc tree and list every `docs/<topic>.md`.
- `docs/getting-started.md` should link back to `README.md` and forward to `docs/architecture.md`
  or `docs/api.md` when those help the next step. It should link to troubleshooting for setup or
  first-run failures.
- `docs/architecture.md` should link to ADRs, topic deep dives, and API docs when relevant.
- `docs/api.md` should link to getting-started material, architecture context, and relevant
  troubleshooting entries where useful.
- `docs/faq.md` should link to canonical answers instead of duplicating long explanations, and
  should link to troubleshooting entries when the answer is a fix workflow.
- `docs/troubleshooting.md` should link back to the relevant setup, API, architecture, FAQ, or
  topic page for each symptom.
- `CONTRIBUTING.md` should point contributors to architecture, API, changelog, and security docs.

## Canonical Ownership Matrix

- `README.md`
  - owns the project overview, quick start, and the top-level doc map
- `CHANGELOG.md`
  - owns release history and user-visible change narrative
- `docs/getting-started.md`
  - owns the first successful workflow and setup details
- `docs/architecture.md`
  - owns system invariants, component boundaries, and design shape
- `docs/api.md`
  - owns API, CLI, RPC, config reference, or other main interface surface
- `docs/faq.md`
  - owns recurring conceptual questions, edge cases, limitations, and common support answers
- `docs/troubleshooting.md`
  - owns symptom-to-cause-to-fix workflows, diagnostics, logs, verification commands, and escalation
    paths
- `docs/<topic>.md`
  - owns reusable deep dives that would otherwise bloat the core docs

Backlog, ADRs, reports, and incident notes own internal reasoning history, rejected approaches,
postmortems, and root-cause narratives. Core docs are not project memory. They may link to ADRs or
design docs when a user needs the policy or architecture boundary, but they should not copy internal
mistake narratives into user instructions.

Maintainer-only notes, validation recipes, internal smoke-test commands, and documentation
generation comments belong in `untracked/comments/<timestamp>_<topic>.md`, not in the tracked core
documentation set.

## Minimum Content Standard

If a file is required but a topic is currently not mature, write the truthful minimal version:

- explain current status;
- state what is not yet present;
- link to the closest relevant document;
- avoid placeholder fluff.

## Front-Facing Content Filter

Before adding a sentence to `README.md`, `docs/*.md`, `llms.txt`, or `llms-full.txt`, ask whether an
external user, contributor, or tool needs it to understand what the package is, how it works, how to
install it, how to use it, how to configure it, how to debug it, how to migrate, or how to
contribute.

Write those docs in professional, positive prose that addresses readers directly when useful. Keep
the voice calm, clear, and externally oriented.

Prefer:

- "MLX cache token counts report the maximum effective layer offset/size."
- "Gemma4 MLX uses hybrid rotating and full KV cache layers, so local rotating-window sizes may
  differ from the effective cache length."

Avoid:

- "The earlier token count was bad observability."
- "We previously reported the wrong layer."
- "This was fixed after investigation."
- "Real model caveat" blocks that exist only to guide maintainers through internal smoke tests.

Those historical statements belong outside core docs. Use `CHANGELOG.md` only for the user-visible
fact that behavior changed, who is affected, and any migration impact. Put root cause and internal
process history in backlog, ADRs, reports, incident notes, or `untracked/comments/` maintainer
notes.

Examples:

- `docs/api.md`: “This project does not yet expose a stable public API. Current entry points are…”
- `ACKNOWLEDGEMENTS.md`: “No formal acknowledgements yet beyond the upstream projects listed…”
- `SECURITY.md`: “No dedicated security contact yet; report privately to…”

## Verification Hints

Before finalizing docs, verify against repository evidence such as:

- package manifests and metadata;
- executable entry points;
- CLI `--help` output;
- config files and schemas;
- example commands or scripts;
- tests, CI commands, and documented setup flows.

## License Default

For a new repository with no stated preference:

- create an MIT `LICENSE`;
- use the current year or year range;
- use the best available holder name from the repo owner, org, or package metadata;
- if ownership is genuinely ambiguous, call it out and avoid inventing a holder.
