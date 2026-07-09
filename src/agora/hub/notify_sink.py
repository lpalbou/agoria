"""Hub-written notify files: liveness without resident processes.

The file mailbox never had a liveness problem because the file was maintained
by the same thing that stored the data. This is agora's equivalent: the hub —
the one process that must exist anyway — appends one JSON line per delivered
message to `<notify_dir>/<agent>-inbox.log` for every member of the message's
channel. No watcher processes, no supervisors, no OS services: an agent (or
its harness) just tails its file, which is fresh for exactly as long as the
hub is up — and if the hub is down there is nothing to be notified about.

`agora watch` still exists for remote clients (a file on the hub's machine is
useless to them), but on the hub's own machine it is now redundant — and
running one against the same file would duplicate lines.

Best-effort by design: a failed file write must never fail a post.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

from ..models import Envelope


def notify_line(envelope: Envelope) -> str:
    """One compact JSON line per message — the same shape `agora watch` emits,
    so existing tailers keep working unchanged."""
    flags = ",".join(f for f, on in [
        ("critical", envelope.critical), ("escalated", envelope.escalated),
        ("to-me", envelope.to_me), ("reply-to-me", envelope.reply_to_me),
        (envelope.status.value, envelope.status.value in ("open", "blocked")),
    ] if on)
    preview = (envelope.body or "")[:200]
    return json.dumps({
        "channel": envelope.channel, "seq": envelope.seq,
        "from": envelope.sender, "id": envelope.id,
        "status": envelope.status.value, "title": envelope.title,
        "flags": flags, **({"preview": preview} if preview else {}),
    })


class NotifySink:
    """Appends viewer-specific envelope lines to per-agent notify files."""

    def __init__(self, notify_dir: str | Path) -> None:
        self._dir = Path(notify_dir).expanduser()
        self._lock = threading.Lock()  # posts come from worker threads

    def deliver(self, agent_id: str, envelope: Envelope) -> None:
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
            line = notify_line(envelope)
            with self._lock, open(self._dir / f"{agent_id}-inbox.log", "a") as fh:
                fh.write(line + "\n")
        except OSError:
            pass  # best-effort: never fail a post over a notify write
