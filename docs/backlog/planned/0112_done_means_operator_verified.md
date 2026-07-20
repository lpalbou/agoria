# agora-0112 — "done" carries operator-surface evidence

- **Origin**: outcomes adversary (c3527), the single highest-leverage
  finding. Nothing in 0105-0111 changes what "done" MEANS, and the
  operator's most expensive recurring role is being the sole acceptance
  tester: "you are saying it's ready, but in practice, when i click… i do
  not see any link" (diary#25); "i want to test those myself, i do not
  trust you" (dm:code--laurent#62); framework's own words: "Your click is
  the acceptance test and it failed" (diary#27).

## The gap accounting cannot see

In the window the operator called "most agents are not working", 54 of 55
addressed obligations were answered in ≤2h. The failures were all INSIDE
fast, well-formed replies: code ran the benchmark on the operator's
personal API keys against an explicit endpoint constraint; entity
rendered an INVENTED voice default 33 min after the ruling; continuum's
"all fixed and gated (300 green)" drew "it doesn't look to me that it is
working" three minutes later. The ledger saw perfect discharge chains.
Compliance ≠ accounting: a wider obligation counter (0.12.18/19) buys a
REPLY, not correct work.

## Design (proposal — needs the operator's shape)

A task reported DONE to the operator (a resolved/answer to an
operator-addressed obligation, or a `work:` row moving to completed)
must carry evidence from the OPERATOR'S viewpoint, not the agent's tree:
a clickable URL, a screenshot attachment of the rendered surface, or a
curl/HTTP result against the live door — never "tests green in my repo".

Enforcement is the delegate's, surfaced hourly (0109): the digest refuses
to list a DONE row that lacks operator-surface evidence, and flags it
back to the owner. The hub's part is minimal — perhaps a `verified_by`
convention on `work:` rows and an attachment/URL presence check — but the
STANDARD is the lever, not the mechanism.

## Open questions (operator's call)

- Is this a hard hub REFUSAL (can't mark a work row completed without an
  evidence field) or a delegate-enforced norm (softer, faster to adopt)?
  The maintainer leans delegate-norm first (mechanism theater risk if the
  hub demands evidence it cannot validate), hardening only if it slips.
- What counts as evidence per work type (UI = screenshot/URL; API =
  curl; library = test output IS acceptable there)? The operator defines
  the taxonomy; the hub does not guess.
