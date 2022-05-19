from . import auth


def foreign_key_entries(db):
    # Records to accommodate for foreign key constraints
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID", 12345678910, "email1", "addressline11", null,'
        ' "addressline31", "addressline41", "ABC DEF")')

    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID", "Gp1", "contactDetailUUID")')
    db.session.execute(
        'INSERT INTO sensitivities() VALUES ("sensitivityUUID", "Water allergy", "What it says on the tin")')

    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID", "gpsUUID", "sensitivityUUID", "Ben", "Jackson", "F",'
        ' 12, "contactDetailUUID")')
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID", "Drug 1")')
    db.session.execute('INSERT INTO standardtests () VALUES ("testUUID", "INCOMPLETE")')


def test_not_authorised(client):
    res = client.get("/api/pickup")
    assert res.status_code == 401
    assert "pickup_status" not in str(res.json)


def test_no_pickup_id_parameter(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/pickup", headers={'Authorization': "Bearer " + token})

    assert res.status_code == 400

    assert "pickup_status" not in str(res.json)


def test_no_pickups_to_return(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/pickup", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_id": "test-id"})

    assert res.status_code == 404
    assert "pickup_status" not in str(res.json)


def test_pickup_id_not_found(client, db):
    foreign_key_entries(db)

    # Record that should not be returned
    db.session.execute(
        'INSERT INTO medicalpickups () VALUES ("medicalPickupUUID",'
        ' "patientUUID", "drugUUID", 1, "2021-02-01", "2021-02-01", 1, "AWAITING_PICKUP")')

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/pickup", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_id": "sdasdasdsa"})

    assert "pickup_status" not in str(res.json)
    assert res.status_code == 404


def test_pickup_successfully_returned(client, db):
    foreign_key_entries(db)

    # Record to be extracted
    db.session.execute(
        'INSERT INTO medicalpickups () VALUES ("medicalPickupUUID",'
        ' "patientUUID", "drugUUID", 1, "2021-02-01", "2021-02-01", 1, "AWAITING_PICKUP")')
    # Record that should be returned
    db.session.execute(
        'INSERT INTO medicalpickups () VALUES ("medicalPickupUUID2",'
        ' "patientUUID", "drugUUID", 1, "2021-03-01", "2021-03-01", 1, "AWAITING_PICKUP")')

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/pickup", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_id": "medicalPickupUUID"})

    assert res.status_code == 200

    assert res.json['pickup_id'] == "medicalPickupUUID"
    assert res.json['patient_id'] == "patientUUID"
    assert res.json['drug_id'] == "drugUUID"
    assert res.json['drug_quantity'] == 1
    assert res.json['scheduled_date'] == "2021-02-01"
    assert res.json['review_date'] == "2021-02-01"
    assert res.json['is_authorised'] == "authorised"
    assert res.json['pickup_status'] == "AWAITING_PICKUP"
