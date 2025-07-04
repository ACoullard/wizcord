import pytest

@pytest.fixture()
def app():

    from app import app as my_app
    
    my_app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield my_app

    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def logged_in_client(client):
    client.post("/api/login", json={
        "username":"jerma985",
        "password":"test"
    })
    return client

