"""Obligation discharge: is an open/blocked message answered yet?

Two modes, chosen by the message itself:

- **binary** (legacy / no structured asks): any reply from someone other than
  the asker discharges the obligation. This is the original behavior and is
  preserved exactly for messages that carry no `asks`.
- **asks** (structured): the message carries numbered `asks` (stored in
  `data.asks`); a reply discharges specific ones by listing their ids in its
  `data.answers`. The obligation is discharged only when EVERY ask has a
  matching answer from a non-sender reply — so a reply that answers 1 of 3
  no longer silently clears the whole message (the partial-answer rot the
  file protocol suffered). This is the agents' unanimous top request, made
  mechanical: importance follows unanswered asks, not a sender's say-so.

Pure functions over already-loaded messages, so they are trivially testable and
carry no transport or storage concerns.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import Message


@dataclass
class DischargeState:
    mode: str = "binary"                       # "binary" | "asks"
    pending: list[str] = field(default_factory=list)   # unanswered ask ids
    answered: list[str] = field(default_factory=list)  # answered ask ids
    discharged: bool = False                   # obligation fully satisfied?

    @property
    def total(self) -> int:
        return len(self.pending) + len(self.answered)

    @property
    def progress(self) -> str:
        """Human/agent-scannable 'answered/total', e.g. '1/3'. Empty in binary
        mode (no structured asks to count)."""
        return f"{len(self.answered)}/{self.total}" if self.mode == "asks" else ""


def asks_of(message: Message) -> list[dict]:
    """The structured asks declared on a message (empty if none/malformed)."""
    asks = (message.data or {}).get("asks")
    if not isinstance(asks, list):
        return []
    return [a for a in asks if isinstance(a, dict) and a.get("id") is not None]


def _answers_of(message: Message) -> list[str]:
    ans = (message.data or {}).get("answers")
    return [str(a) for a in ans] if isinstance(ans, list) else []


def discharge_state(parent: Message, replies: list[Message]) -> DischargeState:
    """Compute whether `parent`'s obligation is discharged given its replies.

    A reply from the asker itself never discharges the asker's own obligation
    (you cannot answer your own question to silence it) — matching the existing
    `has_reply(exclude_sender=...)` rule.
    """
    non_sender = [r for r in replies if r.sender != parent.sender]
    asks = asks_of(parent)
    if not asks:
        return DischargeState(mode="binary", discharged=bool(non_sender))
    answered_ids: set[str] = set()
    for r in non_sender:
        answered_ids.update(_answers_of(r))
    ids = [str(a["id"]) for a in asks]
    pending = [i for i in ids if i not in answered_ids]
    answered = [i for i in ids if i in answered_ids]
    return DischargeState(mode="asks", pending=pending, answered=answered,
                          discharged=not pending)
