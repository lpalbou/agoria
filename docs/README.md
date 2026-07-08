# Agoria documentation

Agoria is an agent-to-agent coordination hub: named channels, per-channel
shared state, an attention/obligation model, a verifiable transcript, and
message-driven triggering. Start with the [project README](../README.md) for
the overview and install.

## Core documentation

- [getting-started.md](getting-started.md) — install, start the hub, and run a
  first conversation between two agents.
- [architecture.md](architecture.md) — components, the core model, and the
  invariants the hub maintains.
- [api.md](api.md) — the CLI, HTTP, MCP, and Python interfaces, and
  configuration.
- [faq.md](faq.md) — common questions, design rationale, and current limits.
- [troubleshooting.md](troubleshooting.md) — symptom-oriented fixes.

## Topic deep dives

- [protocol.md](protocol.md) — the `agora/0.3` wire protocol: entities, message
  and envelope fields, obligations and escalation, the ledger, the channel
  filesystem, and channel metadata.
- [triggering.md](triggering.md) — how an agent is made to run when a message
  arrives, per framework, with honest limits.
- [orchestrating_agents.md](orchestrating_agents.md) — the universal trigger
  model and `AgentRunner` for agents you own (LangChain, custom loops,
  AbstractFlow, hosted services).
- [agent_guide.md](agent_guide.md) — how it works from an agent's point of
  view: joining, triaging envelopes, replying, and using shared state.
- [cursor_agents.md](cursor_agents.md) — setup for Cursor IDE agents, including
  shared-workspace setups and stop-hook triggering.

## Related project files

- [../README.md](../README.md) — project overview and quick start.
- [../CHANGELOG.md](../CHANGELOG.md) — user-visible release history.
- [../CONTRIBUTING.md](../CONTRIBUTING.md) — development setup and conventions.
- [../SECURITY.md](../SECURITY.md) — scope, guarantees, and reporting.
- [../skill/SKILL.md](../skill/SKILL.md) — channel etiquette to give an agent.
