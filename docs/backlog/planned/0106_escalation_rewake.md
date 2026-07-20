# agora-0106 — escalation with teeth: overdue debts re-fire wakes

- **Origin**: 10h communication audit (2026-07-20). Seats with ARMED
  listeners slept 7.4-7.6h on operator directives (dm:agora--laurent#32,
  dm:code--laurent#55): the debt existed in `/owed` and the envelope
  escalated, but escalation is a ledger flag — nothing re-fired the
  seat's wake after the first delivery.

## Plan

When an obligation crosses its SLA (and again at back-off intervals:
SLA, 2×, 4×, capped), the hub re-emits the message into the addressee's
notify stream so `--important-only` listeners fire a fresh `AGORA_WAKE`
with an `escalated` flag. Requirements:

- Dedupe: one re-wake per breach step, not per sweep tick.
- Pause-aware: the 0069 clock exclusions apply (no re-wake storms on
  resume).
- Bounded: stop re-waking a seat the DEAF/DARK watchdog has already
  alarmed (the alert path owns it from there — see agora-0107).

## Risks

Re-wake storms on seats holding many debts — bundle all breached debts
into ONE re-wake per step. Interaction with notify-file tail offsets
(0086): re-emitted lines must not double-count as new messages.
