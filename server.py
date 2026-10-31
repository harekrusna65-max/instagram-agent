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
from datetime import datetime, timezone, timedelta
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse, HTMLResponse

# Force UTF-8 on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
IST = timezone(timedelta(hours=5, minutes=30))

from database.db import init_db, get_unused_quote_count
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

# Global instances & status tracking
client = None
pipeline = None
post_service = None
engagement = None
analytics = None
scheduler_running = False
last_run_events = {}
last_post_info = "None yet"

def init_agent() -> bool:
    global client, pipeline, post_service, engagement, analytics
    try:
        if client is None:
            client = InstagramAgentClient()
        if client.authenticate():
            if pipeline is None:
                pipeline = AutoContentPipeline(client)
                ai = AIGenerator()
                post_service = PostService(client)
                engagement = EngagementService(client, ai)
                analytics = AnalyticsService(client)
            print(f"[✓ SERVER] Authenticated as @{client.username}")
            return True
        else:
            print("[!] Authentication failed on server. Waiting for fresh session.")
            return False
    except Exception as e:
        print(f"[!] Error in init_agent: {e}")
        return False

def bg_scheduler_loop():
    global scheduler_running, last_post_info
    scheduler_running = True
    print("[* SERVER] Background Auto-Pilot IST scheduler thread started...")

    while True:
        try:
            now_ist = datetime.now(IST)
            current_date_str = now_ist.strftime("%Y-%m-%d")
            current_time_str = now_ist.strftime("%H:%M")

            # Try to initialize if not authenticated yet (every 2 minutes)
            if pipeline is None and now_ist.second < 30:
                init_agent()

            # Scheduled Slots in Indian Standard Time (IST):
            # 1. 11:00 AM IST -> Aesthetic Video Reel
            if current_time_str == "11:00" and last_run_events.get("reel_1") != current_date_str:
                last_run_events["reel_1"] = current_date_str
                print(f"[*] [IST 11:00 AM] Triggering Morning Reel...")
                if pipeline:
                    res = pipeline.create_and_post_reel(duration_sec=12, use_voiceover=False)
                    last_post_info = f"Reel published at {now_ist.strftime('%I:%M %p')}: {res.get('url', 'success')}"

            # 2. 03:00 PM IST -> Ultra-Aesthetic Graphic Post
            elif current_time_str == "15:00" and last_run_events.get("post_1") != current_date_str:
                last_run_events["post_1"] = current_date_str
                print(f"[*] [IST 03:00 PM] Triggering Afternoon Image Post...")
                if pipeline:
                    res = pipeline.create_and_post_image()
                    last_post_info = f"Post published at {now_ist.strftime('%I:%M %p')}: {res.get('url', 'success')}"

            # 3. 07:00 PM IST -> Prime-Time Viral Reel
            elif current_time_str == "19:00" and last_run_events.get("reel_2") != current_date_str:
                last_run_events["reel_2"] = current_date_str
                print(f"[*] [IST 07:00 PM] Triggering Prime-Time Reel...")
                if pipeline:
                    res = pipeline.create_and_post_reel(duration_sec=12, use_voiceover=False)
                    last_post_info = f"Reel published at {now_ist.strftime('%I:%M %p')}: {res.get('url', 'success')}"

            # Background community engagement & scheduled tasks
            if post_service:
                post_service.process_pending_scheduled()
            if engagement and now_ist.minute % 15 == 0 and now_ist.second < 30:
                engagement.process_recent_post_comments(post_limit=3)
                engagement.process_unread_dms()

            time.sleep(25)
        except Exception as e:
            print(f"[! SERVER] Scheduler loop exception: {e}")
            time.sleep(15)

@app.on_event("startup")
def startup_event():
    init_agent()
    # Start scheduler thread
    t = threading.Thread(target=bg_scheduler_loop, daemon=True)
    t.start()

@app.get("/", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    """
    Renders the modern Glassmorphism Cloud Admin Panel for @stanger.man69.
    Also returns 200 OK for UptimeRobot keep-alive pings.
    """
    admin_html_file = TEMPLATES_DIR / "admin.html"
    if admin_html_file.exists():
        with open(admin_html_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    
    # Fallback minimal HTML
    return HTMLResponse("<h1>Instagram AI Studio Online</h1><p>Status: Active</p>")

from database.db import get_unused_quote_count

@app.get("/api/status")
def api_status():
    """API endpoint returning raw system status JSON with IST awareness."""
    now_ist = datetime.now(IST)
    is_authed = bool(client and client.username and pipeline is not None)
    
    # Calculate next scheduled post in IST
    curr_h_m = now_ist.strftime("%H:%M")
    if curr_h_m < "11:00":
        next_post = "Today 11:00 AM IST (Aesthetic Reel)"
    elif curr_h_m < "15:00":
        next_post = "Today 03:00 PM IST (Image Post)"
    elif curr_h_m < "19:00":
        next_post = "Today 07:00 PM IST (Prime-Time Reel)"
    else:
        next_post = "Tomorrow 11:00 AM IST (Aesthetic Reel)"

    return {
        "status": "online",
        "service": "Instagram AI Agent",
        "account": f"@{client.username}" if is_authed else "Session Expired (Login Required)",
        "session_authenticated": is_authed,
        "vault_quotes_ready": get_unused_quote_count(),
        "hashtag_engine": "Smart Anti-Shadowban Rotator Active",
        "uptimerobot_keep_alive": "active",
        "scheduler": "running" if scheduler_running else "idle",
        "ist_time": now_ist.strftime("%Y-%m-%d %I:%M:%S %p IST"),
        "next_scheduled_post": next_post,
        "last_post_info": last_post_info,
        "server_utc_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

@app.post("/api/update_session")
async def update_session(request: Request):
    """Allows uploading new session.json or b64 string directly to server without manual redeploy."""
    try:
        body = await request.json()
        raw_b64 = body.get("b64") or body.get("session_b64")
        if raw_b64:
            session_bytes = base64.b64decode(raw_b64)
            session_file = BASE_DIR / "instagrapi_session.json"
            with open(session_file, "wb") as f:
                f.write(session_bytes)
            
            # Re-init agent
            success = init_agent()
            if success:
                return {"status": "success", "message": f"Session updated! Authenticated as @{client.username}"}
            else:
                return {"status": "error", "message": "Session written, but authentication failed with Instagram."}
        return {"status": "error", "message": "Missing 'b64' in request body."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
