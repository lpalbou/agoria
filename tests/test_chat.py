"""Chat REPL helpers + the channel-stats surface it relies on.

The REPL's interactive loop is exercised manually; what must not regress
mechanically: line parsing (say vs command vs escaped slash), title
derivation (the triage headline every agent reads), the room directory
rendering, and the hub's channel stats that feed it.
"""

import time

from fastapi.testclient import TestClient

from agora.chat import channel_table, derive_title, fmt_age, parse_line
from agora.hub.app import create_app

ADMIN_KEY = "test-admin"


def register(client: TestClient, agent_id: str) -> dict[str, str]:
    r = client.post("/agents", json={"id": agent_id},
                    headers={"Authorization": f"Bearer {ADMIN_KEY}"})
    return {"Authorization": f"Bearer {r.json()['api_key']}"}


# -- parse_line ---------------------------------------------------------------

def test_plain_text_is_say():
    assert parse_line("hello everyone") == ("say", "hello everyone")


def test_slash_command_with_argument():
    assert parse_line("/switch entity-society") == ("switch", "entity-society")


def test_command_is_case_insensitive_and_bare_slash_is_help():
    assert parse_line("/WHO")[0] == "who"
    assert parse_line("/")[0] == "help"


def test_double_slash_escapes_a_literal_slash_message():
    assert parse_line("//etc/hosts is fine") == ("say", "/etc/hosts is fine")


# -- derive_title --------------------------------------------------------------

def test_title_is_first_line_collapsed():
    assert derive_title("fix the seam\nlong details follow") == "fix the seam"
    assert derive_title("  spaced   out   words  ") == "spaced out words"


def test_title_truncates_at_word_boundary():
    text = "word " * 40
    title = derive_title(text)
    assert len(title) <= 81 and title.endswith("…") and not title[:-1].endswith(" wor")


# -- fmt_age -------------------------------------------------------------------

def test_fmt_age_bands():
    assert fmt_age(None) == "-"
    assert fmt_age(30) == "now"
    assert fmt_age(300) == "5m"
    assert fmt_age(7200) == "2h"
    assert fmt_age(200000) == "2d"


# -- channel_table ---------------------------------------------------------------

def test_channel_table_marks_current_and_unjoined():
    now = time.time()
    channels = [
        {"name": "design", "private": True, "member": True,
         "member_count": 3, "last_seq": 42, "last_at": now - 120},
        {"name": "commons", "private": False, "member": False,
         "member_count": 9, "last_seq": 118, "last_at": now - 7200},
    ]
    table = channel_table(channels, {"design": 5}, current="design", now=now)
    design_row = next(l for l in table.splitlines() if "design" in l)
    commons_row = next(l for l in table.splitlines() if "commons" in l)
    assert design_row.strip().startswith(">") and " 5" in design_row
    assert commons_row.strip().startswith("·") and "public" in commons_row


def test_channel_table_separates_dms_with_peer_names():
    from agora.chat_render import Style, channel_table as render_table
    now = time.time()
    channels = [
        {"name": "commons", "private": False, "member": True,
         "member_count": 9, "last_seq": 118, "last_at": now - 60},
        {"name": "dm:laurent--runtime", "private": True, "member": True,
         "member_count": 2, "last_seq": 4, "last_at": now - 30},
    ]
    table = render_table(Style(False), channels, {}, current=None, me="laurent")
    assert "── direct messages ──" in table
    assert "@runtime" in table                      # peer, not the raw dm slug
    assert "dm:laurent--runtime" not in table.split("direct messages")[1].splitlines()[1]


# -- message_block (the one layout for history/live/read) -----------------------

def test_message_block_caps_long_bodies_with_read_hint():
    from agora.chat_render import Style, message_block
    body = "\n".join(f"line {i} " + "word " * 30 for i in range(40))
    block = message_block(Style(False), sender="runtime", seq=42, status="open",
                          created_at=time.time(), title="big report", body=body)
    lines = block.splitlines()
    assert len(lines) < 20                      # capped, not a wall
    assert "/read 42" in lines[-1] and "more line" in lines[-1]
    assert "big report" in block                # title surfaced
    assert "#42" in block and "open" in block


