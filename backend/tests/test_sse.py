"""SSE endpoint tests — auth, authorization, and stream lifetime.

Delivery tests (subscribe → publish → receive via SSE) still require async or
live-server infrastructure; the synchronous test client cannot consume a stream
while also publishing to it. The Redis publish half is covered by
test_channels.py::test_post_message_publishes_to_redis. The lifetime cap is
testable because the generator now terminates on its own.
"""

import pytest


@pytest.fixture
def short_streams(monkeypatch):
    """Shrink the lifetime cap and heartbeat so a stream completes in-test."""
    import api.channels_bp as channels_mod
    monkeypatch.setattr(channels_mod, "SSE_MAX_STREAM_SECONDS", 0.5)
    monkeypatch.setattr(channels_mod, "SSE_HEARTBEAT_SECONDS", 0.05)


def test_message_stream_requires_auth(client, app):
    channel_id = str(app.config["_test_ids"]["channel_id"])
    res = client.get(f"/api/channel/message-stream?channel={channel_id}")
    assert res.status_code == 401


def test_server_member_stream_requires_auth(client, app):
    server_id = str(app.config["_test_ids"]["server_id"])
    res = client.get(f"/api/channel/server-member-stream?server={server_id}")
    assert res.status_code == 401


def test_message_stream_invalid_channel_returns_400(logged_in_client):
    res = logged_in_client.get("/api/channel/message-stream?channel=notanobjectid")
    assert res.status_code == 400


def test_message_stream_unauthorized_channel_returns_401(logged_in_client):
    from api.shared_resources import model
    other_server_id = model.add_server("other")
    other_channel_id = model.add_channel("secret", other_server_id)
    res = logged_in_client.get(f"/api/channel/message-stream?channel={other_channel_id}")
    assert res.status_code == 401


def test_server_member_stream_invalid_server_returns_400(logged_in_client):
    res = logged_in_client.get("/api/channel/server-member-stream?server=notanobjectid")
    assert res.status_code == 400


def test_server_member_stream_unauthorized_server_returns_401(logged_in_client):
    from api.shared_resources import model
    other_server_id = model.add_server("other")
    res = logged_in_client.get(f"/api/channel/server-member-stream?server={other_server_id}")
    assert res.status_code == 401


def test_message_stream_closes_at_lifetime_cap(logged_in_client, app, short_streams):
    channel_id = str(app.config["_test_ids"]["channel_id"])
    res = logged_in_client.get(f"/api/channel/message-stream?channel={channel_id}")
    body = res.get_data(as_text=True)
    assert res.status_code == 200
    assert ": heartbeat" in body


def test_server_member_stream_closes_at_lifetime_cap(logged_in_client, app, short_streams):
    server_id = str(app.config["_test_ids"]["server_id"])
    res = logged_in_client.get(f"/api/channel/server-member-stream?server={server_id}")
    body = res.get_data(as_text=True)
    assert res.status_code == 200
    assert ": heartbeat" in body


def test_stream_unsubscribes_after_lifetime_cap(logged_in_client, app, short_streams):
    from api.shared_resources import redis_client
    channel_id = str(app.config["_test_ids"]["channel_id"])
    res = logged_in_client.get(f"/api/channel/message-stream?channel={channel_id}")
    res.get_data()
    assert redis_client.pubsub_numsub(f"channel:{channel_id}")[0][1] == 0


def test_lifetime_cap_is_never_exceeded(logged_in_client, app, monkeypatch):
    """The jittered deadline must stay under the configured cap, or a restart
    resynchronises every client onto a single expiry moment."""
    import time
    import api.channels_bp as channels_mod
    monkeypatch.setattr(channels_mod, "SSE_MAX_STREAM_SECONDS", 0.4)
    monkeypatch.setattr(channels_mod, "SSE_HEARTBEAT_SECONDS", 0.05)
    channel_id = str(app.config["_test_ids"]["channel_id"])

    start = time.monotonic()
    res = logged_in_client.get(f"/api/channel/message-stream?channel={channel_id}")
    res.get_data()
    elapsed = time.monotonic() - start

    assert 0.4 * 0.8 <= elapsed <= 0.4 + 0.2
