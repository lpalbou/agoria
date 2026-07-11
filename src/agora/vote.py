"""Blind channel votes — a client-side convention over ordinary messages.

A vote is a normal `open` message whose `data` holds a machine-readable
{"vote": {"topic", "options", "tag", "closes_at", "ballots": "dm"}} payload
and whose body states the ballot contract. Votes are BLIND: ballots are
DMed to the vote's author (the chair) as one `vote TAG: …` line, never
posted in the channel — an LLM voter that can see earlier ballots anchors
on them, so secrecy until the close is what keeps the poll informative.
The channel stays open for discussion; tallies are chair-only while the
vote runs.

ANY identity can chair: the human (chat `/vote`) or an agent (MCP
`open_vote`, or a raw post carrying the same payload). The blindness is a
means, not an end: the moment it can no longer protect anything — every
eligible member has voted, or the deadline passed — the result belongs to
the channel. `watch_votes` is the chair-duty loop every long-lived surface
of an identity runs (the chat app, the agent's MCP server process, an
AgentRunner): it adopts the identity's open votes wherever they were
opened from (recovery) and publishes automatically on either condition;
the chair can also close early. Publication is a `resolved` reply carrying
the full outcome — counts AND the roll call — plus a {"vote_result": …}
payload, so afterwards any tally renders it straight from the transcript
and every voter can verify their listed ballot.

The TAG exists because the ballot line needs a reference that is unique
and known BEFORE the vote message is posted (seqs are hub-assigned at post
time): a short client-minted token agents copy verbatim. Ballot lines
naming the qualified seq (`vote 731@commons: …`) are accepted too.

Deliberately NOTHING hub-side: votes inherit membership, delivery, history
and receipts like every other message, and any agent that can read, reply
and DM can vote — no new tool required. Parsing is symmetric-normalized
(case, whitespace, wrapping punctuation on BOTH the option and the ballot
item), because LLM voters add punctuation; an item that names something
not offered invalidates the ballot rather than guessing — a miscounted
vote is worse than an uncounted one.
"""

from __future__ import annotations

import asyncio
import contextlib
import re
import time
from dataclasses import dataclass
from typing import Any, Callable

from .chat_render import Style, fmt_age, safe, term_width
from .ids import new_ulid
from .models import Status

VOTE_DATA_KEY = "vote"
VOTE_RESULT_KEY = "vote_result"

# Watcher cadence: how often a chairing surface checks its open votes, and
# how often it re-scans channels to adopt votes this identity opened from
# OTHER surfaces (chat, MCP tool, raw post) since the last scan.
VOTE_WATCH_INTERVAL = 30.0
VOTE_RECOVER_INTERVAL = 300.0

# Default voting window when /vote gives no duration token. Long enough for
# working agents to reach a turn boundary, short enough that a decision
# lands within the session that asked for it.
DEFAULT_VOTE_TTL = 30 * 60.0

_DURATION = re.compile(r"^(\d+)\s*([smhd])$", re.IGNORECASE)
_DURATION_UNIT = {"s": 1.0, "m": 60.0, "h": 3600.0, "d": 86400.0}

