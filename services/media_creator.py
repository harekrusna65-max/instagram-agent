"""
Ultra-Aesthetic, Professional & Modern Media Creator Service for @stanger.man69
Features:
- Dark Luxury Obsidian & Midnight Color Palettes with Cinematic Ambient Bokeh
- Analog 35mm Subtle Film Grain for authentic photographic warmth
- Verified Creator Header (@stanger.man69 + Blue Verification Badge + Category Pill)
- Dual-Layer Frosted Glassmorphism Card with Specular Light Reflection
- Georgia Luxury Serif Typography with Champagne Gold Punchline Accent
- Real-time Animated Audio Spectrum Equalizer Bars in Reels
- Butter-Smooth Cubic Easing & Floating Stardust Particles
"""

import os
import sys
import time
import math
import random
from pathlib import Path
from typing import Tuple, List, Optional, Dict
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
GENERATED_DIR = BASE_DIR / "generated"
POSTS_DIR = GENERATED_DIR / "posts"
REELS_DIR = GENERATED_DIR / "reels"
BACKGROUNDS_DIR = BASE_DIR / "assets" / "backgrounds"

POSTS_DIR.mkdir(parents=True, exist_ok=True)
REELS_DIR.mkdir(parents=True, exist_ok=True)
BACKGROUNDS_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetic Palette Presets
PALETTES = [
    {
        "name": "midnight_sapphire",
        "top": (14, 16, 32),
        "bot": (5, 6, 14),
        "orbs": [
            (0.20, 0.22, 280, (147, 51, 234, 46)),  # Purple
            (0.82, 0.36, 320, (59, 130, 246, 38)),  # Sapphire
            (0.32, 0.78, 280, (245, 158, 11, 32)),  # Warm Amber
            (0.75, 0.72, 240, (236, 72, 153, 30))   # Rose
        ],
        "accent_badge": (216, 180, 254),
        "specular": (168, 85, 247)
    },
    {
        "name": "obsidian_gold",
        "top": (18, 16, 22),
        "bot": (6, 5, 8),
        "orbs": [
            (0.22, 0.24, 290, (245, 158, 11, 44)),  # Amber Gold
            (0.80, 0.38, 300, (217, 119, 6, 36)),   # Warm Bronze
            (0.35, 0.76, 280, (147, 51, 234, 32)),  # Violet
            (0.72, 0.70, 250, (251, 191, 36, 38))   # Champagne
        ],
        "accent_badge": (253, 230, 138),
        "specular": (245, 158, 11)
    },
    {
        "name": "emerald_noir",
        "top": (10, 20, 22),
        "bot": (4, 8, 10),
        "orbs": [
            (0.22, 0.22, 280, (16, 185, 129, 42)),  # Emerald
            (0.82, 0.35, 320, (6, 182, 212, 36)),   # Cyan
            (0.30, 0.78, 270, (245, 158, 11, 30)),  # Warm Amber
            (0.76, 0.72, 250, (59, 130, 246, 28))   # Slate Blue
        ],
        "accent_badge": (167, 243, 208),
        "specular": (16, 185, 129)
    }
]

