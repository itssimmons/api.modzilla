from flask.json import jsonify
from flask import Blueprint
from orm.database import Builder

rooms_bp = Blueprint("channels", __name__, url_prefix="/channels")


@rooms_bp.route("/<string:room_id>/", methods=["GET"])
def read_room(room_id: str):
    rooms = (
        Builder.query("rooms")
        .fields("*")
        .where(f"id = '{room_id}'")
        .read()
        .limit(1)
        .fetchone()
    )

    if not rooms:
        return jsonify({"message": "Room not found"}), 404

    response = jsonify(rooms)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response, 200
