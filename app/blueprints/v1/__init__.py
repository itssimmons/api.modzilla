from flask import Blueprint

from blueprints.v1.social_auth_blueprint import social_auth_bp
from blueprints.v1.users_blueprint import players_bp
from blueprints.v1.chats_blueprint import chats_bp
from blueprints.v1.rooms_blueprint import rooms_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/v1")

v1_bp.register_blueprint(social_auth_bp)
v1_bp.register_blueprint(players_bp)
v1_bp.register_blueprint(chats_bp)
v1_bp.register_blueprint(rooms_bp)
