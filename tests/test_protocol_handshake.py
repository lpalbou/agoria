"""The protocol handshake must be load-bearing: a client built for one
`agora/X.Y` warns (once) when the hub advertises another, and stays silent on
a match. See docs/protocol.md "Scope and stability"."""

from __future__ import annotations

import asyncio
import warnings

import pytest

from agora import PROTOCOL_VERSION
from agora.client import AgoraClient


@pytest.fixture()
def client():
    c = AgoraClient("http://hub.example:8765", "key")
    yield c
    asyncio.run(c.close())  # release the underlying httpx client


def test_mismatch_warns_once_and_records_hub_protocol(client):
    with pytest.warns(RuntimeWarning, match="hub speaks agora/9.9"):
        client._check_protocol("agora/9.9")
    assert client.hub_protocol == "agora/9.9"

    # Second sighting is silent: one warning per client, not one per call.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        client._check_protocol("agora/9.9")


def test_match_and_missing_are_silent(client):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        client._check_protocol(PROTOCOL_VERSION)   # same protocol: silence
        client._check_protocol(None)               # pre-0.9 hub omits it: silence
    assert client.hub_protocol is None             # nothing advertised sticks
