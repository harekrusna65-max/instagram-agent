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

from database.db import (
    init_db,
    get_unused_quote_count,
    is_slot_done_today,
    record_slot_done,
    get_today_slots_status,
    add_scheduled_item,
    get_all_scheduled_posts,
    delete_scheduled_post
)
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
ai_generator = None
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
    print("[* SERVER] Background Auto-Pilot IST slot-window scheduler started...")

    while True:
        try:
            now_ist = datetime.now(IST)
            today_date = now_ist.strftime("%Y-%m-%d")
            hour = now_ist.hour

            # Auto-reconnect if pipeline not ready
            if pipeline is None:
                init_agent()

            # 1. Slot 1: Morning Reel (Active window: 11:00 AM - 02:59 PM IST)
            if 11 <= hour < 15 and not is_slot_done_today("morning_reel", today_date):
                print(f"[*] [IST Morning Slot] Triggering Morning Reel for {today_date}...")
                if pipeline:
                    res = pipeline.create_and_post_reel(duration_sec=12, use_voiceover=False)
                    media_url = res.get("url", "")
                    record_slot_done("morning_reel", today_date, media_url)
                    last_post_info = f"Morning Reel published at {now_ist.strftime('%I:%M %p')}: {media_url}"
                    print(f"[✓] Morning Reel recorded in daily log: {media_url}")

            # 2. Slot 2: Afternoon Post (Active window: 03:00 PM - 06:59 PM IST)
            elif 15 <= hour < 19 and not is_slot_done_today("afternoon_post", today_date):
                print(f"[*] [IST Afternoon Slot] Triggering Afternoon Image Post for {today_date}...")
                if pipeline:
                    res = pipeline.create_and_post_image()
                    media_url = res.get("url", "")
                    record_slot_done("afternoon_post", today_date, media_url)
                    last_post_info = f"Afternoon Post published at {now_ist.strftime('%I:%M %p')}: {media_url}"
                    print(f"[✓] Afternoon Post recorded in daily log: {media_url}")

            # 3. Slot 3: Evening Prime-Time Reel (Active window: 07:00 PM - 11:59 PM IST)
            elif 19 <= hour <= 23 and not is_slot_done_today("evening_reel", today_date):
                print(f"[*] [IST Evening Slot] Triggering Evening Reel for {today_date}...")
                if pipeline:
                    res = pipeline.create_and_post_reel(duration_sec=12, use_voiceover=False)
                    media_url = res.get("url", "")
                    record_slot_done("evening_reel", today_date, media_url)
                    last_post_info = f"Evening Reel published at {now_ist.strftime('%I:%M %p')}: {media_url}"
                    print(f"[✓] Evening Reel recorded in daily log: {media_url}")

            # Process custom scheduled posts queue
            if post_service and pipeline:
                post_service.process_pending_scheduled(pipeline)
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

@app.get("/api/status")
def api_status():
    """API endpoint returning raw system status JSON with IST awareness and slot tracking."""
    now_ist = datetime.now(IST)
    is_authed = bool(client and client.username and pipeline is not None)
    today_date = now_ist.strftime("%Y-%m-%d")
    slots_done = get_today_slots_status(today_date)
    
    # Calculate next scheduled post in IST
    curr_h_m = now_ist.strftime("%H:%M")
    if curr_h_m < "11:00":
        next_post = "Today 11:00 AM IST (Aesthetic Reel)"
    elif curr_h_m < "15:00":
        next_post = "Done: Morning Reel" if slots_done["morning_reel"] else "Catching up: Morning Reel"
        if curr_h_m >= "11:00" and not slots_done["afternoon_post"]:
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
        "today_slots_published": slots_done,
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

@app.get("/api/generate/shayari")
@app.post("/api/generate/shayari")
def api_generate_shayari(topic: str = "sukoon"):
    """1-Tap AI generator for viral hook & poetry lines based on mood."""
    global ai_generator
    if ai_generator is None:
        ai_generator = AIGenerator()
    data = ai_generator.generate_ai_shayari(topic=topic)
    return {"status": "success", **data}

@app.get("/api/schedule/list")
def api_schedule_list():
    """Returns list of pending and recent scheduled posts."""
    try:
        items = get_all_scheduled_posts(limit=20)
        return {"status": "success", "items": items}
    except Exception as e:
        return {"status": "error", "message": str(e), "items": []}

@app.post("/api/schedule")
async def api_schedule_post(request: Request):
    """
    Schedules an auto reel or image post at a specific future IST timestamp.
    Accepts: { media_type: 'reel'|'post', scheduled_time: 'YYYY-MM-DD HH:MM', hook, quote, caption }
    """
    try:
        data = await request.json()
        media_type = (data.get("media_type") or "reel").lower().strip()
        raw_time = (data.get("scheduled_time") or "").strip()
        hook = data.get("hook")
        quote = data.get("quote")
        caption = data.get("caption")

        if not raw_time:
            return {"status": "error", "message": "Scheduled time is required (e.g. 2026-11-02 18:30)."}

        # Normalize time format: replace 'T' with ' ' and ensure seconds
        clean_time = raw_time.replace("T", " ").strip()
        if len(clean_time) == 16:  # 'YYYY-MM-DD HH:MM'
            clean_time += ":00"

        # Check that scheduled time is valid and in future (IST)
        now_ist = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
        if clean_time <= now_ist:
            return {
                "status": "error", 
                "message": f"Scheduled time ({clean_time} IST) must be in the future! Current IST is {now_ist}."
            }

        post_id = add_scheduled_item(
            media_type=media_type,
            scheduled_time=clean_time,
            hook=hook,
            quote=quote,
            caption=caption
        )

        return {
            "status": "success",
            "message": f"Successfully scheduled {media_type.upper()} for {clean_time} IST!",
            "id": post_id
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/schedule/delete/{post_id}")
def api_schedule_delete(post_id: int):
    """Cancels/deletes a pending scheduled post."""
    try:
        success = delete_scheduled_post(post_id)
        if success:
            return {"status": "success", "message": f"Scheduled item #{post_id} cancelled."}
        return {"status": "error", "message": f"Item #{post_id} not found or already published."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
