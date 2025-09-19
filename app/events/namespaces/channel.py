from flask_socketio import emit, join_room, leave_room  # type: ignore
from flask import request

from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

from app import socketio
from app.enums.Status import Status
from builder import Builder


STAFF_ID = 1


@socketio.on('connected', namespace='/channel')
def handle_channel_connect(data: Dict[str, Any]):
    sid: str = request.sid  # type: ignore
    user_id: int = data["user_id"]

    payload: Dict[str, Any] = {
        "user": {
            "id": user_id,
            "sid": sid,
            "status": Status.ONLINE.value
        }
    }

    emit(
        "channel:status",
        payload,
        # to=room,
        broadcast=True,
        include_self=True,
        namespace="/channel",
    )
    
    (
        Builder.query('users')
        .fields(['sid', 'status'])
        .values((sid, Status.ONLINE.value,)) # type: ignore
        .where(f"id = {user_id}")
        .update()
    )


@socketio.on("disconnect", namespace="/channel")
def handle_channel_disconnect(_: None):
    sid: str = request.sid  # type: ignore

    (
        Builder.query("users")
        .fields(["sid", "status"])
        .values((None, Status.OFFLINE.value,))
        .where(f"sid = '{sid}'")
        .update()
    )
    

@socketio.on("cursor:move", namespace="/channel")
def channel_cursor_move(data: Dict[str, Any]):
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


@socketio.on("message", namespace="/channel")
def channel_message(data: Dict[str, Any]):
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
    
    
@socketio.on("message:action", namespace="/channel")
def channel_message_action(data: Dict[str, Any]):
    print("\n---\nevent: message:action\n---\n [", data, "]")
    
    room: str = data["room"]
    payload = data["payload"]
    event = data["event"]
    
    print(payload, room ,event)

    emit(
        event,
        payload,
        to=room,
        broadcast=True,
        include_self=False,
        namespace="/channel",
    )
    
    
@socketio.on("player:action", namespace="/channel")
def channel_player_action(data: Dict[str, Any]):
    print("\n---\nevent: player:action\n---\n [", data, "]")
    
    room: str | None = data.get("room", None)
    payload = data.get("payload", {})
    event = data.get("event", None)
    
    if event == "channel:whisper":
        dest_sid: str  = payload["to"]["sid"]
        del payload["to"]["sid"]

        emit(
            event,
            payload,
            to=dest_sid,
            broadcast=False,
            include_self=False,
            namespace="/channel",
        )
    elif event == "channel:status":
        user = payload["user"]
        
        (
            Builder.query('users')
            .fields(['status'])
            .values((user['status'],))
            .where(f"id = {user['id']}")
            .update()
        )

        emit(
            event,
            payload,
            to=room,
            broadcast=True,
            include_self=True,
            namespace="/channel",
        )
    elif event == "channel:block":
        dest_sid: str  = payload["to"]["sid"]
        del payload["to"]["sid"]
        
        emit(
            event,
            payload,
            to=dest_sid,
            broadcast=False,
            include_self=False,
            namespace="/channel",
        )
    else:
        print("Unknown event:", event)


@socketio.on("join", namespace="/channel")
def player_join(data: Dict[str, Any]):
    print("\n---\nevent: join\n---\n [", data, "]")

    room_id: str = data["room"]
    join_room(room_id)


@socketio.on("leave", namespace="/channel")
def player_leave(data: Dict[str, Any]):
    print("\n---\nevent: leave\n---\n [", data, "]")

    room_id: str = data["room"]
    leave_room(room_id)

