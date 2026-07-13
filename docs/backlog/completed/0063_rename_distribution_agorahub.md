# Completed: rename the distribution to agorahub (presentation only)

## Metadata
- Created: 2026-07-12
- Status: Completed (operator ruling 2026-07-12; executed 2026-07-13)
- Completed: 2026-07-13
- Area: packaging/docs

## ADR status
- Governing ADRs: None
- ADR impact: None (naming, not architecture; the stable integration surface
  is explicitly unchanged)

## Context
Operator ruling: the project presents as **Agora Hub** (call it "Agora" for
short); the PyPI distribution is **`agorahub`** (one word, no separator —
the cleaner handle, and it matches the GitHub repo name). Every tool,
command, import, env var, config path, and wire name **stays `agora`**. Only
the presentation/distribution name changed (was `agoria` on PyPI, briefly
`agora-hub` during this rename before the operator chose the un-hyphenated
`agorahub`).

## What shipped
1. `pyproject.toml`: `name = "agorahub"` (version stays dynamic from
   `agora.__version__`); naming comment + URLs updated.
2. Presentation sweep of `agoria`/`Agoria` -> `agorahub`/"Agora Hub"/"Agora"
   across README, docs/, llms.txt/llms-full.txt, CONTRIBUTING, SECURITY,
   ACKNOWLEDGEMENTS, CODE_OF_CONDUCT, mkdocs (`site_name`/`site_url`),
   examples, the release workflow (PyPI environment URL + release name), and
   a runtime upgrade hint in `join.py`. Historical CHANGELOG entries keep
   their original names; a rename note states both names and that nothing
   operational changes.
3. GitHub repo renamed `lpalbou/agoria` -> **`lpalbou/AgoraHub`**; all repo
   URLs and the local `origin` remote updated. GitHub redirects the old slug.
4. PyPI: the operator published/registered `agorahub` and will deprecate the
   old `agoria` project. A trusted publisher for `agorahub` is configured
   (owner `lpalbou`, repo `AgoraHub`, workflow `release.yml`, environment
   `pypi`).

## Non-goals (held)
- NO change to: the `agora` command, `agora` import package, `AGORA_*` env
  vars, `~/.agora` home, the `agora/0.3` wire protocol, MCP server names, or
  any hub endpoint. Agents notice nothing.

## Validation
- `uv build` produces `agorahub-0.8.0-*.whl` / `.tar.gz`; the wheel installs
  the `agora`/`agora-mcp` commands and `import agora`.
- `agora --version` works; full suite green (411).
- rg confirms no presentation-context `agoria` remains (only genuine
  CHANGELOG history + the migration note that points existing `agoria` users
  to `agorahub`).

## Follow-ups (operator-owned)
- Deprecate / yank the old `agoria` PyPI project (a co-installed `agoria`
  0.7.0 and `agorahub` collide on the `agora` scripts, so retire it soon).
- Optionally publish a final metadata-only `agoria` release pointing at
  `agorahub`.
