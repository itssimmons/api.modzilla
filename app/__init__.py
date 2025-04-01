from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "Shh!"

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app,
    ping_interval=10,
    ping_timeout=20,  # heartbeat
    logger=True,
    engineio_logger=True,
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.0.27:3000",
        "http://192.168.0.218:8000",
    ],
)

from app.events import *
from app.blueprints import v1_bp

app.register_blueprint(v1_bp)
