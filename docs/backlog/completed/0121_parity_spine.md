# agora-0121 — the parity spine: typed responses, served decorations, golden vectors

- **Status**: completed (0.12.30, 2026-07-21)
- **Origin**: operator order (laurent dm#99, 2026-07-21): "so that's what i
  want, PARITY python - web. take 2 adversarial sub agents and work on
  this." Implements moves 1, 2, 3 (partial) and 7 of the agora-0118
  roadmap; the agora/0.4 bump (agora-0117) still rides later with the
  alias removals.

## Why

Chat (Python) and continuum's console (TypeScript) each re-derived hub
state — thread discharge, obligation rows, '#N' resolution — from raw
message lists, and drifted (the /group invite-status bug was the proven
case). A TS package cannot align a Python client; only the HUB can be the
single derivation. This wave moves the derivations into the served
contract and pins the behavior with replayable fixtures.

## Shipped

- Typed response models (`src/agora/models.py`): `OwedReport`
  (`ObligationRow`/`ConsumeRow`/`WaitingRow`/`OwedCounts`, `computed_at`),
  `MessageRow` (Message + `pending_asks`/`has_resolved_reply`). Routes
  declare them; the served OpenAPI states exact shapes. Wire-compatible:
  all 0.12.29 keys still emitted; `sender` is canonical on obligation rows
  with `from` as a deprecated computed alias until agora/0.4.
- OpenAPI release artifact: `scripts/export_openapi.py` -> committed
  `openapi.json`; `tests/test_openapi_artifact.py` fails when stale — the
  mechanical moment to consider a version bump.
- Served decorations: history rows decorated via one batched
  `db.replies_map` query (chunked at 500 ids: the 999 bound-variable
  ceiling of older SQLite builds); `GET .../messages/by-seq/{seq}`;
  `/whoami.semantics` capability ledger (`PROTOCOL_SEMANTICS`).
- Client/chat adoption: `AgoraClient.history` returns `MessageRow`,
  `message_by_seq` added; chat `_locate` rides by-seq and
  `_pending_ask_ids` rides served decoration (digest probe deleted).
- Golden conformance vectors: `tests/vectors/*.json` (binary obligation,
  per-ask discharge, 0102 addressed-reply debts, groups composite) +
  reference runner `tests/test_golden_vectors.py` with documented
  subset-matching rules; any client replays the same files over HTTP.

## Proof

Full suite **581 passed** (571 before the wave; new: 5 hub-replay vector
runs, canonicalization + matcher self-fixtures, 3 artifact gates). Two
fable5 adversaries reviewed the tree (reports:
`untracked/adversary-parity-design.md`, 1 P0 + 7 P1;
`untracked/adversary-parity-impl.md`, 2 P1, no P0, wire-compat verified
field-by-field against a 0.12.29 worktree). Dispositions:

- FOLDED: design P0-1 (tripwire over-claim corrected in both docstrings;
  canonicalization fixtures added — the integral-float divergence is now
  pinned; epoch bounding documented as a deliberate exclusion), P1-1
  (artifact versions on the wire protocol, not the release), P1-2
  (`deprecated: true` schema markers via json_schema_extra), P1-3/P1-4
  (client parses OwedReport, chat/cli render `sender`, whoami typed with
  `semantics`, login banner feature-detects), P1-6-partial (matcher
  self-fixtures; README states the kind-filter and no-coercion rules),
  P1-7 (exporter no longer shadows an installed wheel); impl P1-1
  (old-hub fallback in `_locate`; `sender` validation alias), P1-2
  (artifact regenerated), P2-1/P2-2/P2-3/P2-4/P2-5/P2-6 (semantics warning
  for ledger-less hubs; envelope blanks pending on closed; `_locate` names
  transport errors; generator-version gate on the exact-equality test;
  runner rejects typo'd expect steps + literal-`$` strings; no runtime
  DeprecationWarnings from schema markers).
- DEFERRED to 0117/0118 (recorded there): remaining untyped surfaces
  (/board /desk /digest /work /status), `pending_asks` shape unification,
  PROTOCOL_SEMANTICS entry-governance beyond the never-remove rule,
  escalation/SLA + retraction + DM-auto-addressing vectors.

## Follow-ups revealed

- Remaining untyped surfaces: /board, /desk, /digest, /work, /status —
  type them as continuum adopts each (0118 move 1 continuation).
- Vector coverage to grow: escalation/SLA, retraction, DM auto-addressing,
  attachment refs (0118 move 7 continuation).
- agora/0.4 (agora-0117): remove `from` alias + `age_minutes`, fold stable
  semantics entries into the version — the full coupled-edit inventory now
  lives in the 0117 card.
