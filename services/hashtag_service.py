"""
Smart Hashtag Rotation Service (Anti-Shadowban Engine)
Rotates through diverse, high-engagement hashtag pools to avoid repetitive tag flagging
and maximize reach across different explore page algorithms.
"""

import random
from typing import List

HASHTAG_POOLS = {
    "AESTHETIC_LOFI": [
        "#aesthetic", "#lofi", "#chillvibes", "#nightthoughts", "#aestheticquotes",
        "#ambient", "#midnightthoughts", "#soulful", "#peaceful", "#vibecheck",
        "#aestheticvideos", "#visualsoflife", "#cinematic", "#darkaesthetic"
    ],
    "SHAYARI_POETRY": [
        "#shayari", "#poetry", "#urdupoetry", "#hindishayari", "#dilkibaat",
        "#khamoshi", "#alfaz", "#sukoon", "#shayarilover", "#sadshayari",
        "#twolineshayari", "#dard", "#jazbaat", "#hindiquotes"
    ],
    "DEEP_LIFE_MINDSET": [
        "#deepquotes", "#lifelessons", "#mindset", "#selfrespect", "#realitycheck",
        "#truelines", "#wisdom", "#growth", "#focus", "#motivation",
        "#maturity", "#inspirationalquotes", "#quoteoftheday", "#lifequotes"
    ],
    "VIRAL_REELS_TRENDING": [
        "#reels", "#reelsinstagram", "#viralreels", "#trending", "#reelkarofeelkaro",
        "#foryou", "#instareels", "#explorepage", "#viralvideo", "#reelitfeelit",
        "#contentcreator", "#trendingnow", "#reelsindia"
    ]
}

BRAND_TAGS = ["#stangerman69"]

class HashtagRotator:
    def __init__(self):
        self.pool_names = list(HASHTAG_POOLS.keys())
        self.current_idx = 0

    def get_smart_hashtags(self, category: str = "", count: int = 14) -> str:
        """
        Dynamically selects and blends hashtags:
        - 1 Primary Pool matching category or rotational index
        - 1 Viral Trending Pool
        - Brand watermark tag
        - Shuffled to prevent Instagram footprint detection
        """
        # Determine primary pool
        cat_upper = category.upper()
        if "SHAYARI" in cat_upper or "POETRY" in cat_upper:
            primary_name = "SHAYARI_POETRY"
        elif "SELF" in cat_upper or "LIFE" in cat_upper or "MINDSET" in cat_upper:
            primary_name = "DEEP_LIFE_MINDSET"
        elif "AESTHETIC" in cat_upper or "KHAMOSHI" in cat_upper:
            primary_name = "AESTHETIC_LOFI"
        else:
            primary_name = self.pool_names[self.current_idx % len(self.pool_names)]
            self.current_idx += 1

        primary_tags = HASHTAG_POOLS[primary_name]
        viral_tags = HASHTAG_POOLS["VIRAL_REELS_TRENDING"]

        # Sample tags to ensure variety
        k_primary = min(len(primary_tags), count // 2)
        k_viral = min(len(viral_tags), count - k_primary - len(BRAND_TAGS))

        selected = random.sample(primary_tags, k_primary) + random.sample(viral_tags, k_viral) + BRAND_TAGS
        random.shuffle(selected)
        return " ".join(selected)
