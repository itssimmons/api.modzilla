from flask_socketio import emit, join_room, leave_room  # type: ignore
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any
from app import socketio
from app.enums.Status import Status

ASSISTANT_ID = 1


@socketio.on("activity:channel", namespace="/channel")
def activity_channel(json: Dict[str, Any]):
    print("\n---\nevent: activity:channel\n---\n [", json, "]")
    return json


@socketio.on("message", namespace="/channel")
def player_message(data: Dict[str, Any]):
    print("\n---\nevent: message\n---\n [", data, "]")

    user_id: int = data["user_id"]
    room: str = data["room"]
    txt: str = data["message"]
    uuid = str(uuid4())

    message: Dict[str, Any] = {
        "id": uuid,
        "sender_id": user_id,
        "modified_id": None,
        "message": txt,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modified_at": None,
    }

    emit(
        "main:channel",
        message,
        to=room,
        broadcast=True,
        include_self=False,
        namespace="/channel",
    )


@socketio.on("join", namespace="/channel")
def player_join(data: Dict[str, Any]):
    print("\n---\nevent: join\n---\n [", data, "]")

    user = data["user"]
    room = data["room"]
    op = data["op"] if "op" in data else "old"

    join_room(room)

    activity: Dict[str, Any] = {
        "user": {**user, "status": Status.ONLINE.value},
        "is": op,
    }

    emit("activity:channel", activity, to=room, broadcast=True, namespace="/channel")


@socketio.on("left", namespace="/channel")
def player_left(data: Dict[str, Any]):
    print("\n---\nevent: left\n---\n [", data, "]")

    user = data["user"]
    room = data["room"]
    op = "old"

    leave_room(room)

    activity: Dict[str, Any] = {
        "user": {**user, "status": Status.OFFLINE.value},
        "is": op,
    }

    emit("activity:channel", activity, to=room, broadcast=True, namespace="/channel")
