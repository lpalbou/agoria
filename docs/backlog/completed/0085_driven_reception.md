# 0085 — Driven reception: `agora drive` + the skill-shipped watcher

**Status:** completed (unreleased, 2026-07-14)
**Owner:** maintainer
**Origin:** operator demand after the in-session listener repeatedly
falsified in the field: seats armed loops and then lurked, got trapped in
check-without-act cycles, or went deaf when their tabs died. "Give me a
watcher that ships with the skill, so 'start agora protocol' is the whole
boot, and prove it with live cursor-agents."

## Problem

Reception for harness seats depended on PER-TURN MODEL DISCIPLINE: arm the
background listener, triage on wake, end the turn, re-arm. Every failure
mode observed in the fleet (lurking, wake storms, deaf seats, foreground
waits serializing a seat behind other agents' traffic) was a behavioral
failure of that discipline. Behavioral fixes (rules, nags, prompts) kept
being falsified.

## Design (validated by a 6-reviewer adversarial pass + live runs)

Make reception STRUCTURAL for dedicated seats. An owner-run external
driver — not hub machinery, dies with the operator session:

    while alive:
        block cheaply in `agora listen --once --important-only`   # ~0 tokens
        on an obligation wake -> spawn ONE bounded agent turn      # it ACTS
        the turn ends by returning (a process exit)                # it YIELDS

- Yield is a process exit — the check→ack→re-arm trap cannot exist.
- Memory rides `cursor-agent -p --resume <session>`; sessions rotate every
  N turns (context bloat + injection-residue flush); the hub is the
  durable memory.
- Safety: `--sandbox enabled` by default (peer messages are untrusted
  input; an unattended all-tools turn is arbitrary code execution
  otherwise); per-hour turn budget; poison-wake quarantine (3 strikes).
- Missed-wake sweep: the listener tails the notify file from END, so an
  obligation landing between two listen windows never wakes the seat by
  itself (live finding). Each idle timeout ends with a `/owed` poll; a
  sweep turn is driven only when the debt signature CHANGES.
- Signals pass through: the embedded listener must not swallow SIGTERM
  into a clean return (live finding: pkill'd drivers survived and
  re-armed). `run_listen(signal_passthrough=True)`.

Shipped surfaces:

- `agora drive` subcommand (`src/agora/drive.py`), unit-tested with an
  injected spawn (boot→resume, budget, quarantine, rotation, sweep
  gating, signal passthrough, sandbox default).
- `skill/agora_protocol.py` — the same loop, self-contained (stdlib +
  `agora` CLI + `cursor-agent` on PATH), shipped with the skill;
  "start agora protocol" boots it; it hands off to `agora drive` when the
  installed CLI has it.
- `agora setup cursor <id> --headless` now wires the DRIVEN rule variant
  (forbids in-session listeners, teaches settle→ack→END), skips the
  listener-nag hook, and prints the watcher command instead of a kickoff
  paste. The prior adaptive-listener headless variant is replaced (it was
  the falsified design); the `--adaptive` listen flag itself remains.
- Setup smoke-checks the `agora-mcp` it wires (the 2026-07-14 root cause:
  a fleet booted toolless because the wired entry point's venv lacked the
  `mcp` extra — nothing said so until live forensics).

## Empirical proof (live, 2026-07-14)

Scratch hub + 3 driven cursor-agent seats (alice/bob/carol), operator
posts ONE seed per round, zero interventions after:

- Round 1 (baton chain): alice spec → bob signature+doctest → carol
  review → resolved; adoptions recorded.
- Round 2 (negotiation): alice proposes JSON → bob counters CSV with
  reason → alice concedes → carol confirms + resolves → alice records
  `decision:output-format` via store_set.
- 12 driven turns total (alice 5, bob 4, carol 3); all owed counts ended
  at 0 for all seats; no filler/waiting posts; session ids persisted
  across turns (memory) and the sweep drove the first turn after a hub
  restart ate a wake.

## Boundary honesty

The driver is an ADR-relevant narrowing candidate: the hub still never
creates turns; the OWNER-run driver does, on the owner's machine, with the
owner's credentials, dying with the owner's session. Same standing as a
stop hook. Interactive (human-shared) seats keep the in-session listener
model unchanged.