def test_message_block_marks_dms_and_foreign_channels():
    from agora.chat_render import Style, message_block
    s = Style(False)
    dm = message_block(s, sender="runtime", seq=3, status="fyi",
                       created_at=time.time(), body="hi",
                       me="laurent", channel="dm:laurent--runtime")
    assert dm.splitlines()[1].startswith("DM ")
    assert "#3 " in dm                  # home room: the bare seq suffices
    other = message_block(s, sender="memory", seq=9, status="reply",
                          created_at=time.time(), body="x",
                          me="laurent", channel="entity-society",
                          show_channel=True)
    assert "#9@entity-society" in other  # self-locating, /read-able as printed


def test_message_block_qualifies_refs_outside_their_room():
    """Field bug: seqs are per-channel, but a DM arriving while you watch
    another room rendered '⋯ N more — /read 7' — and /read 7 fetched the
    CURRENT room's unrelated #7. Every hint on a block rendered away from
    its home channel must print a ref that resolves to that very message.
    DMs teach the SHORT form (PEER:SEQ — one peer per DM, so 'agency:7'
    beats '7@dm:agency--laurent'); plain channels keep SEQ@CHANNEL."""
    from agora.chat_render import Style, message_block
    s = Style(False)
    body = "\n".join(f"line {i}" for i in range(12))
    dm = message_block(s, sender="agency", seq=7, status="fyi",
                       created_at=time.time(), body=body,
                       me="laurent", channel="dm:agency--laurent",
                       show_channel=True)
    assert "#agency:7" in dm
    assert "/read agency:7" in dm.splitlines()[-1]
    # The body_bytes hint (body not inlined) must qualify identically.
    stub = message_block(s, sender="agency", seq=7, status="fyi",
                         created_at=time.time(), body_bytes=2048,
                         me="laurent", channel="dm:agency--laurent",
                         show_channel=True)
    assert "/read agency:7" in stub
    # A non-DM foreign room still hints the classic qualified form.
    room = message_block(s, sender="core", seq=9, status="fyi",
                         created_at=time.time(), body_bytes=2048,
                         me="laurent", channel="design", show_channel=True)
    assert "/read 9@design" in room


def test_file_event_line_shows_edit_size():
    from agora.chat_render import Style, file_event_line
    line = file_event_line(Style(False), sender="observer",
                           title="fs:put plans/plan.md", channel="commons",
                           current="commons",
                           data={"version": 2, "size_bytes": 8280})
    assert "observer" in line and "put plans/plan.md" in line
    assert "v2" in line and "8280B" in line and "/fs plans/plan.md" in line
    # Degrades without data (live envelopes may not inline it).
    bare = file_event_line(Style(False), sender="core", title="fs:put x.md",
                           channel="commons", current="commons")
    assert "put x.md" in bare and "v" + "None" not in bare


def test_file_history_table_shows_created_then_deltas():
    from agora.chat_render import Style, file_history_table
    events = [
        {"sender": "gateway", "created_at": time.time(),
         "data": {"op": "put", "version": 1, "size_bytes": 8091}},
        {"sender": "observer", "created_at": time.time(),
         "data": {"op": "put", "version": 2, "size_bytes": 8280}},
    ]
    table = file_history_table(Style(False), "plans/plan.md", events)
    lines = table.splitlines()
    assert "created" in lines[1] and "8091B" in lines[1]
    assert "+189B" in lines[2] and "observer" in lines[2]


def test_ask_lines_render_state_marks_and_reply_hint():
    """Asks are the machine-tracked questions the 'asks N/M' badge counts —
    previously invisible in chat (field finding: the operator could not tell
    WHAT #727 actually asked). ○ = pending, ✓ = answered, · = state unknown;
    the hint prints the exact /reply REF:ID that answers the first open ask."""
    from agora.chat_render import Style, ask_lines
    s = Style(False)
    asks = [{"id": "1", "text": "publish the contract types"},
            {"id": "2", "text": "fold all-cleared to ABSENT", "assignee": "gateway"}]
    known = ask_lines(s, asks, ["2"], "727", 100)
    assert known[0].startswith("  ✓ [1]")
    assert known[1].startswith("  ○ [2]") and "→ gateway" in known[1]
    assert "/reply 727:2 TEXT" in known[-1]          # first PENDING ask, not #1
    unknown = ask_lines(s, asks, None, "7@dm:agency--laurent", 100)
    assert unknown[0].startswith("  · [1]")
    # The ask id rides the LOCAL part of a qualified ref (channels contain ':').
    assert "/reply 7:1@dm:agency--laurent TEXT" in unknown[-1]
    done = ask_lines(s, asks, [], "727", 100)
    assert all("✓" in line for line in done)
    assert not any("/reply" in line for line in done)  # nothing left to answer


