from datetime import datetime, timedelta
from functools import wraps
from os import environ

import requests
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, verify_jwt_in_request, \
    get_jwt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound

# load environment variables from .env file
load_dotenv(".env")
GMAIL_API_URL = environ.get('GMAIL_API_URL')

BASIC_USER = "1"
ADMIN_USER = "2"


# Here is a custom decorator that verifies the JWT is present in the request,
# as well as insuring that the JWT has a claim indicating that this user is
# an administrator
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if claims.get('is_admin', None):
                return fn(*args, **kwargs)
            else:
                return error_response("Admin privileges required", 403)

        return decorator

    return wrapper


def init_application():
    app = Flask(__name__)
    # TODO: ensure that env variables are defined
    db_user = environ.get('DB_USER')
    db_name = environ.get('DB_NAME')
    db_password = environ.get('DB_PASSWORD')
    db_host = environ.get('DB_HOST')
    db_port = environ.get('DB_PORT')
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    secret_key = environ.get('SECRET_KEY')
    app.config['SECRET_KEY'] = secret_key
    return app


application = init_application()
jwt = JWTManager(application)

db = SQLAlchemy(application)
bcrypt = Bcrypt(application)


class Employee(db.Model):
    __tablename__ = 'employees'

    employee_id = db.Column(db.Integer, primary_key=True)
    employee_first_name = db.Column(db.String(255))
    employee_middle_name = db.Column(db.String(255))
    employee_last_name = db.Column(db.String(255))


class EmployerRelation(db.Model):
    __tablename__ = 'employer_relations'

    employer_relation_id = db.Column(db.Integer, primary_key=True)
    parent_employer_id = db.Column(db.Integer)
    child_employer_id = db.Column(db.Integer)
    employer_relation_type = db.Column(db.String(255))
    employer_relation_start_date = db.Column(db.String(10))


class Employer(db.Model):
    __tablename__ = 'employers'

    employer_id = db.Column(db.Integer, primary_key=True)
    employer_name = db.Column(db.String(255))
    employer_addr_line_1 = db.Column(db.String(255))
    employer_addr_line_2 = db.Column(db.String(255))
    employer_addr_city = db.Column(db.String(255))
    employer_addr_state = db.Column(db.String(255))
    employer_addr_zip_code = db.Column(db.String(255))
    employer_founded_date = db.Column(db.String(10))
    employer_dissolved_date = db.Column(db.String(10))
    employer_bankruptcy_date = db.Column(db.String(10))
    employer_industry_sector_code = db.Column(db.Integer)
    employer_status = db.Column(db.String(255))
    employer_legal_status = db.Column(db.String(255))


class Employment(db.Model):
    __tablename__ = 'employments'

    employment_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    employer_id = db.Column(db.Integer)
    job_title = db.Column(db.String(255))
    start_date = db.Column(db.String(10))
    end_date = db.Column(db.String(10))


class NAICSCode(db.Model):
    __tablename__ = 'naics_codes'

    naics_code_id = db.Column(db.Integer, primary_key=True)
    naics_sector_code = db.Column(db.Integer)
    naics_sector_definition = db.Column(db.String(255))
    naics_release_year = db.Column(db.String(4))


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_first_name = db.Column(db.String(255))
    user_last_name = db.Column(db.String(255))
    email_address = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    pending_registr_expiry_datetime = db.Column(db.DateTime)
    access_permissions = db.Column(db.Integer)


class InternalServerError(Exception):
    pass


class EmailSendingError(Exception):
    pass


def error_response(error_message, error_code):
    """
    Create an error response with an error message and a status code.

    :param error_message: The error message to include in the response.
    :param error_code: The HTTP status code for the response.

    :return: A JSON response with the provided error message and status code.
    """
    response_data = {'error': error_message}
    return jsonify(response_data), error_code


