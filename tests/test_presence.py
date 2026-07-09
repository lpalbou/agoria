"""PresenceTracker state hierarchy: connection > recent activity > declared
state > offline. 'active' exists because MCP/REST-only tabs have no push
connection and must not read 'offline' while visibly working."""

from __future__ import annotations

from agora.hub.presence import _ACTIVE_WINDOW, PresenceTracker


def test_never_seen_is_offline():
    t = PresenceTracker()
    assert t.get("ghost").state == "offline"


def test_rest_activity_reads_active_and_ages_out():
    t = PresenceTracker()
    t.touch("bob")
    assert t.get("bob").state == "active"
    # Age the activity past the window: back to offline.
    t._last_seen["bob"] -= _ACTIVE_WINDOW + 1
    assert t.get("bob").state == "offline"


def test_connection_outranks_activity_and_disconnect_falls_back():
    t = PresenceTracker()
    t.touch("bob")
    t.connect("bob")
    assert t.get("bob").state == "idle"          # connected: declared state
    t.update("bob", "working")
    assert t.get("bob").state == "working"
    t.disconnect("bob")
    assert t.get("bob").state == "active"        # recent activity still counts
    t._last_seen["bob"] -= _ACTIVE_WINDOW + 1
    assert t.get("bob").state == "offline"       # goodbye state aged out too