def test_asks_from_is_tolerant_of_malformed_payloads():
    from agora.chat_render import asks_from
    assert asks_from(None) == []
    assert asks_from({"asks": "not-a-list"}) == []
    assert asks_from({"asks": [{"no_id": True}, "junk", {"id": "1", "text": "t"}]}) \
        == [{"id": "1", "text": "t"}]


def test_message_block_lists_asks_below_the_body():
    from agora.chat_render import Style, message_block
    block = message_block(Style(False), sender="uic", seq=727, status="open",
                          created_at=time.time(), title="TASK COMPLETE",
                          body="prose that buries the questions",
                          asks=[{"id": "1", "text": "the contract"},
                                {"id": "2", "text": "fold to ABSENT"}],
                          pending_asks=["1", "2"])
    assert "○ [1] the contract" in block and "○ [2] fold to ABSENT" in block
    assert "/reply 727:1 TEXT" in block


def test_switch_expands_bare_dm_peer():
    """`/switch dm:agency` reaches dm:agency--laurent: your own handle in a
    DM ref is noise — the peer IS the address (operator, 2026-07-14). Full
    names and ordinary channels pass through untouched."""
    from agora.chat import ChatApp

    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    assert app._expand_dm("dm:agency") == "dm:agency--laurent"
    assert app._expand_dm("dm:zeta") == "dm:laurent--zeta"      # sorted order
    assert app._expand_dm("dm:agency--laurent") == "dm:agency--laurent"
    assert app._expand_dm("commons") == "commons"
    assert app._expand_dm("dm:laurent") == "dm:laurent"          # self: unchanged


def test_wrap_body_renders_markdown_tables_aligned():
    """Operator finding (2026-07-14): agents' status tables arrived as
    wrapped pipe soup. The chat surface renders markdown — pipe tables come
    out column-aligned within the terminal width, cells never torn across
    lines by naive wrapping."""
    from agora.chat_render import wrap_body

    body = ("DONE (last 40 min)\n"
            "| # | What | Proof |\n"
            "|---|---|---|\n"
            "| 1 | :8080 stack bounced, console :3003 relaunched | all healthy |\n"
            "| 2 | max_iterations=20 ruling relayed + stored | commons 2013 |\n")
    visible, hidden = wrap_body(body, width=100, max_lines=None)
    assert hidden == 0
    rows = [l for l in visible if l.strip().startswith("|")]
    assert len(rows) >= 4                       # header + rule + 2 data rows
    # aligned: every table row has identical visible width
    assert len({len(r.rstrip()) for r in rows}) == 1
    # a cell's content stays inside its row (no torn 'all healthy' remnant line)
    assert not any(l.strip() == "healthy |" for l in visible)

    # narrow terminal: the table still renders as a table (cells wrap inside
    # their columns instead of the line breaking mid-pipe)
    narrow, _ = wrap_body(body, width=56, max_lines=None)
    nrows = [l for l in narrow if l.strip().startswith("|")]
    assert len({len(r.rstrip()) for r in nrows}) == 1
    assert len(nrows) > 4                       # some cells wrapped to 2 lines


def test_wrap_body_preserves_paragraphs_and_counts_hidden():
    from agora.chat_render import wrap_body
    visible, hidden = wrap_body("a\n\nb", width=80, max_lines=10)
    assert [v.strip() for v in visible] == ["a", "", "b"] and hidden == 0
    visible, hidden = wrap_body("\n".join(str(i) for i in range(30)),
                                width=80, max_lines=10)
    assert len(visible) == 10 and hidden == 20


def test_wrap_body_uncapped_with_max_lines_none():
    from agora.chat_render import wrap_body
    visible, hidden = wrap_body("\n".join(str(i) for i in range(30)),
                                width=80, max_lines=None)
    assert len(visible) == 30 and hidden == 0


