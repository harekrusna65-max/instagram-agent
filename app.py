"""
Instagram AI Studio - Web Application for @stanger.man69
Run with: uv run streamlit run app.py
"""

import os
import sys
import time
from pathlib import Path
import streamlit as st
from PIL import Image

# Force UTF-8 on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Page Configuration
st.set_page_config(
    page_title="Instagram Studio • @stanger.man69",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Luxury Theme)
st.markdown("""
<style>
    .main {
        background-color: #0b0d17;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(25, 30, 48, 0.7), rgba(15, 18, 30, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .metric-val {
        font-size: 2rem;
        font-weight: bold;
        color: #a855f7;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #9333ea, #c026d3);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);
    }
</style>
""", unsafe_allow_html=True)

from database.db import (
    init_db,
    get_fresh_quote,
    mark_quote_as_used,
    get_pending_scheduled_posts,
    add_scheduled_post,
    get_active_rules,
    add_keyword_rule
)
from core.client import InstagramAgentClient
from services.ai_generator import AIGenerator
from services.media_creator import MediaCreator
from services.post_service import PostService
from services.analytics_service import AnalyticsService
from services.auto_content_pipeline import AutoContentPipeline

init_db()

@st.cache_resource
def get_instagram_client():
    cl = InstagramAgentClient()
    if cl.authenticate():
        return cl
    return None

client = get_instagram_client()

# Sidebar: Profile & Status
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/198px-Instagram_logo_2016.svg.png", width=60)
    st.title("Instagram AI Studio")
    st.caption("Autonomous Content & Engagement Engine")

    if client:
        st.success(f"Connected as **@{client.username}**", icon="🟢")
        analytics = AnalyticsService(client)
        try:
            summary = analytics.get_summary()
            prof = summary["profile"]
            st.write(f"**Name:** {prof.get('full_name', '')}")
            st.write(f"**Followers:** {prof.get('follower_count', 0)}")
            st.write(f"**Following:** {prof.get('following_count', 0)}")
            st.write(f"**Media Count:** {prof.get('media_count', 0)}")
        except Exception:
            pass
    else:
        st.error("Not connected! Please run login first.")
        if st.button("Run Browser Login"):
            st.info("Run `uv run python login_browser.py` in terminal.")

if not client:
    st.warning("Please authenticate with Instagram to use the Studio.")
    st.stop()

pipeline = AutoContentPipeline(client)
media_creator = MediaCreator(handle=f"@{client.username}")
ai_gen = AIGenerator()

# Header Metrics
cols = st.columns(4)
with cols[0]:
    st.markdown('<div class="metric-card"><div class="metric-val">33</div><div class="metric-label">Followers</div></div>', unsafe_allow_html=True)
with cols[1]:
    st.markdown('<div class="metric-card"><div class="metric-val">6+</div><div class="metric-label">Total Posts & Reels</div></div>', unsafe_allow_html=True)
with cols[2]:
    st.markdown('<div class="metric-card"><div class="metric-val">100%</div><div class="metric-label">Anti-Duplicate Safe</div></div>', unsafe_allow_html=True)
with cols[3]:
    st.markdown('<div class="metric-card"><div class="metric-val">Active</div><div class="metric-label">AI Status</div></div>', unsafe_allow_html=True)

st.write("")

# Main Tabs
tabs = st.tabs(["📸 Post Studio", "🎬 Reel Studio", "⏰ Post Scheduler", "💬 Inbox & Comments", "⚙️ Keyword Rules"])

