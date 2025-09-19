from flask.json import jsonify
from flask import Blueprint, request

from uuid import uuid4
from datetime import datetime

from builder import Builder, Relationship

chats_bp = Blueprint("chats", __name__, url_prefix="/chats")


@chats_bp.route("/channel/<string:room_id>/", methods=["GET"])
def read_chats(room_id: str):
    chats = (
        Builder.query("chats")
        .fields("*")
        .where(f"chats.room_id = '{room_id}'")
        .relation("users", "sender_id", alias="player")
        .relation(
            "chat_reactions",
            "chat_id",
            relationship=Relationship.HAS_MANY,
            alias="reactions",
        )
        .read()
        .fetchall()
    )

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


@chats_bp.route("/channel/<string:room_id>/<string:chat_id>/react/", methods=["POST"])
def react_message(room_id: str, chat_id: str):
    data = request.get_json()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    affected_row = (Builder.query("chat_reactions")
    .fields(["id", "count"])
    .where(f"chat_id = '{chat_id}'"
           f" AND emoji = '{data['emoji']}'")
    .read())

    if affected_row.exists:
        first = affected_row.fetchone()
        
        (Builder.query("chat_reactions")
        .fields(["count"])
        .values((first["count"] + 1,))
        .where(f"chat_id = '{chat_id}' AND emoji = '{data['emoji']}'")
        .update())
        
        response = jsonify({"success": True, "message": f"Reaction added successfully"})
        return response, 201

    (Builder.query("chat_reactions")
    .fields(["chat_id", "sender_id", "emoji", "created_at"])
    .values((chat_id, data["sender_id"], data["emoji"], created_at))
    .create())

    response = jsonify({"success": True, "message": f"Reaction added successfully"})
    return response, 201
    
@chats_bp.route("/channel/<string:room_id>/<string:chat_id>/delete/", methods=["DELETE"])
def delete_message(room_id: str, chat_id: str):
    affected_row = (Builder.query("chats")
    .where(f"id = '{chat_id}'")
    .read())
    
    if not affected_row.exists:
        response = jsonify({"success": False, "message": "Message not found"})
        return response, 404
    
    (Builder.query("chats")
    .where(f"id = '{chat_id}'")
    .delete())
    
    response = jsonify({"success": True, "message": "Message deleted successfully"})
    return response, 200

    
@chats_bp.route("/channel/<string:room_id>/<string:chat_id>/edit/", methods=["PATCH"])
def edit_message(room_id: str, chat_id: str):
    affected_row = (Builder.query("chats")
    .where(f"id = '{chat_id}'")
    .read())

    if not affected_row.exists:
        response = jsonify({"success": False, "message": "Message not found"})
        return response, 404

    data = request.get_json()
    modified_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    (Builder.query("chats")
    .fields(["message", "modified_at"])
    .values((data["message"], modified_at,))
    .where(f"id = '{chat_id}'")
    .update())

    response = jsonify({"success": True, "message": "Message modified successfully"})
    return response, 200
