import json


def test_get_messages_unauthenticated(client, app):
    channel_id = str(app.config["_test_ids"]["channel_id"])
    res = client.get(f"/api/channel/{channel_id}")
    assert res.status_code == 401


def test_post_message_unauthenticated(client, app):
    channel_id = str(app.config["_test_ids"]["channel_id"])
    res = client.post(f"/api/channel/{channel_id}/post", json={"content": "hello"})
    assert res.status_code == 401


def test_post_message(logged_in_client, app):
    channel_id = str(app.config["_test_ids"]["channel_id"])
    res = logged_in_client.post(f"/api/channel/{channel_id}/post", json={"content": "hello world"})
    assert res.status_code == 200
    assert "id" in res.get_json()


def test_get_messages_empty_channel(logged_in_client, app):
    channel_id = str(app.config["_test_ids"]["channel_id"])
    res = logged_in_client.get(f"/api/channel/{channel_id}")
    assert res.status_code == 200
    body = res.get_json()
    assert body["data"] == []


def test_get_messages_after_post(logged_in_client, app):
    channel_id = str(app.config["_test_ids"]["channel_id"])
    logged_in_client.post(f"/api/channel/{channel_id}/post", json={"content": "test message"})

    res = logged_in_client.get(f"/api/channel/{channel_id}")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert len(data) == 1
    assert data[0]["content"] == "test message"
    assert "id" in data[0] and "author_id" in data[0]


def test_get_messages_pagination(logged_in_client, app):
    channel_id = str(app.config["_test_ids"]["channel_id"])
    for i in range(5):
        logged_in_client.post(f"/api/channel/{channel_id}/post", json={"content": f"msg {i}"})

    res = logged_in_client.get(f"/api/channel/{channel_id}?page=0&limit=3")
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["data"]) == 3
    assert body["metadata"][0]["totalCount"] == 5


def test_get_messages_unauthorized_channel(logged_in_client):
    from api.shared_resources import model
    other_server_id = model.add_server("other server")
    other_channel_id = model.add_channel("private", other_server_id)
    res = logged_in_client.get(f"/api/channel/{other_channel_id}")
    assert res.status_code == 401


def test_post_message_unauthorized_channel(logged_in_client):
    from api.shared_resources import model
    other_server_id = model.add_server("other server")
    other_channel_id = model.add_channel("private", other_server_id)
    res = logged_in_client.post(
        f"/api/channel/{other_channel_id}/post",
        json={"content": "hacked"}
    )
    assert res.status_code == 401


def test_post_message_publishes_to_redis(logged_in_client, app, fake_redis_server):
    import fakeredis

    channel_id = str(app.config["_test_ids"]["channel_id"])

    r = fakeredis.FakeRedis(server=fake_redis_server, decode_responses=False)
    pubsub = r.pubsub()
    pubsub.subscribe(f"channel:{channel_id}")
    pubsub.get_message()  # consume the subscribe-confirmation message

    logged_in_client.post(f"/api/channel/{channel_id}/post", json={"content": "published"})

    msg = pubsub.get_message()
    assert msg is not None and msg["type"] == "message"
    data = json.loads(msg["data"])
    assert data["content"] == "published"
    assert "id" in data and "author_id" in data

    pubsub.unsubscribe()
    pubsub.close()
