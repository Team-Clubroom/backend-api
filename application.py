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


class Employer(db.Model):
    __tablename__ = 'employers'

    employer_id = db.Column(db.Integer, primary_key=True)
    employer_name = db.Column(db.String(255))
    employer_founded_date = db.Column(db.String(10))
    employer_dissolved_date = db.Column(db.String(10))
    employer_status = db.Column(db.String(255))
    employer_legal_status = db.Column(db.String(255))


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(255))
    password = db.Column(db.String(255))
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
            
        print(GMAIL_API_URL)

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
        email = data.get("email", None)
        password = data.get("password", None)
        name = data.get("name", None)

        if not email or not password or not name:
            return jsonify({
                "error": "Required arguments missing"
            }), 400
        email_info = validate_email(email, check_deliverability=False)
        email = email_info.normalized

        # TODO: Exception for user already registered
        user = User()
        user.email_address = email
        # TODO: Encrypt the given user password before storing it in database
        user.password = password
        user.access_permissions = None

        db.session.add(user)
        db.session.commit()

        return send_verification_email(email, name)

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
        # TODO: Don't allow login for unverified accounts
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
