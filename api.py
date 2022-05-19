from flask import Flask
from flask import Response
from flask import send_from_directory
from flask import request
import flask
import flask_sqlalchemy
import flask_praetorian
import json
import os
import uuid
import datetime
from twilio.rest import Client
import smtplib

statuses = ["unauthorised", "authorised"]

VALID_PICKUP_STATES = ["AWAITING_PHARMACIST_AUTHORISATION",
                           "AWAITING_CONFIRMATION",
                           "AWAITING_ASSEMBLY",
                           "AWAITING_COLLECTION",
                           "COLLECTED"]

db = flask_sqlalchemy.SQLAlchemy()
guard = flask_praetorian.Praetorian()


class Users(db.Model):
    userId = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(25))

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, userId):
        return cls.query.get(userId)

    @property
    def identity(self):
        return self.userId


class medicalpickups(db.Model):
    pickupid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    patientid = db.Column(db.String(36))
    drugid = db.Column(db.String(36))
    drugquantity = db.Column(db.Integer())
    scheduleddate = db.Column(db.Date())
    reviewdate = db.Column(db.Date())
    isauthorised = db.Column(db.Boolean())
    pickupstatus = db.Column(db.String(25))

    @classmethod
    def lookup(cls, pickupid):
        return cls.query.filter_by(pickupid=pickupid).one_or_none()

    @classmethod
    def identify(cls, pickupid):
        return cls.query.get(pickupid)

    @property
    def identity(self):
        return self.pickupid


class drugs(db.Model):
    drugid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))

    @classmethod
    def lookup(cls, drugid):
        return cls.query.filter_by(drugid=drugid).one_or_none()

    @classmethod
    def identify(cls, drugid):
        return cls.query.get(drugid)

    @property
    def identity(self):
        return self.drugid


class contactdetails(db.Model):
    contactdetailid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    phonenumber = db.Column(db.String(255))
    emailaddress = db.Column(db.String(255))
    addressline1 = db.Column(db.String(255))
    addressline2 = db.Column(db.String(255))
    addressline3 = db.Column(db.String(255))
    addressline4 = db.Column(db.String(255))
    postcode = db.Column(db.String(7))

    @classmethod
    def lookup(cls, contactdetailid):
        return cls.query.filter_by(contactdetailid=contactdetailid).one_or_none()

    @classmethod
    def identify(cls, contactdetailid):
        return cls.query.get(contactdetailid)

    @property
    def identity(self):
        return self.contactdetailid


class standardtests(db.Model):
    standardtestid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    testname = db.Column(db.String(255))

    @classmethod
    def lookup(cls, standardtestid):
        return cls.query.filter_by(standardtestid=standardtestid).one_or_none()

    @classmethod
    def identify(cls, standardtestid):
        return cls.query.get(standardtestid)

    @property
    def identity(self):
        return self.standardtestid


class patients(db.Model):
    patientid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    gpid = db.Column(db.String(36))
    sensitivityid = db.Column(db.String(36))
    forename = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    sex = db.Column(db.String(1))
    age = db.Column(db.Integer())
    contactdetailid = db.Column(db.String(36))

    @classmethod
    def lookup(cls, patientid):
        return cls.query.filter_by(patientid=patientid).one_or_none()

    @classmethod
    def identify(cls, patientid):
        return cls.query.get(patientid)

    @property
    def identity(self):
        return self.patientid


class gps(db.Model):
    gpid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    contactdetailid = db.Column(db.String(36))

    @classmethod
    def lookup(cls, gpid):
        return cls.query.filter_by(gpid=gpid).one_or_none()

    @classmethod
    def identify(cls, gpid):
        return cls.query.get(gpid)

    @property
    def identity(self):
        return self.gpid


class sensitivities(db.Model):
    sensitivityid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))

    @classmethod
    def lookup(cls, sensitivityid):
        return cls.query.filter_by(sensitivityid=sensitivityid).one_or_none()

    @classmethod
    def identify(cls, sensitivityid):
        return cls.query.get(sensitivityid)

    @property
    def identity(self):
        return self.sensitivityid


