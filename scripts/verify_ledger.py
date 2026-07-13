#!/usr/bin/env python3
"""Standalone Agora ledger verifier — stdlib only, no agora imports.

Written from the canonicalization rules in docs/protocol.md ("Verbatim
ledger", agora/0.3) and nothing else, as proof that the document alone
suffices to verify a transcript:

    python3 scripts/verify_ledger.py ledger.json
    python3 scripts/verify_ledger.py http://127.0.0.1:8765/channels/commons/ledger --key agora_...

Input is a ledger response: {"channel", "count", "head", "turns": [...]}.
Exit code 0 = chain intact and head matches; 1 = tampering detected; 2 = bad
input. Independence matters: this script recomputes every hash from the
served turns — it never trusts the hub's own `verified` flag.
"""

from __future__ import annotations

import hashlib
import json
import sys

# The 15 hashed fields of a turn, per docs/protocol.md rule 1. The ledger
# response may carry more (it doesn't today); anything else is ignored.
HASHED_FIELDS = ("id", "channel", "seq", "sender", "kind", "status", "urgency",
                 "critical", "downgraded", "to", "title", "body", "data",
                 "reply_to", "created_at")


def turn_hash(prev_hash: str, turn: dict, channel: str) -> str:
    """Rules 1-3: canonical payload, then sha256(prev + "\\n" + payload)."""
    fields = {k: turn[k] for k in HASHED_FIELDS if k != "channel"}
    fields["channel"] = channel  # turns omit it; the response names it once
    payload = json.dumps(fields, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True)
    return hashlib.sha256((prev_hash + "\n" + payload).encode()).hexdigest()


def verify(ledger: dict) -> dict:
    """Rule 4 over a full ledger response. Returns
    {ok, head_ok, computed_head, broken_at, hashed, legacy}."""
    channel = ledger["channel"]
    prev = ""
    hashed = legacy = 0
    broken_at = None
    computed_head = ""
    for turn in ledger["turns"]:
        if turn.get("hash") is None:      # unhashed legacy turn: chain restarts
            legacy += 1
            prev = ""
            continue
        expect = turn_hash(prev, turn, channel)
        if expect != turn["hash"] and broken_at is None:
            broken_at = turn["seq"]
        prev = turn["hash"]               # walk the stored chain, like the hub
        computed_head = expect            # last recomputed hash
        hashed += 1
    # An intact chain must also commit to the served head; a broken chain
    # cannot have a meaningful head comparison.
    head_ok = broken_at is None and ledger.get("head", "") == computed_head
    return {"ok": head_ok, "head_ok": head_ok,
            "computed_head": computed_head, "broken_at": broken_at,
            "hashed": hashed, "legacy": legacy}


def _load(source: str, key: str | None) -> dict:
    if source.startswith(("http://", "https://")):
        from urllib.request import Request, urlopen
        req = Request(source, headers={"Authorization": f"Bearer {key}"} if key else {})
        with urlopen(req, timeout=30) as r:
            return json.load(r)
    with open(source, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    key = None
    for i, a in enumerate(argv):
        if a == "--key" and i + 1 < len(argv):
            key = argv[i + 1]
            args = [x for x in args if x != key]
    if len(args) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        ledger = _load(args[0], key)
        result = verify(ledger)
    except Exception as exc:  # bad path/URL/JSON: report, don't traceback
        print(f"error: {exc}", file=sys.stderr)
        return 2
    verdict = "INTACT" if result["ok"] else "TAMPERED"
    print(f"{verdict}  channel={ledger.get('channel')}  hashed={result['hashed']}"
          f"  legacy={result['legacy']}  head_ok={result['head_ok']}"
          + (f"  broken_at={result['broken_at']}" if result["broken_at"] is not None else ""))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
