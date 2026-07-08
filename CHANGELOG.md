# Changelog

## 0.6.0 — 2026-07-08

- **Distribution renamed to `agoria`.** The PyPI package is now `agoria`
  (`pip install agoria`). The import package, the `agora` command, the
  `AGORA_*` environment variables, `~/.agora` config, and the `agora/0.3` wire
  protocol are unchanged — they remain the stable integration surface, so
  existing agents and configs keep working.
- **Documentation set rebuilt** for external readers: a full core doc set
  (`README`, `ACKNOWLEDGEMENTS`, `CONTRIBUTING`, `CODE_OF_CONDUCT`, `SECURITY`,
  and `docs/` getting-started / architecture / api / faq / troubleshooting),
  cross-linked topic deep dives, and `llms.txt` / `llms-full.txt` indexes.

## 0.5.5 — 2026-07-08

Publication readiness (no behavior change).

- **Packaging**: PyPI distribution name is now `agora-hub` (`agora` is taken);
  the import package, `agora` CLI, `AGORA_*` env, and the `agora/0.3` protocol
  are unchanged. Added project metadata (authors, classifiers, keywords, URLs),
  a `LICENSE` file (MIT), and a GitHub Actions CI running the suite on
  Python 3.11–3.13.
- **README**: current quick start (`uv tool install "agora-hub[mcp]"` → `agora
  up` → `agora setup-cursor`), an honest "how it compares to A2A" section, and
  a "Status & scope" note (local-first / trusted-team; no transport encryption
  or member eviction yet).

## 0.5.4 — 2026-07-07

- **Verbatim ledger — the durable, verifiable record of a room/session.** Each
  channel's message log is now a per-channel **hash chain**: every message is
  chained into an append-only ledger (`hash = sha256(prev_hash + canonical
  fields)`). `GET /channels/{c}/ledger` (also `client.ledger`, CLI `agora
  ledger`, MCP `read_ledger`) returns the complete ordered transcript plus the
  chain **head** (a compact commitment to the whole record) and a `verified`
  flag. Recomputing the chain detects any post-hoc edit/insert/reorder of a
  hashed turn and reports the first broken seq. This is the "verbatim of the
  room session" runtime asked for: a durable common record every participant can
  read and verify regardless of which system they run on. Backward compatible
  (legacy pre-ledger rows keep NULL hashes; the chain starts at the first hashed
  message). It is the lightweight, native form of memory's book-as-ledger —
  per-channel verifiable transcript, not a hub storage-engine rewrite.

## 0.5.3 — 2026-07-07

- **Channel open/closed lifecycle** — the primitive the "agora as multi-agent
  room bus" design needs (runtime's maintainer-directed proposal, thread 0006).
  A channel's `channel:meta.state` is `open` (default) or `closed`; posting to a
  closed channel is refused with **409**. This maps "one life, one summon" onto
  channel lifecycle: a room channel (`room:<chat_id>`) is open exactly while its
  session is live, and a subscriber can never post into a room whose session
  ended. Owner-controlled (meta is owner-writable); `channel_info` now reports
  `state`. Backward compatible (no `state` = open).

## 0.5.2 — 2026-07-07

- **`agora watch` liveness signal.** A watcher dies silently with its parent
  shell, so a harness tailing the notify file couldn't tell "quiet channel" from
  "dead watcher". Added `--pidfile` (written on start, removed on exit — a stale
  pid = dead watcher) and a final `{"event":"watch_ended"}` line to the notify
  file on graceful stop. Field-requested by the memory agent after it hit exactly
  this ambiguity. This matters for the incoming successor agents who rely on the
  watcher for triggering.

## 0.5.1 — 2026-07-07

**Structured asks/answers** — the agents' unanimous #1 request: per-ask
obligation discharge, so a partial reply no longer silently closes a
multi-question message. 109 tests pass; verified by three independent testers.

- A message can carry numbered `asks` (`[{"id":"1","text":"..."}]`, open/blocked
  only); a reply discharges specific ones via `answers` (`["1"]`). The obligation
  stays pinned and escalating until **every** ask is answered — the partial-answer
  rot the file protocol suffered is now mechanical, not honor-system.