def get_font_by_type(font_type: str, size: int) -> ImageFont.FreeTypeFont:
    """Robust multi-platform font loader (Windows & Linux)."""
    candidates = {
        "serif_bold": [
            "C:/Windows/Fonts/georgiab.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "C:/Windows/Fonts/timesbd.ttf",
        ],
        "serif_reg": [
            "C:/Windows/Fonts/georgia.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "C:/Windows/Fonts/times.ttf",
        ],
        "sans_bold": [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ],
        "sans_reg": [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    }
    paths = candidates.get(font_type, candidates["sans_reg"])
    for p in paths:
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

def layout_karaoke_words(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw, total_height: int = 1920) -> Tuple[List[Dict], int]:
    """
    Computes precise (x, y) coordinates for each word to enable word-by-word glowing karaoke animation.
    """
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
                    lines.append(current_line)
                current_line = [word]
        if current_line:
            lines.append(current_line)

    line_h = 78
    start_y = (total_height - len(lines) * line_h) // 2 - 25
    karaoke_data = []
    counter = 0
    space_w = draw.textbbox((0, 0), " ", font=font)[2]

    for l_idx, w_list in enumerate(lines):
        line_w = draw.textbbox((0, 0), " ".join(w_list), font=font)[2]
        cx = (1080 - line_w) // 2
        cy = start_y + l_idx * line_h
        for w in w_list:
            wb = draw.textbbox((0, 0), w, font=font)
            ww = wb[2] - wb[0]
            karaoke_data.append({
                "word": w,
                "x": cx,
                "y": cy,
                "w": ww,
                "global_idx": counter,
                "is_last_line": (l_idx == len(lines) - 1 and len(lines) > 1)
            })
            cx += ww + space_w
            counter += 1

    return karaoke_data, start_y

def create_cinematic_background(width: int, height: int, palette: Optional[Dict] = None) -> Image.Image:
    """Creates a high-end luxury gradient background with ambient orbs and subtle 35mm film grain."""
    if not palette:
        palette = random.choice(PALETTES)

    c_top = palette["top"]
    c_bot = palette["bot"]
    base_arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        r = y / height
        base_arr[y, :] = (
            int(c_top[0]*(1-r) + c_bot[0]*r),
            int(c_top[1]*(1-r) + c_bot[1]*r),
            int(c_top[2]*(1-r) + c_bot[2]*r)
        )

    bokeh = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(bokeh)

    for rx, ry, r, c in palette["orbs"]:
        ox, oy = int(width * rx), int(height * ry)
        b_draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=c)

    bokeh = bokeh.filter(ImageFilter.GaussianBlur(95))
    base_img = Image.alpha_composite(Image.fromarray(base_arr).convert("RGBA"), bokeh)

    # Subtle film grain
    arr = np.array(base_img.convert("RGB"), dtype=np.int16)
    noise = np.random.normal(0, 5.5, (height, width, 1)).astype(np.int16)
    arr += noise
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr).convert("RGBA")

def draw_verified_header(
    draw: ImageDraw.ImageDraw,
    card_x: int,
    card_y: int,
    card_w: int,
    category: str,
    handle: str,
    fonts: Dict[str, ImageFont.FreeTypeFont],
    palette: Dict
):
    """Draws a verified creator header with avatar monogram, verified badge, and category pill."""
    # Avatar
    av_x, av_y, av_r = card_x + 55, card_y + 55, 28
    # Gradient glow ring
    draw.ellipse([av_x - av_r - 2, av_y - av_r - 2, av_x + av_r + 2, av_y + av_r + 2], outline=(168, 85, 247, 220), width=2)
    draw.ellipse([av_x - av_r, av_y - av_r, av_x + av_r, av_y + av_r], fill=(26, 31, 52))
    # Monogram "SM"
    draw.text((av_x - 17, av_y - 15), "SM", fill=(255, 255, 255), font=fonts["sans_bold_med"])

    # Creator Display Name
    name_x, name_y = av_x + av_r + 18, av_y - 20
    draw.text((name_x, name_y), "Stranger", fill=(255, 255, 255), font=fonts["sans_bold_med"])
    nb = draw.textbbox((name_x, name_y), "Stranger", font=fonts["sans_bold_med"])

    # High-Definition Verified Blue Badge (✓)
    bx, by, br = nb[2] + 16, name_y + 16, 12
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(56, 151, 240))
    draw.line([(bx - 5, by), (bx - 1, by + 4), (bx + 5, by - 4)], fill=(255, 255, 255), width=3)

    # Subtitle
    draw.text((name_x, name_y + 36), f"{handle}  •  432Hz Vibe", fill=(148, 163, 184), font=fonts["sans_small"])

    # Top Right Category Pill
    cat_text = f"✦  {category.upper()}"
    pb = draw.textbbox((0, 0), cat_text, font=fonts["sans_small"])
    pw = pb[2] - pb[0] + 28
    ph = pb[3] - pb[1] + 14
    px = card_x + card_w - pw - 45
    py = card_y + 45
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=14, fill=(255, 255, 255, 14), outline=(255, 255, 255, 32), width=1)
    draw.text((px + 14, py + 6), cat_text, fill=palette.get("accent_badge", (216, 180, 254)), font=fonts["sans_small"])


