from flask_socketio import emit  # type: ignore
from flask.json import jsonify
from flask import Blueprint, request
from uuid import uuid4

from datetime import datetime
from typing import Dict, Any

from config.database import Builder, Relationship

chats_bp = Blueprint("chats", __name__, url_prefix="/chats")


@chats_bp.route("/channel/<string:room_id>/", methods=["GET"])
def read_chats(room_id: str):
    chats = (Builder.query("chats")
        .fields("*")
        .where(f"chats.room_id = '{room_id}'")
        .relation("users", "sender_id", alias="player")
        .relation("chat_reactions", "chat_id", relationship=Relationship.HAS_MANY, alias="reactions")
        .read()
        .fetchall())

    response = jsonify(chats)
    response.headers["Cache-Control"] = "no-store"
    return response, 200


@chats_bp.route("/channel/<string:room_id>/", methods=["POST"])
def send_message(room_id: str):
    data = request.get_json()

    txt: str = data["message"]
    sender_id: int = data["sender_id"]
    uuid = str(uuid4())

    (
        Builder.query("chats")
        .fields(["id", "message", "sender_id", "room_id"])
        .values((uuid, txt, sender_id, room_id))
        .create()
    )

    response = jsonify({"success": True, "message": f"Message sent successfully"})
    return response, 201

@chats_bp.route("/channel/<string:room_id>/<string:chat_id>/react", methods=["POST"])
def react_to_message(room_id: str, chat_id: str):
    data = request.get_json()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lastrowid = (Builder.query("chat_reactions")
    .fields(["chat_id", "sender_id", "emoji", "created_at"])
    .values((chat_id, data["sender_id"], data["emoji"], created_at))
    .create())
    
    chat_reaction: Dict[str, Any] = {
        "id": lastrowid,
        "chat_id": chat_id,
        "sender_id": data["sender_id"],
        "emoji": data["emoji"],
        "count": 1,
        "created_at": created_at,
    }
    
    emit("channel:reaction", chat_reaction, to=room_id, namespace="/channel")
    
    response = jsonify({"success": True, "message": f"Reaction added successfully"})
    return response, 201
    