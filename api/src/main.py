import os
from flask import Flask, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017/webhook_db")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def check_mongo_connection():
    try:
        client = get_client()
        client.admin.command("ping")
        return True
    except ConnectionFailure:
        return False


@app.route("/")
def root():
    return jsonify({"service": "webhook-api", "status": "running"})


@app.route("/health")
def health():
    mongo_connected = check_mongo_connection()
    status = "healthy" if mongo_connected else "unhealthy"
    http_code = 200 if mongo_connected else 503
    
    return jsonify({
        "status": status,
        "mongo": "connected" if mongo_connected else "disconnected"
    }), http_code