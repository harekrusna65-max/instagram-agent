"""
Analytics & Performance Service
"""

from typing import Dict, Any, List
from core.client import InstagramAgentClient

class AnalyticsService:
    def __init__(self, client: InstagramAgentClient):
        self.client = client

    def get_summary(self) -> Dict[str, Any]:
        """Fetch full account metrics and recent post performance."""
        profile = self.client.get_account_profile()
        medias = self.client.get_user_medias(amount=10)

        total_likes = 0
        total_comments = 0
        posts_data = []

        for m in medias:
            likes = getattr(m, "like_count", 0) or 0
            comments = getattr(m, "comment_count", 0) or 0
            total_likes += likes
            total_comments += comments

            posts_data.append({
                "id": m.id,
                "code": m.code,
                "type": "reel" if getattr(m, "media_type", 1) == 2 else "photo",
                "likes": likes,
                "comments": comments,
                "url": f"https://www.instagram.com/p/{m.code}/",
                "taken_at": str(m.taken_at) if hasattr(m, "taken_at") else ""
            })

        avg_likes = (total_likes / len(medias)) if medias else 0
        avg_comments = (total_comments / len(medias)) if medias else 0
        followers = profile.get("follower_count", 0) or 1
        engagement_rate = round(((avg_likes + avg_comments) / followers) * 100, 2) if followers else 0

        return {
            "profile": profile,
            "metrics": {
                "posts_analyzed": len(medias),
                "total_likes_recent": total_likes,
                "total_comments_recent": total_comments,
                "avg_likes": round(avg_likes, 1),
                "avg_comments": round(avg_comments, 1),
                "est_engagement_rate": f"{engagement_rate}%"
            },
            "recent_posts": posts_data
        }
