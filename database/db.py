"""
SQLite Database Layer for Instagram Agent
Manages scheduled posts, comment triggers, DM auto-reply logs, and leads.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "agent_data.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Scheduled posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_path TEXT NOT NULL DEFAULT '',
                media_type TEXT NOT NULL DEFAULT 'photo', -- 'photo' or 'reel'
                caption TEXT NOT NULL DEFAULT '',
                scheduled_time TEXT NOT NULL, -- ISO timestamp 'YYYY-MM-DD HH:MM:SS'
                status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'published', 'failed'
                media_id TEXT,
                error_message TEXT,
                hook TEXT,
                quote TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: ensure hook and quote columns exist
        try:
            cursor.execute("ALTER TABLE scheduled_posts ADD COLUMN hook TEXT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE scheduled_posts ADD COLUMN quote TEXT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE scheduled_posts ADD COLUMN use_voiceover INTEGER DEFAULT 0")
        except Exception:
            pass

        # Comment & DM Keyword Rules
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keyword_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL UNIQUE,
                reply_comment TEXT,
                reply_dm TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Processed interactions log (Anti-duplicate tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_type TEXT NOT NULL, -- 'comment' or 'dm'
                external_id TEXT NOT NULL UNIQUE, -- comment_id or message_id
                user_id TEXT,
                username TEXT,
                message_text TEXT,
                action_taken TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Leads Captured
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                source TEXT NOT NULL, -- 'comment_trigger' or 'dm'
                keyword TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Content Vault for Quotes & Shayari (Guarantees fresh, never-repeated content)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                hook TEXT NOT NULL,
                quote TEXT NOT NULL UNIQUE,
                caption TEXT NOT NULL,
                is_used INTEGER DEFAULT 0,
                used_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Permanent Published Archive (Strict Anti-Duplicate Guarantee across entire lifetime)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS published_quotes_archive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_hash TEXT NOT NULL UNIQUE,
                hook TEXT,
                quote TEXT NOT NULL,
                category TEXT,
                media_type TEXT,
                published_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bulletproof Daily Autopilot Execution Tracker
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_autopilot_log (
                date TEXT NOT NULL, -- 'YYYY-MM-DD'
                slot TEXT NOT NULL, -- 'morning_reel', 'afternoon_post', 'evening_reel'
                status TEXT NOT NULL, -- 'published'
                media_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (date, slot)
            )
        """)

        # Real-Time Push Notifications History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                url TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default keyword rules if empty
        cursor.execute("SELECT COUNT(*) as count FROM keyword_rules")
        if cursor.fetchone()["count"] == 0:
            cursor.executemany("""
                INSERT INTO keyword_rules (keyword, reply_comment, reply_dm)
                VALUES (?, ?, ?)
            """, [
                ("sukoon", "Inbox check kijiye bhai 🖤 Sent you the full poetry in DM!", "Hey {name}! Sukoon shayari ka khajana aapke liye hazir hai: 'Khamoshi me bhi ek mayaar hota hai, sukoon unhe milta hai jo shukr karna jaante hain.' 🖤✨"),
                ("shayari", "DM sent! Check your message requests 📩", "Shukriya bhai support ke liye! Ye rahi aapki special shayari: 'Apni keemat itni badhao ki log milne ko tarsein.' ⚡🔥"),
                ("link", "Sent you the details in DM! Check your inbox 🚀", "Hey there! Thanks for your interest. Here is the link you requested: https://instagram.com/stanger.man69"),
                ("info", "DM sent! Please check your message requests 📨", "Hey {name}! Thanks for reaching out. Here is all the info you need.")
            ])

        conn.commit()
    
    # Seed quotes vault
    seed_content_vault()


# --- Scheduled Posts Helpers ---
def add_scheduled_item(
    media_type: str,
    scheduled_time: str,
    hook: Optional[str] = None,
    quote: Optional[str] = None,
    caption: Optional[str] = None,
    media_path: str = "",
    use_voiceover: bool = False
) -> int:
    """Schedule a post or reel for future publishing (scheduled_time in 'YYYY-MM-DD HH:MM:SS' format)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scheduled_posts (media_path, media_type, caption, scheduled_time, status, hook, quote, use_voiceover)
            VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)
        """, (media_path, media_type.lower(), caption or "", scheduled_time, hook, quote, 1 if use_voiceover else 0))
        conn.commit()
        return cursor.lastrowid


def add_scheduled_post(media_path: str, media_type: str, caption: str, scheduled_time: str) -> int:
    return add_scheduled_item(media_type=media_type, scheduled_time=scheduled_time, caption=caption, media_path=media_path)


