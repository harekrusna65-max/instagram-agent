"""
Post & Reel Publishing and Scheduling Service
"""

from typing import Dict, Any, Optional
from pathlib import Path
from core.client import InstagramAgentClient
from database.db import (
    add_scheduled_post,
    get_pending_scheduled_posts,
    mark_post_published,
    mark_post_failed,
    record_quote_published
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
            video_p = Path(media_path)
            thumb_p = video_p.with_suffix(".jpg")
            thumb_str = str(thumb_p) if thumb_p.exists() else None
            media = self.client.post_reel(media_path, caption, thumbnail_path=thumb_str)
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

    def process_pending_scheduled(self, pipeline: Optional[Any] = None) -> int:
        """Worker cycle: checks pending scheduled posts and publishes due items."""
        due_posts = get_pending_scheduled_posts()
        count = 0
        for item in due_posts:
            try:
                m_type = (item.get("media_type") or "reel").lower()
                m_path = item.get("media_path") or ""
                print(f"[*] Publishing scheduled post ID #{item['id']} ({m_type})...")

                if m_path and Path(m_path).exists():
                    res = self.publish_now(m_path, m_type, item["caption"])
                elif pipeline:
                    # Dynamically generate and post
                    if m_type == "reel":
                        voiceover_flag = bool(item.get("use_voiceover", 0))
                        res = pipeline.create_and_post_reel(
                            hook=item.get("hook") or None,
                            quote=item.get("quote") or None,
                            caption=item.get("caption") or None,
                            duration_sec=12,
                            use_voiceover=voiceover_flag
                        )
                    else:
                        res = pipeline.create_and_post_image(
                            quote=item.get("quote") or None,
                            category=item.get("hook") or "Aesthetic",
                            caption=item.get("caption") or None
                        )
                else:
                    raise FileNotFoundError(f"Media file not found at '{m_path}' and pipeline not provided.")

                media_id = res.get("media_id", res.get("url", "live"))
                mark_post_published(item["id"], media_id)
                if item.get("quote"):
                    record_quote_published(
                        quote_text=item["quote"],
                        hook=item.get("hook") or "",
                        category=m_type,
                        media_type=m_type
                    )
                post_url = res.get("url", "")
                print(f"[✓] Scheduled post #{item['id']} published successfully! URL: {post_url}")
                try:
                    from services.notification_service import send_push_notification
                    send_push_notification(
                        title=f"⏰ Scheduled {m_type.upper()} Published!",
                        message=f"Post #{item['id']} is now live on Instagram: {post_url}",
                        url=post_url
                    )
                except Exception as notif_err:
                    print(f"[!] Push notification error: {notif_err}")
                count += 1
            except Exception as e:
                print(f"[!] Failed to publish scheduled post #{item['id']}: {e}")
                mark_post_failed(item["id"], str(e))
        return count