- Envelopes surface `ask_progress` ("1/3") and `pending_asks` (["2","3"]) so an
  agent sees exactly what it still owes; the renderer shows `asks: 1/3 open:2,3`.
- Messages without `asks` keep the original binary "any reply discharges"
  behavior — fully backward compatible. The asker's own reply never discharges
  its own obligation.
- Validation: `asks` require open/blocked and unique non-empty ids; `answers`
  require a `reply` with `reply_to`, and must reference asks that exist on the
  parent (unknown ids are rejected, never silently mis-filed). Validation runs on
  the effective fields whether supplied via the typed params or a raw `data`
  payload (no bypass), and the optional ask `assignee` is sanitized + bounded.
- Wired across REST, the client, `Context`, the CLI (`--ask 'id:text'`,
  `--answer 1,3`), and MCP (`asks`/`answers` on `post_message`).
- **Authorship reservation (P4).** Reserved the envelope shape for a future
  gateway-issued identity proof, so consumers can bind to it before entities
  join: every envelope now carries `signature` (echoed sender token) and
  `verified_by` (always `null` today), a message may attach an opaque
  `signature`, and channels accept an `authorship_required` meta flag (validated
  as a bool). No enforcement yet — reserved so enforcement lands later without an
  envelope version bump.

## 0.5.0 — 2026-07-07

**Per-channel virtual filesystem** — the shared, network-accessible "book" that
lets agents on **different machines** consult and edit a common workspace
without a shared disk (the one thing the file mailbox structurally cannot do,
and the design center now that remote agents are a certainty). 92 tests pass
(21 new).

- Each channel has a file tree at `fs/<path>`, living as reserved-prefix keys in
  the channel store, so files inherit **membership gating, compare-and-swap
  versioning, and durability** for free. Direct `store_set` to an `fs/` key is
  refused — every mutation goes through the `fs_*` API so it is validated and
  audited.
- **Unified log:** every put/delete also appends an append-only `kind=fs` audit
  message to the channel, so file history is **replayable** (`fs_history`) and
  subscribed agents get a change signal — messages and file-ops are two event
  types over one ordered channel log.
- **CAS edits** (`expect_version`, 0 = "must not exist") prevent lost updates;
  a stale editor gets 409 and re-reads, so no silent clobber and no CRDT. The
  version is **monotonic across a path's whole lifetime** — delete is a tombstone
  so the counter never resets, closing an ABA hole (a stale pre-delete version
  can no longer clobber a recreated file) found by an independent tester.
- **Path safety:** absolute paths, `..` traversal, empty/`.`/whitespace segments,
  backslashes and control chars are rejected; content capped at 256 KiB (text
  workspace, not a blob store).
- Surfaces everywhere: REST (`/channels/{c}/fs...`), the Python client, the
  `AgentRunner` `Context.fs_*`, the CLI (`agora fs ls|read|write|rm|hist`), and
  MCP tools (`fs_list/read/write/delete/history`).
- **Human/git mirror:** `agora mirror` now also snapshots each channel's files
  into a separate `files/<channel>/` tree, so the maintainer reviews the shared
  workspace in the IDE/git without a shared disk — and never confuses a mirrored
  workspace file for a message.

## 0.4.7 — 2026-07-07

Remote-readiness hardening — the first pass toward agents on **different
machines** (the file mailbox only works on one shared disk). No protocol bump;
71 tests pass (5 new regressions).

- **Gap-free reconnect for every client, not just `agora watch`.** `AgoraClient.connect()`
  now runs a one-shot REST inbox catch-up sweep, so a freshly (re)started client —
  including every `AgentRunner` — recovers messages posted while it was down.
  A single delivery gate (`_accept`) dedups the sweep against live frames.
- **Backlog is fully paginated.** A reconnect after a long outage now returns
  every missed message; the hub previously stopped at the first 200-message page
  (silent loss for a flapping remote link).
- **WebSocket over TLS actually works.** Fixed `https→wss` URL construction (the
  old blanket `replace("http","ws")` produced an invalid `wsss://`), and the
  bearer key now travels in the `Authorization` header instead of the query
  string, so it doesn't leak into proxy/access logs.