def get_pending_scheduled_posts(now_str: Optional[str] = None) -> List[Dict[str, Any]]:
    if not now_str:
        # Default to current IST time
        from datetime import timezone, timedelta
        ist_now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
        now_str = ist_now.strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM scheduled_posts 
            WHERE status = 'pending' AND scheduled_time <= ?
            ORDER BY scheduled_time ASC
        """, (now_str,))
        return [dict(row) for row in cursor.fetchall()]


def get_all_scheduled_posts(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves scheduled posts for the admin queue."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM scheduled_posts 
            ORDER BY 
                CASE status WHEN 'pending' THEN 0 ELSE 1 END,
                scheduled_time DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]


def delete_scheduled_post(post_id: int) -> bool:
    """Cancels/deletes a pending scheduled post."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scheduled_posts WHERE id = ? AND status = 'pending'", (post_id,))
        conn.commit()
        return cursor.rowcount > 0


def mark_post_published(post_id: int, media_id: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE scheduled_posts 
            SET status = 'published', media_id = ? 
            WHERE id = ?
        """, (media_id, post_id))
        conn.commit()


def mark_post_failed(post_id: int, error: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE scheduled_posts 
            SET status = 'failed', error_message = ? 
            WHERE id = ?
        """, (error, post_id))
        conn.commit()


# --- Anti-Duplicate Interaction Helpers ---
def is_interaction_processed(external_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM processed_interactions WHERE external_id = ?", (str(external_id),))
        return cursor.fetchone() is not None


def record_processed_interaction(interaction_type: str, external_id: str, user_id: str, username: str, text: str, action: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO processed_interactions (interaction_type, external_id, user_id, username, message_text, action_taken)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (interaction_type, str(external_id), str(user_id), username, text, action))
        conn.commit()


# --- Content Vault & Fresh Quote Helpers ---
SEEDED_QUOTES = [
    {
        "category": "DEEP LIFE",
        "hook": "Ye baat hamesha yaad rakhna...",
        "quote": "Waqt sabko milta hai zindagi badalne ke liye,\nPar zindagi dobara nahi milti\nwaqt badalne ke liye.",
        "caption": "Waqt ki kadar karo, ye wapas nahi aata ✨⏳\n\n#deepquotes #lifelessons #mindset #timeisprecious #motivation #explorepage #stangerman69"
    },
    {
        "category": "AESTHETIC SHAYARI",
        "hook": "Kuch baatein dil me hi behtar hain...",
        "quote": "Kuch baatein dil me hi achi lagti hain,\nLafzon me aakar\nwo apna wazan kho deti hain.",
        "caption": "Har baat bayan karna zaroori nahi hota 🤫✨\n\n#aesthetic #shayari #poetry #dilkibaat #khamoshi #explore #stangerman69"
    },
    {
        "category": "SELF RESPECT",
        "hook": "Apna mayaar uncha rakho...",
        "quote": "Raaste akele tai karne ka ek alag nasha hai,\nNa kisi ke peeche chalne ki chahat,\nNa kisi ke chhootne ka darr.",
        "caption": "Akele chalna seekho, bheed me bheed mat bano 🔥💯\n\n#selfrespect #attitude #focus #solitude #mindset #motivation #stangerman69"
    },
    {
        "category": "EMOTIONAL & LOVE",
        "hook": "Ek sach jo sabhi jaante hain...",
        "quote": "Kehte hain waqt ke sath sab theek ho jaata hai,\nLekin waqt ke sath bas aadat padti hai,\nDard wahi rehta hai.",
        "caption": "Dard chalta rehta hai, bas hum aage badh jaate hain 💔🥀\n\n#lovestatus #sadshayari #hearttouching #aestheticquotes #emotions #stangerman69"
    },
    {
        "category": "TRUST & RELATIONSHIPS",
        "hook": "Rishton ka sabse bada sabak...",
        "quote": "Apno ki mehfil me jab gairon sa ehsaas hone lage,\nToh samajh lena dooriyan faaslon se nahi,\nDil se aayi hain.",
        "caption": "Faasle dilon me hote hain, shehron me nahi ✨📌\n\n#relationships #trust #truelines #realityoflife #deepthoughts #stangerman69"
    },
    {
        "category": "MOTIVATION & GRIND",
        "hook": "Zindagi me haar mat maanna...",
        "quote": "Koshish itni karo ki kismat ko bhi jhukna pade,\nKyunki haar tab tak nahi hoti,\nJab tak tum khud koshish na chhod do.",
        "caption": "Lage raho, ek din tumhara waqt bhi aayega ⚡🚀\n\n#nevergiveup #hustle #success #dailyinspiration #grind #stangerman69"
    },
    {
        "category": "KHAMOSHI & SUKOON",
        "hook": "Sukoon ki talaash me...",
        "quote": "Khamoshi kamzori nahi hoti,\nYe un baaton ka sabse shaant jawab hai\nJo be-matlab ki behas se bachati hain.",
        "caption": "Sukoon khamoshi me hai, shor me nahi 🤫🤍\n\n#sukoon #peace #innerpeace #deepquotes #maturity #stangerman69"
    },
    {
        "category": "PEOPLE & NATURE",
        "hook": "Insaan ki fitrat...",
        "quote": "Insaan ki fitrat bhi kitni ajeeb hai,\nJo paas hai uski kadar nahi karta,\nAur jo chala gaya usi ka rona rota hai.",
        "caption": "Kadar karna seekho waqt rehte hue ✨🥀\n\n#realitycheck #humanity #lifelessons #kadar #truelines #stangerman69"
    },
    {
        "category": "AESTHETIC LOVE",
        "hook": "Sirf ek chehra...",
        "quote": "Aankhon ke parde bhi bade ajeeb hain,\nDekhte hazaron ko hain,\nPar talaash sirf ek ko karte hain.",
        "caption": "Nazar bas unhi par theharti hai ❤️✨\n\n#romantic #lovestatus #shayariquotes #aestheticvideos #couplegoals #stangerman69"
    },
    {
        "category": "MATURITY",
        "hook": "Samajhdari ki nishani...",
        "quote": "Umar badhne se sirf saal badalte hain,\nSamajh tab aati hai jab apne hi\nparaye hone ka ehsaas karate hain.",
        "caption": "Tajarba umar se nahi, haalat se aata hai 💡✨\n\n#maturity #experience #growth #wisdom #thoughtfortheday #stangerman69"
    }
]

def seed_content_vault():
    """Seeds the vault with all 120+ authentic curated shayaris from ShayariService."""
    try:
        from services.shayari_service import MASTER_SHAYARI_ARCHIVE
        seed_list = MASTER_SHAYARI_ARCHIVE
    except Exception:
        seed_list = SEEDED_QUOTES

    with get_connection() as conn:
        cursor = conn.cursor()
        for item in seed_list:
            cursor.execute("""
                INSERT OR IGNORE INTO content_vault (category, hook, quote, caption, is_used)
                VALUES (?, ?, ?, ?, 0)
            """, (item["category"], item["hook"], item["quote"], item["caption"]))
        conn.commit()


def get_unused_quote_count() -> int:
    """Returns number of unused quotes currently in vault."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM content_vault WHERE is_used = 0")
        return cursor.fetchone()["cnt"]


def replenish_vault_with_quotes(quotes: List[Dict[str, str]]) -> int:
    """Inserts freshly generated quotes into vault."""
    added = 0
    with get_connection() as conn:
        cursor = conn.cursor()
        for item in quotes:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO content_vault (category, hook, quote, caption, is_used)
                    VALUES (?, ?, ?, ?, 0)
                """, (item["category"], item["hook"], item["quote"], item["caption"]))
                if cursor.rowcount > 0:
                    added += 1
            except Exception:
                pass
        conn.commit()
    return added


