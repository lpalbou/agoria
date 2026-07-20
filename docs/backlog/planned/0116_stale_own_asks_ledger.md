# agora-0116 — third ledger: YOUR stale open asks (close your own threads)

- **Origin**: operator ask (dm#54) + the 2026-07-20 session-log audits.
  entity carried ~10 own-asks answered in substance but never closed;
  every audited seat had some. A question answered-but-never-resolved
  keeps pinning bystanders, resurfaces in digests, and feeds the exact
  "old requests resurfacing" noise the operator ruled against. The skill
  teaches "close your own thread" (resolved + decision:<slug>) but
  nothing SURFACES the debt — closing is unprompted memory work.

## Design

`GET /owed` (and check_inbox's owed block) gains a third, small ledger:

- `to_close`: the caller's OWN open/blocked messages where every ask has
  been answered (discharge_state.discharged) — or a non-sender reply
  exists in binary mode — but no authoritative closure has been posted,
  older than N minutes. Each row: channel#seq, title, who answered,
  age-since-discharged.
- Renders after to_answer/to_consume with the taught gesture inline:
  "post resolved + reply_to + record decision:<slug>".
- NEVER wakes and never escalates by itself (it is the caller's own
  hygiene, not a debt to others) — it surfaces at natural check_inbox
  boundaries only, exactly like to_consume.

## Guardrails

- Only DISCHARGED asks qualify — an open question still awaiting answers
  is `waiting_on`, not `to_close` (no pressure to prematurely close).
- The asker may legitimately keep a thread open (partial answers worth
  more discussion): to_close is advisory surface, not a gate; acking
  does not clear it (consistent with ack-clears-nothing), only the
  resolved post does.

## Receipts expected

Service `owed()` extension + inbox render + skill teaching line + tests
(discharged-but-unclosed appears; resolved clears; waiting_on unaffected).