def success_response(message, success_code, data=None):
    """
    Create a success response with a message, optional data, and a status code.

    :param message: A message to include in the response.
    :param success_code: The HTTP status code for the response.
    :param data: Optional data to include in the response (default is None).

    :return: A JSON response with the provided message, optional data, and status code.
    """
    response_data = {'message': message}

    if data is not None:
        response_data['data'] = data

    return jsonify(response_data), success_code


def send_verification_email(email, first_name):
    """
    Send a verification email to the given email address.

    :param email: The recipient's email address.
    :param first_name: The recipient's first name.

    :raises InternalServerError: If there is an internal server error, such as missing environment variables.
    :raises EmailSendingError: If there is an error while sending the email through the external service.

    Note that this function does not return any values upon success but raises exceptions when errors occur.
    """
    api_url = environ.get("API_URL")
    email_admin_token = environ.get("EMAIL_ADMIN_TOKEN")

    if not api_url or not email_admin_token:
        raise InternalServerError("Internal server error")

    # Define amount of time before token expires
    expires = timedelta(hours=72)
    verification_token = create_access_token(identity=email, expires_delta=expires)
    verification_url = f"{api_url}/verify?jwt={verification_token}"

    # Define the data you want to send in the request
    data = {
        'email': email,
        'verification_url': verification_url,
        'first_name': first_name,
        'admin_token': email_admin_token
    }

    try:
        # Send the POST request with the form data
        if not environ.get("GMAIL_API_URL"):
            raise InternalServerError("Internal server error")

        response = requests.post(environ.get("GMAIL_API_URL"), data=data)

        # Check the response status code for errors and raise EmailSendingError if necessary
        if response.status_code != 200:
            raise EmailSendingError("Failed to send email")

    except requests.exceptions.RequestException as e:
        raise EmailSendingError("Something went wrong sending the email")


@application.route('/employers', methods=['GET'])
@jwt_required()
def get_all_employers():
    # Execute the SQL query
    employers = Employer.query.all()

    # # Convert results to list of dictionaries
    results = [{"id": e.employer_id,
                "name": e.employer_name,
                "address": {
                    "line1": e.employer_addr_line_1,
                    "line2": e.employer_addr_line_2,
                    "city": e.employer_addr_city,
                    "state": e.employer_addr_state,
                    "zipCode": e.employer_addr_zip_code,
                },
                "foundedDate": e.employer_founded_date,
                "dissolvedDate": e.employer_dissolved_date,
                "bankruptcyDate": e.employer_bankruptcy_date,
                "industrySectorCode": e.employer_industry_sector_code,
                "status": e.employer_status,
                "legalStatus": e.employer_legal_status
                } for e in employers]
    return success_response(f"{len(results)} employers fetched", 200, results)


@application.route('/verify', methods=['GET'])
@jwt_required(locations=['query_string'])
def verify_user_account():
    try:
        email = get_jwt_identity()
        user = User.query.filter_by(email_address=email).first()
        user.access_permissions = BASIC_USER
        db.session.commit()

        # TODO: return an HTML view here
        return f"<div>" \
               f"<h1>Email {email} has been successfully verified</h1>" \
               f"<p>You can now login to your CELDV account</p>" \
               f"</div>"
    except NoResultFound:
        return error_response("Could not verify email. Try registering first", 400)

    except RuntimeError:
        return error_response("Internal server error", 500)


