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


@application.route('/login', methods=['POST'])
def register_user():
    try:
        # Get data from the JSON request
        data = request.json

        # Extract email, password, and userRole from the request
        email = data['email']
        password = data['password']

        if email != password:
            return jsonify({
                "error": "Password or email are incorrect"
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
