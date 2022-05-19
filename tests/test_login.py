from . import auth


def test_successful_login(client, db):
    res = auth.successful_login(client, db, "theusername", "pspaomdpasmdpomapsd", "admin")
    assert res.status_code == 200


def test_login_incorrect_username(client, db):
    res = auth.login_bad_username(client, db, "theusername", "pspaomdpasmdpomapsd", "admin")
    assert res.status_code == 401


def test_login_incorrect_password(client, db):
    res = auth.login_bad_password(client, db, "theusername", "pspaomdpasmdpomapsd", "admin")
    assert res.status_code == 401


def test_role_correct(client, db):
    role = "testrole"

    res = auth.successful_login(client, db, "testUser", "sdnaslndlas", role)

    token = res.json['access_token']

    res = client.get("/api/test/auth", headers={'Authorization': "Bearer " + token})

    assert res.status_code == 200
    assert res.json['role'] == role


def test_bad_auth_token_rejected(client):
    assert client.get("/api/test/auth").status_code == 401
    assert client.get("/api/test/auth", headers={"Authorization": "Bearer mlmlm"}).status_code == 401
