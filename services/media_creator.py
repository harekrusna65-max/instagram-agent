"""
Ultra-Aesthetic Media Creator Service for @stanger.man69
Features:
- Glassmorphism frosted card design
- Dynamic ambient bokeh light orbs with cinematic glow
- Georgia Luxury Serif typography with drop shadows & gold key-phrase highlights
- Ken Burns slow cinematic camera zoom in reels
- Verified branding & aesthetic badges
"""

import os
import sys
import time
import math
import random
from pathlib import Path
from typing import Tuple, List, Optional
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
GENERATED_DIR = BASE_DIR / "generated"
POSTS_DIR = GENERATED_DIR / "posts"
REELS_DIR = GENERATED_DIR / "reels"

POSTS_DIR.mkdir(parents=True, exist_ok=True)
REELS_DIR.mkdir(parents=True, exist_ok=True)

# Premium Typography
FONT_SERIF_BOLD = "C:/Windows/Fonts/georgiab.ttf"
FONT_SERIF = "C:/Windows/Fonts/georgia.ttf"
FONT_SANS = "C:/Windows/Fonts/segoeui.ttf"

def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        path,
        "C:/Windows/Fonts/georgiab.ttf",
        "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    lines = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        if not para.strip():
            continue
        words = para.split(" ")
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
    return lines

def create_ambient_bokeh_bg(width: int, height: int, seed: int = 42) -> Image.Image:
    """Create a dark luxury gradient background with soft glowing ambient bokeh orbs."""
    # 1. Base Dark Luxury Gradient (deep obsidian black to midnight purple-indigo)
    c_top = (12, 14, 26)
    c_bot = (4, 4, 8)
    base_arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        r = y / height
        base_arr[y, :] = (
            int(c_top[0]*(1-r) + c_bot[0]*r),
            int(c_top[1]*(1-r) + c_bot[1]*r),
            int(c_top[2]*(1-r) + c_bot[2]*r)
        )
    bg_img = Image.fromarray(base_arr)

    # 2. Glowing Bokeh Layer
    bokeh = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(bokeh)

    orbs = [
        {"x": int(width * 0.2), "y": int(height * 0.22), "r": 240, "c": (147, 51, 234, 48)},   # Purple glow
        {"x": int(width * 0.82), "y": int(height * 0.38), "r": 280, "c": (59, 130, 246, 38)},   # Blue glow
        {"x": int(width * 0.35), "y": int(height * 0.78), "r": 260, "c": (245, 158, 11, 35)},  # Warm amber
        {"x": int(width * 0.75), "y": int(height * 0.70), "r": 220, "c": (236, 72, 153, 30)},  # Rose glow
    ]

    for o in orbs:
        x, y, r, c = o["x"], o["y"], o["r"], o["c"]
        b_draw.ellipse([x - r, y - r, x + r, y + r], fill=c)

    bokeh = bokeh.filter(ImageFilter.GaussianBlur(85))
    return Image.alpha_composite(bg_img.convert("RGBA"), bokeh)


