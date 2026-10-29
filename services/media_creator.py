"""
Media Creator Service
Generates aesthetic Instagram Image Posts (4:5) and Video Reels (9:16) for @stanger.man69
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
from PIL import Image, ImageDraw, ImageFont

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
GENERATED_DIR = BASE_DIR / "generated"
POSTS_DIR = GENERATED_DIR / "posts"
REELS_DIR = GENERATED_DIR / "reels"

POSTS_DIR.mkdir(parents=True, exist_ok=True)
REELS_DIR.mkdir(parents=True, exist_ok=True)

# Standard Fonts
FONT_BOLD = "C:/Windows/Fonts/segoeui.ttf"
FONT_REGULAR = "C:/Windows/Fonts/arial.ttf"

def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Break text into lines that fit within max_width."""
    lines = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        if not para.strip():
            lines.append("")
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

class MediaCreator:
    def __init__(self, handle: str = "@stanger.man69"):
        self.handle = handle

    def create_aesthetic_post(
        self,
        quote: str,
        category: str = "POETRY & THOUGHTS",
        theme: str = "midnight"
    ) -> Path:
        """
        Creates a high-resolution 1080x1350 (4:5 Portrait) graphic post.
        """
        W, H = 1080, 1350
        
        # Color palettes
        if theme == "midnight":
            c_top = (15, 18, 30)
            c_bot = (5, 6, 12)
            accent = (168, 85, 247) # purple glow
        elif theme == "obsidian_gold":
            c_top = (26, 22, 18)
            c_bot = (10, 8, 6)
            accent = (245, 158, 11) # gold
        else: # emerald
            c_top = (6, 28, 24)
            c_bot = (3, 12, 10)
            accent = (52, 211, 153)

        # 1. Create smooth vertical gradient
        base_arr = np.zeros((H, W, 3), dtype=np.uint8)
        for y in range(H):
            ratio = y / H
            r = int(c_top[0] * (1 - ratio) + c_bot[0] * ratio)
            g = int(c_top[1] * (1 - ratio) + c_bot[1] * ratio)
            b = int(c_top[2] * (1 - ratio) + c_bot[2] * ratio)
            base_arr[y, :] = (r, g, b)

        img = Image.fromarray(base_arr)
        draw = ImageDraw.Draw(img)

        # 2. Draw card container frame
        margin = 60
        card_box = [margin, margin, W - margin, H - margin]
        draw.rounded_rectangle(card_box, radius=32, outline=(50, 55, 75), width=2)

        # Subtle accent corner glow
        draw.line([margin + 20, margin, margin + 140, margin], fill=accent, width=4)
        draw.line([W - margin - 140, H - margin, W - margin - 20, H - margin], fill=accent, width=4)

        # 3. Category Tag
        f_tag = get_font(FONT_BOLD, 28)
        tag_text = f"•  {category.upper()}  •"
        tag_bbox = draw.textbbox((0, 0), tag_text, font=f_tag)
        tag_w = tag_bbox[2] - tag_bbox[0]
        draw.text(((W - tag_w) // 2, margin + 80), tag_text, fill=(160, 175, 205), font=f_tag)

        # 4. Large Quote Symbol
        f_quote_mark = get_font(FONT_BOLD, 120)
        draw.text((120, margin + 140), "“", fill=(80, 90, 120), font=f_quote_mark)

        # 5. Main Quote Body
        f_body = get_font(FONT_BOLD, 48)
        max_text_width = W - 240
        lines = wrap_text(quote, f_body, max_text_width, draw)

        # Calculate vertical centering
        line_height = 70
        total_text_h = len(lines) * line_height
        start_y = (H - total_text_h) // 2

        for i, line in enumerate(lines):
            line_bbox = draw.textbbox((0, 0), line, font=f_body)
            line_w = line_bbox[2] - line_bbox[0]
            x = (W - line_w) // 2
            y = start_y + (i * line_height)
            draw.text((x, y), line, fill=(245, 245, 250), font=f_body)

        # 6. Watermark & Branding
        f_handle = get_font(FONT_BOLD, 34)
        handle_text = self.handle
        h_bbox = draw.textbbox((0, 0), handle_text, font=f_handle)
        h_w = h_bbox[2] - h_bbox[0]
        
        # Bottom decorative divider
        div_y = H - margin - 140
        draw.line([(W // 2) - 80, div_y, (W // 2) + 80, div_y], fill=(70, 75, 100), width=2)

        # Draw handle
        draw.text(((W - h_w) // 2, H - margin - 100), handle_text, fill=(220, 225, 240), font=f_handle)

        timestamp = int(time.time())
        filename = POSTS_DIR / f"post_{timestamp}.jpg"
        img.save(filename, "JPEG", quality=95)
        return filename

    def create_aesthetic_reel(
        self,
        hook: str,
        quote: str,
        duration_sec: int = 6,
        fps: int = 30
    ) -> Path:
        """
        Creates a vertical 1080x1920 (9:16) MP4 video reel with animated text and progress bar.
        """
        W, H = 1080, 1920
        total_frames = duration_sec * fps
        timestamp = int(time.time())
        output_file = REELS_DIR / f"reel_{timestamp}.mp4"

        # Fonts
        f_hook = get_font(FONT_BOLD, 52)
        f_quote = get_font(FONT_BOLD, 46)
        f_handle = get_font(FONT_BOLD, 36)
        f_badge = get_font(FONT_BOLD, 26)

        # Dummy draw for text measurement
        dummy_img = Image.new("RGB", (W, H))
        d_draw = ImageDraw.Draw(dummy_img)

        hook_lines = wrap_text(hook, f_hook, W - 200, d_draw)
        quote_lines = wrap_text(quote, f_quote, W - 220, d_draw)

        # Generate star/dust particles for background atmospheric drift
        num_particles = 45
        particles = [
            {
                "x": random.randint(0, W),
                "y": random.randint(0, H),
                "speed": random.uniform(0.8, 2.5),
                "radius": random.randint(1, 3),
                "alpha": random.randint(40, 180)
            }
            for _ in range(num_particles)
        ]

        # Video Writer using OpenCV
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_file), fourcc, fps, (W, H))

        # Base gradient colors
        c_top = (12, 14, 25)
        c_bot = (4, 4, 8)

        base_arr = np.zeros((H, W, 3), dtype=np.uint8)
        for y in range(H):
            ratio = y / H
            r = int(c_top[0] * (1 - ratio) + c_bot[0] * ratio)
            g = int(c_top[1] * (1 - ratio) + c_bot[1] * ratio)
            b = int(c_top[2] * (1 - ratio) + c_bot[2] * ratio)
            base_arr[y, :] = (r, g, b)

        hook_end_frame = int(2.2 * fps)

        for frame_idx in range(total_frames):
            frame_img = Image.fromarray(base_arr.copy())
            draw = ImageDraw.Draw(frame_img)

            # Update & draw particles
            for p in particles:
                p["y"] = (p["y"] - p["speed"]) % H
                px, py, pr, pa = int(p["x"]), int(p["y"]), p["radius"], p["alpha"]
                draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(pa, pa, min(255, pa + 40)))

            # Card frame outline
            margin_x = 70
            margin_y = 180
            draw.rounded_rectangle(
                [margin_x, margin_y, W - margin_x, H - margin_y],
                radius=36,
                outline=(55, 60, 85),
                width=2
            )

            # Top Badge
            badge_text = "• AESTHETIC REELS •"
            bb = draw.textbbox((0, 0), badge_text, font=f_badge)
            bw = bb[2] - bb[0]
            draw.text(((W - bw) // 2, margin_y + 60), badge_text, fill=(168, 85, 247), font=f_badge)

            # Phase 1: Hook (0 to 2.2 sec)
            if frame_idx < hook_end_frame:
                # Fade in hook
                progress = frame_idx / hook_end_frame
                alpha = int(min(255, max(50, progress * 255)))
                
                total_h = len(hook_lines) * 80
                sy = (H - total_h) // 2
                for i, hl in enumerate(hook_lines):
                    hb = draw.textbbox((0, 0), hl, font=f_hook)
                    hw = hb[2] - hb[0]
                    draw.text(((W - hw) // 2, sy + (i * 80)), hl, fill=(alpha, alpha, alpha), font=f_hook)
            else:
                # Phase 2: Main Quote Reveal (smooth fade-in)
                reveal_progress = min(1.0, (frame_idx - hook_end_frame) / (0.8 * fps))
                alpha = int(reveal_progress * 255)

                total_h = len(quote_lines) * 75
                sy = (H - total_h) // 2 - 40
                
                # Small quote mark
                draw.text((margin_x + 60, sy - 80), "“", fill=(90, 100, 140), font=get_font(FONT_BOLD, 90))

                for i, ql in enumerate(quote_lines):
                    qb = draw.textbbox((0, 0), ql, font=f_quote)
                    qw = qb[2] - qb[0]
                    draw.text(((W - qw) // 2, sy + (i * 75)), ql, fill=(245, 245, 250), font=f_quote)

            # Watermark at bottom
            hb = draw.textbbox((0, 0), self.handle, font=f_handle)
            hw = hb[2] - hb[0]
            draw.text(((W - hw) // 2, H - margin_y - 90), self.handle, fill=(200, 205, 225), font=f_handle)

            # Progress bar at very bottom
            progress_ratio = frame_idx / total_frames
            bar_w = int((W - 2 * margin_x) * progress_ratio)
            draw.line([margin_x, H - margin_y - 10, margin_x + bar_w, H - margin_y - 10], fill=(168, 85, 247), width=4)

            # Convert PIL RGB to OpenCV BGR
            cv_frame = cv2.cvtColor(np.array(frame_img), cv2.COLOR_RGB2BGR)
            writer.write(cv_frame)

        writer.release()

        # Generate thumbnail image for Instagram upload
        thumb_path = output_file.with_suffix(".jpg")
        # Extract a nice frame for thumbnail
        cap = cv2.VideoCapture(str(output_file))
        cap.set(cv2.CAP_PROP_POS_FRAMES, hook_end_frame + 15)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(str(thumb_path), frame)
        else:
            frame_img.save(thumb_path, "JPEG")
        cap.release()

        return output_file
