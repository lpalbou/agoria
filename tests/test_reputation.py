"""Reputation (0094): peer ±1 on four fixed axes, per-channel scores that
sum to the hub score, leaderboards at both levels, full attribution.

The anti-gaming contract under test: identity-bound votes (auth is the
rater), ONE live vote per (rater, target, axis, channel) with
revision-in-place (never stacking), self-votes refused, membership required
on both sides, notes bounded, archived channels read-only, and the audit
surface (votes-for) naming who stands where on whom.
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


def register(client, agent_id):
    r = client.post("/agents", json={"id": agent_id}, headers=ADMIN)
    return {"Authorization": f"Bearer {r.json()['api_key']}"}


def setup_room(client, name="workroom", *, private=False):
    """Three members (alpha owner, beta, gamma) + outsider not in the room."""
    keys = {a: register(client, a) for a in ("alpha", "beta", "gamma", "outsider")}
    client.post("/channels", json={"name": name, "private": private},
                headers=keys["alpha"])
    for a in ("beta", "gamma"):
        client.post(f"/channels/{name}/join", json={}, headers=keys[a])
    return keys


def rate(client, key, target, axis="trust", value=1, note="", channel="workroom"):
    return client.put(f"/channels/{channel}/reputation/{target}",
                      json={"axis": axis, "value": value, "note": note},
                      headers=key)


# -- casting: validation walls ------------------------------------------------


def test_vote_requires_valid_axis_value_and_no_self():
    client = make_client()
    k = setup_room(client)
    r = rate(client, k["alpha"], "beta", axis="charisma")
    assert r.status_code == 400 and "axis must be one of" in r.text
    r = rate(client, k["alpha"], "beta", value=5)
    assert r.status_code == 400 and "+1 or -1" in r.text
    r = rate(client, k["alpha"], "beta", value=0)
    assert r.status_code == 400
    r = rate(client, k["alpha"], "alpha")
    assert r.status_code == 400 and "self-votes are refused" in r.text


def test_vote_requires_shared_membership_both_sides():
    client = make_client()
    k = setup_room(client)
    # Rater outside the channel: refused at the membership wall.
    r = rate(client, k["outsider"], "beta")
    assert r.status_code == 403
    # Target outside the channel: refused with the teaching text.
    r = rate(client, k["alpha"], "outsider")
    assert r.status_code == 400 and "not a member" in r.text
    # Unregistered target: 404.
    r = rate(client, k["alpha"], "ghost")
    assert r.status_code == 404


def test_note_bounded_at_280():
    client = make_client()
    k = setup_room(client)
    r = rate(client, k["alpha"], "beta", note="x" * 281)
    assert r.status_code == 413
    r = rate(client, k["alpha"], "beta", note="x" * 280)
    assert r.status_code == 200


# -- the one-live-vote invariant ----------------------------------------------


def test_revision_replaces_never_stacks():
    client = make_client()
    k = setup_room(client)
    assert rate(client, k["alpha"], "beta", value=1).status_code == 200
    assert rate(client, k["alpha"], "beta", value=1).status_code == 200
    assert rate(client, k["alpha"], "beta", value=1).status_code == 200
    board = client.get("/channels/workroom/reputation",
                       headers=k["alpha"]).json()
    row = next(r for r in board["leaderboard"] if r["target"] == "beta")
    # Three casts, ONE ballot: the score is +1, not +3.
    assert row["total"] == 1 and row["axes"]["trust"]["score"] == 1
    assert row["raters"] == 1

    # Flipping the vote replaces it in place: -1, not 0-sum history.
    assert rate(client, k["alpha"], "beta", value=-1,
                note="claimed shipped; was not").status_code == 200
    board = client.get("/channels/workroom/reputation",
                       headers=k["alpha"]).json()
    row = next(r for r in board["leaderboard"] if r["target"] == "beta")
    assert row["total"] == -1
    assert row["axes"]["trust"] == {"score": -1, "up": 0, "down": 1}


def test_withdraw_vote():
    client = make_client()
    k = setup_room(client)
    rate(client, k["alpha"], "beta", axis="trust", value=1)
    rate(client, k["alpha"], "beta", axis="helper", value=1)
    r = client.delete("/channels/workroom/reputation/beta?axis=trust",
                      headers=k["alpha"])
    assert r.json()["removed"] == 1
    r = client.delete("/channels/workroom/reputation/beta",
                      headers=k["alpha"])
    assert r.json()["removed"] == 1  # the remaining helper vote
    board = client.get("/channels/workroom/reputation",
                       headers=k["alpha"]).json()
    assert board["leaderboard"] == []


# -- scores, leaderboards, and the hub sum -------------------------------------


def test_channel_leaderboard_shape_and_order():
    client = make_client()
    k = setup_room(client)
    rate(client, k["alpha"], "beta", axis="trust", value=1)
    rate(client, k["gamma"], "beta", axis="thorough", value=1)
    rate(client, k["alpha"], "gamma", axis="helper", value=-1)
    board = client.get("/channels/workroom/reputation",
                       headers=k["beta"]).json()
    assert board["channel"] == "workroom"
    assert board["axes"] == ["trust", "wisdom", "thorough", "helper"]
    lb = board["leaderboard"]
    assert [r["target"] for r in lb] == ["beta", "gamma"]  # +2 before -1
    beta = lb[0]
    assert beta["total"] == 2 and beta["raters"] == 2
    assert beta["axes"]["trust"] == {"score": 1, "up": 1, "down": 0}
    assert beta["axes"]["thorough"] == {"score": 1, "up": 1, "down": 0}


def test_hub_reputation_is_sum_over_channels():
    client = make_client()
    k = setup_room(client)
    # Second shared room with its own votes.
    client.post("/channels", json={"name": "lab", "private": False},
                headers=k["alpha"])
    client.post("/channels/lab/join", json={}, headers=k["beta"])
    rate(client, k["alpha"], "beta", axis="trust", value=1)
    rate(client, k["gamma"], "beta", axis="trust", value=1)
    rate(client, k["alpha"], "beta", axis="trust", value=1, channel="lab")

    hub = client.get("/reputation", headers=k["outsider"]).json()
    assert hub["channel"] is None
    row = next(r for r in hub["leaderboard"] if r["target"] == "beta")
    # workroom (+2) + lab (+1) = 3, across 2 channels.
    assert row["total"] == 3 and row["channels"] == 2
    assert row["axes"]["trust"]["up"] == 3

    # Channel boards stay membership-gated; the outsider reads only hub.
    r = client.get("/channels/workroom/reputation", headers=k["outsider"])
    assert r.status_code == 403


def test_votes_audit_surface_names_raters_and_whys():
    client = make_client()
    k = setup_room(client)
    rate(client, k["alpha"], "beta", axis="trust", value=1,
         note="receipts matched claims all week")
    rate(client, k["gamma"], "beta", axis="trust", value=-1,
         note="two stale version claims")
    votes = client.get("/channels/workroom/reputation/beta/votes",
                       headers=k["beta"]).json()
    assert {v["rater"] for v in votes} == {"alpha", "gamma"}
    assert all(v["note"] for v in votes)
    # Non-members cannot read the audit surface.
    r = client.get("/channels/workroom/reputation/beta/votes",
                   headers=k["outsider"])
    assert r.status_code == 403


# -- lifecycle interactions -----------------------------------------------------


def test_archived_channel_refuses_new_votes_keeps_board_readable():
    client = make_client()
    k = setup_room(client)
    rate(client, k["alpha"], "beta", value=1)
    op = register(client, "operator-x")
    client.app.state.service.db._conn.execute(
        "UPDATE agents SET operator = 1 WHERE id = 'operator-x'")
    client.app.state.service.db._conn.commit()
    r = client.post("/channels/workroom/archive", headers=op, json={})
    assert r.status_code == 200, r.text
    r = rate(client, k["alpha"], "beta", value=-1)
    assert r.status_code in (403, 409)  # archived: no new judgment written
    # Hub-wide board still carries the history.
    hub = client.get("/reputation", headers=k["alpha"]).json()
    assert any(row["target"] == "beta" for row in hub["leaderboard"])
