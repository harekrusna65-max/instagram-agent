# 🤖 Instagram AI Agent (@stanger.man69)

An autonomous Instagram management agent featuring post scheduling, AI caption generation, comment trigger automation, and DM auto-replies.

---

## 🚀 Features

- **📊 Live Analytics**: Real-time stats, follower metrics, and recent post engagement.
- **📸 Instant Post & Reel Publishing**: Upload images or reels with 1-click.
- **⏰ Smart Scheduler**: Queue posts in SQLite for future automatic publishing.
- **🤖 Comment Trigger Automation**: When users comment keywords like `LINK`, `PRICE`, or `INFO`, automatically reply and send them a DM.
- **💬 Smart DM Auto-Responder**: Automatically replies to inbound direct messages using AI.
- **✨ AI Content Generator**: Generates viral hooks, engaging body copy, CTAs, and relevant hashtags.
- **🛡️ Anti-Ban Safe Pacing**: Human-like randomized delays between actions to keep your account safe.

---

## 🛠️ How to Run

Navigate to project directory:
```powershell
cd "d:\instagram agent"
```

### 1. Interactive Controller (Recommended)
```powershell
uv run python main.py
```
This opens the interactive menu with options:
- `[1]` 📊 View Account Profile & Live Analytics
- `[2]` 📸 Upload Post (Photo / Reel) Now
- `[3]` ⏰ Schedule a Post for Later
- `[4]` 🤖 Run Auto-Engagement Bot (Auto-DM & Comment Responder)
- `[5]` ✨ AI Caption & Hashtag Generator
- `[6]` 💬 View Direct Message Inbox
- `[7]` ⚙️ Keyword Auto-Reply Rules

### 2. 24/7 Background Daemon
To run the automated scheduler and comment/DM listener in the background:
```powershell
uv run python main.py --daemon
```

---

## ⚙️ Configuration (Optional)

Create a `.env` file in the project folder to enable Gemini AI:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(If no API key is provided, the agent seamlessly uses high-converting built-in smart templates).*
