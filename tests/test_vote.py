"""/vote + /tally — the blind-ballot voting convention.

What must not regress: the argument grammar (topic + distinct options),
ballot parsing (LLM voters add punctuation, rank with '>', revise
themselves, tag their DM ballots for one vote among several), ballot
secrecy (chair-only counts while the vote runs, everyone after the close,
forged results ignored), the tally math (latest ballot wins, borda only
when someone ranked), and the published result (auditable roll call,
machine-readable payload the transcript view re-derives from).
"""

import asyncio
import time

from agora.chat import ChatApp
from agora.models import Message, Status
from agora.vote import (VoteTally, ballot_from, parse_ballot,
                        parse_dm_ballot, parse_vote_arg, result_body,
                        tally_ballots, vote_block, vote_body)

OPTS = ["sqlite", "postgres", "flat files"]
TAG = "v-abc123"


# -- argument grammar ------------------------------------------------------------

def test_parse_vote_arg_splits_topic_and_options():
    assert parse_vote_arg("pick a db | sqlite | postgres") == \
        ("pick a db", ["sqlite", "postgres"])
    # Blank and duplicate options are dropped (duplicates would split a tally).
    assert parse_vote_arg("t | a |  | A. | b") == ("t", ["a", "b"])


def test_parse_vote_arg_rejects_unusable_shapes():
    assert parse_vote_arg("no options at all") is None
    assert parse_vote_arg("topic | only-one") is None
    assert parse_vote_arg(" | a | b") is None


# -- ballot parsing ----------------------------------------------------------------

def test_parse_ballot_accepts_text_number_case_and_punctuation():
    assert parse_ballot("vote: sqlite", OPTS) == [0]
    assert parse_ballot("VOTE: 2", OPTS) == [1]
    assert parse_ballot("reasoning first\nvote: 'SQLite.'", OPTS) == [0]
    assert parse_ballot("vote: Flat files!", OPTS) == [2]


def test_parse_ballot_ranking_last_line_wins_and_dedupes():
    assert parse_ballot("vote: 2 > 1 > 3", OPTS) == [1, 0, 2]
    two_lines = "vote: sqlite\nactually, reconsidering:\nvote: 3 > 1"
    assert parse_ballot(two_lines, OPTS) == [2, 0]      # the LAST vote line
    assert parse_ballot("vote: 1 > 1 > 2", OPTS) == [0, 1]


def test_parse_ballot_refuses_to_guess():
    """An item naming something not offered invalidates the whole ballot —
    a miscounted vote is worse than an uncounted one (the reply then shows
    up as a comment in the tally, so nothing disappears silently)."""
    assert parse_ballot("vote: mongodb", OPTS) is None
    assert parse_ballot("vote: sqlite > mongodb", OPTS) is None
    assert parse_ballot("no vote line here at all", OPTS) is None
    assert parse_ballot("vote: 9", OPTS) is None        # out of range


def test_parse_dm_ballot_matches_only_this_votes_tag():
    """DM ballots are tagged — one DM thread may carry ballots for several
    concurrent votes, so untagged or foreign-tagged lines never count."""
    refs = {TAG, "731@commons"}
    assert parse_dm_ballot(f"vote {TAG}: 2 > 1", refs, OPTS) == [1, 0]
    assert parse_dm_ballot("vote 731@commons: sqlite", refs, OPTS) == [0]
    assert parse_dm_ballot("vote #731@commons: 1", refs, OPTS) == [0]
    assert parse_dm_ballot(f"vote {TAG.upper()}: 'SQLite.'", refs, OPTS) == [0]
    assert parse_dm_ballot("vote v-other: 1", refs, OPTS) is None
    assert parse_dm_ballot("vote: 1", refs, OPTS) is None      # untagged
    both = f"vote v-other: 2\nvote {TAG}: 1"
    assert parse_dm_ballot(both, refs, OPTS) == [0]
    revised = f"vote {TAG}: 1\nno wait:\nvote {TAG}: 2"
    assert parse_dm_ballot(revised, refs, OPTS) == [1]


def test_ballot_from_prefers_structured_data():
    assert ballot_from("prose says vote: 1", {"vote": ["postgres"]}, OPTS) == [1]
    assert ballot_from("", {"vote": "3"}, OPTS) == [2]
    assert ballot_from("vote: 1", None, OPTS) == [0]


# -- tally math ---------------------------------------------------------------------

