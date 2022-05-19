import api


def successful_login(client, db, username, password, role):
    db.session.add(api.Users(username=username,
                             password=api.guard.hash_password(password),
                             role=role))

    body = {"username": username, "password": password}

    return client.post('/api/login', json=body)


def login_bad_username(client, db, username, password, role):
    db.session.add(api.Users(username=username,
                             password=api.guard.hash_password(password),
                             role=role))

    body = {"username": username + "-", "password": password}

    return client.post('/api/login', json=body)


def login_bad_password(client, db, username, password, role):
    db.session.add(api.Users(username=username,
                             password=api.guard.hash_password(password),
                             role=role))

    body = {"username": username, "password": password + "-"}

    return client.post('/api/login', json=body)


def get_access_token(client, db, username, password, role):
    return successful_login(client, db, username, password, role).json['access_token']
