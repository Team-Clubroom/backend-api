from email_validator import validate_email, EmailNotValidError
from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

application = Flask(__name__);
application.config['SECRET_KEY'] = "dkoiuf121nd91akd9n234m2n3j3dlser123"
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:myrootpassword@127.0.0.1:3306/backend_test'
jwt = JWTManager(application)

db = SQLAlchemy(application)
# db.init_app(application)
bcrypt = Bcrypt(application)


# login_manager = LoginManager(application)
# login_manager.login_view = 'login'


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


@application.route('/')
def hello_world():
    # Execute the SQL query
    employers = Employer.query.all()

    # Convert results to list of dictionaries
    results = [{"id": e.employer_id, "name": e.employer_name} for e in employers]
    return jsonify(results)
    # return "Hello world :)"


@application.route('/hello-private')
@jwt_required()
def hello_world_private():
    return "Hello world privately :)"


@application.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        email = data.get("email", None)
        password = data.get("password", None)

        if not email or not password:
            return jsonify({
                "error": "Required arguments missing"
            }), 400
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized

        # TODO: Exception for user already registered

        user = User()
        user.email_address = email
        user.password = password
        user.access_permissions = None

        db.session.add(user)
        db.session.commit()

        # TODO: Send verification email here

        success_response = {
            'message': 'Verification email sent'
        }

        return jsonify(success_response), 201

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

        if email != password:
            return jsonify({
                'error': 'Password or email are incorrect'
            }), 400

        # create token
        token = create_access_token(identity=email)

        # Assuming registration is successful, you can send a success response
        response = {
            'message': 'Login successful',
            'token': token
        }
        return jsonify(response), 201  # 201 Created status code

    except KeyError:
        # Handle missing or invalid JSON keys in the request
        error_response = {
            'error': 'Invalid request format'
        }
        return jsonify(error_response), 400  # 400 Bad Request status code
