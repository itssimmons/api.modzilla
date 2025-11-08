from flask_socketio import SocketIO
from flask_openapi3 import Info, FlaskOpenAPI3

socketio = SocketIO(
    app,
    ping_interval=10,  # heartbeat
    ping_timeout=20,
    logger=True,
    engineio_logger=True,
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.0.61:3000",
        "http://192.168.0.61:8000",
    ],
)


api_info = Info(title="Mi API de Ejemplo", version="1.0.0", description="Una descripción de mi API.")
openapi = FlaskOpenAPI3(app, info=api_info)