from . import auth


def test_not_authorised(client):
    res = client.get("/api/drug")
    assert res.status_code == 401
    assert "drug_id" not in str(res.json)


def test_drug_no_drug_id_parameter(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "pharmacist")
    res = client.get("/api/drug", headers={'Authorization': "Bearer " + token})
    assert res.status_code == 400
    assert "name" not in str(res.json)


def test_no_drug_to_return(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "pharmacist")
    res = client.get("/api/drug", headers={'Authorization': "Bearer " + token},
                     query_string={"drug_id": "drug-id"})
    assert res.status_code == 404
    assert "name" not in str(res.json)


def test_drug_id_not_found(client, db):
    # Record that should not be returned
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID", "Paracetamol")')
    token = auth.get_access_token(client, db, "test_user", "test_password", "pharmacist")
    res = client.get("/api/drug", headers={'Authorization': "Bearer " + token},
                     query_string={"drug_id": "sdasdasdsa"})
    assert "name" not in str(res.json)
    assert res.status_code == 404


def test_drug_successfully_returned(client, db):
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID", "Paracetamol")')
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID2", "Aspirin")')
    token = auth.get_access_token(client, db, "test_user", "test_password", "pharmacist")
    res = client.get("/api/drug", headers={'Authorization': "Bearer " + token},
                     query_string={"drug_id": "drugUUID2"})
    assert res.status_code == 200
    assert res.json['drug_id'] == "drugUUID2"
    assert res.json['name'] == "Aspirin"