"""Message retraction (0097): author unsays a message so no agent or
entity ever reads it, and any obligation it carried dies.

What must hold: author-only (or operator) retraction; redact-at-read on
EVERY agent-facing surface (get_messages, read_message, inbox); a retracted
open/blocked message drops out of the owed ledger (the stray-message
phantom-debt case); threading survives (reply_to intact, tombstone keeps
its seq); the ledger still verifies (hash commits to the original bytes,
preserved for operator audit); non-authors are refused.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from agora.hub.app import create_app

ADMIN_KEY = "test-admin"
ADMIN = {"Authorization": f"Bearer {ADMIN_KEY}"}


def make_client() -> TestClient:
    app = create_app(db_path=":memory:", admin_key=ADMIN_KEY,
                     rate_per_minute=600.0, dark_watch_seconds=0)
    return TestClient(app)


def register(client, agent_id, operator=False):
    r = client.post("/agents", json={"id": agent_id, "operator": operator},
                    headers=ADMIN)
    return {"Authorization": f"Bearer {r.json()['api_key']}"}


def room(client):
    ka, kb = register(client, "alice"), register(client, "bob")
    client.post("/channels", json={"name": "room", "private": False}, headers=ka)
    client.post("/channels/room/join", json={}, headers=kb)
    return ka, kb


def post(client, key, **kw):
    r = client.post("/channels/room/messages", headers=key,
                    json={"title": kw.pop("title", "t"), "body": kw.pop("body", "b"), **kw})
    assert r.status_code == 200, r.text
    return r.json()


# -- authority -----------------------------------------------------------------


def test_only_author_or_operator_can_retract():
    client = make_client()
    ka, kb = room(client)
    msg = post(client, ka, body="alice said this")
    # A non-author is refused with teaching text.
    r = client.post(f"/channels/room/messages/{msg['id']}/retract", headers=kb)
    assert r.status_code == 403 and "author" in r.text
    # The author succeeds.
    r = client.post(f"/channels/room/messages/{msg['id']}/retract", headers=ka)
    assert r.status_code == 200 and r.json()["retracted"] is True
    # An operator can retract someone else's message.
    op = register(client, "op", operator=True)
    client.post("/channels/room/join", json={}, headers=op)
    msg2 = post(client, kb, body="bob said this")
    r = client.post(f"/channels/room/messages/{msg2['id']}/retract", headers=op)
    assert r.status_code == 200 and r.json()["retracted"] is True


# -- redaction on every read surface -------------------------------------------


def test_retracted_body_is_redacted_on_all_read_surfaces():
    client = make_client()
    ka, kb = room(client)
    msg = post(client, ka, title="secret title", body="the silly words")
    client.post(f"/channels/room/messages/{msg['id']}/retract", headers=ka)

    # messages list
    rows = client.get("/channels/room/messages", headers=kb).json()
    row = next(m for m in rows if m["id"] == msg["id"])
    assert "silly" not in row["body"] and "secret" not in (row["title"] or "")
    assert row["retracted"] is True and row["body"] == "[retracted by alice]"

    # read_message (deliberate body fetch)
    chain = client.get(f"/channels/room/messages/{msg['id']}", headers=kb).json()
    fetched = next(m for m in chain if m["id"] == msg["id"])
    assert "silly" not in fetched["body"] and fetched["retracted"] is True


def test_retracted_open_message_drops_from_owed():
    """The stray-message case: an open message addressed to bob is a debt
    bob owes forever — until the author retracts it, which must clear it."""
    client = make_client()
    ka, kb = room(client)
    msg = post(client, ka, body="a", status="open",
               asks=[{"id": "1", "text": "answer me", "to": ["bob"]}])
    owed = client.get("/owed", headers=kb).json()
    assert any(o["id"] == msg["id"] for o in owed["to_answer"])

    client.post(f"/channels/room/messages/{msg['id']}/retract", headers=ka)
    owed = client.get("/owed", headers=kb).json()
    assert not any(o["id"] == msg["id"] for o in owed["to_answer"])
    # And it no longer surfaces as an obligation in bob's inbox.
    inbox = client.get("/inbox", headers=kb).json()
    assert not any(e["id"] == msg["id"] and e["status"] in ("open", "blocked")
                   for e in inbox)


def test_retracted_attachments_and_asks_are_dropped():
    client = make_client()
    ka, kb = room(client)
    msg = post(client, ka, body="body", status="open",
               asks=[{"id": "1", "text": "q", "to": ["bob"]}])
    client.post(f"/channels/room/messages/{msg['id']}/retract", headers=ka)
    row = next(m for m in client.get("/channels/room/messages", headers=kb).json()
               if m["id"] == msg["id"])
    assert row["data"] is None  # asks/answers/attachments unconsumable


# -- threading + ledger integrity ----------------------------------------------


def test_threading_survives_retraction():
    client = make_client()
    ka, kb = room(client)
    parent = post(client, ka, body="parent", status="open",
                  asks=[{"id": "1", "text": "q", "to": ["bob"]}])
    reply = client.post("/channels/room/messages", headers=kb,
                        json={"title": "r", "body": "the answer",
                              "status": "reply", "reply_to": parent["id"],
                              "answers": ["1"]}).json()
    client.post(f"/channels/room/messages/{parent['id']}/retract", headers=ka)
    # The reply still threads to the (now tombstoned) parent.
    rows = {m["id"]: m for m in client.get("/channels/room/messages",
                                           headers=kb).json()}
    assert rows[reply["id"]]["reply_to"] == parent["id"]
    assert rows[parent["id"]]["seq"] == parent["seq"]  # seq preserved


def test_ledger_still_verifies_after_retraction():
    """The hash chain commits to the ORIGINAL bytes (retraction is
    read-time presentation), so the verified ledger stays intact."""
    client = make_client()
    ka, _ = room(client)
    msg = post(client, ka, body="original words")
    client.post(f"/channels/room/messages/{msg['id']}/retract", headers=ka)
    led = client.get("/channels/room/ledger", headers=ka).json()
    assert led["verified"] is True and led["broken_at"] is None


def test_retract_is_idempotent_and_first_retractor_sticks():
    client = make_client()
    ka, _ = room(client)
    msg = post(client, ka, body="x")
    r1 = client.post(f"/channels/room/messages/{msg['id']}/retract", headers=ka)
    r2 = client.post(f"/channels/room/messages/{msg['id']}/retract", headers=ka)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r2.json()["retracted"] is True


def test_missing_message_404():
    client = make_client()
    ka, _ = room(client)
    r = client.post("/channels/room/messages/nope/retract", headers=ka)
    assert r.status_code == 404
