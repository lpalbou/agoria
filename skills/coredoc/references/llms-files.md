# `llms.txt` And `llms-full.txt`

Use this file when creating or updating AI-readable repository documentation indexes.

## What They Are

From the `llms.txt` proposal at `llmstxt.org`:

- `llms.txt` is a root-level Markdown file intended to help LLMs use a website or documentation
  corpus at inference time.
- The core structure is:
  - H1 title
  - blockquote summary
  - optional explanatory prose
  - H2 sections containing Markdown link lists

Mintlify's docs show a practical paired pattern used by some documentation tooling:

- `llms.txt` as the concise documentation index
- `llms-full.txt` as one expanded file containing the full documentation context

These files are useful because tools and models can discover the important docs quickly without
having to parse complex HTML or guess which pages matter.

## Repository Guidance

For this documentation profile, default to both files at the repo root:

- `llms.txt`
- `llms-full.txt`

If the project has published docs URLs, prefer canonical absolute URLs.

If the project is repo-first and has no stable hosted docs, use stable repository-relative Markdown
paths or canonical repository URLs consistently. Do not mix arbitrary path styles in one file.

## `llms.txt` Requirements

Keep it concise and curated.

Recommended shape:

```markdown
# Project Name

> One short summary of what the project is and how to use the docs.

Optional guidance paragraphs.

## Core Docs
- [README.md](README.md): project overview and quick start
- [docs/getting-started.md](docs/getting-started.md): setup and first run
- [docs/architecture.md](docs/architecture.md): system design and invariants
- [docs/api.md](docs/api.md): API or CLI surface
- [docs/faq.md](docs/faq.md): common questions and limitations
- [docs/troubleshooting.md](docs/troubleshooting.md): common symptoms, diagnostics, and fixes

## Contributing
- [CONTRIBUTING.md](CONTRIBUTING.md): contributor workflow
- [SECURITY.md](SECURITY.md): vulnerability reporting

## Topic Deep Dives
- [docs/<topic>.md](docs/<topic>.md): why this topic matters

## Optional
- [CHANGELOG.md](CHANGELOG.md): release history
- [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md): credits and lineage
```

Rules:

- Keep section names meaningful.
- Use short link descriptions that tell an agent why to open the page.
- Put secondary material in `Optional` when it is not needed for a short context.
- Do not turn `llms.txt` into a complete prose manual. It is an index, not the full corpus.
- Keep the same professional, positive, external-facing tone as the tracked source docs.
- Do not include maintainer-only notes, internal validation commands, or content copied from
  `untracked/comments/`.

## `llms-full.txt` Requirements

Keep it faithful and readable.

Recommended shape:

```markdown
# Project Name

> One short summary.

## Document Index
- short linked index mirroring `llms.txt`

---

## README.md
<faithful content or normalized extract>

---

## docs/getting-started.md
<faithful content or normalized extract>
```

Rules:

- Include the same core corpus referenced by `llms.txt`, scoped to the most important docs by
  default.
- Preserve meaning when normalizing formatting.
- Do not inject hidden instructions, speculative plans, or undocumented claims.
- Do not inject internal repair history or ephemeral postmortem text from changelogs, backlog,
  reports, or chat. `llms-full.txt` should teach what the package is, how it works, and how to use
  it, not preserve how the project got there.
- Do not aggregate maintainer-only notes from `untracked/comments/`, internal smoke-test blocks, or
  documentation-generation commentary.
- Prefer document separators so tools and humans can navigate the aggregate.
- Keep duplicated content low; if two docs repeat heavily, consolidate the real docs first.
- Do not blindly concatenate huge, repetitive, or sensitive material. Link out when a bounded
  aggregate is more useful than a giant dump.

## Faithfulness Rules

- Only include documents that currently exist.
- Keep summaries aligned with the real docs.
- Regenerate after meaningful documentation changes.
- Regenerate after changes to setup flow, CLI/API surface, configuration, release process, or
  topic deep dives included by the file.
- If a doc says a feature is absent or unstable, `llms.txt` and `llms-full.txt` must say the same.
- If an API, CLI, or integration changed, update the core docs before or together with the LLM
  index files.
- If the source docs intentionally omit internal mistake history, do not reintroduce that history
  in the LLM index files.
- If maintainers need extra internal guidance, keep it in `untracked/comments/<timestamp>_<topic>.md`
  and out of the LLM index files.

## Important Caveat

These files are discoverability aids, not canonical documentation. Some consumers may ignore them.
Never place important instructions, caveats, or policy only in `llms.txt` or `llms-full.txt`.

## Why This Matters

The official proposal frames `llms.txt` as inference-time help for LLMs using documentation.
Mintlify's implementation shows a practical pattern already used in documentation tooling:

- concise top-level discovery via `llms.txt`
- full-context ingestion via `llms-full.txt`

This skill treats that pattern as a pragmatic repository convention, even when docs are not hosted
by Mintlify.
