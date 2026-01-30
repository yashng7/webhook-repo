from flask import Flask, jsonify, request
from src.database import check_connection, init_indexes, get_collection
from src.signature import verify_signature
from src.parser import parse_event
from src.repository import save_event, get_events, get_event_count
from src.config import Config

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


@app.route("/api/events", methods=["GET"])
def api_events():
    try:
        limit = request.args.get("limit", default=50, type=int)
        offset = request.args.get("offset", default=0, type=int)
        action = request.args.get("action", default=None, type=str)
        
        limit = max(1, min(limit, 100))
        offset = max(0, offset)
        
        if action and action.upper() not in ("PUSH", "PULL_REQUEST", "MERGE"):
            return jsonify({
                "error": "Invalid action filter. Must be PUSH, PULL_REQUEST, or MERGE"
            }), 400
        
        events = get_events(limit=limit, offset=offset, action=action)
        total = get_event_count(action=action)
        
        return jsonify({
            "events": events,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total,
                "has_more": offset + len(events) < total
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhook", methods=["POST"])
def webhook():
    signature_header = request.headers.get("X-Hub-Signature-256", "")
    payload_body = request.get_data()
    
    if not verify_signature(payload_body, Config.WEBHOOK_SECRET, signature_header):
        return jsonify({"error": "Invalid signature"}), 401
    
    event_type = request.headers.get("X-GitHub-Event", "")
    delivery_id = request.headers.get("X-GitHub-Delivery", "")
    
    if not event_type:
        return jsonify({"error": "Missing X-GitHub-Event header"}), 400
    
    if not delivery_id:
        return jsonify({"error": "Missing X-GitHub-Delivery header"}), 400
    
    payload = request.get_json()
    
    if payload is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    parsed_event = parse_event(event_type, delivery_id, payload)
    
    if parsed_event is None:
        return jsonify({
            "status": "ignored",
            "reason": f"Event type '{event_type}' not handled"
        }), 200
    
    result = save_event(parsed_event)
    
    if not result["success"]:
        return jsonify({"error": "Failed to save event"}), 500
    
    response_data = {
        "status": "received",
        "duplicate": result["duplicate"],
        "event": {
            "request_id": parsed_event["request_id"],
            "author": parsed_event["author"],
            "action": parsed_event["action"],
            "from_branch": parsed_event["from_branch"],
            "to_branch": parsed_event["to_branch"],
            "timestamp": parsed_event["timestamp"].isoformat()
        }
    }
    
    if result["inserted_id"]:
        response_data["inserted_id"] = result["inserted_id"]
    
    return jsonify(response_data), 200


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