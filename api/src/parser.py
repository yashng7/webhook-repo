from datetime import datetime, timezone


def parse_event(event_type, delivery_id, payload):
    if event_type == "push":
        return parse_push(delivery_id, payload)
    
    if event_type == "pull_request":
        return parse_pull_request(delivery_id, payload)
    
    return None


def parse_push(delivery_id, payload):
    ref = payload.get("ref", "")
    to_branch = extract_branch_name(ref)
    
    pusher = payload.get("pusher", {})
    author = pusher.get("name", "unknown")
    
    head_commit = payload.get("head_commit", {})
    timestamp = head_commit.get("timestamp")
    
    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()
    
    return {
        "request_id": delivery_id,
        "author": author,
        "action": "PUSH",
        "from_branch": None,
        "to_branch": to_branch,
        "timestamp": normalize_timestamp(timestamp),
        "raw_payload": payload
    }


def parse_pull_request(delivery_id, payload):
    pr_action = payload.get("action", "")
    pull_request = payload.get("pull_request", {})
    merged = pull_request.get("merged", False)
    
    if pr_action == "closed" and merged:
        return parse_merge(delivery_id, payload)
    
    if pr_action in ("opened", "synchronize", "reopened"):
        return parse_pr_opened(delivery_id, payload)
    
    return None


def parse_pr_opened(delivery_id, payload):
    pull_request = payload.get("pull_request", {})
    
    user = pull_request.get("user", {})
    author = user.get("login", "unknown")
    
    head = pull_request.get("head", {})
    base = pull_request.get("base", {})
    from_branch = head.get("ref", "unknown")
    to_branch = base.get("ref", "unknown")
    
    timestamp = pull_request.get("updated_at") or pull_request.get("created_at")
    
    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()
    
    return {
        "request_id": delivery_id,
        "author": author,
        "action": "PULL_REQUEST",
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": normalize_timestamp(timestamp),
        "raw_payload": payload
    }


def parse_merge(delivery_id, payload):
    pull_request = payload.get("pull_request", {})
    
    merged_by = pull_request.get("merged_by", {})
    author = merged_by.get("login")
    
    if not author:
        user = pull_request.get("user", {})
        author = user.get("login", "unknown")
    
    head = pull_request.get("head", {})
    base = pull_request.get("base", {})
    from_branch = head.get("ref", "unknown")
    to_branch = base.get("ref", "unknown")
    
    timestamp = pull_request.get("merged_at")
    
    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()
    
    return {
        "request_id": delivery_id,
        "author": author,
        "action": "MERGE",
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": normalize_timestamp(timestamp),
        "raw_payload": payload
    }


def extract_branch_name(ref):
    prefix = "refs/heads/"
    if ref.startswith(prefix):
        return ref[len(prefix):]
    return ref


def normalize_timestamp(timestamp):
    if isinstance(timestamp, datetime):
        return timestamp
    
    if isinstance(timestamp, str):
        try:
            normalized = timestamp.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except ValueError:
            pass
    
    return datetime.now(timezone.utc)