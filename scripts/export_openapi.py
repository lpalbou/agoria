#!/usr/bin/env python3
"""Export the hub's OpenAPI document as a release artifact.

    python3 scripts/export_openapi.py [openapi.json]

The export is DESCRIPTIVE, NOT NORMATIVE: it is generated from the running
implementation, so it is exact for the release it ships with, but the wire
contract — semantics, canonicalization, versioning policy — is
docs/protocol.md. The stamp below says so inside the document itself, since
the file will be read far from this repo.
"""

from __future__ import annotations

import json
import sys


def build_document() -> dict:
    from agora import PROTOCOL_VERSION, __version__
    from agora.hub.app import create_app

    app = create_app(db_path=":memory:", admin_key="openapi-export")
    doc = app.openapi()
    doc["info"]["title"] = "Agora Hub HTTP API"
    doc["info"]["description"] = (
        f"Generated from agorahub {__version__} (wire protocol "
        f"{PROTOCOL_VERSION}). Descriptive, not normative: this document "
        "mirrors the implementation it was exported from. The authoritative "
        "wire contract — semantics, ledger canonicalization, and the "
        "version-bump policy — is docs/protocol.md in the repository."
    )
    doc["info"]["x-agora-protocol"] = PROTOCOL_VERSION
    return doc


def main(argv: list[str]) -> int:
    out = argv[0] if argv else "openapi.json"
    doc = build_document()
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False)
        fh.write("\n")
    print(f"wrote {out} ({len(doc.get('paths', {}))} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
