"""
Core Instagram Client Wrapper
Handles authentication, SSL certificate configuration, and anti-ban safe pacing.
"""

import os
import sys
import ssl
import json
import time
import random
import certifi
from pathlib import Path
from typing import Optional, Dict, Any, List
from instagrapi import Client
from instagrapi.types import UserShort, Media

# Monkey-patch moviepy.VideoFileClip if moviepy is installed
try:
    import moviepy
    import moviepy.editor
    if not hasattr(moviepy, "VideoFileClip"):
        moviepy.VideoFileClip = moviepy.editor.VideoFileClip
except Exception:
    pass

# Ensure UTF-8 console output on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
SESSION_FILE = BASE_DIR / "instagrapi_session.json"
RAW_SESSION_FILE = BASE_DIR / "session.json"
CA_FILE = BASE_DIR / "cacert_win.pem"


def get_ca_bundle_path() -> str:
    """Ensure Windows Root CA bundle exists for SSL verification."""
    if not CA_FILE.exists():
        certs = ssl.enum_certificates("ROOT") + ssl.enum_certificates("CA")
        with open(CA_FILE, "w", encoding="utf-8") as f:
            with open(certifi.where(), "r", encoding="utf-8") as cf:
                f.write(cf.read())
            f.write("\n")
            for cert, encoding, trust in certs:
                if encoding == "x509_asn":
                    f.write(ssl.DER_cert_to_PEM_cert(cert) + "\n")
    
    ca_path = str(CA_FILE.resolve())
    os.environ["CURL_CA_BUNDLE"] = ca_path
    os.environ["SSL_CERT_FILE"] = ca_path
    os.environ["REQUESTS_CA_BUNDLE"] = ca_path
    return ca_path


class InstagramAgentClient:
    def __init__(self):
        self.ca_path = get_ca_bundle_path()
        self.cl = Client()
        self._configure_ssl()
        self.user_id: Optional[str] = None
        self.username: Optional[str] = None

    def _configure_ssl(self):
        """Configure SSL verification on internal adapters."""
        for adapter in list(self.cl.private.adapters.values()) + list(self.cl.public.adapters.values()):
            if hasattr(adapter, "client") and hasattr(adapter.client, "verify"):
                adapter.client.verify = self.ca_path

    def _safe_delay(self, min_sec: float = 1.5, max_sec: float = 3.5):
        """Simulate human-like behavior between actions."""
        time.sleep(random.uniform(min_sec, max_sec))

    def authenticate(self) -> bool:
        """Authenticate using stored session or environment variable."""
        # Restore session from environment variable if on cloud (Render / Docker)
        import base64
        env_b64 = os.getenv("IG_SESSION_B64")
        if env_b64 and not SESSION_FILE.exists():
            try:
                decoded = base64.b64decode(env_b64)
                with open(SESSION_FILE, "wb") as f:
                    f.write(decoded)
                print("[✓] Restored session from IG_SESSION_B64 environment variable.")
            except Exception as e:
                print(f"[!] Failed to decode IG_SESSION_B64: {e}")

        if SESSION_FILE.exists():
            try:
                self.cl.load_settings(str(SESSION_FILE))
                self._configure_ssl()
                account = self.cl.account_info()
                self.user_id = str(self.cl.user_id)
                self.username = account.username
                return True
            except Exception as e:
                print(f"[!] Saved instagrapi_session failed: {e}. Trying raw session.json...")

        if RAW_SESSION_FILE.exists():
            try:
                with open(RAW_SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sessionid = data.get("sessionid")
                if sessionid:
                    self.cl.login_by_sessionid(sessionid)
                    self._configure_ssl()
                    account = self.cl.account_info()
                    self.user_id = str(self.cl.user_id)
                    self.username = account.username
                    self.cl.dump_settings(str(SESSION_FILE))
                    return True
            except Exception as e:
                print(f"[!] Raw session login failed: {e}")
                return False

        print("[!] No valid session found. Please run `uv run python login_browser.py` first.")
        return False

    def get_account_profile(self) -> Dict[str, Any]:
        """Fetch current user profile details."""
        if not self.user_id:
            raise RuntimeError("Not authenticated")
        info = self.cl.user_info(self.user_id)
        return {
            "pk": info.pk,
            "username": info.username,
            "full_name": info.full_name,
            "follower_count": info.follower_count,
            "following_count": info.following_count,
            "media_count": info.media_count,
            "biography": info.biography,
            "external_url": info.external_url,
            "is_private": info.is_private,
        }

    def get_user_medias(self, amount: int = 10) -> List[Media]:
        """Fetch recent posts of current user."""
        if not self.user_id:
            raise RuntimeError("Not authenticated")
        return self.cl.user_medias(int(self.user_id), amount=amount)

    def post_photo(self, photo_path: str, caption: str) -> Media:
        """Upload a photo post."""
        self._safe_delay(2.0, 4.0)
        resolved_path = Path(photo_path).resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"Photo not found at {resolved_path}")
        media = self.cl.photo_upload(str(resolved_path), caption=caption)
        self._safe_delay()
        return media

    def post_reel(self, video_path: str, caption: str, thumbnail_path: Optional[str] = None) -> Media:
        """Upload a reel/video post."""
        self._safe_delay(2.0, 5.0)
        resolved_path = Path(video_path).resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"Video not found at {resolved_path}")
        media = self.cl.clip_upload(str(resolved_path), caption=caption, thumbnail=thumbnail_path)
        self._safe_delay()
        return media

    def get_direct_threads(self, amount: int = 15) -> List[Any]:
        """Fetch recent direct message inbox threads."""
        self._safe_delay(1.0, 2.5)
        return self.cl.direct_threads(amount=amount)

    def send_direct_message(self, text: str, user_ids: Optional[List[int]] = None, thread_id: Optional[str] = None) -> Any:
        """Send a direct message to a user or thread."""
        self._safe_delay(1.5, 3.5)
        if thread_id:
            return self.cl.direct_send(text, thread_ids=[thread_id])
        elif user_ids:
            return self.cl.direct_send(text, user_ids=user_ids)
        else:
            raise ValueError("Either user_ids or thread_id must be provided")

    def get_media_comments(self, media_id: str, amount: int = 20) -> List[Any]:
        """Fetch comments on a specific post."""
        self._safe_delay(1.0, 2.0)
        return self.cl.media_comments(media_id, amount=amount)

    def reply_to_comment(self, media_id: str, text: str, replied_to_comment_id: Optional[str] = None) -> Any:
        """Post a comment reply."""
        self._safe_delay(2.0, 4.0)
        return self.cl.media_comment(media_id, text, replied_to_comment_id=replied_to_comment_id)