class requiredtests(db.Model):
    requiredtestid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    drugid = db.Column(db.String(36))
    standardtestid = db.Column(db.String(36))
    pharmacistdiscretion = db.Column(db.String(255))
    testfrequency = db.Column(db.Integer())

    @classmethod
    def lookup(cls, requiredtestid):
        return cls.query.filter_by(requiredtestid=requiredtestid).one_or_none()

    @classmethod
    def identify(cls, requiredtestid):
        return cls.query.get(requiredtestid)

    @property
    def identity(self):
        return self.requiredtestid


class patienthistory(db.Model):
    patienthistoryid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    patientid = db.Column(db.String(36))
    standardtestid = db.Column(db.String(36))
    dateconducted = db.Column(db.Date())
    ispassed = db.Column(db.Boolean())

    @classmethod
    def lookup(cls, patienthistoryid):
        return cls.query.filter_by(pickupId=patienthistoryid).one_or_none()

    @classmethod
    def identify(cls, patienthistoryid):
        return cls.query.get(patienthistoryid)

    @property
    def identity(self):
        return self.patienthistoryid


class testrequests(db.Model):
    testrequestid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    daterequested = db.Column(db.Date())
    standardtestid = db.Column(db.String(36))
    patientid = db.Column(db.String(36))
    gpid = db.Column(db.String(36))

    @classmethod
    def lookup(cls, testrequestid):
        return cls.query.filter_by(testrequestid=testrequestid).one_or_none()

    @classmethod
    def identify(cls, testrequestid):
        return cls.query.get(testrequestid)

    @property
    def identity(self):
        return self.testrequestid


class repeatprescription(db.Model):
    repeatprescriptionid = db.Column(db.String(36), primary_key=True, default=uuid.uuid4)
    drugid = db.Column(db.String(36))
    patientid = db.Column(db.String(36))
    drugquantity = db.Column(db.Integer())
    medicationstartdate = db.Column(db.Date())
    reviewdate = db.Column(db.Date())
    maximumissues = db.Column(db.Integer())
    issuefrequency = db.Column(db.Integer())
    pickupcreated = db.Column(db.Integer())

    @classmethod
    def lookup(cls, repeatprescriptionid):
        return cls.query.filter_by(pickupid=repeatprescriptionid).one_or_none()

    @classmethod
    def identify(cls, repeatprescriptionid):
        return cls.query.get(repeatprescriptionid)

    @property
    def identity(self):
        return self.repeatprescriptionid


def init():
    # Initialize the flask-praetorian instance for the app
    guard.init_app(app, Users)

    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://" + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_URL + "/" + DB_NAME
    db.init_app(app)

    # Add a default user
    with app.app_context():
        db.create_all()
        if db.session.query(Users).filter_by(username=DEFAULT_ACCOUNT_USERNAME).count() < 1:
            db.session.add(Users(
              username=DEFAULT_ACCOUNT_USERNAME,
              password=guard.hash_password(DEFAULT_ACCOUNT_PASSWORD),
              role=DEFAULT_ACCOUNT_ROLE
                ))
        db.session.commit()


# Initialise flask app
app = Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.debug = True
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}

# Initialize environment variables
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_URL = os.environ.get('DB_URL')
DB_NAME = os.environ.get('DB_NAME')
DEFAULT_ACCOUNT_USERNAME = os.environ.get('DEFAULT_ACCOUNT_USERNAME')
DEFAULT_ACCOUNT_PASSWORD = os.environ.get('DEFAULT_ACCOUNT_PASSWORD')
DEFAULT_ACCOUNT_ROLE = os.environ.get('DEFAULT_ACCOUNT_ROLE')
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
FROM_NUMBER = os.environ['TWILIO_FROM_NUMBER']
REQUEST_EMAIL_ADDRESS = os.environ['REQUEST_EMAIL_ADDRESS']
REQUEST_PASSWORD = os.environ['REQUEST_PASSWORD']
init()


def get_default_response(body={}):
    res = Response()
    res.headers['Content-type'] = "application/json"
    res.data = json.dumps(body)
    return res


@app.route('/')
def index():
    file = open("index.html", "r")
    return file.read()


@app.route('/api/swagger/<path:path>')
def send_swagger_files(path):
    return send_from_directory('swagger', path)


# Returns YAML documentation
@app.route("/api/spec")
def spec():
    file = open("swagger/index.html", "r")
    return file.read()


