from cryptography.hazmat.primitives.asymmetric import x25519
import base64
from flask import session

def test_init_e2ee(client):
    res = client.get("/api/init-e2ee")

def test_session_login(client):
    res1 = client.post("/api/login", json={
        "username":"jerma985",
        "password":"test"
    })
    res2 = client.get("/api/login/current-user")
    result = res2.json["username"]
    assert result == "jerma985"


def test_e2ee(client):
    res = client.get("/api/init-e2ee")
    public_key_string = res.json["x255_public_key"]
    client_private_key = x25519.X25519PrivateKey.generate()
    public_key_bytes = base64.b64decode(public_key_string)
    public_key = x25519.X25519PublicKey.from_public_bytes(public_key_bytes)
    sym_key = client_private_key.exchange(public_key)

    client_public_key = client_private_key.public_key()
    client_public_bytes = client_public_key.public_bytes_raw()
    client_public_key_b64 = base64.b64encode(client_public_bytes).decode("utf-8")

    with client:
        res2 = client.post("/api/respond-e2ee", json={
            "public_key": client_public_key_b64
        })
        print(res2)
        server_sym_ley = session["symmetric_key"]

    assert sym_key == server_sym_ley
    print(f"client sym key: {sym_key}\nserver sym key: {server_sym_ley}")


def test_anonymous_login(client):
    # Anonymous login should create a user with is_anonymous=True and log the client in
    res = client.post("/api/login/anonymous")
    assert res.status_code == 200
    data = res.get_json()
    assert "username" in data and "id" in data

    from api.shared_resources import model
    from bson import ObjectId

    user = model.get_user_by_id(ObjectId(data["id"]))
    assert user.get("is_anonymous") is True

    # current-user endpoint should now return the logged-in anonymous user
    res2 = client.get("/api/login/current-user")
    assert res2.status_code == 200
    assert res2.get_json()["id"] == data["id"]


def test_anonymous_login_creates_new_each_call(client):
    # First anonymous login creates a user
    res1 = client.post("/api/login/anonymous")
    assert res1.status_code == 200
    data1 = res1.get_json()

    # Second anonymous login in same session should create a new distinct anonymous user
    res2 = client.post("/api/login/anonymous")
    assert res2.status_code == 200
    data2 = res2.get_json()

    assert data1["id"] != data2["id"]

    # Ensure both are marked anonymous in DB
    from api.shared_resources import model
    from bson import ObjectId
    db_user1 = model.get_user_by_id(ObjectId(data1["id"]))
    db_user2 = model.get_user_by_id(ObjectId(data2["id"]))
    assert db_user1.get("is_anonymous") is True
    assert db_user2.get("is_anonymous") is True


def test_unauthenticated_current_user_returns_401(client):
    # A fresh unauthenticated client should get 401, not a 200 with a ghost anonymous user
    res = client.get("/api/login/current-user")
    assert res.status_code == 401


def test_unauthenticated_request_does_not_create_db_user(client):
    # Hitting current-user without any session should not insert any user into the DB
    from api.shared_resources import model
    user_count_before = model.users.count_documents({})

    client.get("/api/login/current-user")

    user_count_after = model.users.count_documents({})
    assert user_count_before == user_count_after
