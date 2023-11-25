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


@development_routes_bp.route('/employers-graph', methods=["POST"])
def gimme_employers_graph():
    json_obj = {
        "nodes": [
            {"id": "13", "name": "Ultra-Mart", "estDate": "1988-09-21", "position": {"x": 0, "y": 0}},
            {"id": "14", "name": "Ultra-Rx", "estDate": "1993-11-11", "position": {"x": 300, "y": 400}},
            {"id": "15", "name": "Mega-Mart", "estDate": "1999-03-16", "position": {"x": 400, "y": 200}},
            {"id": "16", "name": "Okay-Mart", "estDate": "2000-02-21", "position": {"x": 700, "y": 600}},
            {"id": "17", "name": "Mega-Mart Neighborhoods", "estDate": "2000-07-01", "position": {"x": 800, "y": 300}},
            {"id": "18", "name": "Not-Great-Mart", "estDate": "2006-08-16", "position": {"x": 1200, "y": 500}},
        ],
        "edges": [
            {
                "id": "1",
                "target": "16",
                "source": "15",
                "relationType": "Subsidiary",
            },
            {
                "id": "2",
                "target": "17",
                "source": "15",
                "relationType": "Subsidiary",
            },
            {
                "id": "3",
                "target": "14",
                "source": "13",
                "relationType": "Subsidiary",
            },
            {
                "id": "4",
                "target": "15",
                "source": "13",
                "relationType": "Subsidiary",
            },
            {
                "id": "5",
                "target": "18",
                "source": "16",
                "relationType": "Subsidiary",
            },
        ]
    }

    return success_response("Employer graph fetched", 200, json_obj)
