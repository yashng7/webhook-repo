from flask import Flask, jsonify
from src.database import check_connection, init_indexes, get_collection

app = Flask(__name__)

_indexes_initialized = False


def ensure_indexes():
    global _indexes_initialized
    if not _indexes_initialized:
        try:
            init_indexes()
            _indexes_initialized = True
        except Exception:
            pass


@app.before_request
def before_request():
    ensure_indexes()


@app.route("/")
def root():
    return jsonify({"service": "webhook-api", "status": "running"})


@app.route("/health")
def health():
    mongo_connected = check_connection()
    status = "healthy" if mongo_connected else "unhealthy"
    http_code = 200 if mongo_connected else 503
    
    return jsonify({
        "status": status,
        "mongo": "connected" if mongo_connected else "disconnected"
    }), http_code


@app.route("/debug/schema")
def debug_schema():
    try:
        collection = get_collection()
        indexes = list(collection.list_indexes())
        index_info = [{"name": idx["name"], "keys": dict(idx["key"])} for idx in indexes]
        
        return jsonify({
            "collection": collection.name,
            "indexes": index_info,
            "document_count": collection.count_documents({})
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500