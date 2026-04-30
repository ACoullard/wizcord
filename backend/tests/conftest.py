import os

# Must be set before app.py is imported — it has no default and crashes on KeyError.
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")

import mongomock
import fakeredis
import pytest
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Session-level patches — activated before any test module or app code is
# imported so that every MongoClient() and Redis.from_url() call uses fakes.
# ---------------------------------------------------------------------------

_fake_redis_server = fakeredis.FakeServer()

_mongo_patch = mongomock.patch(servers=(("localhost", 27017),))
_mongo_patch.start()

_redis_patch = patch(
    "redis.Redis.from_url",
    lambda *a, **kw: fakeredis.FakeRedis(server=_fake_redis_server, decode_responses=False),
)
_redis_patch.start()


def pytest_sessionfinish(session, exitstatus):
    _redis_patch.stop()
    _mongo_patch.stop()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_redis():
    return fakeredis.FakeRedis(server=_fake_redis_server, decode_responses=False)


def _seed(model):
    """Insert a standard set of test data and return the created IDs."""
    from models.model import AccessLevel

    server_id = model.add_server("test server")
    channel_id = model.add_channel("general", server_id)
    channel_id2 = model.add_channel("off-topic", server_id)

    user1_id = model.add_user("jerma985", "jerma@test.com")
    model.add_user_to_server(user1_id, server_id)
    model.add_user_to_channel(user1_id, channel_id, AccessLevel.POST)
    model.add_user_to_channel(user1_id, channel_id2, AccessLevel.POST)

    user2_id = model.add_user("theFreak", "freak@test.com")
    model.add_user_to_server(user2_id, server_id)
    model.add_user_to_channel(user2_id, channel_id, AccessLevel.VIEW)

    return {
        "server_id": server_id,
        "channel_id": channel_id,
        "channel_id2": channel_id2,
        "user1_id": user1_id,
        "user2_id": user2_id,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def app():
    import api.shared_resources as sr
    import api.login_bp as login_mod
    import api.channels_bp as channels_mod
    from models.model import DB_NAME

    # Reconnect model singleton to the (freshly emptied) mongomock store.
    sr.model.connect(verbose=False)

    # Replace redis_client in every module that imported it as a local binding.
    r = _fresh_redis()
    sr.redis_client = r
    login_mod.redis_client = r
    channels_mod.redis_client = r

    from app import app as flask_app
    flask_app.config.update({"TESTING": True})

    flask_app.config["_test_ids"] = _seed(sr.model)

    yield flask_app

    sr.model.client.drop_database(DB_NAME)
    _fresh_redis().flushall()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def logged_in_client(client):
    client.post("/api/login", json={"username": "jerma985", "password": "test"})
    return client


@pytest.fixture()
def fake_redis_server():
    return _fake_redis_server
