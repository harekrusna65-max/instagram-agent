"""
Audio Service for Soulful Instagram Reels
Features:
- Authentic emotional poetry voiceover (Urdu/Hindi lehza with soulful pacing and dramatic pauses)
- Dynamic duration calculation so 100% of the shayari is spoken without getting cut off
- Rich acoustic piano / lofi music generator + support for custom BGM in assets/music/
- Cinematic reverb and audio mixing via FFmpeg
"""

import os
import sys
import math
import wave
import struct
import shutil
import random
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import imageio_ffmpeg

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import edge_tts

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "generated" / "audio"
MUSIC_DIR = BASE_DIR / "assets" / "music"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_EXE = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


def get_media_duration(file_path: Path) -> float:
    """Extract exact media duration in seconds using ffmpeg."""
    cmd = [FFMPEG_EXE, "-i", str(file_path)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            try:
                raw = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = raw.split(":")
                return float(h) * 3600 + float(m) * 60 + float(s)
            except Exception:
                pass
    return 10.0


def synthesize_soulful_piano_bgm(output_wav: Path, duration_sec: float, sample_rate: int = 44100):
    """
    Synthesize an emotional, melancholy acoustic piano chord progression (Am - F - C - G).
    """
    num_samples = int(sample_rate * duration_sec)
    chords = [
        [220.0, 261.63, 329.63, 440.0],  # Am (A3, C4, E4, A4)
        [174.61, 220.0, 261.63, 349.23], # F  (F3, A3, C4, F4)
        [130.81, 164.81, 196.0, 261.63], # C  (C3, E3, G3, C4)
        [196.0, 246.94, 293.66, 392.0],  # G  (G3, B3, D4, G4)
    ]
    chord_dur = 4.0
    samples = [0.0] * num_samples

    total_chords_needed = int(math.ceil(duration_sec / chord_dur)) + 1
    for i in range(total_chords_needed):
        chord = chords[i % len(chords)]
        start_t = i * chord_dur
        for n_idx, freq in enumerate(chord):
            note_start = start_t + (n_idx * 0.32)
            start_idx = int(note_start * sample_rate)
            if start_idx >= num_samples:
                break
            end_idx = min(num_samples, start_idx + int(5.5 * sample_rate))
            for s_idx in range(start_idx, end_idx):
                t_note = (s_idx - start_idx) / sample_rate
                # Exponential decay for piano key
                decay = math.exp(-t_note * 1.3)
                # Harmonic spectrum for rich piano timbre
                val = (
                    math.sin(2 * math.pi * freq * t_note) * 0.65 +
                    math.sin(4 * math.pi * freq * t_note) * 0.22 +
                    math.sin(6 * math.pi * freq * t_note) * 0.10 +
                    math.sin(8 * math.pi * freq * t_note) * 0.04
                ) * decay * 0.16
                samples[s_idx] += val

    max_v = max(abs(s) for s in samples) or 1.0
    with wave.open(str(output_wav), "w") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        raw = bytearray()
        for s in samples:
            norm = int((s / max_v) * 26000)
            norm = max(-32767, min(32767, norm))
            raw.extend(struct.pack("<hh", norm, norm))
        f.writeframes(raw)


# Mood to track matching dictionary
MOOD_TRACK_MAPPING = {
    "sad_emotional": [
        "02_heartfelt_piano_ballad.wav",
        "03_nocturnal_solitude_strings.wav"
    ],
    "sukoon_midnight": [
        "01_midnight_sukoon_lofi.wav",
        "04_rainy_window_lofi.wav",
        "aesthetic_lofi_vibe.wav"
    ],
    "attitude_mindset": [
        "05_deep_cinematic_swell.wav",
        "03_nocturnal_solitude_strings.wav"
    ],
    "love_nostalgia": [
        "06_golden_hour_serenity.wav",
        "01_midnight_sukoon_lofi.wav"
    ]
}

def detect_shayari_mood(text: str = "", category: str = "") -> str:
    """
    Analyzes Hindi/Urdu poetry lyrics and category to classify emotional mood.
    Returns: 'sad_emotional' | 'sukoon_midnight' | 'attitude_mindset' | 'love_nostalgia'
    """
    combined = f"{category} {text}".lower()

    # Keyword pools
    sad_kws = ["dard", "rona", "aansu", "dil", "toot", "judai", "zakhm", "akela", "bewafa", "chhod", "yaad", "tanhai", "gham", "rooth", "mar"]
    sukoon_kws = ["sukoon", "khamoshi", "raat", "shaant", "neend", "midnight", "hawa", "chand", "sitare", "khwaab", "rooh", "aalam", "duniya"]
    attitude_kws = ["waqt", "aukaat", "dushman", "sabak", "matlab", "izzat", "self respect", "shor", "sher", "udaan", "kismat", "pehchan", "badla", "kamyabi", "fitrat"]
    love_kws = ["ishq", "mohabbat", "pyaar", "nazar", "deedar", "muskurahat", "ehsaas", "sanam", "humsafar", "baatein"]

    scores = {
        "sad_emotional": sum(1 for k in sad_kws if k in combined),
        "sukoon_midnight": sum(1 for k in sukoon_kws if k in combined),
        "attitude_mindset": sum(1 for k in attitude_kws if k in combined),
        "love_nostalgia": sum(1 for k in love_kws if k in combined)
    }

    if "SAD" in category.upper() or "DARD" in category.upper():
        scores["sad_emotional"] += 3
    elif "KHAMOSHI" in category.upper() or "SUKOON" in category.upper():
        scores["sukoon_midnight"] += 3
    elif "SELF" in category.upper() or "ATTITUDE" in category.upper() or "REALITY" in category.upper():
        scores["attitude_mindset"] += 3

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "sukoon_midnight"


def transliterate_to_devanagari(text: str) -> str:
    """
    Transliterates Roman Hindi / Urdu text into natural Devanagari Hindi.
    This unlocks true human-sounding pronunciation in hi-IN-MadhurNeural,
    eliminating synthetic robotic letter-by-letter English pronunciation!
    """
    if not text or not text.strip():
        return ""
    
    # If text already contains Devanagari characters, return as is
    if any("\u0900" <= c <= "\u097F" for c in text):
        return text

    import urllib.request
    import urllib.parse
    import json

    lines = text.split("\n")
    out_lines = []
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            out_lines.append("")
            continue
        try:
            url = "https://inputtools.google.com/request?text=" + urllib.parse.quote(line_clean) + "&itc=hi-t-i0-und&num=1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and data[0] == "SUCCESS":
                    words = [item[1][0] if item[1] else item[0] for item in data[1]]
                    out_lines.append(" ".join(words))
                else:
                    out_lines.append(line_clean)
        except Exception:
            out_lines.append(line_clean)

    return "\n".join(out_lines)


class AudioService:
    def __init__(self, voice: str = "hi-IN-MadhurNeural"):
        # hi-IN-MadhurNeural provides authentic Hindi/Urdu poetry delivery for Devanagari script
        # Fallback: hi-IN-SwaraNeural or ur-IN-SalmanNeural
        self.voice = voice
        self.last_used_track: Optional[Path] = None

    def _get_next_bgm_track(
        self,
        fallback_path: Path,
        total_duration: float,
        text: str = "",
        category: str = ""
    ) -> Path:
        """Picks a track from assets/music/ intelligently matching the emotional mood of the shayari."""
        custom_tracks = sorted(list(MUSIC_DIR.glob("*.mp3")) + list(MUSIC_DIR.glob("*.wav")))
        if not custom_tracks:
            synthesize_soulful_piano_bgm(fallback_path, duration_sec=total_duration + 2.0)
            print(f"[BGM] Generated soulful acoustic piano BGM progression")
            return fallback_path

        # Detect shayari mood
        mood = detect_shayari_mood(text, category)
        target_filenames = MOOD_TRACK_MAPPING.get(mood, [])

        # Filter custom tracks that match target mood filenames or keywords
        matched_tracks = [t for t in custom_tracks if t.name in target_filenames or any(k in t.name.lower() for k in mood.split("_"))]
        candidate_pool = matched_tracks if matched_tracks else custom_tracks

        # Avoid playing same track twice consecutively
        available = [t for t in candidate_pool if t != self.last_used_track]
        bg_music = random.choice(available) if available else candidate_pool[0]
        self.last_used_track = bg_music

        print(f"[BGM Match] Detected Mood: '{mood.upper()}'. Selected Track: {bg_music.name}")
        return bg_music

    async def _create_voiceover_async(self, text: str, output_path: Path):
        # Format text with natural poetic rate & pitch for human emotional warmth
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate="-7%",
            pitch="-1Hz"
        )
        await communicate.save(str(output_path))

    def generate_poetic_voiceover(self, hook: str, quote: str, filename: str) -> Tuple[Path, float]:
        """
        Creates an authentic, human-like emotional poetic voiceover.
        Transliterates to natural Devanagari Hindi so edge-tts pronounces words with genuine
        Urdu/Hindi lehza and soulful inflections rather than synthetic English phonemes.
        Returns: (voice_file_path, duration_seconds)
        """
        out_path = AUDIO_DIR / filename
        
        # Format hook and clean every line of the shayari
        clean_hook = (hook or "").strip(" .!?,")
        raw_lines = [l.strip(" .!?,") for l in (quote or "").split("\n") if l.strip()]
        
        # Transliterate to pure Devanagari Hindi for native human pronunciation
        deva_hook = transliterate_to_devanagari(clean_hook)
        deva_lines = [transliterate_to_devanagari(l) for l in raw_lines]

        # Punctuate lines with natural dramatic pauses (Poetic recitation rhythm)
        clean_quote = "...\n\n".join(deva_lines)
        poetic_text = f"{deva_hook}...\n\n{clean_quote}."
        
        try:
            asyncio.run(self._create_voiceover_async(poetic_text, out_path))
        except Exception as e:
            print(f"[!] Primary voice notice ({e}), switching to hi-IN-SwaraNeural...")
            self.voice = "hi-IN-SwaraNeural"
            asyncio.run(self._create_voiceover_async(poetic_text, out_path))

        duration = get_media_duration(out_path)
        print(f"[VOICEOVER] Generated {duration:.2f}s of human-like poetry voiceover at: {out_path.name}")
        return out_path, duration

    def attach_audio_to_video(
        self,
        video_path: Path,
        voice_mp3: Path,
        total_duration: float,
        text: str = "",
        category: str = ""
    ) -> Path:
        """
        Mixes emotional voiceover + soulful background music with professional
        studio mastering DSP (warmth EQ, de-harshing, broadcast compand) and attaches to video.
        """
        # 1. Get rotated BGM track matched to shayari emotion
        fallback_bgm = AUDIO_DIR / f"{video_path.stem}_piano.wav"
        bg_music = self._get_next_bgm_track(fallback_bgm, total_duration, text=text, category=category)

        output_video = video_path.with_name(f"{video_path.stem}_soulful.mp4")

        # Studio Voice Filterchain:
        # 1. Warmth EQ: Boost 140Hz (+3.5dB) for deep human chest resonance (Shure SM7B broadcast feel)
        # 2. De-harshing: Cut 3.2kHz (-2.0dB) to remove digital synthetic edge
        # 3. Broadcast compand: Smooths dynamic range so whispers and punchlines are intimate & clear
        # 4. adelay=400: Synchronizes with title card fade-in
        # 5. Soft background music ducking (volume=0.20) with smooth fade-out and subtle ambient reverb
        voice_filter = (
            "equalizer=f=140:t=q:w=1.2:g=3.5,"
            "equalizer=f=3200:t=q:w=2.0:g=-2.0,"
            "compand=attacks=0.03:decays=0.25:points=-80/-80|-35/-24|-15/-10|0/-4:gain=2.5,"
            "volume=1.35,adelay=400|400"
        )
        music_filter = f"volume=0.20,afade=t=out:st={max(1.0, total_duration - 2.5)}:d=2.5,aecho=0.8:0.7:45:0.25"

        filter_str = (
            f"[1:a]{voice_filter}[voice];"
            f"[2:a]{music_filter}[music];"
            f"[voice][music]amix=inputs=2:duration=longest:dropout_transition=2[aout]"
        )

        cmd = [
            FFMPEG_EXE,
            "-y",
            "-i", str(video_path),
            "-i", str(voice_mp3),
            "-stream_loop", "-1",
            "-i", str(bg_music),
            "-filter_complex", filter_str,
            "-map", "0:v:0",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(total_duration),
            str(output_video)
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print(f"[!] FFmpeg error: {res.stderr.decode('utf-8', errors='ignore')}")
            return video_path

        # Copy thumbnail
        thumb_old = video_path.with_suffix(".jpg")
        thumb_new = output_video.with_suffix(".jpg")
        if thumb_old.exists():
            import shutil
            shutil.copy(thumb_old, thumb_new)

        return output_video

    def attach_music_only_to_video(
        self,
        video_path: Path,
        duration_sec: float,
        text: str = "",
        category: str = ""
    ) -> Path:
        """
        Attaches pure aesthetic background music intelligently matched to the emotion of the shayari.
        Prioritizes mood matching across tracks in assets/music/.
        """
        fallback_bgm = AUDIO_DIR / f"{video_path.stem}_ambient.wav"
        bg_music = self._get_next_bgm_track(fallback_bgm, duration_sec, text=text, category=category)

        output_video = video_path.with_name(f"{video_path.stem}_music.mp4")

        # Smooth fade-out in last 2 seconds
        filter_str = f"[1:a]volume=0.9,afade=t=out:st={max(1.0, duration_sec - 2.0)}:d=2.0[aout]"

        cmd = [
            FFMPEG_EXE,
            "-y",
            "-i", str(video_path),
            "-i", str(bg_music),
            "-filter_complex", filter_str,
            "-map", "0:v:0",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(duration_sec),
            str(output_video)
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print(f"[!] FFmpeg error: {res.stderr.decode('utf-8', errors='ignore')}")
            return video_path

        # Copy thumbnail
        thumb_old = video_path.with_suffix(".jpg")
        thumb_new = output_video.with_suffix(".jpg")
        if thumb_old.exists():
            import shutil
            shutil.copy(thumb_old, thumb_new)

        return output_video
