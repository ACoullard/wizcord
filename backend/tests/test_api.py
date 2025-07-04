from flask import session


def test_get_servers(logged_in_client):
    res = logged_in_client.get("/api/servers")
    
    server_id = res.json[0]["id"]

    res2 = logged_in_client.get(f"/api/server-data/{server_id}")

    print(res2.json)

    res3 = logged_in_client.get("/api/login/current-user")
    print(res3.json)

    assert res2.json["users"][0] == res3.json["id"]