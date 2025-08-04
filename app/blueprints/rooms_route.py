from flask.json import jsonify
from flask import Blueprint
from config.database import Builder

rooms_bp = Blueprint("channels", __name__, url_prefix="/channels")


@rooms_bp.route("/<string:room_id>/", methods=["GET"])
def read_room(room_id: str):
    """
    Get one room
    ---
    tags:
      - Rooms
    parameters:
      - in: path
        name: room_id
        schema:
          type: string
        description: Room ID
        required: true
        example: 53c38a2c-9640-4957-92d7-0d4400b2b9ac
    responses:
      200:
        description: Ok
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Room'
      404:
        description: Not found
    """

    rooms = (Builder.query("rooms")
        .fields("*")
        .where(f"id = '{room_id}'")
        .read()
        .limit(1)
        .fetchone())
    
    if not rooms:
        return jsonify({ "message": "Room not found" }), 404

    response = jsonify(rooms)
    # response.headers["Cache-Control"] = "public, max-age=3600"
    return response, 200

