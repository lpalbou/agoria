"""Hub backup/restore (operator request c3963: 'sure agora backup and agora
restore could be useful').

What must hold: a snapshot of a LIVE db is a consistent, integrity-checked,
complete copy (messages, fs files, agents survive a round-trip); restore
refuses corrupt or non-hub files BEFORE touching anything; restore preserves
the current db aside (never destroys the only copy); stale WAL sidecars are
removed so old pages cannot resurrect.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from agora import backup
from agora.db import Database


def _make_hub_db(path: Path) -> None:
    db = Database(str(path))
    try:
        db.register_agent("op", "op", "k-op", operator=True)
        db.register_agent("flow", "flow", "k-flow")
        db.create_channel("room", False, "op")
        db.add_member("room", "flow")
        db.insert_message("room", "op", kind="message", status="fyi",
                          urgency="inbox", title="t", body="hello", data=None,
                          reply_to=None, critical=False, downgraded=False, to=[])
        db.store_set("room", "fs/notes.md",
                     {"content": "the file", "mime": "text/markdown"}, "op")
    finally:
        db.close()  # never leak the connection: a live WAL handle over the
        # same file breaks a later restore's fresh read (order-dependent).


def test_snapshot_roundtrip_preserves_everything(tmp_path):
    src = tmp_path / "hub.db"
    _make_hub_db(src)
    out = tmp_path / "backups" / "snap.db"
    info = backup.snapshot(src, out)
    assert Path(info["path"]).exists()
    assert info["counts"]["messages"] >= 1
    assert info["counts"]["agents"] == 2
    assert info["counts"]["fs_files"] == 1
    # The copy opens as a real hub db with the same content.
    conn = sqlite3.connect(out)
    assert conn.execute("SELECT body FROM messages").fetchone()[0] == "hello"


def test_snapshot_refuses_overwrite_and_missing_source(tmp_path):
    src = tmp_path / "hub.db"
    _make_hub_db(src)
    out = tmp_path / "snap.db"
    backup.snapshot(src, out)
    with pytest.raises(ValueError, match="refusing to overwrite"):
        backup.snapshot(src, out)
    with pytest.raises(ValueError, match="not found"):
        backup.snapshot(tmp_path / "nope.db", tmp_path / "x.db")


def test_restore_verifies_before_touching_and_preserves_current(tmp_path):
    db = tmp_path / "hub.db"
    _make_hub_db(db)
    snap = tmp_path / "snap.db"
    backup.snapshot(db, snap)

    # Corrupt/foreign snapshots are refused BEFORE the db is touched.
    junk = tmp_path / "junk.db"
    junk.write_bytes(b"not a database at all")
    with pytest.raises(ValueError):
        backup.restore(junk, db)
    foreign = tmp_path / "foreign.db"
    sqlite3.connect(foreign).execute("CREATE TABLE x (y)")
    with pytest.raises(ValueError, match="not a hub database"):
        backup.restore(foreign, db)
    # Untouched by the refusals.
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 1
    conn.close()

    # Mutate the live db, then restore the snapshot: content rolls back and
    # the pre-restore copy holds the mutated state.
    live = Database(str(db))
    live.insert_message("room", "flow", kind="message", status="fyi",
                        urgency="inbox", title="", body="after snapshot",
                        data=None, reply_to=None, critical=False,
                        downgraded=False, to=[])
    live.close()  # the CLI stops the hub before restore; simulate that here
    info = backup.restore(snap, db)
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 1
    conn.close()
    preserved = Path(info["preserved"])
    assert preserved.exists()
    conn = sqlite3.connect(preserved)
    assert conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 2


def test_restore_removes_stale_wal_sidecars(tmp_path):
    db = tmp_path / "hub.db"
    _make_hub_db(db)
    snap = tmp_path / "snap.db"
    backup.snapshot(db, snap)
    for suffix in ("-wal", "-shm"):
        Path(str(db) + suffix).write_bytes(b"stale")
    backup.restore(snap, db)
    for suffix in ("-wal", "-shm"):
        assert not Path(str(db) + suffix).exists()
