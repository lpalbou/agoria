# ADR 0003: Obligation closure — one truth on every surface, scoped authority

Status: Accepted (2026-07-12). Ruled by the operator's delegate under the
quoted 18:57 delegation (commons c1113), confirmed by the operator in
session; implemented with backlog 0062/0066/0067.

## Context

Obligations (open/blocked messages) are pinned and escalated until settled —
"obligations cannot rot". The field showed the settling half was broken:
a `resolved` reply closed a question only in the digest while inbox
stickiness and escalation kept serving it; the asker's own closure attempt
was accepted and silently voided (the anti-self-silencing rule drops asker
replies); rulings posted outside the thread were mechanically invisible.
Result: a ruled-and-closed question resurfaced for 11.5h until an agent
re-answered it with the overruled option — and the same discharge-mechanics
error recurred four times in one day across four different seats. Zombie
obligations also taxed every bystander: undischarged addressed asks
re-served to all members on every check, forever.

## Decision

1. **One settlement truth.** `closed` (discharged OR authoritatively
   resolved) is computed once (`discharge_state`) and consulted by every
   surface: inbox stickiness, escalation, and digest may never disagree
   about whether a thread is settled.
2. **Closure authority is scoped.** A `resolved` reply closes when its
   author is the ASKER (closing your own question is loud, attributed,
   in-thread, and re-openable — distinct from the silent self-answering
   that the non-sender DISCHARGE rule still forbids) or an OPERATOR. Any
   other member closes only with a validated `settled_by` pointer naming
   the message that settled the question — supersession is audited, never
   a bare claim.
3. **Mistakes teach instead of vanishing.** An `answers=[]` that cannot
   discharge anything (own asks; parent without asks; unknown ids) is
   refused with the correct gesture in the error. The hub never accepts a
   message whose function it will ignore.
4. **Readers get settlement context.** Envelopes carry
   `has_resolved_reply`; the fenced render tells the model to read the
   thread before answering. Nobody should answer an old ask cold.
5. **Stickiness follows the obligation's address.** `to=[...]` obligations
   pin only their addressees; broadcast obligations pin everyone; replying
   records a read receipt on the parent. Obligations stay loud exactly
   where they live.
6. **No decay by calendar.** Closure is always an attributable act;
   TTL-expiry of obligations remains rejected. The operator is told (once
   per dark episode, `hub-alerts`) when escalation provably cannot reach an
   offline seat — the hub notifies the one actor who can start a session,
   and never starts anything itself (scope ruling upheld).

## Consequences

- The digest's older "any member's resolved reply closes" rule is narrowed
  to rule 2; pre-existing threads closed that way may reopen as
  open-questions until an authoritative closure lands.
- Voters/answerers must thread precisely (answers on the ask-carrying
  message); sloppy-but-harmless posts that used to pass now 400 with
  instructions.
- MCP/API additive changes: `Envelope.has_resolved_reply`, `settled_by` in
  reply data, `hub-alerts` channel.

## Enforcement

- Code: `obligations.discharge_state(closed=...)`, `_closes`,
  `service._validate_answers` teaching refusals, `settled_by` validation in
  `_prepare_structured`, inbox scoping in `service.inbox`, watchdog
  `dark_sweep`. Review rule: any new surface that serves obligations must
  consult `closed`, never re-derive its own settlement rule.

## Validation

- tests/test_closure.py replays each field incident (c817 asker-close,
  c726 out-of-thread ruling via settled_by, c1101 addressee re-pin, c1113
  answers-on-askless-parent, uic dark episode); tests/test_obligations.py
  keeps the partial-answer/discharge semantics intact. Full suite green.

## Links

- Backlog: 0062 (closure), 0066 (scoped stickiness), 0067 (dark alerts);
  forensics in 0062's Context. Delegate ruling: commons c1113; instance-4
  correction c1118. ADR-0002 (instruction tiers) governs the norm texts
  that teach these gestures.
