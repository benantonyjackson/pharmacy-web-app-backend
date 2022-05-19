from . import auth


def foreign_key_entries(db):
    db.session.execute('INSERT INTO drugs () VALUES'
                       '("56f5dc7e-2843-4cd9-87e8-f19f92c4ad0e", "Drug 1"),'
                       '("fcc62716-5d81-4aa6-aab8-0468a50923fc", "Drug 2"),'
                       '("d99ac869-88c6-4467-a7ac-80d4e2895a91", "Drug 3");')

    db.session.execute('INSERT INTO contactdetails () VALUES'
                       '("1463ae92-1ede-4069-b483-84be677132b7", 12345678910, "email1", "addressline11", null, "addressline31", "addressline41", "ABC DEF"),'
                       '("f060e426-1943-4dbb-92e4-9c08d9540fa7", 09876543210, "email2", "addressline12", null, "addressline32", "addressline42", "DEF GHI"),'
                       '("1d46cb3a-266c-4d2f-944d-fade75b0a42e", 54321678910, "email3", "addressline13", null, "addressline33", "addressline43", "JKL MNO"),'
                       '("53a26750-b964-4b5c-97a6-0becf2c9cfaf", 67891054321, "email4", "addressline14", null, "addressline34", "addressline44", "PQR STU"),'
                       '("4264d731-0d61-4976-9a98-25c5c445b8fb", 12398746572, "email5", "addressline15", null, "addressline35", "addressline45", "WXY ABC"),'
                       '("805e924e-1451-4751-9437-a20cbd717afd", 15436726534, "email6", "addressline16", null, "addressline36", "addressline46", "GOO GOO");')

    db.session.execute('INSERT INTO sensitivities() '
                       'VALUES'
                       '("9db1906a-4dab-44b3-b6e1-8b4460cb9b62", "Water allergy",'
                       ' "What it says on the tin")')

    db.session.execute('INSERT INTO sensitivities() VALUES ("b9b7fc9d-df55-4ded-94ba-1b61498529cd", "Air allergy",'
                       ' "What it says on the tin")')

    db.session.execute('INSERT INTO sensitivities() VALUES ("24243d1e-597b-49fb-b625-e65c5b9037f1", '
                       '"Visible light allergy", "What it says on the tin")')

    db.session.execute('INSERT INTO gps () VALUES'
                       '("a01f82d6-192b-4c34-b0c1-83fbb3b05b8b", "Gp1", "53a26750-b964-4b5c-97a6-0becf2c9cfaf"),'
                       '("d87fdfe5-5945-4d5d-8a9f-06e153e6d709", "Gp2", "4264d731-0d61-4976-9a98-25c5c445b8fb"),'
                       '("f8905548-9f2b-4040-b84c-5b8f68320f81", "Gp3", "805e924e-1451-4751-9437-a20cbd717afd");')

    db.session.execute('INSERT INTO patients() VALUES'
                       '("a714ead6-a451-4d54-ae56-11e1df6ac032", "a01f82d6-192b-4c34-b0c1-83fbb3b05b8b", "9db1906a-4dab-44b3-b6e1-8b4460cb9b62", "Ben", "Jackson", "F", 12, "1463ae92-1ede-4069-b483-84be677132b7"),'
                       '("56ba0568-448d-42db-bec3-9a759d6f9908", "d87fdfe5-5945-4d5d-8a9f-06e153e6d709", "b9b7fc9d-df55-4ded-94ba-1b61498529cd", "Joe", "Blogs", "M", 18, "f060e426-1943-4dbb-92e4-9c08d9540fa7"),'
                       '("510b5ab9-3685-46ec-8082-3ef8ba848688", "f8905548-9f2b-4040-b84c-5b8f68320f81", "24243d1e-597b-49fb-b625-e65c5b9037f1", "John", "Smith", "M", 73, "1d46cb3a-266c-4d2f-944d-fade75b0a42e");')

    db.session.execute('INSERT INTO medicalpickups () VALUES'
                       '("91de0111-a5c7-4e38-bc6d-5935172c1c70", "a714ead6-a451-4d54-ae56-11e1df6ac032", "56f5dc7e-2843-4cd9-87e8-f19f92c4ad0e", 1, "2021-02-13", NOW(), 1, "AWAITING_PICKUP"),'
                       '("5d8caa1d-9580-4e68-89f3-ff3c23eb3e55", "56ba0568-448d-42db-bec3-9a759d6f9908", "fcc62716-5d81-4aa6-aab8-0468a50923fc", 1, "2021-02-13", NOW(), 1, "AWAITING_PICKUP"),'
                       '("4c826247-df94-4f8f-8a55-faf98a4912bd", "510b5ab9-3685-46ec-8082-3ef8ba848688", "d99ac869-88c6-4467-a7ac-80d4e2895a91", 1, "2021-02-13", NOW(), 1, "AWAITING_PICKUP");')

    db.session.execute('INSERT INTO standardtests ()'
                       'VALUES'
                       '("test1", "Blood test 1"),'
                       '("test2", "Blood test 2"),'
                       '("test3", "Blood test 3");')


