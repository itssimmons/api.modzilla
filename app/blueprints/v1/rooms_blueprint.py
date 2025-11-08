from flask import Blueprint, Response

from addons.builder import Builder

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
        return Response({"exception": {
            "message": "Room not found",
            "code": "ROOM_NOT_FOUND",
            "details": { "room_id": room_id }
        }}, mimetype='application/json', status=404)

    response = Response(rooms, mimetype='application/json', status=200)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response