def test_tally_counts_first_choices_and_borda_only_when_ranked():
    plain = tally_ballots(OPTS, {"a": [0], "b": [0], "c": [1]})
    assert plain.first == [2, 1, 0] and plain.borda is None
    assert plain.voters[0] == ["a", "b"] and plain.ranked == 0

    mixed = tally_ballots(OPTS, {"a": [0], "b": [1, 0, 2]})
    # borda (n=3): single-choice a -> sqlite +2; b ranks postgres 2, sqlite 1.
    assert mixed.first == [1, 1, 0]
    assert mixed.borda == [3, 2, 0] and mixed.ranked == 1


# -- rendering ----------------------------------------------------------------------

def test_vote_body_states_the_blind_dm_contract():
    body = vote_body("pick a db", OPTS, "laurent", TAG)
    assert "BLIND VOTE" in body and "do NOT post your choice" in body
    assert "DM your ballot to laurent" in body
    assert f"vote {TAG}: <option number" in body
    assert "2. postgres" in body


def test_vote_block_shows_counts_notes_and_footer():
    from agora.chat_render import Style
    tally = VoteTally(first=[2, 1, 0], voters=[["observer", "memory"],
                                               ["gateway"], []],
                      borda=[3, 2, 0], ranked=1)
    block = vote_block(Style(False), ref="731", topic="pick a db",
                       options=OPTS, tally=tally, total_members=6,
                       waiting=["flow (working)"], comments=["hub"],
                       notes=["public ballot (visible to everyone): observer"],
                       footer="chair view — /tally 731 close")
    assert "VOTE #731 pick a db — 3/6 voted" in block
    assert "1. sqlite" in block and " 2  observer, memory" in block
    assert "borda: sqlite 3 > postgres 2" in block
    assert "waiting: flow (working)" in block
    assert "commented, no ballot: hub" in block
    assert "public ballot (visible to everyone): observer" in block
    assert "chair view — /tally 731 close" in block


def test_result_body_is_the_auditable_roll_call():
    tally = tally_ballots(OPTS, {"observer": [0], "memory": [0],
                                 "gateway": [1, 0]})
    body = result_body("pick a db", OPTS, tally, 6)
    assert body.startswith("VOTE RESULT — pick a db")
    assert "sqlite: 2  (observer, memory)" in body
    assert "postgres: 1  (gateway)" in body
    assert "turnout 3/6" in body


# -- the commands: blind lifecycle -----------------------------------------------------

def _vote_msg(sender: str = "laurent",
              closes_at: float | None = None) -> Message:
    spec = {"topic": "pick a db", "options": OPTS, "tag": TAG,
            "ballots": "dm"}
    if closes_at is not None:
        spec["closes_at"] = closes_at
    return Message(id="01HVOTE731", channel="commons", seq=731,
                   sender=sender, title="VOTE: pick a db",
                   body=vote_body("pick a db", OPTS, sender, TAG),
                   status=Status.open, created_at=time.time() - 300,
                   data={"vote": spec})


def _reply(sender, seq, body, data=None):
    return Message(id=f"01HR{seq}", channel="commons", seq=seq, sender=sender,
                   body=body, status=Status.reply, reply_to="01HVOTE731",
                   created_at=time.time(), data=data)


def _dm(channel, sender, seq, body):
    return Message(id=f"01HD{seq}", channel=channel, seq=seq, sender=sender,
                   body=body, created_at=time.time())


def _wire(app, vote, channel_replies, dm_pages, members=None, presence=()):
    """Stub the client surface cmd_tally touches."""
    async def list_channels():
        return ([{"name": "commons", "member": True}]
                + [{"name": n, "member": True} for n in dm_pages]
                + [{"name": "spectator", "member": False}])

    async def history(channel, since=0, limit=200):
        if limit == 1:
            return [vote]
        if channel == "commons":
            return channel_replies if since == vote.seq else []
        return dm_pages.get(channel, []) if since == 0 else []

    async def read(channel, mid):
        assert (channel, mid) == ("commons", vote.id)
        return [vote]

    async def channel_info(channel):
        return {"members": [{"agent_id": a} for a in (members or [])]}

    class FakeHTTP:
        async def get(self, path):
            assert path == "/presence"
            return [{"agent_id": a, "state": s} for a, s in presence]

    app.client.list_channels = list_channels
    app.client.history = history
    app.client.read = read
    app.client.channel_info = channel_info
    app.client._http = FakeHTTP()
    app.client._json = lambda resp: resp
    out: list[str] = []
    app._print = lambda text="": out.append(text)
    return out


