import pytest

from api import app as _app
from api import db as _db
from api import medicalpickups
import api


@pytest.fixture(scope='function')
def client(app):
    """Get a test client for your Flask app"""
    return app.test_client()


@pytest.fixture(scope='function')
def app():
    with _app.app_context():
        yield _app


@pytest.fixture(scope='function')
def db(app):
    _db.session.query(medicalpickups).delete()
    _db.session.query(api.patienthistory).delete()
    _db.session.query(api.testrequests).delete()
    _db.session.query(api.patients).delete()
    _db.session.query(api.gps).delete()
    _db.session.query(api.sensitivities).delete()
    # Drugs_drugcollisions
    # collisions
    _db.session.query(api.requiredtests).delete()
    _db.session.query(api.drugs).delete()
    _db.session.query(api.Users).delete()
    _db.session.query(api.contactdetails).delete()
    _db.session.query(api.standardtests).delete()

    yield _db