def test_read_command_renders_the_full_body():
    """Field bug: /read rendered through the same capped preview layout as
    live traffic, so 'show me the whole message' printed the identical
    truncated block — ending in a '/read SEQ' hint pointing at itself.
    A deliberate read must show every line and carry no truncation hint."""
    import asyncio

    from agora.chat import ChatApp
    from agora.models import Message

    app = ChatApp("http://127.0.0.1:1", "k", "tester")
    app.current = "commons"
    body = "\n".join(f"line {i}" for i in range(40))
    msg = Message(id="01HREADFULL", channel="commons", seq=662,
                  sender="agent", title="big report", body=body)

    async def fake_read(channel, mid):
        assert (channel, mid) == ("commons", "01HREADFULL")
        return [msg]
    app.client.read = fake_read
    out: list[str] = []
    app._print = lambda text="": out.append(text)

    asyncio.run(app.cmd_read("01HREADFULL"))
    text = "\n".join(out)
    assert "line 0" in text and "line 39" in text   # every line, first to last
    assert "more line" not in text                  # no self-referential hint


# -- qualified refs: seqs are per-channel, hints must resolve from any room -------

def _qualified_ref_app():
    """A ChatApp in 'commons' with a stubbed client: one DM channel whose
    seq 7 exists, and a fake read/post that records the channel actually hit."""
    from agora.chat import ChatApp
    from agora.models import Message

    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    dm_chan = "dm:agency--laurent"
    msg = Message(id="01HDMSEQ7", channel=dm_chan, seq=7,
                  sender="agency", title="status", body="the long report")

    async def list_channels():
        return [{"name": "commons", "member": True},
                {"name": dm_chan, "member": True},
                {"name": "spectator", "member": False}]

    async def history(channel, since=0, limit=200):
        # The regression this guards: 'commons' also HAS a seq 7 — a
        # qualified ref must never touch the current room.
        assert channel == dm_chan, f"resolved in the wrong channel: {channel}"
        assert (since, limit) == (6, 1)
        return [msg]

    calls = {"read": [], "post": []}

    async def read(channel, mid):
        calls["read"].append((channel, mid))
        return [msg]

    async def post(channel, body, **kw):
        calls["post"].append((channel, kw.get("reply_to"), body))
        return msg

    app.client.list_channels = list_channels
    app.client.history = history
    app.client.read = read
    app.client.post = post
    out: list[str] = []
    app._print = lambda text="": out.append(text)
    return app, calls, out


def test_read_accepts_qualified_refs_and_peer_sugar():
    """'/read 7@dm:agency--laurent' (the printed hint) and '/read 7@agency'
    (peer sugar) both read seq 7 OF THE DM CHANNEL — not the current room's
    #7, which is what the bare '/read 7' hint used to fetch (field bug)."""
    import asyncio

    app, calls, out = _qualified_ref_app()
    asyncio.run(app.cmd_read("7@dm:agency--laurent"))
    asyncio.run(app.cmd_read("7@agency"))
    assert calls["read"] == [("dm:agency--laurent", "01HDMSEQ7")] * 2
    # The rendered block self-locates; DMs teach the short PEER:SEQ ref.
    assert any("#agency:7" in line for line in out)


def test_read_accepts_leading_peer_form_for_dms():
    """'/read agency:7' — a DM has ONE peer, so PEER:SEQ is the natural
    handle (laurent 2026-07-13: '3@dm:artemis--laurent' is too much typing).
    Must resolve identically to '7@agency', and must NOT shadow the classic
    'SEQ:ASK' form ('727:1' keeps meaning seq 727 ask 1 in this room)."""
    import asyncio

    app, calls, out = _qualified_ref_app()
    asyncio.run(app.cmd_read("agency:7"))
    assert calls["read"] == [("dm:agency--laurent", "01HDMSEQ7")]


def test_reply_leading_peer_form_with_ask_suffix():
    """'/reply agency:7:1 TEXT' — peer form composes with the ask suffix:
    channel = the DM, seq 7, answering ask id 1."""
    import asyncio

    app, calls, out = _qualified_ref_app()
    asyncio.run(app.cmd_reply("agency:7:1 confirmed, shipping"))
    assert calls["post"] == [("dm:agency--laurent", "01HDMSEQ7",
                              "confirmed, shipping")]


