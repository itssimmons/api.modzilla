from app import app, socketio

if __name__ == "__main__":
    socketio.run(               # type: ignore
        app, 
        host="0.0.0.0",
        port=8000,
        debug=True,
        allow_unsafe_werkzeug=True,
    )
