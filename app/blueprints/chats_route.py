from flask.json import jsonify
from flask import Blueprint, request
from uuid import uuid4
from config.database import Builder

chats_bp = Blueprint("chats", __name__, url_prefix="/chats")


@chats_bp.route("/channel", methods=["GET"])
def read_chats():
    """
    Example:
        .. code-block:: bash
        curl -X GET "http://127.0.0.1:8000/{version}/channel"
    """

    chats = Builder.query("chats").fields("*").read().fetchall()
    response = jsonify(chats)
    response.headers["Cache-Control"] = "no-store"
    return response, 200


@chats_bp.route("/channel", methods=["POST"])
def send_message():
    data = request.get_json()

    txt: str = data["message"]
    user_id: int = data["user_id"]
    uuid = str(uuid4())

    (
        Builder.query("chats")
        .fields(["id", "message", "sender_id"])
        .values((uuid, txt, user_id))
        .create()
    )

    response = jsonify({"success": True, "message": f"Message saved successfully"})
    return response, 201