@app.route('/api/login', methods=['POST'])
def login():
    req = flask.request.get_json(force=True)
    username = req.get('username', None)
    password = req.get('password', None)
    user = guard.authenticate(username, password)
    ret = {'access_token': guard.encode_jwt_token(user)}
    return ret, 200


# Endpoint for unit tests to verify roles are working as expected
@app.route('/api/test/auth', methods=['GET'])
@flask_praetorian.auth_required
def test_auth():
    role = flask_praetorian.current_user().role
    return get_default_response({"role": role})


@app.route('/api/refresh', methods=['POST'])
def refresh():
    old_token = flask.request.get_data()
    new_token = guard.refresh_jwt_token(old_token)
    ret = {'access_token': new_token}
    return ret, 200


def generate_pickups_from_repeat_prescriptions():
    # Checks for repeat prescriptions that have not been converted to medical pickups
    query = db.session.query(repeatprescription).filter_by(pickupcreated=0)

    if query.count() > 0:
        for repeat_prescription in query:
            generate_pickup_from_repeat_prescription(repeat_prescription)


def generate_pickup_from_repeat_prescription(repeat_prescription):
    pickup_date = repeat_prescription.medicationstartdate

    # Calculate when prescription ends
    if repeat_prescription.maximumissues is None:
        end_date = repeat_prescription.reviewdate
    elif repeat_prescription.medicationstartdate is None:
        end_date = pickup_date + datetime.timedelta(
            days=(repeat_prescription.maximumissues * repeat_prescription.issuefrequency))
    else:
        issue_end_date = pickup_date + datetime.timedelta(
            days=(repeat_prescription.maximumissues * repeat_prescription.issuefrequency))

        end_date = min(issue_end_date, repeat_prescription.reviewdate)

    # Generates individual pickups
    while pickup_date < end_date:
        # Create new pickup
        pickup = medicalpickups(
            patientid=repeat_prescription.patientid,
            drugid=repeat_prescription.drugid,
            drugquantity=repeat_prescription.drugquantity,
            scheduleddate=pickup_date,
            reviewdate=end_date,
            isauthorised=True,
            pickupstatus="AWAITING_PHARMACIST_AUTHORISATION"
        )

        db.session.add(pickup)

        # Increments pickup date
        pickup_date = pickup_date + datetime.timedelta(days=repeat_prescription.issuefrequency)
    
    repeat_prescription.pickupcreated = 1
    db.session.commit()


@app.route('/api/pickups', methods=['GET'])
@flask_praetorian.auth_required
def get_pickups():
    generate_pickups_from_repeat_prescriptions()
    arr = []

    pickup_status = request.args.get("pickup_status")
    scheduled_before = request.args.get("scheduled_before")

    if pickup_status is None:
        return get_default_response({"message": "Parameter required: status",
                                     "status_code": 400}), 400

    if pickup_status not in VALID_PICKUP_STATES:
        return get_default_response({"message": pickup_status + " Is not a valid status. The list of valid "
                                                                "status is " + str(VALID_PICKUP_STATES),
                                     "status_code": 400}), 400

    if scheduled_before is None:
        return get_default_response({"message": "Parameter required: scheduled_before",
                                     "status_code": 400}), 400

    query = db.session.query(medicalpickups).filter(
        medicalpickups.pickupstatus == pickup_status,
        medicalpickups.scheduleddate <= scheduled_before).order_by(medicalpickups.scheduleddate)

    for instance in query:
        arr.append({"pickup_id": instance.pickupid,
                    "patient_id": instance.patientid,
                    "drug_id": instance.drugid,
                    "drug_quantity": instance.drugquantity,
                    "scheduled_date": str(instance.scheduleddate),
                    "review_date": str(instance.reviewdate),
                    "is_authorised": statuses[instance.isauthorised],
                    "pickup_status": instance.pickupstatus})
    return get_default_response(arr)


