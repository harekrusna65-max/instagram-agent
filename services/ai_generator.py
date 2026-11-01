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

    def generate_ai_shayari(self, topic: str = "sukoon") -> Dict[str, str]:
        """
        Generate on-demand viral Shayari with Hook and Quote for the 1-Tap AI Generator feature.
        """
        topic_lower = (topic or "sukoon").lower().strip()

        if self.has_gemini:
            prompt = f"""
            You are an elite Urdu/Hindi Shayar writing for a viral Instagram luxury aesthetic page (@stanger.man69).
            Write a fresh, viral, deep 2-to-3 line Shayari on the theme: "{topic_lower}".
            Rules:
            1. Language: Poetic Roman Urdu / Hindi (Hinglish) that touches the heart.
            2. The last line must have an impactful punchline word/phrase suitable for gold highlight.
            3. Provide a scroll-stopping Hook line (e.g., 'Ye baat hamesha yaad rakhna...', 'Zindagi ka ek gehra sach...').
            Output format strictly JSON with keys "hook", "quote", "category":
            {{"hook": "...", "quote": "Line 1\\nLine 2\\nLine 3", "category": "{topic_lower.upper()}"}}
            Return ONLY raw JSON, no markdown backticks.
            """
            try:
                import json
                resp = self.model.generate_content(prompt)
                raw = resp.text.strip().replace("```json", "").replace("```", "").strip()
                data = json.loads(raw)
                if data.get("quote"):
                    return {
                        "hook": data.get("hook", "Ye baat dil me utar jaayegi..."),
                        "quote": data.get("quote", ""),
                        "category": data.get("category", topic_lower.upper())
                    }
            except Exception as e:
                print(f"[!] Gemini shayari generation error: {e}")

        # Curated Aesthetic Vault for 6 Core Themes
        theme_pools = {
            "attitude": [
                ("Apni keemat itni badhao...", "Humse milne ke liye log taraste hain,\nKyunki hum bheed ka hissa nahi,\nApni dunya ke badshah hain."),
                ("Kamyabi se shor machao...", "Khamoshi meri kamzori nahi mera mayaar hai,\nHum bolte kam hain,\nLekin jawab lajawab dete hain."),
                ("Apna daur khud laenge...", "Jo log aaj hume dekh kar aage nikal gaye,\nKal wo hi humse milne ke liye,\nWaqt maangte nazar aayenge.")
            ],
            "mohabbat": [
                ("Mohabbat ka sabse khoobsurat ehsaas...", "Kuch log zindagi me aate hain toh sukoon ban jaate hain,\nUnse baatein na bhi ho,\nToh bhi unka khayal dil ko sukoon deta hai."),
                ("Ishq wo nahi jo dikhaya jaye...", "Mohabbat toh bas khamoshi se nibhai jaati hai,\nJahan lafzon ki zaroorat na ho,\nBas ek nazar me sab samajh aa jaye.")
            ],
            "tanhai": [
                ("Raat ki tanhai me...", "Kabhi kabhi akele rehna hi behtar lagta hai,\nKyunki yahan koi jhootha dikhava nahi hota,\nBas hum hote hain aur hamari khamoshi."),
                ("Dard lafzon me kahan aata hai...", "Umar thodi aur beet jaane do,\nKayi chehron se naqab utarenge,\nAur tab tumhe khamoshi ki keemat samajh aayegi.")
            ],
            "zindagi": [
                ("Zindagi ka sabse bada sach...", "Waqt sabko ek sabak sikhata hai,\nJo log kal tak jaan the hamari,\nWo aaj bas ek yaad bankar reh gaye."),
                ("Maturity tab aati hai jab...", "Jab aap har baat par behas karna chhod dete hain,\nAur muskurakar wahan se aage badh jaate hain,\nJahan kadar nahi hoti.")
            ],
            "success": [
                ("Hausla itna bada rakho...", "Raste mushkil zaroor hain magar manzilen kareeb hain,\nMehnat itni shanti se karo,\nKi kamyabi dunya me toofan macha de."),
                ("Sapne sach tab hote hain jab...", "Aaram ki dunya chhod kar,\nAap apne lakshya ke liye raat din ek kar dete hain.")
            ],
            "sukoon": [
                ("Ye baat dil me utar jaayegi...", "Sukoon dunya ke shor me nahi,\nApne andar ki khamoshi me milta hai,\nJahan bas rab ki raza hoti hai."),
                ("Midnight sukoon...", "Jab dil me koi jalan na ho aur niyat saaf ho,\nToh neend bhi sukoon ki aati hai,\nAur zindagi bhi khushnuma lagti hai.")
            ]
        }

        # Select pool
        matched_pool = theme_pools.get(topic_lower, theme_pools["sukoon"])
        chosen_hook, chosen_quote = random.choice(matched_pool)

        return {
            "hook": chosen_hook,
            "quote": chosen_quote,
            "category": topic_lower.upper()
        }

    def generate_fresh_vault_quotes(self, count: int = 5) -> List[Dict[str, str]]:
        """
        Autonomously generates fresh, viral-grade Shayari & Quotes to keep the Content Vault infinitely full.
        """
        import json
        if self.has_gemini:
            prompt = f"""
            You are a master Urdu/Hindi poet and Instagram aesthetic quote writer.
            Create {count} unique, heart-touching, aesthetic 2-to-4 line Shayari / Deep Quotes.
            Topics: Khamoshi, Self-Respect, Waqt, Rishte, Sukoon, Maturity, Solitude.
            Format output strictly as a JSON array of objects with keys:
            - "category": e.g. "AESTHETIC SHAYARI", "DEEP LIFE", "SELF RESPECT", "KHAMOSHI"
            - "hook": catchy first line (e.g. "Ye baat hamesha yaad rakhna...")
            - "quote": 2-4 lines of poetic text separated by newline
            - "caption_line": 1-2 sentence emotional caption
            Only return valid JSON array, no markdown fences.
            """
            try:
                resp = self.model.generate_content(prompt)
                raw_text = resp.text.strip().replace("```json", "").replace("```", "").strip()
                data = json.loads(raw_text)
                if isinstance(data, list):
                    return [
                        {
                            "category": item.get("category", "DEEP LIFE"),
                            "hook": item.get("hook", "Ye baat hamesha yaad rakhna..."),
                            "quote": item.get("quote", ""),
                            "caption": item.get("caption_line", "Sukoon khamoshi me hai ✨")
                        }
                        for item in data if item.get("quote")
                    ]
            except Exception as e:
                print(f"[!] AI Quote generation error: {e}. Using generative templates.")

        # High-variety generative poetic builder
        categories = ["AESTHETIC SHAYARI", "DEEP LIFE", "SELF RESPECT", "KHAMOSHI & SUKOON", "MATURITY", "PEOPLE & REALITY"]
        hooks = [
            "Ye baat dil me utar jaayegi...",
            "Waqt sabko ek sabak sikhata hai...",
            "Khamoshi ka bhi ek mayaar hota hai...",
            "Apni keemat samajhna seekho...",
            "Zindagi ka sabse gehra sach...",
            "Logon ki fitrat samajh aane lage toh..."
        ]

        poetic_templates = [
            ("Umar thodi aur beet jaane do,\nKayi chehron se naqab utarenge,\nAur tab tumhe khamoshi ki keemat samajh aayegi.", "AESTHETIC SHAYARI", "Waqt sab bata deta hai ✨⏳"),
            ("Jahan kadar na ho wahan se nikal jaana hi behtar hai,\nChahe wo kisi ka ghar ho, mehfil ho,\nYa kisi ka dil.", "SELF RESPECT", "Apni izzat sabse pehle 💯🔥"),
            ("Zindagi me kuch dard aise hote hain,\nJo lafzon me bayan nahi hote,\nBas aankhon ki nami me thehar jaate hain.", "KHAMOSHI & SUKOON", "Kuch dard bas mehsoos hote hain 🥀💔"),
            ("Mushkil waqt ka ek sabse bada fayda hai,\nYe bata deta hai ki kaun apna hai,\nAur kaun bas waqt guzar raha tha.", "DEEP LIFE", "Asal chehre waqt dikhata hai 📌💡"),
            ("Har baat par shikayat karna chhod do,\nKyunki sukoon unhe milta hai\nJo har haal me shukr ada karna jaante hain.", "MATURITY", "Shukr me hi sukoon hai 🤍✨"),
            ("Akele chalne ka hausla rakho,\nBheed hamesha hausla cheen leti hai,\nLekin pehchan akele rehkar hi banti hai.", "PEOPLE & REALITY", "Apni pehchan khud banao ⚡🚀")
        ]

        results = []
        sampled = random.sample(poetic_templates, min(count, len(poetic_templates)))
        for q, cat, cap in sampled:
            results.append({
                "category": cat,
                "hook": random.choice(hooks),
                "quote": q,
                "caption": cap
            })
        return results
