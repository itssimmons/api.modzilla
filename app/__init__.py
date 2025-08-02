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
       "*"
    ],
)

from app.events import *
from app.blueprints import v1_bp

@app.route("/ping")  
def ping():
    from time import time
    start = time() * 1000

    end = time() * 1000
    return f"Pong in {end - start:.2f}ms"

app.register_blueprint(v1_bp)
