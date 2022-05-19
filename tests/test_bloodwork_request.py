from . import auth
from api import testrequests


def test_not_authorised(client):
    res = client.post("/api/bloodwork/request")
    assert res.status_code == 401


def test_bloodwork_request_no_patient_id(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "pharmacist")
    res = client.post("/api/bloodwork/request", headers={'Authorization': "Bearer " + token},
        query_string={'standard_test_id': "test1", 'message': "message"})
    assert res.status_code == 400


def test_bloodwork_request_no_standard_test_id(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "pharmacist")
    res = client.post("/api/bloodwork/request", headers={'Authorization': "Bearer " + token},
        query_string={'patient_id': "patient1", 'message': "message"})
    assert res.status_code == 400


def test_bloodwork_request_no_message(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "pharmacist")
    res = client.post("/api/bloodwork/request", headers={'Authorization': "Bearer " + token},
        query_string={'patient_id': "patient1", 'standard_test_id': "standardTest1"})
    assert res.status_code == 400


def test_request_successful(client, db):
    db.session.execute('INSERT INTO contactdetails () VALUES ("contact1", 12345678910, "email1", "addressline11", null, "addressline31", "addressline41", "ABC DEF")')
    db.session.execute('INSERT INTO contactdetails () VALUES ("contact2", 09876543210, "email2", "addressline12", null, "addressline32", "addressline42", "DEF GHI")')
    db.session.execute('INSERT INTO gps () VALUES ("gp1", "Gp1", "contact1")')
    db.session.execute('INSERT INTO sensitivities() VALUES ("sensitivity1", "Water allergy", "What it says on the tin")')
    db.session.execute('INSERT INTO patients() VALUES ("patient1", "gp1", "sensitivity1", "Ben", "Jackson", "F", 12, "contact2")')
    db.session.execute('INSERT INTO standardtests() VALUES ("standardTest1", "bloodwork")')
    token = auth.get_access_token(client, db, "test_user", "test_password", "pharmacist")
    res = client.post("/api/bloodwork/request", headers={'Authorization': "Bearer " + token},
        query_string={'patient_id': "patient1", 'standard_test_id': "standardTest1", 'message': "message"})
    assert db.session.query(testrequests).count() > 0
    assert res.status_code == 200