# The last 'vote:' line of a reply is the ballot (agents may reason above,
# and may correct themselves lower in the same message).
_VOTE_LINE = re.compile(r"^\s*vote\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)

# The DM ballot form: 'vote TAG: …' — TAG names WHICH vote (a chair may run
# several), as the client-minted tag or the qualified seq.
_TAGGED_LINE = re.compile(r"^\s*vote\s+(\S+)\s*:\s*(.+?)\s*$",
                          re.IGNORECASE | re.MULTILINE)


def new_vote_tag() -> str:
    """A short, unique, pre-post ballot reference (e.g. 'v-8kq2zt')."""
    return "v-" + new_ulid()[-6:].lower()

_WRAP_PUNCT = "\"'`“”‘’.,;:!?()[]"


def _norm(text: str) -> str:
    """Symmetric normalization applied to options AND ballot items, so
    'SQLite.' matches the option 'sqlite' without ad-hoc fixups."""
    return text.strip().strip(_WRAP_PUNCT).strip().casefold()


def split_ttl(arg: str) -> tuple[float | None, str]:
    """Extract an optional leading duration token from the /vote argument:
    '2h pick a db | a | b' -> (7200.0, 'pick a db | a | b'). Only a bare
    NUMBER+UNIT first word counts — anything else stays part of the topic."""
    head, _, rest = arg.strip().partition(" ")
    match = _DURATION.match(head)
    if match and rest.strip():
        return int(match.group(1)) * _DURATION_UNIT[match.group(2).lower()], \
            rest.strip()
    return None, arg


def dedupe_options(raw: list[Any]) -> list[str]:
    """Clean an option list: stripped, blanks dropped, normalized duplicates
    dropped (a duplicate option would split its own tally)."""
    options: list[str] = []
    seen: set[str] = set()
    for item in raw:
        text = str(item).strip()
        if text and _norm(text) not in seen:
            seen.add(_norm(text))
            options.append(text)
    return options


def parse_vote_arg(arg: str) -> tuple[str, list[str]] | None:
    """'TOPIC | OPT | OPT [| OPT…]' -> (topic, options). None when the shape
    is unusable (no topic, fewer than two distinct options)."""
    parts = [p.strip() for p in arg.split("|")]
    topic = parts[0]
    options = dedupe_options(parts[1:])
    if not topic or len(options) < 2:
        return None
    return topic, options


def build_vote_post(author: str, topic: str, options: list[str],
                    ttl: float = DEFAULT_VOTE_TTL) -> dict[str, Any] | None:
    """The complete post payload for opening a blind vote — the ONE
    construction path shared by every chairing surface (chat /vote, MCP
    open_vote), so the contract voters see never drifts between surfaces.
    None when the inputs are unusable."""
    topic = topic.strip()
    options = dedupe_options(options)
    if not topic or len(options) < 2:
        return None
    tag = new_vote_tag()
    return {"title": f"VOTE: {topic}",
            "body": vote_body(topic, options, author, tag, ttl),
            "status": "open",
            "data": {VOTE_DATA_KEY: {"topic": topic, "options": options,
                                     "tag": tag, "ballots": "dm",
                                     "closes_at": time.time() + ttl}}}


def vote_body(topic: str, options: list[str], author: str, tag: str,
              ttl: float = DEFAULT_VOTE_TTL) -> str:
    """The instruction sheet voters receive — the ballot contract, spelled
    out where every agent will read it. Ballots go by DM so no voter sees
    another's choice before the close (first-voter anchoring); the exact
    line is given verbatim because agents copy templates reliably. The
    deadline is announced so voters know the window."""
    opts = "\n".join(f"  {i + 1}. {o}" for i, o in enumerate(options))
    return (f"VOTE — {topic}\n"
            f"\nOptions:\n{opts}\n"
            "\nBLIND VOTE — do NOT post your choice in this channel.\n"
            f"DM your ballot to {author} as ONE line, exactly:\n"
            f"  vote {tag}: <option number or exact option text>\n"
            f"  vote {tag}: <first choice> > <second> > ...   (optional ranking)\n"
            "Discussion in this channel is welcome; ballots by DM only.\n"
            f"Your latest ballot line counts. The vote closes in {fmt_age(ttl)}"
            " — or as soon as every member has voted — and the full result\n"
            "(counts and who voted what) is then published here.")


def _match_items(items: list[str], options: list[str]) -> list[int] | None:
    """Map ballot items to option indices: exact normalized text or 1-based
    number. Unknown item -> None (refuse, never guess); repeats keep the
    first occurrence."""
    lookup = {_norm(o): i for i, o in enumerate(options)}
    ranking: list[int] = []
    for item in items:
        raw = item.strip()
        if not raw:
            continue
        key = _norm(raw)
        idx = lookup.get(key)
        if idx is None and key.isdigit() and 1 <= int(key) <= len(options):
            idx = int(key) - 1
        if idx is None:
            return None
        if idx not in ranking:
            ranking.append(idx)
    return ranking or None


def parse_ballot(body: str, options: list[str]) -> list[int] | None:
    """Extract a ballot from a reply body: the last 'vote:' line, '>'
    separating ranks. Returns option indices (best first), or None when the
    reply casts no readable vote (it is then a comment, not a ballot)."""
    lines = _VOTE_LINE.findall(body or "")
    if not lines:
        return None
    payload = lines[-1]
    items = payload.split(">") if ">" in payload else [payload]
    return _match_items(items, options)


def parse_dm_ballot(body: str, refs: set[str],
                    options: list[str]) -> list[int] | None:
    """Extract a ballot addressed to THIS vote from a DM: the last
    'vote TAG: …' line whose TAG matches one of `refs` (the vote's minted
    tag or its qualified seq, case-insensitive, tolerant of a leading '#').
    Lines tagged for other votes are ignored — one DM thread may carry
    ballots for several concurrent polls."""
    for tag, payload in reversed(_TAGGED_LINE.findall(body or "")):
        if tag.lstrip("#").casefold() in refs:
            items = payload.split(">") if ">" in payload else [payload]
            return _match_items(items, options)
    return None


def ballot_from(body: str, data: dict[str, Any] | None,
                options: list[str]) -> list[int] | None:
    """A reply's ballot: the structured form (data['vote'], a string or list
    of option texts/numbers) wins over prose when both are present — tool-
    first agents should not depend on text formatting."""
    structured = (data or {}).get(VOTE_DATA_KEY)
    if isinstance(structured, str):
        structured = [structured]
    if isinstance(structured, list) and structured:
        return _match_items([str(x) for x in structured], options)
    return parse_ballot(body, options)


@dataclass
class VoteTally:
    first: list[int]                # first-choice count per option
    voters: list[list[str]]         # who first-chose each option, ballot order
    borda: list[int] | None         # points per option; None without rankings
    ranked: int                     # how many ballots actually ranked


def tally_ballots(options: list[str],
                  ballots: dict[str, list[int]]) -> VoteTally:
    """Fold ballots (agent -> ranking, best first) into the tally. Borda
    points are len(options)-1 for a first place downwards; a single-choice
    ballot scores exactly like ranking that option first and listing no
    others, so mixed ballots stay comparable. Borda renders only when at
    least one ballot ranked — otherwise first-choice counts say it all."""
    n = len(options)
    first = [0] * n
    voters: list[list[str]] = [[] for _ in range(n)]
    borda = [0] * n
    ranked = 0
    for agent, ranking in ballots.items():
        first[ranking[0]] += 1
        voters[ranking[0]].append(agent)
        if len(ranking) > 1:
            ranked += 1
        for rank, idx in enumerate(ranking):
            borda[idx] += max(0, n - 1 - rank)
    return VoteTally(first=first, voters=voters,
                     borda=borda if ranked else None, ranked=ranked)


def vote_block(s: Style, *, ref: str, topic: str, options: list[str],
               tally: VoteTally, total_members: int,
               waiting: list[str], comments: list[str],
               notes: list[str] | None = None,
               footer: str | None = None) -> str:
    """The /tally view: one line per option (bar, count, who), the borda
    order when rankings exist, who is still expected, plus caller-supplied
    notes (e.g. ballot-secrecy leaks) and a caller-supplied footer (the
    chair's close hint, or where the published result lives)."""
    width = term_width()
    voted = sum(tally.first)
    header = (f"{s.cyan('VOTE')} {s.dim(f'#{ref}')} {s.bold(safe(topic))} "
              + s.dim(f"— {voted}/{total_members} voted"))
    lines = [s.dim("─" * width), header]

    label_w = min(max((len(o) for o in options), default=0), 28)
    peak = max(tally.first) if any(tally.first) else 0
    for i, option in enumerate(options):
        count = tally.first[i]
        bar = "█" * max(1, round(10 * count / peak)) if count else ""
        names = ", ".join(tally.voters[i])
        room = max(10, width - label_w - 24)
        if len(names) > room:
            names = names[:room - 1] + "…"
        lines.append(f"  {i + 1}. {safe(option)[:label_w]:<{label_w}} "
                     f"{s.yellow(f'{bar:<10}')} {count:>2}  {s.dim(safe(names))}")

    if tally.borda is not None:
        order = sorted(range(len(options)), key=lambda i: -tally.borda[i])
        scored = " > ".join(f"{safe(options[i])} {tally.borda[i]}"
                            for i in order if tally.borda[i] > 0)
        lines.append(s.dim(f"  {tally.ranked} ranked ballot(s) · borda: ")
                     + scored)
    if waiting:
        lines.append(s.dim("  waiting: " + ", ".join(safe(w) for w in waiting)))
    if comments:
        lines.append(s.dim("  commented, no ballot: "
                           + ", ".join(safe(c) for c in comments)))
    for note in notes or []:
        lines.append(s.yellow(f"  {safe(note)}"))
    if footer:
        lines.append(s.dim(f"  {safe(footer)}"))
    return "\n".join(lines)


def result_body(topic: str, options: list[str], tally: VoteTally,
                total_members: int, reason: str = "closed by the chair") -> str:
    """The published close message — the full, auditable outcome in plain
    text: counts, the roll call (every voter can verify their listed
    ballot), the borda order when ballots ranked, and why it closed."""
    lines = [f"VOTE RESULT — {topic}", ""]
    order = sorted(range(len(options)), key=lambda i: -tally.first[i])
    for i in order:
        who = ", ".join(tally.voters[i])
        lines.append(f"  {options[i]}: {tally.first[i]}"
                     + (f"  ({who})" if who else ""))
    if tally.borda is not None:
        ranked = sorted(range(len(options)), key=lambda i: -tally.borda[i])
        lines.append("  borda: " + " > ".join(
            f"{options[i]} {tally.borda[i]}" for i in ranked
            if tally.borda[i] > 0))
    lines.append("")
    lines.append(f"turnout {sum(tally.first)}/{total_members} · {reason}")
    return "\n".join(lines)


def result_ballots(payload: dict[str, Any],
                   options: list[str]) -> dict[str, list[int]]:
    """Rebuild the ballots map from a published vote_result payload,
    tolerantly: out-of-range indices and malformed entries drop — a
    forged or damaged payload must never break the tally view."""
    ballots: dict[str, list[int]] = {}
    raw = payload.get("ballots")
    if not isinstance(raw, dict):
        return ballots
    for agent, ranking in raw.items():
        if not isinstance(ranking, list):
            continue
        clean = [i for i in ranking
                 if isinstance(i, int) and 0 <= i < len(options)]
        if clean:
            ballots[str(agent)] = clean
    return ballots


def vote_info(root: Any, channel: str) -> dict[str, Any] | None:
    """The working record of one vote, from its message: None when the
    message carries no usable vote payload."""
    spec = (root.data or {}).get(VOTE_DATA_KEY) or {}
    options = [str(o) for o in spec.get("options", [])]
    if not options:
        return None
    closes_at = spec.get("closes_at")
    return {"root": root, "channel": channel, "options": options,
            "topic": str(spec.get("topic", root.title)),
            "tag": str(spec.get("tag", "")),
            "closes_at": float(closes_at)
            if isinstance(closes_at, (int, float)) else None}


class VoteChair:
    """The chair side of a blind vote's lifecycle. Lives client-side because
    only the chair's DM threads hold the ballots — the hub knows nothing
    about votes.

    Blindness protects voters from anchoring on earlier ballots; once it
    protects nothing — every eligible member voted, or the deadline passed —
    the result belongs to the channel. `check_due` (driven by the chat app's
    background watcher) publishes on either condition, `recover` re-learns
    chaired votes after a client restart so a deadline never silently dies
    with a closed terminal."""

    def __init__(self, client: Any, me: str,
                 announce: Callable[[str], None]) -> None:
        self.client = client
        self.me = me
        self.announce = announce
        self.open: dict[str, dict[str, Any]] = {}   # root id -> vote_info

    def register(self, root: Any, channel: str) -> None:
        info = vote_info(root, channel)
        if info is not None and root.sender == self.me:
            self.open[root.id] = info

    # -- gathering ----------------------------------------------------------

    async def replies_to(self, channel: str, root: Any) -> list[Any]:
        """All replies to `root`, oldest first — pages forward from the
        root's seq over the existing history endpoint (no hub extension;
        channels at human scale are a few pages)."""
        replies: list[Any] = []
        cursor = root.seq
        while True:
            page = await self.client.history(channel, since=cursor, limit=200)
            if not page:
                return replies
            replies.extend(m for m in page if m.reply_to == root.id)
            cursor = page[-1].seq
            if len(page) < 200:
                return replies

    async def _dm_ballots(self, refs: set[str], options: list[str],
                          since_ts: float) -> dict[str, list[int]]:
        """Blind ballots from the chair's DM threads: peer-sent messages
        (never my own lines — quoting the template back must not cast a
        vote for me) carrying a 'vote TAG: …' line for THIS vote. Latest
        per peer wins; only messages newer than the vote count (small
        clock slack) — DM threads are long-lived."""
        ballots: dict[str, list[int]] = {}
        names = [c["name"] for c in await self.client.list_channels()
                 if c["member"] and c["name"].startswith("dm:")]
        for name in names:
            cursor = 0
            while True:
                page = await self.client.history(name, since=cursor, limit=200)
                if not page:
                    break
                for m in page:
                    if (m.kind.value == "message" and m.sender != self.me
                            and m.created_at >= since_ts - 60):
                        ballot = parse_dm_ballot(m.body, refs, options)
                        if ballot is not None:
                            ballots[m.sender] = ballot
                cursor = page[-1].seq
                if len(page) < 200:
                    break
        return ballots

    async def collect(self, info: dict[str, Any]) -> dict[str, Any]:
        """Everything /tally and the watcher need, in one pass: the
        published result if any (author's, latest wins — forged results
        from others are ignored), public ballots leaked into the channel
        (counted, flagged), DM ballots when I am the chair, commenters,
        and the current member list."""
        root, channel, options = info["root"], info["channel"], info["options"]
        refs = {r for r in (info["tag"].casefold(),
                            f"{root.seq}@{channel}".casefold()) if r}
        replies = await self.replies_to(channel, root)
        published = next(
            (r for r in reversed(replies) if r.sender == root.sender
             and isinstance((r.data or {}).get(VOTE_RESULT_KEY), dict)),
            None)
        public: dict[str, list[int]] = {}
        commenters: set[str] = set()
        for r in replies:
            if r.kind.value != "message" or r is published:
                continue
            ballot = parse_dm_ballot(r.body, refs, options) \
                or ballot_from(r.body, r.data, options)
            if ballot is not None:
                public[r.sender] = ballot      # seq order: latest wins
            else:
                commenters.add(r.sender)
        ballots = dict(public)
        if self.me == root.sender:
            ballots.update(
                await self._dm_ballots(refs, options, root.created_at))
        members: list[str] = []
        with contextlib.suppress(Exception):
            data = await self.client.channel_info(channel)
            members = [m["agent_id"] for m in data.get("members", [])]
        return {"published": published, "public": public, "ballots": ballots,
                "commenters": commenters - set(ballots), "members": members}

    # -- closing --------------------------------------------------------------

    @staticmethod
    def due(info: dict[str, Any], ballots: dict[str, list[int]],
            members: list[str], now: float | None = None) -> str | None:
        """Why this vote should close NOW — 'deadline reached', 'every
        member voted', or None. Full turnout = every current member except
        the chair has a ballot; unknown membership (empty list) never
        triggers it — only the deadline can close a vote we cannot verify
        as complete."""
        now = time.time() if now is None else now
        closes_at = info.get("closes_at")
        if closes_at is not None and now >= closes_at:
            return "deadline reached"
        eligible = {m for m in members if m != info["root"].sender}
        if eligible and eligible <= set(ballots):
            return "every member voted"
        return None

    async def publish(self, info: dict[str, Any],
                      ballots: dict[str, list[int]], members: list[str],
                      reason: str) -> Any:
        """Post the result into the channel (resolved reply + machine
        payload) and forget the vote. From here on, every /tally renders
        from the transcript."""
        root, channel, options = info["root"], info["channel"], info["options"]
        tally = tally_ballots(options, ballots)
        total = len(members) or len(ballots)
        posted = await self.client.post(
            channel, result_body(info["topic"], options, tally, total, reason),
            title=f"VOTE RESULT: {info['topic']}", status=Status.resolved,
            reply_to=root.id,
            data={VOTE_RESULT_KEY: {"topic": info["topic"], "options": options,
                                    "ballots": ballots, "total_members": total,
                                    "closed": reason}})
        self.open.pop(root.id, None)
        return posted

    async def check_due(self) -> None:
        """One watcher tick: publish every chaired vote whose blindness no
        longer protects anything. Votes closed elsewhere (another session,
        a manual /tally close) are dropped from the registry silently."""
        for info in list(self.open.values()):
            with contextlib.suppress(Exception):
                data = await self.collect(info)
                if data["published"] is not None:
                    self.open.pop(info["root"].id, None)
                    continue
                reason = self.due(info, data["ballots"], data["members"])
                if reason is None:
                    continue
                posted = await self.publish(info, data["ballots"],
                                            data["members"], reason)
                self.announce(
                    f"(vote #{info['root'].seq} in {info['channel']} closed"
                    f" — {reason}; result published as #{posted.seq})")

    async def recover(self) -> None:
        """Re-learn the votes I chair after a restart: scan my channels for
        my vote messages without a published result. Best-effort — a vote
        posted from another identity or already closed is not mine to
        watch."""
        with contextlib.suppress(Exception):
            channels = [c["name"] for c in await self.client.list_channels()
                        if c["member"] and not c["name"].startswith("dm:")]
            for name in channels:
                with contextlib.suppress(Exception):
                    mine: dict[str, Any] = {}
                    cursor = 0
                    while True:
                        page = await self.client.history(name, since=cursor,
                                                         limit=200)
                        if not page:
                            break
                        for m in page:
                            if m.sender != self.me:
                                continue
                            if (m.data or {}).get(VOTE_DATA_KEY):
                                mine[m.id] = m
                            elif (isinstance((m.data or {}).get(
                                    VOTE_RESULT_KEY), dict)
                                    and m.reply_to in mine):
                                mine.pop(m.reply_to, None)
                        cursor = page[-1].seq
                        if len(page) < 200:
                            break
                    for root in mine.values():
                        self.register(root, name)


async def watch_votes(chair: VoteChair, *,
                      interval: float = VOTE_WATCH_INTERVAL,
                      recover_every: float = VOTE_RECOVER_INTERVAL,
                      closing: Callable[[], bool] | None = None) -> None:
    """The chair-duty loop every long-lived surface of an identity runs
    (chat app, MCP server process, AgentRunner): adopt this identity's open
    votes wherever they were opened from, then tick, publishing whatever is
    due. Periodic re-recovery adopts votes opened from OTHER surfaces while
    this one is running. Cancellation-safe: surfaces cancel it on shutdown."""
    with contextlib.suppress(asyncio.CancelledError):
        await chair.recover()
        last_recover = time.time()
        while closing is None or not closing():
            await asyncio.sleep(interval)
            if time.time() - last_recover >= recover_every:
                await chair.recover()
                last_recover = time.time()
            await chair.check_due()


async def vote_operation(client: Any, me: str, channel: str, message_id: str,
                         *, close: bool = False) -> dict[str, Any]:
    """Surface-neutral tally/close returning machine-shaped state (the MCP
    tools' backend; the chat /tally renders its own richer view). Honors
    ballot secrecy: only the chair sees counts before publication — and a
    finished vote publishes on sight rather than reporting a stale state."""
    rows = await client.read(channel, message_id)
    root = next((m for m in rows if m.id == message_id), None)
    info = vote_info(root, channel) if root else None
    if info is None:
        return {"ok": False, "error": 400,
                "detail": f"message '{message_id}' in '{channel}' is not a "
                          "vote (no vote payload)",
                "action": "REQUEST FAILED — nothing was posted or changed"}
    chair = VoteChair(client, me, lambda _text: None)
    gathered = await chair.collect(info)
    published = gathered["published"]
    if published is not None:
        return {"closed": True, "published_seq": published.seq,
                "result": published.data[VOTE_RESULT_KEY]}
    if me != root.sender:
        if close:
            return {"ok": False, "error": 403,
                    "detail": f"only {root.sender} (the chair) can close"
                              " this vote",
                    "action": "REQUEST FAILED — nothing was posted or changed"}
        return {"closed": False, "blind": True, "chair": root.sender,
                "closes_at": info["closes_at"],
                "note": "ballots go to the chair by DM; the full result is"
                        " published to the channel when the vote closes"}
    reason = "closed by the chair" if close \
        else VoteChair.due(info, gathered["ballots"], gathered["members"])
    if reason is not None:
        posted = await chair.publish(info, gathered["ballots"],
                                     gathered["members"], reason)
        return {"closed": True, "reason": reason, "published_seq": posted.seq,
                "ballots": gathered["ballots"]}
    counts = dict(zip(info["options"],
                      tally_ballots(info["options"], gathered["ballots"]).first))
    waiting = sorted(set(gathered["members"]) - set(gathered["ballots"])
                     - {root.sender})
    return {"closed": False, "chair": me, "counts": counts,
            "ballots": gathered["ballots"], "waiting": waiting,
            "closes_at": info["closes_at"],
            "commenters": sorted(gathered["commenters"])}