@application.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        user_first_name = data.get("user_first_name", None)
        user_last_name = data.get("user_last_name", None)
        email = data.get("email", None)
        password = data.get("password", None)

        if not email or not password or not user_first_name or not user_last_name:
            return error_response("Required arguments missing", 400)

        email_info = validate_email(email, check_deliverability=False)
        email = email_info.normalized

        # Check if registration email already exists in backend_test.users
        existing_user = User.query.filter_by(email_address=email).first()

        if existing_user:
            # CASE 1: Record with matching email exists and user is not verified (i.e., access_permissions is Null)
            if existing_user.access_permissions is None:
                # Resend verification email with updated token
                send_verification_email(email, user_first_name)

                # TODO: Update all timestamping functionality to use UTC time
                existing_user.pending_registr_expiry_datetime = datetime.now() + timedelta(days=3)

                db.session.commit()

                return success_response("Verification email resent!", 200)
                # return jsonify({"message": "Verification email resent!"}), 200

            # CASE 2: Record with matching email exists and user is already verified
            return error_response("Email is already registered to a verified account", 400)

        user = User()
        user.user_first_name = user_first_name
        user.user_last_name = user_last_name
        user.email_address = email
        # TODO: Update all timestamping functionality to use UTC times
        user.pending_registr_expiry_datetime = datetime.now() + timedelta(days=3)
        # TODO: Encrypt the given user password before storing it in database
        user.password = password
        user.access_permissions = None

        db.session.add(user)
        # only commit changes to the users table if the email is sent successfully
        send_verification_email(email, user_first_name)
        db.session.commit()

        return success_response("Verification email sent!", 200)

    except EmailNotValidError as e:
        return error_response("Invalid email", 400)
    except RuntimeError:
        return error_response("Invalid request format", 400)
    except EmailSendingError as e:
        return error_response(str(e), 500)
    except InternalServerError as e:
        return error_response(str(e), 500)


@application.route('/login', methods=['POST'])
def login_user():
    try:
        # Get data from the JSON request
        data = request.json
        # Extract email, password, and userRole from the request
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email_address=email).first()
        if not user:
            return error_response("Account doesn't exist. Please create an account first", 400)

        # Check if user has valid access permissions. If not, do not allow login
        if user.access_permissions is None:
            return error_response("Account not verified. Please verify your email first", 400)

        # TODO: Decrypt the db password before comparing it against user provided password when logging in
        if user.password != password:
            return error_response("Invalid user name or password", 400)

        # Define amount of time before token expires
        expires = timedelta(hours=72)
        is_admin = user.access_permissions == ADMIN_USER
        token = create_access_token(identity=email, expires_delta=expires, additional_claims={"is_admin": is_admin})

        # Assuming registration is successful, you can send a success response
        return success_response("Login successful", 200,
                                {'jwt': token, "isAdmin": is_admin, "email": email, "firstName": user.user_first_name,
                                 "lastName": user.user_last_name})

    except KeyError:
        # Handle missing or invalid JSON keys in the request
        return error_response("Invalid request form", 400)


@application.route('/employer/name-change', methods=['POST'])
def employer_name_change():
    try:
        # Parse the input data
        data = request.json
        old_employer_id = data.get("old_employer_id")
        new_employer_name = data.get("new_employer_name")
        effective_date = data.get("name_change_effective_date")

        if not all([old_employer_id, new_employer_name, effective_date]):
            return error_response("Missing required fields", 400)

        # Locate and update employer record with old name
        old_employer = Employer.query.filter_by(employer_id=old_employer_id).first()
        if not old_employer:
            return error_response("Employer record with specified name not found", 404)

        old_employer.employer_status = "Rebranded"

        # Create employer record for post-rebrand employer
        new_employer = Employer(
            employer_name=new_employer_name,
            employer_addr_line_1=old_employer.employer_addr_line_1,
            employer_addr_line_2=old_employer.employer_addr_line_2,
            employer_addr_city=old_employer.employer_addr_city,
            employer_addr_state=old_employer.employer_addr_state,
            employer_addr_zip_code=old_employer.employer_addr_zip_code,
            employer_founded_date=old_employer.employer_founded_date,
            employer_dissolved_date=old_employer.employer_dissolved_date,
            employer_bankruptcy_date=old_employer.employer_bankruptcy_date,
            employer_industry_sector_code=old_employer.employer_industry_sector_code,
            employer_status="Active",
            employer_legal_status=old_employer.employer_legal_status
        )

        db.session.add(new_employer)
        db.session.flush()

        # Create new employer_relation record
        new_relation = EmployerRelation(
            parent_employer_id=old_employer.employer_id,
            child_employer_id=new_employer.employer_id,
            employer_relation_type="Rebranding",
            employer_relation_start_date=effective_date
        )

        db.session.add(new_relation)
        db.session.commit()

        return success_response("Employer name change processed", 201)

    except Exception as e:
        return error_response(str(e), 500)