MEMBERS = ["laurent", "observer", "gateway", "memory", "uic", "flow"]


def test_chair_tally_folds_dm_ballots_public_leaks_and_comments():
    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    vote = _vote_msg()
    channel_replies = [
        _reply("uic", 733, "no strong preference, both work for the console"),
        _reply("observer", 734, "leaking on purpose:\nvote: sqlite"),
    ]
    dm_pages = {
        "dm:gateway--laurent": [
            _dm("dm:gateway--laurent", "gateway", 3, f"vote {TAG}: 1"),
            _dm("dm:gateway--laurent", "laurent", 4, f"(nudge) vote {TAG}: …"),
            _dm("dm:gateway--laurent", "gateway", 5,
                f"reconsidered:\nvote {TAG}: 2 > 1"),
        ],
        "dm:laurent--memory": [
            _dm("dm:laurent--memory", "memory", 7, "vote v-other: 2"),
            _dm("dm:laurent--memory", "memory", 8, f"vote {TAG}: 'SQLite.'"),
        ],
    }
    out = _wire(app, vote, channel_replies, dm_pages, MEMBERS,
                presence=[("flow", "working"), ("uic", "offline")])

    asyncio.run(app.cmd_tally("731"))
    text = "\n".join(out)
    assert "3/6 voted" in text
    assert " 2  observer, memory" in text        # sqlite: leak + DM ballot
    assert " 1  gateway" in text                 # postgres, after revision
    assert "public ballot (visible to everyone): observer" in text
    assert "waiting: flow (working), uic (offline)" in text
    assert "commented, no ballot: uic" in text
    assert "chair view (only you see this)" in text
    # My own nudge line in the DM thread must never count as a ballot.
    assert "laurent" not in text.split("waiting:")[0].split("voted")[1]


def test_non_author_gets_blind_notice_and_cannot_close():
    app = ChatApp("http://127.0.0.1:1", "k", "observer")
    app.current = "commons"
    vote = _vote_msg(sender="laurent")
    out = _wire(app, vote, [], {}, MEMBERS)

    asyncio.run(app.cmd_tally("731"))
    text = "\n".join(out)
    assert "blind" in text and "DM to laurent" in text
    assert "voted" not in text                   # no counts leak pre-close
    out.clear()
    asyncio.run(app.cmd_tally("731 close"))
    assert any("only laurent" in line for line in out)


def test_close_publishes_resolved_result_with_payload():
    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    vote = _vote_msg()
    dm_pages = {
        "dm:gateway--laurent": [
            _dm("dm:gateway--laurent", "gateway", 3, f"vote {TAG}: 2 > 1")],
        "dm:laurent--memory": [
            _dm("dm:laurent--memory", "memory", 8, f"vote {TAG}: sqlite")],
    }
    out = _wire(app, vote, [], dm_pages, MEMBERS)
    posts = []

    async def post(channel, body, **kw):
        posts.append((channel, body, kw))
        return Message(id="01HRESULT", channel="commons", seq=740,
                       sender="laurent", body=body, status=Status.resolved)
    app.client.post = post

    asyncio.run(app.cmd_tally("731 close"))
    channel, body, kw = posts[0]
    assert channel == "commons" and kw["status"] == Status.resolved
    assert kw["reply_to"] == vote.id
    payload = kw["data"]["vote_result"]
    assert payload["ballots"] == {"gateway": [1, 0], "memory": [0]}
    assert payload["total_members"] == 6
    assert "VOTE RESULT — pick a db" in body and "turnout 2/6" in body
    text = "\n".join(out)
    assert "result published as #740" in text
    assert "closed — published as #740" in text


def test_after_close_anyone_tallies_from_the_transcript():
    app = ChatApp("http://127.0.0.1:1", "k", "observer")   # NOT the author
    app.current = "commons"
    vote = _vote_msg(sender="laurent")
    forged = _reply("uic", 738, "hah", data={"vote_result": {
        "ballots": {"uic": [1]}, "total_members": 6}})
    real = _reply("laurent", 740, "VOTE RESULT — pick a db",
                  data={"vote_result": {
                      "ballots": {"gateway": [1, 0], "memory": [0],
                                  "ghost": [99]},     # 99: tolerated, dropped
                      "total_members": 6}})
    out = _wire(app, vote, [forged, real], {}, MEMBERS)

    asyncio.run(app.cmd_tally("731"))
    text = "\n".join(out)
    assert "2/6 voted" in text
    assert " 1  memory" in text and " 1  gateway" in text
    assert "closed by laurent — published as #740" in text
    assert "uic" not in text                     # the forged payload is ignored


