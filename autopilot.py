"""
Autonomous Auto-Pilot Engine for @stanger.man69
Runs 24/7 in background:
1. Auto-creates & publishes fresh aesthetic Reels & Posts on schedule (without any human action)
2. Auto-replies to comment triggers (e.g. 'LINK') and DMs continuously
"""

import sys
import time
import schedule
from datetime import datetime
from database.db import init_db
from core.client import InstagramAgentClient
from services.auto_content_pipeline import AutoContentPipeline
from services.ai_generator import AIGenerator
from services.post_service import PostService
from services.engagement_service import EngagementService

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def job_publish_reel(pipeline: AutoContentPipeline):
    print(f"\n[🤖 AUTOPILOT] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Auto-creating & uploading fresh Reel...")
    try:
        res = pipeline.create_and_post_reel(duration_sec=12, use_voiceover=False)
        print(f"[✓ AUTOPILOT] Reel published successfully! URL: {res.get('url')}")
    except Exception as e:
        print(f"[! AUTOPILOT] Reel upload error: {e}")

def job_publish_post(pipeline: AutoContentPipeline):
    print(f"\n[🤖 AUTOPILOT] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Auto-creating & uploading fresh Image Post...")
    try:
        res = pipeline.create_and_post_image()
        print(f"[✓ AUTOPILOT] Post published successfully! URL: {res.get('url')}")
    except Exception as e:
        print(f"[! AUTOPILOT] Post upload error: {e}")

def run_autopilot(reels_per_day: int = 2, posts_per_day: int = 1):
    print("==================================================")
    print("      INSTAGRAM 24/7 AUTONOMOUS AUTO-PILOT")
    print("==================================================")
    print(f"Target: {reels_per_day} Reels/day + {posts_per_day} Posts/day")
    print("Anti-Duplicate: 100% Guaranteed Fresh Quotes from Vault")
    print("Engagement: Continuous DM & Comment Auto-Responder Active")
    print("==================================================\n")

    init_db()
    client = InstagramAgentClient()
    if not client.authenticate():
        print("[!] Authentication failed. Run login first.")
        sys.exit(1)

    print(f"[✓] Authenticated as @{client.username}")
    pipeline = AutoContentPipeline(client)
    ai = AIGenerator()
    post_service = PostService(client)
    engagement = EngagementService(client, ai)

    # Schedule daily postings:
    # Schedule Reel 1 at 11:00 AM, Reel 2 at 07:00 PM (peak Instagram viral hours in IST)
    # Schedule Post at 03:00 PM
    schedule.every().day.at("11:00").do(job_publish_reel, pipeline)
    schedule.every().day.at("19:00").do(job_publish_reel, pipeline)
    schedule.every().day.at("15:00").do(job_publish_post, pipeline)

    print("[*] Schedules Active:")
    print("    - 11:00 AM: Reel 1 (Morning Viral Window)")
    print("    - 03:00 PM: Aesthetic Image Post")
    print("    - 07:00 PM: Reel 2 (Evening Peak Viral Window)")
    print("\n[*] Listening for DMs, comments, and scheduled triggers... Press Ctrl+C to stop.\n")

    while True:
        try:
            # 1. Run any scheduled tasks due
            schedule.run_pending()

            # 2. Process manual queued posts from SQLite
            post_service.process_pending_scheduled()

            # 3. Check for new comments (auto-reply & DM)
            engagement.process_recent_post_comments(post_limit=3)

            # 4. Check for new DMs (AI reply)
            engagement.process_unread_dms()

            time.sleep(30)
        except KeyboardInterrupt:
            print("\nAuto-Pilot stopped by user.")
            break
        except Exception as e:
            print(f"[!] Auto-Pilot loop exception: {e}")
            time.sleep(15)

if __name__ == "__main__":
    run_autopilot()
