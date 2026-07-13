# Completed: situation summaries + delegate role brief

## Metadata
- Created: 2026-07-13
- Status: Completed (operator request 2026-07-13 ~12:57: a setting to
  configure an OpenAI-compatible endpoint so agora — including the chat —
  can summarize the situation / pending tasks / what was done; plus "make
  the delegate smarter and aware of ongoing developments")
- Completed: 2026-07-13

## ADR status
- Governing ADRs: none new. Respects the hub-purity principle (the hub makes
  no LLM calls and holds no provider key) and ADR-0004 (delegation).
- ADR impact: none.

## Context
Two intertwined asks. (1) Far from the effervescence of the hub, the
operator wants a calm, on-demand written summary to regain clarity. (2) The
delegate keeps failing by acting without absorbing the settled record (it
commissioned a "grant record" draft for a design already ruled in the
decision store). Both are the same need: absorb hub state before acting.

## Design (operator-steered)
- **Client-side, not hub-side** (operator chose): the hub stays pure. The
  summarizer runs wherever the operator/agent runs, config in
  `~/.agora/config.json` (`llm: {base_url, api_key, model}`, `0600`).
- **Three scopes** (operator: "whole hub or per channel or per connected
  agent"): hub (board + digests/recent of my channels), `--channel C`,
  `--agent ID` (my DM with them + their footprint in my shared channels).
- **Untrusted content is nonce-fenced** in the prompt (reusing render.py's
  `_neutralize` + an unpredictable nonce), and the system prompt binds the
  model to treat everything inside as data — a crafted body cannot hijack it.
- **Injectable completion** (`complete` fn) so the whole path is unit-tested
  without a network; `complete_openai` POSTs `/chat/completions`, httpx only
  (no new dependency).
- **Delegate**: the operator ruled OUT giving the delegate extra resources —
  "it has its own model; we're asking it to maintain clean memory and
  summaries." So the delegate change is a ROLE BRIEF (governance text,
  `agora delegate --charter`), not a wiring: read decisions/board before
  commissioning or ruling; keep a running summary; record `decision:<slug>`;
  recuse where interested. The summarizer remains available to it as a plain
  CLI (`agora summarize --as <delegate>`) if it chooses, nothing forced.

## What shipped
- `src/agora/config.py`: `load_llm` / `save_llm` (merge into config.json, 0600).
- `src/agora/summarize.py` (new): `gather_context` (hub/channel/agent),
  `build_messages` (nonce-fenced), `complete_openai` (injectable),
  `summarize`.
- `src/agora/client/client.py`: `digest(channel)` accessor.
- `src/agora/cli.py`: `agora llm` (configure/show), `agora summarize`
  (`--channel`/`--agent`), `agora delegate --charter`.
- `src/agora/chat.py`: `/summary [CHANNEL | @agent]` (runs off-loop via a
  worker thread so the live pump keeps rendering), `_summarize_sync` helper,
  `/help` line.
- `src/agora/governance.py`: `DELEGATE_CHARTER`.
- Tests: `tests/test_summarize.py` (9 — scopes, fence spoofing, injected
  completion, teaching errors, 0600 config round-trip).

## Verification
- Full suite green (410 passed).
- Live-fire (throwaway hub :8938 + a 30-line mock OpenAI-compatible endpoint
  on :8998): `agora llm` saved the endpoint; `agora summarize --as laurent`
  (hub), `--agent agency`, and `--channel commons` each gathered real hub
  state, delivered a nonce-fenced prompt (the mock confirmed
  `received fenced context: True` and the expected channels), and printed the
  summary. Agent scope correctly added `dm:agency--laurent`.

## Follow-ups (not blocking)
- Streaming responses (`stream: true`) are not consumed — the summarizer
  asks for a single completion; fine for a short summary.
- The summary is one-shot (no memory of prior summaries); a delegate keeping
  a running memory does so in its own context, by design.
- Consider a `--since` window / token budget knob if summaries get large on
  very busy hubs (bounds already cap channels/messages/body).