def test_forged_result_alone_does_not_close_the_vote():
    app = ChatApp("http://127.0.0.1:1", "k", "observer")
    app.current = "commons"
    vote = _vote_msg(sender="laurent")
    forged = _reply("uic", 738, "hah", data={"vote_result": {
        "ballots": {"uic": [1]}, "total_members": 6}})
    out = _wire(app, vote, [forged], {}, MEMBERS)

    asyncio.run(app.cmd_tally("731"))
    text = "\n".join(out)
    assert "blind" in text and "closed by" not in text


def test_cmd_vote_posts_blind_vote_with_tag_and_confirms():
    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    posts = []

    async def post(channel, body, **kw):
        posts.append((channel, body, kw))
        return _vote_msg()
    app.client.post = post
    out: list[str] = []
    app._print = lambda text="": out.append(text)

    asyncio.run(app.cmd_vote("pick a db | sqlite | postgres | flat files"))
    channel, body, kw = posts[0]
    assert channel == "commons" and kw["status"] == Status.open
    spec = kw["data"]["vote"]
    assert spec["options"] == OPTS and spec["ballots"] == "dm"
    assert spec["tag"].startswith("v-") and f"vote {spec['tag']}:" in body
    assert "BLIND VOTE" in body
    # Default 30m deadline is stamped into the payload and announced.
    assert abs(spec["closes_at"] - (time.time() + 1800)) < 5
    assert "closes in 30m" in body
    assert app.votes.open                        # registered with the watcher
    assert any("auto-publishes in 30m" in line for line in out)
    assert any("close early: /tally 731 close" in line for line in out)

    out.clear()
    asyncio.run(app.cmd_vote("2h pick a db | sqlite | postgres"))
    spec = posts[1][2]["data"]["vote"]
    assert abs(spec["closes_at"] - (time.time() + 7200)) < 5   # '2h' override

    out.clear()
    asyncio.run(app.cmd_vote("no pipes given"))
    assert posts[2:] == [] and any("usage: /vote" in line for line in out)


def test_split_ttl_extracts_leading_duration():
    from agora.vote import split_ttl
    assert split_ttl("2h pick a db | a | b") == (7200.0, "pick a db | a | b")
    assert split_ttl("45s go | a | b") == (45.0, "go | a | b")
    assert split_ttl("pick a db | a | b") == (None, "pick a db | a | b")
    assert split_ttl("30m") == (None, "30m")            # alone: it IS the topic
    assert split_ttl("99x topic | a | b")[0] is None    # bad unit: topic text


def test_due_detects_deadline_and_full_turnout():
    from agora.vote import VoteChair, vote_info
    info = vote_info(_vote_msg(), "commons")
    info["closes_at"] = 1000.0
    members = ["laurent", "gateway", "memory"]
    assert VoteChair.due(info, {}, members, now=1000.1) == "deadline reached"
    assert VoteChair.due(info, {}, members, now=999.0) is None
    full = {"gateway": [0], "memory": [1]}       # everyone except the chair
    assert VoteChair.due(info, full, members, now=1.0) == "every member voted"
    # Unknown membership must never trigger 'complete' — only the deadline
    # can close a vote whose completeness cannot be verified.
    assert VoteChair.due(info, full, [], now=1.0) is None


def test_watcher_autopublishes_on_deadline():
    """The chair's background watcher releases the vote the moment its
    blindness protects nothing anymore — no manual /tally close needed."""
    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    vote = _vote_msg()
    dm_pages = {"dm:laurent--memory": [
        _dm("dm:laurent--memory", "memory", 8, f"vote {TAG}: sqlite")]}
    out = _wire(app, vote, [], dm_pages, MEMBERS)
    posts = []

    async def post(channel, body, **kw):
        posts.append((channel, body, kw))
        return Message(id="01HRESULT", channel="commons", seq=740,
                       sender="laurent", body=body, status=Status.resolved)
    app.client.post = post

    app.votes.register(vote, "commons")
    app.votes.open[vote.id]["closes_at"] = time.time() - 1   # already due
    asyncio.run(app.votes.check_due())
    channel, body, kw = posts[0]
    assert kw["status"] == Status.resolved and kw["reply_to"] == vote.id
    assert "deadline reached" in body
    assert vote.id not in app.votes.open                     # forgotten
    assert any("deadline reached" in line and "#740" in line for line in out)


