from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from src.database import get_collection


def save_event(event_data):
    collection = get_collection()
    
    document = {
        "request_id": event_data["request_id"],
        "author": event_data["author"],
        "action": event_data["action"],
        "from_branch": event_data["from_branch"],
        "to_branch": event_data["to_branch"],
        "timestamp": event_data["timestamp"],
        "raw_payload": event_data.get("raw_payload", {}),
        "created_at": datetime.now(timezone.utc)
    }
    
    try:
        result = collection.insert_one(document)
        return {
            "success": True,
            "inserted_id": str(result.inserted_id),
            "duplicate": False
        }
    except DuplicateKeyError:
        return {
            "success": True,
            "inserted_id": None,
            "duplicate": True
        }


def event_exists(request_id):
    collection = get_collection()
    return collection.count_documents({"request_id": request_id}, limit=1) > 0


def get_event_by_request_id(request_id):
    collection = get_collection()
    document = collection.find_one({"request_id": request_id})
    
    if document:
        return serialize_event(document)
    
    return None


def get_events(limit=50, offset=0, action=None):
    collection = get_collection()
    
    query = {}
    if action:
        query["action"] = action.upper()
    
    cursor = collection.find(query).sort("timestamp", -1).skip(offset).limit(limit)
    
    events = []
    for document in cursor:
        events.append(serialize_event(document))
    
    return events


def get_event_count(action=None):
    collection = get_collection()
    
    query = {}
    if action:
        query["action"] = action.upper()
    
    return collection.count_documents(query)


def serialize_event(document):
    return {
        "id": str(document["_id"]),
        "request_id": document["request_id"],
        "author": document["author"],
        "action": document["action"],
        "from_branch": document["from_branch"],
        "to_branch": document["to_branch"],
        "timestamp": document["timestamp"].isoformat() if document.get("timestamp") else None,
        "created_at": document["created_at"].isoformat() if document.get("created_at") else None
    }