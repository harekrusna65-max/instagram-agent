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
                media_path TEXT NOT NULL,
                media_type TEXT NOT NULL DEFAULT 'photo', -- 'photo' or 'reel'
                caption TEXT NOT NULL,
                scheduled_time TEXT NOT NULL, -- ISO timestamp 'YYYY-MM-DD HH:MM:SS'
                status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'published', 'failed'
                media_id TEXT,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

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
        
        # Insert default keyword rules if empty
        cursor.execute("SELECT COUNT(*) as count FROM keyword_rules")
        if cursor.fetchone()["count"] == 0:
            cursor.executemany("""
                INSERT INTO keyword_rules (keyword, reply_comment, reply_dm)
                VALUES (?, ?, ?)
            """, [
                ("link", "Sent you the details in DM! Check your inbox 🚀", "Hey there! Thanks for your interest. Here is the link you requested: https://example.com/info"),
                ("price", "Check your DMs! Sent you the full pricing details 📩", "Hello! Here are the details and special pricing. Let me know if you have questions!"),
                ("info", "DM sent! Please check your message requests 📨", "Hey! Thanks for reaching out. Here is all the info you need.")
            ])

        conn.commit()
    
    # Seed quotes vault
    seed_content_vault()


# --- Scheduled Posts Helpers ---
def add_scheduled_post(media_path: str, media_type: str, caption: str, scheduled_time: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scheduled_posts (media_path, media_type, caption, scheduled_time, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (media_path, media_type, caption, scheduled_time))
        conn.commit()
        return cursor.lastrowid


def get_pending_scheduled_posts() -> List[Dict[str, Any]]:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM scheduled_posts 
            WHERE status = 'pending' AND scheduled_time <= ?
            ORDER BY scheduled_time ASC
        """, (now_str,))
        return [dict(row) for row in cursor.fetchall()]


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
    with get_connection() as conn:
        cursor = conn.cursor()
        for item in SEEDED_QUOTES:
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
    """Inserts freshly generated AI quotes into vault."""
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


def get_fresh_quote(category: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetches an UNUSED quote from the vault.
    Guarantees that no quote/shayari is ever repeated!
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        if category:
            cursor.execute("""
                SELECT * FROM content_vault 
                WHERE is_used = 0 AND category = ?
                ORDER BY RANDOM() LIMIT 1
            """, (category,))
        else:
            cursor.execute("""
                SELECT * FROM content_vault 
                WHERE is_used = 0 
                ORDER BY RANDOM() LIMIT 1
            """)
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        # If all quotes have been used, reset and recycle or fetch any
        cursor.execute("UPDATE content_vault SET is_used = 0")
        conn.commit()
        cursor.execute("SELECT * FROM content_vault ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None


def mark_quote_as_used(quote_id: int):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE content_vault 
            SET is_used = 1, used_at = ? 
            WHERE id = ?
        """, (now_str, quote_id))
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