@application.route('/employers-graph', methods=['POST'])
@jwt_required()
def get_employer_graph():
    data = request.json
    employer_id = data.get("employer_id", None)

    if not employer_id:
        return error_response("Invalid employer id", 400)

    try:
        employer = Employer.query.filter_by(employer_id=employer_id).first()
        if employer:
            employers = []
            employer_ids = set()
            mapping = set()

            def add_employer(employer):
                if employer.employer_id not in employer_ids:
                    employer_ids.add(employer.employer_id)
                    employers.append({
                        "id": str(employer.employer_id),
                        "name": employer.employer_name,
                        "estDate": employer.employer_founded_date,
                        "position": {"x": 0, "y": 0}
                    })

            def find_parents(child_employer):
                parent_relations = EmployerRelation.query.filter_by(child_employer_id=child_employer.employer_id).all()
                for parent_relation in parent_relations:
                    parent_employer = Employer.query.get(parent_relation.parent_employer_id)
                    if parent_employer.employer_id not in employer_ids:
                        add_employer(parent_employer)
                        mapping.add((parent_employer.employer_id, child_employer.employer_id,
                                     parent_relation.employer_relation_type))
                        find_parents(parent_employer)
                        find_children(parent_employer)

            def find_children(parent_employer):
                child_relations = EmployerRelation.query.filter_by(parent_employer_id=parent_employer.employer_id).all()
                for child_relation in child_relations:
                    child_employer = Employer.query.get(child_relation.child_employer_id)
                    if child_employer.employer_id not in employer_ids:
                        add_employer(child_employer)
                        mapping.add((parent_employer.employer_id, child_employer.employer_id,
                                     child_relation.employer_relation_type))
                        find_children(child_employer)
                        find_parents(child_employer)

            add_employer(employer)
            find_parents(employer)
            find_children(employer)

            mapping_list = [
                {"id": str(index + 1), "source": str(parent), "target": str(child), "relationType": relation_type} for
                index, (parent, child, relation_type) in enumerate(mapping)]

            return success_response("Employer graph fetched successfully", 200, {
                "nodes": employers,
                "edges": mapping_list
            })
        else:
            return error_response("Employer not found", 404)
    except Exception as e:
        return error_response("Internal server error", 500)


@application.route('/employer', methods=['POST'])
@admin_required()
def create_employer():
    try:
        # Parse the input data
        data = request.json
        employer_name = data.get("employer_name")
        employer_addr_line_1 = data.get("employer_addr_line_1")
        employer_addr_line_2 = data.get("employer_addr_line_2")
        employer_addr_city = data.get("employer_addr_city")
        employer_addr_state = data.get("employer_addr_state")
        employer_addr_zip_code = data.get("employer_addr_zip_code")
        employer_founded_date = data.get("employer_founded_date")
        employer_dissolved_date = data.get("employer_dissolved_date")
        employer_bankruptcy_date = data.get("employer_bankruptcy_date")
        employer_industry_sector_code = data.get("employer_industry_sector_code")
        employer_status = data.get("employer_status")
        employer_legal_status = data.get("employer_legal_status")

        if not all([employer_name, employer_addr_line_1, employer_addr_city,
                    employer_addr_state, employer_addr_zip_code,
                    employer_founded_date, employer_industry_sector_code,
                    employer_status, employer_legal_status]):
            return error_response("Missing required fields", 400)

        new_employer = Employer(
            employer_name=employer_name,
            employer_addr_line_1=employer_addr_line_1,
            employer_addr_line_2=employer_addr_line_2,
            employer_addr_city=employer_addr_city,
            employer_addr_state=employer_addr_state,
            employer_addr_zip_code=employer_addr_zip_code,
            employer_founded_date=employer_founded_date,
            employer_dissolved_date=employer_dissolved_date,
            employer_bankruptcy_date=employer_bankruptcy_date,
            employer_industry_sector_code=employer_industry_sector_code,
            employer_status=employer_status,
            employer_legal_status=employer_legal_status
        )

        db.session.add(new_employer)
        db.session.commit()

        return success_response("New employer added", 201, {"employer_id": new_employer.employer_id})

    except Exception as e:
        return error_response(str(e), 500)


