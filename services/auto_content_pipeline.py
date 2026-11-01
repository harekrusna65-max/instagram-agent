"""
Autonomous Content Pipeline
Generates aesthetic media (Post / Reel), crafts viral captions, and uploads directly to Instagram.
"""

import random
import math
import time
from pathlib import Path
from typing import Dict, Any, Optional
from core.client import InstagramAgentClient
from services.media_creator import MediaCreator
from services.ai_generator import AIGenerator
from services.post_service import PostService
from services.audio_service import AudioService
from services.hashtag_service import HashtagRotator
from database.db import (
    get_fresh_quote,
    mark_quote_as_used,
    get_unused_quote_count,
    replenish_vault_with_quotes,
    is_quote_published,
    record_quote_published,
    get_all_used_quote_hashes
)
from services.shayari_service import ShayariService

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
        self.hashtags = HashtagRotator()

    def _ensure_vault_replenished(self):
        """Auto-generate fresh unique quotes if content vault is getting low (Guarantees infinite content)."""
        try:
            cnt = get_unused_quote_count()
            if cnt < 15:
                print(f"[*] Content Vault running low ({cnt} unused left). Generating 25 fresh unique shayaris...")
                svc = ShayariService()
                used_hashes = get_all_used_quote_hashes()
                fresh_batch = []
                for _ in range(25):
                    q = svc.get_unique_quote(exclude_hashes=used_hashes)
                    h = svc.get_hash(q["quote"])
                    used_hashes.add(h)
                    fresh_batch.append(q)
                added = replenish_vault_with_quotes(fresh_batch)
                print(f"[✓] Added {added} fresh unique quotes to Content Vault! Total unused now: {get_unused_quote_count()}")
        except Exception as e:
            print(f"[!] Vault replenishment notice: {e}")

    def create_and_post_image(
        self,
        quote: Optional[str] = None,
        category: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an aesthetic image post and upload it to Instagram with strict anti-duplicate guarantee."""
        self._ensure_vault_replenished()
        quote_id = None

        # Check if user-provided quote was already published before
        if quote and is_quote_published(quote):
            print(f"[!] Warning: Quote was already published in a previous post! Picking fresh unique quote to avoid repetition.")
            quote = None

        if not quote:
            fresh = get_fresh_quote(category)
            if fresh:
                quote = fresh["quote"]
                category = category or fresh["category"]
                caption_base = fresh["caption"].split("#")[0].strip()
                smart_tags = self.hashtags.get_smart_hashtags(category=category)
                caption = caption or f"{caption_base}\n\n{smart_tags}"
                quote_id = fresh.get("id")
            else:
                svc = ShayariService()
                fresh_item = svc.get_unique_quote(category=category, exclude_hashes=get_all_used_quote_hashes())
                quote = fresh_item["quote"]
                category = category or fresh_item["category"]
                smart_tags = self.hashtags.get_smart_hashtags(category=category)
                caption = caption or f"{fresh_item['caption'].split('#')[0].strip()}\n\n{smart_tags}"
        else:
            category = category or "AESTHETIC POST"
            if not caption:
                gen = self.ai.generate_caption(quote[:40], tone="poetic and aesthetic")
                smart_tags = self.hashtags.get_smart_hashtags(category=category)
                caption = f"{gen['caption'].split('#')[0].strip()}\n\n{smart_tags}"

        print(f"[*] Designing aesthetic post for: '{quote[:30]}...'")
        img_path = self.creator.create_aesthetic_post(quote=quote, category=category)
        print(f"[✓] Image created: {img_path}")

        print("[*] Uploading image post to Instagram...")
        res = self.post_service.publish_now(str(img_path), "photo", caption)
        
        # Permanently record quote as published and mark as used (Strict anti-duplicate)
        record_quote_published(quote, hook=category or "", category=category or "", media_type="photo")
        if quote_id:
            mark_quote_as_used(quote_id, media_type="photo")
            print(f"[✓] Quote #{quote_id} permanently recorded as published in database.")

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
        Strict anti-duplicate: every reel has a 100% unique quote.
        """
        self._ensure_vault_replenished()
        quote_id = None
        category = "AESTHETIC REELS"

        # Check if user-provided quote was already published before
        if quote and is_quote_published(quote):
            print(f"[!] Warning: Reel quote was already published in a previous post! Picking fresh unique quote.")
            hook = None
            quote = None

        if not hook or not quote:
            fresh = get_fresh_quote()
            if fresh:
                hook = hook or fresh["hook"]
                quote = quote or fresh["quote"]
                category = fresh.get("category", "AESTHETIC REELS")
                caption_base = fresh["caption"].split("#")[0].strip()
                smart_tags = self.hashtags.get_smart_hashtags(category=category)
                caption = caption or f"{caption_base}\n\n{smart_tags}"
                quote_id = fresh.get("id")
            else:
                svc = ShayariService()
                fresh_item = svc.get_unique_quote(exclude_hashes=get_all_used_quote_hashes())
                hook = hook or fresh_item["hook"]
                quote = quote or fresh_item["quote"]
                smart_tags = self.hashtags.get_smart_hashtags(category=fresh_item["category"])
                caption = caption or f"{fresh_item['caption'].split('#')[0].strip()}\n\n{smart_tags}"
        elif not caption:
            gen = self.ai.generate_caption(f"{hook} {quote[:30]}", tone="viral aesthetic reel")
            smart_tags = self.hashtags.get_smart_hashtags(category="VIRAL_REELS")
            caption = f"{gen['caption'].split('#')[0].strip()}\n\n{smart_tags}"
            smart_tags = self.hashtags.get_smart_hashtags(category="VIRAL_REELS")
            caption = f"{gen['caption'].split('#')[0].strip()}\n\n{smart_tags}"

        combined_text = f"{hook or ''} {quote or ''}"
        voice_path = None
        voice_dur = 0.0

        # When voiceover is requested, generate speech FIRST to compute the exact video duration
        # This guarantees 100% of the shayari words are read and none are cut off!
        if use_voiceover:
            print("[*] Generating full poetic voiceover first to dynamically match video duration...")
            voice_path, voice_dur = self.audio_service.generate_poetic_voiceover(
                hook=hook,
                quote=quote,
                filename=f"voice_{int(time.time())}.mp3"
            )
            # Video duration = exact spoken duration + 2.5s lingering buffer for emotional BGM fade-out
            total_duration = max(float(duration_sec), float(math.ceil(voice_dur + 2.5)))
            print(f"[✓] Voiceover duration: {voice_dur:.2f}s -> Adjusted video length: {total_duration:.1f}s")
        else:
            total_duration = float(duration_sec)

        # Step 1: Render Video matching exact duration
        print(f"[*] Step 1: Rendering vertical aesthetic video reel ({total_duration}s)...")
        raw_reel_path = self.creator.create_aesthetic_reel(
            hook=hook,
            quote=quote,
            duration_sec=int(total_duration)
        )
        print(f"[✓] Reel video rendered: {raw_reel_path}")

        # Step 2: Attach Audio
        if use_voiceover and voice_path:
            print(f"[*] Step 2: Attaching complete voiceover ({voice_dur:.2f}s) + mood BGM...")
            final_reel_path = self.audio_service.attach_audio_to_video(
                video_path=raw_reel_path,
                voice_mp3=voice_path,
                total_duration=total_duration,
                text=combined_text,
                category=category or ""
            )
        else:
            print("[*] Step 2: Attaching pure aesthetic BGM matched to shayari mood...")
            final_reel_path = self.audio_service.attach_music_only_to_video(
                video_path=raw_reel_path,
                duration_sec=total_duration,
                text=combined_text,
                category=category or ""
            )

        print(f"[✓] Reel audio successfully mixed: {final_reel_path}")

        print("[*] Step 3: Uploading Reel to Instagram...")
        res = self.post_service.publish_now(str(final_reel_path), "reel", caption)

        # Permanently record quote as published and mark as used (Strict anti-duplicate)
        record_quote_published(quote, hook=hook or "", category=category or "", media_type="reel")
        if quote_id:
            mark_quote_as_used(quote_id, media_type="reel")
            print(f"[✓] Quote #{quote_id} permanently recorded as published in database.")

        print(f"[✓] Successfully published Reel! URL: {res.get('url')}")
        return res