class MediaCreator:
    def __init__(self, handle: str = "@stanger.man69"):
        self.handle = handle

    def create_aesthetic_post(
        self,
        quote: str,
        category: str = "AESTHETIC POETRY",
        theme: Optional[str] = None
    ) -> Path:
        """
        Creates a high-resolution 1080x1350 (4:5 Portrait) modern, professional graphic card.
        """
        W, H = 1080, 1350
        palette = random.choice(PALETTES)
        base_bg = create_cinematic_background(W, H, palette)

        # Frosted glass card geometry
        m_x, m_y = 60, 115
        card_w = W - 2 * m_x
        card_h = H - 2 * m_y

        card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card_layer)

        # Ambient card shadow
        cd.rounded_rectangle([m_x - 3, m_y - 3, W - m_x + 3, H - m_y + 3], radius=44, fill=(0, 0, 0, 95))
        # Translucent glass body with subtle border
        cd.rounded_rectangle([m_x, m_y, W - m_x, H - m_y], radius=42, fill=(18, 22, 38, 185), outline=(255, 255, 255, 36), width=2)

        # Specular light reflection on top edge
        for lx in range(m_x + 50, W - m_x - 50):
            rel = (lx - (m_x + 50)) / (W - 2 * m_x - 100)
            alpha = int(220 * (math.sin(rel * 3.14159) ** 2))
            cd.point((lx, m_y + 1), fill=(255, 255, 255, alpha))
            cd.point((lx, m_y + 2), fill=(210, 225, 255, int(alpha * 0.5)))

        img = Image.alpha_composite(base_bg, card_layer)
        draw = ImageDraw.Draw(img)

        # Typography
        fonts = {
            "sans_bold_med": get_font_by_type("sans_bold", 32),
            "sans_small": get_font_by_type("sans_reg", 22),
            "serif_body": get_font_by_type("serif_bold", 46),
            "quote_mark": get_font_by_type("serif_bold", 130)
        }

        # 1. Verified Header
        draw_verified_header(draw, m_x, m_y, card_w, category, self.handle, fonts, palette)

        # 2. Large Stylized Opening Quote
        draw.text((m_x + 65, m_y + 125), "“", fill=(130, 110, 195, 175), font=fonts["quote_mark"])

        # 3. Poetic Lines
        lines = wrap_text(quote, fonts["serif_body"], card_w - 180, draw)
        line_height = 76
        total_text_h = len(lines) * line_height
        start_y = (H - total_text_h) // 2 + 35

        for i, line in enumerate(lines):
            lb = draw.textbbox((0, 0), line, font=fonts["serif_body"])
            lw = lb[2] - lb[0]
            x = (W - lw) // 2
            y = start_y + (i * line_height)
            # Drop shadow
            draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 205), font=fonts["serif_body"])
            # Highlight punchline in Champagne Gold
            is_last = (i == len(lines) - 1 and len(lines) > 1)
            text_color = (255, 218, 128) if is_last else (248, 250, 252)
            draw.text((x, y), line, fill=text_color, font=fonts["serif_body"])

        # 4. Audio Waveform Spectrum (Bottom of card)
        num_bars = 24
        bar_w, bar_gap = 6, 8
        total_w = num_bars * (bar_w + bar_gap) - bar_gap
        start_bx = (W - total_w) // 2
        bar_base_y = H - m_y - 110

        for bi in range(num_bars):
            bh = int(12 + 28 * (math.sin(bi * 0.45) ** 2))
            bx1 = start_bx + bi * (bar_w + bar_gap)
            bx2 = bx1 + bar_w
            by1 = bar_base_y - bh
            by2 = bar_base_y
            draw.rounded_rectangle([bx1, by1, bx2, by2], radius=3, fill=(168, 85, 247, 200))

        # 5. Aesthetic Footer Note
        footer_txt = "Save for late night thoughts • Share with someone special"
        fb = draw.textbbox((0, 0), footer_txt, font=fonts["sans_small"])
        fw = fb[2] - fb[0]
        draw.text(((W - fw) // 2, H - m_y - 65), footer_txt, fill=(148, 163, 184), font=fonts["sans_small"])

        timestamp = int(time.time())
        filename = POSTS_DIR / f"post_{timestamp}.jpg"
        img.convert("RGB").save(filename, "JPEG", quality=95)
        return filename

    def create_aesthetic_reel(
        self,
        hook: str,
        quote: str,
        category: str = "AESTHETIC REELS",
        duration_sec: int = 12,
        fps: int = 30
    ) -> Path:
        """
        Creates a vertical 1080x1920 (9:16) MP4 video reel with:
        - Real Cinematic Video B-Roll (from assets/backgrounds/ or procedural rainy night city)
        - Word-by-Word Glowing Champagne Gold Karaoke Animation
        - Verified Creator Header (@stanger.man69 + Blue Badge)
        - Real-time Dancing Audio Spectrum Equalizer
        - Specular Frosted Glassmorphism card & 35mm film grain
        """
        W, H = 1080, 1920
        total_frames = duration_sec * fps
        timestamp = int(time.time())
        output_file = REELS_DIR / f"reel_{timestamp}.mp4"

        fonts = {
            "sans_bold_med": get_font_by_type("sans_bold", 34),
            "sans_small": get_font_by_type("sans_reg", 24),
            "hook": get_font_by_type("serif_bold", 52),
            "quote": get_font_by_type("serif_bold", 46),
            "quote_mark": get_font_by_type("serif_bold", 130)
        }

        # Card geometry
        m_x, m_y = 65, 200
        card_w = W - 2 * m_x
        card_h = H - 2 * m_y

        dummy_img = Image.new("RGB", (W, H))
        d_draw = ImageDraw.Draw(dummy_img)
        hook_lines = wrap_text(hook, fonts["hook"], card_w - 180, d_draw)
        karaoke_words, quote_start_y = layout_karaoke_words(quote, fonts["quote"], card_w - 180, d_draw, total_height=H)
        total_words = max(1, len(karaoke_words))

        # Check for custom B-roll video clip in assets/backgrounds/
        broll_clips = list(BACKGROUNDS_DIR.glob("*.mp4")) + list(BACKGROUNDS_DIR.glob("*.mov"))
        broll_cap = None
        if broll_clips:
            chosen_clip = random.choice(broll_clips)
            broll_cap = cv2.VideoCapture(str(chosen_clip))
            print(f"[B-Roll] Using video background from assets/backgrounds/: {chosen_clip.name}")
        else:
            print("[B-Roll] Using procedural cinematic rainy night city traffic simulation")

        # Procedural Rain Simulation Assets
        num_drops = 70
        raindrops = [
            {
                "x": random.randint(30, W - 30),
                "y": random.randint(0, H),
                "r": random.uniform(2.0, 4.5),
                "speed": random.uniform(0.7, 2.6),
                "streak": random.uniform(5.0, 15.0)
            }
            for _ in range(num_drops)
        ]

        # Night city traffic bokeh orbs
        palette = random.choice(PALETTES)
        base_ambient_bg = create_cinematic_background(W, H, palette)

        # Video Writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_file), fourcc, fps, (W, H))

        hook_end_frame = int(2.8 * fps)
        karaoke_start_frame = hook_end_frame
        # Paced smoothly so words glow as they are spoken, reserving last ~2s for final gold linger
        karaoke_end_frame = max(karaoke_start_frame + int(fps * 2.0), int(total_frames - (2.0 * fps)))
        frames_per_word = max(1, (karaoke_end_frame - karaoke_start_frame) // total_words)

        for frame_idx in range(total_frames):
            # 1. Base B-Roll Layer
            if broll_cap and broll_cap.isOpened():
                ret, b_frame = broll_cap.read()
                if not ret:
                    broll_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, b_frame = broll_cap.read()
                if ret:
                    b_frame_resized = cv2.resize(b_frame, (W, H))
                    # Dark aesthetic tint & vignette
                    b_frame_dark = cv2.convertScaleAbs(b_frame_resized, alpha=0.45, beta=-15)
                    frame_img = Image.fromarray(cv2.cvtColor(b_frame_dark, cv2.COLOR_BGR2RGB)).convert("RGBA")
                else:
                    frame_img = base_ambient_bg.copy()
            else:
                # Procedural rainy night city glass
                frame_img = base_ambient_bg.copy()
                rain_draw = ImageDraw.Draw(frame_img)
                for r in raindrops:
                    r["y"] = (r["y"] + r["speed"]) % H
                    rx, ry, rr, sl = int(r["x"]), int(r["y"]), r["r"], r["streak"]
                    rain_draw.line([rx, ry - sl, rx, ry], fill=(210, 225, 255, 65), width=int(rr * 0.75))
                    rain_draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(235, 245, 255, 130))

            # 2. Specular Frosted Glass Card
            card_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card_overlay)
            cd.rounded_rectangle([m_x, m_y, W - m_x, H - m_y], radius=44, fill=(14, 18, 34, 192), outline=(255, 255, 255, 34), width=2)

            # Specular light reflection on top edge
            for lx in range(m_x + 50, W - m_x - 50):
                rel = (lx - (m_x + 50)) / (W - 2 * m_x - 100)
                alpha = int(210 * (math.sin(rel * 3.14159) ** 2))
                cd.point((lx, m_y + 1), fill=(255, 255, 255, alpha))

            frame_img = Image.alpha_composite(frame_img, card_overlay)
            draw = ImageDraw.Draw(frame_img)

            # 3. Verified Creator Header
            draw_verified_header(draw, m_x, m_y, card_w, category, self.handle, fonts, palette)

            # 4. Animated Real-time Audio Spectrum Equalizer
            num_bars = 28
            bar_w, bar_gap = 6, 8
            tot_w = num_bars * (bar_w + bar_gap) - bar_gap
            start_bx = (W - tot_w) // 2
            base_by = H - m_y - 100

            for bi in range(num_bars):
                h_wave = int(10 + 26 * (math.sin(frame_idx * 0.22 + bi * 0.45) ** 2) + 14 * (math.cos(frame_idx * 0.15 - bi * 0.3) ** 2))
                bx1 = start_bx + bi * (bar_w + bar_gap)
                bx2 = bx1 + bar_w
                by1 = base_by - h_wave
                by2 = base_by
                col_r = int(168 + (250 - 168) * (bi / num_bars))
                col_g = int(85 + (204 - 85) * (bi / num_bars))
                col_b = int(247 + (60 - 247) * (bi / num_bars))
                draw.rounded_rectangle([bx1, by1, bx2, by2], radius=3, fill=(col_r, col_g, col_b, 220))

            # Phase 1: Hook Line (0 to 3.0s)
            if frame_idx < hook_end_frame:
                t = min(1.0, frame_idx / (0.8 * fps))
                ease = t * t * (3 - 2 * t)
                alpha = int(ease * 255)
                offset_y = int((1.0 - ease) * 20)

                total_h = len(hook_lines) * 82
                sy = (H - total_h) // 2 + offset_y
                for i, hl in enumerate(hook_lines):
                    hb = draw.textbbox((0, 0), hl, font=fonts["hook"])
                    hw = hb[2] - hb[0]
                    x = (W - hw) // 2
                    y = sy + (i * 82)
                    draw.text((x + 2, y + 2), hl, fill=(0, 0, 0, alpha), font=fonts["hook"])
                    draw.text((x, y), hl, fill=(255, 255, 255, alpha), font=fonts["hook"])
            else:
                # Phase 2: Word-by-Word Glowing Karaoke Animation!
                draw.text((m_x + 65, quote_start_y - 90), "“", fill=(130, 110, 195, 175), font=fonts["quote_mark"])
                active_word_idx = (frame_idx - karaoke_start_frame) // frames_per_word

                for w_item in karaoke_words:
                    w_text = w_item["word"]
                    wx, wy = w_item["x"], w_item["y"]
                    g_idx = w_item["global_idx"]
                    is_last = w_item["is_last_line"]

                    # Drop shadow
                    draw.text((wx + 2, wy + 2), w_text, fill=(0, 0, 0, 200), font=fonts["quote"])

                    if g_idx < active_word_idx:
                        # Already spoken words: crisp white or gold punchline
                        col = (255, 218, 128) if is_last else (248, 250, 252)
                        draw.text((wx, wy), w_text, fill=col, font=fonts["quote"])
                    elif g_idx == active_word_idx:
                        # Actively highlighted word: Glowing radiant champagne gold!
                        glow_col = (255, 242, 170)
                        draw.text((wx - 1, wy), w_text, fill=(245, 158, 11, 140), font=fonts["quote"])
                        draw.text((wx + 1, wy), w_text, fill=(245, 158, 11, 140), font=fonts["quote"])
                        draw.text((wx, wy), w_text, fill=glow_col, font=fonts["quote"])
                    else:
                        # Upcoming words: soft dimmed translucent silver
                        draw.text((wx, wy), w_text, fill=(140, 150, 175, 115), font=fonts["quote"])

            # 5. Glowing Bottom Progress Bar
            progress_ratio = frame_idx / total_frames
            bar_w_prog = int((W - 2 * m_x) * progress_ratio)
            draw.line([m_x, H - m_y - 12, m_x + bar_w_prog, H - m_y - 12], fill=(168, 85, 247), width=4)

            cv_frame = cv2.cvtColor(np.array(frame_img.convert("RGB")), cv2.COLOR_RGB2BGR)
            writer.write(cv_frame)

        writer.release()
        if broll_cap:
            broll_cap.release()

        # Generate thumbnail
        thumb_path = output_file.with_suffix(".jpg")
        cap = cv2.VideoCapture(str(output_file))
        cap.set(cv2.CAP_PROP_POS_FRAMES, hook_end_frame + 20)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(str(thumb_path), frame)
        cap.release()

        return output_file

        # Generate thumbnail
        thumb_path = output_file.with_suffix(".jpg")
        cap = cv2.VideoCapture(str(output_file))
        cap.set(cv2.CAP_PROP_POS_FRAMES, hook_end_frame + 20)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(str(thumb_path), frame)
        cap.release()

        return output_file
