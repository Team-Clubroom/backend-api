# development_routes.py
from datetime import timedelta

from flask import Blueprint
from flask_jwt_extended import create_access_token

from application import success_response

development_routes_bp = Blueprint('development_routes', __name__)


@development_routes_bp.route('/token')
def gimme_token():
    # Define amount of time before token expires
    expires = timedelta(hours=72)
    token = create_access_token(identity="", expires_delta=expires)

    # Assuming registration is successful, you can send a success response
    return success_response("Token granted", 200, {'jwt': token})
