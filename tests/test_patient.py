from . import auth


def test_not_authorised(client):
    res = client.get("/api/patient")
    assert res.status_code == 401
    assert "patient_id" not in str(res.json)


def test_no_patient_id_parameter(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/patient", headers={'Authorization': "Bearer " + token})

    assert res.status_code == 400

    assert "forename" not in str(res.json)


def test_no_patients_to_return(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/patient", headers={'Authorization': "Bearer " + token},
                     query_string={"patient_id": "patient-id"})

    assert res.status_code == 404
    assert "forename" not in str(res.json)


def test_patient_id_not_found(client, db):
    # Records to accommodate for foreign key constraints
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID", 12345678910, "email1", "addressline11", null,'
        ' "addressline31", "addressline41", "ABC DEF")')

    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID", "Gp1", "contactDetailUUID")')
    db.session.execute(
        'INSERT INTO sensitivities() VALUES ("sensitivityUUID", "Water allergy", "What it says on the tin")')

    # Record that should not be returned
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID", "gpsUUID", "sensitivityUUID", "Ben", "Jackson", "F",'
        ' 12, "contactDetailUUID")')
    # Record that should not be returned
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID2", "gpsUUID", "sensitivityUUID", "Ben2", "Jackson2", "F",'
        ' 12, "contactDetailUUID")')
    # Record that should not be returned
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID3", "gpsUUID", "sensitivityUUID", "Ben2", "Jackson2", "F",'
        ' 12, "contactDetailUUID")')

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/patient", headers={'Authorization': "Bearer " + token},
                     query_string={"patient_id": "sdasdasdsa"})

    assert "forename" not in str(res.json)
    assert res.status_code == 404


def test_patient_successfully_retrieved(client, db):
    # Records to accommodate for foreign key constraints
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID", 12345678910, "email1", "addressline11", null,'
        ' "addressline31", "addressline41", "ABC DEF")')

    db.session.execute('INSERT INTO gps () VALUES ("gpsUUID", "Gp1", "contactDetailUUID")')
    db.session.execute(
        'INSERT INTO sensitivities() VALUES ("sensitivityUUID", "Water allergy", "What it says on the tin")')

    # Record that should not be returned
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID", "gpsUUID", "sensitivityUUID", "Ben", "Jackson", "F",'
        ' 12, "contactDetailUUID")')
    # Record that should  be returned
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID2", "gpsUUID", "sensitivityUUID", "Ben2", "Jackson2", "F",'
        ' 12, "contactDetailUUID")')
    # Record that should not be returned
    db.session.execute(
        'INSERT INTO patients() VALUES ("patientUUID3", "gpsUUID", "sensitivityUUID", "Ben2", "Jackson2", "F",'
        ' 12, "contactDetailUUID")')

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/patient", headers={'Authorization': "Bearer " + token},
                     query_string={"patient_id": "patientUUID2"})

    assert res.status_code == 200

    assert res.json['patient_id'] == "patientUUID2"
    assert res.json['gp_id'] == "gpsUUID"
    assert res.json['sensitivity_id'] == "sensitivityUUID"
    assert res.json['forename'] == "Ben2"
    assert res.json['surname'] == "Jackson2"
    assert res.json['sex'] == "F"
    assert res.json['age'] == 12
    assert res.json['contact_id'] == "contactDetailUUID"