@app.route('/api/pickup', methods=['GET'])
@flask_praetorian.auth_required
def get_pickup():
    if request.args.get("pickup_id") is None:
        return get_default_response({"message": "Parameter required: pickup_id",
                                     "status_code": 400}), 400

    query = db.session.query(medicalpickups).filter_by(pickupid=request.args.get("pickup_id"))

    if query.count() < 1:
        return get_default_response({"message": "No pick up with that ID could be found",
                                     "status_code": 404}), 404

    instance = query.first()

    return_value = {"pickup_id": instance.pickupid,
                    "patient_id": instance.patientid,
                    "drug_id": instance.drugid,
                    "drug_quantity": instance.drugquantity,
                    "scheduled_date": str(instance.scheduleddate),
                    "review_date": str(instance.reviewdate),
                    "is_authorised": statuses[instance.isauthorised],
                    "pickup_status": instance.pickupstatus}

    return get_default_response(return_value)


@app.route('/api/pickup/status', methods=['PATCH'])
@flask_praetorian.auth_required
def update_pickup_status():
    if request.args.get("pickup_id") is None:
        return get_default_response({"message": "Parameter required: pickup_id",
                                     "status_code": 400}), 400

    pickup_id = request.args.get("pickup_id")

    if request.json is None:
        return get_default_response({"message": "JSON body required",
                                     "status_code": 400}), 400

    if "status" not in request.json:
        return get_default_response({"message": "Field required in JSON body: status",
                                     "status_code": 400}), 400

    if request.json['status'] not in VALID_PICKUP_STATES:
        return get_default_response({"message": request.json['status'] + " Is not a valid status. This list of valid "
                                                                         "status are " + str(VALID_PICKUP_STATES),
                                     "status_code": 400}), 400

    query = db.session.query(medicalpickups).filter_by(pickupid=pickup_id)
    pickup = query.first()

    if flask_praetorian.current_user().role != "pharmacist":
        if pickup.pickupstatus != "AWAITING_ASSEMBLY" or request.json['status'] != "AWAITING_COLLECTION":
            return get_default_response({"message": "Pharmacist role required to update pickup status",
                                         "status_code": 401}), 401

    if query.count() < 1:
        return get_default_response({"message": "No pickup with that ID could be found",
                                     "status_code": 404}), 404

    if pickup.pickupstatus == "AWAITING_PHARMACIST_AUTHORISATION":
        authorised = json.loads(is_authorised(pickup_id).data)
        if not authorised['is_authorised']:
            return get_default_response({"message": "Cannot update status as pickup has unmet requirements",
                                         "status_code": 400}), 400

    if request.json['status'] == 'AWAITING_CONFIRMATION':
        drug_name = db.session.query(drugs).filter_by(drugid=pickup.drugid).first().name
        message_body = "Our records show that you are due to run out" \
                       " of " + drug_name + " soon. Please contact your pharmacy to arrange pick up."

        send_message(pickup_id, message_body)

    if request.json['status'] == 'AWAITING_COLLECTION':
        drug_name = db.session.query(drugs).filter_by(drugid=pickup.drugid).first().name
        message_body = drug_name + " is now ready for collection."

        send_message(pickup_id, message_body)

    pickup.pickupstatus = request.json['status']
    db.session.commit()
    return get_default_response({"message": "Successfully updated pickup status"})


@app.route('/api/drug', methods=['GET'])
@flask_praetorian.auth_required
def get_drug():
    if request.args.get("drug_id") is None:
        return get_default_response({"message": "Parameter required: drug_id",
                                     "status_code": 400}), 400

    query = db.session.query(drugs).filter_by(drugid=request.args.get("drug_id"))
    if query.count() < 1:
        return get_default_response({"message": "No drug with that ID could be found",
                                     "status_code": 404}), 404
    instance = query.first()
    return_value = {"drug_id": instance.drugid,
                    "name": instance.name}
    return get_default_response(return_value)


@app.route('/api/test', methods=['GET'])
@flask_praetorian.auth_required
def get_test():
    if request.args.get("test_id") is None:
        return get_default_response({"message": "Parameter required: test_id",
                                     "status_code": 400}), 400

    query = db.session.query(standardtests).filter_by(standardtestid=request.args.get("test_id"))

    if query.count() < 1:
        return get_default_response({"message": "No test with that ID could be found",
                                     "status_code": 404}), 404

    instance = query.first()

    return_value = {
                    "test_id": instance.standardtestid,
                    "name": instance.testname,
    }

    return get_default_response(return_value)


