from flask import Flask, request, jsonify

application = Flask(__name__);


@application.route('/')
def hello_world():
    return "Hello world :)"


@application.route('/register', methods=['POST'])
def register_user():
    try:
        # Get data from the JSON request
        data = request.json

        # Extract email, password, and userRole from the request
        email = data['email']
        password = data['password']
        user_role = data['userRole']

        # Perform some registration logic here, e.g., create a new user
        # You would typically validate the input and store the user data in a database

        # Assuming registration is successful, you can send a success response
        response = {
            'message': 'User registered successfully',
            'email': email,
            'userRole': user_role
        }
        return jsonify(response), 201  # 201 Created status code

    except KeyError:
        # Handle missing or invalid JSON keys in the request
        error_response = {
            'error': 'Invalid request format'
        }
        return jsonify(error_response), 400  # 400 Bad Request status code