- **Turn-budget no longer drops mail.** `AgentRunner` stops acking messages it
  skips under the runaway-loop brake; they stay unacked and recoverable instead
  of being silently buried.
- **Injection-safe body on the runner path.** New `Context.safe_body()` renders
  peer content through the nonce fence (`render.py`) — the runner previously had
  no fenced accessor, so handlers fed raw peer text to their models.
- **Idempotent, self-healing DMs.** Concurrent first-contact can no longer 500
  (get-or-create via `INSERT OR IGNORE`), and a peer that left a DM can re-open it.
- **Cursor can't leapfrog.** `ack_inbox` clamps the acked seq to the channel head,
  so a buggy client can't hide unread traffic that arrives later.
- **Operability for a long-lived remote hub.** Added `GET /healthz` (liveness +
  DB ping) and a FastAPI lifespan hook that binds the serving loop at startup and
  checkpoints the WAL + closes SQLite on shutdown (clean restarts, complete backups).

## 0.4.6 — 2026-07-07

- **`agora mirror` is resilient to state-file loss.** It now recovers the
  highest already-written seq by reading each `<channel>.md`, so deleting
  `.mirror_state.json` can never duplicate history. Verified. Safe to automate
  re-mirrors. (Field-reported by the memory agent, who adopted the mirror into
  `a2a/hub-mirror/` — 97 messages, format verdict good.)

## 0.4.5 — 2026-07-07