@application.route('/employer', methods=['PATCH'])
@admin_required()
def update_employer():
    # TODO: implement this route
    return error_response("Server reached but route not implemented yet", 400)


@application.route('/employer/split', methods=['POST'])
def split_employers():
    try:
        # Parse the input data
        data = request.json
        company_a_id = data.get('company_a_id')
        company_b_id = data.get('company_b_id')
        company_c_id = data.get('company_c_id')
        start_date = data.get('employer_relation_start_date')

        if not all([company_a_id, company_b_id, company_c_id, start_date]):
            return error_response("Missing required fields", 400)

        # Fetch employer IDs
        company_a = Employer.query.filter_by(employer_id=company_a_id).first()
        company_b = Employer.query.filter_by(employer_id=company_b_id).first()
        company_c = Employer.query.filter_by(employer_id=company_c_id).first()

        if not all([company_a, company_b, company_c]):
            return error_response("One or more companies not found", 404)

        # Relation type is spin-off
        relation_type = "Spin-off"

        # Create new employer_relation records
        new_relation_a_b = EmployerRelation(parent_employer_id=company_a.employer_id,
                                            child_employer_id=company_b.employer_id,
                                            employer_relation_type=relation_type,
                                            employer_relation_start_date=start_date)

        new_relation_a_c = EmployerRelation(parent_employer_id=company_a.employer_id,
                                            child_employer_id=company_c.employer_id,
                                            employer_relation_type=relation_type,
                                            employer_relation_start_date=start_date)

        db.session.add_all([new_relation_a_b, new_relation_a_c])
        db.session.commit()

        return success_response("Employers successfully split", 200)

    except Exception as e:
        return error_response(str(e), 500)


@application.route('/employer/merge', methods=['POST'])
def merge_employers():
    try:
        # Parse the input data
        data = request.json
        company_a_id = data.get('company_a_id')
        company_b_id = data.get('company_b_id')
        company_c_id = data.get('company_c_id')
        start_date = data.get('employer_relation_start_date')

        if not all([company_a_id, company_b_id, company_c_id,
                    start_date]):
            return error_response("Missing required fields", 400)

        # Fetch employer IDs
        company_a = Employer.query.filter_by(employer_id=company_a_id).first()
        company_b = Employer.query.filter_by(employer_id=company_b_id).first()
        company_c = Employer.query.filter_by(employer_id=company_c_id).first()

        if not all([company_a, company_b, company_c]):
            return error_response("One or more companies not found", 404)

        # Relation type is Merger
        relation_type = "Merger"

        # Create new employer_relation records
        new_relation_a_c = EmployerRelation(parent_employer_id=company_a.employer_id,
                                            child_employer_id=company_c.employer_id,
                                            employer_relation_type=relation_type,
                                            employer_relation_start_date=start_date)

        new_relation_b_c = EmployerRelation(parent_employer_id=company_b.employer_id,
                                            child_employer_id=company_c.employer_id,
                                            employer_relation_type=relation_type,
                                            employer_relation_start_date=start_date)

        db.session.add_all([new_relation_a_c, new_relation_b_c])
        db.session.commit()

        return success_response("Employers successfully merged", 200)

    except Exception as e:
        return error_response(str(e), 500)

