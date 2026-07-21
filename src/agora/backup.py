"""Hub backup/restore: the whole hub is ONE SQLite file (messages, channel
fs, store, agents, reputation — everything). These helpers make copying it
safe and restoring it hard to get wrong.

- `snapshot` uses SQLite's ONLINE backup API, which is correct against a
  LIVE hub under WAL (readers/writers keep going; the copy is a consistent
  point-in-time image). It then integrity-checks the copy and reports what
  it contains, so a backup is a verified artifact, not a hopeful `cp`.
- `restore` refuses to run the dangerous way: the CALLER must have stopped
  the hub (the CLI checks the port), the snapshot is integrity-checked and
  shape-checked BEFORE it replaces anything, the current db is preserved
  aside as `<db>.pre-restore-<ts>` (a restore must never be the thing that
  destroys data), and stale `-wal`/`-shm` sidecars are removed so the old
  WAL cannot resurrect overwritten state.

Operator verbs, hub-machine local; no hub process involvement.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import time
from pathlib import Path

#: Tables a real hub db always has — the shape check that stops someone
#: restoring an unrelated SQLite file over their hub.
_EXPECTED_TABLES = {"agents", "channels", "messages", "store"}


def _counts(conn: sqlite3.Connection) -> dict[str, int]:
    out: dict[str, int] = {}
    for table in ("messages", "agents", "channels"):
        out[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    out["fs_files"] = conn.execute(
        "SELECT COUNT(*) FROM store WHERE key LIKE 'fs/%'").fetchone()[0]
    return out


def _verify(path: Path) -> dict[str, int]:
    """Integrity-check + shape-check a db file; return its counts. Raises
    ValueError with a human reason on any failure. Opened with a normal
    connection (issuing only reads): `mode=ro` cannot open a live WAL
    database without directory write access for its `-shm`/`-wal`, which is
    exactly the state a snapshot-of-a-running-hub sees."""
    if not Path(path).exists():
        raise ValueError(f"file not found: {path}")
    conn = sqlite3.connect(str(path))
    try:
        try:
            ok = conn.execute("PRAGMA integrity_check").fetchone()[0]
        except sqlite3.DatabaseError as e:
            raise ValueError(f"not a valid SQLite database: {e}") from e
        if ok != "ok":
            raise ValueError(f"integrity_check failed: {ok}")
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        missing = _EXPECTED_TABLES - tables
        if missing:
            raise ValueError(f"not a hub database (missing tables: {sorted(missing)})")
        return _counts(conn)
    finally:
        conn.close()


def snapshot(db_path: str | Path, out_path: str | Path) -> dict:
    """Point-in-time copy of a (possibly live) hub db via the online backup
    API, verified after writing. Returns {path, bytes, counts}."""
    src_path, out = Path(db_path), Path(out_path)
    if not src_path.exists():
        raise ValueError(f"hub database not found: {src_path}")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise ValueError(f"refusing to overwrite existing file: {out}")
    # Normal connection (backup only reads the source): a live hub db under
    # WAL cannot be opened mode=ro without directory-level shm access.
    src = sqlite3.connect(str(src_path))
    dst = sqlite3.connect(str(out))
    try:
        src.backup(dst)  # online, WAL-safe, consistent point-in-time image
        dst.commit()
    finally:
        dst.close()
        src.close()
    counts = _verify(out)  # a backup is a VERIFIED artifact or it is nothing
    os.chmod(out, 0o600)   # the hub db carries key hashes + private DMs
    return {"path": str(out), "bytes": out.stat().st_size, "counts": counts}


def default_snapshot_path(backups_dir: str | Path) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return Path(backups_dir) / f"agora-{stamp}.db"


def restore(snapshot_path: str | Path, db_path: str | Path) -> dict:
    """Replace the hub db with a verified snapshot. The CALLER must ensure
    the hub is STOPPED (the CLI refuses while the port answers). The current
    db is kept aside — a restore never destroys the only copy of anything."""
    snap, db = Path(snapshot_path), Path(db_path)
    if not snap.exists():
        raise ValueError(f"snapshot not found: {snap}")
    counts = _verify(snap)  # refuse to install a corrupt/foreign file
    preserved = None
    if db.exists():
        preserved = db.with_name(
            db.name + f".pre-restore-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(db, preserved)
    # Stale WAL/SHM sidecars belong to the OLD db; left in place they could
    # replay old pages over the restored file at next open.
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(db) + suffix)
        if sidecar.exists():
            sidecar.unlink()
    shutil.copy2(snap, db)
    os.chmod(db, 0o600)
    return {"path": str(db), "counts": counts,
            "preserved": str(preserved) if preserved else None}
