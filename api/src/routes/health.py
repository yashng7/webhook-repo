from flask import Blueprint, jsonify
from src.services.database import check_connection

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    mongo_connected = check_connection()
    
    status = "healthy" if mongo_connected else "unhealthy"
    http_code = 200 if mongo_connected else 503
    
    return jsonify({
        "status": status,
        "mongo": "connected" if mongo_connected else "disconnected"
    }), http_code