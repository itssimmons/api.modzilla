from flask import Blueprint

from app.blueprints.player_route import players_bp
from app.blueprints.chats_route import chats_bp
from app.blueprints.rooms_route import rooms_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/v1")

v1_bp.register_blueprint(players_bp)
v1_bp.register_blueprint(chats_bp)
v1_bp.register_blueprint(rooms_bp)
