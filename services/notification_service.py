"""
Push Notification Service for Instagram Agent
Dispatches real-time alerts to phone via ntfy.sh and logs notifications in DB.
"""

import os
from typing import Optional, Dict, Any, List
from database.db import record_notification, get_recent_notifications

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import requests

NTFY_TOPIC = os.getenv("NTFY_TOPIC", "stanger_man69_alerts")


def send_push_notification(title: str, message: str, url: str = "", tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Sends an immediate push notification to the user's phone via ntfy.sh
    and records it into the local database history.
    Uses JSON payload for full emoji and unicode support.
    """
    try:
        record_notification(title, message, url)
    except Exception as e:
        print(f"[PUSH DB] Notice: {e}")

    payload = {
        "topic": NTFY_TOPIC,
        "title": title,
        "message": message,
        "tags": tags or ["tada", "instagram"],
        "priority": 4
    }
    if url:
        payload["click"] = url

    try:
        res = requests.post(
            "https://ntfy.sh",
            json=payload,
            timeout=8
        )
        safe_title = title.encode("ascii", "replace").decode("ascii")
        print(f"[PUSH] Sent notification '{safe_title}' (status: {res.status_code})")
        return {"status": "success", "http_code": res.status_code}
    except Exception as e:
        print(f"[PUSH ERROR] Failed to send push notification: {e}")
        return {"status": "error", "message": str(e)}
