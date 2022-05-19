from . import auth


def test_return_empty(db, client):
    token = auth.get_access_token(client, db, "testUser", "password", "pharmacist")
    res = client.get("/api/pickups", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_status": "AWAITING_PHARMACIST_AUTHORISATION",
                                   "scheduled_before": "2022-01-01"}
                     )
    assert res.json == []
    assert res.status_code == 200


def test_return_one(db, client):
    token = auth.get_access_token(client, db, "testUser", "password", "pharmacist")
    db.session.execute('INSERT INTO contactdetails () VALUES ("contactDetailUUID", 12345678910, "email1", "addressline11", null, "addressline31", "addressline41", "ABC DEF")')
    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID", "Gp1", "contactDetailUUID")')
    db.session.execute('INSERT INTO sensitivities() VALUES ("sensitivityUUID", "Water allergy", "What it says on the tin")')
    db.session.execute('INSERT INTO patients() VALUES ("patientUUID", "gpsUUID", "sensitivityUUID", "Ben", "Jackson", "F", 12, "contactDetailUUID")')
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID", "Drug 1")')
    db.session.execute('INSERT INTO standardtests () VALUES ("testUUID", "Blood test 1")')
    db.session.execute('INSERT INTO medicalpickups () VALUES ("medicalPickupUUID", "patientUUID", "drugUUID", 1, 2021-02-01, 2021-02-01, 1, "AWAITING_PHARMACIST_AUTHORISATION")')

    res = client.get("/api/pickups", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_status": "AWAITING_PHARMACIST_AUTHORISATION",
                                   "scheduled_before": "2022-01-01"})

    assert res.json[0]["pickup_id"] == 'medicalPickupUUID'
    assert res.status_code == 200


def test_return_multiple(db, client):
    token = auth.get_access_token(client, db, "testUser", "password", "pharmacist")
    db.session.execute('INSERT INTO contactdetails () VALUES ("contactDetailUUID", 12345678910, "email1", "addressline11", null, "addressline31", "addressline41", "ABC DEF")')
    db.session.execute('INSERT INTO contactdetails () VALUES ("contactDetailUUID2", 01987654321, "email2", "addressline12", null, "addressline32", "addressline42", "DEF ABC")')
    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID", "Gp1", "contactDetailUUID")')
    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID2", "Gp2", "contactDetailUUID2")')
    db.session.execute('INSERT INTO sensitivities() VALUES ("sensitivityUUID", "Water allergy", "What it says on the tin")')
    db.session.execute('INSERT INTO sensitivities() VALUES ("sensitivityUUID2", "Water allergy", "What it says on the tin")')
    db.session.execute('INSERT INTO patients() VALUES ("patientUUID", "gpsUUID", "sensitivityUUID", "Ben", "Jackson", "F", 12, "contactDetailUUID")')
    db.session.execute('INSERT INTO patients() VALUES ("patientUUID2", "gpsUUID2", "sensitivityUUID2", "Ben", "Jackson", "F", 12, "contactDetailUUID2")')
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID", "Drug 1")')
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID2", "Drug 1")')
    db.session.execute('INSERT INTO standardtests () VALUES ("testUUID", "Blood test 1")')
    db.session.execute('INSERT INTO standardtests () VALUES ("testUUID2", "Blood test 2")')
    db.session.execute('INSERT INTO medicalpickups () VALUES ("medicalPickupUUID", "patientUUID", "drugUUID", 1, 2021-02-01, 2021-02-01, 1, "AWAITING_PHARMACIST_AUTHORISATION")')
    db.session.execute('INSERT INTO medicalpickups () VALUES ("medicalPickupUUID2", "patientUUID2", "drugUUID2", 1, 2021-02-01, 2021-02-01, 1, "AWAITING_PHARMACIST_AUTHORISATION")')

    res = client.get("/api/pickups", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_status": "AWAITING_PHARMACIST_AUTHORISATION",
                                   "scheduled_before": "2022-01-01"})

    assert len(res.json) == 2
    assert res.json[0]["pickup_id"] == 'medicalPickupUUID'
    assert res.json[1]["pickup_id"] == 'medicalPickupUUID2'
    assert res.status_code == 200


