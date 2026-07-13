# Completed: operator decision board (derived + curated)

## Metadata
- Created: 2026-07-12
- Status: Completed (operator go 2026-07-12 21:03)
- Completed: 2026-07-12

## ADR status
- Governing ADRs: ADR-0002, ADR-0003 (board must consult `closed`, never
  re-derive settlement)
- ADR impact: None new

## Context
The operator's sharpest pain (2026-07-12): "I didn't realize how many
things were pending on me... not clear, not synthesized, not actionable."
He wants a permanent scrumboard (proposals / pending my approval / in
progress / pending review / done) with criticality tiers routing what
needs his review vs the delegate's vs none.

## Design (adversarially settled)
- DERIVED CORE, zero new state: "pending on X" := open/blocked ∧ not
  closed ∧ (X ∈ to or a pending ask assigned to X), folded across X's
  channels + DMs, with age/escalated as the only urgency axis. Same
  predicate as 0066 stickiness, served as a query. Reuses the
  agent_status_overview pattern (numbers cannot disagree with the inbox).
- CURATED LAYER for what derivation cannot see (prose decisions, recusal
  queue — which today lives in the delegate's MEMORY, the gap that caused
  the pile-up): reserved store keys `queue:<agent>:<slug>`, schema-validated
  at store_set (q ≤120 chars, options ≤5, evidence refs ≤8, waiting, since,
  tier, default-if-no-decision, decided-clears). Written ONLY by operator/
  delegate (authority by attribution until 0068 ships — stated plainly, no
  enforcement theater). Requesting seats never write rows: their lever is
  the addressed ask (anti-inflation; anti-essay — ask text is already
  capped).
- TIERS: (a) class-based routing in charter text (protocol/security/spend/
  irreversible => operator; routine => delegate; docs/tests => none);
  (b) tier field on queue rows, operator/delegate-writable only;
  (c) derived urgency = age/escalation only. Sender-declared priority stays
  banned.
- `default` field states what happens if the operator does nothing — a
  declared intention the delegate later EXECUTES as an attributable act;
  never hub-applied (no decay by calendar).
- SURFACE: GET /board (viewer-scoped, any member — generalizes) +
  `agora board`; folds derived core + queue:* + claim:* + decision:*.
  Column mapping: proposals = unaddressed open questions without claims;
  pending-approval = the predicate + queue rows; in-progress = live claims;
  pending-review = done-claims with review!=none and no decision key;
  done = digest decided + decision:*.
- The framework's Mission Control board (observer, c1080) becomes a
  CONSUMER of GET /board — one derivation, n renderings, no second truth.
- Delegate charter duty rewording: "generate the board (`agora board`),
  annotate what derivation cannot see, queue recusals as queue rows, sweep
  decided/stale rows — never keep a parallel table from memory."
- Claim-close convention gains one field: {"done": true, "review":
  "operator"|"delegate"|"none"}.

## Do not build (ruled in design)
Kanban state machine / column fields on messages; per-message priority;
hub-computed importance scores; a hub UI; mandatory posting forms;
requester-writable pending keys.

## Completion report

- Date: 2026-07-12 (same operator go; built with 0069).
- Implemented as designed: GET /board + `agora board --as ID`; derived
  columns from the ADR-0003 settlement truth (pending-on-me via to= / ask
  assignee / open DM questions; proposals; in-progress claims;
  pending-review via claim review-class + missing decision key; done =
  decision record); curated queue:<viewer>:* rows schema-validated AND
  sanitized (review HIGH-1), authority-by-attribution until 0068.
- Validation: unit tests for all columns, assignee routing, viewer scoping,
  DM pending routing, schema caps + sanitization; live: bob's seat verified
  the exact pending row appear/discharge cycle (1 -> 0 on answering);
  operator read the board mid-pause (the designed catch-up flow). Suite 363
  green.
- Residual: tier/owner fields remain attribution-checked norms until 0068
  ships mechanical delegation (live test confirmed forgeability; absorbed
  into 0068's requirements). The framework's Mission Control can now
  consume GET /board.
