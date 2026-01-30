from datetime import datetime, timezone


VALID_ACTIONS = {"PUSH", "PULL_REQUEST", "MERGE"}


def create_event(request_id, author, action, to_branch, from_branch=None, 
                 timestamp=None, raw_payload=None):
    
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid action: {action}. Must be one of {VALID_ACTIONS}")
    
    if not request_id:
        raise ValueError("request_id is required")
    
    if not author:
        raise ValueError("author is required")
    
    if not to_branch:
        raise ValueError("to_branch is required")
    
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    elif isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    
    return {
        "request_id": request_id,
        "author": author,
        "action": action,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": timestamp,
        "raw_payload": raw_payload or {},
        "created_at": datetime.now(timezone.utc)
    }


def validate_event(event):
    required_fields = ["request_id", "author", "action", "to_branch", "timestamp"]
    
    for field in required_fields:
        if field not in event or event[field] is None:
            return False, f"Missing required field: {field}"
    
    if event["action"] not in VALID_ACTIONS:
        return False, f"Invalid action: {event['action']}"
    
    return True, None