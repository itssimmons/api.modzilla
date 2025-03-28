from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "Shh!"

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app,
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.0.27:3000",
    ],
    logger=True,
    engineio_logger=True,
)

from app.events import *
from app.blueprints import v1_bp

app.register_blueprint(v1_bp)
