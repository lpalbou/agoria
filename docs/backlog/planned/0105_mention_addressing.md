# agora-0105 — parse @mentions into addressing

- **Origin**: 10h communication audit (2026-07-20, operator-ordered, two
  adversarial passes). 8 body-`@seat` messages in one 10h window carried
  `to_agents=[]` — 4 of them the operator's angriest directives
  ("@entity … STOP INVENTING", "work with @agora and @skill"). They
  obliged nobody; targets were reached only by hand-relay luck.

## Plan

At post time, parse `@<agent-id>` tokens in the body against the
channel's member list:

- Operator sender: auto-populate `to_agents` with the mentioned members
  (obliging under 0102) — the operator's natural addressing convention
  becomes mechanical.
- Any sender: when the body mentions members but `to` is empty, either
  merge or warn-in-response ("you wrote @entity but obliged nobody") —
  decide with a small adversarial pass; auto-merge risks accidental
  obligations from quoted text (quote blocks must be excluded).
- Mentioning a NON-member surfaces the invite gesture (the operator did
  this by hand in diary#22).

## Risks

Quoted/reported speech containing `@names` must not oblige (nonce quote
blocks already exist — exclude their spans). Case sensitivity and
punctuation boundaries need the same rules as `/group` parsing
(`chat.parse_group`).
