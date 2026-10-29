"""
FastAPI Server for Render Deployment + UptimeRobot Keep-Alive
- Keeps server awake 24/7 via UptimeRobot pings
- Runs Auto-Pilot background scheduler (daily Reels & Posts)
- Continuous Comment & DM Auto-Responder
- Webhook / HTTP endpoints to trigger manual posts or check stats
"""

import os
import sys
import time
import base64
import threading
import schedule
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse

# Force UTF-8 on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database.db import init_db
from core.client import InstagramAgentClient
from services.auto_content_pipeline import AutoContentPipeline
from services.ai_generator import AIGenerator
from services.post_service import PostService
from services.engagement_service import EngagementService
from services.analytics_service import AnalyticsService

init_db()

app = FastAPI(
    title="Instagram Agent Cloud Server",
    description="24/7 Cloud Handler for @stanger.man69 with UptimeRobot Support"
)

# Global instances
client = None
pipeline = None
post_service = None
engagement = None
analytics = None
scheduler_running = False

def init_agent():
    global client, pipeline, post_service, engagement, analytics
    try:
        if client is None:
            client = InstagramAgentClient()
            if client.authenticate():
                pipeline = AutoContentPipeline(client)
                ai = AIGenerator()
                post_service = PostService(client)
                engagement = EngagementService(client, ai)
                analytics = AnalyticsService(client)
                print(f"[✓ SERVER] Authenticated as @{client.username}")
            else:
                print("[!] Authentication failed on server. Waiting for IG_SESSION_B64.")
    except Exception as e:
        print(f"[!] Error in init_agent: {e}")

def bg_scheduler_loop():
    global scheduler_running
    scheduler_running = True
    print("[* SERVER] Background Auto-Pilot scheduler thread started...")

    # Schedule times (IST times converted or daily triggers)
    # Daily Reel 1 at 11:00 AM, Post at 03:00 PM, Reel 2 at 07:00 PM
    schedule.every().day.at("11:00").do(lambda: pipeline.create_and_post_reel(duration_sec=12, use_voiceover=False) if pipeline else None)
    schedule.every().day.at("15:00").do(lambda: pipeline.create_and_post_image() if pipeline else None)
    schedule.every().day.at("19:00").do(lambda: pipeline.create_and_post_reel(duration_sec=12, use_voiceover=False) if pipeline else None)

    while True:
        try:
            schedule.run_pending()
            if post_service:
                post_service.process_pending_scheduled()
            if engagement:
                engagement.process_recent_post_comments(post_limit=3)
                engagement.process_unread_dms()
            time.sleep(30)
        except Exception as e:
            print(f"[! SERVER] Scheduler error: {e}")
            time.sleep(15)

@app.on_event("startup")
def startup_event():
    init_agent()
    # Start scheduler thread
    t = threading.Thread(target=bg_scheduler_loop, daemon=True)
    t.start()

@app.get("/")
def home():
    """UptimeRobot ping endpoint to keep Render awake 24/7."""
    return {
        "status": "online",
        "service": "Instagram AI Agent",
        "account": f"@{client.username}" if client and client.username else "Authenticating...",
        "uptimerobot_keep_alive": "active",
        "scheduler": "running" if scheduler_running else "idle",
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": time.time()}

@app.get("/stats")
def get_stats():
    if not analytics:
        return {"error": "Client not initialized"}
    try:
        return analytics.get_summary()
    except Exception as e:
        return {"error": str(e)}

@app.get("/trigger/reel")
@app.post("/trigger/reel")
def trigger_reel(background_tasks: BackgroundTasks, hook: str = None, quote: str = None):
    """Trigger an instant 12s Reel creation and upload."""
    if not pipeline:
        return {"error": "Pipeline not initialized"}
    
    def task():
        pipeline.create_and_post_reel(hook=hook, quote=quote, duration_sec=12, use_voiceover=False)

    background_tasks.add_task(task)
    return {"status": "success", "message": "Reel generation and upload started in background."}

@app.get("/trigger/post")
@app.post("/trigger/post")
def trigger_post(background_tasks: BackgroundTasks, quote: str = None, category: str = None):
    """Trigger an instant Image Post creation and upload."""
    if not pipeline:
        return {"error": "Pipeline not initialized"}
    
    def task():
        pipeline.create_and_post_image(quote=quote, category=category)

    background_tasks.add_task(task)
    return {"status": "success", "message": "Image Post generation and upload started in background."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