# --- TAB 1: POST STUDIO ---
with tabs[0]:
    st.subheader("Create & Upload Aesthetic Image Post (4:5 Portrait)")
    col_input, col_preview = st.columns([1.2, 1])

    with col_input:
        if st.button("🎲 Pick Random Fresh Shayari from Vault", key="btn_fresh_post"):
            fresh = get_fresh_quote()
            if fresh:
                st.session_state["post_quote"] = fresh["quote"]
                st.session_state["post_category"] = fresh["category"]
                st.session_state["post_caption"] = fresh["caption"]
                st.session_state["post_quote_id"] = fresh["id"]

        category = st.selectbox(
            "Category",
            ["AESTHETIC POETRY", "DEEP LIFE", "SELF RESPECT", "KHAMOSHI & SUKOON", "LOVE & EMOTIONS", "ATTITUDE & FOCUS"],
            index=0
        )
        quote_text = st.text_area(
            "Shayari / Quote Text (Last line will be highlighted in gold):",
            value=st.session_state.get("post_quote", "Kuch log zindagi me aate hain,\nhume sikhane ke liye,\nki har muskuraane wala\napna nahi hota."),
            height=130
        )
        caption_text = st.text_area(
            "Instagram Caption & Hashtags:",
            value=st.session_state.get("post_caption", "Har muskuraane wala apna nahi hota ✨🥀\n\n#aesthetic #poetry #shayari #deepquotes #viral #stangerman69 #explorepage"),
            height=100
        )

        st.write("")
        if st.button("🚀 Publish Post to Instagram NOW", key="btn_publish_post"):
            with st.spinner("Designing ultra-aesthetic card & uploading to Instagram..."):
                try:
                    res = pipeline.create_and_post_image(
                        quote=quote_text,
                        category=category,
                        caption=caption_text
                    )
                    st.success(f"🎉 Successfully Published Live on Instagram!")
                    if res.get("url"):
                        st.markdown(f"[👉 Click here to view on Instagram]({res['url']})")
                except Exception as e:
                    st.error(f"Error publishing post: {e}")

    with col_preview:
        st.caption("Live Post Preview (Generated Card)")
        if st.button("👁️ Generate Preview", key="btn_gen_preview"):
            img_path = media_creator.create_aesthetic_post(quote=quote_text, category=category)
            st.session_state["preview_post_path"] = str(img_path)

        preview_p = st.session_state.get("preview_post_path")
        if preview_p and Path(preview_p).exists():
            st.image(preview_p, use_container_width=True)
        else:
            st.info("Click 'Generate Preview' to see how the card looks.")


# --- TAB 2: REEL STUDIO ---
with tabs[1]:
    st.subheader("Create & Upload 9:16 Vertical Video Reel (with Music)")
    r_col1, r_col2 = st.columns([1.2, 1])

    with r_col1:
        if st.button("🎲 Pick Random Viral Reel Idea", key="btn_fresh_reel"):
            fresh = get_fresh_quote()
            if fresh:
                st.session_state["reel_hook"] = fresh["hook"]
                st.session_state["reel_quote"] = fresh["quote"]
                st.session_state["reel_caption"] = fresh["caption"]
                st.session_state["reel_quote_id"] = fresh["id"]

        reel_hook = st.text_input(
            "Reel Hook (Appears for first 3.2 seconds):",
            value=st.session_state.get("reel_hook", "Zindagi me ye hamesha yaad rakhna...")
        )
        reel_quote = st.text_area(
            "Main Shayari / Quote Body:",
            value=st.session_state.get("reel_quote", "Jitna kam bologe,\nLog utna zyada sunenge.\nApni keemat badhao, shor nahi."),
            height=120
        )
        reel_caption = st.text_area(
            "Reel Caption & Hashtags:",
            value=st.session_state.get("reel_caption", "Apni keemat badhao, shor nahi ✨🤫\n\n#aesthetic #reels #deepquotes #mindset #motivation #viral #stangerman69 #explorepage"),
            height=90
        )

        r_dur = st.slider("Reel Duration (Seconds)", min_value=8, max_value=15, value=12)
        use_voiceover = st.checkbox("Enable AI Voiceover (Unchecked = Pure Aesthetic Lofi Beat)", value=False)

        st.write("")
        if st.button("🎬 Render & Upload Reel to Instagram NOW", key="btn_publish_reel"):
            with st.spinner("Rendering 1080x1920 video, mixing audio & uploading to Instagram... (Takes ~25s)"):
                try:
                    res = pipeline.create_and_post_reel(
                        hook=reel_hook,
                        quote=reel_quote,
                        caption=reel_caption,
                        duration_sec=r_dur,
                        use_voiceover=use_voiceover
                    )
                    st.success("🎉 Reel Successfully Published Live on Instagram!")
                    if res.get("url"):
                        st.markdown(f"[👉 Click here to watch on Instagram]({res['url']})")
                except Exception as e:
                    st.error(f"Error publishing reel: {e}")

    with r_col2:
        st.caption("Reel Specifications")
        st.markdown("""
        * **Format:** 9:16 Vertical Video (1080x1920)
        * **Style:** Floating Atmospheric Particles + Ambient Bokeh
        * **Camera:** Slow Ken Burns Cinematic Zoom
        * **Typography:** Georgia Luxury Serif + Warm Gold Punchline
        * **Sound:** 432Hz Aesthetic Lofi Beat (with soft fade-out)
        * **Duration:** Custom selected (Default 12s)
        """)


