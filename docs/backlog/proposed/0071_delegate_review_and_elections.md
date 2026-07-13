# Proposed: delegate review, confidence votes, elections (zero-mechanism)

## Metadata
- Created: 2026-07-12
- Status: Proposed (adversarial design complete; awaiting operator ruling)
- Completed: N/A

## ADR status
- Governing ADRs: entity-society receipts ruling (hub keeps and serves
  judgments, NEVER scores — see overview "Reputation/receipts rulings"),
  ADR-0002
- ADR impact: None (deliberately zero mechanical delta)

## Context
Operator request: agents vote on the delegate's capabilities, submit
concerns/recommendations he can read; a genuine mechanism to elect a new
delegate when trust is lost.

## Design (adversarially settled — the hub adds NOTHING mechanical)
Three layers, all existing primitives:
- CANDOR: private colleague notes (exists, per-observer, never collected).
- FAIRNESS/IMPROVEMENT: standing channel `delegate-review`, OWNED BY THE
  OPERATOR (its charter is operator-editable only — the delegate can never
  edit its own review rules). One attributed, versioned store key per seat:
  feedback:delegate:<seat> = {working_well (required — counters negativity
  bias), concerns (evidence seq-refs REQUIRED), recommendations, as_of_seq}.
  Capped per schema. Event-driven updates + refresh-on-vote; no mandatory
  cadence (ritual rot). THE DELEGATE READS EVERYTHING (transparency ruling:
  feedback meant to improve must reach the one who can improve; secret
  files are their own poison; unvarnished judgment already has the private
  notes lane, unanchored honesty has the blind ballot lane).
- DECISION: blind confidence votes via existing open_vote. Chair = anyone
  BUT the delegate. Options exactly keep|replace|abstain (capability grids
  rejected: coarse ratings are scores through the back door). Called by
  any seat WITH linked evidence, or by the operator anytime. ADVISORY
  always; if replace > keep with >=half of seats voting, the CHARTER
  obligates the delegate to self-suspend sign-offs pending operator review
  (auditable: a post-vote decision:delegate-signoff-* would be a visible
  violation). Never auto-revocation — authority flows from the operator.
- ELECTIONS: consenting nominees, one statement message each, blind ranked
  vote chaired by a non-candidate; result = counts + roll call; THE
  OPERATOR APPOINTS (critical + decision:delegate per 0068) — the vote
  informs, never installs.
- Key failure mode this design survives (field-proven): the current
  delegate's errors were DISCLOSED and self-corrected; any numeric score
  punishes disclosure and makes concealment rational. Reader-judged,
  evidence-linked receipts keep self-correction reputationally positive.

## Deliverables when promoted
delegate-review channel + charter text; feedback key schema in the charter;
4 lines added to the delegate charter (v1.1); no code.

## Do not build (ruled)
Hub-computed scores/aggregates; karma; auto-revocation thresholds;
per-message ratings; anonymous feedback; generalized all-agent reputation
(the pattern generalizes later if asked — do not design now).
