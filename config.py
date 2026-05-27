"""
config.py
Bot-wide configuration constants.
"""
import os

# ─── Banner ───────────────────────────────────────────────────────────────────
# Set BANNER_IMAGE_URL to a publicly accessible image URL, or leave it as the
# default placeholder.  You can also override it via the environment variable
# BANNER_IMAGE_URL at runtime.
BANNER_IMAGE_URL: str = os.environ.get(
    'BANNER_IMAGE_URL',
    'https://i.imgur.com/4M34hi2.png'   # ← replace with your own banner URL
)