def get_all_used_quote_hashes() -> set:
    """Returns SHA-256 hashes of all quotes that have ever been published or marked used."""
    import hashlib
    hashes = set()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT quote_hash FROM published_quotes_archive")
        for r in cursor.fetchall():
            if r["quote_hash"]:
                hashes.add(r["quote_hash"])
        cursor.execute("SELECT quote FROM content_vault WHERE is_used = 1")
        for r in cursor.fetchall():
            if r["quote"]:
                clean = " ".join(r["quote"].lower().split())
                hashes.add(hashlib.sha256(clean.encode("utf-8")).hexdigest())
        cursor.execute("SELECT quote FROM scheduled_posts WHERE status = 'published' AND quote IS NOT NULL")
        for r in cursor.fetchall():
            if r["quote"]:
                clean = " ".join(r["quote"].lower().split())
                hashes.add(hashlib.sha256(clean.encode("utf-8")).hexdigest())
    return hashes


def is_quote_published(quote_text: str) -> bool:
    """Checks whether this exact quote has ever been published before."""
    import hashlib
    clean = " ".join((quote_text or "").lower().split())
    h = hashlib.sha256(clean.encode("utf-8")).hexdigest()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM published_quotes_archive WHERE quote_hash = ?", (h,))
        if cursor.fetchone():
            return True
        cursor.execute("SELECT 1 FROM content_vault WHERE is_used = 1 AND quote = ?", (quote_text,))
        if cursor.fetchone():
            return True
    return False


