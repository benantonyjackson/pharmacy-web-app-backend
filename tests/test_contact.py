from . import auth


def test_not_authorised(client):
    res = client.get("/api/contact")
    assert res.status_code == 401
    assert "contact_id" not in str(res.json)


def test_contact_no_contact_id_parameter(client, db):
    # Record that should not be returned
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID", 12345678910, "email1", "addressline11", null,'
        ' "addressline31", "addressline41", "ABC DEF")')

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/contact", headers={'Authorization': "Bearer " + token})

    assert res.status_code == 400

    assert "phone_number" not in str(res.json)


def test_no_contacts_to_return(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/contact", headers={'Authorization': "Bearer " + token},
                     query_string={"contact_id": "example-contact-id"})

    assert res.status_code == 404
    assert "pickup_status" not in str(res.json)


def test_contact_id_not_found(client, db):
    # Record that should not be returned
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID", 12345678910, "email1", "addressline11", null,'
        ' "addressline31", "addressline41", "ABC DEF")')
    #Record that should not be returned
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID2", 01987654321, "email2", "addressline12", null,'
        ' "addressline32", "addressline42", "DEF ABC")')
    # Record that should not be returned
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID3", 07123456789, "email1", "addressline13", null,'
        ' "addressline34", "addressline44", "AA1 1AA")')

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/contact", headers={'Authorization': "Bearer " + token},
                     query_string={"contact_id": "example-contact-id"})

    assert "drug_id" not in str(res.json)
    assert res.status_code == 404


def test_retrieve_contact(client, db):
    # Record that should not be returned
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID", "12345678910", "email1", "addressline11", null,'
        ' "addressline31", "addressline41", "ABC DEF")')
    # Record that should be returned
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID2", "01987654321", "email2", "addressline12", null,'
        ' "addressline32", "addressline42", "DEF ABC")')
    # Record that should not be returned
    db.session.execute(
        'INSERT INTO contactdetails () VALUES ("contactDetailUUID3", "07123456789", "email1", "addressline13", null,'
        ' "addressline34", "addressline44", "AA1 1AA")')

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/contact", headers={'Authorization': "Bearer " + token},
                     query_string={"contact_id": "contactDetailUUID2"})

    assert res.status_code == 200

    assert res.json['contact_id'] == "contactDetailUUID2"
    assert res.json['phone_number'] == "01987654321"
    assert res.json['email_address'] == "email2"
    assert res.json['address_line_1'] == "addressline12"
    assert res.json['address_line_2'] is None
    assert res.json['address_line_3'] == "addressline32"
    assert res.json['address_line_4'] == "addressline42"
    assert res.json['postcode'] == "DEF ABC"
