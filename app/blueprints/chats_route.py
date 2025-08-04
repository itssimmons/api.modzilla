from flask.json import jsonify
from flask import Blueprint, request
from uuid import uuid4
from config.database import Builder

chats_bp = Blueprint("chats", __name__, url_prefix="/chats")


@chats_bp.route("/channel/<string:room_id>/", methods=["GET"])
def read_chats(room_id: str):
    chats = (Builder.query("chats")
        .fields("*")
        .where(f"chats.room_id = '{room_id}'")
        .relation("users", "sender_id")
        .read()
        .fetchall())

    response = jsonify(chats)
    response.headers["Cache-Control"] = "no-store"
    return response, 200


@chats_bp.route("/channel/", methods=["POST"])
def send_message():
    data = request.get_json()

    txt: str = data["message"]
    sender_id: int = data["sender_id"]
    room_id: str = data["room_id"]
    uuid = str(uuid4())

    (
        Builder.query("chats")
        .fields(["id", "message", "sender_id", "room_id"])
        .values((uuid, txt, sender_id, room_id))
        .create()
    )

    response = jsonify({"success": True, "message": f"Message saved successfully"})
    return response, 201
