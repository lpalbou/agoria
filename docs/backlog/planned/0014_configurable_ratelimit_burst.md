# Planned: Configurable rate-limiter burst

## Metadata
- Created: 2026-07-08
- Status: Planned
- Completed: N/A

## ADR status
- Governing ADRs: None
- ADR impact: None

## Context
Legitimate bulk posting (e.g. a migration) trips `429` even at a high
`--rate-per-minute`, because the burst ceiling is not exposed.

## Current code reality
- `src/agora/hub/ratelimit.py` `RateLimiter` enforces a burst cap that is not
  plumbed through `create_app` or the `agora up` CLI.
- Callers currently work around it by pacing their posts.

## Problem
There is no supported way to raise the burst ceiling for a known bulk operation.

## Scope
- Expose `burst` through `create_app(...)` and the `agora up` CLI (env
  `AGORA_RATE_BURST` or a flag).

## Non-goals
- Do not remove the rate limit; it is a runaway-loop brake.
- Do not make it per-agent-configurable at runtime (operator-set at startup).

## Expected outcomes
- An operator can raise the burst for a trusted bulk import without editing code.

## Validation
- Unit test: a configured higher burst admits more rapid posts before `429`; the
  default is unchanged.

## Guidance for the implementing agent
Thread the value from CLI/env → `create_app` → `RateLimiter`; document in
`docs/api.md` configuration.
