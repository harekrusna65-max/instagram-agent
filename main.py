"""
Instagram Agent Entry Point
Run `uv run python main.py` for interactive CLI.
Run `uv run python main.py --daemon` for continuous background automation.
"""

import sys
import time

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database.db import init_db
from core.client import InstagramAgentClient
from services.ai_generator import AIGenerator
from services.post_service import PostService
from services.engagement_service import EngagementService

def run_daemon():
    print("==================================================")
    print("   INSTAGRAM AGENT - BACKGROUND DAEMON RUNNING")
    print("==================================================")
    init_db()
    client = InstagramAgentClient()
    if not client.authenticate():
        print("[!] Failed to authenticate. Please run `uv run python login_browser.py`")
        sys.exit(1)

    print(f"[✓] Authenticated as @{client.username}")
    ai = AIGenerator()
    post_service = PostService(client)
    engagement = EngagementService(client, ai)

    print("[*] Monitoring scheduled posts, comment triggers, and incoming DMs...")
    print("[*] Press Ctrl+C to stop.\n")

    while True:
        try:
            # 1. Process scheduled posts
            post_service.process_pending_scheduled()

            # 2. Process comments
            engagement.process_recent_post_comments(post_limit=3)

            # 3. Process DMs
            engagement.process_unread_dms()

            time.sleep(30)
        except KeyboardInterrupt:
            print("\nDaemon stopped by user.")
            break
        except Exception as e:
            print(f"[!] Daemon cycle exception: {e}")
            time.sleep(15)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--daemon", "-d", "worker"]:
        run_daemon()
    else:
        from cli import main
        main()
