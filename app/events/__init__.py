from flask_socketio import emit  # type: ignore
from flask import request
from typing import Any, Set
from extensions import socketio

online_sid: Set[str] = set()


# Handling heartbeats
@socketio.on("connect")
def handle_connect():
    online_sid.add(request.sid)  # type: ignore


@socketio.on("disconnect")
def handle_disconnect():
    online_sid.discard(request.sid)  # type: ignore


@socketio.on_error_default
def default_error_handler(e: Any):
    print("\n--- [BEGIN | default_error_handler] ---")
    print("Reason: ", str(e))
    print(request.event["message"])  # "my error event" # type: ignore
    print(request.event["args"])  # (data,) # type: ignore
    print("--- [END | default_error_handler] ---\n")


from events.namespaces.channel import *  # noqa: E402, F403