def test_numeric_and_unknown_heads_fall_through_to_classic_parse():
    """'727:1' (SEQ:ASK) must never be rewritten to a peer lookup, and an
    unknown non-numeric head ('ghost:3') falls through to the classic parse
    (ULID 'ghost' + ask '3') rather than resolving to a wrong channel."""
    import asyncio

    app, calls, out = _qualified_ref_app()

    async def history(channel, since=0, limit=200):
        # classic parse in the CURRENT room: seq 727 not found there
        assert channel == "commons"
        return []
    app.client.history = history
    asyncio.run(app.cmd_read("727:1"))
    assert calls["read"] == []                       # not found in commons
    assert any("no message 727" in line for line in out)

    calls["read"].clear()
    asyncio.run(app.cmd_read("ghost:3"))             # unknown peer: ULID path
    assert calls["read"] == [("commons", "ghost")]


def test_reply_qualified_ref_posts_into_that_channel():
    """A reply through a qualified ref must land in the referenced message's
    channel (a bare-seq reply into the wrong room is the worst variant of
    the ambiguity: it posts content somewhere the sender never intended)."""
    import asyncio

    app, calls, out = _qualified_ref_app()
    asyncio.run(app.cmd_reply("7@agency on it — deploying now"))
    assert calls["post"] == [("dm:agency--laurent", "01HDMSEQ7",
                              "on it — deploying now")]
    assert any("reply sent to dm:agency--laurent" in line for line in out)


def test_moderation_arg_parser():
    """/kick and /ban share one grammar: AGENT [--time X] [--target T]
    [reason...]. 'mn' is accepted for minutes; a missing --time returns
    None so each command applies its own default (kick 15m, ban forever)."""
    from agora.chat import ChatApp

    parse = ChatApp._parse_moderation
    assert parse("bob") == ("bob", None, "channel", "")
    assert parse("bob --time 30mn spamming") == ("bob", 1800.0, "channel", "spamming")
    assert parse("bob --time=2h") == ("bob", 7200.0, "channel", "")
    assert parse("bob --target hub runaway loop") == ("bob", None, "hub", "runaway loop")
    assert parse("bob be nice next time") == ("bob", None, "channel", "be nice next time")
    assert isinstance(parse(""), str)                    # usage error
    assert isinstance(parse("--time 5m"), str)           # agent missing
    assert isinstance(parse("bob --time nonsense"), str)  # bad duration
    assert isinstance(parse("bob --target moon"), str)   # bad target


def test_locate_rejects_unknown_targets_and_missing_room():
    """Bad '@' targets name the problem; a bare seq with no current room
    points at the qualified form instead of failing silently."""
    import asyncio

    app, calls, out = _qualified_ref_app()
    asyncio.run(app.cmd_read("7@nowhere"))
    assert calls["read"] == [] and any("unknown channel" in l for l in out)
    app.current = None
    out.clear()
    asyncio.run(app.cmd_read("7"))
    assert calls["read"] == [] and any("no current channel" in l for l in out)


def test_reply_ask_syntax_attaches_answers():
    """'/reply 727:1 TEXT' formally answers ask 1 (the badge counter moves);
    '727:1,2' answers both. A plain '/reply 727 TEXT' keeps answers off —
    same visible reply, no discharge (that asymmetry was invisible before)."""
    import asyncio

    from agora.chat import ChatApp
    from agora.models import Message

    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    msg = Message(id="01HASK727", channel="commons", seq=727, sender="uic",
                  title="TASK COMPLETE", body="…",
                  data={"asks": [{"id": "1", "text": "a"}, {"id": "2", "text": "b"}]})

    async def history(channel, since=0, limit=200):
        assert channel == "commons"
        return [msg]

    posts = []

    async def post(channel, body, **kw):
        posts.append((channel, kw.get("reply_to"), kw.get("answers")))
        return msg

    app.client.history = history
    app.client.post = post
    out: list[str] = []
    app._print = lambda text="": out.append(text)

    asyncio.run(app.cmd_reply("727:1 the contract is in ui-kit/src"))
    asyncio.run(app.cmd_reply("727:1,2 both folded"))
    asyncio.run(app.cmd_reply("727 just a comment"))
    assert posts == [("commons", "01HASK727", ["1"]),
                     ("commons", "01HASK727", ["1", "2"]),
                     ("commons", "01HASK727", None)]
    assert any("answers ask [1]" in line for line in out)
    assert any("answers ask [1, 2]" in line for line in out)


