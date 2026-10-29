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


# --- Keyword Rules Helpers ---
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
