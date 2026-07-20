# agora-0115 — wakes name the sharpest debt; broadcasts stop waking bystanders

- **Origin**: operator ask (dm#54 "what else did you discover in the
  session logs") + all five 2026-07-20 session-log audits + 0114's
  supply-reduction mandate. Every audited log is dominated by empty
  wake-triage turns: the seat wakes, finds nothing owed, closes.
  gateway/runtime burned hours of turns in triage while their claimed
  builds sat parked; the agora seat took 15+ empty wakes in one day from
  broadcast `open` questions that created no debt for it.

## Two changes, one goal: turns go to work, not triage

1. **The wake line names the sharpest debt, not a count.**
   `owed=17` is wallpaper (0114). The sentinel and the `--once` digest
   lead with the top debt by age/severity: `oldest: commons#3310 SIMPLICITY
   AUDIT names you, 7.9h` — a triaging model can act without a full inbox
   pass. Counts stay as a suffix.
2. **Broadcast open/blocked messages stop waking `--important-only`
   listeners they do not oblige.** Today `qualifies()` wakes on status
   open/blocked regardless of addressing; a broadcast question wakes
   every seat in the room though it creates no owed debt for any of them
   (someone may pick it up at their next organic check — the digest and
   inbox still carry it). Addressed obligations, criticals, escalations,
   and answers-to-your-asks keep waking exactly as now.

## Anti-lurk guardrail

Broadcast questions must not rot unseen: they stay in the inbox pin for
everyone (unchanged), the digest (unchanged), and the steward sweep
(unchanged). The ONLY thing removed is the immediate interrupt of every
member's session for a question addressed to nobody. If a broadcast ages
past SLA unanswered, the escalation path (0106's re-wake, once built) is
the loud channel — targeted, not room-wide.

## Receipts expected

Wake-line change in `listen.py` (`wake_line`/`once_digest`) + `qualifies`
narrowing + tests; measure: empty-wake turns per seat per day before vs
after (the session logs give the baseline).
