"""
Post & Reel Publishing and Scheduling Service
"""

from typing import Dict, Any, Optional
from core.client import InstagramAgentClient
from database.db import (
    add_scheduled_post,
    get_pending_scheduled_posts,
    mark_post_published,
    mark_post_failed
)

class PostService:
    def __init__(self, client: InstagramAgentClient):
        self.client = client

    def publish_now(self, media_path: str, media_type: str, caption: str) -> Dict[str, Any]:
        """Publish photo or reel immediately."""
        media_type = media_type.lower()
        if media_type == "photo":
            media = self.client.post_photo(media_path, caption)
        elif media_type == "reel":
            media = self.client.post_reel(media_path, caption)
        else:
            raise ValueError(f"Unsupported media type: {media_type}. Must be 'photo' or 'reel'.")

        return {
            "success": True,
            "media_id": media.id,
            "code": getattr(media, "code", None),
            "url": f"https://www.instagram.com/p/{media.code}/" if getattr(media, "code", None) else None
        }

    def schedule(self, media_path: str, media_type: str, caption: str, scheduled_time: str) -> int:
        """Schedule a post for future publishing (Format: YYYY-MM-DD HH:MM:SS)."""
        post_id = add_scheduled_post(media_path, media_type, caption, scheduled_time)
        return post_id

    def process_pending_scheduled(self) -> int:
        """Worker cycle: checks pending scheduled posts and publishes due items."""
        due_posts = get_pending_scheduled_posts()
        count = 0
        for item in due_posts:
            try:
                print(f"[*] Publishing scheduled post ID #{item['id']} ({item['media_type']})...")
                res = self.publish_now(item["media_path"], item["media_type"], item["caption"])
                mark_post_published(item["id"], res["media_id"])
                print(f"[✓] Published successfully! Post URL: {res['url']}")
                count += 1
            except Exception as e:
                print(f"[!] Failed to publish scheduled post #{item['id']}: {e}")
                mark_post_failed(item["id"], str(e))
        return count