def test_watcher_autopublishes_on_full_turnout():
    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    vote = _vote_msg()                                       # no deadline
    dm_pages = {
        f"dm:{a}--laurent" if a < "laurent" else f"dm:laurent--{a}": [
            _dm("dm:x", a, i + 1, f"vote {TAG}: {1 + i % 3}")]
        for i, a in enumerate(["observer", "gateway", "memory",
                               "uic", "flow"])}
    out = _wire(app, vote, [], dm_pages, MEMBERS)
    posts = []

    async def post(channel, body, **kw):
        posts.append((channel, body, kw))
        return Message(id="01HRESULT", channel="commons", seq=741,
                       sender="laurent", body=body, status=Status.resolved)
    app.client.post = post

    app.votes.register(vote, "commons")
    asyncio.run(app.votes.check_due())
    assert posts and "every member voted" in posts[0][1]
    assert "turnout 5/6" in posts[0][1]
    assert vote.id not in app.votes.open


def test_watcher_drops_votes_closed_elsewhere():
    """A result already in the transcript (manual close, another session)
    unregisters the vote without posting a duplicate."""
    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    vote = _vote_msg()
    result = _reply("laurent", 740, "VOTE RESULT — pick a db",
                    data={"vote_result": {"ballots": {}, "total_members": 6}})
    out = _wire(app, vote, [result], {}, MEMBERS)
    posts = []

    async def post(channel, body, **kw):
        posts.append((channel, body, kw))
    app.client.post = post

    app.votes.register(vote, "commons")
    app.votes.open[vote.id]["closes_at"] = time.time() - 1
    asyncio.run(app.votes.check_due())
    assert posts == [] and vote.id not in app.votes.open and out == []


def test_recover_relearns_open_votes_after_restart():
    """A chat restart must not orphan a running vote: recovery re-registers
    my open votes (and skips ones whose result is already published)."""
    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    open_vote = _vote_msg()
    closed_vote = Message(id="01HVOTEOLD", channel="commons", seq=700,
                          sender="laurent", title="VOTE: old",
                          body="…", status=Status.open,
                          data={"vote": {"topic": "old", "options": OPTS,
                                         "tag": "v-old111", "ballots": "dm"}})
    closed_result = Message(id="01HDONE", channel="commons", seq=705,
                            sender="laurent", body="…", reply_to="01HVOTEOLD",
                            data={"vote_result": {"ballots": {},
                                                  "total_members": 6}})
    foreign_vote = Message(id="01HNOTMINE", channel="commons", seq=710,
                           sender="uic", title="VOTE: theirs", body="…",
                           data={"vote": {"topic": "t", "options": OPTS,
                                          "tag": "v-uic222"}})

    async def list_channels():
        return [{"name": "commons", "member": True},
                {"name": "dm:laurent--memory", "member": True},
                {"name": "spectator", "member": False}]

    async def history(channel, since=0, limit=200):
        if channel == "commons" and since == 0:
            return [closed_vote, closed_result, foreign_vote, open_vote]
        return []
    app.client.list_channels = list_channels
    app.client.history = history

    asyncio.run(app.votes.recover())
    assert set(app.votes.open) == {open_vote.id}


def test_chair_tally_publishes_a_finished_vote_on_sight():
    """/tally by the chair on a vote past its deadline must not show a stale
    'still running' view — the finished vote publishes right there."""
    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    vote = _vote_msg(closes_at=time.time() - 10)             # expired
    dm_pages = {"dm:laurent--memory": [
        _dm("dm:laurent--memory", "memory", 8, f"vote {TAG}: postgres")]}
    out = _wire(app, vote, [], dm_pages, MEMBERS)
    posts = []

    async def post(channel, body, **kw):
        posts.append((channel, body, kw))
        return Message(id="01HRESULT", channel="commons", seq=742,
                       sender="laurent", body=body, status=Status.resolved)
    app.client.post = post

    asyncio.run(app.cmd_tally("731"))
    assert posts and "deadline reached" in posts[0][1]
    text = "\n".join(out)
    assert "closed — published as #742" in text


