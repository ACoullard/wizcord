"""SSE endpoint tests — auth and authorization only.

Full streaming delivery tests (subscribe → publish → receive via SSE) require
async or live-server infrastructure. The synchronous Flask test client would
block forever on the `while True` generator loop. The Redis publish half is
already covered by test_channels.py::test_post_message_publishes_to_redis.
"""


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
