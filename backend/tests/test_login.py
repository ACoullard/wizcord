from cryptography.hazmat.primitives.asymmetric import x25519
import base64
from flask import session


def test_login_success(client):
    res = client.post("/api/login", json={"username": "jerma985", "password": "test"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["username"] == "jerma985"
    assert "id" in data


def test_login_unknown_user(client):
    res = client.post("/api/login", json={"username": "nobody", "password": "test"})
    assert res.status_code == 401


def test_current_user_after_login(client):
    client.post("/api/login", json={"username": "jerma985", "password": "test"})
    res = client.get("/api/login/current-user")
    assert res.status_code == 200
    assert res.get_json()["username"] == "jerma985"


def test_unauthenticated_current_user_returns_401(client):
    res = client.get("/api/login/current-user")
    assert res.status_code == 401


def test_unauthenticated_request_does_not_create_db_user(client):
    from api.shared_resources import model
    count_before = model.users.count_documents({})
    client.get("/api/login/current-user")
    assert model.users.count_documents({}) == count_before


def test_anonymous_login_returns_user_data(client):
    res = client.post("/api/login/anonymous")
    assert res.status_code == 200
    data = res.get_json()
    assert "username" in data and "id" in data


def test_anonymous_login_creates_anonymous_db_user(client):
    res = client.post("/api/login/anonymous")
    data = res.get_json()

    from api.shared_resources import model
    from bson import ObjectId
    user = model.get_user_by_id(ObjectId(data["id"]))
    assert user.get("is_anonymous") is True


def test_anonymous_login_logs_in_user(client):
    res = client.post("/api/login/anonymous")
    anon_id = res.get_json()["id"]
    res2 = client.get("/api/login/current-user")
    assert res2.status_code == 200
    assert res2.get_json()["id"] == anon_id


def test_anonymous_login_creates_new_user_each_call(client):
    res1 = client.post("/api/login/anonymous")
    res2 = client.post("/api/login/anonymous")
    assert res1.get_json()["id"] != res2.get_json()["id"]


def test_e2ee_key_exchange(client):
    res = client.get("/api/init-e2ee")
    assert res.status_code == 200
    public_key_string = res.get_json()["x255_public_key"]

    client_private_key = x25519.X25519PrivateKey.generate()
    server_public_key = x25519.X25519PublicKey.from_public_bytes(base64.b64decode(public_key_string))
    client_sym_key = client_private_key.exchange(server_public_key)

    client_public_b64 = base64.b64encode(client_private_key.public_key().public_bytes_raw()).decode()

    with client:
        res2 = client.post("/api/respond-e2ee", json={"public_key": client_public_b64})
        assert res2.status_code == 200
        server_sym_key = session["symmetric_key"]

    assert client_sym_key == server_sym_key
