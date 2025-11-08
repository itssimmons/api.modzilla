from flask import Blueprint, Response, request

from addons.builder import Builder

import json


players_bp = Blueprint("users", __name__, url_prefix="/users")


@players_bp.route("/", methods=["GET"])
def index():
    relationships: str = request.args.get("relationships", '')
    relationship_list = relationships.split(",") if relationships else []
    
    users = Builder.query("users").fields("*")
    for relation in relationship_list:
        users = users.relation(relation)
    users = users.read().fetchall()
    
    for user in users:
        del user["password"]
    
    response = Response(json.dumps(users), mimetype='application/json', status=200)
    response.headers["Cache-Control"] = "no-store"
    return response