def test_user_not_authorised(client):
    res = client.get("/api/pickup/authorised")
    assert res.status_code == 401
    assert "patient_id" not in str(res.json)


def test_no_pickup_id_parameter(client, db):
    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/pickup/authorised", headers={'Authorization': "Bearer " + token})

    assert res.status_code == 400

    assert "forename" not in str(res.json)


def test_pickup_has_no_required_tests(client, db):
    foreign_key_entries(db)

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/pickup/authorised", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_id": "5d8caa1d-9580-4e68-89f3-ff3c23eb3e55"})

    assert res.status_code == 200
    assert res.json['is_authorised']


def test_requirements_not_met(client, db):
    foreign_key_entries(db)

    db.session.execute('INSERT INTO requiredtests () VALUES'
                       '("requiredtest1", "56f5dc7e-2843-4cd9-87e8-f19f92c4ad0e", "test1", "non", 60),'
                       '("requiredtest2", "56f5dc7e-2843-4cd9-87e8-f19f92c4ad0e", "test2", "non", 30);')

    db.session.execute("INSERT INTO patienthistory () VALUES"
                       "('history1', 'a714ead6-a451-4d54-ae56-11e1df6ac032',  'test1', '2020-12-31', 1),"
                       "('history2', 'a714ead6-a451-4d54-ae56-11e1df6ac032', 'test2', '2020-12-31', 1);")

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/pickup/authorised", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_id": "91de0111-a5c7-4e38-bc6d-5935172c1c70"})

    assert res.status_code == 200
    assert not res.json['is_authorised']


def test_requirements_met_due_to_discretion(client, db):
    foreign_key_entries(db)

    db.session.execute('INSERT INTO requiredtests () VALUES'
                       '("requiredtest3", "d99ac869-88c6-4467-a7ac-80d4e2895a91", "test1", "non", 60),'
                       '("requiredtest4", "d99ac869-88c6-4467-a7ac-80d4e2895a91", "test2", "full", 30);')

    db.session.execute("INSERT INTO patienthistory () VALUES"
                       "('history3', '510b5ab9-3685-46ec-8082-3ef8ba848688',  'test1', '2020-12-31', 1),"
                       "('history4', '510b5ab9-3685-46ec-8082-3ef8ba848688', 'test2', '2020-12-31', 1);")

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/pickup/authorised", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_id": "4c826247-df94-4f8f-8a55-faf98a4912bd"})

    assert res.status_code == 200
    assert res.json['is_authorised']


def test_requirements_met(client, db):
    foreign_key_entries(db)

    db.session.execute('INSERT INTO requiredtests () VALUES'
                       '("requiredtest3", "d99ac869-88c6-4467-a7ac-80d4e2895a91", "test1", "non", 60),'
                       '("requiredtest4", "d99ac869-88c6-4467-a7ac-80d4e2895a91", "test2", "non", 90);')

    db.session.execute("INSERT INTO patienthistory () VALUES"
                       "('history3', '510b5ab9-3685-46ec-8082-3ef8ba848688',  'test1', '2020-12-31', 1),"
                       "('history4', '510b5ab9-3685-46ec-8082-3ef8ba848688', 'test2', '2020-12-31', 1);")

    token = auth.get_access_token(client, db, "test_user", "test_password", "technician")

    res = client.get("/api/pickup/authorised", headers={'Authorization': "Bearer " + token},
                     query_string={"pickup_id": "4c826247-df94-4f8f-8a55-faf98a4912bd"})

    assert res.status_code == 200
    assert res.json['is_authorised']
