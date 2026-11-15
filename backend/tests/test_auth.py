def test_register_success(client):
    resp = client.post("/auth/register", json={"email": "new@docvera.test", "password": "pass1234"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@docvera.test"
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@docvera.test", "password": "pass1234"})
    resp = client.post("/auth/register", json={"email": "dup@docvera.test", "password": "pass1234"})
    assert resp.status_code == 409


def test_login_success(client):
    client.post("/auth/register", json={"email": "login@docvera.test", "password": "pass1234"})
    resp = client.post("/auth/login", json={"email": "login@docvera.test", "password": "pass1234"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "wp@docvera.test", "password": "pass1234"})
    resp = client.post("/auth/login", json={"email": "wp@docvera.test", "password": "wrongpass"})
    assert resp.status_code == 401


def test_me_with_valid_token(registered_user):
    client, token, user = registered_user
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@docvera.test"


def test_me_without_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 403