# --- TAB 3: SCHEDULER ---
with tabs[2]:
    st.subheader("Schedule Posts for Future Auto-Publishing")
    sch_col1, sch_col2 = st.columns(2)
    with sch_col1:
        st.write("Schedule a new post:")
        s_type = st.radio("Media Type", ["Photo", "Reel"], horizontal=True)
        s_date = st.date_input("Publish Date")
        s_time = st.time_input("Publish Time")
        s_quote = st.text_area("Quote / Shayari", value="Khamoshi behtar hai un baaton se jo rishte tod dein.")
        s_caption = st.text_area("Caption", value="Deep thoughts ✨ #aesthetic #stangerman69")

        if st.button("⏰ Schedule This Post"):
            sch_datetime = f"{s_date} {s_time}:00"
            if s_type == "Photo":
                media_path = str(media_creator.create_aesthetic_post(quote=s_quote))
            else:
                media_path = str(media_creator.create_aesthetic_reel(hook="Dhyan se suno...", quote=s_quote, duration_sec=12))
            
            post_id = add_scheduled_post(media_path, s_type.lower(), s_caption, sch_datetime)
            st.success(f"Post #{post_id} scheduled for {sch_datetime}!")

    with sch_col2:
        st.write("Pending Scheduled Posts:")
        pending = get_pending_scheduled_posts()
        if pending:
            st.dataframe(pending)
        else:
            st.info("No pending scheduled posts at the moment.")


# --- TAB 4: INBOX & COMMENTS ---
with tabs[3]:
    st.subheader("Recent Direct Messages & Engagement")
    if st.button("🔄 Refresh Inbox & Comments"):
        st.rerun()

    dm_col, com_col = st.columns(2)
    with dm_col:
        st.write("📩 Recent Direct Message Threads:")
        try:
            threads = client.get_direct_threads(amount=6)
            for th in threads:
                u_names = ", ".join([u.username for u in th.users]) if th.users else "User"
                last_m = th.messages[0].text if th.messages and hasattr(th.messages[0], "text") else "<Media/Action>"
                st.markdown(f"**@{u_names}:** {last_m}")
                st.divider()
        except Exception as e:
            st.warning(f"Could not load inbox: {e}")

    with com_col:
        st.write("💬 Recent Post Comments:")
        try:
            medias = client.get_user_medias(amount=3)
            for m in medias:
                st.markdown(f"**Post: https://instagram.com/p/{m.code}**")
                comments = client.get_media_comments(m.id, amount=3)
                for c in comments:
                    st.write(f"- **@{c.user.username}:** {c.text}")
                st.divider()
        except Exception as e:
            st.warning(f"Could not load comments: {e}")


# --- TAB 5: KEYWORD RULES ---
with tabs[4]:
    st.subheader("Manage Keyword Auto-Reply Rules (Comment to DM)")
    rules = get_active_rules()
    st.dataframe(rules)

    st.write("Add New Keyword Trigger:")
    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1:
        new_kw = st.text_input("Keyword (e.g. 'link', 'price', 'details')")
    with r_col2:
        new_cr = st.text_input("Comment Reply", value="Check your DM! Sent you the details 🚀")
    with r_col3:
        new_dm = st.text_input("DM Reply Text", value="Hey! Here is what you requested: https://example.com")

    if st.button("➕ Add Rule"):
        if new_kw:
            add_keyword_rule(new_kw, new_cr, new_dm)
            st.success(f"Rule for '{new_kw}' added!")
            st.rerun()
