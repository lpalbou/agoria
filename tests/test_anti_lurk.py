"""The anti-lurk mechanics (0077-0080), from the 2026-07-13 field failure:
seats ran compliant reception loops — listen, ack, re-arm — while acting on
nothing. Forensics on the live hub found the mechanical gaps these tests pin:
70 asks in 48h named seats only in prose (flagging nobody), answers to one's
own asks were silently ackable, and read-but-unanswered debt was invisible.

- 0077 per-ask addressing: asks[].to flags and pins the named seats.
- 0078 asker-side consumption: an unread, unfollowed answer to your own ask
  is a visible debt.
- 0079 the owed surface: GET /owed ignores read receipts on purpose.
- 0080 lurk visibility: acked_unanswered in the operator overview.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agora.hub.app import create_app

ADMIN_KEY = "test-admin"


@pytest.fixture()
def client() -> TestClient:
    app = create_app(db_path=":memory:", admin_key=ADMIN_KEY, rate_per_minute=600.0)
    return TestClient(app)


def _register(client, agent_id):
    r = client.post("/agents", headers={"Authorization": f"Bearer {ADMIN_KEY}"},
                    json={"id": agent_id, "about": ""})
    assert r.status_code == 200
    return r.json()["api_key"]


def _auth(key):
    return {"Authorization": f"Bearer {key}"}


@pytest.fixture()
def room(client):
    """A channel with three members: asker, named, bystander."""
    keys = {a: _register(client, a) for a in ("asker", "named", "bystander")}
    client.post("/channels", headers=_auth(keys["asker"]),
                json={"name": "canvass", "private": False})
    for a in ("named", "bystander"):
        client.post("/channels/canvass/join", headers=_auth(keys[a]), json={})
    return keys


def _post(client, key, **kw):
    payload = {"title": kw.pop("title", "t"), "body": kw.pop("body", "b"), **kw}
    r = client.post("/channels/canvass/messages", headers=_auth(key), json=payload)
    assert r.status_code == 200, r.text
    return r.json()


def _inbox(client, key):
    return client.get("/inbox", headers=_auth(key)).json()


# -- 0077: per-ask addressing ---------------------------------------------------


def test_ask_to_validates_membership_cap_and_self(client, room):
    k = room["asker"]
    r = client.post("/channels/canvass/messages", headers=_auth(k), json={
        "title": "t", "body": "b", "status": "open",
        "asks": [{"id": "1", "text": "x", "to": ["ghost"]}]})
    assert r.status_code == 400 and "non-members" in r.json()["detail"]

    r = client.post("/channels/canvass/messages", headers=_auth(k), json={
        "title": "t", "body": "b", "status": "open",
        "asks": [{"id": "1", "text": "x", "to": ["asker"]}]})
    assert r.status_code == 400 and "yourself" in r.json()["detail"]

    r = client.post("/channels/canvass/messages", headers=_auth(k), json={
        "title": "t", "body": "b", "status": "open",
        "asks": [{"id": "1", "text": "x",
                  "to": ["named", "bystander", "named", "bystander"]}]})
    assert r.status_code == 400 and "max 3" in r.json()["detail"]


def test_ask_named_seat_is_flagged_and_pinned_until_its_ask_is_answered(client, room):
    """Miss B made mechanical: a seat named by an ask gets to_me and the pin,
    the bystander does not — and the pin lifts for the named seat the moment
    ITS ask is answered, even while another seat's ask stays open."""
    msg = _post(client, room["asker"], status="open", title="canvass",
                asks=[{"id": "1", "text": "row for named", "to": ["named"]},
                      {"id": "2", "text": "row for bystander", "to": ["bystander"]}])

    env = next(e for e in _inbox(client, room["named"]) if e["id"] == msg["id"])
    assert env["to_me"] is True                      # flagged despite to=[]
    bys = next(e for e in _inbox(client, room["bystander"]) if e["id"] == msg["id"])
    assert bys["to_me"] is True                      # named by ask 2

    # named answers ITS ask and acks: its pin lifts, bystander's stays.
    _post(client, room["named"], status="reply", reply_to=msg["id"],
          answers=["1"], title="ans", body="done")
    client.post("/inbox/ack", headers=_auth(room["named"]),
                json={"cursors": {"canvass": 99}})
    client.post("/inbox/ack", headers=_auth(room["bystander"]),
                json={"cursors": {"canvass": 99}})
    assert not any(e["id"] == msg["id"] for e in _inbox(client, room["named"]))
    assert any(e["id"] == msg["id"] for e in _inbox(client, room["bystander"]))


# -- 0078 + 0079: owed ledgers ----------------------------------------------------