def test_ask_at_mention_names_the_seat(monkeypatch):
    """'/ask @agency TEXT' is the direct ask-ONE-agent form (operator
    request, 2026-07-14): the mention becomes the message `to` AND the
    ask's per-ask `to`, so the named seat is flagged, pinned, and owes the
    answer; a bare /ask stays a room-open question."""
    import asyncio

    from agora.chat import ChatApp
    from agora.models import Message, Status

    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    posts = []

    async def post(channel, body, **kw):
        posts.append((channel, body, kw.get("to"), kw.get("asks"),
                      kw.get("status")))
        return Message(id="01X", channel=channel, seq=1, sender="laurent",
                       title="t", body=body)

    app.client.post = post
    out: list[str] = []
    app._print = lambda text="": out.append(text)

    asyncio.run(app.cmd_post("@agency status table please?",
                             status=Status.open))
    asyncio.run(app.cmd_post("@code @uic split this", status=Status.open))
    asyncio.run(app.cmd_post("anyone up?", status=Status.open))

    ch, body, to, asks, _ = posts[0]
    assert body == "status table please?" and to == ["agency"]
    assert asks[0]["to"] == ["agency"]
    assert posts[1][2] == ["code", "uic"] and posts[1][3][0]["to"] == ["code", "uic"]
    assert posts[2][2] is None and "to" not in posts[2][3][0]
    assert any("owed by agency" in line for line in out)


def test_read_marks_ask_state_from_digest_and_tolerates_ask_suffix():
    """A deliberate read fetches the digest to mark which asks are still
    pending (discharge lives hub-side, in the replies); a question absent
    from the open list reads as fully answered. '/read 727:1' reads 727."""
    import asyncio

    from agora.chat import ChatApp
    from agora.models import Message

    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    msg = Message(id="01HASK727", channel="commons", seq=727, sender="uic",
                  title="TASK COMPLETE", body="…",
                  data={"asks": [{"id": "1", "text": "a"}, {"id": "2", "text": "b"}]})

    async def history(channel, since=0, limit=200):
        return [msg]

    async def read(channel, mid):
        assert (channel, mid) == ("commons", "01HASK727")
        return [msg]

    digest = {"open_questions": [
        {"seq": 727, "pending_asks": [{"id": "2", "text": "b"}]}]}

    class FakeHTTP:
        async def get(self, path):
            assert path == "/channels/commons/digest"
            return digest

    app.client.history = history
    app.client.read = read
    app.client._http = FakeHTTP()
    app.client._json = lambda resp: resp
    out: list[str] = []
    app._print = lambda text="": out.append(text)

    asyncio.run(app.cmd_read("727:1"))          # ask suffix tolerated
    text = "\n".join(out)
    assert "✓ [1]" in text and "○ [2]" in text  # 1 answered, 2 still owed
    out.clear()
    digest["open_questions"] = []               # discharged: left the open list
    asyncio.run(app.cmd_read("727"))
    text = "\n".join(out)
    assert "✓ [1]" in text and "✓ [2]" in text and "○" not in text


def test_critical_banner_hints_qualified_ref_from_other_rooms():
    """A critical pins until /read — from another room the banner must hint
    the ref that actually un-pins it, not the current room's same-numbered
    message."""
    import time as _time

    from agora.chat import ChatApp
    from agora.chat_render import Style
    from agora.models import Envelope, Kind, Status, Urgency

    app = ChatApp("http://127.0.0.1:1", "k", "laurent")
    app.current = "commons"
    app.style = Style(False)
    out: list[str] = []
    app._print = lambda text="": out.append(text)
    env = Envelope(id="01HCRIT", channel="ops", seq=3, sender="boss",
                   kind=Kind.message, status=Status.fyi,
                   urgency=Urgency.interrupt, effective_urgency=Urgency.interrupt,
                   critical=True, title="halt", body="stop the rollout",
                   body_bytes=16, created_at=_time.time())
    app.show_envelope(env)
    text = "\n".join(out)
    assert "/read 3@ops" in text
    # Same critical in its home room keeps the bare seq.
    app.current = "ops"
    out.clear()
    app.show_envelope(env)
    assert "/read 3" in "\n".join(out) and "3@ops" not in "\n".join(out)