@app.route('/api/contact', methods=['GET'])
@flask_praetorian.auth_required
def get_contact():
    if request.args.get("contact_id") is None:
        return get_default_response({"message": "Parameter required: contact_id",
                                     "status_code": 400}), 400

    query = db.session.query(contactdetails).filter_by(contactdetailid=request.args.get("contact_id"))

    if query.count() < 1:
        return get_default_response({"message": "No contact with that ID could be found",
                                     "status_code": 404}), 404

    instance = query.first()

    return_value = {
        "contact_id": instance.contactdetailid,
        "phone_number": instance.phonenumber,
        "email_address": instance.emailaddress,
        "address_line_1": instance.addressline1,
        "address_line_2": instance.addressline2,
        "address_line_3": instance.addressline3,
        "address_line_4": instance.addressline4,
        "postcode": instance.postcode,
    }

    return get_default_response(return_value)


@app.route('/api/gp', methods=['GET'])
@flask_praetorian.auth_required
def get_gp():
    if request.args.get("gp_id") is None:
        return get_default_response({"message": "Parameter required: gp_id",
                                     "status_code": 400}), 400

    query = db.session.query(gps).filter_by(gpid=request.args.get("gp_id"))

    if query.count() < 1:
        return get_default_response({"message": "No gp with that ID could be found",
                                     "status_code": 404}), 404

    instance = query.first()

    return_value = {
        "gp_id": instance.gpid,
        "name": instance.name,
        "contact_id": instance.contactdetailid
    }

    return get_default_response(return_value)


@app.route('/api/patient', methods=['GET'])
@flask_praetorian.auth_required
def get_patient():
    if request.args.get("patient_id") is None:
        return get_default_response({"message": "Parameter required: patient_id",
                                     "status_code": 400}), 400

    query = db.session.query(patients).filter_by(patientid=request.args.get("patient_id"))

    if query.count() < 1:
        return get_default_response({"message": "No patient with that ID could be found",
                                     "status_code": 404}), 404

    instance = query.first()

    return_value = {
        "patient_id": instance.patientid,
        "gp_id": instance.gpid,
        "sensitivity_id": instance.sensitivityid,
        "forename": instance.forename,
        "surname": instance.surname,
        "sex": instance.sex,
        "age": instance.age,
        "contact_id": instance.contactdetailid,
    }

    return get_default_response(return_value)


@app.route('/api/sensitivity', methods=['GET'])
@flask_praetorian.auth_required
def get_sensitivity():
    if request.args.get("sensitivity_id") is None:
        return get_default_response({"message": "Parameter required: sensitivity_id",
                                     "status_code": 400}), 400

    query = db.session.query(sensitivities).filter_by(sensitivityid=request.args.get("sensitivity_id"))

    if query.count() < 1:
        return get_default_response({"message": "No sensitivity with that ID could be found",
                                     "status_code": 404}), 404

    instance = query.first()

    return_value = {
        "sensitivity_id": instance.sensitivityid,
        "name": instance.name,
        "description": instance.description
    }

    return get_default_response(return_value)


# Code snippet from https://www.afternerd.com/blog/how-to-send-an-email-using-python-and-smtplib/
def send_email(email_address, message, subject):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(REQUEST_EMAIL_ADDRESS, REQUEST_PASSWORD)
        server.sendmail(
            "pharmacyaad@gmail.com",
            email_address,
            "Subject: " + subject + "\n\n" + message)
        server.quit()
    except Exception:
        pass


@app.route('/api/bloodwork/request', methods=['POST'])
@flask_praetorian.auth_required
def request_bloodwork():
    if request.args.get("patient_id") is None:
        return get_default_response({"message": "Parameter required: patient_id",
                                     "status_code": 400}), 400
    if request.args.get("standard_test_id") is None:
        return get_default_response({"message": "Parameter required: standard_test_id",
                                     "status_code": 400}), 400
    if request.args.get("message") is None:
        return get_default_response({"message": "Parameter required: message",
                                     "status_code": 400}), 400

    patientRecord = patients.lookup(request.args.get("patient_id"))
    patientGp = patientRecord.gpid

    gp_record = gps.lookup(patientRecord.gpid)
    gp_contact = contactdetails.lookup(gp_record.contactdetailid)

    test_name = standardtests.lookup(request.args.get("standard_test_id")).testname

    send_email(gp_contact.emailaddress,
               "This is a formal request for " + test_name + "\n\n"
               + "Patient details: \n\n" +
               "Patient ID: " + patientRecord.patientid + "\n" +
               "forename: " + patientRecord.forename + "\n" +
               "surname: " + patientRecord.surname + "\n" +
               "sex: " + patientRecord.sex + "\n" +
               "age: " + str(patientRecord.age) + "\n\n\n" +
               "Pharmacist notes:\n"
               + request.args.get("message"), "New test request")

    newRecord = testrequests(daterequested = datetime.datetime.now(), standardtestid = request.args.get("standard_test_id"), patientid = request.args.get("patient_id"), gpid = patientGp)
    db.session.add(newRecord)
    db.session.commit()
    return get_default_response()


