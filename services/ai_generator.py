"""
AI Content & Reply Generator
Supports Google Gemini API with smart offline fallback templates.
"""

import os
import sys
import random
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class AIGenerator:
    def __init__(self):
        self.has_gemini = False
        if GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.has_gemini = True
            except Exception as e:
                print(f"[!] Gemini initialization failed: {e}. Using offline fallback.")
                self.has_gemini = False

    def generate_caption(self, topic: str, tone: str = "engaging") -> Dict[str, Any]:
        """Generate high-converting caption with hook, body, CTA, and hashtags."""
        if self.has_gemini:
            prompt = f"""
            You are an expert Instagram growth strategist and copywriter.
            Create an engaging Instagram post caption for: "{topic}".
            Tone: {tone}
            Structure:
            1. Strong viral Hook (first line that stops the scroll)
            2. Value-packed Body (concise, with emojis and clean formatting)
            3. Clear Call to Action (e.g. 'Comment LINK below')
            4. 15-20 highly relevant, targeted hashtags.
            Output format: Plain text formatted ready to copy/post.
            """
            try:
                response = self.model.generate_content(prompt)
                return {"caption": response.text.strip(), "source": "gemini"}
            except Exception as e:
                print(f"[!] Gemini generation error: {e}. Falling back to template.")

        # High-quality smart offline template
        hooks = [
            f"Stop scrolling! Here is what nobody tells you about {topic} 👇",
            f"The secret to mastering {topic} in 2026 🚀",
            f"If you want to level up your {topic}, read this carefully 💡",
            f"3 simple rules that completely changed how I think about {topic} ✨",
        ]
        
        hook = random.choice(hooks)
        body = (
            f"\n\nConsistency and strategy are everything when it comes to {topic}.\n\n"
            f"🔑 Focus on what actually moves the needle.\n"
            f"📈 Test, iterate, and don't be afraid to innovate.\n"
            f"💬 Drop a comment below if you want the step-by-step breakdown!"
        )
        cta = "\n\n👉 Double tap if this resonated, and share with someone who needs this today!"
        hashtags = (
            f"\n\n#{topic.replace(' ', '')} #growth #mindset #instagramgrowth #creator "
            f"#trending #success #dailyinspiration #explorepage #digitalstrategy"
        )
        full_caption = hook + body + cta + hashtags
        return {"caption": full_caption, "source": "template"}

    def generate_dm_reply(self, incoming_message: str, sender_name: str) -> str:
        """Generate friendly, contextual AI reply for a DM."""
        if self.has_gemini:
            prompt = f"""
            You are managing the Instagram DMs for @stanger.man69.
            The user "{sender_name}" sent this DM: "{incoming_message}".
            Write a friendly, polite, natural, and helpful reply in 1-2 sentences. Keep it human and conversational.
            """
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                pass

        return f"Hey {sender_name}! Thanks for reaching out. How can I help you today? Feel free to ask anything! 🙌"

    def generate_comment_reply(self, comment_text: str, commenter_name: str) -> str:
        """Generate quick, positive comment reply."""
        templates = [
            f"Appreciate you @{commenter_name}! Thanks for the support 🙌",
            f"Spot on @{commenter_name}! Glad you liked it 🔥",
            f"Thanks for dropping by @{commenter_name}! More coming soon 🚀",
            f"Sent you a DM with more details @{commenter_name}! Check inbox 📩"
        ]
        return random.choice(templates)