# -- Ctrl-C policy: one clears the line, two in a row quit ------------------------

def test_second_interrupt_window_logic():
    """Pure policy check with an injected clock: only a Ctrl-C following
    another within CTRL_C_QUIT_WINDOW counts as 'really quit'."""
    from agora.chat import CTRL_C_QUIT_WINDOW, ChatApp

    app = ChatApp("http://127.0.0.1:1", "k", "tester")
    assert not app._second_interrupt(now=100.0)              # first ever
    assert app._second_interrupt(now=100.0 + CTRL_C_QUIT_WINDOW - 0.1)
    app2 = ChatApp("http://127.0.0.1:1", "k", "tester")
    assert not app2._second_interrupt(now=100.0)
    assert not app2._second_interrupt(now=100.0 + CTRL_C_QUIT_WINDOW + 0.1)


def test_input_loop_clears_on_one_ctrl_c_and_quits_on_two():
    """Flow check through the real loop: the first KeyboardInterrupt prints
    the clear hint and keeps the loop alive; an immediate second one exits
    the loop without ever asking for input again."""
    import asyncio

    from agora.chat import ChatApp

    app = ChatApp("http://127.0.0.1:1", "k", "tester")
    out: list[str] = []
    app._print = lambda text="": out.append(text)
    prompts = {"count": 0}

    async def scripted(prompt: str) -> str:
        prompts["count"] += 1
        if prompts["count"] <= 2:
            raise KeyboardInterrupt     # two rapid Ctrl-C
        raise AssertionError("loop should have quit on the second Ctrl-C")
    app._make_prompt = lambda: scripted

    asyncio.run(app._input_loop())      # returns instead of raising
    assert prompts["count"] == 2
    assert any("Ctrl-C again" in line for line in out)


# -- dispatch: every /command in HELP must be wired ------------------------------

def test_every_help_command_is_dispatched():
    """The field bug this guards: /dm was documented in HELP and cmd_dm
    existed, but the dispatch table never registered it — users got
    'unknown command'. Every slash command HELP advertises must dispatch."""
    import asyncio
    import re

    from agora.chat import HELP, ChatApp

    app = ChatApp("http://127.0.0.1:1", "k", "tester")
    called = []
    # Stub every handler so dispatch resolves without I/O.
    for name in dir(app):
        if name.startswith("cmd_"):
            async def stub(*a, _n=name, **kw):
                called.append(_n)
            setattr(app, name, stub)

    commands = set(re.findall(r"^/([a-z]+)", HELP, re.MULTILINE))
    commands -= {"quit"}  # quit is handled before the table
    for cmd in sorted(commands):
        called.clear()
        keep_going = asyncio.run(app.dispatch(f"/{cmd} someargument here"))
        assert keep_going, f"/{cmd} unexpectedly quit"
        assert called, f"/{cmd} is in HELP but not dispatched"


# -- hub channel stats (the directory's data source) -----------------------------

def test_list_channels_carries_stats():
    app = create_app(db_path=":memory:", admin_key=ADMIN_KEY, rate_per_minute=600.0)
    client = TestClient(app)
    alice = register(client, "alice")
    bob = register(client, "bob")
    client.post("/channels", json={"name": "design"}, headers=alice)
    invite = client.post("/channels/design/invites", json={},
                         headers=alice).json()["invite_token"]
    client.post("/channels/design/join", json={"invite_token": invite}, headers=bob)
    for i in range(3):
        client.post("/channels/design/messages",
                    json={"body": f"m{i}", "title": f"m{i}"}, headers=alice)

    rows = client.get("/channels", headers=bob).json()
    design = next(r for r in rows if r["name"] == "design")
    assert design["member_count"] == 2
    # 3 posts + join system messages; head seq must match a fresh read.
    head = client.get("/channels/design/messages", headers=bob).json()[-1]["seq"]
    assert design["last_seq"] == head
    assert design["last_at"] is not None and design["last_at"] > 0