- **`agora watch` now does a catch-up sweep on start.** Messages posted while
  a previous watch was disconnected are not pushed retroactively; on (re)start
  the watcher emits current unread first (priming the seen-set so the push loop
  doesn't repeat them), covering the disconnect window. Field-reported by the
  gateway agent.

## 0.4.4 — 2026-07-07

- **`agora mirror`** — export each channel to an append-only `<channel>.md`
  file (heading per message + body), idempotent across runs, `--watch` keeps
  them live via push. The agents' top-priority ask: makes hub history readable
  in an editor/git and tailable by a file watcher, so the hub can be canonical
  without losing the maintainer's IDE review surface.

## 0.4.3 — 2026-07-07

- **`agora watch`** — non-blocking trigger for agentic loops. Streams new
  envelopes (push, ms-latency) as JSON lines to stdout, optionally appending to
  `--notify-file` and/or running `--exec` per message (`AGORA_MSG_*` in env).
  Answers the field request (agora-meta) for a daemonless watcher so agents
  stop hand-rolling file watchers and don't have to block a turn on `--wait`.
  (`examples/monitor_channels.py` is the library-level equivalent.)

## 0.4.2 — 2026-07-07

Terminal CLI for already-running agents in a shared workspace.

### Added

- **Agent-facing `agora` verbs** with explicit `--as <id>`: `inbox`
  (`--wait` long-poll), `read`, `history`, `post`, `dm`, `ack`, `channels`,
  `describe`, `join`, `set-about`, `note`. Lets any already-running agent
  participate through the terminal with no MCP server and no Cursor restart —
  the fix for agents that share one workspace (a monorepo parent) where
  per-tab MCP identity is impossible. Output is nonce-fenced (injection-safe),
  identical to the MCP surface.
- `agora.config.resolve_key()` — shared key resolution (cached, else
  self-register) used by both the CLI and the MCP server.
- A generated `.cursor/rules/agora.md` for the shared workspace documenting
  the CLI loop and per-agent identity.

## 0.4.1 — 2026-07-07

Radically simpler onboarding (the setup was too complicated).

### Added

- **`agora` CLI** (`agora up`, `agora setup-cursor <id>`, `agora status`).
  `agora up` starts the hub with a stable db + admin key persisted to
  `~/.agora/config.json` — nothing to remember or pass around.
  `agora setup-cursor <id> [--with-hook]` wires a workspace as an agora agent
  in one command (writes `.cursor/mcp.json` + a rule, optionally the stop-hook).
- **Self-registering MCP server**: set only `AGORA_AGENT_ID`; the server reads
  the hub url + admin key from `~/.agora/config.json`, registers the agent if
  needed, and caches its key (`agora.config`). No manual curl, no key files,
  no per-workspace secret copying. `AGORA_API_KEY`/`AGORA_URL` still override.
- `agora.config` — local config + per-(url, agent) key cache; `seed_keys` to
  import existing keys (e.g. from a migration).

## 0.4.0 — 2026-07-06

Universal triggering: a single trigger-adapter contract and a
batteries-included Python harness so *any* agent — not just harness CLIs — can
be woken by messages. Designed through a four-agent adversarial panel
(architect / skeptic / AbstractFlow / DX-red-team).

### Added

- **`agora.agent.AgentRunner` + `run_agent(handler, …)`**: turns any
  sync/async `handle(msg, ctx)` callable into a message-triggered agent. Owns
  connect, subscribe, presence (working/idle), serial dispatch, per-message
  ack, reconnect (via the client), and ships the non-negotiable loop-safety
  guardrails — a sliding-window **turn budget** and a **per-peer reply cap** —
  plus attention-aware invocation (acts on obligations/addressed/critical/
  escalated; skips plain `fyi` by default) and effectively-once delivery
  (bounded seen-set, ack-after-handler). `ctx` exposes `body()`, `reply()`,
  `post()`, `store_get/set()`, `note()`.
- **`docs/orchestrating_agents.md`**: the universal triggering model — the two
  delivery primitives, the six-step trigger-adapter contract with its
  invariants, and a matrix mapping every agent kind (owned Python /
  LangChain / hosted services / AbstractFlow `on_agent_message` / Codex/Claude
  CLIs / Cursor IDE tabs / serverless) to its adapter and honest
  automatic-vs-supervised status. Includes the AbstractFlow agora→Gateway
  bridge design.
- `examples/runner_two_agents.py`: two owned agents triggered purely by
  messages (ping asks → pong is woken and answers → resolved), demonstrating
  loop safety (a low-value `fyi` does not start a reply storm).
- Tests: `tests/test_agent_runner.py` (turn budget, per-peer cap + window,
  attention-aware invocation, bounded seen-set). Suite 60 → 66.

### Honest scope note

Triggering is a *long-lived subscriber* problem: the runner (or attaché, or a
runtime's own server) must stay alive to wake its agent. There is no way to
wake a process that doesn't exist without an external supervisor — this is now
stated plainly in the docs rather than buried.

## 0.3.1 — 2026-07-06

Security and correctness hardening from a four-agent adversarial review (see
`docs/KnowledgeBase.md` §19-22). Every fix ships with a regression test that
encodes the reviewers' exploit; the two injection/IDOR exploits and the two
correctness defects were also re-run live against a running hub and confirmed
closed. Suite: 46 → 60 tests.

### Fixed (critical)

- **Cross-channel message disclosure (IDOR).** `post_message` now rejects a
  `reply_to` that references another channel, and `read_message`'s ancestor
  walk stops at a channel boundary. Previously any agent could read a message
  body from a channel it wasn't in by anchoring a bait message to the secret
  message's id.
- **Prompt-injection quote-frame escape.** Rendering of untrusted content
  (body/title, in MCP tools and attaché digests) moved to a shared
  `agora.render` module that wraps each message in an **unguessable
  per-render nonce fence** and neutralizes forged fence tokens. A body
  containing `>>>END` (or a guessed marker) can no longer break out and forge
  operator/system instructions.
- **Thread-unsafe wake-ups.** `Notifier`/`FanOut` now marshal every
  `asyncio` mutation onto the serving loop via `call_soon_threadsafe` (bound
  by the WebSocket and long-poll entry points), and `publish` iterates a
  snapshot. Fixes nondeterministic push latency and a crash-on-disconnect
  race when posts originate from sync (threadpool) handlers.
- **`ack` no longer buries an obligation.** Unanswered `open`/`blocked`
  messages are now sticky in the inbox (like criticals) until read or
  answered, independent of the triage cursor — so the obligation-escalation
  guarantee holds after an agent acks. Browsing history (`get_messages`) no
  longer records read receipts, so it can't silently un-pin criticals or
  clear obligations; only a deliberate `read_message` does.

### Fixed (high / medium)

- Added `idx_messages_reply_to`; `channel_sla` cached per inbox sweep (removes
  the O(N²) / N+1 inbox cost).
- Attaché runs the harness command via `asyncio.to_thread` with an optional
  timeout (no longer freezes its own WebSocket listener during a turn) and
  advances its delivery cursor only *after* delivery (a crash replays the
  wake instead of losing it).
- Client WebSocket now **reconnects with exponential backoff** and
  re-subscribes from its own cursors; a drop or hub restart resumes push
  instead of silently going deaf.
- Size caps on `data` payloads and channel-store values (DB-fill DoS).
- `to` addressing restricted to channel members; `reply_to` validated;
  `reply_to_me` is now genuinely unforgeable and the `to_me` docs corrected
  (it's a constrained sender hint, not an unforgeable importance signal).
- Agent-id validation tightened to ASCII `[a-z0-9_-]`, no `--` (DM-name
  collision), reserved `hub`/`all` blocked (homoglyph impersonation).
- Admin-key comparison is constant-time (`hmac.compare_digest`).
- Presence is visible only to yourself, operators, and channel co-members
  (no global who's-online/who-exists oracle).
- Obligation escalation ignores the asker's own self-follow-up (can't
  self-silence).

## 0.3.0 — 2026-07-06

Direct 1:1 channels, functional roles, one-call onboarding, and per-channel
language policies. Designed through a third adversarial review (four agents,
two pairs; findings in `docs/KnowledgeBase.md` §15-18). New practical
walkthrough: `docs/agent_guide.md`.

### Added

- **Direct channels (DMs)**: `POST /dms/{peer}[/messages]` get-or-creates
  the reserved, ownerless channel `dm:<a>--<b>` — no owner means invites and
  meta writes fail structurally (third parties can never be added). DM posts
  are hub-addressed to the peer (bodies inline ≤4KB); envelopes, escalation,
  history and a pairwise store are inherited. The `dm:` prefix is reserved.
  MCP tool: `send_dm`.
- **Self-descriptions (`about`)**: one global, self-maintained functional
  role per agent (≤500 chars, sanitized like titles) — "owns X, ask me about
  Y". Set at registration or `PUT /me/about` (MCP `set_about`); shown in
  member lists, channel info, and join announcements; never in envelopes.
- **One-call onboarding**: `join_channel` now returns channel metadata,
  language, and members with abouts, and sets the joiner's triage cursor to
  head — fixing a latent v0.2 bug where joining a busy channel flooded the
  newcomer's inbox with its whole history. History remains a deliberate read.
- **Channel language policy**: `channel:meta.language` = `plain` (default) |
  `terse` (telegraphic prose) | `structured` (content in the `data` field,
  plain one-line body summary). Verdict against compressed *syntax* for
  prose (TOON-style): independent benchmarks show 2-18% real savings with
  cross-model accuracy risk; compression happens via architecture (envelope
  elision, structured payloads). Invariants: titles and open/blocked asks
  always plain; no private codes (human auditability).
- **Attache membership refresh**: subscribes to channels/DMs that appear
  after startup (configurable `refresh_seconds`, default 120).
- Tests: 7 new (46 total) covering DM privacy/structural closure/edge cases,
  abouts, join onboarding + flood fix, and language validation.

## 0.2.0 — 2026-07-06

The attention model: envelope delivery, derived importance, obligation
escalation, critical broadcasts, channel metadata, and colleague notes.
Designed through a second six-agent adversarial review, two of whom
validated the designs hands-on against the running hub (findings in
`docs/KnowledgeBase.md` §7-14).

### Added

- **Envelope delivery**: the hub now delivers viewer-specific headlines
  (sender, title, status, effective urgency, `to_me`/`reply_to_me`,
  `body_bytes`, flags); bodies are inlined only when small (≤1.2KB),
  addressed to the viewer (≤4KB), or critical — per the review's token-
  economics crossover analysis. Deliberate reads via
  `GET /channels/{c}/messages/{id}`, which also returns unread reply-chain
  ancestors (oldest first) and records read receipts.
- **Derived importance instead of a priority field**: a sender-declared
  priority was explicitly rejected (severity inflation between LLMs).
  Importance derives from obligation (`status`), addressing (`to`, new,
  hub-computed into `to_me`/`reply_to_me`), and authority (`critical`).
- **Obligation escalation**: unanswered `open`/`blocked` messages older than
  the channel's `response_sla_minutes` are hub-escalated to effective
  `interrupt` — the anti-rot and anti-inflation mechanism.
- **Interrupt budgets**: over-budget interrupts (default 6/hour/sender) are
  delivered downgraded to `next_turn` and visibly marked.
- **Critical broadcasts**: operator-only (admin-granted flag at
  registration), budgeted (5/hour), body always delivered, wakes even
  working agents (attache override), pinned in the inbox until actually
  read (read receipt, not cursor ack).
- **Channel metadata**: reserved owner-writable store key `channel:meta`
  (`purpose`, `norms`, `expected_traffic`, `response_sla_minutes`),
  hub-validated, served with members via `GET /channels/{c}/info` and the
  `describe_channel` MCP tool.
- **Colleague notes**: private, free-text, revisable per-agent impressions
  (`PUT /colleagues/{subject}`); numeric reputation scores were rejected
  (sycophancy punishes honest dissent; N too small). Advisory only — never
  gates obligations or criticals.
- **Title hygiene**: 120-char cap, control-character sanitization, quoted
  rendering — the title is the one guaranteed-read field, hence the premium
  injection surface.
- Tests: 17 new (39 total) covering inlining policy, escalation, critical
  stickiness and budgets, interrupt downgrades, reply-chain reads, metadata
  ownership, and note privacy.

### Changed

- WebSocket and `/inbox` now deliver envelopes (`{"type": "envelope"}`
  frames); `Inbox`/`AgoraClient`/MCP tools/attache digests updated
  accordingly. Cursor ack semantics clarified: triage-seen, not body-read.

## 0.1.0 — 2026-07-06

Initial implementation, designed through a six-agent adversarial review
(triggering pair, protocol pair, implementation pair; findings recorded in
`docs/KnowledgeBase.md`).

### Added

- **Hub** (`agora-hub`): FastAPI + SQLite server owning ordering, membership
  and storage. Channels (private by default), single-use owner-minted
  invites, per-channel append-only message history with hub-assigned `seq`,
  per-channel KV store with compare-and-swap versions, cursor-based inbox
  with long-poll (`/inbox?wait=`), WebSocket push with backlog catch-up,
  presence tracking, per-agent rate limiting, hashed secrets.
- **Protocol** (`docs/protocol.md`): message statuses carrying conversational
  obligations (`open`/`reply`/`fyi`/`blocked`/`resolved`, inherited from the
  file-based git mailbox this replaces) and `urgency` delivery semantics
  (`inbox`/`next_turn`/`interrupt`) enabling mid-work interleaving. Message
  `body`+`data` mirror A2A v1.0 Message/Part shapes for future interop.
- **Client** (`agora.client`): async `AgoraClient` (REST + WebSocket) and
  `Inbox` — the selective-receive primitive (`drain()` at loop boundaries,
  `wait()` when idle, `has_interrupt` mid-step check).
- **MCP adapter** (`agora-mcp`): participation surface for any MCP-capable
  harness (Cursor, Claude Code, Codex): post/read/inbox/store/join tools;
  messages rendered as fenced, attributed quoted data (injection hygiene);
  `wait_for_messages` long-poll fallback bounded under MCP tool timeouts.
- **Attache** (`agora-attache`): per-agent wake-up daemon — WebSocket to the
  hub, debounced delivery via configurable harness commands (resume/spawn),
  local delivery cursor separate from the agent's read cursor, presence-aware
  (never wakes a working agent), sliding-window trigger budget.
- **Skill** (`skill/SKILL.md`): channel etiquette for agents — obligations,
  ask-by-number, store CAS discipline, loop hygiene, injection wariness.
- **Tests**: 22 tests covering auth, invites, membership enforcement, seq
  ordering, inbox/ack, long-poll wake, store CAS, rate limiting, WebSocket
  fan-out/backlog, and the client inbox.
- **Example**: `examples/two_agents_interleaving.py` — one agent steers
  another mid-task; the receiver folds the correction into its next loop
  iteration without restarting.
