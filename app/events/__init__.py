from flask_socketio import emit  # type: ignore
from flask import request
from typing import Any
from app import socketio
from config.database import Builder


@socketio.on("pragma")
def table_info(t: str):
    f = Builder.resolve_asterisk(t)
    emit("pragma", f)


# Handling errors


@socketio.on_error_default
def default_error_handler(e: Any):
    print("Reason: ", str(e))
    print(request.event["message"])  # "my error event" # type: ignore
    print(request.event["args"])  # (data,) # type: ignore


from app.events.namespaces.channel import *
