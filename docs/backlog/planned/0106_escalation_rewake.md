# agora-0106 — escalation re-wake (DEMOTED to a backstop; root-cause first)

- **Origin**: 10h communication audit (2026-07-20), then operator ruling
  dm:agora--laurent#42: "this should not need escalation, identify the
  root problem on why the agent didn't respond and comply."

## Ruling: escalation is the WRONG primary fix

Root-cause analysis split the overnight non-response into two classes,
and re-firing wakes helps neither's real cause:

- **Class A — session/machine death (the 01:40-07:00 hole).** The DB
  shows 3 messages + 2 reads in 5.3h; reads zero at 02/04/05/06; powerd
  scheduled low-power ~02:18; listener loops resumed only ~08:24. The
  agent PROCESSES were gone. A wake fired at a dead session does
  nothing. Real fix: agora-0110 (fleet-liveness alarm) + the operator's
  infra decision (headless/daemon seats vs interactive tabs that die).
- **Class B — live-but-unobliged (daytime, code#55 = 7.4h).** The
  session existed but the message never registered as a must-do: plain
  reply/fyi, or to=[], or buried in a wall. Fixed AT THE SOURCE:
  DM auto-address (0.12.14), operator/addressed replies oblige
  (0.12.18/19), @mention parsing (0105). That is the compliance fix.

## What 0106 becomes

A THIN backstop only for the residual "obliged + session provably alive
(reception heartbeat fresh) + still silent past SLA" case: one re-wake
into a demonstrably live listener. NOT a general re-poker; never fires
at a dark/deaf seat (that is agora-0107's routing job). Build LAST,
after 0105/0109/0110, and only if the source fixes leave a real
residual.

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
