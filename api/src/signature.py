import hmac
import hashlib


def verify_signature(payload_body, secret, signature_header):
    if not secret:
        return True
    
    if not signature_header:
        return False
    
    if not signature_header.startswith("sha256="):
        return False
    
    expected_signature = signature_header[7:]
    
    computed_hash = hmac.new(
        secret.encode("utf-8"),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_hash, expected_signature)