def test_owed_to_answer_ignores_read_receipts(client, room):
    """The lurk case itself: reading and acking an addressed ask does NOT
    clear the debt — only replying (or closure) does."""
    msg = _post(client, room["asker"], status="open", title="do X",
                asks=[{"id": "1", "text": "please do X", "to": ["named"]}])
    # named reads it (receipt) and acks past it — the classic silent lurk.
    client.get(f"/channels/canvass/messages/{msg['id']}", headers=_auth(room["named"]))
    client.post("/inbox/ack", headers=_auth(room["named"]),
                json={"cursors": {"canvass": 99}})

    owed = client.get("/owed", headers=_auth(room["named"])).json()
    assert owed["counts"]["to_answer"] == 1
    row = owed["to_answer"][0]
    assert row["id"] == msg["id"] and row["asks_naming_you"] == ["1"]

    # bystander owes nothing (the ask names only `named`).
    assert client.get("/owed", headers=_auth(room["bystander"])).json()["counts"]["to_answer"] == 0

    # replying clears it.
    _post(client, room["named"], status="reply", reply_to=msg["id"],
          answers=["1"], title="done", body="X done")
    owed = client.get("/owed", headers=_auth(room["named"])).json()
    assert owed["counts"]["to_answer"] == 0


def test_owed_to_consume_tracks_unread_answers_and_clears(client, room):
    """Miss A made mechanical: an answer to your own ask is a visible debt
    until you read it (receipt) or post later in-thread; an authoritative
    close clears everything."""
    msg = _post(client, room["asker"], status="open", title="my question",
                asks=[{"id": "1", "text": "which shape?"}])
    ans = _post(client, room["named"], status="reply", reply_to=msg["id"],
                answers=["1"], title="shape C", body="evidence...")

    owed = client.get("/owed", headers=_auth(room["asker"])).json()
    assert owed["counts"]["to_consume"] == 1
    row = owed["to_consume"][0]
    assert row["answered_by"] == "named" and row["answer_id"] == ans["id"]

    # Reading the ANSWER (the cheapest honest consumption) clears the debt.
    client.get(f"/channels/canvass/messages/{ans['id']}", headers=_auth(room["asker"]))
    owed = client.get("/owed", headers=_auth(room["asker"])).json()
    assert owed["counts"]["to_consume"] == 0

    # A second answer re-creates debt; a later in-thread post by the asker
    # (e.g. the resolved close) clears it without a read receipt.
    ans2 = _post(client, room["bystander"], status="reply", reply_to=msg["id"],
                 answers=["1"], title="also shape C", body="more evidence")
    assert client.get("/owed", headers=_auth(room["asker"])).json()["counts"]["to_consume"] == 1
    _post(client, room["asker"], status="resolved", reply_to=msg["id"],
          title="consumed: shape C it is", body="adopting C")
    assert client.get("/owed", headers=_auth(room["asker"])).json()["counts"]["to_consume"] == 0


# -- 0080: operator lurk visibility ------------------------------------------------


def test_addressed_obligation_survives_a_bare_read(client, room):
    """The 0080 root fix (watcher audit): read+ack was how lurking seats
    silenced the inbox, status, the stop hook, and the dark watchdog in one
    motion — `read_message` alone must NOT unpin an ADDRESSED obligation.
    Only engaging (a reply) clears it. Bystander economics are unchanged: a
    bystander's read still releases the broadcast pin."""
    msg = _post(client, room["asker"], status="open", title="for named",
                to=["named"], asks=[{"id": "1", "text": "row"}])

    # named reads AND acks — the lurk motion — and stays pinned.
    client.get(f"/channels/canvass/messages/{msg['id']}", headers=_auth(room["named"]))
    client.post("/inbox/ack", headers=_auth(room["named"]),
                json={"cursors": {"canvass": 99}})
    assert any(e["id"] == msg["id"] for e in _inbox(client, room["named"]))

    # Replying (engaging) is what unpins.
    _post(client, room["named"], status="reply", reply_to=msg["id"],
          answers=["1"], title="done", body="answered")
    assert not any(e["id"] == msg["id"] for e in _inbox(client, room["named"]))

    # Broadcast + bystander: a bare read still releases (unchanged economics).
    bmsg = _post(client, room["asker"], status="open", title="broadcast",
                 asks=[{"id": "1", "text": "anyone"}])
    client.get(f"/channels/canvass/messages/{bmsg['id']}",
               headers=_auth(room["bystander"]))
    client.post("/inbox/ack", headers=_auth(room["bystander"]),
                json={"cursors": {"canvass": 199}})
    assert not any(e["id"] == bmsg["id"] for e in _inbox(client, room["bystander"]))


def test_overview_counts_acked_unanswered(client, room):
    msg = _post(client, room["asker"], status="open", title="for named",
                asks=[{"id": "1", "text": "row", "to": ["named"]}])
    client.post("/inbox/ack", headers=_auth(room["named"]),
                json={"cursors": {"canvass": msg["seq"]}})

    rows = client.get("/admin/status",
                      headers={"Authorization": f"Bearer {ADMIN_KEY}"}).json()
    named = next(r for r in rows if r["agent_id"] == "named")
    assert named["acked_unanswered"] == 1 and named["owed_answers"] == 1
    asker = next(r for r in rows if r["agent_id"] == "asker")
    assert asker["acked_unanswered"] == 0