class MediaCreator:
    def __init__(self, handle: str = "@stanger.man69"):
        self.handle = handle

    def create_aesthetic_post(
        self,
        quote: str,
        category: str = "AESTHETIC POETRY",
        theme: str = "luxury_midnight"
    ) -> Path:
        """
        Creates a high-resolution 1080x1350 (4:5 Portrait) ultra-aesthetic graphic card.
        """
        W, H = 1080, 1350
        base_bg = create_ambient_bokeh_bg(W, H)

        # Frosted glass card
        card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(card_layer)
        m_x, m_y = 65, 110
        card_box = [m_x, m_y, W - m_x, H - m_y]

        # Rounded translucent card fill with subtle border
        c_draw.rounded_rectangle(card_box, radius=42, fill=(18, 22, 36, 175), outline=(255, 255, 255, 38), width=2)
        # Accent glowing lines
        c_draw.line([m_x + 60, m_y, m_x + 240, m_y], fill=(168, 85, 247, 240), width=4)
        c_draw.line([W - m_x - 240, H - m_y, W - m_x - 60, H - m_y], fill=(245, 158, 11, 240), width=4)

        img = Image.alpha_composite(base_bg, card_layer)
        draw = ImageDraw.Draw(img)

        # Typography
        f_badge = get_font(FONT_SANS, 24)
        f_quote_mark = get_font(FONT_SERIF_BOLD, 130)
        f_body = get_font(FONT_SERIF_BOLD, 46)
        f_handle = get_font(FONT_SANS, 32)

        # Top Category Badge
        badge_text = f"•  {category.upper()}  •"
        bb = draw.textbbox((0, 0), badge_text, font=f_badge)
        bw = bb[2] - bb[0]
        draw.text(((W - bw) // 2, m_y + 65), badge_text, fill=(200, 185, 240, 220), font=f_badge)

        # Quote symbol
        draw.text((m_x + 75, m_y + 105), "“", fill=(130, 100, 190, 160), font=f_quote_mark)

        # Quote lines
        lines = wrap_text(quote, f_body, W - 240, draw)
        line_height = 74
        total_text_h = len(lines) * line_height
        start_y = (H - total_text_h) // 2

        for i, line in enumerate(lines):
            lb = draw.textbbox((0, 0), line, font=f_body)
            lw = lb[2] - lb[0]
            x = (W - lw) // 2
            y = start_y + (i * line_height)
            # Text shadow for pop
            draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 190), font=f_body)
            # Highlight the last punchline in warm gold
            is_last = (i == len(lines) - 1 and len(lines) > 1)
            text_color = (255, 218, 128) if is_last else (245, 248, 255)
            draw.text((x, y), line, fill=text_color, font=f_body)

        # Divider & Branding
        draw.line([(W // 2) - 80, H - m_y - 135, (W // 2) + 80, H - m_y - 135], fill=(75, 85, 115, 180), width=2)
        hb = draw.textbbox((0, 0), self.handle, font=f_handle)
        hw = hb[2] - hb[0]
        draw.text(((W - hw) // 2, H - m_y - 95), self.handle, fill=(230, 235, 250), font=f_handle)

        timestamp = int(time.time())
        filename = POSTS_DIR / f"post_{timestamp}.jpg"
        img.convert("RGB").save(filename, "JPEG", quality=95)
        return filename

    def create_aesthetic_reel(
        self,
        hook: str,
        quote: str,
        duration_sec: int = 12,
        fps: int = 30
    ) -> Path:
        """
        Creates a vertical 1080x1920 (9:16) MP4 video reel with:
        - Floating ambient particles and glowing bokeh
        - Ken Burns cinematic zoom drift
        - Georgia Serif luxury typography
        - Gold punchline highlight
        """
        W, H = 1080, 1920
        total_frames = duration_sec * fps
        timestamp = int(time.time())
        output_file = REELS_DIR / f"reel_{timestamp}.mp4"

        # Fonts
        f_hook = get_font(FONT_SERIF_BOLD, 52)
        f_quote = get_font(FONT_SERIF_BOLD, 46)
        f_handle = get_font(FONT_SANS, 34)
        f_badge = get_font(FONT_SANS, 24)
        f_qm = get_font(FONT_SERIF_BOLD, 120)

        # Dummy draw for text measurement
        dummy_img = Image.new("RGB", (W, H))
        d_draw = ImageDraw.Draw(dummy_img)

        hook_lines = wrap_text(hook, f_hook, W - 220, d_draw)
        quote_lines = wrap_text(quote, f_quote, W - 230, d_draw)

        # Base ambient bokeh background
        base_bg = create_ambient_bokeh_bg(W, H)

        # Particles
        num_particles = 40
        particles = [
            {
                "x": random.randint(0, W),
                "y": random.randint(0, H),
                "speed": random.uniform(0.7, 2.0),
                "radius": random.randint(1, 3),
                "alpha": random.randint(50, 180)
            }
            for _ in range(num_particles)
        ]

        # Video Writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_file), fourcc, fps, (W, H))

        hook_end_frame = int(3.2 * fps)

        for frame_idx in range(total_frames):
            # Slow cinematic zoom (scale 1.00 -> 1.03)
            zoom = 1.0 + (frame_idx / total_frames) * 0.03
            frame_img = base_bg.copy()
            draw = ImageDraw.Draw(frame_img)

            # Draw floating atmospheric particles
            for p in particles:
                p["y"] = (p["y"] - p["speed"]) % H
                px, py, pr, pa = int(p["x"]), int(p["y"]), p["radius"], p["alpha"]
                draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(pa, pa, min(255, pa + 45), pa))

            # Glassmorphism Card Frame
            margin_x = int(68 * zoom)
            margin_y = int(170 * zoom)
            card_box = [margin_x, margin_y, W - margin_x, H - margin_y]

            # Translucent card body
            card_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            co_draw = ImageDraw.Draw(card_overlay)
            co_draw.rounded_rectangle(card_box, radius=44, fill=(16, 20, 32, 180), outline=(255, 255, 255, 36), width=2)
            
            # Glowing borders top & bottom
            co_draw.line([margin_x + 50, margin_y, margin_x + 220, margin_y], fill=(168, 85, 247, 230), width=4)
            co_draw.line([W - margin_x - 220, H - margin_y, W - margin_x - 50, H - margin_y], fill=(245, 158, 11, 230), width=4)

            frame_img = Image.alpha_composite(frame_img, card_overlay)
            draw = ImageDraw.Draw(frame_img)

            # Top Badge
            badge_text = "•  A E S T H E T I C   R E E L S  •"
            bb = draw.textbbox((0, 0), badge_text, font=f_badge)
            bw = bb[2] - bb[0]
            draw.text(((W - bw) // 2, margin_y + 55), badge_text, fill=(190, 180, 235, 210), font=f_badge)

            # Phase 1: Hook (0 to 3.2s)
            if frame_idx < hook_end_frame:
                progress = min(1.0, frame_idx / (0.8 * fps))
                alpha = int(progress * 255)
                
                total_h = len(hook_lines) * 82
                sy = (H - total_h) // 2
                for i, hl in enumerate(hook_lines):
                    hb = draw.textbbox((0, 0), hl, font=f_hook)
                    hw = hb[2] - hb[0]
                    x = (W - hw) // 2
                    y = sy + (i * 82)
                    draw.text((x + 2, y + 2), hl, fill=(0, 0, 0, alpha), font=f_hook)
                    draw.text((x, y), hl, fill=(alpha, alpha, alpha), font=f_hook)
            else:
                # Phase 2: Main Quote (3.2s to end)
                reveal_progress = min(1.0, (frame_idx - hook_end_frame) / (0.8 * fps))
                alpha = int(reveal_progress * 255)

                total_h = len(quote_lines) * 76
                sy = (H - total_h) // 2 - 30

                # Subtle quote mark
                draw.text((margin_x + 60, sy - 85), "“", fill=(120, 95, 175, int(alpha * 0.7)), font=f_qm)

                for i, ql in enumerate(quote_lines):
                    qb = draw.textbbox((0, 0), ql, font=f_quote)
                    qw = qb[2] - qb[0]
                    x = (W - qw) // 2
                    y = sy + (i * 76)
                    
                    # Drop shadow
                    draw.text((x + 2, y + 2), ql, fill=(0, 0, 0, alpha), font=f_quote)
                    
                    # Highlight the last emotional punchline in luxury gold
                    is_last = (i == len(quote_lines) - 1 and len(quote_lines) > 1)
                    if is_last:
                        col = (255, 215, 120, alpha)
                    else:
                        col = (245, 248, 255, alpha)
                    draw.text((x, y), ql, fill=col, font=f_quote)

            # Watermark at bottom
            hb = draw.textbbox((0, 0), self.handle, font=f_handle)
            hw = hb[2] - hb[0]
            draw.text(((W - hw) // 2, H - margin_y - 85), self.handle, fill=(215, 220, 240, 220), font=f_handle)

            # Glowing progress bar at bottom
            progress_ratio = frame_idx / total_frames
            bar_w = int((W - 2 * margin_x) * progress_ratio)
            draw.line([margin_x, H - margin_y - 12, margin_x + bar_w, H - margin_y - 12], fill=(168, 85, 247), width=4)

            # Write frame
            cv_frame = cv2.cvtColor(np.array(frame_img.convert("RGB")), cv2.COLOR_RGB2BGR)
            writer.write(cv_frame)

        writer.release()

        # Generate thumbnail
        thumb_path = output_file.with_suffix(".jpg")
        cap = cv2.VideoCapture(str(output_file))
        cap.set(cv2.CAP_PROP_POS_FRAMES, hook_end_frame + 20)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(str(thumb_path), frame)
        cap.release()

        return output_file