def record_quote_published(quote_text: str, hook: str = "", category: str = "", media_type: str = ""):
    """Permanently records that a quote has been published so it is NEVER repeated."""
    import hashlib
    clean = " ".join((quote_text or "").lower().split())
    h = hashlib.sha256(clean.encode("utf-8")).hexdigest()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO published_quotes_archive (quote_hash, hook, quote, category, media_type)
            VALUES (?, ?, ?, ?, ?)
        """, (h, hook, quote_text, category, media_type))
        cursor.execute("""
            UPDATE content_vault 
            SET is_used = 1, used_at = ? 
            WHERE quote = ?
        """, (now_str, quote_text))
        conn.commit()


def get_fresh_quote(category: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetches an UNUSED, never-published quote from the vault.
    Guarantees that no quote/shayari is EVER repeated!
    Never resets is_used to 0. If vault is running low, dynamically generates brand new unique quotes!
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        if category:
            cursor.execute("""
                SELECT * FROM content_vault 
                WHERE is_used = 0 AND category LIKE ?
                ORDER BY RANDOM() LIMIT 1
            """, (f"%{category}%",))
        else:
            cursor.execute("""
                SELECT * FROM content_vault 
                WHERE is_used = 0 
                ORDER BY RANDOM() LIMIT 1
            """)
        row = cursor.fetchone()
        if row:
            return dict(row)

    # If all existing quotes in vault are exhausted, DO NOT RESET is_used!
    # Generate a brand-new unique quote using the procedural and online engine.
    try:
        from services.shayari_service import ShayariService
        svc = ShayariService()
        used = get_all_used_quote_hashes()
        new_q = svc.get_unique_quote(category=category, exclude_hashes=used)
        add_custom_quote_to_vault(
            category=new_q["category"],
            hook=new_q["hook"],
            quote=new_q["quote"],
            caption=new_q["caption"]
        )
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM content_vault WHERE quote = ?", (new_q["quote"],))
            fresh_row = cursor.fetchone()
            if fresh_row:
                return dict(fresh_row)
        return new_q
    except Exception as e:
        print(f"[!] Dynamic fresh quote generation notice: {e}")
        return None


def mark_quote_as_used(quote_id: int, media_type: str = ""):
    """Marks a quote as used in vault AND writes to permanent published archive."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM content_vault WHERE id = ?", (quote_id,))
        row = cursor.fetchone()
        cursor.execute("""
            UPDATE content_vault 
            SET is_used = 1, used_at = ? 
            WHERE id = ?
        """, (now_str, quote_id))
        if row:
            import hashlib
            clean = " ".join(row["quote"].lower().split())
            h = hashlib.sha256(clean.encode("utf-8")).hexdigest()
            cursor.execute("""
                INSERT OR IGNORE INTO published_quotes_archive (quote_hash, hook, quote, category, media_type)
                VALUES (?, ?, ?, ?, ?)
            """, (h, row["hook"], row["quote"], row["category"], media_type))
        conn.commit()


def add_custom_quote_to_vault(category: str, hook: str, quote: str, caption: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO content_vault (category, hook, quote, caption, is_used)
            VALUES (?, ?, ?, ?, 0)
        """, (category, hook, quote, caption))
        conn.commit()
        return cursor.lastrowid
def get_active_rules() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM keyword_rules WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]


def add_keyword_rule(keyword: str, reply_comment: str, reply_dm: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO keyword_rules (keyword, reply_comment, reply_dm, is_active)
            VALUES (?, ?, ?, 1)
        """, (keyword.lower().strip(), reply_comment, reply_dm))
        conn.commit()


# --- Daily Autopilot Slot Helpers ---
def is_slot_done_today(slot: str, date_str: str) -> bool:
    """Checks if a given autopilot slot (morning_reel, afternoon_post, evening_reel) was done today."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as cnt FROM daily_autopilot_log 
            WHERE date = ? AND slot = ?
        """, (date_str, slot))
        return cursor.fetchone()["cnt"] > 0


def record_slot_done(slot: str, date_str: str, media_url: str = ""):
    """Records that a slot was published today."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO daily_autopilot_log (date, slot, status, media_url)
            VALUES (?, ?, 'published', ?)
        """, (date_str, slot, media_url))
        conn.commit()


def get_today_slots_status(date_str: str) -> Dict[str, bool]:
    """Returns status of all 3 slots for today."""
    return {
        "morning_reel": is_slot_done_today("morning_reel", date_str),
        "afternoon_post": is_slot_done_today("afternoon_post", date_str),
        "evening_reel": is_slot_done_today("evening_reel", date_str)
    }


# --- Push Notification Helpers ---
def record_notification(title: str, message: str, url: str = "") -> int:
    """Stores push notification in database history."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications_history (title, message, url)
            VALUES (?, ?, ?)
        """, (title, message, url))
        conn.commit()
        return cursor.lastrowid


def get_recent_notifications(limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieves recent push notifications sent."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM notifications_history
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
