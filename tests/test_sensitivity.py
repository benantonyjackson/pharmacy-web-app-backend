from . import auth


def test_not_authorised(client):
    res = client.get("/api/sensitivity")
    assert res.status_code == 401
    assert "sensitivity_id" not in str(res.json)


def test_no_sensitivity_id_parameter(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/sensitivity", headers={'Authorization': "Bearer " + token})

    assert res.status_code == 400

    assert "name" not in str(res.json)


def test_no_sensitivity_to_return(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/sensitivity", headers={'Authorization': "Bearer " + token},
                     query_string={"sensitivity_id": "sensitivity-id"})

    assert res.status_code == 404
    assert "name" not in str(res.json)


def test_sensitivity_id_not_found(client, db):
    # Record that should not be returned
    db.session.execute('INSERT INTO sensitivities() '
                       'VALUES'
                       '("9db1906a-4dab-44b3-b6e1-8b4460cb9b62", "Water allergy",'
                       ' "What it says on the tin")')

    # Record that should not be returned
    db.session.execute('INSERT INTO sensitivities() VALUES ("b9b7fc9d-df55-4ded-94ba-1b61498529cd", "Air allergy",'
                       ' "What it says on the tin")')

    # Record that should not be returned
    db.session.execute('INSERT INTO sensitivities() VALUES ("24243d1e-597b-49fb-b625-e65c5b9037f1", '
                       '"Visible light allergy", "What it says on the tin")')

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/sensitivity", headers={'Authorization': "Bearer " + token},
                     query_string={"sensitivity_id": "sdasdasdsa"})

    assert "name" not in str(res.json)
    assert res.status_code == 404


def test_sensitivity_successfully_retrieved(client, db):
    # Record that should not be returned
    db.session.execute('INSERT INTO sensitivities() '
                       'VALUES'
                       '("9db1906a-4dab-44b3-b6e1-8b4460cb9b62", "Water allergy",'
                       ' "What it says on the tin")')

    # Record that should be returned
    db.session.execute('INSERT INTO sensitivities() VALUES ("b9b7fc9d-df55-4ded-94ba-1b61498529cd", "Air allergy",'
                       ' "What it says on the tin")')

    # Record that should not be returned
    db.session.execute('INSERT INTO sensitivities() VALUES ("24243d1e-597b-49fb-b625-e65c5b9037f1", '
                       '"Visible light allergy", "What it says on the tin")')

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/sensitivity", headers={'Authorization': "Bearer " + token},
                     query_string={"sensitivity_id": "b9b7fc9d-df55-4ded-94ba-1b61498529cd"})

    assert res.status_code == 200

    assert res.json['sensitivity_id'] == "b9b7fc9d-df55-4ded-94ba-1b61498529cd"
    assert res.json['name'] == "Air allergy"
    assert res.json['description'] == "What it says on the tin"