def is_authorised(pickup_id):
    if pickup_id is None:
        return get_default_response({"message": "Parameter required: pickup_id",
                                     "status_code": 400}), 400

    query = db.session.query(medicalpickups).filter_by(pickupid=pickup_id)

    if query.count() < 1:
        return get_default_response({"message": "No pick up with that ID could be found",
                                     "status_code": 404}), 404

    pickup = query.first()

    drug_id = pickup.drugid
    patient_id = pickup.patientid
    scheduled_date = pickup.scheduleddate

    requirements = []

    authorised = True

    # Loops through all test requirements
    for requirement in db.session.query(requiredtests).filter_by(drugid=drug_id):
        minimum_last_test_date = scheduled_date - datetime.timedelta(days=requirement.testfrequency)

        # Queries the database for tests in the patients medical history that would match the requirements for the drug
        query2 = db.session.query(patienthistory).filter(patienthistory.patientid == patient_id,
                                                         patienthistory.standardtestid == requirement.standardtestid,
                                                         patienthistory.dateconducted > minimum_last_test_date)
        if query2.count() > 0:
            requirement_met = "Yes"
        else:
            requirement_met = "No"
            # If pharmacist has discretion to authorise pickup without test then requirements is considered to be met
            if requirement.pharmacistdiscretion == "non":
                # If any of the requirements are not met then the pharmacist cannot authorise the pickup
                authorised = False

        requirements.append({"requirement_id": requirement.requiredtestid,
                             "drug_id": requirement.drugid,
                             "test_id": requirement.standardtestid,
                             "pharmacist_discretion": requirement.pharmacistdiscretion,
                             "minimum_last_test_date": str(minimum_last_test_date),
                             "requirement_met": requirement_met})

    return get_default_response({"is_authorised": authorised, "requirements": requirements})


@app.route('/api/pickup/authorised', methods=['GET'])
@flask_praetorian.auth_required
def get_pickup_authorised():
    return is_authorised(request.args.get("pickup_id"))


def send_message(pickup_id, message_body):
    query = db.session.query(medicalpickups).filter_by(pickupid=pickup_id)

    if query.count() < 1:
        return get_default_response({"message": "No pick up with that ID could be found",
                                     "status_code": 404}), 404
    try:

        query = db.session.query(patients).filter_by(patientid=query.first().patientid)

        contact_details = db.session.query(contactdetails).filter_by(
            contactdetailid=query.first().contactdetailid).first()
    except Exception:
        get_default_response({"message": "An error occurred when trying to fetch patient contact details"}), 400

    # Code snippet from https://www.twilio.com/docs/sms/quickstart/python
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=message_body,
            from_=FROM_NUMBER,
            to=contact_details.phonenumber
        )
    except Exception:
        return get_default_response({"message": "An error occurred when trying to send the message to the patient"}),\
               400

    return get_default_response({"phone": contact_details.phonenumber, "email": contact_details.emailaddress,
                                 "message": message_body})


@app.route('/api/send/sms', methods=['POST'])
@flask_praetorian.auth_required
def send_pickup_alert():
    if request.args.get("pickup_id") is None:
        return get_default_response({"message": "Parameter required: pickup_id",
                                     "status_code": 400}), 400

    if "message" not in request.json:
        return get_default_response({"message": "Field required in JSON body: message",
                                     "status_code": 400}), 400

    pickup_id = request.args.get("pickup_id")
    message_body = request.json['message']

    return send_message(pickup_id, message_body)
