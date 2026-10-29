"""
Autonomous Content Pipeline
Generates aesthetic media (Post / Reel), crafts viral captions, and uploads directly to Instagram.
"""

import random
import math
from pathlib import Path
from typing import Dict, Any, Optional
from core.client import InstagramAgentClient
from services.media_creator import MediaCreator
from services.ai_generator import AIGenerator
from services.post_service import PostService
from services.audio_service import AudioService

# Curated viral quotes library (Aesthetic Shayari, Deep Life, Love, Attitude)
CURATED_QUOTES = [
    {
        "category": "AESTHETIC SHAYARI",
        "hook": "Kuch baatein bina bole samajh jaani chahiye...",
        "quote": "Kehte hain sab kuch badalta hai waqt ke sath,\nLekin kuch yaadein kabhi purani nahi hoti.",
        "caption": "Waqt badalta hai, log badalte hain... lekin yaadein wahi rehti hain ✨\n\nDrop a ❤️ if you felt this.\n\n#aesthetic #shayari #lovestatus #deepquotes #poetry #reelsinstagram #explorepage #viral #stangerman69"
    },
    {
        "category": "DEEP THOUGHTS",
        "hook": "Zindagi ka sabse bada sach...",
        "quote": "Khamoshi behtar hai un baaton se,\nJo rishton me daraar daal dein.",
        "caption": "Kabhi kabhi khamosh rehna hi sabse bada jawab hota hai 🤫✨\n\nShare with someone who needs this wisdom today.\n\n#deepthoughts #mindset #lifelessons #aestheticquotes #quotesoftheday #explore #hindiquotes"
    },
    {
        "category": "ATTITUDE & FOCUS",
        "hook": "Khud par bharosa rakho...",
        "quote": "Bheed ka hissa banna aasan hai,\nPar akele chalne me alag hi junoon hai.",
        "caption": "Apna rasta khud banao, kisi ke peeche chalne ki zaroorat nahi 🔥⚡\n\nDouble tap if you believe in your journey! 💯\n\n#motivation #attitude #focus #successmindset #grind #reelkarofeelkaro #trending"
    },
    {
        "category": "LOVE & EMOTIONS",
        "hook": "Ek pyaari si baat...",
        "quote": "Kehte hain pyaar me neend udd jaati hai,\nLekin sukoon bhi bas unhi se milta hai.",
        "caption": "Sukoon bas unhi ke paas hai ❤️🌹\n\nTag your special someone in the comments 👇\n\n#love #lovestatus #aestheticvideos #romantic #shayariquotes #couples #explorepage"
    }
]

class AutoContentPipeline:
    def __init__(self, client: InstagramAgentClient):
        self.client = client
        self.creator = MediaCreator(handle=f"@{client.username or 'stanger.man69'}")
        self.ai = AIGenerator()
        self.post_service = PostService(client)
        self.audio_service = AudioService()

    def create_and_post_image(
        self,
        quote: Optional[str] = None,
        category: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an aesthetic image post and upload it to Instagram."""
        if not quote:
            selected = random.choice(CURATED_QUOTES)
            quote = selected["quote"]
            category = category or selected["category"]
            caption = caption or selected["caption"]
        else:
            category = category or "AESTHETIC POST"
            if not caption:
                gen = self.ai.generate_caption(quote[:40], tone="poetic and aesthetic")
                caption = gen["caption"]

        print(f"[*] Designing aesthetic post for: '{quote[:30]}...'")
        img_path = self.creator.create_aesthetic_post(quote=quote, category=category)
        print(f"[✓] Image created: {img_path}")

        print("[*] Uploading image post to Instagram...")
        res = self.post_service.publish_now(str(img_path), "photo", caption)
        print(f"[✓] Successfully published image post! URL: {res.get('url')}")
        return res

    def create_and_post_reel(
        self,
        hook: Optional[str] = None,
        quote: Optional[str] = None,
        caption: Optional[str] = None,
        duration_sec: int = 12,
        use_voiceover: bool = False
    ) -> Dict[str, Any]:
        """
        Generate an animated vertical video reel with soulful aesthetic music.
        By default uses pure atmospheric aesthetic BGM (No robotic AI voice) for maximum virality.
        """
        if not hook or not quote:
            selected = random.choice(CURATED_QUOTES)
            hook = hook or selected["hook"]
            quote = quote or selected["quote"]
            caption = caption or selected["caption"]
        elif not caption:
            gen = self.ai.generate_caption(f"{hook} {quote[:30]}", tone="viral aesthetic reel")
            caption = gen["caption"]

        total_duration = float(duration_sec)

        # Step 1: Render Video
        print(f"[*] Step 1: Rendering vertical aesthetic video reel ({total_duration}s)...")
        raw_reel_path = self.creator.create_aesthetic_reel(
            hook=hook,
            quote=quote,
            duration_sec=int(total_duration)
        )
        print(f"[✓] Reel video rendered: {raw_reel_path}")

        # Step 2: Attach Pure Aesthetic BGM (or Voiceover if explicitly enabled)
        if use_voiceover:
            print("[*] Step 2: Generating voiceover and mixing with BGM...")
            voice_path, voice_dur = self.audio_service.generate_poetic_voiceover(
                hook=hook,
                quote=quote,
                filename="voice_custom.mp3"
            )
            final_reel_path = self.audio_service.attach_audio_to_video(
                video_path=raw_reel_path,
                voice_mp3=voice_path,
                total_duration=total_duration
            )
        else:
            print("[*] Step 2: Attaching pure soulful aesthetic BGM (No robot voice)...")
            final_reel_path = self.audio_service.attach_music_only_to_video(
                video_path=raw_reel_path,
                duration_sec=total_duration
            )

        print(f"[✓] Reel audio successfully mixed: {final_reel_path}")

        print("[*] Step 3: Uploading Reel to Instagram...")
        res = self.post_service.publish_now(str(final_reel_path), "reel", caption)
        print(f"[✓] Successfully published Reel! URL: {res.get('url')}")
        return res
