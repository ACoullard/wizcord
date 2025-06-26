from cryptography import fernet
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
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


    