def test_filter_by_status(db, client):
    token = auth.get_access_token(client, db, "testUser", "password", "pharmacist")
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID", 12345678910, "email1", "addressline11", null, "addressline31", "addressline41", "ABC DEF")')
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID2", 01987654321, "email2", "addressline12", null, "addressline32", "addressline42", "DEF ABC")')
    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID", "Gp1", "contactDetailUUID")')
    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID2", "Gp2", "contactDetailUUID2")')
    db.session.execute(
        'INSERT INTO sensitivities() VALUES ("sensitivityUUID", "Water allergy", "What it says on the tin")')
    db.session.execute(
        'INSERT INTO sensitivities() VALUES ("sensitivityUUID2", "Water allergy", "What it says on the tin")')
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID", "gpsUUID", "sensitivityUUID", "Ben", "Jackson", "F", 12, "contactDetailUUID")')
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID2", "gpsUUID2", "sensitivityUUID2", "Ben", "Jackson", "F", 12, "contactDetailUUID2")')
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID", "Drug 1")')
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID2", "Drug 1")')
    db.session.execute('INSERT INTO standardtests () VALUES ("testUUID", "Blood test 1")')
    db.session.execute('INSERT INTO standardtests () VALUES ("testUUID2", "Blood test 2")')
    db.session.execute(
        'INSERT INTO medicalpickups () VALUES ("medicalPickupUUID", "patientUUID", "drugUUID", 1, 2021-02-01, 2021-02-01, 1, "AWAITING_PHARMACIST_AUTHORISATION")')
    db.session.execute(
        'INSERT INTO medicalpickups () VALUES ("medicalPickupUUID2", "patientUUID2", "drugUUID2", 1, 2021-02-01, 2021-02-01, 1, "AWAITING_CONFIRMATION")')

    res = client.get("/api/pickups", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_status": "AWAITING_PHARMACIST_AUTHORISATION",
                                   "scheduled_before": "2022-01-01"})

    assert len(res.json) == 1
    assert res.json[0]["pickup_id"] == 'medicalPickupUUID'
    assert res.status_code == 200


def test_filter_by_date_scheduled(db, client):
    token = auth.get_access_token(client, db, "testUser", "password", "pharmacist")
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID", 12345678910, "email1", "addressline11", null, "addressline31", "addressline41", "ABC DEF")')
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID2", 01987654321, "email2", "addressline12", null, "addressline32", "addressline42", "DEF ABC")')
    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID", "Gp1", "contactDetailUUID")')
    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID2", "Gp2", "contactDetailUUID2")')
    db.session.execute(
        'INSERT INTO sensitivities() VALUES ("sensitivityUUID", "Water allergy", "What it says on the tin")')
    db.session.execute(
        'INSERT INTO sensitivities() VALUES ("sensitivityUUID2", "Water allergy", "What it says on the tin")')
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID", "gpsUUID", "sensitivityUUID", "Ben", "Jackson", "F", 12, "contactDetailUUID")')
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID2", "gpsUUID2", "sensitivityUUID2", "Ben", "Jackson", "F", 12, "contactDetailUUID2")')
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID", "Drug 1")')
    db.session.execute('INSERT INTO drugs () VALUES ("drugUUID2", "Drug 1")')
    db.session.execute('INSERT INTO standardtests () VALUES ("testUUID", "Blood test 1")')
    db.session.execute('INSERT INTO standardtests () VALUES ("testUUID2", "Blood test 2")')
    db.session.execute(
        'INSERT INTO medicalpickups () VALUES ("medicalPickupUUID", "patientUUID", "drugUUID", 1, "2021-02-01", "2021-02-01", 1, "AWAITING_PHARMACIST_AUTHORISATION")')
    db.session.execute(
        'INSERT INTO medicalpickups () VALUES ("medicalPickupUUID2", "patientUUID2", "drugUUID2", 1, "2021-03-01", "2021-03-01", 1, "AWAITING_PHARMACIST_AUTHORISATION")')

    res = client.get("/api/pickups", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_status": "AWAITING_PHARMACIST_AUTHORISATION",
                                   "scheduled_before": "2021-02-15"})

    assert len(res.json) == 1
    assert res.json[0]["pickup_id"] == 'medicalPickupUUID'
    assert res.status_code == 200
