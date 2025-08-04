from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_swagger_ui import get_swaggerui_blueprint # type: ignore

app = Flask(__name__)
app.config["SECRET_KEY"] = "Shh!"

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app,
    ping_interval=10, # heartbeat
    ping_timeout=20,
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


SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'http://127.0.0.1:8000/spec'  # URL for exposing API documentation (without trailing '/')

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)

@app.route("/spec")
def spec():
    from pathlib import Path
    from os import getcwd
    from json import loads
    raw_json = Path(f"{getcwd()}/docs/swagger.json").read_text()
    swag = loads(raw_json)
    return jsonify(swag)

@app.route("/ping")  
def ping():
    from time import time
    start = time() * 1000

    end = time() * 1000
    return f"Pong in {end - start:.2f}ms"

app.register_blueprint(swaggerui_blueprint)
app.register_blueprint(v1_bp)
