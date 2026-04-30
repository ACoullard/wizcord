def test_get_servers_unauthenticated(client):
    res = client.get("/api/servers")
    assert res.status_code == 401


def test_get_servers_returns_list(logged_in_client):
    res = logged_in_client.get("/api/servers")
    assert res.status_code == 200
    servers = res.get_json()
    assert isinstance(servers, list) and len(servers) >= 1
    assert all("id" in s and "name" in s for s in servers)


def test_get_server_data_unauthenticated(client, app):
    server_id = str(app.config["_test_ids"]["server_id"])
    res = client.get(f"/api/server-data/{server_id}")
    assert res.status_code == 401


def test_get_server_data_unauthorized(logged_in_client):
    from api.shared_resources import model
    other_server_id = model.add_server("secret server")
    res = logged_in_client.get(f"/api/server-data/{other_server_id}")
    assert res.status_code == 401


def test_get_server_data(logged_in_client):
    servers = logged_in_client.get("/api/servers").get_json()
    server_id = servers[0]["id"]

    res = logged_in_client.get(f"/api/server-data/{server_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert "channels" in data and len(data["channels"]) >= 1
    assert "users" in data and len(data["users"]) >= 1
    assert all("id" in u and "username" in u for u in data["users"])


def test_current_user_in_server_member_list(logged_in_client):
    servers = logged_in_client.get("/api/servers").get_json()
    server_id = servers[0]["id"]
    server_data = logged_in_client.get(f"/api/server-data/{server_id}").get_json()
    current_user = logged_in_client.get("/api/login/current-user").get_json()
    user_ids = [u["id"] for u in server_data["users"]]
    assert current_user["id"] in user_ids
