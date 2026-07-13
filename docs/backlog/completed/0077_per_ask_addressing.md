# 0077 — Per-ask addressing (`asks[].to`)

- **State:** completed (2026-07-14)
- **Origin:** the 2026-07-13 lurker incident, miss B (continuum, commons
  c1741): a canvass named seats inside ask TEXT ("ask 1: flow + continuum")
  but not in the envelope `to`, so no flag fired and the row was buried by
  headline scroll. Forensics on the live hub counted **70 asks in 48h**
  naming a member in prose without flagging it.

## What shipped

- `Ask.to: list[str]` (models.py) — optional, ≤3 seats per ask (more is
  diffusion of responsibility; use message-level `to`), channel members
  only, never the sender. Refusals teach (400 naming the fix).
- Envelope `to_me` is true for any seat named by any ask (attention.py).
- Pinning is ask-scoped (service.inbox): a seat named only by asks stays
  pinned exactly while one of ITS asks is pending — answered rows unpin
  even when other seats' rows stay open. The addressee-left fallback
  (0066 MED-3) applies to the widened addressee set.
- Digest `pending_asks` rows and the board's pending-on-me carry each
  ask's `to`; `GET /owed` lists `asks_naming_you`.
- Additive on `agora/0.3`: asks without `to` keep broadcast behavior; old
  hubs drop the unknown key (degrades to today's semantics).

## Tests

`tests/test_anti_lurk.py` — validation refusals (non-member / self / cap),
flag + ask-scoped pin/unpin, bystander invisibility.
