from flask_socketio import emit, join_room  # type: ignore
from flask import request
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any
from app import socketio
from app.enums.Status import Status
from orm.database import Builder

STAFF_ID = 1


@socketio.on("disconnect", namespace="/channel")
def handle_disconnect_channel(_: None):
    """TODO: make it global, not only for /channel"""
    sid: str = request.sid  # type: ignore
    op = "old"

    user = (
        Builder.query("users")
        .fields("*")
        .where(f"sid = '{sid}'")
        .limit(1)
        .read()
        .fetchone()
    )

    activity: Dict[str, Any] = {
        "user": {**user, "status": Status.OFFLINE.value},
        "sid": None,
        "is": op,
    }

    emit("activity:channel", activity, broadcast=True, namespace="/channel")

    (
        Builder.query("users")
        .fields(["sid", "status"])
        .values((None, Status.OFFLINE.value))
        .where(f"sid = '{sid}'")
        .update()
    )


@socketio.on("connected", namespace="/channel")
def player_connected(data: Dict[str, Any]):
    """TODO: make it global, not only for /channel"""
    print("\n---\nevent: online\n---\n [", data, "]")

    sid: str = request.sid  # type: ignore
    user: Dict[str, Any] = data["user"]
    op = data["op"] if "op" in data else "old"

    user_id: int = user["id"]

    activity: Dict[str, Any] = {
        "user": {**user, "status": Status.ONLINE.value},
        "is": op,
    }

    emit("activity:channel", activity, broadcast=True, namespace="/channel")

    (
        Builder.query("users")
        .fields(["sid"])
        .values((sid,))  # type: ignore
        .where(f"id = {user_id}")
        .update()
    )


@socketio.on("cursor:move", namespace="/channel")
def player_cursor_move(data: Dict[str, Any]):
    print("\n---\nevent: cursor:move\n---\n [", data, "]")

    room: str = data["room"]
    data["room"] = None

    emit(
        "cursor:move",
        data,
        to=room,
        broadcast=True,
        include_self=False,
        namespace="/channel",
    )


@socketio.on("activity:channel", namespace="/channel")
def activity_channel(data: Dict[str, Any]):
    print("\n---\nevent: activity:channel\n---\n [", data, "]")

    user = data["user"]
    room = data["room"] if "room" in data else None
    op = "old"

    activity: Dict[str, Any] = {
        "user": {**user},
        "sid": None,
        "is": op,
    }

    emit("activity:channel", activity, to=room, broadcast=True, namespace="/channel")


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

    room: str = data["room"]
    join_room(room)


@socketio.on("idle", namespace="/channel")
def player_idle(data: Dict[str, Any]):
    print("\n---\nevent: idle\n---\n [", data, "]")

    user = data["user"]
    op = "old"

    activity: Dict[str, Any] = {
        "user": {**user, "status": Status.IDLE.value},
        "sid": None,
        "is": op,
    }

    emit("activity:channel", activity, broadcast=True, namespace="/channel")


@socketio.on("online", namespace="/channel")
def player_online(data: Dict[str, Any]):
    print("\n---\nevent: idle\n---\n [", data, "]")

    user = data["user"]
    op = "old"

    activity: Dict[str, Any] = {
        "user": {**user, "status": Status.ONLINE.value},
        "sid": None,
        "is": op,
    }

    emit("activity:channel", activity, broadcast=True, namespace="/channel")
