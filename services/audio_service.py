"""
Audio Service for Instagram Reels
Generates natural emotional Hindi/English voiceover and ambient aesthetic soundscapes,
and combines them into the Reel video using ffmpeg.
"""

import os
import sys
import math
import wave
import struct
import asyncio
import subprocess
from pathlib import Path
from typing import Optional
import imageio_ffmpeg
import truststore

# Enable Windows certificate store for edge-tts
truststore.inject_into_ssl()
import edge_tts

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "generated" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


def generate_ambient_pad_wav(output_wav: Path, duration_sec: float = 6.0, sample_rate: int = 44100):
    """
    Synthesize a warm, calming 432Hz ambient chord pad (Lofi / Cinema vibe).
    """
    num_samples = int(sample_rate * duration_sec)
    # Frequencies: A minor 9th ambient chord (A2, C3, E3, G3, B3)
    notes = [110.0, 130.81, 164.81, 196.00, 246.94]
    
    with wave.open(str(output_wav), "w") as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            # Envelope: fade-in 0.8s, fade-out 1.2s
            fade_in = min(1.0, t / 0.8)
            fade_out = min(1.0, (duration_sec - t) / 1.2)
            env = fade_in * fade_out
            
            # Combine subtle sine waves with warm detuning
            val = 0.0
            for freq in notes:
                # Add gentle detune / shimmer
                val += math.sin(2 * math.pi * freq * t) * 0.18
                val += math.sin(2 * math.pi * (freq * 1.002) * t) * 0.12
            
            sample_val = int(val * env * 24000)
            sample_val = max(-32767, min(32767, sample_val))
            
            # Stereo left & right
            frames.extend(struct.pack("<hh", sample_val, sample_val))
            
        wav_file.writeframes(frames)


class AudioService:
    def __init__(self, voice: str = "hi-IN-MadhurNeural"):
        self.voice = voice

    async def _create_voiceover_async(self, text: str, output_path: Path):
        communicate = edge_tts.Communicate(text, self.voice, rate="-5%", pitch="-2Hz")
        await communicate.save(str(output_path))

    def generate_voiceover(self, text: str, filename: str = "voiceover.mp3") -> Path:
        """Generate high-quality emotional spoken voiceover."""
        out_path = AUDIO_DIR / filename
        asyncio.run(self._create_voiceover_async(text, out_path))
        return out_path

    def attach_audio_to_video(
        self,
        video_path: Path,
        speech_text: Optional[str] = None,
        duration_sec: float = 6.0
    ) -> Path:
        """
        Mixes ambient music and speech voiceover, then attaches to the MP4 video.
        Outputs an Instagram-ready MP4 with AAC audio track.
        """
        temp_bg = AUDIO_DIR / "ambient_bg.wav"
        generate_ambient_pad_wav(temp_bg, duration_sec=duration_sec)

        output_video = video_path.with_name(f"{video_path.stem}_audio.mp4")

        if speech_text:
            voice_mp3 = self.generate_voiceover(speech_text, f"{video_path.stem}_voice.mp3")
            
            # Merge background ambient pad + voiceover + video using ffmpeg
            # Voice is full volume (1.0), ambient pad is subtle background (0.22)
            cmd = [
                FFMPEG_EXE,
                "-y",
                "-i", str(video_path),
                "-i", str(voice_mp3),
                "-i", str(temp_bg),
                "-filter_complex",
                "[1:a]volume=1.2[a1];[2:a]volume=0.22[a2];[a1][a2]amix=inputs=2:duration=first[aout]",
                "-map", "0:v:0",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(output_video)
            ]
        else:
            # Only ambient background music
            cmd = [
                FFMPEG_EXE,
                "-y",
                "-i", str(video_path),
                "-i", str(temp_bg),
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(output_video)
            ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print(f"[!] FFmpeg audio attach error: {res.stderr.decode('utf-8', errors='ignore')}")
            return video_path

        # Also create/update thumbnail for the new video
        thumb_old = video_path.with_suffix(".jpg")
        thumb_new = output_video.with_suffix(".jpg")
        if thumb_old.exists():
            import shutil
            shutil.copy(thumb_old, thumb_new)

        return output_video
