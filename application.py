from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from os import environ
from dotenv import load_dotenv
import requests
from sqlalchemy.exc import NoResultFound

# load environment variables from .env file
load_dotenv(".env")
GMAIL_API_URL = environ.get('GMAIL_API_URL')


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
    employer_relation_end_date = db.Column(db.String(10))


class Employer(db.Model):
    __tablename__ = 'employers'

    employer_id = db.Column(db.Integer, primary_key=True)
    employer_name = db.Column(db.String(255))
    employer_previous_name = db.Column(db.String(255))
    employer_founded_date = db.Column(db.String(10))
    employer_dissolved_date = db.Column(db.String(10))
    employer_bankruptcy_date = db.Column(db.String(10))
    employer_status = db.Column(db.String(255))
    employer_legal_status = db.Column(db.String(255))
    employer_name_change_reason = db.Column(db.String(255))


class Employment(db.Model):
    __tablename__ = 'employments'

    employment_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    employer_id = db.Column(db.Integer)
    job_title = db.Column(db.String(255))
    start_date = db.Column(db.String(10))
    end_date = db.Column(db.String(10))


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_first_name = db.Column(db.String(255))
    user_last_name = db.Column(db.String(255))
    email_address = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    pending_registr_expiry_datetime = db.Column(db.DateTime)
    access_permissions = db.Column(db.Integer)


def send_verification_email(email, first_name):
    api_url = environ.get("API_URL")
    email_admin_token = environ.get("EMAIL_ADMIN_TOKEN")
    if not api_url or not email_admin_token:
        return jsonify({"error": "Internal server error"}), 500

    # TODO: Set expiration date on verification token
    verification_url = f"{api_url}/verify?jwt={create_access_token(email)}"

    # Define the data you want to send in the request
    data = {
        'email': email,
        'verification_url': verification_url,
        'first_name': first_name,
        'admin_token': email_admin_token
    }

    try:
        # Send the POST request with the form data
        if not GMAIL_API_URL:
            return jsonify({
                "message": "Internal server error"
            }), 500

        response = requests.post(GMAIL_API_URL, data=data)

        # Check the response status code
        if response.status_code == 200:
            return jsonify({
                "message": "Verification email sent successfully"
            }), 200
        else:
            return jsonify({
                "message": "Failed to send email"
            }), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            "message": "Something went wrong sending the email"
        }), 500


@application.route('/employers')
@jwt_required()
def get_all_employers():
    # Execute the SQL query
    employers = Employer.query.all()

    # Convert results to list of dictionaries
    results = [{"id": e.employer_id, "name": e.employer_name} for e in employers]
    return jsonify(results)


@application.route('/hello-private')
@jwt_required()
def hello_world_private():
    return "Hello world privately :)"


@application.route('/verify', methods=['GET'])
@jwt_required(locations=['query_string'])
def verify_user_account():
    try:
        email = get_jwt_identity()
        user = User.query.filter_by(email_address=email).first()
        user.access_permissions = 1
        db.session.commit()

        # TODO: return an HTML view here
        return f"<div>" \
               f"<h1>Email {email} has been successfully verified</h1>" \
               f"<p>You can now login to your CELDV account</p>" \
               f"</div>"
    except NoResultFound:
        return jsonify({"error": "Could not verify email. Try registering first"}), 400

    except RuntimeError:
        return jsonify({"error": "Internal server error"}), 500


@application.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        user_first_name = data.get("user_first_name", None)
        user_last_name = data.get("user_last_name", None)
        email = data.get("email", None)
        password = data.get("password", None)

        if not email or not password or not user_first_name or not user_last_name:
            return jsonify({
                "error": "Required arguments missing"
            }), 400
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

                return jsonify({"message": "Verification email resent!"}), 200

            # CASE 2: Record with matching email exists and user is already verified
            return jsonify({"error": "Email is already registered to a verified account"}), 400

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
        db.session.commit()

        return send_verification_email(email, user_first_name)

    except EmailNotValidError as e:
        error_response = {
            'error': 'Invalid email'
        }
        return jsonify(error_response), 400

    except RuntimeError:
        error_response = {
            'error': 'Invalid request format'
        }
        return jsonify(error_response), 400  # 400 Bad Request status code


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
            return jsonify({
                "error": "Account doesn't exist. Please create an account first"
            }), 400

        # Check if user has valid access permissions. If not, do not allow login
        if user.access_permissions is None:
            return jsonify({
                "error": "Account not verified. Please verify your email first"
            }), 400

        # TODO: Decrypt the db password before comparing it against user provided password when logging in
        if user.password != password:
            return jsonify({
                "error": "Invalid user name or password"
            }), 400

        # create token
        # TODO: Set expiration date on LOGIN token
        token = create_access_token(identity=email)

        # Assuming registration is successful, you can send a success response
        response = {
            'message': 'Login successful',
            'data': {
                'jwt': token
            }
        }
        return jsonify(response), 201  # 201 Created status code

    except KeyError:
        # Handle missing or invalid JSON keys in the request
        error_response = {
            'error': 'Invalid request format'
        }
        return jsonify(error_response), 400  # 400 Bad Request status code
