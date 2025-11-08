from flask import Flask
from flask_cors import CORS

from middlewares.auth_middleware import Auth


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './resources'
app.config["SECRET_KEY"] = "Shh!"

CORS(app, resources={r"/*": {"origins": "*"}})

app.wsgi_app = Auth(app.wsgi_app, urls={'/v1/*', '/auth/logout'})  # type: ignore

from extensions import socketio, openapi  # noqa: F401
from blueprints.v1 import v1_bp  # noqa: F401

app.register_blueprint(v1_bp)