def test_build_vote_post_is_the_shared_construction_path():
    """Chat /vote and MCP open_vote must produce the identical contract —
    one builder, no drift."""
    from agora.vote import build_vote_post
    payload = build_vote_post("uic", "pick a db", ["sqlite", "sqlite.", "postgres"],
                              ttl=600)
    spec = payload["data"]["vote"]
    assert payload["title"] == "VOTE: pick a db" and payload["status"] == "open"
    assert spec["options"] == ["sqlite", "postgres"]      # deduped
    assert spec["ballots"] == "dm" and spec["tag"].startswith("v-")
    assert abs(spec["closes_at"] - (time.time() + 600)) < 5
    assert f"vote {spec['tag']}:" in payload["body"]
    assert "DM your ballot to uic" in payload["body"]
    assert build_vote_post("uic", "topic", ["only-one"]) is None
    assert build_vote_post("uic", "  ", ["a", "b"]) is None


def test_watch_votes_recovers_then_ticks_and_rerecovers():
    """The chair-duty loop: one recovery up front, due-checks every tick,
    periodic re-recovery to adopt votes opened from other surfaces."""
    from agora.vote import watch_votes

    calls = {"recover": 0, "check": 0}

    class StubChair:
        async def recover(self):
            calls["recover"] += 1

        async def check_due(self):
            calls["check"] += 1

    ticks = {"n": 0}

    def closing():
        ticks["n"] += 1
        return ticks["n"] > 4                 # a few ticks, then stop

    asyncio.run(watch_votes(StubChair(), interval=0.001, recover_every=0.0,
                            closing=closing))
    assert calls["recover"] >= 2              # startup + at least one re-scan
    assert calls["check"] >= 3


def test_vote_operation_honors_secrecy_and_publishes_when_due():
    """The MCP backend: blind for voters, counts for the chair, publish on
    close/deadline — same semantics as the chat surface."""
    from agora.vote import vote_operation

    vote = _vote_msg(sender="laurent")

    class FakeClient:
        def __init__(self, me):
            self.me = me
            self.posted = []

        async def whoami(self):
            return {"id": self.me}

        async def read(self, channel, mid):
            return [vote]

        async def history(self, channel, since=0, limit=200):
            if channel.startswith("dm:") and since == 0:
                return [_dm(channel, "memory", 8, f"vote {TAG}: sqlite")]
            return []

        async def list_channels(self):
            return [{"name": "dm:laurent--memory", "member": True}]

        async def channel_info(self, channel):
            return {"members": [{"agent_id": a} for a in
                                ["laurent", "memory", "flow"]]}

        async def post(self, channel, body, **kw):
            self.posted.append((channel, body, kw))
            return Message(id="01HRESULT", channel=channel, seq=750,
                           sender="laurent", body=body, status=Status.resolved)

    # A non-chair voter gets the blind notice, and cannot close.
    voter = FakeClient("memory")
    state = asyncio.run(vote_operation(voter, "memory", "commons", vote.id))
    assert state["blind"] is True and "counts" not in state
    refused = asyncio.run(vote_operation(voter, "memory", "commons", vote.id,
                                         close=True))
    assert refused["ok"] is False and refused["error"] == 403

    # The chair sees counts and who is waiting.
    chair = FakeClient("laurent")
    state = asyncio.run(vote_operation(chair, "laurent", "commons", vote.id))
    assert state["closed"] is False
    assert state["counts"] == {"sqlite": 1, "postgres": 0, "flat files": 0}
    assert state["waiting"] == ["flow"]

    # Closing publishes and reports the roll call.
    done = asyncio.run(vote_operation(chair, "laurent", "commons", vote.id,
                                      close=True))
    assert done["closed"] is True and done["reason"] == "closed by the chair"
    assert done["ballots"] == {"memory": [0]}
    assert chair.posted and "VOTE RESULT" in chair.posted[0][1]


def test_cmd_tally_rejects_non_vote_messages():
    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    plain = Message(id="01HPLAIN", channel="commons", seq=5,
                    sender="hub", body="hello")

    async def history(channel, since=0, limit=200):
        return [plain]

    async def read(channel, mid):
        return [plain]
    app.client.history = history
    app.client.read = read
    out: list[str] = []
    app._print = lambda text="": out.append(text)

    asyncio.run(app.cmd_tally("5"))
    assert any("not a vote" in line for line in out)
