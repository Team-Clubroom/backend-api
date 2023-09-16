from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

application = Flask(__name__);
application.config['SECRET_KEY'] = "dkoiuf121nd91akd9n234m2n3j3dlser123"
jwt = JWTManager(application)


@application.route('/')
def hello_world():
    return "Hello world :)"


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
